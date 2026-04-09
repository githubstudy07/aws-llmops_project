import boto3
import json

dynamodb = boto3.client("dynamodb", region_name="ap-northeast-1")
try:
    response = dynamodb.list_tables()
    print(json.dumps(response["TableNames"], indent=2))
except Exception as e:
    print(f"Error: {e}")
