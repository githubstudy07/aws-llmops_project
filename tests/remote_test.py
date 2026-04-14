import urllib.request
import json
import os
import time

def test_chat():
    url = "https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat"
    api_key = "vKi3EE5VUn76kdNFioDvtaoLtmuPKBz5FaesXwC9"
    # Create a unique session ID to avoid history interference
    session_id = f"test-session-{int(time.time())}"
    payload = {
        "message": "AWS LLMOpsのメリットを一つ教えて、語尾に注目して答えて。",
        "session_id": session_id
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    print(f"Testing URL: {url}")
    print(f"Session ID: {session_id}")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            print(f"Status Code: {status}")
            
            with open("test_output.json", "w", encoding="utf-8") as f:
                f.write(body)
            
            parsed = json.loads(body)
            print(f"Prompt Source: {parsed.get('prompt_source')}")
            print(f"Trace ID: {parsed.get('trace_id')}")
            print(f"Response: {parsed.get('response')[:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(f"Error details: {e.read().decode('utf-8')}")

if __name__ == "__main__":
    test_chat()
