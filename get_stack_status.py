import boto3
import json

cf = boto3.client("cloudformation", region_name="ap-northeast-1")
try:
    response = cf.describe_stacks(StackName="handson-llmops-vfinal")
    print(json.dumps({"Status": response["Stacks"][0]["StackStatus"]}, indent=2))
except Exception as e:
    print(f"Error: {e}")
