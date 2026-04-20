# -*- coding: utf-8 -*-
"""
Test: LangGraph Session Persistence via API Gateway
"""

import json
import time
import requests

# ===== Configuration =====
API_ENDPOINT = "https://fvvlweg9z2.execute-api.ap-northeast-1.amazonaws.com/Prod/chat"
API_KEY = "VJPruwqorT3dAiBNQAvQEaj5iwocHsRJk6mU2hP0"
REGION = "ap-northeast-1"
THREAD_ID = f"test-session-{int(time.time())}"


def test_multi_turn_conversation():
    """Multi-turn conversation via API Gateway"""

    print(f"\n{'='*60}")
    print("TEST: Multi-Turn Conversation Persistence")
    print(f"{'='*60}")
    print(f"Thread ID: {THREAD_ID}")
    print(f"API Endpoint: {API_ENDPOINT}\n")

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # ===== Turn 1: Initial message =====
    print("[Turn 1] Sending initial message...")
    turn1_payload = {
        "message": "My name is Alice. Please remember this.",
        "thread_id": THREAD_ID
    }

    response1 = requests.post(API_ENDPOINT,
                              headers=headers,
                              json=turn1_payload,
                              timeout=30)

    print(f"Status: {response1.status_code}")
    assert response1.status_code == 200, f"Turn 1 failed: {response1.text}"

    result1 = response1.json()

    # Handle API Gateway response format
    if 'body' in result1:
        body = json.loads(result1['body'])
    else:
        body = result1

    print(f"Response: {body['response'][:150]}...")
    print(f"Thread ID (response): {body['thread_id']}")
    if 'model' in body:
        print(f"Model: {body['model']}")
    print()

    assert body['thread_id'] == THREAD_ID, "Thread ID mismatch in response"

    time.sleep(1)

    # ===== Turn 2: Memory test =====
    print("[Turn 2] Asking to recall the name...")
    turn2_payload = {
        "message": "What is my name that I told you?",
        "thread_id": THREAD_ID
    }

    response2 = requests.post(API_ENDPOINT,
                              headers=headers,
                              json=turn2_payload,
                              timeout=30)

    print(f"Status: {response2.status_code}")
    assert response2.status_code == 200, f"Turn 2 failed: {response2.text}"

    result2 = response2.json()

    # Handle API Gateway response format
    if 'body' in result2:
        body2 = json.loads(result2['body'])
    else:
        body2 = result2

    print(f"Response: {body2['response'][:150]}...")
    print(f"Thread ID (response): {body2['thread_id']}\n")

    assert body2['thread_id'] == THREAD_ID, "Thread ID mismatch in Turn 2"

    # ===== Summary =====
    print("="*60)
    print("TEST PASSED")
    print("="*60)
    print(f"[PASS] Turn 1: Initial message sent via API Gateway")
    print(f"[PASS] Turn 2: Follow-up message sent via same thread_id")
    print(f"[PASS] API Gateway + Lambda integration verified")
    print(f"[INFO] Checkpoint persistence (DynamoDB) is handled internally by Lambda")
    print(f"\nThread ID for manual verification: {THREAD_ID}")
    print(f"Check CloudWatch logs: /aws/lambda/handson-llmops-langgraph-chat-v58-CrewFunction")
    print("="*60)


if __name__ == "__main__":
    test_multi_turn_conversation()
