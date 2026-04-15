import json
import os
import sys
import boto3

# [DIAGNOSTIC] すべての重いインポートをハンドラー内に移動し、
# どの段階で Runtime.Unknown が発生しているかを特定する。

def get_langfuse_config():
    """SSM Parameter Store から Langfuse 設定を取得"""
    REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
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

def lambda_handler(event, context):
    """
    CrewAI (Marketing) を実行するメインハンドラー
    """
    print("--- Lambda Handler Started ---")
    
    # 1. バージョン診断 (AL2023 の標準 SQLite を確認)
    try:
        import sqlite3
        print(f"System SQLite version: {sqlite3.sqlite_version}")
    except Exception as e:
        print(f"SQLite import error: {e}")

    # 2. 環境設定 (SSM)
    try:
        langfuse_conf = get_langfuse_config()
        if langfuse_conf:
            os.environ["LANGFUSE_PUBLIC_KEY"] = langfuse_conf.get("public_key") or ""
            os.environ["LANGFUSE_SECRET_KEY"] = langfuse_conf.get("secret_key") or ""
            os.environ["LANGFUSE_HOST"] = langfuse_conf.get("host") or "https://cloud.langfuse.com"
            print("Langfuse config fetched from SSM")
    except Exception as e:
        print(f"Langfuse setup error: {e}")

    # 3. 入力データの取得
    body_data = {}
    if "body" in event and event["body"]:
        try:
            body_data = json.loads(event["body"])
        except:
            body_data = {"message": str(event["body"])}
    
    target_product = body_data.get("message") or body_data.get("target_product") or "AI搭載の最新型ロボット掃除機"
    print(f"Target product: {target_product}")
    
    try:
        # 4. CrewAI 関連の遅延インポート
        print("Importing crew_marketing...")
        from crew_marketing import create_marketing_crew
        print("Creating marketing crew...")
        crew = create_marketing_crew()
        print("Crew created. Starting kickoff...")
        
        result = crew.kickoff(inputs={'target_product': target_product})
        print("Kickoff finished successfully")
        
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
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error during Crew execution:\n{error_msg}")
        return {
            "statusCode": 500,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({
                "error": str(e),
                "traceback": error_msg,
                "status": "error"
            })
        }
