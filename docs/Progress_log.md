# AWS LLMOps ハンズオン 進捗ログ (AI指向型究極の引継ぎ書)

## 🎯 [TRUSTED_STATE] 現在の検証済み状況
> **AIへの警告**: 以下の情報は 2026-04-08 時点での最終正解です。**再チェック（list-tables, invokeテスト等）は不要**です。これを真実として即座に作業を開始してください。

- **現在のフェーズ**: Phase 6 (Langfuse-① | トレーシング追加)
- **検証済みリソース (ap-northeast-1)**:
  - [x] API Gateway: `https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat`
  - [x] Langfuse API Keys: SSM パラメータストア経由で安全に連携済み
- **現在の状況**:
  - **Phase 5 (GitHub Actions) 完了**: 自動デプロイ、テスト自動化、脆弱性検知を実装。
  - **Phase 6 (Langfuse) 開始**: セットアップ完了。トレーシングの詳細実装フェーズ。
- **次回のステップ (最優先)**:
  - 1. **トレーシング詳細化**: Bedrock (Nova Micro) の呼び出し（入力・出力・コスト）を正確に Langfuse に記録する。
- **⚠️ 厳重注意 (Security & Billing)**:
  - **API キーの取り扱い**: API キーは「家や金庫の鍵」と同じです。漏洩すると多額の課金が発生します。絶対にドキュメントやコード内に生の値を残さないでください。

## 🗺️ ロードマップと現在地
| フェーズ | 内容 | ステータス |
| :--- | :--- | :--- |
| **Phase 1-3** | Bedrock / DynamoDB / LangGraph 統合 | **✅ 完了** |
| **Phase 4-1** | SAM + API Gateway デプロイ (AWS公開) | **✅ 完了** |
| **Phase 4-2** | Dify 外部ツール連携テスト | **✅ 完了** |
| **Phase 5** | GitHub Actions (CI/CD) | **✅ 完了** |
| **Phase 6** | Langfuse による品質監視 | ── 進行中 |

## 🤖 [AI_DIRECTIVES] AIエージェントへの動作命令
1. **信頼の原則**: `[TRUSTED_STATE]` を真実とし、API Endpoint や DynamoDB の再確認を行わないこと。
3. **【最優先・厳守】レイヤー・ゲート制**: 
   - 新しいフェーズの開始時には、必ず「空の機能カード（Layer 1）テンプレート」**のみ**を提示すること。
   - **その際、サービス名・機能番号・機能名はAIがあらかじめ記入して提示し、ユーザーを「内容の言語化」に集中させること。ただし、回答のヒントになるような「例（（例：...））」は、ユーザーの思考を奪うため絶対に記載してはならない。**
   - **ユーザーがその内容を送信してくるまで、技術的な解説、構成の提案、コードの生成を一切行ってはならない。** 
   - AIが勝手に内容を埋めることは「学習の機会を奪う致命的なエラー」として厳禁し、ユーザーの「思考の言語化」を待つこと。
   - **ただし、ユーザーの要望により、言語化のプロセスにおいてはAIが複数の選択肢（A案、B案など）を提示し、ユーザーがその中から選択、あるいは調整する形式を許容する。**
4. **現場監督ワークフローの遵守**: 
   - 作業開始前に [Manager_Checklist.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/Manager_Checklist.md) の「ゴール」への合意を得ること。
   - **その際、管理表の項目には必ず「サービス名-機能番号 | 機能名」を明記すること。**
   - 作業完了報告には、必ず「根拠（証跡）」を添え、非機能要件（安全性・コスト等）のセルフチェックを含めること。
   - **【最重要】「証跡」はAIによる要約文ではなく、必ず「コマンドの実行ログ（Raw Output）」を [Manager_Checklist.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/Manager_Checklist.md) に直接貼り付けて提示すること。品質を客観的に証明せよ。**
5. **レファレンス参照**: 各フェーズの入出力や依存関係は [レファレンス・マップ.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/レファレンス_マップ.md) を参照せよ。
6. **学習方針の遵守**: 本ハンズオンの設計思想と学習ルールは [AI支援型ハンズオン学習カリキュラム.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/AI支援型ハンズオン学習カリキュラム.md) に基づく。AIは実装の深掘りではなく、学習者の「提案・判断力」を養う伴走者として振る舞うこと。
7. **セマンティックツリー構造の表示**: 各フェーズの課題提示（3層アンカー：Layer 1 機能カード, Layer 2 出力判定, Layer 3 説明テスト）において、Layer 1 / Layer 3 等の見出しには必ず「サービス名-機能番号 | 機能名」を付与せよ。機能番号と名称は、`C:\Users\naoji\Desktop\Naoji(ex)修理後\IT\AI\プロンプト\` 配下の各サービス「機能全体像」ファイル（API Gateway, Bedrock/Dify, Lambda, DynamoDB, GitHub Actions, LangGraph, Terraform, IAM）を一次ソースとして参照し、**チェックリストの項目もこれらの一次ソースと粒度を完全に揃えて提示すること。**
8. **レファレンス・マップの自動提示**: 各フェーズの開始時には、必ず最新の [レファレンス・マップ.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/レファレンス_マップ.md) の内容をヒントとしてユーザーに提示すること。
9. **QA履歴の永続化**: 各フェーズの Layer 1 での Q&A およびフィードバックは、必ず [機能カードQA.md](file:///C:/Users/naoji/Documents/projects/aws-llmops_project/docs/機能カードQA.md) に追記して記録すること。
10. **手順の自己宣言と省略禁止**: 回答の冒頭に適用中のルール番号（例：[Rule 8: レファレンス提示]）を明記すること。ユーザーの承諾なく工程をマージ、または要約して省略することを「重大なデバッグミス」と同等に扱い、厳禁とする。
11. **ドキュメントの最新性（降順表示）**: [レファレンス・マップ.md] および [Manager_Checklist.md] は、常に最新のフェーズが一番上に来るように降順（新しい順）で記載・更新すること。
12. **【再発防止】ドキュメント整合性強制チェック**: 
    - 新しいフェーズの開始時、および管理表への項目追加時には、**「レファレンス・マップの更新」「管理表の更新」「QA履歴の記録」の3点を完了するまで、技術的な解説やコード生成へ進むことを厳禁とする。**
    - 回答の掉尾（最後）において、「更新したドキュメントの一覧」を提示し、整合性が保たれていることを自己申告せよ。
13. **【厳守】機密情報のチャット受取禁止**: 
    - 機密情報が必要な場合は、必ず「プロジェクトルートに一時ファイル（例：`temp_keys.txt`）を作成させ、AIがそれをファイルシステム経由で読み取り、設定完了後にAIがそのファイルを削除する」という手順を強制せよ。
14. **【厳守】デバッグ泥沼化の防止**: 
    - 実装を開始する前に、必ず [AI実装の鉄則_デバッグ泥沼回避ガイド.md](file:///c:/Users/naoji/Documents/projects/aws-llmops_project/docs/AI実装の鉄則_デバッグ泥沼回避ガイド.md) を読み込み、その「鉄則」を遵守することを宣言せよ。
    - 特に、エラー解決に2回失敗した場合は、独力での解決を中止し、必ずWeb検索機能を使用して最新の公式ドキュメントを確認すること。

---

### セッション 14 (2026-04-11)
- **実施内容**: Langfuse SDK 高度化（初期化エラー修正）およびコスト自動計算 (A案) の実装。
- **成果物**: 
    - `src/app.py`: `trace` オブジェクト経由のハンドラー取得、手動 `generation` の紐付け強化。
    - `docs/機能カードQA.md`: SDK 仕様変更に関する知見を追加。
- **決定事項**:
    - **A案（コスト自動計算）** を採用。
    - **役割分担**: 職人（AI）がテストを実行し、監督（ユーザー）が品質を判定する運用フローを再確認。
- **次への引継ぎ**: 
    - デプロイ成果を確認し、Langfuse ダッシュボードにて Bedrock Nova Micro のコスト計算が反映されているか、監督による最終レビューを受ける。

---

### セッション 13 (2026-04-11)
- **実施内容**: 前回の不適切なデバッグ残骸（ゴミコード）のクリーンアップ、Langfuse 正式連携の実装完了。
- **成果物**: 
    - `src/requirements.txt`: `langchain` 追加。
    - `src/app.py`: `CallbackHandler` 初期化フローの正常化、不要な物理検索コード等の削除。
    - `docs/AI実装の鉄則_デバッグ泥沼回避ガイド.md`: 泥沼化防止マニュアル作成。
- **決定事項**:
    - **[Lesson Learned]**: AIが力技（物理走査等）を使い始めたら、即座にWeb検索とクリーンアップを命じること。
    - GitHub Actions 経由でクリーンなコードを本番反映。
- **次への引継ぎ**: 
    - デプロイ完了後、API Gateway 経由で通信し、Langfuse ダッシュボードにてトレース（Bedrock 呼び出し・コスト）が記録されているか最終確認を行う。

---

### セッション 12 (2026-04-10)
- **実施内容**: 中断後のコンテキスト復元、ルール更新、および Phase 6 (Langfuse-①) の方針決定。
- **成果物**: 
    - `Progress_log.md`: **Rule 3 更新**（AIによる選択肢提示を許可）。
    - `Manager_Checklist.md`: Phase 6 No.1 の**証跡（SSMパラメータ確認ログ）**を追記。
- **決定事項**:
    - **実装方針**: **C案（本番運用・分析重視）** を採用。
    - **課金確認**: Hobby プラン（50,000 obs/月）内で収まることを確認済み。
- **次への引継ぎ**: 
    - `src/app.py` の `chatbot` ノードに対して、Langfuse の **`Generation` 記録**を手動で実装する。
    - これにより、Bedrock (Nova Micro) の入出力およびコスト計算を正確に可視化する。
    - `session_id`, `user_id` などのメタデータ紐付けも同時に行う。


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
- **実施内容**: Phase 4 開始。`template.yaml`, `src/app.py`, `src/requirements.txt` を作成。
- **結果**: `local_test.py` により、実際の AWS リソースを使用した Lambda 動作確認に成功。
- **次への引継ぎ**: `sam deploy` を実行し、API Gateway 経由での呼び出しを確認する。

---
### セッション 4 (2026-04-09)
- **実施内容**: AI駆動開発における「現場監督（ユーザー）vs 熟練職人（AI）」の管理体制を確立。
- **成果物**: 
    - `docs/Manager_Checklist.md` (フェーズ毎の機能・非機能レビュー表) の作成。
    - `汎用_AI駆動開発_現場監督用管理プロンプト.md` (他プロジェクト用テンプレート) の作成。
- **次への引継ぎ**: 新規チャットにて「現場監督モード」で Phase 4-2 を開始する。

---
### セッション 5 (2026-04-09)
- **実施内容**: 新カリキュラム方針（AI支援型）を導入。
- **成果物**: 
    - `docs/機能カードQA.md`, `docs/レファレンス・マップ.md` を作成。
    - 500エラーを「境界線モニタリング」によりJSON形式不備と特定し、疎通確認。
    - Layer 3（説明テスト）により、API Gateway/Lambda/LangGraph/Bedrock/DynamoDBのフローを言語化。
- **次への引継ぎ**: セッション6で整備した「機能番号 | 機能名」の表示ルールに従い、Phase 4-2 を開始する。

---
### セッション 6 (2026-04-09)
- **実施内容**: 体系的記憶（セマンティックツリー）のための機能IDマッピングを整備。
- **成果物**: 
    - `Progress_log.md` の `[AI_DIRECTIVES]` を更新し、各サービス（API Gateway, Dify, Lambda, DynamoDB, IAM等）の「機能番号 | 機能名」をハンズオン出力に含めるようルール化。
    - 各種「機能全体像」ドキュメントの所在と内容を確認し、AIの一次ソースとして紐付け。
- **次への引継ぎ**: **Phase 5 (GitHub Actions / CI/CD)** に進む。Dify から AWS API を叩く準備は整ったため、次は開発フローの自動化に取り組む。

---
### セッション 7 (2026-04-10)
- **実施内容**: Phase 4-2 (Dify 外部ツール連携) の完遂と管理ルールの強化。
- **成果物**: 
    - `docs/dify_openapi_schema.yaml` の作成。
    - Dify にて AWS API Gateway との疎通確認に成功。
    - `docs/レファレンス・マップ.md` および `docs/機能カードQA.md` の事後更新。
    - `Progress_log.md` に「サービス名付き機能表示」「開始時のレファレンスマップ提示」「QA自動記録」を AI 命令として追記。
- **次への引継ぎ**: Session 8 にて GitHub Actions セキュリティチェックを実施後、Phase 5 (GitHub Actions / CI/CD) の実装を開始する。

---
### セッション 8 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-01/11) 開始。GitHub リポジトリ作成およびセキュリティ設定。レイヤー 1（OIDC 連携）完了。
- **成果物**: 
    - GitHub Repo: `https://github.com/githubstudy07/aws-llmops_project`
    - セキュリティ設定: `gh api` により Secret Scanning / Push Protection を有効化。
    - 管理ルール更新: **「証跡は生のコマンドログを Manager_Checklist.md に貼る」** ルールを AI_DIRECTIVES に明文化。
- **次への引継ぎ**: `cicd-setup.yaml` による AWS 側の OIDC ID プロバイダおよび IAM ロールの作成に進む。

---

### セッション 9 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-⑪ | OIDC 連携) 基盤構築。
- **成果物**: 
    - `cicd-setup.yaml` の作成とデプロイ成功（OIDCプロバイダー・IAMロール作成）。
    - `docs/GitHub Actions_AWS_OIDC_シーケンス図.md` の作成（認証フローの可視化）。
    - `dify-github-actions-user` への権限追加による環境整備。
- **次への引継ぎ**: 
    - 次回は、GitHub リポジトリに `.github/workflows/deploy.yml` を作成する。
    - 作成した IAM ロール ARN (`arn:aws:iam::891377371917:role/github-actions-deployment-role`) をワークフローで使用し、`git push` による自動デプロイを検証する。
    - **注意**: `handson-llmops-vfinal` スタックは本体リソースのため、絶対に削除しないこと。

---

### セッション 10 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-① / ④ / ⑰) 自動デプロイの実装と修正。
- **成果物**: 
    - `.github/workflows/deploy.yml` の作成。
    - S3バケット指定不備の解消（明示的指定への修正）。
    - 自動デプロイの成功確認および証跡の記録。
- **次への引継ぎ**: 
    - 自動デプロイ基盤が整ったため、今後はコード変更を push するだけで即座に AWS 環境へ反映可能。
    - 次回は、GitHub Actions のさらなる活用（セキュリティスキャン、テスト自動化等）または Dify 連携の完成系へ進む。

---

### セッション 11 (2026-04-10)
- **実施内容**: Phase 5 (GitHub Actions-⑱ / ⑭ / ⑬ / 5-2) 高度化の実装。
- **成果物**: 
    - `.github/dependabot.yml` (脆弱性自動検知)。
    - `tests/test_app.py` (ユニットテスト自動化)。
    - `deploy.yml` 強化 (手動トリガー、Concurrency 制御、テストゲート接続)。
- **次への引継ぎ**: Phase 6 (Langfuse による品質監視) へ進む。
