import json
import boto3
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph_checkpoint_dynamodb.saver import DynamoDBSaver
from botocore.config import Config

"""
Phase 3-3: LangGraph 永続化 - DynamoDB チェックポインター
DynamoDB を使用して、会話の「状態 (State)」を永続的に記録します。
"""

# 設定
REGION = "ap-northeast-1"
MODEL_ID = "apac.amazon.nova-micro-v1:0"
CHECKPOINT_TABLE = "handson-langgraph-checkpoints"
WRITES_TABLE = "handson-langgraph-writes"

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
        return {"messages": [{"role": "assistant", "content": f"エラー: {str(e)}"}]}

# 3. グラフの構築
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# 4. DynamoDB チェックポインターの設定
# DynamoDBSaver は 2 つのテーブル名を必要とします
checkpointer = DynamoDBSaver(
    checkpoints_table_name=CHECKPOINT_TABLE,
    writes_table_name=WRITES_TABLE,
    client_config={"region_name": REGION}
)

# コンパイル時に checkpointer を指定
app = workflow.compile(checkpointer=checkpointer)

def run_interaction(thread_id, user_input):
    print(f"\n--- Thread ID: {thread_id} ---")
    print(f"[user]: {user_input}")
    
    config = {"configurable": {"thread_id": thread_id}}
    input_data = {"messages": [{"role": "user", "content": user_input}]}
    
    # 実行
    output = app.invoke(input_data, config)
    
    # 最後のAIメッセージのみ表示
    last_msg = output["messages"][-1]
    print(f"[ai]: {last_msg.content}")

if __name__ == "__main__":
    # 5. テスト実行
    # NOTE: 実行前に AWS コンソールまたは CLI で 'langgraph-checkpoints' テーブルを作成しておく必要があります。
    # (DynamoDBSaver は自動作成機能を持たないため、事前に手動作成が必要です)
    
    session_id = "user-story-abc"
    
    print("--- 記憶のテスト ---")
    run_interaction(session_id, "私の名前はナオジです。覚えておいてください。")
    run_interaction(session_id, "私の名前は何ですか？")
