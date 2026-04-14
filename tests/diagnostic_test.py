import urllib.request
import json

def test_diagnostic():
    url = "https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat"
    api_key = "vKi3EE5VUn76kdNFioDvtaoLtmuPKBz5FaesXwC9"
    payload = {
        "diagnostic": True
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    print(f"Testing Diagnostic URL: {url}")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            print(f"Status Code: {status}")
            print(f"Response: {body}")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(f"Error details: {e.read().decode('utf-8')}")

if __name__ == "__main__":
    test_diagnostic()
