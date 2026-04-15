import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import os
from crew_marketing import create_marketing_crew

def lambda_handler(event, context):
    print("--- CrewAI Multi-Agent Handler Started ---")
    
    # HTTP エンドポイントからの呼び出しを想定
    body = event.get('body', '{}')
    if isinstance(body, str):
        payload = json.loads(body)
    else:
        payload = body

    target_product = payload.get("target_product", "新しい健康飲料")
    
    try:
        crew = create_marketing_crew()
        result = crew.kickoff(inputs={"target_product": target_product})
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "CrewAI execution successful",
                "target_product": target_product,
                "result": str(result)
            }, ensure_ascii=False)
        }
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal Server Error",
                "details": str(e)
            }, ensure_ascii=False)
        }
