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

# 1. State (状態) の定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Node (ノード) の定義: AI を呼び出す関数
def chatbot(state: State):
    bedrock_messages = []
    for msg in state["messages"]:
        role = "user" if msg.type == "human" else "assistant"
        bedrock_messages.append({
            "role": role,
            "content": [{"text": msg.content}]
        })

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=bedrock_messages,
            system=[{"text": "あなたは簡潔に回答する、親切な AI アシスタントです。"}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.7}
        )
        output_text = response["output"]["message"]["content"][0]["text"]
        return {"messages": [{"role": "assistant", "content": output_text}]}
    except Exception as e:
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

        # LangGraph 実行
        config = {"configurable": {"thread_id": thread_id}}
        input_data = {"messages": [{"role": "user", "content": user_input}]}
        
        output = app.invoke(input_data, config)
        
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
