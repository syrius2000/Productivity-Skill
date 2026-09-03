# リポジトリ・Skill正本整理のアーカイブ概要

created: 2026-08-19 22:03 (JST)
update: 2026-08-19 22:03 (JST)
author: Codex (GPT-5)

## 対象期間

2026-07-24 〜 2026-08-19

## アーカイブ対象

- `docs/Artifacts/repository_current_state_012_0724.md`

本書は、指定されたアクティブ計画書 `docs/Artifacts/implementation_plan_012_0819.md` を保持し、それ以外のArtifactをアーカイブする指示に基づいて作成した。元の個別文書は本概要へ統合したため、`docs/Artifacts/` から整理した。

## 旧文書の要約

### 正本と責任分担

- `Productivity-Skill` は一般コード理解、SQL・統計コード理解、設計、学習、Skill開発支援を担当する。
- `rwd-mysql-skill-toolkit` はDB固有SkillとRWDデータワークフローの実行・統合を担当する。
- `agentic-evidence-analysis` はVCD、カテゴリカル分析、Bayes Factor、Evidence Score、統計的エビデンス解釈を担当する。
- 汎用Skillを複数リポジトリで二重管理せず、責任領域ごとに正本を分離する。

### `Productivity-Skill` のSkill構成

アーカイブ時点のリポジトリ内Skillは次の7件である。

- `code-understanding-pro`
- `code-understanding-pyramid`
- `stats-sql-comprehension`
- `grilling`
- `domain-modeling`
- `teach`
- `writing-great-skills`

### 整理済みの不要Skill

重複または現行運用に不要として、次のSkillを整理済みと記録していた。

- `grill-me`
- `grill-with-docs`
- `improve-codebase-architecture`
- `to-spec`
- `to-tickets`
- `diagnosing-bugs`

### 当時の検証基準

旧文書では、Skillディレクトリ一覧、`npx skills list`、`git diff --check`、`git status --short --branch` を確認基準としていた。Skill一覧が7件と一致し、Markdown空白エラーがなく、正本リポジトリの作業ツリーと追跡先が一致することを期待状態としていた。

## 現行運用への引継ぎ

- 現在の実装計画は `docs/Artifacts/implementation_plan_012_0819.md` に保持する。
- 過去の計画・検証・完了報告は `docs/Archives/` に保存する。
- リポジトリ内の文書リンクは相対パス、外部文書へのリンクは絶対URLを使用する。
- 本概要は旧文書の履歴を保持するための要約であり、現在のSkill件数やGit状態の最新確認結果を保証するものではない。
