import json
import os
import sys

# [CRITICAL] Lambda の古い SQLite3 を pysqlite3-binary で差し替える
# この処理は他のすべてのインポート（特に crewai / chromadb）より前に行う必要がある
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
    print("SQLite3 has been successfully swapped with pysqlite3-binary")
except ImportError:
    print("pysqlite3-binary not found, using standard sqlite3")

import boto3
from crew_marketing import create_marketing_crew

# 1. 環境設定
REGION = os.environ.get("AWS_REGION", "ap-northeast-1")

def get_langfuse_config():
    """SSM Parameter Store から Langfuse 設定を取得"""
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

# 2. 初期化 (環境変数のセット)
LANGFUSE_CONF = get_langfuse_config()
if LANGFUSE_CONF:
    os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_CONF.get("public_key") or ""
    os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_CONF.get("secret_key") or ""
    os.environ["LANGFUSE_HOST"] = LANGFUSE_CONF.get("host") or "https://cloud.langfuse.com"

def lambda_handler(event, context):
    """
    CrewAI (Marketing) を実行するメインハンドラー
    """
    print("Lambda started")
    
    # 3. 入力データの取得
    body_data = {}
    if "body" in event and event["body"]:
        try:
            body_data = json.loads(event["body"])
        except:
            body_data = {"message": str(event["body"])}
    
    # Dify等からの入力を想定したキー (message) または直接指定 (target_product)
    target_product = body_data.get("message") or body_data.get("target_product") or "AI搭載の最新型ロボット掃除機"
    print(f"Target product: {target_product}")
    
    try:
        # 4. Crew の作成と実行
        print("Creating marketing crew...")
        crew = create_marketing_crew()
        print("Crew created. Starting kickoff...")
        
        # タイムアウト対策として、実行開始をログ
        result = crew.kickoff(inputs={'target_product': target_product})
        print("Kickoff finished successfully")
        
        # 5. レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "response": str(result),
                "target_product": target_product,
                "status": "success"
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"Error during Crew execution: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": str(e),
                "target_product": target_product,
                "status": "error"
            })
        }
