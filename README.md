# Productivity Skill Portfolio

AI コーディングエージェント（Antigravity, Cursor, Claude Code, Codex, Gemini CLI 等）の生産性を飛躍的に高めるためのエージェントスキル（Agent Skills）コレクションです。

---

## 🧭 汎用Skillの正本と編集先

`Productivity-Skill` は、汎用的なコード理解・開発生産性Skillの正本です。一般コード、SQL、統計コードの理解・レビューを改善する場合は、このリポジトリ内のSkillを編集します。

| 編集したい領域 | 正本リポジトリ | 編集先・責任範囲 |
| --- | --- | --- |
| 汎用コード理解・開発生産性 | このリポジトリ | [`.agents/skills/`](./.agents/skills/) 配下。`code-understanding-pro` は親Skillとして、一般コードを `generic`、SQLを `sql`、R/Python統計コードを `stats` に分岐する。 |
| DB固有SkillとRWDワークフロー | [rwd-mysql-skill-toolkit](https://github.com/syrius2000/rwd-mysql-skill-toolkit) | DB固有Skillの正本であり、`Productivity-Skill` と `agentic-evidence-analysis` を利用する「RWDデータワークフローの実行・統合ハブ」。 |
| VCD・統計的エビデンス分析 | [agentic-evidence-analysis](https://github.com/syrius2000/agentic-evidence-analysis) | VCD・統計的エビデンス分析Skillの正本。 |

### コード理解スイート

| Skill | 現行バージョン | 役割 |
| --- | --- | --- |
| [`code-understanding-pro`](./.agents/skills/code-understanding-pro/SKILL.md) | 2.0.0-ja | 親Skill。対象を判定し、一般コードは `generic`、SQLは `sql`、R/Python統計コードは `stats` へ分岐して、共通の成果物契約に統合する。 |
| [`code-understanding-pyramid`](./.agents/skills/code-understanding-pyramid/SKILL.md) | 3.0.0 | 5段階の理解順序を提供する共通フレームワーク。 |
| [`stats-sql-comprehension`](./.agents/skills/stats-sql-comprehension/SKILL.md) | 2.0.0 | SQL・dbt・BigQueryとR/Python統計解析の専門アダプター。 |

移行の根拠、削除前ソースツリーの監査用ダイジェスト、および検証結果は [Skill正本・移行インベントリ](./docs/Artifacts/skill_ownership_inventory_008_0724.md) を参照してください。

---

## 🚀 はじめに (Getting Started)

本リポジトリ内のスキルはすべて `npx skills` (Agent Skills Standard) に準拠しています。
本リポジトリを導入することで、プロジェクトや各種エージェントで一元化された高品質なスキルを活用できます。

### インストール方法
```bash
# プロジェクトへの導入
npx skills add syrius2000/Productivity-Skill

# グローバル導入
npx skills add syrius2000/Productivity-Skill -g
```

---

## 🛠️ 収録スキル一覧 (13 Skills)

### 1. 📊 統計解析＆SQL高度解読

#### 📈 **`stats-sql-comprehension`** (v2.0.0)
- **概要**: 複雑な分析用SQL（dbt, BigQuery, CTE, ウィンドウ関数）や統計解析コード（R, Python）を5段階ピラミッドで解読・可視化・評価するスキル。
- **特徴**: CTEや結合構造のMermaidリネージ図作成、フルスキャンや多対多結合による行数膨張リスクの検出、統計的バイアス（選択・生存者バイアス等）の検証を行います。
- **起動条件**: 「このSQLを説明して」「クエリを解読して」「dbtモデルを解説して」「データフローを可視化して」「統計コードをレビューして」「SQLのパフォーマンスを評価して」

---

### 2. 🔍 コード理解・レビュー・リファクタリング

#### 📖 **`code-understanding-pro`** (v2.0.0-ja)
- **概要**: 既存コードの段階的理解、詳細解析、コードレビュー、ドキュメント化、安全なリファクタリング支援を包括的に行う日本語スキル。
- **特徴**: 5段階の「理解のピラミッド」に従い、コードの事実・推測・不確実性・リスクを明確に分離して出力します。
- **起動条件**: 「このコードを説明して」「レビューして」「QAして」「リファクタリング案を出して」「DocStringを書いて」

#### 🏛️ **`code-understanding-pyramid`** (v3.0.0)
- **概要**: AIソフトウェアアーキテクトとして、構造把握（準備・概要・詳細・深い理解・活用）を順番に追跡して分析するスキル。
- **特徴**: 意図やテストコードを最優先に検証し、`[CRITICAL]`, `[CONSIDER]`, `[NIT]`, `[FYI]` のマージ基準付きフィードバックを提供。
- **起動条件**: 「review」「explain」「analyze」などの解析要求

---

### 3. 🌶️ 思考整理・設計のストレステスト (Grilling)

#### 🔥 **`grilling`**
- **概要**: プラン、意思決定、設計アイデアに対してAIが多角的に「徹底的な1問1答インタビュー」を行う思考検証スキル。
- **特徴**: 1度に複数質問をせず、対話形式で条件分岐や制約をクリアにしていきます。環境から調べられる事実はAIが調査し、意思決定のみをユーザーに求めます。
- **起動条件**: 設計やプランの検討時、「grill」「面接して」「深掘りして」

#### ⚡ **`grill-me`**
- **概要**: `/grill-me` コマンドで `grilling` スキルを即座に起動するショートカットスキル。
- **起動条件**: `/grill-me`

#### 📑 **`grill-with-docs`**
- **概要**: 面接を進めながら、同時に ADR（アーキテクチャ決定記録）やドメイン用語集（Glossary）ドキュメントをリアルタイム生成する拡張面接スキル。
- **起動条件**: ドキュメント作成を伴う設計面接時

---

### 4. 🐛 デバッグ・品質向上

#### 🕵️ **`diagnosing-bugs`**
- **概要**: 勘や対症療法に頼らず、再現ループの構築と仮説検証によって根本原因を特定・解消する構造的デバッグスキル。
- **特徴**: 「再現ループ構築 ➔ Repro最小化 ➔ 3〜5個の仮説立案 ➔ 計装 ➔ 回帰テスト ➔ クリーンアップ」の6段階プロセスを厳格に適用。
- **起動条件**: 「diagnose」「debug this」「バグの原因を探して」「エラーが起きる」

---

### 5. 📝 ドキュメント・タスク自動生成

#### 📄 **`to-spec`**
- **概要**: チャット上のこれまでの会話文脈とコードベースの理解から、再ヒアリングなしで完全な「仕様書（Spec / PRD）」を自動合成するスキル。
- **特徴**: Problem Statement, Solution, Extensive User Stories, Implementation/Testing Decisions, Out of Scope を網羅。
- **起動条件**: 「仕様書にして」「Specを作成して」

#### 🎟️ **`to-tickets`**
- **概要**: 作成された仕様書（Spec）から、実装可能でマージしやすい単位の作業チケット（タスクリスト）へ自動分割するスキル。
- **起動条件**: 「チケットに分解して」「タスク化して」

---

### 6. 🏗️ アーキテクチャ改善・ドメインモデル管理

#### 📐 **`improve-codebase-architecture`**
- **概要**: コードベース全体の結合度・複雑性・テスト容易性を診断し、安全かつ段階的なリファクタリング計画を立案するスキル。
- **起動条件**: 「アーキテクチャを改善して」「構造を整理して」

#### 📘 **`domain-modeling`**
- **概要**: チームやプロジェクト固有の「ユビキタス言語（用語集/Glossary）」およびドメイン構造モデルを整理・保守するスキル。
- **起動条件**: 用語集の作成・更新、ドメインモデルの定義時

---

### 7. 📚 学習・スキル開発

#### 👨‍🏫 **`teach`**
- **概要**: 一方的な解説ではなく、対話形式で段階的に複雑な技術・アルゴリズム・コードの仕組みを教えてくれる教育スキル。
- **起動条件**: 「教えて」「解説して」「分かりやすく説明して」

#### 🛠️ **`writing-great-skills`**
- **概要**: エージェント用の新しいスキルを作成・修正する際、TDDアプローチと抜け穴塞ぎ（Bulletproofing）によって高品質なスキルを設計するガイドラインスキル。
- **起動条件**: エージェントスキルの自作・修正時

---

## 📁 ディレクトリ構造

```text
.
├── .agents/
│   └── skills/                  # エージェントスキル格納フォルダ
│       ├── code-understanding-pro/
│       ├── code-understanding-pyramid/
│       ├── diagnosing-bugs/
│       ├── domain-modeling/
│       ├── grill-me/
│       ├── grill-with-docs/
│       ├── grilling/
│       ├── improve-codebase-architecture/
│       ├── stats-sql-comprehension/
│       ├── teach/
│       ├── to-spec/
│       ├── to-tickets/
│       └── writing-great-skills/
├── docs/                        # プロジェクトドキュメント
└── README.md
```

---

## 📜 ライセンス

本リポジトリ全体のライセンスは定義していません。各スキルに同梱された
`SKILL.md`、`LICENSE`、`LICENSE.txt` 等の記載を確認してください。
たとえば、`code-understanding-pro` は `Internal Use License`、
`stats-sql-comprehension` は `MIT` と定義されています。
