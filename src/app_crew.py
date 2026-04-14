import json
import os
import sys

def lambda_handler(event, context):
    try:
        # Move imports inside to catch errors
        print(f"Python version: {sys.version}")
        from crew_marketing import create_marketing_crew
        
        # 1. 入力の取得
        body = event.get("body", "{}")
        if isinstance(body, str):
            params = json.loads(body)
        else:
            params = body or {}

        target_product = params.get("target_product", "AI搭載のスマート水筒")

        # 2. CrewAI の初期化と実行
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
            "body": json.dumps({
                "status": "error",
                "message": str(e)
            })
        }
