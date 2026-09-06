---
name: stats-sql-comprehension
description: Use when code-understanding-pro needs specialist analysis of complex analytical SQL, dbt models, BigQuery queries, CTEs, window functions, or R/Python statistical code. Return findings to that parent Skill; do not operate as a standalone report writer.
version: "2.1.0"
license: "MIT"
---

# 統計解析＆SQL高度解読スキル (stats-sql-comprehension)

## 目的

このSkillは、高度で複雑な**分析用SQL（dbtモデル, BigQuery, CTE, ウィンドウ関数）**および**統計解析コード（R, Python）**を単に「説明」するだけでなく、データフローの可視化、処理の追跡、パフォーマンスおよび統計的妥当性の評価、最適化提案までを段階的に実行します。

---

## スイート内の役割

本Skillは `code-understanding-pro` の専門アダプターである。

| 対象                    | アダプター | テンプレート                      |
| ----------------------- | ---------- | --------------------------------- |
| SQL、dbt、BigQuery、CTE | `sql`      | `assets/output-template-sql.md`   |
| R/Python統計解析コード  | `stats`    | `assets/output-template-stats.md` |

- 共通理解の順序は `code-understanding-pyramid` を使う。
- 成果物は親Skillの `report.md`、`run_meta.json`、`source_manifest.json` に統合する。親Skillが利用できない場合は、保存や検証を開始せず、その制約を明示して専門観点だけを返す。
- 独自の出力ディレクトリや長文チャット回答を作らない。
- 完了前に親Skillの `validate_report.py` を対応アダプターで実行する。

## SQL安全契約

- SQLは原則として読解対象であり、無承認では実行しない。ユーザーの明示承認なしに実行しない。
- 実行が承認された場合も、まず読み取り専用の件数・重複・NULL・JOIN前後検証を行う。
- DB名、SQL方言、1行の粒度、JOINキーが不明な場合は推測と事実を分ける。
- PHI/PIIや認証情報をレポートへ複製しない。

---

## 追加する専門確認

親Skillの理解順序を繰り返さず、親から渡された対象・事実・未確認点・依頼観点に対して、該当する行だけを確認する。情報がない項目は推測せず「未確認」と返す。結論に必要な情報がコードにない場合は、非該当とはせず未確認とする。

## SQL追加確認

| 対象となる入力 | 確認すること |
|---|---|
| テーブル、CTE、集計、または1行の意味 | 粒度と主キー候補を確認し、不明なら未確認とする |
| JOINまたは複数テーブル | キーの一意性、結合前後の粒度、行数増加が集計へ与える影響を確認する |
| WHERE、CASE、NULL処理 | 絞り込み、Outer JOIN後のNULL、三値論理による除外を確認する |
| GROUP BY、集計関数、window関数 | 集計単位、重複合算、window枠を確認する。`DISTINCT`や近似集計は意味・精度・方言を確認してから提案する |

## 統計追加確認

| 対象となる入力 | 確認すること |
|---|---|
| 比較、推定、予測、対象集団 | 推定対象と母集団を区別する |
| 除外、追跡、欠測、サブセット | 選択・欠測の条件と一般化可能性への影響を確認する |
| 群比較、因果、観察データ | 交絡と選択バイアスを分ける。処置群の平均だけから因果効果を主張しない |
| モデル、検定、推定量 | 前提、適合確認、未確認の前提を示す |
| 乱数、依存パッケージ、実行環境 | 再現に必要な情報と不足を示す |

親Skillへ返す専門節の形式は `assets/output-template-sql.md` または `assets/output-template-stats.md` を参照する。データフロー図は、親Skillが `complex` と判定した場合だけ作る。

## 参照ファイル

SQL性能・方言の詳細が判断に必要な場合だけ `references/sql-performance-cheatsheet.md` を読む。統計手法・バイアスの詳細評価が必要な場合だけ `references/stats-validation-checklist.md` を読む。
