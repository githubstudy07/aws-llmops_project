# GitHub Actions & AWS OIDC 連携シーケンス

この図は、GitHub Actions が AWS アクセスキーを使用せずに、セキュアに AWS へのアクセス権限を取得するフローを示しています。

```mermaid
%%{init: { 'theme': 'base', 'themeVariables': { 'signalColor': '#FFFFFF', 'signalTextColor': '#FFFFFF', 'noteTextColor': '#333333', 'sequenceNumberColor': '#000000' } } }%%
sequenceDiagram
    autonumber
    participant GHA as GitHub Actions (Workflow)
    participant GIDP as GitHub OIDC Provider
    participant AWS as AWS (STS / IAM)
    participant RES as AWS リソース (Lambda / S3 / etc.)

    Note over GHA, RES: 【認証・認可フェーズ】

    GHA->>GIDP: 1. OIDCトークン(JWT)をリクエスト
    GIDP-->>GHA: 2. 署名済みトークンを発行 (リポジトリ情報などを内包)

    GHA->>AWS: 3. トークンを提示してRoleの引き受けを要求 (AssumeRoleWithWebIdentity)
    
    Note right of AWS: 4. トークンの署名を検証し、信頼ポリシー (リポジトリ名等) を確認

    AWS-->>GHA: 5. 一時的な認証情報を発行 (AccessKey, SecretKey, SessionToken)

    Note over GHA, RES: 【実行フェーズ】

    GHA->>RES: 6. 一時的な認証情報を使ってリソース操作 (SAM Deploy等)
    RES-->>GHA: 7. 実行結果の返却

    Note over GHA, RES: ※ 認証情報はワークフロー終了後に自動消滅し、GitHub側には残らない
```

## 各ステップの解説

1.  **JWTリクエスト**: ワークフロー内で `permissions: id-token: write` を設定することで、GitHub Actions がトークンを取得可能になります。
2.  **証明書発行**: このトークンには「どのリポジトリのどのブランチから実行されているか」という情報（Claims）が署名付きで含まれます。
3.  **信頼の検証**: AWS 側の IAM OIDC プロバイダーが GitHub の署名を検証します。さらに、IAM ロールの「信頼関係」設定により、特定のリポジトリからの要求のみを受理します。
4.  **一時的な鍵**: 発行されるのは数十分〜数時間だけ有効な「使い捨ての鍵」です。万が一漏洩しても、時間が経てば無効化されるため、固定のアクセスキーよりも格段に安全です。
