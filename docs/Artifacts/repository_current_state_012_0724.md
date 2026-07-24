# リポジトリ・Skill正本の現行整理

created: 2026-07-24 21:29 (JST)
author: AI Agent (GPT-5)

## 目的

過去の計画・検証・完了報告を、現在のリポジトリ構成とSkillの実体に合わせて整理する。本書を現行状態の参照先とし、過去の作業経緯や一時的な判断は`docs/Archives/`に保管する。

## 現在の責任分担

| リポジトリ | 正本・責任 | 現在の確認状態 |
|---|---|---|
| `Productivity-Skill` | 一般コード理解、SQL・統計コード理解、設計・学習・Skill開発支援 | 整理開始時点で`master` / `origin/master` が`f9da43f`で一致 |
| `rwd-mysql-skill-toolkit` | DB固有Skill、RWDデータワークフローの実行・統合 | `main` / `origin/main` が`51c6628`で一致 |
| `agentic-evidence-analysis` | VCD、カテゴリカル分析、Bayes Factor、Evidence Score、統計的エビデンス解釈 | ローカルcheckoutなし。公開`main`は`dc87797` |

正本は責任領域で分離する。`Productivity-Skill`と`rwd-mysql-skill-toolkit`で汎用Skillを二重管理せず、DB/RWD固有の実行資産はtoolkit、統計的エビデンス分析の専門資産は`agentic-evidence-analysis`で管理する。

## `Productivity-Skill` の現行Skill

### コード・SQL・統計の理解

| Skill | 用途 |
|---|---|
| `code-understanding-pro` | 日本語による既存コードの理解、レビュー、ドキュメント化、安全なリファクタリング支援 |
| `code-understanding-pyramid` | `code-understanding-pro`が利用する5段階の理解フレームワーク |
| `stats-sql-comprehension` | 複雑なSQL、dbt、BigQuery、R/Python統計コードの解読・評価 |

### 思考整理・用語管理

| Skill | 用途 |
|---|---|
| `grilling` | 計画・設計・意思決定を1問1答で壁打ちし、前提・制約・分岐を明確化 |
| `domain-modeling` | 必要な場合だけ、用語集やドメイン上の判断を整理・記録 |

### 学習・Skill開発

| Skill | 用途 |
|---|---|
| `teach` | 継続的な対話形式の学習支援 |
| `writing-great-skills` | Agent Skillの作成・レビュー・改善 |

## 整理済みの不要Skill

次のSkillは、重複または現在の運用に不要なため削除済みである。

- `grill-me`
- `grill-with-docs`
- `improve-codebase-architecture`
- `to-spec`
- `to-tickets`
- `diagnosing-bugs`

削除後、`npx skills list`で上記7SkillだけがProject Skillsとして検出されることを確認した。

## 運用ルール

- 計画・設計の壁打ちは`grilling`を基本とする。
- 用語やドメイン判断を永続化する必要がある場合だけ、`domain-modeling`を明示的に使う。
- 一般コード理解の変更は`Productivity-Skill`、DB/RWD実行の変更は`rwd-mysql-skill-toolkit`、統計的エビデンス分析の変更は`agentic-evidence-analysis`を編集する。
- `docs/Artifacts/`には現行の参照文書だけを置き、過去の計画・検証・完了報告は`docs/Archives/`に移す。
- リポジトリ内の文書リンクは相対パス、外部リポジトリへのリンクは絶対URLを使う。

## 検証基準

```bash
find .agents/skills -mindepth 1 -maxdepth 1 -type d | sort
npx skills list
git diff --check
git status --short --branch
```

期待状態は、Skill一覧が本書の7件と一致し、Markdownの空白エラーがなく、各正本リポジトリの作業ツリーと追跡先が一致していることである。
