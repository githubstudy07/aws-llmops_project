# File: src/main.py
import json
import os
import boto3
import logging
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_aws import ChatBedrockConverse
from langgraph_checkpoint_aws import DynamoDBSaver
from langfuse.langchain import CallbackHandler
from langfuse import get_client, propagate_attributes

# --- Logging Setup ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- Configuration ---
DDB_TABLE_NAME = os.environ.get("CHECKPOINT_TABLE")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
REGION = os.environ.get("AWS_REGION_NAME", "ap-northeast-1")

def get_langfuse_config():
    """環境変数から Langfuse 設定を取得"""
    lf_host = os.environ.get("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")
    lf_pk = os.environ.get("LANGFUSE_PUBLIC_KEY")
    lf_sk = os.environ.get("LANGFUSE_SECRET_KEY")

    logger.info(f"Langfuse Config: host={lf_host}, pk_exists={bool(lf_pk)}, sk_exists={bool(lf_sk)}")

    if not lf_pk or not lf_sk:
        logger.warning("Langfuse API keys not configured via environment variables. Tracing may be disabled.")
        return lf_host, None, None

    return lf_host, lf_pk, lf_sk

# --- State Definition ---
class State(TypedDict):
    # add_messages allows appending new messages to the existing list
    messages: Annotated[list, add_messages]

# --- Node Implementation ---
def chatbot(state: State):
    """Bedrock Nova Micro を呼び出すノード"""
    llm = ChatBedrockConverse(
        model_id=MODEL_ID,
        region_name=REGION,
        temperature=0,
        max_tokens=2048
    )

    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# --- Graph Construction ---
def create_graph(checkpointer):
    """LangGraph 1.x のグラフ構造を構築"""
    workflow = StateGraph(State)
    
    # ノードの追加
    workflow.add_node("chatbot", chatbot)
    
    # エッジの追加
    workflow.add_edge(START, "chatbot")
    workflow.add_edge("chatbot", END)
    
    # チェックポインター（永続化層）付きでコンパイル
    return workflow.compile(checkpointer=checkpointer)

# --- Lambda Handler ---
def lambda_handler(event, context):
    """Lambda エントリポイント"""
    logger.info(f"Event Received: {json.dumps(event)}")
    
    try:
        # 1. リクエスト解析
        body = json.loads(event.get("body", "{}"))
        user_message = body.get("message")
        thread_id = body.get("thread_id", "session-default")
        
        if not user_message:
            return {
                "statusCode": 400, 
                "body": json.dumps({"error": "Message is required"}, ensure_ascii=False)
            }

        # 2. 永続化層 (DynamoDB) の準備
        saver = DynamoDBSaver(table_name=DDB_TABLE_NAME, region_name=REGION)
        
        # 3. グラフの構築と実行
        graph = create_graph(saver)
        
        # Langfuse ハンドラーの初期化
        lf_host, lf_pk, lf_sk = get_langfuse_config()

        langfuse_handler = None
        if lf_pk and lf_sk:
            # Set environment variables for Langfuse client initialization
            os.environ["LANGFUSE_PUBLIC_KEY"] = lf_pk
            os.environ["LANGFUSE_SECRET_KEY"] = lf_sk
            os.environ["LANGFUSE_BASE_URL"] = lf_host
            langfuse_handler = CallbackHandler()
        
        # コンテキスト（thread_id）とコールバックの設定
        config = {
            "configurable": {"thread_id": thread_id}
        }
        if langfuse_handler:
            config["callbacks"] = [langfuse_handler]

        # 実行 (過去の履歴は graph が DynamoDB から自動的にロードする)
        input_data = {"messages": [{"role": "user", "content": user_message}]}

        # Langfuse v4: session_id でトレースをグループ化
        with propagate_attributes(session_id=thread_id):
            result = graph.invoke(input_data, config=config)

        # トレースを確実に送信（Langfuse クライアントから flush）
        if langfuse_handler:
            get_client().flush()
        
        # 最新の回答を抽出 (最後のメッセージ)
        final_answer = result["messages"][-1].content

        # 4. レスポンス返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "response": final_answer,
                "thread_id": thread_id,
                "model": MODEL_ID
            }, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(f"Handler failed: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal Server Error", 
                "details": str(e)
            }, ensure_ascii=False)
        }
