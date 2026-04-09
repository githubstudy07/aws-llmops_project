import os
import json

# 環境変数をインポート前にセット（src.app のモジュールレベル初期化で参照されるため）
os.environ["CHECKPOINT_TABLE"] = "handson-langgraph-checkpoints"
os.environ["WRITES_TABLE"] = "handson-langgraph-writes"
os.environ["BEDROCK_MODEL_ID"] = "apac.amazon.nova-micro-v1:0"
os.environ["AWS_REGION"] = "ap-northeast-1"

from src.app import lambda_handler

def test_local():
    event = {
        "body": json.dumps({
            "message": "こんにちは！私の名前はナオジです。",
            "session_id": "sam-test-001"
        })
    }
    
    print("--- Request 1 ---")
    response = lambda_handler(event, None)
    print(f"Status: {response['statusCode']}")
    print(f"Body: {response['body']}")

    event2 = {
        "body": json.dumps({
            "message": "私の名前は何ですか？",
            "session_id": "sam-test-001"
        })
    }
    
    print("\n--- Request 2 (Persistence Check) ---")
    response2 = lambda_handler(event2, None)
    print(f"Status: {response2['statusCode']}")
    print(f"Body: {response2['body']}")

if __name__ == "__main__":
    test_local()
