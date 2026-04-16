import boto3
import requests
import json
import uuid
import time

def get_api_endpoint():
    cf = boto3.client("cloudformation", region_name="ap-northeast-1")
    stack = cf.describe_stacks(StackName="handson-llmops-vfinal")["Stacks"][0]
    for output in stack["Outputs"]:
        if output["OutputKey"] == "ChatApiEndpoint":
            return output["OutputValue"]
    return None

def test_archivist():
    url = get_api_endpoint()
    api_key = "nOQNrxNTym9hfL8YbhYWq1fJpRs7NYSa1EPZy0dq"
    
    if not url:
        print("API Endpoint not found.")
        return

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    
    content_id = f"remote_test_{uuid.uuid4().hex[:6]}"
    topic = "AWS Bedrock Nova Micro performance in 2026"
    
    # Payload must match app_crew.py's expected keys
    payload = {
        "topic": topic,
        "content_id": content_id,
        "session_id": f"session-{uuid.uuid4().hex[:6]}"
    }
    
    print(f"Sending request to Archivist...")
    print(f"Payload: {json.dumps(payload)}")
    
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"Response Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response Body: {response.text[:200]}...")
        else:
            print(f"Error Response Body: {response.text}")
    except requests.exceptions.Timeout:
        print("\n⚠️ Request timed out at APIGW level (expected).")
        response = None
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        response = None

    # Verify DynamoDB directly
    print("\n--- Verifying DynamoDB ---")
    db = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = db.Table("handson-research-archives-v2")
    
    # Wait and retry DynamoDB check a few times
    for i in range(8):
        print(f"Polling DynamoDB (attempt {i+1})...")
        item = table.get_item(Key={"content_id": content_id}).get("Item")
        if item:
            print("✅ Data successfully saved to DynamoDB!")
            print(f"Stored Content (first 100 chars): {item.get('content', '')[:100]}...")
            return
        time.sleep(20)
    
    print("❌ Data NOT found in DynamoDB after multiple attempts.")

if __name__ == "__main__":
    test_archivist()
