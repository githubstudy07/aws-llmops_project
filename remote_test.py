import boto3
import requests
import json
import uuid

def get_api_endpoint():
    cf = boto3.client("cloudformation", region_name="ap-northeast-1")
    stack = cf.describe_stacks(StackName="handson-llmops-vfinal")["Stacks"][0]
    for output in stack["Outputs"]:
        if output["OutputKey"] == "ChatApiEndpoint":
            return output["OutputValue"]
    return None

def test_api():
    url = get_api_endpoint()
    if not url:
        print("API Endpoint not found.")
        return

    print(f"Testing API Endpoint: {url}")
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    
    # 1st request: Tell name
    payload1 = {
        "input": "私の名前はナオジです。覚えておいてください。",
        "thread_id": session_id
    }
    print(f"\n--- Request 1 (Context Setting) ---")
    response1 = requests.post(url, json=payload1)
    print(f"Status: {response1.status_code}")
    print(f"Response: {response1.json().get('response')}")

    # 2nd request: Ask name (to verify persistence)
    payload2 = {
        "input": "私の名前は何ですか？",
        "thread_id": session_id
    }
    print(f"\n--- Request 2 (Persistence Verification) ---")
    response2 = requests.post(url, json=payload2)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.json().get('response')}")

if __name__ == "__main__":
    test_api()
