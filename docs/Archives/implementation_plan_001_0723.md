# インプリメンテーションプラン: スキルの整合性検証と問題修正

created: 2026-07-23 00:02 (JST)
author: AI Agent (Gemini 3.6 Flash)

## 1. 概要

リポジトリ `.agents/skills/` 内に存在するスキルの文法的・機能的整合性を点検した結果、`code-understanding-pyramid` スキルにおいて深刻な構文破壊（改行の喪失およびYAML frontmatterの破綻）が確認されました。また、`code-understanding-pro` についても仕様との完全な一致を確認・検証します。

本プランでは、発見された問題を解消し、すべてのスキルがAgentエコシステム規格に準拠して正常に動作する状態まで整備・修正します。

---

## 2. 現状の分析と問題点

### 2.1 `code-understanding-pyramid` の問題 (Critical)

1. **構文破壊 (Malformed Markdown & YAML Frontmatter)**:
   `SKILL.md` の改行が全て失われ1行化しており、フロントマター (`---name: code-understanding-pyramiddescription: ...`) がパース不能になっています。
2. **冗長ファイル・重複構造**:
   同フォルダ内に `code-understanding-pyramid` (拡張子なし) や `code-understanding-pyramid-ja.md` など、破損した類似ファイルが存在しています。

### 2.2 `code-understanding-pro` の状態 (Minor / Valid)

- `SKILL.md` の YAML Frontmatter、目次構造、参照リファレンス、`manifest.json` との整合性は取れており正常に機能しています。
- 各出力テンプレート (`assets/`)、リファレンス文書 (`references/`)、補助スクリプト (`scripts/collect_code_context.py`) の実在を確認済みです。

---

## 3. 修正計画方針

### タスク 1: `code-understanding-pyramid` の修正と標準化

- **`SKILL.md` の改修**:
  - 正しい YAML frontmatter (`name`, `description`, `version`) を設定。
  - 日本語版を標準（または英和併記の標準フォーマット）として改行と見出し構造をきれいに復元。
  - フロントマターの規約（`Use when ...` で始まる起動条件記述）に準拠。
- **無効ファイルの整理**:
  - 壊れている非標準ファイル (`code-understanding-pyramid`, `code-understanding-pyramid-ja.md`) を削除し、単一の明確な `SKILL.md` 構成に整理。

### タスク 2: `code-understanding-pro` の微調整と検証

- `SKILL.md` 内のリファレンスパス（`references/`, `assets/`）へのリンク切れがないか総合点検。
- `description` のトリガーキーワードの感度チェックと微修正。

### タスク 3: 最終動作・機能検証

- 修正後の全スキルの文法（YAML Frontmatter、Markdown構造）を検証。
- agentによるスキルの認識・ロードが正常に行えるか検証。

---

## 4. 変更対象ファイル一覧

- `file:///Users/myamaguchi/Programing/Productivity-Skill/.agents/skills/code-understanding-pyramid/SKILL.md` (修正)
- `file:///Users/myamaguchi/Programing/Productivity-Skill/.agents/skills/code-understanding-pyramid/code-understanding-pyramid` (削除)
- `file:///Users/myamaguchi/Programing/Productivity-Skill/.agents/skills/code-understanding-pyramid/code-understanding-pyramid-ja.md` (削除)
- `file:///Users/myamaguchi/Programing/Productivity-Skill/.agents/skills/code-understanding-pro/SKILL.md` (検証・必要に応じて微修正)

---

## 5. 段階的承認のお願い

上記のインプリメンテーションプランをご確認の上、問題がなければ**「承認 (Approval)」**の旨をご指示ください。承認をいただき次第、実際のファイル修正およびクリーンアップを実行いたします。
