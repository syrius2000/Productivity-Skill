# Productivity Skill Portfolio

AI コーディングエージェント（Antigravity, Cursor, Claude Code, Codex, 及びそのCLI）の生産性を飛躍的に高めるためのエージェントスキル（Agent Skills）コレクションです。

---

## 🧭 汎用Skillの正本と編集先

`Productivity-Skill` は、汎用的なコード理解・開発生産性Skillと、配布対象として同期されたQuality Loop Skillを管理するリポジトリです。一般コード、SQL、統計コードの理解・レビューや、このリポジトリで管理するSkillの改善を行う場合は、対象の正本境界を確認してから編集します。

| 編集したい領域 | 正本リポジトリ | 編集先・責任範囲 |
| :--- | :--- | :--- |
| **汎用コード理解・開発生産性** | このリポジトリ | [`.agents/skills/`](./.agents/skills/) 配下。`code-understanding-pro` は親Skillとして、一般コードを `generic`、SQLを `sql`、R/Python統計コードを `stats` に分岐する。 |
| **Quality Loop QA管理** | `QA-products`（ローカル正本リポジトリ） | 案件・仕様・テスト・実装回答の正本はQA-products。Productivity-Skillの`quality-review` / `quality-response`は検証済みの配布用Skillとして限定同期する。 |
| **DB固有SkillとRWDワークフロー** | [rwd-mysql-skill-toolkit](https://github.com/syrius2000/rwd-mysql-skill-toolkit) | DB固有Skillの正本であり、`Productivity-Skill` と `agentic-evidence-analysis` を利用する「RWDデータワークフローの実行・統合ハブ」。 |
| **VCD・統計的エビデンス分析** | [agentic-evidence-analysis](https://github.com/syrius2000/agentic-evidence-analysis) | VCD・統計的エビデンス分析Skillの正本。 |

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
├── tests/                       # リポジトリ保守・Skill契約検証テスト
└── README.md
```

実装計画や作業報告は `docs/Artifacts/`、完了済みの履歴や過去の整理履歴は [アーカイブ概要](./docs/Archives/README.md) で確認します。
公開する各Skillのバージョンは `SKILL.md` の front matter（`version`）を正本とし、`manifest.json` があるSkillではその値を一致させます（`VERSION` はCLI同梱版など実行時に参照する補助情報）。Skillの実際の起動条件・出力契約・安全境界は、各Skillの `SKILL.md` を正本とします。

---

## 🚀 はじめに (Getting Started)

本リポジトリは、Agent Skills形式のSkillを`.agents/skills/`で管理します。公開配布元から導入する場合は、利用するエージェントと配布経路が対応していることを確認してください。

### インストール方法

```bash
# プロジェクトへの導入
npx skills add syrius2000/Productivity-Skill

# グローバル導入
npx skills add syrius2000/Productivity-Skill -g
```

### 起動方法のルール

- **自然言語自動起動 (Model-invoked)**: 自然言語で依頼すると、エージェントが状況を判別して自動起動します。
- **手動コマンド起動 (User-invoked)**: `disable-model-invocation: true` の`teach`と`writing-great-skills`は、自然言語による自動起動ではなく、スラッシュコマンド等で明示的に起動します。
- **導入経路の確認**: `npx skills`を利用する場合のコマンドや配置先は、利用するエージェントとCLIの現行仕様を確認してください。このREADMEはローカルリポジトリの構成を説明するもので、外部公開・配布の成功を保証するものではありません。

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

親Skill `code-understanding-pro`、共通理解フレームワーク `code-understanding-pyramid`、専門アダプター `stats-sql-comprehension` の3スキルが連携して高度なコード解読・レビューを提供します。

| Skill | 現行バージョン | 役割 |
| :--- | :---: | :--- |
| [`code-understanding-pro`](./.agents/skills/code-understanding-pro/SKILL.md) | 2.3.0-ja | 親Skill。対象を判定し、一般コードは `generic`、SQLは `sql`、R/Python統計コードは `stats` へ分岐して、共通の成果物契約に統合する。 |
| [`code-understanding-pyramid`](./.agents/skills/code-understanding-pyramid/SKILL.md) | 3.0.0 | 5段階の理解順序を提供する共通フレームワーク。 |
| [`stats-sql-comprehension`](./.agents/skills/stats-sql-comprehension/SKILL.md) | 2.1.0 | SQL・dbt・BigQueryとR/Python統計解析の専門アダプター（詳細は [統計解析＆SQL高度解読](#1--統計解析sql高度解読-stats--sql-suite) 参照）。 |

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

### 3. 🔬 方針・実装着手前の軽量レビュー (Pre-Implementation Review)

#### 🧭 **`decision-plan-review`**
- **概要**: 方針や技術選択を覆し得る重大な前提・未知の制約を早期に確認し、手戻りのない意思決定を支援するレビュー専用スキル。
- **特徴**: 正式な仕様書（Spec）がなくても、計画やアイデアの段階で「前提の破綻」「隠れたトレードオフ」を抽出します。
- **利用場面 / 起動例**:
  - 「この方針の想定が甘くないか、後戻りする条件だけ確認して」
  - 「技術選択の前提に重大なリスクがないかレビューして」

#### 🚦 **`implementation-readiness-review`**
- **概要**: 具体的な変更計画・設計に対し、着手前に確認すべきことと実装中に決められることを整理し、実装準備状況（Ready）を判定するスキル。
- **特徴**: 1画面程度の読み取り専用レビュー。一般的な計画作成では誤発火せず、実装着手前の手戻り要因をピンポイントで洗い出します。
- **利用場面 / 起動例**:
  - 「この計画で実装開始してよいか、手戻り要因を見て」
  - 「受入基準とテスト方針が明確になっているか確認して」

---

### 4. 🛡️ 厳格QMS型QA＆品質ループ (Quality Loop Suite)

#### 🔍 **`quality-review`** (v1.5.0)
- **概要**: Quality Loop案件において独立レビュアー（Reviewer）として動作し、専用CLI経由で安全に品質検証を行うスキル。
- **適用条件**: 正式なQuality Loop案件でReviewer工程を行う場合、または対象ファイルが明示された単発QAを`review-standalone`で開始する場合に使用します。一般的なコードレビューの入口ではありません。
- **特徴**: 案件正本（`case.json`）の直接改ざんを禁止し、CLIによる状態遷移制御（単発開始 `review-standalone`、初回レビュー `review`、計画評価 `review-plan`、独立検証 `verify`、残余リスク評価 `assess-risk`）、申告外変更の機械的遮断（`undeclared-change-detected`）、比例性ゲートを厳格に適用します。
- **境界**: `review-standalone`は案件を開始してレビュー担当者へ引き渡すbootstrapであり、Finding、品質適合、受入、実装許可、Owner裁定を単独では生成しません。
- **利用場面 / 起動例**:
  - Quality Loop案件でステータスが `next_role=reviewer` の際に自動起動。
  - case情報がない単発QAでは、対象ファイルを `--target` または `--artifact` で指定して `review-standalone` から開始。

#### ✍️ **`quality-response`** (v1.4.0)
- **概要**: Quality Loop案件において実装者（Implementer）として動作し、専用CLI経由で計画や修正・反証エビデンスを提出するスキル。
- **特徴**: いきなり修正せず事前に計画合意を結ぶ「Plan Before Fix」を強制。自己受入・自己クローズを物理的に禁止し、Owner裁定への境界を遵守します。
- **利用場面 / 起動例**:
  - Quality Loop案件でステータスが `next_role=implementer` の際に自動起動（`submit-plan`, `submit-response`）。

---

### 5. 🌶️ 思考整理・設計のストレステスト (Grilling)

#### 🔥 **`grilling`**
- **概要**: プラン、意思決定、設計アイデアに対し、AIが「デザインツリー（決定境界のフロンティア）」をラウンド形式で徹底的に面接・質問する思考検証スキル。
- **特徴**: 調査可能な事実はAI自身が環境から調べ、ユーザーには意思決定のみを問う。未確定の質問群をフロンティアとしてラウンドごとに整理し、思考の抜け漏れを限界まで潰します。
- **利用場面 / 起動例**:
  - 設計やプランの検討時に「grill」「面接して」「設計のストレステストをして」「深掘りして」

---

### 6. 🏗️ ドメインモデリング・ユビキタス言語管理

#### 📘 **`domain-modeling`**
- **概要**: チームやプロジェクト固有の用語集（`CONTEXT.md`）およびドメイン構造モデルをアクティブに構築・保守するスキル。
- **特徴**: 曖昧な言葉遣いや既存用語との不一致をその場で指摘し、真に必要なトレードオフが存在する場合にのみADR（Architecture Decision Record）の作成を提案します。
- **利用場面 / 起動例**:
  - 「用語集（Glossary）を作成・更新して」「ドメインモデルを定義して」「用語のブレを指摘して」

---

### 7. 👨‍🏫 学習・教育支援

#### 📚 **`teach`**
- **概要**: 一方的な解説ではなく、対話形式で段階的に技術やコードの仕組みを教え、`./docs/learning/` 配下にポータル（`INDEX.html`）や教材・学習記録を体系的に構築する教育スキル。
- **利用場面 / 起動例**:
  - `/teach`（明示起動）: 「〜について体系的に学びたい」「ステップバイステップで教えて」
- [日本語の利用案内](./.agents/skills/teach/README.md)

---

### 8. 🖋️ スキル開発・設計メタガイド

#### 🛠️ **`writing-great-skills`**
- **概要**: エージェント用の新しいスキルを作成・修正する際、予測可能性（Predictability）、牽引語（Leading Words）、情報階層・段階的開示（Progressive Disclosure）、No-op枝刈り等を用いて高品質に仕上げるためのメタスキル。
- **利用場面 / 起動例**:
  - `/writing-great-skills`（明示起動）: 新しいスキルの設計・作成、既存スキルのリファクタリング
- [日本語の利用案内](./.agents/skills/writing-great-skills/README.md)

---

### 9. 🗃️ ドキュメント管理・自動アーカイブ

#### 📦 **`artifacts-archiver`**
- **概要**: `./docs/Artifacts/` 内の完了済み計画書や報告書を精査し、対象期間を明記したまとめ文書へ集約して `./docs/Archives/` へ退避するスキル。
- **特徴**: アクティブな計画書のファイル名・連番を保持し、同じ案件の計画・実装・検証記録を一つのサマリーへまとめます。
- **利用場面 / 起動例**:
  - 「Artifactsを整理して」「過去の計画書をアーカイブして」「古い書類をまとめて」

---

## 📜 ライセンス

本リポジトリは、原則として [MIT License](./LICENSE) のもとで公開されています。

各スキル個別の利用条件については、各スキルの `SKILL.md`（front matter の `license` 項目）または同梱のライセンス文書をご確認ください。
- **汎用・教育・作業支援スキル（11件）**: `MIT`
- **`code-understanding-pro`**: `Internal use`（個人利用・社内検討向け。詳細は同梱の [`LICENSE.txt`](./.agents/skills/code-understanding-pro/LICENSE.txt) を参照）
