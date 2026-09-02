# リポジトリ正本整理・作業完了報告

created: 2026-07-24 12:26 (JST)
author: Codex (GPT-5)

## 1. 実施結果

今回の作業では、3リポジトリの責任境界と正本を確認し、不要な作業Branchを削除した。

| リポジトリ | 正本Branch | 確認した先端 | 状態 |
|---|---|---|---|
| `Productivity-Skill` | `master` | `16596b3` | `origin/master` と一致 |
| `rwd-mysql-skill-toolkit` | `main` | `5cd79f2` | `origin/main` と一致 |
| `agentic-evidence-analysis` | `main` | `dc87797` | 統計的エビデンス分析の正本 |

`agentic-evidence-analysis` の `codex/agent-only-evidence-reference` は、正本の `main` と共通祖先を持たない古い作業系譜であり、現行の正本方針と矛盾するREADMEを含んでいたため、リモートから削除した。

## 2. 責任分担

- `Productivity-Skill`: 一般コード、SQL、R/Pythonコード理解・開発支援Skill。
- `agentic-evidence-analysis`: VCD、カテゴリカル分析、Bayes Factor、Evidence Score、統計的解釈の正本。
- `rwd-mysql-skill-toolkit`: DB固有Skill、RWD実行、データワークフロー統合ハブ。

汎用コード理解SkillとDB/RWD Skillの重複は確認されなかった。toolkit側の共有資産は、RWD実行に必要なものとして維持する。

## 3. 検証結果

- `Productivity-Skill`: `4 passed`
- `rwd-mysql-skill-toolkit`: `30 passed`
- `npx skills list`: Productivity-Skillの13 Skillを検出。
- 公開正本からの導入確認: `agentic-evidence-analysis` の5 Skillを一時ディレクトリへ導入成功。
- `git diff --check`: 両リポジトリで成功。
- ルートの既存コミット `16596b3` を `origin/master` へpush済み。

## 4. worktree整理

以下を確認・整理した。

- `/private/tmp/Productivity-Skill-consolidate-0724`
- `/private/tmp/rwd-mysql-skill-toolkit-cleanup-0724`
- ルート配下の一時的な `rwd-mysql-skill-toolkit/` checkout

整理後は、ルートとtoolkitの正本checkoutだけを残す状態とした。未変更の一時worktreeを削除したため、作業中のコミットや変更は失われていない。

## 5. サブエージェントの高コスト呼び出しを避ける方法

### チャットでの指定

タスク開始時に、次のように明示する。

```text
このタスクではサブエージェントを使用しないでください。
すべてメインエージェントで実施し、並列委譲・追加スレッド生成・Ultra/Max相当の高推論設定を使わないでください。
必要な調査は読み取り専用で、結果を簡潔に要約してください。
```

サブエージェントを許可する場合でも、次のように範囲を固定する。

```text
サブエージェントは最大1件、読み取り専用、低コストモデル・低推論に限定してください。
独立作業がない場合は委譲せず、完了したら直ちに終了してください。
```

### `Config.toml`での強制設定

現在確認したグローバル設定は `/Users/myamaguchi/.codex/config.toml` の次の内容である。

```toml
[agents]
default_subagent_model = "gpt-5.6-terra"
default_subagent_reasoning_effort = "medium"
max_concurrent_threads_per_session = 4
```

サブエージェントを完全に使わない場合は、グローバル設定または信頼したプロジェクトの `.codex/config.toml` に次を設定する。

```toml
[agents]
enabled = false
```

限定的に許可する場合は、次のように同時実行数・モデル・推論量を抑える。

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 1
default_subagent_model = "gpt-5.6-terra"
default_subagent_reasoning_effort = "low"
```

`enabled = false` が最も確実な抑止策である。`enabled = true` の場合、明示的なspawn指定やカスタムAgentファイルの `model` / `model_reasoning_effort` が既定値を上書きし得るため、チャット指示だけに依存しない。特にUltra/Max相当の高推論を使うと自動委譲が起こり得るため、費用を抑える作業では避ける。

## 6. 今後の運用

- 通常の調査・小規模修正は、サブエージェントなしで実施する。
- 並列化が必要な場合だけ、最大1件・読み取り専用・低推論を明示する。
- 大規模変更では、先に日本語の実装計画Artifactを作成し、承認後に実行する。
- Branch削除、push、共有checkoutの整理は、対象を確認してから行う。
