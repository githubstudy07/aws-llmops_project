# テストケース実施結果 (改訂版)

## 1. 実施概要
- **実施日**: 2026-04-09
- **実施手法**: 静的解析および設定・コードの整合性シミュレーション
- **修正点**: #1の判定をFailに変更、#9の検証深化、500エラーの関連性分析を追加

---

## 2. フェーズ別詳細結果

### Phase 1: テスト実施可否の事前判定
全16件について、提供された成果物からの検証が可能と判定しました（#9, #12については環境・インフラ設定の不備がコード解析から特定されています）。

### Phase 2: 全16件の検証トレースと結果判定

| # | テスト名 | 結果 | 検証トレース |
|---|---|---|---|
| 1 | AI対話機能 | **Fail** | `app.py` L.70は `message` を期待するが、`remote_test.py` L.25は `input` を送信。400エラーとなるため。 |
| 2 | セッション維持 | **Pass** | `app.py` L.80で `thread_id` を正しく生成し `app.invoke` に渡している。 |
| 3 | メッセージ欠落 | **Pass** | `app.py` L.73-77 に欠落時の 400 エラー返却ロジックが実装済み。 |
| 4 | 不当なJSON形 | **Pass** | `app.py` L.69 の `json.loads` 例外を L.100 で安全に捕捉している。 |
| 5 | 長文入力 | **Pass** | 明示的な制限コードなし。Lambdaタイムアウト(60s)およびメモリ(512MB)の範囲内で処理。 |
| 6 | API Key認証 | **Pass** | `template.yaml` L.63 および L.87-108 にてUsagePlan含め完全定義。 |
| 7 | API Key未提示 | **Pass** | API Gatewayの `ApiKeyRequired: true` 設定によりLambda起動前に403を返却。 |
| 8 | 無効なAPI Key | **Pass** | 上記同様。無効なキーによるアクセスはインフラ層で遮断。 |
| 9 | DynamoDB保存 | **Blocked**| **深掘り検証**: IAM権限(L.41)はCRUDを網羅。しかし**不整合**あり：①期待値 `handson-` プレフィックスの有無、②現存テーブル `PK/SK` と `DynamoDBSaver` 期待属性(`thread_id`)の乖離。 |
| 10| Bedrockエラー | **Pass** | `app.py` L.34-45 にて外部API例外を捕捉し、ユーザーへ通知する実装あり。 |
| 11| HTTPS強制 | **Pass** | API Gateway REST API エンドポイントによる標準仕様。 |
| 12| CORS対応 | **Fail** | `app.py` にヘッダーはあるが、`template.yaml` にプリフライト用の `OPTIONS` メソッドが皆無。 |
| 13| 最小権限(IAM) | **Pass** | `template.yaml` L.35-44 で特定サービス・特定リソースに絞り込み済み。 |
| 14| タイムアウト | **Pass** | `template.yaml` L.17 で Lambda の 60秒 タイムアウトを明示。 |
| 15| リトライ挙動 | **Pass** | `src/app.py` L.17 で Bedrock クライアントに `max_attempts: 3` を設定。 |
| 16| 構造化ログ | **Pass** | `template.yaml` L.21 の `LogFormat: JSON` 指定により設定済み。 |

---

## 3. 結果サマリ

### 3.1 全体統計
| 指標 | 件数 | 備考 |
|---|---|---|
| テストケース総数 | 16 | |
| **Pass** | 13 | |
| **Fail** | 2 | #1(キー不一致), #12(OPTIONS不足) |
| **Blocked / Fail**| 1 | #9(DBスキーマ/名称不一致) |
| **合格率** | 81.25 ％ | |

### 3.2 BUG-001 と 500 エラーの関連性分析
- **BUG-001 (Request Key Mismatch)**:
  - `remote_test.py` でリクエストを投げると、Lambdaは 400 エラーを返します。
- **500 エラーの真因**:
  - ユーザーが `message` キーを使用しても 500 が出る場合、原因は **#9 (DynamoDB)** にあります。
  - `app.py` が `handson-langgraph-checkpoints` を探しているのに対し、実際のテーブル名やキー属性（PK/SK）が一致せず、`app.invoke` 内で例外が発生、それが 500 エラーとして露出しています。

---

## 4. 推奨アクション

1.  **プロトコル統一**: `app.py` または `remote_test.py` のどちらかを修正（`message` か `input` に統一）。
2.  **DynamoDB設定修正**: `template.yaml` のテーブル名修正、および `DynamoDBSaver` の初期化時に `partition_key="PK", sort_key="SK"` を指定する（またはテーブルを作り直す）。
3.  **CORS追加**: `template.yaml` に `OPTIONS` メソッドと Mock 統合を追加。

---
**判定者**: Antigravity (AI)
