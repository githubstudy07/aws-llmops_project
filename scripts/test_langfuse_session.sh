#!/bin/bash

# Langfuse Session Grouping Test Script
# このスクリプトは、同じ thread_id で複数回 API をコールし、
# Langfuse Dashboard で trace がセッションとしてグループ化されているか確認します。

set -e

# ========================================
# 設定
# ========================================
API_ENDPOINT="https://4cxepz44c1.execute-api.ap-northeast-1.amazonaws.com/Prod/chat"
API_KEY="${CHAT_API_KEY}"  # 環境変数から取得
THREAD_ID="session-test-$(date +%s)"
NUM_REQUESTS=3

echo "======================================"
echo "Langfuse Session Grouping Test"
echo "======================================"
echo "API Endpoint: $API_ENDPOINT"
echo "Thread ID: $THREAD_ID"
echo "Number of Requests: $NUM_REQUESTS"
echo ""

# ========================================
# API キーの確認
# ========================================
if [ -z "$API_KEY" ]; then
    echo "❌ ERROR: CHAT_API_KEY environment variable is not set"
    echo "   Please set it before running this test:"
    echo "   export CHAT_API_KEY='your-api-key'"
    exit 1
fi

echo "✅ API Key configured"
echo ""

# ========================================
# テストリクエスト実行
# ========================================
echo "Starting $NUM_REQUESTS test requests with same thread_id..."
echo ""

for i in $(seq 1 $NUM_REQUESTS); do
    echo "Request $i/$NUM_REQUESTS"

    REQUEST_BODY=$(cat <<EOF
{
    "message": "Test message $i - testing session grouping. Can you confirm this is request number $i?",
    "thread_id": "$THREAD_ID"
}
EOF
)

    RESPONSE=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $API_KEY" \
        -d "$REQUEST_BODY")

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $API_KEY" \
        -d "$REQUEST_BODY")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "  ✅ HTTP $HTTP_CODE"
        # レスポンス例を表示（最初のリクエストのみ）
        if [ $i -eq 1 ]; then
            echo "  Response (first 200 chars):"
            echo "  $(echo $RESPONSE | cut -c1-200)..."
        fi
    else
        echo "  ❌ HTTP $HTTP_CODE"
        echo "  Response: $RESPONSE"
        exit 1
    fi

    # リクエスト間の待機（トレース送信待ち）
    if [ $i -lt $NUM_REQUESTS ]; then
        echo "  Waiting 2 seconds before next request..."
        sleep 2
    fi
    echo ""
done

echo "======================================"
echo "✅ All requests completed successfully!"
echo "======================================"
echo ""
echo "📊 Next steps to verify session grouping:"
echo "1. Open Langfuse Dashboard: https://us.cloud.langfuse.com"
echo "2. Go to Sessions tab"
echo "3. Search for thread_id: $THREAD_ID"
echo "4. Confirm that $NUM_REQUESTS traces are grouped under this session"
echo ""
echo "🔗 Session ID to search for: $THREAD_ID"
echo ""
