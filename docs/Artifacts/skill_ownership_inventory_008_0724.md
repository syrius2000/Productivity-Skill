# Skill正本・移行インベントリ

created: 2026-07-24 04:11 (JST)
author: AI Agent (Codex GPT-5)

## 目的

`Productivity-Skill`、`rwd-mysql-skill-toolkit`、`agentic-evidence-analysis` の責任範囲を固定し、汎用Skillの移行元と削除前ソースツリーを追跡可能にする。

## 正本の割り当て

| 領域 | 正本 | 編集判断 |
| --- | --- | --- |
| 汎用コード理解・開発生産性Skill | [Productivity-Skill](../../README.md) | 汎用のコード理解、レビュー、設計・開発支援を変更する場合は本リポジトリを編集する。 |
| DB固有Skill・RWDデータワークフロー | [rwd-mysql-skill-toolkit](https://github.com/syrius2000/rwd-mysql-skill-toolkit) | DB固有Skillの正本かつ、他の2リポジトリを利用する「RWDデータワークフローの実行・統合ハブ」である。 |
| VCD・統計的エビデンス分析Skill | [agentic-evidence-analysis](https://github.com/syrius2000/agentic-evidence-analysis) | VCD・統計的エビデンス分析を変更する場合は同リポジトリを編集する。 |

今回、`agentic-evidence-analysis` は変更していない。

## 移行の来歴

- 移行元リポジトリ: `rwd-mysql-skill-toolkit`
- 移行元コミット: `e8448079a9429ba7a925cdc1481c7a7e05584df1`
- 移行先: 本リポジトリの [`.agents/skills/`](../../.agents/skills/)
- 検証済みスイート結果: 19 passed

### コード理解スイート

| Skill | 現行バージョン | 移行後の役割 |
| --- | --- | --- |
| [`code-understanding-pro`](../../.agents/skills/code-understanding-pro/SKILL.md) | 2.0.0-ja | 親ルーター。`generic`、`sql`、`stats` の各経路と共通成果物契約を統合する。 |
| [`code-understanding-pyramid`](../../.agents/skills/code-understanding-pyramid/SKILL.md) | 3.0.0 | 5段階の理解順序を提供する共通フレームワーク。 |
| [`stats-sql-comprehension`](../../.agents/skills/stats-sql-comprehension/SKILL.md) | 2.0.0 | SQL・統計解析の専門アダプター。 |

### 移行ファイルのカテゴリ別インベントリ

| Skill | 移行元パス | ファイル数 | カテゴリ |
| --- | --- | ---: | --- |
| `code-understanding-pro` | `.agent/skills/code-understanding-pro/` | 25 | 親ルーター、成果物テンプレート、出力契約、収集・検証・出力スクリプト、テスト。 |
| `code-understanding-pyramid` | `.agent/skills/code-understanding-pyramid/` | 1 | 5段階理解フレームワーク。 |
| `stats-sql-comprehension` | `.agent/skills/stats-sql-comprehension/` | 7 | SQL・統計アダプター、出力テンプレート、参照資料、マニフェスト。 |
| `teach` | `.agent/skills/teach/` | 6 | 発動条件を正本へ反映した教育Skillと補助フォーマット。 |
| `writing-great-skills` | `.agent/skills/writing-great-skills/` | 3 | 発動条件を正本へ反映したSkill作成支援。 |

## 削除前ソースツリーの監査用SHA-256

各ダイジェストは、`git ls-tree -r --full-tree e844807 .agent/skills/<skill>` の標準出力に対してSHA-256を計算した値である。

| Skill | SHA-256 |
| --- | --- |
| `code-understanding-pro` | `1760c288cbedae0048e501d4efa4217fdc708d6edba9ab7be68ec46a08bab238` |
| `code-understanding-pyramid` | `6cdb216a59764ad491af093cc663e4211748dde36cd90edfe42019d1a6fd3e7a` |
| `stats-sql-comprehension` | `02ead5cce9b7c89913ba0491f372f8d8bab63652b8646531376c7a1f09f0a2d9` |
| `teach` | `72d843d538ae011bafb540bd805b52524d5fab8d1a2fcf1e0e8814a05668f626` |
| `writing-great-skills` | `571c839bdb281eb66953c0d3980d2e97d80af04da981e17bf7598d9d4b9ca7e8` |

## 運用上の判断

- 汎用Skillの改善は本リポジトリで一元管理し、`rwd-mysql-skill-toolkit` に複製を維持しない。
- DB固有の実装やRWD実行フローは `rwd-mysql-skill-toolkit` で管理する。
- VCD・統計的エビデンス分析の実装は `agentic-evidence-analysis` で管理する。
- toolkit側の複製削除は、この移行記録と本リポジトリの導入検証を前提に別タスクで実施する。
