import requests
import uuid
import json

endpoint = "https://ux3t2ciln0.execute-api.ap-northeast-1.amazonaws.com/v1/chat"
thread_id = f"test-thread-{uuid.uuid4().hex[:8]}"

print(f"--- Round 1: Sending Name (thread_id: {thread_id}) ---")
payload1 = {
    "thread_id": thread_id,
    "message": "私の名前はナオジです。覚えておいてください。"
}
resp1 = requests.post(endpoint, json=payload1)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text}")

if resp1.status_code == 200:
    print(f"\n--- Round 2: Asking Name (thread_id: {thread_id}) ---")
    payload2 = {
        "thread_id": thread_id,
        "message": "私の名前を覚えていますか？"
    }
    resp2 = requests.post(endpoint, json=payload2)
    print(f"Status: {resp2.status_code}")
    print(f"Response: {resp2.text}")
else:
    print("Round 1 failed. Skipping Round 2.")
