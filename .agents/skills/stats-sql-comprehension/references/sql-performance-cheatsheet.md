# SQLパフォーマンス＆アンチパターン分析チェックリスト

## 1. 最重要パフォーマンスチェック項目

| チェック観点 | 症状・アンチパターン | 改善策 |
|---|---|---|
| **フルスキャン** | `WHERE` 句でのパーティションキー未指定、関数適用 `WHERE DATE(ts) = '2026-01-01'` | パーティションキーを直接比較、インデックス活用 |
| **JOINによる行数爆発** | 多対多の関係を持つテーブル同志の `JOIN` | `JOIN` 前にユニークキー化 (`GROUP BY` / `DISTINCT`) または `EXISTS` 利用 |
| **不要データのロード** | 巨大テーブルに対する `SELECT *` | 必要なカラムのみを指定 (`SELECT colA, colB`) |
| **過度なシャッフル** | 巨大データ同志の `GROUP BY` や非効率な `COUNT(DISTINCT)` | `APPROX_COUNT_DISTINCT` 検討、前段での絞り込み |
| **ウィンドウ関数の範囲** | `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` の乱用 | 必要な範囲に絞る (`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`) |

## 2. BigQuery / dbt 固有の最適化観点

- **マテリアライズドモデルの活用**: 頻繁に参照される重いCTEは dbt の `ephemeral` ではなく `table` や `incremental` としてマテリアライズ。
- **パーティションとクラスタリング**: `partition_by` および `cluster_by` の設計が検索クエリと一致しているか。
