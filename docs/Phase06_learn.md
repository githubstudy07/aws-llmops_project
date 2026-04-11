# Langfuse `trace_id` 外部公開時のセキュリティ懸念と対策

本ドキュメントは、LLMアプリケーション（Langfuse等）において、特定の実行トレースID（`trace_id`）をクライアント（フロントエンドやDify等）に返却し、評価（スコアリング）を受け付ける際のアーキテクチャ上の懸念と、その対策パターンをまとめたものです。

---

## 1. セキュリティ上の懸念

本プロジェクトのような「API Key による認証」が適用されている環境では攻撃対象が限定されますが、一般的なパブリックAPIとして設計する場合は以下のリスクが存在します。

1. **トレースデータの不正閲覧リスク（認可不備）**
   *   推測可能、あるいは漏洩した `trace_id` を使い、そのトレースに含まれるプロンプトや回答全文（他ユーザーの機密情報）を読み取るAPIエンドポイントが存在する場合の情報漏洩リスク。
2. **評価の改ざん・スパム攻撃（不正書き込み）**
   *   有効な `trace_id` を知る第三者が、大量の不正なスコア（例：意図的な「Bad」評価）を送信し、分析データを汚染するリスク。
3. **PII（個人情報）との紐付けリスク**
   *   `trace_id` 自体はUUID等の無意味な文字列でも、ユーザーIDなどと結びつくことで、個別の利用状況をトラッキングされるリスク。

---

## 2. 対策アーキテクチャ関係図

これらのリスクを軽減するために取られる主要な対策アプローチ（案1〜案3）の全体像です。

```mermaid
graph TD
    Client["クライアント (Dify 等)"]
    Gateway["API Gateway<br>(API Key 認証)"]
    Lambda["Lambda バックエンド"]
    Langfuse["Langfuse Cloud"]
    DB[("DynamoDB<br>(セッション/ID管理)")]

    Client -->|"チャットリクエスト / 評価送信"| Gateway
    Gateway -->|"認証済みリクエスト"| Lambda
    
    %% 通常のフロー
    Lambda -->|"トレース記録 / スコア送信"| Langfuse
    
    %% 対策の選択肢
    Lambda -. "【現状案】生 trace_id 返却" .-> Client
    Lambda -. "【案1】Proxy ID 生成・変換" .-> DB
    Lambda -. "【案2】署名付トークン(JWT) 発行・検証" .-> Client
    Lambda -. "【案3】trace_id の持ち主検証" .-> DB

    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:white;
    classDef client fill:#4285F4,stroke:#000,stroke-width:2px,color:white;
    classDef saas fill:#00C7B7,stroke:#000,stroke-width:2px,color:white;
    classDef db fill:#3B48CC,stroke:#000,stroke-width:2px,color:white;
    
    class Gateway,Lambda aws;
    class Client client;
    class Langfuse saas;
    class DB db;
```

---

## 3. 対策パターンのシーケンス図

各対策方式がどのようにしてクライアントとやり取りするかを示します。

### 【案1】プロキシ ID（Short ID）方式
実際の `trace_id` を外部に出さず、一時的な別名IDのみを返却する方式です。

```mermaid
sequenceDiagram
    participant Client as クライアント
    participant Lambda as バックエンド
    participant DB as DynamoDB
    participant Langfuse

    Note over Client,Langfuse: チャット応答フェーズ
    Client->>Lambda: 1. チャットリクエスト
    Lambda->>Langfuse: 2. トレース開始 (trace_id 発行)
    Lambda->>Lambda: 3. ランダムな Proxy ID 生成
    Lambda->>DB: 4. {Proxy ID: trace_id} を対応表に保存
    Lambda-->>Client: 5. 回答 + Proxy ID を返却

    Note over Client,Langfuse: スコアリングフェーズ
    Client->>Lambda: 6. 評価送信 (Proxy ID, スコア 1/0)
    Lambda->>DB: 7. Proxy ID から実 trace_id を検索
    Lambda->>Langfuse: 8. 実 trace_id にスコアを紐付け
    Lambda-->>Client: 9. 評価完了
```

### 【案2】署名付きトークン（JWT）方式
DB等で状態を持たず、改ざん防止の署名を施したトークンにIDを包んで渡す方式です。スパム対策に有効です。

```mermaid
sequenceDiagram
    participant Client as クライアント
    participant Lambda as バックエンド
    participant Langfuse

    Note over Client,Langfuse: チャット応答フェーズ
    Client->>Lambda: 1. チャットリクエスト
    Lambda->>Langfuse: 2. トレース開始 (trace_id 発行)
    Lambda->>Lambda: 3. trace_id + 有効期限 で署名付トークン生成
    Lambda-->>Client: 4. 回答 + トークン を返却

    Note over Client,Langfuse: スコアリングフェーズ
    Client->>Lambda: 5. 評価送信 (トークン, スコア 1/0)
    Lambda->>Lambda: 6. 署名の妥当性と有効期限を検証
    Lambda->>Langfuse: 7. トークン内の trace_id にスコア紐付け
    Lambda-->>Client: 8. 評価完了
```

### 【案3】セッション紐付け検証（所有権確認）方式
ID自体は生で返すものの、評価時に「このリクエストを送ってきたユーザーは、本当にこの trace_id を発生させたユーザーか？」を検証します。

```mermaid
sequenceDiagram
    participant Client as クライアント
    participant Lambda as バックエンド
    participant DB as DynamoDB
    participant Langfuse

    Note over Client,Langfuse: チャット応答フェーズ
    Client->>Lambda: 1. チャットリクエスト (session_id)
    Lambda->>Langfuse: 2. トレース開始 (trace_id 発行)
    Lambda->>DB: 3. {trace_id, session_id} の所有権ログを保存
    Lambda-->>Client: 4. 回答 + 生 trace_id を返却

    Note over Client,Langfuse: スコアリングフェーズ
    Client->>Lambda: 5. 評価送信 (trace_id, session_id, スコア)
    Lambda->>DB: 6. trace_id の所有者が session_id か検証
    alt 検証成功
        Lambda->>Langfuse: 7. trace_id にスコア紐付け
        Lambda-->>Client: 8. 評価完了
    else 検証失敗
        Lambda-->>Client: 403 Forbidden (不正アクセス)
    end
```

---

## 4. 本プロジェクト (Phase 6) での採用方針について
現在のハンズオン構成では、全体が **API Gateway の API Key によって保護されている閉鎖環境** であり、かつデータの「読み取り API」は外部公開していません。

そのため、過剰な複雑化（状態管理や署名検証の追加）を避ける学習的観点から、「現状案（生の `trace_id` を返却する方式）」で進めることも有効な選択肢となります。実運用を見据えたより堅牢な設計を学ぶ場合は、上記の中から用途に応じた対策を選択します。
