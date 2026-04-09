import boto3
import json
from botocore.config import Config

"""
Phase 1: Bedrock 基礎 - Amazon Nova Micro 呼び出し
このスクリプトは、東京リージョン (ap-northeast-1) から Bedrock の Amazon Nova Micro モデルを呼び出し、応答を取得します。

### セキュリティリスク
- 認証情報のハードコード: AWS アクセスキーをスクリプト内に記述しないでください。
  開発時は IAM ロール、または AWS CLI (`aws configure`) で設定したプロファイルを利用してください。
- 最小権限: 利用するモデルのみを許可する IAM ポリシーを使用してください。

### 課金リスク (Cost Monitoring)
- Amazon Nova Micro は現在、入力/出力トークンごとの従量課金です。
- 想定外の長い応答を防ぐために `maxNewTokens` を指定しています。
- 料金目安 (100万トークンあたり): 入力 ~$0.04 / 出力 ~$0.14
"""

# 実行リージョンの指定
REGION = "ap-northeast-1"
# モデル ID (Amazon Nova Micro)
# Note: 東京リージョンで直接有効でない場合は、クロスリージョン推論の推論プロファイル ID を使用できます。
MODEL_ID = "amazon.nova-micro-v1:0"

# タイムアウト設定 (Nova モデルは処理に時間がかかる場合があるため、長めに設定)
config = Config(
    read_timeout=300,  # 5分
    retries={'max_attempts': 3}
)

def invoke_nova_micro():
    # Bedrock Runtime クライアントの初期化
    client = boto3.client("bedrock-runtime", region_name=REGION, config=config)

    # リクエストペイロード (Converse API 互換の構造)
    payload = {
        "system": [{"text": "あなたは簡潔に回答する技術アシスタントです。"}],
        "messages": [
            {
                "role": "user",
                "content": [{"text": "AWS Bedrock とは何ですか？2行で説明してください。"}]
            }
        ],
        "inferenceConfig": {
            "maxNewTokens": 300,  # 課金抑制のための最大トークン数制限
            "temperature": 0.5,
            "topP": 0.9
        }
    }

    try:
        print(f"--- モデル '{MODEL_ID}' を呼び出しています (リージョン: {REGION}) ---")
        response = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )

        # レスポンスの解析
        result = json.loads(response["body"].read())
        output_text = result["output"]["message"]["content"][0]["text"]
        
        print("\n[AIからの回答]")
        print(output_text)
        
        # 使用料情報の出力 (コスト意識を高めるため)
        usage = result.get("usage", {})
        print(f"\n--- 使用トークン数 ---")
        print(f"入力: {usage.get('inputTokens', 0)}")
        print(f"出力: {usage.get('outputTokens', 0)}")

    except Exception as e:
        print(f"\n[エラーが発生しました]")
        print(f"詳細: {e}")
        print("ヒント: IAM 権限が正しく設定されているか、東京リージョンでモデルが利用可能か確認してください。")

if __name__ == "__main__":
    invoke_nova_micro()
