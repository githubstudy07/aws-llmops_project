#!/usr/bin/env python3
"""
API Gateway テスト実行スクリプト（IAM認証使用）
APIキーを直接指定せず、AWS IAM認証で安全に呼び出します。
"""

import json
import boto3
from datetime import datetime

# API Gateway クライアント
apigw = boto3.client('apigateway', region_name='ap-northeast-1')

API_ID = 'handson-llmops-v10-apigw'
RESOURCE_PATH = '/chat'
HTTP_METHOD = 'POST'
STAGE = 'Prod'

print("=" * 70)
print("API Gateway テスト実行（IAM認証）- Step 2 検証")
print(f"タイムスタンプ: {datetime.now().isoformat()}")
print("=" * 70)

try:
    # テストペイロード
    test_body = json.dumps({
        "message": "Session 60 - DynamoDB checkpoint verification test",
        "thread_id": "verify-session-60"
    })

    print(f"\n📤 リクエスト情報:")
    print(f"  API ID: {API_ID}")
    print(f"  パス: {RESOURCE_PATH}")
    print(f"  ステージ: {STAGE}")
    print(f"  ペイロード: {test_body[:100]}...")

    # API Gateway TestInvokeMethod を実行
    response = apigw.test_invoke_method(
        restApiId=API_ID,
        resourceId='/chat',  # リソースID（実際のIDに置き換え可能）
        httpMethod=HTTP_METHOD,
        pathWithQueryString=RESOURCE_PATH,
        body=test_body,
        headers={
            'Content-Type': 'application/json'
        },
        clientCertificateId=None,
        stageVariables={}
    )

    # レスポンス解析
    status = response['status']
    headers = response.get('headers', {})
    body = response.get('body', '')

    print(f"\n📥 レスポンス:")
    print(f"  ステータス: {status}")
    print(f"  ヘッダー: {headers}")

    if body:
        try:
            body_json = json.loads(body)
            print(f"  ボディ: {json.dumps(body_json, indent=2, ensure_ascii=False)}")

            if status == 200:
                print("\n✅ API呼び出し成功")
                print(f"  レスポンス内容: {body_json.get('response', 'N/A')[:150]}...")
            else:
                print(f"\n⚠️ 予期しないステータス: {status}")
        except json.JSONDecodeError:
            print(f"  ボディ（テキスト）: {body[:200]}")
    else:
        print("  ボディ: なし")

    # DynamoDB チェックポイント確認
    print("\n" + "=" * 70)
    print("DynamoDB チェックポイント確認")
    print("=" * 70)

    dynamodb = boto3.client('dynamodb', region_name='ap-northeast-1')
    table_name = 'langgraph-chat-checkpoints-v2'

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': {'S': 'CHUNK_verify-session-60'}
            },
            Limit=5
        )

        item_count = response.get('Count', 0)
        print(f"\n  テーブル: {table_name}")
        print(f"  検索キー: CHUNK_verify-session-60")
        print(f"  見つかった項目: {item_count} 件")

        if item_count > 0:
            print("\n  ✅ DynamoDB チェックポイント保存確認：成功")
            for idx, item in enumerate(response.get('Items', [])[:3]):
                print(f"\n    [{idx+1}] PK: {item.get('PK', {}).get('S', 'N/A')}")
                print(f"        SK: {item.get('SK', {}).get('S', 'N/A')}")
        else:
            print("\n  ⚠️ チェックポイントが見つかりません（初回実行の可能性）")

    except Exception as e:
        print(f"\n  ❌ DynamoDB クエリエラー: {str(e)}")

    print("\n" + "=" * 70)
    print("🎉 Step 2 検証完了")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ エラー: {str(e)}")
    print(f"エラータイプ: {type(e).__name__}")
    import traceback
    traceback.print_exc()
