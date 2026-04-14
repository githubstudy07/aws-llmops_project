import json
import os


def lambda_handler(event, context):
    """
    CrewAI 実行用の Lambda ハンドラー。
    Crew の初期化をこの関数内で行うことで、import 時の LLM 接続を回避します。
    """
    try:
        # 1. 入力の取得 (API Gateway または直接呼び出し)
        body = event.get("body", "{}")
        if isinstance(body, str):
            params = json.loads(body)
        else:
            params = body or {}

        target_product = params.get("target_product", "AI搭載のスマート水筒")

        # 2. CrewAI の初期化と実行
        # ★ 呼び出し時に初めて Crew を作成する（遅延初期化）
        from crew_marketing import create_marketing_crew
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
