#!/usr/bin/env python3
"""
CloudWatch Logs 自動解析スクリプト
Lambda実行ログからDynamoDBチェックポイント動作を確認
"""

import boto3
import json
from datetime import datetime, timedelta

# CloudWatch Logs クライアント
logs = boto3.client('logs', region_name='ap-northeast-1')

LOG_GROUP_NAME = '/aws/lambda/langgraph-chat-v58-chat'
ONE_DAY_AGO = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)

print("=" * 70)
print("CloudWatch Logs 解析 - Step 2 検証")
print(f"ログチーム: {LOG_GROUP_NAME}")
print(f"分析期間: 過去24時間")
print("=" * 70)

try:
    response = logs.filter_log_events(
        logGroupName=LOG_GROUP_NAME,
        startTime=ONE_DAY_AGO,
        limit=100
    )

    events = response.get('events', [])

    if not events:
        print("\n⚠️ 過去1時間のログがありません")
        print("理由: まだLambda関数が呼び出されていない可能性があります")
        print("\n推奨:")
        print("  1. remote_verify.py でAPI経由でテストするか")
        print("  2. API Gatewayエンドポイントを実際に呼び出すか")
        print("  3. もっと長い期間（--since 7h など）で確認")
    else:
        print(f"\n✅ {len(events)} 件のログイベントを検出しました\n")

        # ログ内容の解析
        checkpoint_count = 0
        error_count = 0
        success_count = 0

        for event in events[:20]:  # 最新20件を表示
            msg = event['message']
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)

            print(f"[{timestamp.isoformat()}]")
            print(f"  {msg[:100]}")

            if 'checkpoint' in msg.lower() or 'dynamodb' in msg.lower():
                checkpoint_count += 1
            if 'error' in msg.lower() or 'exception' in msg.lower():
                error_count += 1
            if '200' in msg or 'success' in msg.lower():
                success_count += 1
            print()

        # サマリー
        print("=" * 70)
        print("📊 ログサマリー")
        print("=" * 70)
        print(f"  DynamoDB/チェックポイント関連: {checkpoint_count} 件")
        print(f"  エラー検出: {error_count} 件")
        print(f"  成功パターン: {success_count} 件")

        if error_count > 0:
            print("\n❌ エラーが検出されました。詳細をご確認ください。")
        else:
            print("\n✅ Step 2検証: DynamoDBチェックポイント保存が正常に機能している可能性があります")

except Exception as e:
    print(f"\n❌ エラー: {str(e)}")
    print(f"エラータイプ: {type(e).__name__}")
