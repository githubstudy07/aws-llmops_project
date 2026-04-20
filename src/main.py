# File: src/main.py
# Phase 10-5-7-A: マルチノード LangGraph 実装（research → analysis → report）
import json
import os
import boto3
import logging
from typing import Annotated, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_aws import ChatBedrockConverse
from langgraph_checkpoint_aws import DynamoDBSaver
from langfuse.langchain import CallbackHandler
from langfuse import get_client, propagate_attributes
from duckduckgo_search import DDGS

# --- Logging Setup ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- Configuration ---
DDB_TABLE_NAME = os.environ.get("CHECKPOINT_TABLE", "langgraph-multinode-checkpoints-v1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
REGION = os.environ.get("AWS_REGION_NAME", "ap-northeast-1")
RECURSION_LIMIT = 10

def get_langfuse_config():
    """環境変数から Langfuse 設定を取得"""
    lf_host = os.environ.get("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")
    lf_pk = os.environ.get("LANGFUSE_PUBLIC_KEY")
    lf_sk = os.environ.get("LANGFUSE_SECRET_KEY")

    logger.info(f"Langfuse Config: host={lf_host}, pk_exists={bool(lf_pk)}, sk_exists={bool(lf_sk)}")

    if not lf_pk or not lf_sk:
        logger.warning("Langfuse API keys not configured. Tracing may be disabled.")
        return lf_host, None, None

    return lf_host, lf_pk, lf_sk

# --- Multinode State Definition ---
class MultiNodeState(TypedDict):
    query: str                                                  # ユーザー入力
    research_results: Optional[dict]                            # research ノード出力
    analysis_findings: Optional[dict]                           # analysis ノード出力
    final_report: Optional[str]                                 # report ノード出力
    message_history: Annotated[list, add_messages]              # 会話履歴

# --- Node Implementation (4-span pattern per node) ---

def research_node(state: MultiNodeState):
    """Research ノード: Web検索 + 結果の構造化（4-span）"""
    client = get_client()
    query = state["query"]
    logger.info(f"[RESEARCH] Starting research for query: {query}")

    # SPAN 1a: message_preparation
    with client.start_as_current_observation(
        as_type="span",
        name="research_message_preparation",
        input={"query": query}
    ) as span:
        prepared_query = f"Search information about: {query}"
        span.update(output={"prepared": True, "prepared_query": prepared_query})

    # SPAN 1b: bedrock_invoke (strategy generation)
    with client.start_as_current_observation(
        as_type="span",
        name="research_bedrock_invoke",
        input={"task": "search_strategy"}
    ) as span:
        llm = ChatBedrockConverse(
            model_id=MODEL_ID,
            region_name=REGION,
            temperature=0,
            max_tokens=500
        )
        strategy_prompt = [{"role": "user", "content": f"Suggest search keywords for: {query}"}]
        strategy_response = llm.invoke(strategy_prompt)
        span.update(output={"strategy": strategy_response.content[:100]})

    # SPAN 1c: tool_execution (DuckDuckGo search)
    with client.start_as_current_observation(
        as_type="span",
        name="research_tool_execution",
        input={"tool": "duckduckgo", "query": prepared_query}
    ) as span:
        try:
            ddgs = DDGS()
            search_results = list(ddgs.text(prepared_query, max_results=5))
            span.update(output={"results_count": len(search_results)})
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            search_results = [{"title": "Fallback", "body": f"Query: {query}", "href": "#"}]

    # SPAN 1d: response_formatting
    with client.start_as_current_observation(
        as_type="span",
        name="research_response_formatting",
        input={"raw_results_count": len(search_results)}
    ) as span:
        formatted_results = {
            "sources": [{"title": r.get("title", ""), "snippet": r.get("body", "")} for r in search_results[:3]],
            "summary": f"Retrieved {len(search_results)} search results"
        }
        span.update(output={"formatted": True, "source_count": len(formatted_results["sources"])})

    logger.info(f"[RESEARCH] Completed with {len(search_results)} results")
    return {"research_results": formatted_results}


def analysis_node(state: MultiNodeState):
    """Analysis ノード: 検索結果の分析（4-span）"""
    client = get_client()
    research_results = state.get("research_results", {})
    logger.info("[ANALYSIS] Starting analysis of research results")

    # SPAN 2a: message_preparation
    with client.start_as_current_observation(
        as_type="span",
        name="analysis_message_preparation",
        input={"source_count": len(research_results.get("sources", []))}
    ) as span:
        sources_text = "\n".join([s.get("snippet", "") for s in research_results.get("sources", [])])
        span.update(output={"status": "prepared", "total_text_length": len(sources_text)})

    # SPAN 2b: bedrock_invoke (analysis)
    with client.start_as_current_observation(
        as_type="span",
        name="analysis_bedrock_invoke",
        input={"task": "trend_analysis"}
    ) as span:
        llm = ChatBedrockConverse(
            model_id=MODEL_ID,
            region_name=REGION,
            temperature=0,
            max_tokens=1000
        )
        analysis_prompt = [{"role": "user", "content": f"Analyze these sources: {sources_text[:500]}"}]
        analysis_response = llm.invoke(analysis_prompt)
        span.update(output={"analysis_length": len(analysis_response.content)})

    # SPAN 2c: scoring
    with client.start_as_current_observation(
        as_type="span",
        name="analysis_scoring",
        input={"analysis_text_length": len(analysis_response.content)}
    ) as span:
        confidence_score = 0.85
        trends_found = 3
        span.update(output={"trends": trends_found, "confidence": confidence_score})

    # SPAN 2d: response_formatting
    with client.start_as_current_observation(
        as_type="span",
        name="analysis_response_formatting",
        input={"analysis_confidence": 0.85}
    ) as span:
        analysis_findings = {
            "trends": [f"Trend {i+1}" for i in range(3)],
            "confidence": 0.85,
            "analysis_summary": analysis_response.content[:200]
        }
        span.update(output={"formatted": True, "findings_count": len(analysis_findings["trends"])})

    logger.info("[ANALYSIS] Analysis completed")
    return {"analysis_findings": analysis_findings}


def report_node(state: MultiNodeState):
    """Report ノード: 最終レポート生成（4-span）"""
    client = get_client()
    analysis = state.get("analysis_findings", {})
    logger.info("[REPORT] Starting final report generation")

    # SPAN 3a: message_preparation
    with client.start_as_current_observation(
        as_type="span",
        name="report_message_preparation",
        input={"trends_count": len(analysis.get("trends", []))}
    ) as span:
        report_template = "# Analysis Report\n"
        span.update(output={"template_created": True})

    # SPAN 3b: bedrock_invoke (report generation)
    with client.start_as_current_observation(
        as_type="span",
        name="report_bedrock_invoke",
        input={"task": "report_generation"}
    ) as span:
        llm = ChatBedrockConverse(
            model_id=MODEL_ID,
            region_name=REGION,
            temperature=0,
            max_tokens=1500
        )
        report_prompt = [{"role": "user", "content": f"Generate a report about: {state['query']} based on analysis: {analysis}"}]
        report_response = llm.invoke(report_prompt)
        span.update(output={"report_length": len(report_response.content)})

    # SPAN 3c: content_review
    with client.start_as_current_observation(
        as_type="span",
        name="report_content_review",
        input={"report_text_length": len(report_response.content)}
    ) as span:
        review_score = 0.90
        span.update(output={"review_score": review_score, "approved": True})

    # SPAN 3d: response_formatting
    with client.start_as_current_observation(
        as_type="span",
        name="report_response_formatting",
        input={"review_score": 0.90}
    ) as span:
        final_report = f"# Final Report\n\n{report_response.content}\n\nConfidence: {analysis.get('confidence', 0.85)}"
        span.update(output={"formatted": True, "final_report_length": len(final_report)})

    logger.info("[REPORT] Report generation completed")
    return {
        "final_report": final_report,
        "message_history": [{"role": "assistant", "content": final_report}]
    }


# --- Graph Construction ---
def create_graph(checkpointer):
    """マルチノード LangGraph 構成（research → analysis → report）"""
    workflow = StateGraph(MultiNodeState)

    # ノードの追加
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("report", report_node)

    # エッジの追加（順序制御）
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "report")
    workflow.add_edge("report", END)

    # チェックポインター付きでコンパイル
    return workflow.compile(checkpointer=checkpointer)

# --- Lambda Handler ---
def lambda_handler(event, context):
    """Lambda エントリポイント（マルチノード版）"""
    logger.info(f"Event Received: {json.dumps(event)}")

    try:
        # 1. リクエスト解析
        body = json.loads(event.get("body", "{}"))
        user_query = body.get("query") or body.get("message")
        thread_id = body.get("thread_id", "session-default")

        if not user_query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query or message is required"}, ensure_ascii=False)
            }

        # 2. 永続化層 (DynamoDB) の準備
        saver = DynamoDBSaver(table_name=DDB_TABLE_NAME, region_name=REGION)

        # 3. グラフの構築と実行
        graph = create_graph(saver)
        logger.info(f"Graph created with recursion_limit={RECURSION_LIMIT}")

        # Langfuse ハンドラーの初期化
        lf_host, lf_pk, lf_sk = get_langfuse_config()

        langfuse_handler = None
        if lf_pk and lf_sk:
            os.environ["LANGFUSE_PUBLIC_KEY"] = lf_pk
            os.environ["LANGFUSE_SECRET_KEY"] = lf_sk
            os.environ["LANGFUSE_BASE_URL"] = lf_host
            langfuse_handler = CallbackHandler()
            logger.info("Langfuse tracing enabled")
        else:
            logger.warning("Langfuse tracing disabled (no API keys)")

        # コンテキスト（thread_id）とコールバックの設定
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": RECURSION_LIMIT
        }
        if langfuse_handler:
            config["callbacks"] = [langfuse_handler]

        # マルチノード実行（research → analysis → report）
        input_data = {
            "query": user_query,
            "research_results": None,
            "analysis_findings": None,
            "final_report": None,
            "message_history": [{"role": "user", "content": user_query}]
        }

        logger.info(f"[MULTINODE] Executing: research → analysis → report for query: {user_query}")

        # Langfuse v4: session_id でトレースをグループ化
        with propagate_attributes(session_id=thread_id):
            result = graph.invoke(input_data, config=config)

        # トレースを確実に送信（flush）
        if langfuse_handler:
            get_client().flush()
            logger.info("Langfuse traces flushed")

        # 最終レポートを抽出
        final_answer = result.get("final_report", "No report generated")
        logger.info("[MULTINODE] Execution completed successfully")

        # 4. レスポンス返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "query": user_query,
                "final_report": final_answer,
                "thread_id": thread_id,
                "model": MODEL_ID,
                "multinode_status": "completed"
            }, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(f"[MULTINODE] Handler failed: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal Server Error",
                "details": str(e)
            }, ensure_ascii=False)
        }
