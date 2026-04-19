import urllib.request
import json
import uuid

# Configuration
ENDPOINT = "https://qr8zkld942.execute-api.ap-northeast-1.amazonaws.com/v1/chat"
THREAD_ID = f"test-thread-{uuid.uuid4().hex[:8]}"

def post(msg: str, tid: str) -> dict:
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"message": msg, "thread_id": tid}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

print(f"--- Round 1: Sending Name (thread_id: {THREAD_ID}) ---")
try:
    r1 = post("私の名前はナオジです。覚えてください。", THREAD_ID)
    print(f"Response: {json.dumps(r1, ensure_ascii=False)}")
    
    print(f"\n--- Round 2: Asking Name (thread_id: {THREAD_ID}) ---")
    r2 = post("私の名前は何でしたか？", THREAD_ID)
    print(f"Response: {json.dumps(r2, ensure_ascii=False)}")
    
    if "ナオジ" in r2.get("reply", ""):
        print("\nSUCCESS: Context persisted via DynamoDB checkpointer.")
    else:
        print("\nFAILURE: Context NOT persisted.")
except Exception as e:
    print(f"\nERROR occurred: {str(e)}")
