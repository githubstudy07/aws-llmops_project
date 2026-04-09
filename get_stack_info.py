import boto3
import json

cf = boto3.client("cloudformation", region_name="ap-northeast-1")
try:
    response = cf.describe_stacks(StackName="aws-sam-cli-managed-default")
    print(json.dumps(response["Stacks"][0]["Outputs"], indent=2))
except Exception as e:
    print(f"Error: {e}")
