# E2Eテストケース (機能単位)

## 1. 機能単位の特定

成果物（`src/app.py`, `template.yaml`）および復元された要件に基づき、テスト対象となる機能単位を以下に定義します。

| 機能ID | 機能名 | 概要 | E2Eフローの起点 | E2Eフローの終点 | 構築状況 |
|---|---|---|---|---|---|
| F-001 | AI対話機能 | ユーザーのメッセージに対し、Bedrock(Nova Micro)を用いて回答を生成する | API GatewayへのPOSTリクエスト | AI対話レスポンスの受信 | 実装済み |
| F-002 | セッション管理機能 | `session_id`を用いてDynamoDBに履歴を保持し、文脈を維持した対話を行う | API GatewayへのPOSTリクエスト | 過去の文脈を反映したレスポンス | 実装済み |
| F-003 | 入力制御機能 | 必須項目（message）の有無をチェックし、不正なリクエストを拒絶する | API GatewayへのPOSTリクエスト | ステータスコード400の返却 | 実装済み |
| F-004 | API認証機能 | API Keyの有無と正当性を検証し、未認可のリクエストを拒絶する | API GatewayへのPOSTリクエスト | ステータスコード403の返却 | 実装済み |

---

## 2. テストケース一覧表

| # | 機能ID | テストシナリオ名 | 種別 | 前提条件 | 操作手順（E2E） | 期待結果（確認ポイント） | 優先度 | 備考 |
|---|---|---|---|---|---|---|---|---|
| 1 | F-001 | 正常なメッセージを送信した場合、AIからの回答が返却されること | 正常系 | APIがデプロイ済みであり、正しいAPIキーを保持していること | `curl -X POST [ChatApiEndpoint] -H "x-api-key: [ValidApiKey]" -H "Content-Type: application/json" -d '{"message": "富士山の高さは？", "session_id": "e2e-test-001"}'` | 1. ステータスコード 200 が返ること<br>2. レスポンスの `response` フィールドに回答テキストが含まれること<br>3. `session_id` が "e2e-test-001" であること | High | |
| 2 | F-002 | 同一のsession_idで複数回対話した場合、過去の文脈が維持されること | 正常系 | 1回目の対話が完了していること | 1. `curl ... -d '{"message": "私の名前は太郎です", "session_id": "e2e-test-002"}'`<br>2. `curl ... -d '{"message": "私の名前は何ですか？", "session_id": "e2e-test-002"}'` | 1. 2回目のレスポンス内容に「太郎」という文言が含まれていること<br>2. いずれもステータスコード 200 であること | High | 履歴保存先：DynamoDB |
| 3 | F-003 | messageが欠落している場合、400エラーが返却されること | 異常系 | 有効なAPIキーを使用すること | `curl -X POST [ChatApiEndpoint] -H "x-api-key: [ValidApiKey]" -H "Content-Type: application/json" -d '{"session_id": "e2e-test-003"}'` | 1. ステータスコード 400 が返ること<br>2. レスポンスボディに `"error": "Message is required"` が含まれること | Medium | |
| 4 | F-004 | APIキーなしでリクエストした場合、403エラーが返却されること | 異常系 | なし | `curl -X POST [ChatApiEndpoint] -H "Content-Type: application/json" -d '{"message": "hello"}'` | 1. ステータスコード 403 が返ること<br>2. `Forbidden` メッセージが返ること | High | API Gateway標準の認証 |
| 5 | F-004 | 誤ったAPIキーでリクエストした場合、403エラーが返却されること | 異常系 | なし | `curl -X POST [ChatApiEndpoint] -H "x-api-key: INVALID_KEY" ...` | 1. ステータスコード 403 が返ること | High | |
| 6 | F-001 | 外部サービス（Bedrock）でエラーが発生した場合、システムとしてのエラーメッセージが返ること | 異常系 | （デバッグ用）Bedrockへの権限を一時的に剥奪するか、存在しないモデルIDを指定する | `curl -X POST [ChatApiEndpoint] ...` | 1. ステータスコード 200 が返ること（実装上、例外は捕捉され固定メッセージを返却するため）<br>2. レスポンスに 「エラーが発生しました。」 が含まれること | Medium | `app.py` のtry-except挙動を確認 |

---

## 3. 今後追加予定のテストケース（未実装機能）

| # | 機能ID | テストシナリオ名（予定） | 対応予定フェーズ | 備考 |
|---|---|---|---|---|
| 1 | F-EXT | Difyから外部ツールとして正常に呼び出せること | Phase 4-2 | Dify連携 |
| 2 | F-MON | 大量のリクエスト時にスロットリングが発生すること | Phase 5以降 | クォータ制限の検証 |
| 3 | F-OPS | CI/CDパイプラインにより自動的にテストが実行されること | Phase 5 | GitHub Actions連携 |

---

## 4. カバレッジ確認

| 機能ID | 機能名 | 正常系ケース数 | 異常系ケース数 | カバー状況 |
|---|---|---|---|---|
| F-001 | AI対話機能 | 1 | 1 | 十分 |
| F-002 | セッション管理機能 | 1 | 0 | 十分（文脈維持に特化） |
| F-003 | 入力制御機能 | 0 | 1 | 十分（バリデーション単一） |
| F-004 | API認証機能 | 0 | 2 | 十分（セキュリティ重視） |

**追加提案:**
- 現在の `F-002` は「維持」のみですが、履歴の「上限（トークン制限等）」に関する異常系を追加検討する余地があります。ただし、今回のNova Micro利用範囲では基本フローの検証を優先しました。

---

## 5. テスト実行環境・変数

テスト実行時は以下のプレースホルダを実際の値に置き換えてください。
- `[ChatApiEndpoint]`: `https://rxajg598kk.execute-api.ap-northeast-1.amazonaws.com/Prod/chat`
- `[ValidApiKey]`: AWSコンソールまたは `Progress_log.md` 記載の手順で取得したキー
- `[InvalidApiKey]`: 任意の異なる文字列
