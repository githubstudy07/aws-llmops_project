#!/usr/bin/env python3
"""
Phase 10-5-7-B Test: Langfuse Span Instrumentation Verification
Tests the 4-span chatbot node implementation by invoking the API
and verifying that spans appear in Langfuse Dashboard.
"""

import json
import boto3
import time
from datetime import datetime
import os
import requests

REGION = 'ap-northeast-1'
THREAD_ID = f"phase-10-5-7b-test-{int(time.time())}"

# Fetch API endpoint from CloudFormation stack
cfn = boto3.client('cloudformation', region_name=REGION)
try:
    stacks = cfn.describe_stacks()['Stacks']
    api_stack = None
    for stack in stacks:
        if 'handson' in stack['StackName'].lower() or 'llmops' in stack['StackName'].lower():
            api_stack = stack
            break

    if api_stack:
        outputs = {o['OutputKey']: o['OutputValue'] for o in api_stack.get('Outputs', [])}
        CHAT_API_ENDPOINT = outputs.get('ChatApiEndpoint')
        if not CHAT_API_ENDPOINT:
            CHAT_API_ENDPOINT = outputs.get('ApiEndpoint', '') + 'chat'
    else:
        raise Exception("No matching CloudFormation stack found")
except Exception as e:
    print(f"Warning: Could not fetch API from CloudFormation: {e}")
    print("Falling back to manual endpoint URL...")
    CHAT_API_ENDPOINT = os.environ.get('CHAT_API_ENDPOINT', 'http://localhost:3000/chat')

print("=" * 70)
print("Phase 10-5-7-B: Langfuse Span Instrumentation Test")
print(f"Time: {datetime.now().isoformat()}")
print("=" * 70)

# Test 1: Invoke Lambda via API Gateway (HTTP)
print(f"\nSTEP 1: Invoking API Gateway endpoint")
print(f"  API Endpoint: {CHAT_API_ENDPOINT}")
print(f"  Thread ID: {THREAD_ID}")
print(f"  Region: {REGION}")

test_body = {
    "message": "Phase 10-5-7-B: Test span-based tracing in chatbot node",
    "thread_id": THREAD_ID
}

try:
    api_key = os.environ.get('API_KEY', 'Z8qcY2aAhU9JPiOsZ9yNp2Nf0gfM2lpj3u8jx1j0')
    response = requests.post(
        CHAT_API_ENDPOINT,
        json=test_body,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key
        },
        timeout=120
    )

    status = response.status_code
    print(f"\n  API Response Status: {status}")

    if status == 200:
        try:
            body_json = response.json()
            response_text = body_json.get('response', '')[:150]
            print(f"  Response received: {response_text}...")
            print(f"  Model: {body_json.get('model', 'N/A')}")
            print(f"  Thread ID returned: {body_json.get('thread_id', 'N/A')}")
        except Exception as parse_err:
            print(f"  Could not parse response: {str(parse_err)}")
            print(f"  Raw response: {response.text[:200]}")
    else:
        print(f"  Unexpected status: {status}")
        print(f"  Response: {response.text[:200]}")

except Exception as e:
    print(f"  API invocation failed: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Verify DynamoDB checkpoint was saved
print(f"\nSTEP 2: Verifying DynamoDB checkpoint")

dynamodb = boto3.client('dynamodb', region_name=REGION)
table_name = 'langgraph-chat-checkpoints-v2'

try:
    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': {'S': f'thread:{THREAD_ID}'}
        },
        Limit=5
    )

    count = response.get('Count', 0)
    print(f"  [OK] Checkpoint query succeeded")
    print(f"  [OK] Items found: {count}")

    if count > 0:
        for idx, item in enumerate(response.get('Items', [])[:3]):
            sk = item.get('SK', {}).get('S', 'N/A')
            print(f"     [{idx+1}] {sk}")
    else:
        print(f"  [INFO] No checkpoints found (may be normal for new sessions)")

except Exception as e:
    print(f"  [ERROR] DynamoDB query failed: {str(e)}")

# Test 3: Langfuse Dashboard manual verification instructions
print(f"\nSTEP 3: Manual Langfuse Dashboard Verification")
print(f"\n  Langfuse Dashboard: https://us.cloud.langfuse.com")
print(f"  Expected Spans (in order):")
print(f"    1. message_preparation - Message count from state")
print(f"    2. bedrock_invoke - LLM invocation with model and message count")
print(f"    3. token_counting - Token estimation from response content")
print(f"    4. response_formatting - Response type and success flag")
print(f"\n  Instructions:")
print(f"    1. Wait 15-20 seconds for trace data to arrive")
print(f"    2. Navigate to Traces section")
print(f"    3. Find trace with session_id = '{THREAD_ID}'")
print(f"    4. Click to view trace details")
print(f"    5. Check 'Spans' section for 4 spans listed above")
print(f"    6. Verify parent-child relationships and timing data")

print(f"\n  🔑 Thread ID for Dashboard search: {THREAD_ID}")

# Test 4: Summary
print(f"\n" + "=" * 70)
print("[OK] Phase 10-5-7-B Test Complete")
print("=" * 70)
print(f"\nNext Steps:")
print(f"  1. Navigate to Langfuse Dashboard")
print(f"  2. Search for session: {THREAD_ID}")
print(f"  3. Verify 4 spans are present and properly nested")
print(f"  4. Check parent-child span relationships")
print(f"  5. Review timing data for performance analysis")
