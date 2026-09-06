# Productivity Skill Portfolio

AI コーディングエージェント（Antigravity, Cursor, Claude Code, Codex, 及びそのCLI）の生産性を飛躍的に高めるためのエージェントスキル（Agent Skills）コレクションです。

---

## 🧭 汎用Skillの正本と編集先

`Productivity-Skill` は、汎用的なコード理解・開発生産性・QA品質管理Skillの正本です。一般コード、SQL、統計コードの理解・レビューや品質管理ワークフローを改善する場合は、このリポジトリ内のSkillを編集します。

| 編集したい領域 | 正本リポジトリ | 編集先・責任範囲 |
| :--- | :--- | :--- |
| **汎用コード理解・開発生産性** | このリポジトリ | [`.agents/skills/`](./.agents/skills/) 配下。`code-understanding-pro` は親Skillとして、一般コードを `generic`、SQLを `sql`、R/Python統計コードを `stats` に分岐する。 |
| **Quality Loop QA管理** | [`QA-products`](/Users/myamaguchi/Programing/QA-products) | 開発・仕様・テストの正本はQA-products。Productivity-Skillの`quality-review` / `quality-response`は検証済み配布成果物として限定同期する。 |
| **DB固有SkillとRWDワークフロー** | [rwd-mysql-skill-toolkit](https://github.com/syrius2000/rwd-mysql-skill-toolkit) | DB固有Skillの正本であり、`Productivity-Skill` と `agentic-evidence-analysis` を利用する「RWDデータワークフローの実行・統合ハブ」。 |
| **VCD・統計的エビデンス分析** | [agentic-evidence-analysis](https://github.com/syrius2000/agentic-evidence-analysis) | VCD・統計的エビデンス分析Skillの正本。 |

### コード理解スイート

| Skill | 現行バージョン | 役割 |
| :--- | :---: | :--- |
| [`code-understanding-pro`](./.agents/skills/code-understanding-pro/SKILL.md) | 2.3.0-ja | 親Skill。対象を判定し、一般コードは `generic`、SQLは `sql`、R/Python統計コードは `stats` へ分岐して、共通の成果物契約に統合する。 |
| [`code-understanding-pyramid`](./.agents/skills/code-understanding-pyramid/SKILL.md) | 3.0.0 | 5段階の理解順序を提供する共通フレームワーク。 |
| [`stats-sql-comprehension`](./.agents/skills/stats-sql-comprehension/SKILL.md) | 2.1.0 | SQL・dbt・BigQueryとR/Python統計解析の専門アダプター。 |

版を公開するSkillでは、`SKILL.md`のfront matterにある`version`を正本とする。`manifest.json`があるSkillでは、その値をfront matterと一致させ、`VERSION`はCLI同梱版など実行時に読むSkillだけが持つ補助情報とする。

過去の整理履歴は [アーカイブ概要](./docs/Archives/README.md) を参照してください。

---

## 🚀 はじめに (Getting Started)

本リポジトリ内のスキルはすべて `npx skills` (Agent Skills Standard) に準拠しています。
本リポジトリを導入することで、各種エージェントで一元化された高品質なスキルを活用できます。

### インストール方法

```bash
# プロジェクトへの導入
npx skills add syrius2000/Productivity-Skill

# グローバル導入
npx skills add syrius2000/Productivity-Skill -g
```

### 起動方法のルール

- **自然言語自動起動 (Model-invoked)**: 自然言語で依頼すると、エージェントが状況を判別して自動起動します。
- **手動コマンド起動 (User-invoked)**: `disable-model-invocation: true` のスキル（`/teach`, `/writing-great-skills` 等）は、常時コンテキストを消費しないよう設計されており、スラッシュコマンド等で明示的に起動します。

---

## 🛠️ 収録スキル一覧 (12 Skills)

### 1. 📊 統計解析＆SQL高度解読 (Stats & SQL Suite)

#### 📈 **`stats-sql-comprehension`** (v2.1.0)
- **概要**: 複雑な分析用SQL（dbt, BigQuery, CTE, ウィンドウ関数）や統計解析コード（R, Python）を5段階ピラミッドで解読・可視化・評価する専門スキル。
- **特徴**: CTEや結合構造のMermaidリネージ図作成、フルスキャンや多対多結合による行数膨張リスクの検出、統計的バイアス（選択・生存者バイアス等）の検証を行います。
- **利用場面 / 起動例**:
  - 「このSQLのデータフローと処理ロジックを説明して」
  - 「BigQuery / dbt モデルのパフォーマンスと結合リスクを評価して」
  - 「R/Pythonの統計解析コード・前処理の論理妥当性をレビューして」

---

### 2. 🔍 コード理解・レビュー・リファクタリング (Code Understanding Suite)

#### 📖 **`code-understanding-pro`** (v2.3.0-ja)
- **概要**: 既存コードの段階的理解、詳細解析、コードレビュー、ドキュメント化、安全なリファクタリング支援を包括的に行う親ルータースキル（日本語完全対応）。
- **特徴**: 対象コードの性質に応じて `generic` / `sql` / `stats` へ適切にルーティングし、事実・推測・不確実性・リスクを明確に分離したレポートを出力します。
- **利用場面 / 起動例**:
  - 「このモジュールの全体構造と振る舞いを解説して」
  - 「関数のリファクタリング案とDocStringを作成して」

#### 🏛️ **`code-understanding-pyramid`** (v3.0.0)
- **概要**: 5段階の「理解のピラミッド（準備・概要・詳細・深い理解・活用）」を提供する共通アーキテクチャフレームワーク。
- **特徴**: 一般コードレビューでは `[Critical]`, `[Major]`, `[Consider]`, `[Nit]`, `[FYI]` の重要度語彙を用い、確証のない推測を排除した客観的レビューを実行します。
- **利用場面 / 起動例**:
  - 「コードの深層レビューと構造解析を実行して」

---

### 3. 🛡️ 厳格QMS型QA＆品質ループ (Quality Loop Suite)

#### 🔍 **`quality-review`** (v1.5.0)
- **概要**: Quality Loop案件において独立レビュアー（Reviewer）として動作し、専用CLI経由で安全に品質検証を行うスキル。
- **特徴**: 案件正本（`case.json`）の直接改ざんを禁止し、CLIによる状態遷移制御（単発開始 `review-standalone`、初回レビュー `review`、計画評価 `review-plan`、独立検証 `verify`、残余リスク評価 `assess-risk`）、申告外変更の機械的遮断（`undeclared-change-detected`）、比例性ゲートを厳格に適用します。
- **利用場面 / 起動例**:
  - Quality Loop案件でステータスが `next_role=reviewer` の際に自動起動。
  - case情報がない単発QAでは、対象Artifactを `--target` または `--artifact` で指定して `review-standalone` から開始。

#### ✍️ **`quality-response`** (v1.4.0)
- **概要**: Quality Loop案件において実装者（Implementer）として動作し、専用CLI経由で計画や修正・反証エビデンスを提出するスキル。
- **特徴**: いきなり修正せず事前に計画合意を結ぶ「Plan Before Fix」を強制。自己受入・自己クローズを物理的に禁止し、Owner裁定への境界を遵守します。
- **利用場面 / 起動例**:
  - Quality Loop案件でステータスが `next_role=implementer` の際に自動起動（`submit-plan`, `submit-response`）。

---

### 4. 🌶️ 思考整理・設計のストレステスト (Grilling)

#### 🔥 **`grilling`**
- **概要**: プラン、意思決定、設計アイデアに対し、AIが「デザインツリー（決定境界のフロンティア）」をラウンド形式で徹底的に面接・質問する思考検証スキル。
- **特徴**: 調査可能な事実はAI自身が環境から調べ、ユーザーには意思決定のみを問う。未確定の質問群をフロンティアとしてラウンドごとに整理し、思考の抜け漏れを限界まで潰します。
- **利用場面 / 起動例**:
  - 設計やプランの検討時に「grill」「面接して」「設計のストレステストをして」「深掘りして」

---

### 5. 🏗️ ドメインモデリング・ユビキタス言語管理

#### 📘 **`domain-modeling`**
- **概要**: チームやプロジェクト固有の用語集（`CONTEXT.md`）およびドメイン構造モデルをアクティブに構築・保守するスキル。
- **特徴**: 曖昧な言葉遣いや既存用語との不一致をその場で指摘し、真に必要なトレードオフが存在する場合にのみADR（Architecture Decision Record）の作成を提案します。
- **利用場面 / 起動例**:
  - 「用語集（Glossary）を作成・更新して」「ドメインモデルを定義して」「用語のブレを指摘して」

---

### 6. 📚 学習・教育支援

#### 👨‍🏫 **`teach`**
- **概要**: 一方的な解説ではなく、対話形式で段階的に技術やコードの仕組みを教え、`./docs/learning/` 配下にポータル（`INDEX.html`）や教材・学習記録を体系的に構築する教育スキル。
- **利用場面 / 起動例**:
  - `/teach`（明示起動）: 「〜について体系的に学びたい」「ステップバイステップで教えて」
- [日本語の利用案内](./.agents/skills/teach/README.md)

---

### 7. 🛠️ スキル開発・設計メタガイド

#### 🖋️ **`writing-great-skills`**
- **概要**: エージェント用の新しいスキルを作成・修正する際、予測可能性（Predictability）、牽引語（Leading Words）、情報階層・段階的開示（Progressive Disclosure）、No-op枝刈り等を用いて高品質に仕上げるためのメタスキル。
- **利用場面 / 起動例**:
  - `/writing-great-skills`（明示起動）: 新しいスキルの設計・作成、既存スキルのリファクタリング
- [日本語の利用案内](./.agents/skills/writing-great-skills/README.md)

---

### 8. 🗄️ ドキュメント管理・自動アーカイブ

#### 🗃️ **`artifacts-archiver`**
- **概要**: `./docs/Artifacts/` 内の完了済み計画書や報告書を精査し、対象期間を明記したまとめ文書へ集約して `./docs/Archives/` へ退避するスキル。
- **特徴**: アクティブな計画書のファイル名・連番を保持し、同じ案件の計画・実装・検証記録を一つのサマリーへまとめます。
- **利用場面 / 起動例**:
  - 「Artifactsを整理して」「過去の計画書をアーカイブして」「古い書類をまとめて」

---

### 9. 🔬 方針・実装着手前の軽量レビュー

#### ✅ **`decision-plan-review`**

- **概要**: 方針や技術選択を覆し得る前提・未知を確認し、人間の意思決定を支援します。正式Specは不要です。
- **起動例**: 「この方針の想定が甘くないか、後戻りする条件だけ確認して」

#### ✅ **`implementation-readiness-review`**

- **概要**: 具体的な変更計画について、着手前に確認すべきことと実装中に決められることを短く整理します。
- **起動例**: 「この計画で実装開始してよいか、手戻り要因を見て」

通常は1画面程度の読取り専用レビューです。一般的な計画作成・実装依頼では起動せず、`READY`も実装承認の代行にはなりません。実装後の正式QAは `quality-review`、回答・修正提出は `quality-response` が担当します。

---

## 📁 ディレクトリ構造

```text
.
├── .agents/
│   └── skills/                  # エージェントスキル格納フォルダ (12 Skills)
│       ├── artifacts-archiver/       # ドキュメント自動アーカイブ
│       ├── code-understanding-pro/   # コード理解・親ルーター (v2.3.0-ja)
│       ├── code-understanding-pyramid/# 5段階理解ピラミッド (v3.0.0)
│       ├── domain-modeling/          # ドメイン用語集・ADR管理
│       ├── grilling/                 # 思考・設計ストレステスト面接
│       ├── quality-response/         # QMS型QA・実装者回答 (v1.4.0)
│       ├── quality-review/           # QMS型QA・独立レビュー (v1.5.0)
│       ├── decision-plan-review/     # 方針・前提の軽量レビュー
│       ├── implementation-readiness-review/ # 実装着手前レビュー
│       ├── stats-sql-comprehension/  # 統計＆SQL高度解読 (v2.1.0)
│       ├── teach/                    # 対話型教育ポータル構築
│       └── writing-great-skills/     # スキル設計・作成メタガイド
├── docs/
│   ├── Archives/                # 過去サマリー文書・ZIPアーカイブ
│   └── Artifacts/               # アクティブ作業用計画・報告書
├── tests/                       # リポジトリ保守・契約検証テスト
└── README.md
```

---

## 📜 ライセンス

本リポジトリ全体のライセンスは定義していません。各スキルに同梱された `SKILL.md`、`LICENSE`、`LICENSE.txt` 等の記載を確認してください。
