# 新スキル企画立案および実施計画: 統計解析＆SQL高度解読スキル (stats-sql-comprehension)

created: 2026-07-23 00:55 (JST)
author: AI Agent (Gemini 3.6 Flash)

## 1. 企画の目的と背景

### 1.1 背景とニーズ

現在リポジトリには汎用的なコード理解スキル（`code-understanding-pro` 等）が配置されていますが、製薬・統計・RWD（リアルワールドデータ）・データ分析の実務においては、以下のニーズが極めて高い状況です：

1. **複雑なSQLの解読・解説のニーズ**: CTE（共通テーブル式）、ウィンドウ関数、複雑なJOIN、集約ロジック、dbtモデル、BigQueryクエリ等の処理フロー・意味・コストの解説。
2. **統計解析コードの論理妥当性の検証ニーズ**: R / Python 等で書かれた統計モデル、データ前処理、仮説検定、外れ値・欠損値処理、バイアス（選択バイアス・生存者バイアス等）の分析。

### 1.2 提供する価値

新規開発する **`stats-sql-comprehension`** スキルは、統計ロジックとSQLデータパイプラインに特化した段階的解読・解説・評価フレームワークを提供します。

---

## 2. スキル設計コンセプト (企画概要)

### スキル名

**`stats-sql-comprehension`** (統計＆SQLコード高度解読・分析アシスタント)

### 起動条件（トリガーキーワード）

- 「このSQLを説明して」「クエリのロジックを解析して」「SQLを解読して」「dbtモデルを解説して」
- 「統計コードをレビューして」「Rの解析ロジックを説明して」「集計ロジックの妥当性を評価して」
- 「SQLのパフォーマンスやデータフローを可視化して」

### コア機能・フレームワーク (5段階の統計＆SQL理解ピラミッド)

1. **Step 0: データコンテキスト把握 (Context)**
   - 対象SQL / 統計コードの役割、入力テーブル・カラム、出力指標、対象データベースエンジン（BigQuery, dbt, PostgreSQL, R/Python）の特定。
2. **Step 1: データフロー＆構造概要 (Structural Mapping)**
   - CTEや中間テーブルの流れをラフなデータフロー（Mermaidリネージ図）で可視化。
   - 統計解析プロセスの全体像（抽出 ➔ 前処理/集計 ➔ モデリング ➔ 出力）を一文要約。
3. **Step 2: SQLロジック＆統計処理の詳細追跡 (Detail Trace)**
   - **SQL**: JOIN条件（Inner/Outer/Cross）による行数膨張リスク、NULLハンドリング、ウィンドウ関数の範囲 (`PARTITION BY`, `ROWS BETWEEN`) の正確なトレース。
   - **統計**: 前処理（Imputation, フィルタリング）、変数変換、群間比較・推定式の追跡。
4. **Step 3: 統計的妥当性＆パフォーマンス評価 (Audit & Optimization)**
   - **SQL効率**: フルスキャン、シャッフル、インデックス/パーティション利用、重複発生リスクの評価。
   - **統計的品質**: 生存者バイアス、選択バイアス、検定前提条件、データ欠損メカニズムの評価。
5. **Step 4: 実務アウトプット生成 (Value Output)**
   - わかりやすい解説ドキュメント、SQLリファクタリング・高速化案、データ品質検証クエリの提案。

---

## 3. ディレクトリ構成案

```text
.agents/skills/stats-sql-comprehension/
├── SKILL.md                           # スキル本体定義（Frontmatter + 理解ピラミッドガイド）
├── manifest.json                      # スキルメタデータ
├── assets/
│   ├── output-template-sql.md         # SQL解読・解説用標準テンプレート
│   ├── output-template-stats.md       # 統計コード評価用標準テンプレート
│   └── mermaid-dataflow-patterns.md   # SQLデータフロー・リネージのMermaidパターン集
└── references/
    ├── sql-performance-cheatsheet.md   # SQLアンチパターン・パフォーマンス最適化チェックリスト
    └── stats-validation-checklist.md  # 統計解析・RWDパイプライン妥当性チェックリスト
```

---

## 4. 実施計画 (Implementation Roadmap)

### フェーズ 1: スキル定義ファイル群の作成

- `SKILL.md` の作成（YAML Frontmatter、5段階フレームワーク、SQL/統計固有ルール）。
- `manifest.json` の記述。
- `assets/` (テンプレート3種) および `references/` (チェックリスト2種) の作成。

### フェーズ 2: ローカル検証

- `npx skills list` および `npx skills ls --json` によるスキルの認識確認。
- サンプルSQLおよび統計コードに対する動作シミュレーション。

### フェーズ 3: リポジトリ統合とドキュメント更新

- `README.md` に `stats-sql-comprehension` スキルを追加。
- Git コミットおよび GitHub リモートリポジトリ (`syrius2000/Productivity-Skill`) への PUSH。

---

## 5. 承認のお願い

上記企画立案および実施計画の内容をご確認の上、実際のスキル作成および配置・PUSH作業へ進めてよろしければ**「承認」**または**「実行してください」**とお知らせください。
