import boto3
import json

dynamodb = boto3.client("dynamodb", region_name="ap-northeast-1")

for table in ["handson-langgraph-checkpoints", "handson-langgraph-writes"]:
    try:
        desc = dynamodb.describe_table(TableName=table)
        print(f"--- {table} ---")
        print(json.dumps(desc["Table"]["KeySchema"], indent=2))
        print(json.dumps(desc["Table"]["AttributeDefinitions"], indent=2))
    except Exception as e:
        print(f"Error describing {table}: {e}")
