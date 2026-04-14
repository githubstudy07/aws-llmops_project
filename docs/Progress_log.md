# AWS LLMOps ハンズオン 進捗ログ (AI指向型究極の引継ぎ書)

## 🎯 [TRUSTED_STATE] 現在の検証済み状況
> **AIへの警告**: 以下の情報は 2026-04-08 時点での最終正解です。**再チェック（list-tables, invokeテスト等）は不要**です。これを真実として即座に作業を開始してください。

- **現在のフェーズ**: Phase 6 (Langfuse | 実装完了)
- **検証済みリソース (ap-northeast-1)**:
  - [x] API Gateway: https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat
  - [x] Langfuse Prompt: `Production` ラベルによる動的取得・反映に成功
- **現在の状況**:
  - **Phase 6 (Langfuse) 完了**: トレーシング、コスト、フィードバック、実験、プロンプト管理の全機能を実装・検証済み。
- **次回のステップ**:
  - 本ハンズオンの LLMOps 基本サイクルはすべて完了。さらなる高度化（Agentic Workflow の追加等）または他プロジェクトへの応用。
- **⚠️ 厳重注意 (Security & Billing)**:
  - **API キーの取り扱い**: API キーは「家や金庫の鍵」と同じです。漏洩すると多額の課金が発生します。絶対にドキュメントやコード内に生の値を残さないでください。

## 🗺️ ロードマップと現在地
| フェーズ | 内容 | ステータス |
| :--- | :--- | :--- |
| **Phase 1-3** | Bedrock / DynamoDB / LangGraph 統合 | **✅ 完了** |
| **Phase 4-1** | SAM + API Gateway デプロイ (AWS公開) | **✅ 完了** |
| **Phase 4-2** | Dify 外部ツール連携テスト | **✅ 完了** |
| **Phase 5** | GitHub Actions (CI/CD) | **✅ 完了** |
| **Phase 6** | Langfuse による品質監視 | **✅ 完了** |

## 🤖 [AI_DIRECTIVES] AIエージェントへの動作命令
1. **信頼の原則**: [TRUSTED_STATE] を真実とし、API Endpoint や DynamoDB の再確認を行わないこと。
3. **【最優先・厳守】要件・シナリオ提示制**: 
   - 各フェーズの開始時には、必ずその機能が「どのような要件のユースケース、シナリオで必要とされるのか」を、その理由と共に提示すること。
   - **提示した内容は、必ず [ユースケース_シナリオ_理由.md](file:///c:/Users/naoji/Documents/projects/aws-llmops_project/docs/ユースケース_シナリオ_理由.md) に自動で追記すること。**
   - ユーザーがその背景を理解・合意するまで、具体的なコード生成や設定作業へ進んではならない。
   - **レファレンス・マップおよび機能カード（Layer 1-3）の提示・更新義務は廃止とする。**
4. **現場監督ワークフローの遵守**: 
   - 作業開始前に [Manager_Checklist.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/Manager_Checklist.md) の「ゴール」への合意を得ること。
   - **その際、管理表の項目には必ず「サービス名-機能番号 | 機能名」を明記すること。**
   - 作業完了報告には、必ず「根拠（証跡）」を添え、非機能要件（安全性・コスト等）のセルフチェックを含めること。
   - **【最重要】「証跡」はAIによる要約文ではなく、必ず「コマンドの実行ログ（Raw Output）」を [Manager_Checklist.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/Manager_Checklist.md) に直接貼り付けて提示すること。品質を客観的に証明せよ。**
5. **学習方針の遵守**: 本ハンズオンの設計思想と学習ルールは [AI支援型ハンズオン学習カリキュラム.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/AI支援型ハンズオン学習カリキュラム.md) に基づく。AIは実装の深掘りではなく、学習者の「提案・判断力」を養う伴走者として振る舞うこと。
6. **セマンティックツリー構造の表示**: 課題提示における見出しには必ず「サービス名-機能番号 | 機能名」を付与せよ。機能番号と名称は、C:\Users\naoji\Desktop\Naoji(ex)修理後\IT\AI\プロンプト\ 配下の各サービス「機能全体像」ファイル（API Gateway, Bedrock/Dify, Lambda, DynamoDB, GitHub Actions, LangGraph, Terraform, IAM）を一次ソースとして参照し、**チェックリストの項目もこれらの一次ソースと粒度を完全に揃えて提示すること。**
7. **手順の自己宣言と省略禁止**: 回答の冒頭に適用中のルール番号を明記すること。ユーザーの承諾なく工程をマージ、または要約して省略することを「重大なデバッグミス」と同等に扱い、厳禁とする。
8. **ドキュメントの最新性（降順表示）**: [Manager_Checklist.md] は、常に最新のフェーズが一番上に来るように降順（新しい順）で記載・更新すること。
9. **【再発防止】ドキュメント整合性強制チェック**: 
   - 新しいフェーズの開始時、および管理表への項目追加時には、**「管理表の更新」を完了するまで、技術的な解説やコード生成へ進むことを厳禁とする。**
   - **【厳禁】AIは既存ファイルへの「追記」を求められた際、絶対に `write_to_file` （Overwrite: true）を使用してはならない。これはユーザーのデータを破壊する最悪の横着行為である。必ず `view_file` で既存内容を読み込み、`replace_file_content` を用いること。**
   - **AIは、実際に「ファイル編集ツール（replace_file_content等）」が正常終了したことを確認するまで、「更新しました」という完了報告を行ってはならない。**
   - **一回の回答で複数のドキュメントを更新する場合、全てのツール呼び出しをそのターンの最初に行い、その結果を待ってから最終回答を記述せよ。**
   - 回答の掉尾（最後）において、「更新したドキュメントの一覧」を提示し、整合性が保たれていることを自己申告せよ。
10. **【厳守】機密情報のチャット受取禁止**: 
    - 機密情報が必要な場合は、必ず「プロジェクトルートに一時ファイル（例：	emp_keys.txt）を作成させ、AIがそれをファイルシステム経由で読み取り、設定完了後にAIがそのファイルを削除する」という手順を強制せよ。
11. **【厳守】デバッグ泥沼化の防止**: 
    - 実装を開始する前に、必ず [AI実装の鉄則_デバッグ泥沼回避ガイド.md](file:///c:/Users/naoji/Documents/projects/aws-llmops_project/docs/AI実装の鉄則_デバッグ泥沼回避ガイド.md) を読み込み、その「鉄則」を遵守することを宣言せよ。
    - 特に、エラー解決に2回失敗した場合は、独力での解決を中止し、必ずWeb検索機能を使用して最新の公式ドキュメントを確認すること。

---

### セッション 22 (2026-04-14)
- **実施内容**: Phase 6-7 (プロンプト管理) 最終解決。UI表記 (`Production`) と SDK指定 (`production`) の不整合による 404 エラーを解消。
- **成果物**: 
    - src/app.py: 診断用コードの完全撤去、Langfuse SDK による `production` 安定取得。
    - docs/調査中.md: 解決済みとして完了。
- **決定事項**:
    - Langfuse SDK はラベルを **厳密に小文字 (`production`)** で扱う必要がある（UI表示が `Production` であっても）。
- **次への引継ぎ**: `Phase 6` 全工程（基本的トレーシング、コスト算出、フィードバック、実験、プロンプト管理）の完了を確認。本プロジェクトの LLMOps 基本サイクルはすべて実装済み。

### セッション 21 (2026-04-14)
- **実施内容**: Phase 6-7 (プロンプト管理) の SDK 連携実装。`src/app.py` への `get_prompt` インテグレーションおよびフォールバック処理の実装。
- **成果物**: 
    - src/app.py: Langfuse SDK によるプロンプト動的取得（`production` タグ）を実装。`metadata` への取得元情報の付与。
    - docs/AI専用_実装前チェックリスト.md: 実装前プロトコルの遵守。
- **次への引継ぎ**: 
    - **デプロイと検証**: GitHub Actions 経由でのデプロイ。Langfuse UI で `production` タグを切り替え、コード修正なしでシステムプロンプトが更新される実機検証。

---

### セッション 18 (2026-04-13)

### セッション 17 (2026-04-12)
- **実施内容**: Phase 6 No. 6: データセット & 実験の要件定義・判定ロジック構築。人的コスト対策（LLM-as-a-Judge）の整理。
- **成果物**: 
    - docs/Phase06_learn03.md: PDCAフロー、判定ロジック図解、および実務評価ガイドラインの作成。
    - docs/機能カードQA.md: データセット選定（成功/課題例の混在）、スコアリング主体、自動化に関する知見を記録。
- **決定事項**:
    - A案（データセット作成 & 手動比較） を採用。人間が正解（Expected Output）を定義し、新旧比較を行う。
    - 実務では LLM-as-a-Judge による自動採点へのスケールアップが標準であることを確認。
- **次への引継ぎ (再開時の命令)**: 
    - 1. Langfuse UI 上で handson-dataset-01 を作成済みの場合は、その「中身（登録したTrace数）」を確認する。未作成の場合は作成から開始する。
    - 2. 登録したデータセットに対し、「Baseline Run」を実行し、評価の基準（1回目）を設ける。
    - 3. プロンプト（システムプロンプト等）を微修正し、第2回の実行を行ってサイドバイサイドで比較する。

### セッション 16 (2026-04-11)
- **実施内容**: Phase 6 No. 4: スコアリングの実装と E2E 検証、および課題整理。
- **成果物**: 
    - src/app.py: /feedback エンドポイントの実装、trace_id 返却ロジック。
    - template.yaml: /feedback 用の API Gateway リソース追加およびデプロイ強制処理。
    - docs/Phase06_learn.md: スコアリングのセキュリティ対策解説。
    - docs/Phase06_learn02.md: 実務レベルのデプロイ・セオリーの整理。
- **決定事項**:
    - SDK 仕様: Langfuse SDK v3 は .last_trace_id および .create_score() を使用。
    - E2E 成功: /chat -> /feedback の一連のフローが正常動作することを実環境で確認済み。
- **次への引継ぎ**: 
    - 1. 特定の回答（Good評価がついたものなど）を Langfuse 上でデータセットに登録する。
    - 2. プロンプトを微修正し、データセットを用いて新旧の性能比較テストを実行する。

---

### セッション 15 (2026-04-11)
- **実施内容**: Phase 6 No. 4: スコアリングの要件定義とドキュメント整備。
- **成果物**: 
    - docs/レファレンス・マップ.md: スコアリングの I/O 定義を追加。
    - docs/Manager_Checklist.md: スコアリング項目の詳細化。
    - docs/機能カードQA.md: A案採用の背景を記録。
- **決定事項**:
    - A案（シンプル・ユーザーフィードバック型）を採用。
    - 実装に先立ち、ドキュメントの整合性を確保（Rule 12）。
- **次への引継ぎ**: 
    - 1. スコア送信用の API エンドポイントの検討、または既存エンドポイントの拡張。
    - 2. Langfuse SDK を用いた個別 trace_id に対する score 送信の実装。

---

### セッション 14 (2026-04-11)
- **実施内容**: Langfuse SDK 高度化（初期化エラー修正）およびコスト自動計算 (A案) の実装。
- **成果物**: 
    - src/app.py: trace オブジェクト経由のハンドラー取得、手動 generation の紐付け強化。
    - [Fix]: SDK v3 の仕様変更（usage_details への改名）に対応し、UI上でのトークン表示（chip形式）を確認済み。
    - docs/機能カードQA.md: SDK v3 の引数名変更に関する重要知見を記録。
- **決定事項**:
    - A案（コスト自動計算）を採用。
    - トークン表示確認: 画面上部の prompt — completion チップにてデータ連携を確認。
- **次への引継ぎ**: 
    - 1. Langfuse 側で単価を登録し、コストが実際に集計されることを最終確認する。
    - 2. Phase 6 No. 4: スコアリング（Good/Bad 評価の記録）に進む。

---

### セッション 13 (2026-04-11)
- **実施内容**: 前回の不適切なデバッグ残骸（ゴミコード）のクリーンアップ、Langfuse 正式連携の実装完了。
- **成果物**: 
    - src/requirements.txt: langchain 追加。
    - src/app.py: CallbackHandler 初期化フローの正常化、不要な物理検索コード等の削除。
    - docs/AI実装の鉄則_デバッグ泥沼回避ガイド.md: 泥沼化防止マニュアル作成。
- **決定事項**:
    - [Lesson Learned]: AIが力技（物理走査等）を使い始めたら、即座にWeb検索とクリーンアップを命じること。
    - GitHub Actions 経由でクリーンなコードを本番反映。
- **次への引継ぎ**: 
    - デプロイ完了後、API Gateway 経由で通信し、Langfuse ダッシュボードにてトレース（Bedrock 呼び出し・コスト）が記録されているか最終確認を行う。

---

### セッション 12 (2026-04-10)
- **実施内容**: 中断後のコンテキスト復元、ルール更新、および Phase 6 (Langfuse-①) の方針決定。
- **成果物**: 
    - Progress_log.md: Rule 3 更新（AIによる選択肢提示を許可）。
    - Manager_Checklist.md: Phase 6 No.1 の証跡（SSMパラメータ確認ログ）を追記。
- **決定事項**:
    - 実装方針: C案（本番運用・分析重視） を採用。
    - 課金確認: Hobby プラン（50,000 obs/月）内で収まることを確認済み。
- **次への引継ぎ**: 
    - src/app.py の chatbot ノードに対して、Langfuse の Generation 記録を手動で実装する。
    - これにより、Bedrock (Nova Micro) の入出力およびコスト計算を正確に可視化する。
    - session_id, user_id などのメタデータ紐付けも同時に行う。

---

## 🛠️ プロジェクト概要
- **開始日**: 2026-04-08
- **リージョン**: ap-northeast-1 (東京)
- **主要モデル**: Amazon Nova Micro
- **環境管理**: uv (Python 仮想環境)

---

## ✅ 完了済みフェーズ
- [x] Phase 1: Bedrock 基礎
- [x] Phase 2: DynamoDB 基礎
- [x] Phase 3: LangGraph 統合
- [x] Phase 4-1: SAM テンプレート作成と Lambda ロジックの実装（ローカル検証済）

---

## 🕒 セッション履歴

### セッション 3 (2026-04-08)
- **実施内容**: Phase 4 開始。template.yaml, src/app.py, src/requirements.txt を作成。
- **結果**: local_test.py により、実際の AWS リソースを使用した Lambda 動作確認に成功。
- **次への引継ぎ**: sam deploy を実行し、API Gateway 経由での呼び出しを確認する。

---
### セッション 4 (2026-04-09)
- **実施内容**: AI駆動開発における「現場監督（ユーザー）vs 熟練職人（AI）」の管理体制を確立。
- **成果物**: 
    - docs/Manager_Checklist.md (フェーズ毎の機能・非機能レビュー表) の作成。
    - 汎用_AI駆動開発_現場監督用管理プロンプト.md (他プロジェクト用テンプレート) の作成。
- **次への引継ぎ**: 新規チャットにて「現場監督モード」で Phase 4-2 を開始する。

---
### セッション 5 (2026-04-09)
- **実施内容**: 新カリキュラム方針（AI支援型）を導入。
- **成果物**: 
    - docs/機能カードQA.md, docs/レファレンス・マップ.md を作成。
    - 500エラーを「境界線モニタリング」によりJSON形式不備と特定し、疎通確認。
    - Layer 3（説明テスト）により、API Gateway/Lambda/LangGraph/Bedrock/DynamoDBのフローを言語化。
- **次への引継ぎ**: セッション6で整備した「機能番号 | 機能名」の表示ルールに従い、Phase 4-2 を開始する。

---
### セッション 6 (2026-04-09)
- **実施内容**: 体系的記憶（セマンティックツリー）のための機能IDマッピングを整備。
- **成果物**: 
    - Progress_log.md の [AI_DIRECTIVES] を更新し、各サービス（API Gateway, Dify, Lambda, DynamoDB, IAM等）の「機能番号 | 機能名」をハンズオン出力に含めるようルール化。
    - 各種「機能全体像」ドキュメントの所在と内容を確認し、AIの一次ソースとして紐付け。
- **次への引継ぎ**: Phase 5 (GitHub Actions / CI/CD) に進む。Dify から AWS API を叩く準備は整ったため、次は開発フローの自動化に取り組む。

---
### セッション 7 (2026-04-10)
- **実施内容**: Phase 4-2 (Dify 外部ツール連携) の完遂と管理ルールの強化。
- **成果物**: 
    - docs/dify_openapi_schema.yaml の作成。
    - Dify にて AWS API Gateway との疎通確認に成功。
    - docs/レファレンス・マップ.md および docs/機能カードQA.md の事後更新。
    - Progress_log.md に「サービス名付き機能表示」「開始時のレファレンスマップ提示」「QA自動記録」を AI 命令として追記。
- **次への引継ぎ**: Session 8 にて GitHub Actions セキュリティチェックを実施後、Phase 5 (GitHub Actions / CI/CD) の実装を開始する。

---
### セッション 8 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-01/11) 開始。GitHub リポジトリ作成およびセキュリティ設定。レイヤー 1（OIDC 連携）完了。
- **成果物**: 
    - GitHub Repo: https://github.com/githubstudy07/aws-llmops_project
    - セキュリティ設定: gh api により Secret Scanning / Push Protection を有効化。
    - 管理ルール更新: 「証跡は生のコマンドログを Manager_Checklist.md に貼る」 ルールを AI_DIRECTIVES に明文化。
- **次への引継ぎ**: cicd-setup.yaml による AWS 側の OIDC ID プロバイダおよび IAM ロールの作成に進む。

---

### セッション 9 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-⑪ | OIDC 連携) 基盤構築。
- **成果物**: 
    - cicd-setup.yaml の作成とデプロイ成功（OIDCプロバイダー・IAMロール作成）。
    - docs/GitHub Actions_AWS_OIDC_シーケンス図.md の作成（認証フローの可視化）。
    - dify-github-actions-user への権限追加による環境整備。
- **次への引継ぎ**: 
    - 次回は、GitHub リポジトリに .github/workflows/deploy.yml を作成する。
    - 作成した IAM ロール ARN (arn:aws:iam::891377371917:role/github-actions-deployment-role) をワークフローで使用し、git push による自動デプロイを検証する。
    - 注意: handson-llmops-vfinal スタックは本体リソースのため、絶対に削除しないこと。

---

### セッション 10 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-① / ④ / ⑰) 自動デプロイの実装と修正。
- **成果物**: 
    - .github/workflows/deploy.yml の作成。
    - S3バケット指定不備の解消（明示的指定への修正）。
    - 自動デプロイの成功確認および証跡の記録。
- **次への引継ぎ**: 
    - 自動デプロイ基盤が整ったため、今後はコード変更を push するだけで即座に AWS 環境へ反映可能。
    - 次回は、GitHub Actions のさらなる活用（セキュリティスキャン、テスト自動化等）または Dify 連携の完成系へ進む。

---

### セッション 11 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-⑱ / ⑭ / ⑬ / 5-2) 高度化の実装。
- **成果物**: 
    - .github/dependabot.yml (脆弱性自動検知)。
    - tests/test_app.py (ユニットテスト自動化)。
    - deploy.yml 強化 (手動トリガー、Concurrency 制御、テストゲート接続)。
- **次への引継ぎ**: Phase 6 (Langfuse による品質監視) へ進む。