import json
import os
import sys
import sqlite3
from crew_marketing import create_marketing_crew

def lambda_handler(event, context):
    """
    CrewAI 実行用の Lambda ハンドラー。
    """
    try:
        # 1. 入力の取得 (API Gateway または直接呼び出し)
        body = event.get("body", "{}")
        if isinstance(body, str):
            params = json.loads(body)
        else:
            params = body or {}

        # 診断モード (プラットフォームの状態を確認)
        if params.get("diagnostic"):
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "status": "diagnostic",
                    "sqlite_version": sqlite3.sqlite_version,
                    "python_version": sys.version,
                    "env": {k: v for k, v in os.environ.items() if "AWS" in k or "PATH" in k}
                }, ensure_ascii=False)
            }

        # 2. CrewAI の初期化と実行
        target_product = params.get("target_product", "AI搭載のスマート水筒")
        
        # ★ インポート済みのファクトリ関数から Crew を作成
        crew = create_marketing_crew()

        print(f"Starting CrewAI for product: {target_product}")
        result = crew.kickoff(inputs={"target_product": target_product})

        # 3. 結果の返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "success",
                "product": target_product,
                "result": str(result)
            }, ensure_ascii=False)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "error",
                "message": str(e)
            })
        }
