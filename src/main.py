# File: src/main.py
import json
import os
import boto3
import logging
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.aws import DynamoDBSaver

# --- Logging Setup ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- Configuration ---
DDB_TABLE_NAME = os.environ.get("CHECKPOINT_TABLE")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
REGION = os.environ.get("BEDROCK_REGION", "ap-northeast-1")

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
    # LangChain の invoke を使用
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
        thread_id = body.get("thread_id", "default-thread")
        
        if not user_message:
            return {
                "statusCode": 400, 
                "body": json.dumps({"error": "Message is required"}, ensure_ascii=False)
            }

        # 2. 永続化層 (DynamoDB) の準備
        # AWS Lambda 実行環境の認証情報をそのまま使用
        ddb_client = boto3.client("dynamodb", region_name=REGION)
        saver = DynamoDBSaver(table_name=DDB_TABLE_NAME, client=ddb_client)
        
        # 3. グラフの構築と実行
        graph = create_graph(saver)
        
        # コンテキスト（thread_id）の設定
        config = {"configurable": {"thread_id": thread_id}}
        
        # 実行 (過去の履歴は graph が DynamoDB から自動的にロードする)
        input_data = {"messages": [{"role": "user", "content": user_message}]}
        result = graph.invoke(input_data, config=config)
        
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
