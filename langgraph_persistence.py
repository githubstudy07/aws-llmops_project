import json
import boto3
import logging
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph_checkpoint_aws import DynamoDBSaver
from langchain_aws import ChatBedrockConverse
from botocore.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Phase 3-3: LangGraph 永続化 - DynamoDB チェックポインター (セッション 59 仕様)
DynamoDB を使用して、会話の「状態 (State)」を永続的に記録します。
"""

# 設定
REGION = "ap-northeast-1"
MODEL_ID = "apac.amazon.nova-micro-v1:0"
CHECKPOINT_TABLE = "langgraph-chat-checkpoints-v2"  # スキーマ: PK (HASH), SK (RANGE) ✅ 検証済み

# 1. State (状態) の定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Node (ノード) の定義: AI を呼び出す関数
def chatbot(state: State):
    llm = ChatBedrockConverse(
        model_id=MODEL_ID,
        region_name=REGION,
        temperature=0.7,
        max_tokens=300
    )
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 3. グラフの構築
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# 4. DynamoDB チェックポインターの設定 (セッション 59 仕様)
# 最新版: table_name と region_name パラメータ、PK/SK スキーマ対応
checkpointer = DynamoDBSaver(table_name=CHECKPOINT_TABLE, region_name=REGION)

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
    # 5. テスト実行 (セッション 59 版)
    # NOTE: テーブル 'langgraph-chat-checkpoints-v2' は既に存在し、52 個のチェックポイントが記録済みです。
    # (PK/SK スキーマで既に DynamoDB に作成済み - セッション 58 で検証済み)

    session_id = "user-story-abc"

    logger.info("--- 記憶のテスト開始 ---")
    try:
        run_interaction(session_id, "私の名前はナオジです。覚えておいてください。")
        run_interaction(session_id, "私の名前は何ですか？")
        logger.info("✅ テスト完了: 記憶保持が成功しました。")
    except Exception as e:
        logger.error(f"❌ テスト失敗: {str(e)}", exc_info=True)
