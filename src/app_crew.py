import json

def lambda_handler(event, context):
    """
    生存確認および設定検証用の最小構成ハンドラー
    """
    body_data = {}
    if "body" in event and event["body"]:
        try:
            body_data = json.loads(event["body"])
        except:
            body_data = {"raw": event["body"]}

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
                "runtime": "python:3.12 (AL2023)"
            }
        })
    }
