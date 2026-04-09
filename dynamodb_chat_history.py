import boto3
from datetime import datetime
from botocore.exceptions import ClientError

"""
Phase 2: DynamoDB 基礎 - 会話履歴の保存と取得
このスクリプトは、DynamoDB を使用して AI エージェントの会話履歴を取り扱う方法を学びます。

### 理由 (Why?)
AI (Bedrock Nova Micro) は一回ごとに内容を忘れてしまうため、
「さっき何を言ったか」をデータベース（DynamoDB）に覚えさせる必要があります。

### 目的 (Purpose)
- プログラムからテーブルを操作 (データの読み書き) できるようにする。
- session_id と timestamp を使って、会話を時系列で取り出せるようにする。

### 課金リスク (Billing Risk)
- DynamoDB は「オンデマンド (PAY_PER_REQUEST)」モードを推奨します。
- オンデマンドは「使った分だけ」課金されます（100万回の読み書きで約数円程度）。
- 「プロビジョニング済み (PROVISIONED)」は使用しなくても固定料金がかかるため、初学者は避けてください。
"""

# 設定
REGION = "ap-northeast-1"
TABLE_NAME = "chat-history-simple"

def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=REGION)

def save_chat_message(session_id, role, content, model_id="amazon.nova-micro-v1:0"):
    """
    会話メッセージを 1 件保存します。
    - session_id (パーティションキー): 会話の識別子 (例: sess-001)
    - timestamp (ソートキー): メッセージの送信日時 (ISO 8601 形式)
    """
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)
    
    timestamp = datetime.utcnow().isoformat()
    
    try:
        table.put_item(
            Item={
                "session_id": session_id,
                "timestamp": timestamp,
                "role": role,          # 'user' または 'assistant'
                "content": content,    # メッセージ本文
                "model_id": model_id   # 使用した AI モデル名
            }
        )
        print(f"[{role}] メッセージを保存しました: {content[:15]}...")
    except ClientError as e:
        print(f"保存エラー: {e.response['Error']['Message']}")
        print(f"ヒント: テーブル '{TABLE_NAME}' が AWS 上に存在するか確認してください。")

def get_chat_history(session_id):
    """
    特定の session_id に紐づく会話履歴をすべて取得します。
    """
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("session_id").eq(session_id)
        )
        items = response.get("Items", [])
        
        print(f"\n--- セッション '{session_id}' の履歴 (合計: {len(items)}件) ---")
        for item in items:
            print(f"[{item['role']}] {item['content']}")
        return items
    except ClientError as e:
        print(f"取得エラー: {e.response['Error']['Message']}")
        return []

if __name__ == "__main__":
    # テスト実行例
    # 注意: このスクリプトを動かすには、AWS コンソールで 'chat-history-simple' テーブルを作成しておく必要があります。
    print("--- DynamoDB 操作テスト ---")
    session_id = "test-session-001"
    
    # ユーザー発言の保存
    save_chat_message(session_id, "user", "こんにちは。DynamoDB のテストです。")
    
    # アシスタント返答の保存 (シミュレーション)
    save_chat_message(session_id, "assistant", "こんにちは！履歴に保存されました。")
    
    # 履歴の取得
    get_chat_history(session_id)
