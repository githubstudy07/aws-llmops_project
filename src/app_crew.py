import json
import os
from crew_marketing import marketing_crew

def lambda_handler(event, context):
    """
    CrewAI 実行用の Lambda ハンドラー
    """
    try:
        # 1. 入力の取得 (API Gateway または直接呼び出し)
        body = event.get("body", "{}")
        if isinstance(body, str):
            params = json.loads(body)
        else:
            params = body
        
        target_product = params.get("target_product", "AI搭載のスマート水筒")

        # 2. CrewAI の実行
        # inputs を辞書で渡し、エージェントがタスクを遂行します
        print(f"Starting CrewAI for product: {target_product}")
        result = marketing_crew.kickoff(inputs={"target_product": target_product})

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
