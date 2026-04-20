# AWS LLMOps Project - File Aliases

このファイルは、本プロジェクトで頻繁に編集するファイルへのショートカットを定義します。
AI に編集を依頼する際に、以下のエイリアス名を使用すれば、フルパスの代わりになります。

---

## 📋 ドキュメント管理ファイル

| エイリアス | 正式パス | 用途 |
|---|---|---|
| `progress_log` | `docs/Progress_log.md` | セッション進捗・引継ぎ記録 |
| `manager_checklist` | `docs/Manager_Checklist.md` | フェーズ・機能の完了チェック |
| `ai_checklist` | `docs/AI専用_実装前チェックリスト.md` | 実装前の確認リスト |
| `usecase` / `ユースケース` | `docs/ユースケース_シナリオ_理由.md` | 機能の背景・要件定義 |
| `debug_analysis` | `docs/デバック/02_Output_構造化分析.md` | 最新デバッグ分析 |

---

## 🔧 ソースコード（メイン）

| エイリアス | 正式パス | 用途 |
|---|---|---|
| `src_main` | `src/main.py` | Lambda ハンドラー（本体） |
| `src_app` | `src/app.py` | アプリケーションロジック |
| `src_requirements` | `src/requirements.txt` | Lambda 依存パッケージ |

---

## 🧪 テストスクリプト

| エイリアス | 正式パス | 用途 |
|---|---|---|
| `langgraph_persistence` | `langgraph_persistence.py` | LangGraph チェックポイント検証用スクリプト |
| `local_test` | `local_test.py` | ローカル動作検証スクリプト |

---

## 🚀 インフラストラクチャ

| エイリアス | 正式パス | 用途 |
|---|---|---|
| `template_yaml` | `template.yaml` | SAM CloudFormation テンプレート |
| `samconfig_toml` | `samconfig.toml` | SAM 設定ファイル |

---

## 🚀 バッチ操作（複数ファイル同時編集）

一度に複数ファイルを更新する場合のメタエイリアス：

| メタエイリアス | 対象ファイル | 用途 |
|---|---|---|
| `update_progress` / `進捗を関連ファイルに記載` | 1. `docs/Progress_log.md`<br>2. `docs/Manager_Checklist.md`<br>3. `docs/ユースケース_シナリオ_理由.md` | セッション完了時に進捗ログ・チェックリスト・ユースケースを一括更新 |

---

## 🔍 ファイル読み込み指示（自動実行エイリアス）

AI が自動的にファイルを Read し、その内容に従うメタエイリアス：

| メタエイリアス | 対象ファイル | 動作 |
|---|---|---|
| `実装前チェックリストを読み込んで実装` / `pre_impl_checklist` | `docs/AI専用_実装前チェックリスト.md` | AI が自動的にこのファイルを Read し、STEP 1-5 に従って実装を進める |

---

## 📌 使用方法

**例1：単純な複数ファイル編集**

```
AI へ指示:
「progress_log と manager_checklist を編集して、セッション 60 の結果を追記してください」

AI が自動的に以下に変換:
progress_log → docs/Progress_log.md
manager_checklist → docs/Manager_Checklist.md
```

**例2：メタエイリアス（バッチ操作）**

```
AI へ指示:
「進捗を関連ファイルに記載」
または
「update_progress」

AI が自動的に以下の3ファイルを同時更新:
1. progress_log (セッション記録)
2. manager_checklist (フェーズ完了チェック)
3. usecase (機能背景・要件)
```

---

**作成日**: 2026-04-20 (Session 60)
**管理者**: User (naoji)
**最終更新**: 2026-04-20 (バッチ操作追加)
