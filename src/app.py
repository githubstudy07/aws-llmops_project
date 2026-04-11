import json
import os
import boto3
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph_checkpoint_dynamodb.saver import DynamoDBSaver
from botocore.config import Config

# 環境変数
REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
CHECKPOINT_TABLE = os.environ.get("CHECKPOINT_TABLE")
WRITES_TABLE = os.environ.get("WRITES_TABLE")

# Bedrock Runtime クライアント
config = Config(read_timeout=300, retries={'max_attempts': 3})
client = boto3.client("bedrock-runtime", region_name=REGION, config=config)

# Langfuse 設定の取得 (SSM Parameter Store)
def get_langfuse_config():
    ssm = boto3.client("ssm", region_name=REGION)
    try:
        response = ssm.get_parameters_by_path(
            Path="/handson/langfuse/",
            WithDecryption=True
        )
        params = response.get("Parameters", [])
        config_map = {p["Name"]: p["Value"] for p in params}
        return {
            "public_key": config_map.get("/handson/langfuse/public_key"),
            "secret_key": config_map.get("/handson/langfuse/secret_key"),
            "host": config_map.get("/handson/langfuse/host")
        }
    except Exception as e:
        print(f"Warning: Failed to fetch Langfuse config from SSM: {e}")
        return None

LANGFUSE_CONF = get_langfuse_config()

# SDK インポートと環境変数セット
IMPORT_ERR = "None"
try:
    from langfuse.langchain import CallbackHandler
    from langfuse import get_client
except ImportError as e:
    IMPORT_ERR = str(e)
    CallbackHandler = None
    get_client = None

if LANGFUSE_CONF and LANGFUSE_CONF.get("secret_key"):
    os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_CONF["public_key"]
    os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_CONF["secret_key"]
    os.environ["LANGFUSE_HOST"] = LANGFUSE_CONF["host"]

# グローバルクライアントの取得
langfuse_client = get_client() if get_client else None

# 1. State (状態) の定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Node (ノード) の定義
def chatbot(state: State, config: dict = None):
    if config is None: config = {}
    
    bedrock_messages = []
    for msg in state["messages"]:
        m_type = getattr(msg, "type", "") if not isinstance(msg, dict) else msg.get("type", msg.get("role", ""))
        role = "user" if m_type in ["human", "user"] else "assistant"
        m_content = getattr(msg, "content", "") if not isinstance(msg, dict) else msg.get("content", "")
        bedrock_messages.append({"role": role, "content": [{"text": m_content}]})

    # [Option A] コスト管理 & トレーシング
    if langfuse_client:
        try:
            # コンテキストマネージャーにより自動で親子関係と属性が維持される
            with langfuse_client.start_as_current_observation(
                as_type="generation",
                name="bedrock-generation",
                model=MODEL_ID,
                input=bedrock_messages,
                model_parameters={"temperature": 0.7, "maxTokens": 300}
            ) as generation:
                response = client.converse(
                    modelId=MODEL_ID,
                    messages=bedrock_messages,
                    system=[{"text": "あなたは簡潔に回答する、親切な AI アシスタントです。"}],
                    inferenceConfig={"maxTokens": 300, "temperature": 0.7}
                )
                usage = response.get("usage", {})
                output_text = response["output"]["message"]["content"][0]["text"]

                # トークン使用量を連携 (コスト自動計算のトリガー)
                generation.update(
                    output=output_text,
                    usage_details={
                        "input_tokens": usage.get("inputTokens", 0),
                        "output_tokens": usage.get("outputTokens", 0),
                        "total_tokens": usage.get("totalTokens", 0)
                    }
                )
                return {"messages": [{"role": "assistant", "content": output_text}]}
        except Exception as e:
            print(f"Warning: Langfuse tracking failed, but continuing: {e}")

    # フォールバック (Langfuse 不在時)
    response = client.converse(
        modelId=MODEL_ID,
        messages=bedrock_messages,
        system=[{"text": "あなたは簡潔に回答する、親切な AI アシスタントです。"}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.7}
    )
    return {"messages": [{"role": "assistant", "content": response["output"]["message"]["content"][0]["text"]}]}

# 3. グラフの構築
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

checkpointer = DynamoDBSaver(
    checkpoints_table_name=CHECKPOINT_TABLE,
    writes_table_name=WRITES_TABLE,
    client_config={"region_name": REGION}
)
app = workflow.compile(checkpointer=checkpointer)

def lambda_handler(event, context):
    INIT_ERR = "None"
    try:
        path = event.get("resource", "/chat")
        body = json.loads(event.get("body", "{}"))

        if path == "/feedback":
            trace_id = body.get("trace_id")
            score_value = body.get("score_value")
            
            if not trace_id or score_value is None:
                return {"statusCode": 400, "body": json.dumps({"error": "trace_id and score_value are required"})}
                
            if langfuse_client:
                langfuse_client.create_score(
                    trace_id=trace_id,
                    name=body.get("score_name", "user-feedback"),
                    value=score_value,
                    comment=body.get("comment", "")
                )
                langfuse_client.flush()
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"status": "success", "message": "Score recorded"})
                }
            else:
                return {"statusCode": 500, "body": json.dumps({"error": "Langfuse client not initialized"})}

        # /chat endpoint handling
        user_input = body.get("message")
        thread_id = body.get("session_id", "default-session")

        if not user_input:
            return {"statusCode": 400, "body": json.dumps({"error": "Message is required"})}

        callbacks = []
        handler = None
        if CallbackHandler and langfuse_client:
            try:
                # 修正: セッション ID は metadata を通じて渡す
                handler = CallbackHandler()
                callbacks.append(handler)
            except Exception as e:
                INIT_ERR = str(e)

        graph_config = {
            "configurable": {"thread_id": thread_id},
            "callbacks": callbacks,
            "metadata": {
                "langfuse_session_id": thread_id, # SDK v3+ 推奨形式
                "user_input": user_input
            }
        }
        
        output = app.invoke({"messages": [{"role": "user", "content": user_input}]}, graph_config)

        if langfuse_client:
            langfuse_client.flush()
        
        last_msg = output["messages"][-1]
        response_text = last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", str(last_msg))

        # トレースIDの取得
        trace_id = getattr(handler, "last_trace_id", None) if handler else None

        # 診断サフィックス
        conn_type = "Real" if handler else "Mock"
        suffix = f"\n\n[Final Diagnosis: {conn_type} | Imp_Err: {IMPORT_ERR} | Init_Err: {INIT_ERR}]"
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "response": response_text + suffix,
                "session_id": thread_id,
                "trace_id": trace_id
            }, ensure_ascii=False)
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
