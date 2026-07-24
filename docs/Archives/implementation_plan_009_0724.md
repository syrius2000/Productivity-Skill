# agentic-evidence-analysis 正本化・責任境界整理 作業計画

created: 2026-07-24 07:36 (JST)
author: Codex (GPT-5)

## 目的

`agentic-evidence-analysis` を統計的エビデンス分析の正本として明確化し、`Productivity-Skill`、`rwd-mysql-skill-toolkit`との重複と責任境界を整理する。

## 最終責任分担

| リポジトリ | 責任 |
|---|---|
| `Productivity-Skill` | 一般コード・SQL・R/Pythonコード理解 |
| `agentic-evidence-analysis` | VCD、カテゴリカル分析、Bayes Factor、Evidence Score、統計的解釈 |
| `rwd-mysql-skill-toolkit` | RWD実行、DB統合、設定・成果物連携 |

## 作業フェーズ

### 1. 現状監査

- `agentic-evidence-analysis` mainと未統合Branchを比較する。
- toolkitとの同名Skill、`shared`、設定schema、テスト、READMEをハッシュ・機能単位で比較する。
- 正本候補、移管候補、toolkitに残す実行連携を一覧化する。

成果物: `agentic-evidence-analysis`側の所有権インベントリ。

### 2. agentic-evidence-analysisの正本宣言

- README/AGENTSの「統合正本」を自己矛盾のない形へ修正する。
- 統計分析Skill、設定schema、統計品質契約、分析テストを正本範囲として明記する。
- `codex/agent-only-evidence-reference`は、そのままmergeせず、必要な変更だけ再選別する。

### 3. toolkitとの接続整理

- toolkitのDB/RWD実行Skillは維持する。
- 統計アルゴリズム・VCD解釈・Evidence Scoreの正本はagentic側へ寄せる。
- toolkit側の同名Skillは、重複実体を削除するか、実行ハブ用の薄い連携層へ縮小する。
- `.agent/shared`は一括削除せず、統計分析用・実行連携用の責任を個別判定する。

### 4. 契約テストと導入確認

- 正本リポジトリからSkillを導入できることを確認する。
- toolkitからRWD実行が成立することを確認する。
- 同名Skillの二重管理がないこと、READMEの責任記述と実ファイルが一致することを検証する。

### 5. 公開

- agentic側を先にcommit・pushする。
- 公開先からの導入確認後、必要なtoolkit整理をcommit・pushする。
- Branch削除、履歴書換え、`shared`の移動・削除は別途承認なしには行わない。

## 承認ゲート

- Gate A: 現状監査と所有権インベントリの確認。
- Gate B: agentic側の正本宣言と移管対象の承認。
- Gate C: toolkit側の重複削除・薄い連携層化の承認。
- Gate D: 両リポジトリのテスト・導入確認後にpush。

この計画の提示時点では、コード変更・Skill移動・Branch削除・pushを実行しない。
