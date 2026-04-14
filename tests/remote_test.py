import urllib.request
import json
import os

def test_chat():
    url = "https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat"
    api_key = "vKi3EE5VUn76kdNFioDvtaoLtmuPKBz5FaesXwC9"
    payload = {
        "message": "AWS LLMOpsのメリットを一つ教えて、語尾に注目して答えて。",
        "session_id": "test-zura-session"
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    print(f"Testing URL: {url}")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            print(f"Status Code: {status}")
            
            # Save to file to avoid terminal encoding issues
            with open("test_output.json", "w", encoding="utf-8") as f:
                f.write(body)
            
            print("Response Body saved to test_output.json")
            # Also try to print to stdout safely
            parsed = json.loads(body)
            print(f"Prompt Source: {parsed.get('prompt_source')}")
            print(f"Trace ID: {parsed.get('trace_id')}")
            
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(f"Error details: {e.read().decode('utf-8')}")

if __name__ == "__main__":
    test_chat()
