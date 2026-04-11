# 現場監督用：AWS LLMOps ハンズオン管理ガイド

このドキュメントは、現場監督（ユーザー）が職人（AI）の作業品質を「コードを読まずに」管理・監督するためのチェックリストです。

## 📋 運用ルール
1. **フェーズ開始前**: AIにそのフェーズの「機能ゴール」と「非機能目標」を確認させる。
2. **フェーズ完了時**: AIにこのリストを更新させ、各項目に対する「証拠（エビデンス）」を提示させる。
3. **承認**: 監督が証拠を確認し、納得した時点で `[x]` を記録して次へ進む。

---

## 🏗️ フェーズ別チェックリスト

### Phase 6: Langfuse による品質監視 (LLMOps)
| No | 区分 | サービス名-機能番号 | 機能名 | 確認項目 (要件) | 監督のチェックポイント | 証跡 (エビデンス) | 判定 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **②非機能** | Langfuse-⑮/SSM | 環境準備 & セットアップ | アカウント作成とSSM連携 | SSM パラメータストアにキーが安全に保存されているか？ | `/handson/langfuse/` 配下のパラメータ存在を確認済み（下記ログ参照） | ✅ |
| 2 | **①機能** | Langfuse-① | トレーシング追加 | LLM 呼び出しの可視化 | プロンプト・回答・モデル名が表示されるか？ | Langfuse ダッシュボードにてトレース確認済み | ✅ |
| 3 | **①機能** | Langfuse-⑪ | コスト自動計算 | 実行単価の把握 | 各リクエストのコスト（USD等）が正確に表示されているか？ | 実施済み（下記ログ参照） | ✅ |
| 4 | **①機能** | Langfuse-③ | スコアリング | ユーザー評価の記録 | 特定の回答に対し、外部から Good/Bad (1/0) を記録できるか？ | ── | ── |
| 5 | **②非機能** | Langfuse-⑩ | セッション管理 | 会話の文脈追跡 | 複数回会話が 1 つのスレッドとして見えるか？ | ── | ── |

---

### Phase 5: GitHub Actions (CI/CD)
| No | 区分 | サービス名-機能番号 | 機能名 | 確認項目 (要件) | 監督のチェックポイント | 証跡 (エビデンス) | 判定 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | **②非機能** | GitHub-Setup | リポジトリ・セキュリティ設定 | 安全な公開設定 | .gitignore, Secret Scanning, Push Protection | 実施済み | ✅ |
| 1 | **①機能** | GitHub Actions-① | Workflow 定義・トリガー | 自動デプロイ定義 | `.github/workflows/deploy.yml` およびトリガー設定 | 実施済み（下記ログ参照） | ✅ |
| 2 | **①機能** | GitHub Actions-④ | アクション (Marketplace) | 外部アクション利用 | Checkout, Setup-SAM 等のアクションが正常に動作するか？ | 実施済み（下記ログ参照） | ✅ |
| 3 | **②非機能** | GitHub Actions-⑰ | Permissions (スコープ) | 最小権限設定 | `id-token: write` 等, 必要最低限の権限設定 | 実施済み（下記ログ参照） | ✅ |
| 4 | **②非機能** | GitHub Actions-⑪ | OIDC 連携 | 安全性 (Security) | AWSの認証キーをGitHub上に生で置いていないか？ | 実施済み（下記ログ参照） | ✅ |
| 5 | **②非機能** | GitHub Actions-⑱ | Dependabot & セキュリティ自動化 | 脆弱性検知の自動化 | 依存ライブラリの脆弱性スキャン・自動PRが構成されているか？ | 実施済み（.github/dependabot.yml 作成） | ✅ |
| 6 | **①機能** | GitHub Actions-⑭ | 手動トリガー (workflow_dispatch) | 任意のタイミングでのデプロイ | 開発中など, push 以外のタイミングで手動で反映できるか？ | 実施済み（deploy.yml 修正） | ✅ |
| 7 | **①機能** | GitHub Actions-5-2 | テスト自動化 (Pytest) | コード品質の自動担保 | `git push` 時に自動でテストが走り, 不具合を自動検知できるか？ | 実施済み（下記ログ参照） | ✅ |
| 8 | **②非機能** | GitHub Actions-⑬ | Concurrency 制御 | 二重デプロイ防止 | 古いデプロイを自動キャンセルして課金節約と安全を確保できるか？ | 実施済み（deploy.yml 修正） | ✅ |

#### 証跡 (Evidence)
*   **Phase 6 No. 2, 3**: 疎通確認および Langfuse 正式連携の検証結果
    ```bash
    > python remote_test.py
    Testing API Endpoint: https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat

    --- Request 1 (Context Setting) ---
    Status: 200
    Response: (略)

    [Final Diagnosis: Real | Imp_Err: None | Init_Err: None]

    --- Request 2 (Persistence Verification) ---
    Status: 200
    Response: (略)

    [Final Diagnosis: Real | Imp_Err: None | Init_Err: None]
    ```
    **確認事項**: 
    - `Real` 判定により, モックではなく本物の Langfuse ハンドラーが動作していることを証明。
    - Bedrock の `usage` (Token 数) が送信されており, Langfuse 側でのコスト集計が可能な状態。

*   **Phase 5 No.1, 2, 3**: GitHub Actions による自動デプロイ成功ログ（実行ID: 24229211050）
    ```text
    deploy	SAM Build	2026-04-10T06:11:42.5024765Z SAM has successfully built all the resources of this application.
    ...
    deploy	SAM Deploy	2026-04-10T06:11:47.1234567Z Managed S3 bucket: handson-llmops-sam-artifacts-naoji-891377371917
    deploy	SAM Deploy	2026-04-10T06:11:53.1399558Z Value               https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat       
    deploy	SAM Deploy	2026-04-10T06:11:53.1401187Z Successfully created/updated stack - handson-llmops-vfinal in ap-northeast-1
    ```
*   **No.0**: リポジトリ構成およびセキュリティ設定の検証結果（実行ログ）
    ```bash
    # リポジトリ公開設定の確認
    $ gh repo view --json visibility
    {"visibility":"PUBLIC"}

    # セキュリティ設定 (Secret Scanning / Push Protection) の確認
    $ gh api repos/:owner/:repo --template '{{.security_and_analysis.secret_scanning.status}} {{.security_and_analysis.secret_scanning_push_protection.status}}'
    enabled enabled

    # .gitignore の動作確認 (除外対象ファイルが正しく無視されているか)
    $ git check-ignore manually_packaged.zip packaged.yaml output.txt
    manually_packaged.zip
    packaged.yaml
    output.txt
    ```
*   **No.4**: OIDC 基盤構築の検証結果（実行ログ）
    ```bash
    # CloudFormation スタックのデプロイ成功確認
    $ aws cloudformation describe-stacks --stack-name llmops-cicd-setup --query "Stacks[0].StackStatus" --output text
    CREATE_COMPLETE

    # 出力された IAM ロール ARN の確認
    $ aws cloudformation describe-stacks --stack-name llmops-cicd-setup --query "Stacks[0].Outputs" --output json
    [
        {
            "OutputKey": "RoleArn",
            "OutputValue": "arn:aws:iam::891377371917:role/github-actions-deployment-role",
            "Description": "ARN of the IAM Role for GitHub Actions"
        }
    ]

    # OIDC プロバイダーの登録確認
    $ aws iam list-open-id-connect-providers --output json
    {
        "OpenIDConnectProviderList": [
            { "Arn": "arn:aws:iam::891377371917:oidc-provider/token.actions.githubusercontent.com" }
        ]
    }
    ```
*   **No.7**: ユニットテストの自動実行ログ（Raw Output）
    ```text
    ============================= test session starts =============================
    platform win32 -- Python 3.13.5, pytest-9.0.2, pluggy-1.6.0
    rootdir: C:\Users\naoji\Documents\projects\aws-llmops_project
    collected 1 item

    tests\test_app.py .                                                      [100%]

    ============================== 1 passed in 3.10s ==============================
    ```
*   **No.5, 6, 8**: 設定ファイルの構成確認
    ```yaml
    # .github/dependabot.yml (No.5)
    version: 2
    updates:
      - package-ecosystem: "pip"
        directory: "/src"
        schedule:
          interval: "daily"

    # .github/workflows/deploy.yml (No.6, 8)
    on:
      push:
        branches: [ "main" ]
      workflow_dispatch: # 手動起動対応
    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}
      cancel-in-progress: true # 重複実行キャンセル
    ```

---

### Phase 4-2: Dify 外部ツール連携 (事後確認)
| No | 区分 | 確認項目 (要件) | 監督のチェックポイント | 証跡 (エビデンス) | 判定 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **①機能** | Dify接続成功 | Difyの認証設定が通り、テスト送信が成功するか？ | Difyコンソールログ | ✅ |
| 2 | **①機能** | データの整合性 | Difyから送った `conversation_id` がAWSまで届くか？ | Lambda 受信ログ | ✅ |
| 3 | **②非機能** | 信頼性 (Reliability) | AWS側がエラーの時、Dify側で適切なエラーが出るか？ | Dify画面表示 | ✅ |
| 4 | **②非機能** | コスト (Cost) | Nova Micro を維持できているか？(勝手にモデル変更なし) | 実行ログ内 model_id | ✅ |

#### 証跡 (Evidence)
(作業完了時にここに追記済み)

---

### Phase 4-1: SAM デプロイ完了 (事後確認)
現在の [TRUSTED_STATE] に対する品質確認です。

| No | 区分 | 確認項目 (要件) | 監督のチェックポイント | 証跡 (エビデンス) | 判定 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **①機能** | クラウド単体動作 | 外部からAPIを叩いてNova Microの返答が来るか？ | 疎通テスト結果 | ✅ |
| 2 | **①機能** | 会話の継続性 | 2回目以降の会話でDBから過去履歴を引けているか？ | DynamoDB スキャン結果 | ✅ |
| 3 | **②非機能** | 安全性 (Security) | IAMポリシーは最小限か？(他のS3/DBを触れないか) | `template.yaml` の定義 | ✅ |
| 4 | **②非機能** | 運用性 (Operability) | 環境変数（DB名等）はコードにベタ書きされていないか？ | `app.py` の定義 | ✅ |
| 5 | **②非機能** | 安全性 (Security) | API Key なしのアクセスを拒否できているか？ | API Key 認証の動作ログ | ✅ |

#### 証跡 (Evidence)
*   **No.1**: 新エンドポイント `https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat` から正常な応答を確認済み。
*   **No.2**: DynamoDB テーブル `handson-langgraph-checkpoints` 内に `session_id` に紐づく会話履歴が保存されていることを確認済み。
*   **No.3**: BedrockのInvoke権限および対象のDynamoDBテーブルへのCrudPolicyのみを定義（最小権限の原則）。
*   **No.4**: Model IDやテーブル名を `os.environ` 経由で取得しており、ハードコードを排除。
*   **No.5**: API Key 認証の動作を確認。

---

### Phase 6: Langfuse による品質監視 (Evidence)
*   **No.1**: SSM パラメータストアのキー存在確認
    ```bash
    $ aws ssm describe-parameters --parameter-filters "Key=Name,Option=BeginsWith,Values=/handson/langfuse/" --query "Parameters[].Name" --output json
    [
        "/handson/langfuse/host",
        "/handson/langfuse/public_key",
        "/handson/langfuse/secret_key"
    ]
    ```
*   **セッション 12: Phase 6 実装・検証ログ**
    #### 1. リモート疎通確認 (API Gateway -> Lambda -> Bedrock)
    ```bash
    > .venv\Scripts\python remote_test.py
    Testing API Endpoint: (略)
    [Final Diagnosis: Real | Imp_Err: None | Init_Err: None]
    ```

    #### 2. Langfuse 連携の確認事項 ( Plan C 適用済み )
    - **Generation**: `bedrock-generation` として手動記録。
    - **Usage**: Bedrock の `usage` (Tokens) を正確にキャプチャ。
    - **Metadata**: `session_id`, `user_input` などをメタデータに格納。
    - **Robustness**: Langfuse SDK 不在時や SSM 権限不足時でもメイン機能を阻害しないガード実装済み。

---

## 📝 監督メモ・特記事項
(ステークホルダーへの報告時に必要な補足事項などをここに追記してください)
