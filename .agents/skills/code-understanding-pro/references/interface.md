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

Quick Modeはチャットのみで完結する。それ以外のモードは3ファイルを必須とする。

## `run_meta.json`

| フィールド | 型 | 説明 |
|---|---|---|
| `interface_version` | string | この契約の版 |
| `skill` | string | 成果物を所有するSkill |
| `skill_version` | string | Skill版 |
| `mode` | string | Full / Review / Documentation / Refactoring |
| `adapter` | string | `generic` / `sql` / `stats` |
| `audience` | string | `beginner` / `practitioner` / `expert` |
| `target` | string | 解析対象 |
| `report_file` | string | 常に `report.md` |
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
