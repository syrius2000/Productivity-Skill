# 過去計画・検証資料の統合アーカイブ概要

created: 2026-09-04 18:20 (JST)
update: 2026-09-04 18:20 (JST)
author: Codex (GPT-5)

## 対象期間

2026-07-23 〜 2026-09-04

## 統合対象

本書は、完了済みまたは過去の計画・検証資料を統合した記録である。元ファイルは本書への集約後に整理した。保持対象のアクティブ計画、構造化QA証跡、ZIPバックアップは統合対象外である。

### 旧Artifacts

- `docs/Artifacts/Artifact_001_squash_fix_commits_0820.md`
- `docs/Artifacts/Artifact_002_cherry_pick_18fc9f5_0820.md`
- `docs/Artifacts/Artifact_003_readme_refinement_0820.md`

### 旧Archivesの個別資料

- `archived_summary_001_0819.md`
- `archived_summary_002_0819.md`
- `archived_summary_003_0901.md`
- `completion_report_004_0723.md`
- `completion_report_010_0724.md`
- `implementation_plan_001_0723.md`
- `implementation_plan_003_0723.md`
- `implementation_plan_005_0723.md`
- `implementation_plan_006_0723.md`
- `implementation_plan_007_0724.md`
- `implementation_plan_009_0724.md`
- `implementation_plan_011_0724.md`
- `implementation_plan_012_0819.md`
- `skill_ownership_inventory_008_0724.md`
- `verification_report_002_0723.md`

## 主な経緯

### 1. 初期Skill整備と検証

2026年7月23日に、Skillの整合性確認、`code-understanding-pyramid`の復元・修正、Skill追加、README整備、統計解析・SQL専門Skillの追加が計画・実施された。初期検証資料では、Skill一覧と`npx skills`による導入確認が記録されている。

### 2. 正本化と責任境界の整理

2026年7月24日に、`Productivity-Skill`、`rwd-mysql-skill-toolkit`、`agentic-evidence-analysis`の責任分担、重複Skillの整理、移行インベントリ、Git反映方針が整理された。汎用Skillは`Productivity-Skill`、DB固有SkillとRWDワークフローは別リポジトリ、VCD・統計的エビデンス分析は専門リポジトリを正本とする境界が記録された。

### 3. Skill配置と仕様駆動QAの整備

2026年8月19日に、`spec-driven-qa-review`と関連QA資産の配置、パッケージ整合性、複数サイクルのレビュー・回答・再検証、未解決マーカー、残余リスクの扱いが整理された。構造化されたQA証跡は、別途`docs/Archives/QA/`に保持している。

### 4. コード理解Skillの強化

2026年9月2日に、`code-understanding-pro`、`code-understanding-pyramid`、`stats-sql-comprehension`のモード判定、5段階理解、Mermaid・文章フロー、出力契約、版情報を強化する計画と実施結果が記録された。LLM実呼び出しによる動的代表ケース検証は未実施として残された。

### 5. Productivity-Skillのインベントリ整合

2026年9月4日に、READMEのSkill数を11へ修正し、`spec-driven-qa-review`の案内を追加した。また、全Skillの実在ディレクトリ、入口リンク、manifest、VERSION、front matterの整合性を検証する契約テストを追加し、11件のテストと全11Skillの静的検証に成功した。

## 保持する現行資料

- `docs/Artifacts/Implementation_agy_001.md`：ユーザー指定のアクティブ計画
- `docs/Artifacts/implementation_plan_003_0902.md`：上記アクティブ計画から参照される計画
- `docs/Artifacts/implementation_plan_004_0904.md`：上記アクティブ計画から参照される実装計画・実績
- `docs/Archives/README.md`：本書を案内する索引
- `docs/Archives/QA/QA-0001-plan-012-skill-placement/`：構造化QA証跡
- `docs/Archives/spec-driven-qa-author-response.zip`
- `docs/Archives/spec-driven-qa-review.zip`

## 未解決事項と注意

- `Implementation_agy_001.md`に記載された`code-understanding-pro`の軽量化・再構成は未実施である。
- LLM動的評価、独立QA、commit、push、公開の完了は本書から推定しない。
- 旧QA証跡には、当時存在したArtifactや旧サマリーへの歴史的な参照が含まれる。証跡の改変を避けるため、内容は変更していない。
- 元ファイルの復元が必要な場合はGit履歴から復元できる。今回の整理では、ユーザー指定のアクティブ計画と構造化QA資産を削除していない。
