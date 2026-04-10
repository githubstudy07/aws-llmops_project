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
        # パラメータを一括取得
        params = ssm.get_parameters_by_path(
            Path="/handson/langfuse/",
            WithDecryption=True
        )["Parameters"]
        
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
from langfuse.callback import CallbackHandler
from langfuse import Langfuse

# Langfuse クライアントの初期化 (単体操作用)
langfuse_client = None
if LANGFUSE_CONF and LANGFUSE_CONF.get("secret_key"):
    langfuse_client = Langfuse(
        public_key=LANGFUSE_CONF["public_key"],
        secret_key=LANGFUSE_CONF["secret_key"],
        host=LANGFUSE_CONF["host"]
    )

# 1. State (状態) の定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Node (ノード) の定義: AI を呼び出す関数
def chatbot(state: State, config: dict):
    # Langfuse ハンドラーの取得 (追跡コンテキストの継承)
    callbacks = config.get("callbacks", [])
    handler = next((c for c in callbacks if isinstance(c, CallbackHandler)), None)

    bedrock_messages = []
    for msg in state["messages"]:
        role = "user" if msg.type == "human" else "assistant"
        bedrock_messages.append({
            "role": role,
            "content": [{"text": msg.content}]
        })

    # Generation (生成) の記録開始
    generation = None
    if handler:
        generation = handler.langfuse.generation(
            name="bedrock-generation",
            model=MODEL_ID,
            model_parameters={"temperature": 0.7, "maxTokens": 300},
            input=bedrock_messages
        )

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=bedrock_messages,
            system=[{"text": "あなたは簡潔に回答する、親切な AI アシスタントです。"}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.7}
        )
        usage = response.get("usage", {})
        output_text = response["output"]["message"]["content"][0]["text"]

        # 成功時の記録
        if generation:
            generation.end(
                output=output_text,
                usage={
                    "input": usage.get("inputTokens", 0),
                    "output": usage.get("outputTokens", 0),
                    "total": usage.get("totalTokens", 0)
                }
            )

        return {"messages": [{"role": "assistant", "content": output_text}]}
    except Exception as e:
        if generation:
            generation.end(level="ERROR", status_message=str(e))
        print(f"Error invoking Bedrock: {e}")
        return {"messages": [{"role": "assistant", "content": f"エラーが発生しました。"}]}

# 3. グラフの構築
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# 4. DynamoDB チェックポインターの設定
checkpointer = DynamoDBSaver(
    checkpoints_table_name=CHECKPOINT_TABLE,
    writes_table_name=WRITES_TABLE,
    client_config={"region_name": REGION}
)

# コンパイル
app = workflow.compile(checkpointer=checkpointer)

def lambda_handler(event, context):
    """
    API Gateway からのリクエストを処理する Lambda ハンドラー
    """
    try:
        # リクエストボディの解析
        body = json.loads(event.get("body", "{}"))
        user_input = body.get("message")
        thread_id = body.get("session_id", "default-session")

        if not user_input:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Message is required"})
            }

        # Langfuse コールバックの設定
        callbacks = []
        handler = None
        if LANGFUSE_CONF and LANGFUSE_CONF.get("secret_key"):
            handler = CallbackHandler(
                public_key=LANGFUSE_CONF["public_key"],
                secret_key=LANGFUSE_CONF["secret_key"],
                host=LANGFUSE_CONF["host"],
                session_id=thread_id,
                metadata={"user_input": user_input}
            )
            callbacks.append(handler)
            print(f"Langfuse handler initialized for session: {thread_id}")
        
        # LangGraph 実行
        config = {
            "configurable": {"thread_id": thread_id},
            "callbacks": callbacks
        }
        input_data = {"messages": [{"role": "user", "content": user_input}]}
        
        output = app.invoke(input_data, config)

        # Langfuse データの送信を強制 (Lambda 終了前に必須)
        if handler:
            handler.flush()
        
        # 最後の AI メッセージを取得
        last_msg = output["messages"][-1]
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  # CORS対応
            },
            "body": json.dumps({
                "response": last_msg.content,
                "session_id": thread_id
            }, ensure_ascii=False)
        }

    except Exception as e:
        print(f"Internal Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
