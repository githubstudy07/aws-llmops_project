import boto3
from botocore.exceptions import ClientError
import time

"""
DynamoDB テーブル作成スクリプト (`create_dynamodb_table.py`)
- 会話履歴保存用のテーブル 'chat-history-simple' を作成します。
- 課金リスクを抑えるため「オンデマンド (PAY_PER_REQUEST)」モードを使用します。
"""

REGION = "ap-northeast-1"
TABLE_NAME = "chat-history-simple"

def create_chat_history_table():
    dynamodb = boto3.client("dynamodb", region_name=REGION)

    print(f"--- テーブル '{TABLE_NAME}' の作成を開始します (リージョン: {REGION}) ---")

    try:
        # テーブル作成のリクエスト
        response = dynamodb.create_table(
            TableName=TABLE_NAME,
            # キーの定義
            AttributeDefinitions=[
                {
                    "AttributeName": "session_id",
                    "AttributeType": "S"  # String
                },
                {
                    "AttributeName": "timestamp",
                    "AttributeType": "S"  # String (ISO 8601)
                }
            ],
            # キーの種類
            KeySchema=[
                {
                    "AttributeName": "session_id",
                    "KeyType": "HASH"  # パーティションキー
                },
                {
                    "AttributeName": "timestamp",
                    "KeyType": "RANGE" # ソートキー
                }
            ],
            # 課金モード: オンデマンド (初学者に安全)
            BillingMode="PAY_PER_REQUEST"
        )
        
        print(f"作成リクエストを送信しました。ステータス: {response['TableDescription']['TableStatus']}")
        
        # テーブルが利用可能 (ACTIVE) になるまで待機
        print("テーブルが ACTIVE になるまで待機しています...", end="", flush=True)
        while True:
            status = dynamodb.describe_table(TableName=TABLE_NAME)["Table"]["TableStatus"]
            if status == "ACTIVE":
                print("\n✅ テーブル作成完了！利用可能です。")
                break
            print(".", end="", flush=True)
            time.sleep(2)

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceInUseException":
            print(f"ℹ️ テーブル '{TABLE_NAME}' は既に存在します。そのまま使用できます。")
        elif error_code == "AccessDeniedException":
            print(f"\n❌ 権限エラー: AWS ユーザーに DynamoDB の操作権限がありません。")
            print("【対策】'docs/DYNAMODB_SETUP.md' を参照して IAM 権限を追加してください。")
        else:
            print(f"\n❌ エラーが発生しました: {e.response['Error']['Message']}")

if __name__ == "__main__":
    create_chat_history_table()
