import json
import os

def lambda_handler(event, context):
    """
    [ISOLATION TEST] 極限まで機能を削ぎ落とした最小構成
    """
    print("--- ISOLATION TEST: Lambda Handler Started ---")
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Hello from minimal Lambda!",
            "status": "booted",
            "region": os.environ.get("AWS_REGION")
        })
    }
