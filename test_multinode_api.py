#!/usr/bin/env python3
# Test script for Phase 10-5-7-A Multi-node LangGraph
import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_ENDPOINT = "https://y4jp7l4u6j.execute-api.ap-northeast-1.amazonaws.com/Prod/chat"
API_KEY_HEADER = "x-api-key"
API_KEY = "YOUR_API_KEY_HERE"  # Set via environment or AWS Secrets

def test_multinode_turn1(query: str = "latest AI trends", thread_id: str = "multinode-test-001"):
    """Test Turn 1: Full execution (research → analysis → report)"""
    print(f"\n{'='*60}")
    print(f"[TURN 1] Multi-node Execution Test")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Thread ID: {thread_id}")

    payload = {
        "query": query,
        "thread_id": thread_id
    }

    headers = {
        "Content-Type": "application/json",
        API_KEY_HEADER: API_KEY
    }

    print(f"\nSending request to: {API_ENDPOINT}")
    start_time = time.time()

    try:
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=60)
        elapsed = time.time() - start_time

        print(f"\n📊 Response Status: {response.status_code}")
        print(f"⏱️  Elapsed Time: {elapsed:.2f}s")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS")
            print(f"Thread ID: {data.get('thread_id')}")
            print(f"Query: {data.get('query')}")
            print(f"Multinode Status: {data.get('multinode_status')}")
            print(f"Final Report Length: {len(data.get('final_report', ''))}")
            print(f"\nFinal Report (first 300 chars):\n{data.get('final_report', '')[:300]}...")
            return True, elapsed, data
        else:
            print(f"\n❌ FAILED")
            print(f"Response: {response.text}")
            return False, elapsed, None

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ ERROR: {str(e)}")
        print(f"⏱️  Elapsed Time: {elapsed:.2f}s")
        return False, elapsed, None


def test_multinode_turn2(query: str = "most important point from previous analysis", thread_id: str = "multinode-test-001"):
    """Test Turn 2: State restoration + incremental execution"""
    print(f"\n{'='*60}")
    print(f"[TURN 2] State Restoration Test")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Thread ID: {thread_id} (same as Turn 1)")

    payload = {
        "query": query,
        "thread_id": thread_id
    }

    headers = {
        "Content-Type": "application/json",
        API_KEY_HEADER: API_KEY
    }

    print(f"\nSending request to: {API_ENDPOINT}")
    start_time = time.time()

    try:
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=60)
        elapsed = time.time() - start_time

        print(f"\n📊 Response Status: {response.status_code}")
        print(f"⏱️  Elapsed Time: {elapsed:.2f}s (should be faster than Turn 1)")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS")
            print(f"Thread ID: {data.get('thread_id')}")
            print(f"Query: {data.get('query')}")
            print(f"Multinode Status: {data.get('multinode_status')}")
            print(f"\nFinal Report (first 300 chars):\n{data.get('final_report', '')[:300]}...")
            return True, elapsed, data
        else:
            print(f"\n❌ FAILED")
            print(f"Response: {response.text}")
            return False, elapsed, None

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ ERROR: {str(e)}")
        return False, elapsed, None


def main():
    print(f"\n{'='*80}")
    print(f"Phase 10-5-7-A: Multi-node LangGraph Verification Test")
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"{'='*80}")

    # Turn 1: Full execution
    success1, elapsed1, data1 = test_multinode_turn1(
        query="latest developments in generative AI",
        thread_id="multinode-verify-001"
    )

    # Wait a moment
    time.sleep(2)

    # Turn 2: State restoration
    success2, elapsed2, data2 = test_multinode_turn2(
        query="what are the most important findings?",
        thread_id="multinode-verify-001"
    )

    # Summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Turn 1 (Full Execution): {'✅ PASS' if success1 else '❌ FAIL'} - {elapsed1:.2f}s")
    print(f"Turn 2 (State Restore):  {'✅ PASS' if success2 else '❌ FAIL'} - {elapsed2:.2f}s")

    if success1 and success2:
        print(f"\n✅ All tests passed!")
        print(f"\nExpected verification points:")
        print(f"  [ ] Check CloudWatch logs for node execution order (research → analysis → report)")
        print(f"  [ ] Check Langfuse Dashboard for 15-span hierarchy (3 parent + 12 child)")
        print(f"  [ ] Check DynamoDB checkpoints table for state persistence")
        print(f"  [ ] Verify Langfuse session grouping by thread_id")
        return 0
    else:
        print(f"\n❌ Some tests failed. Check logs and API endpoint configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
