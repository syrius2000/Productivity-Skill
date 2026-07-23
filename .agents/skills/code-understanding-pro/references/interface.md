# Code Understanding Report Interface

interface_version: `2.0`

## 役割

| Skill | 役割 | 成果物の所有者 |
|---|---|---|
| `code-understanding-pro` | 依頼の判定、対象確認、出力管理、チャット要約 | 所有する |
| `code-understanding-pyramid` | 文脈、概要、詳細、設計、活用の理解フレーム | 所有しない |
| `stats-sql-comprehension` | SQL・統計コード固有の分析観点 | 所有しない |

下位Skillは独自の長文チャット回答や別出力ディレクトリを作らず、親Skillのレポート本文へ分析結果を返す。

## 成果物

```text
skill_out/code_understanding/<target>/run_<id>/
├── report.md
├── run_meta.json
└── source_manifest.json
```

Quick Modeはチャットのみで完結する。Full、Review、Documentation、Refactoringは上記3ファイルを必須とする。

## Context補助成果物（レポート契約の対象外）

`collect_code_context.py --output-root` は、解析済みレポートではなく、親Skillを補助するContext成果物を保存する。

```text
skill_out/code_understanding/<target>/run_<id>/
├── code_context.md
├── run_meta.json       # mode: Context
└── source_manifest.json
```

`code_context.md` は収集した生テキストを含む補助資料であり、Full、Review、Documentation、Refactoringの `report.md` 契約の対象外である。必須見出しを満たすことを要求せず、`validate_report.py` の検証CLIの対象外とする。収集結果をそのまま `report.md` へ強制してはならない。

Context成果物の `run_meta.json` は `mode=Context` と `report_file=code_context.md` を記録する。

Contextの `source_manifest.json` は、実際に `code_context.md` へ出力された各ファイルを記録する。ディレクトリ引数は実際に出力されたファイルへ展開し、出力上限などで省略されたファイルやディレクトリ自体は記録しない。

## `run_meta.json`

| フィールド | 型 | 説明 |
|---|---|---|
| `interface_version` | string | この契約の版 |
| `skill` | string | 成果物を所有するSkill |
| `skill_version` | string | Skill版 |
| `mode` | string | Full / Review / Documentation / Refactoring。Context成果物では `Context` |
| `adapter` | string | `generic` / `sql` / `stats` |
| `audience` | string | `beginner` / `practitioner` / `expert` |
| `target` | string | 解析対象 |
| `report_file` | string | 通常成果物では `report.md`、Context成果物では `code_context.md` |
| `generated_at` | string | JSTを含むISO 8601時刻 |

## `source_manifest.json`

ソース本文は複製せず、パス、存在状態、ファイルサイズ、SHA-256だけを記録する。存在しないソースは `exists=false` とし、推測で補完しない。

## Markdown必須節

1. 結論
2. 対象と前提
3. 全体像
4. 処理フロー
5. 詳細
6. 初学者向け用語解説
7. 注意点・リスク
8. 根拠ファイル・行番号

`sql` アダプターは、データ粒度、テーブル・CTE一覧、JOINと行数変化、検証SQLも必須とする。

`stats` アダプターは、対象母集団、欠測・除外、推定量・前提、バイアスと妥当性、再現・検証コードも必須とする。

## 完了条件

```bash
python3 .agents/skills/code-understanding-pro/scripts/validate_report.py \
  skill_out/code_understanding/<target>/run_<id>/report.md \
  --adapter generic
```

検証が成功するまで、チャットで完了を報告しない。
