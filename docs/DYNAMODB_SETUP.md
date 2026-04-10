# DynamoDB セットアップガイド

## 1. 概要
このガイドは、`aws-llmops_project` で使用する DynamoDB テーブルの作成方法と必要な IAM 権限について説明します。

## 2. 必要な IAM 権限の追加
`AccessDeniedException` (権限不足) が発生した場合、以下の手順に従ってください。

1. **AWS コンソール** にログインします。
2. **IAM** → **Users (ユーザー)** を選択します。
3. 今回使用しているユーザー (`dify-github-actions-user`) を選択します。
4. **Permissions (許可)** タブで **Add permissions (許可を追加)** → **Create inline policy (インラインポリシーを作成)** をクリックします。
5. **JSON** タブに切り替えて、以下の内容を貼り付けます。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:DescribeTable",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:UpdateItem",
                "dynamodb:ListTables",
                "dynamodb:BatchWriteItem",
                "dynamodb:BatchGetItem"
            ],
            "Resource": "*"
        }
    ]
}
```

6. **Review policy (ポリシーを確認)** をクリックし、名前（例: `DynamoDBBasicPolicy`）を入力して **Create policy (ポリシーを作成)** で完了です。

## 3. テーブルの作成方法
権限の追加が完了したら、以下のコマンドを実行します。

```bash
# uv を使用している場合
python create_dynamodb_table.py
```

このスクリプトは以下の設定でテーブルを作成します：
- **テーブル名**: `chat-history-simple`
- **パーティションキー (`session_id`)**: 会話ごとにデータを区別するための ID (String)。
- **ソートキー (`timestamp`)**: 同じ会話内でメッセージを時系列に並べるための項目 (String)。
- **Billing Mode**: **On-Demand (PAY_PER_REQUEST)**
  - 使った分だけ課金されるモードです。学習用途や小規模開発では最もコスト効率が良く、安全です。

## 4. 動作確認
テーブル作成後、以下のスクリプトを実行して正しく読み書きできるか確認してください。

```bash
python dynamodb_chat_history.py
```

成功すると、メッセージが保存され、履歴として表示されます。
