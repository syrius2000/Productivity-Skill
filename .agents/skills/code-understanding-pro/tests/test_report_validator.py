from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "scripts" / "validate_report.py"


def run_validator(path: Path, adapter: str = "generic") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path), "--adapter", adapter],
        text=True,
        capture_output=True,
        check=False,
    )


def valid_report(adapter: str = "generic") -> str:
    specialist_sections = ""
    if adapter == "sql":
        specialist_sections = """
## データ粒度
1行は患者1人です。

## テーブル・CTE一覧
| 名前 | 役割 |
|---|---|
| cohort | 対象集団 |

## JOINと行数変化
JOIN前後の件数を確認します。

## 検証SQL
```sql
SELECT COUNT(*) FROM cohort;
```
"""
    if adapter == "stats":
        specialist_sections = """
## 対象母集団
解析対象と除外条件を示します。

## 欠測・除外
欠測処理と除外件数を示します。

## 推定量・前提
推定量、単位、統計的前提を示します。

## バイアスと妥当性
選択バイアスと一般化可能性を確認します。

## 再現・検証コード
```r
summary(model)
```
"""
    return f"""# コード理解レポート

## 結論
入力を検証して出力します。

## 対象と前提
対象は `src/example.py:1` です。

## 全体像
3段階で処理します。

## 処理フロー
```mermaid
flowchart TD
  A[入力] --> B[検証] --> C[出力]
```

## 詳細
入力例を使って値の変化を追跡します。

## 初学者向け用語解説
| 用語 | 意味 |
|---|---|
| 引数 | 関数へ渡す値 |

## 注意点・リスク
空入力を確認します。

## 根拠ファイル・行番号
- `src/example.py:1`
{specialist_sections}
"""


def test_validator_accepts_beginner_generic_report(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(valid_report(), encoding="utf-8")
    result = run_validator(report)
    assert result.returncode == 0, result.stderr


def test_validator_rejects_missing_required_section(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(valid_report().replace("## 結論", "## 要約"), encoding="utf-8")
    result = run_validator(report)
    assert result.returncode != 0
    assert "結論" in result.stderr


def test_validator_rejects_unclosed_mermaid_block(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(valid_report().replace("```\n\n## 詳細", "\n\n## 詳細", 1), encoding="utf-8")
    result = run_validator(report)
    assert result.returncode != 0
    assert "Mermaid" in result.stderr


def test_validator_requires_sql_specific_sections(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(valid_report(), encoding="utf-8")
    result = run_validator(report, "sql")
    assert result.returncode != 0
    assert "データ粒度" in result.stderr


def test_validator_accepts_sql_specific_report(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(valid_report("sql"), encoding="utf-8")
    result = run_validator(report, "sql")
    assert result.returncode == 0, result.stderr


def test_validator_accepts_stats_specific_report(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(valid_report("stats"), encoding="utf-8")
    result = run_validator(report, "stats")
    assert result.returncode == 0, result.stderr


def test_bundled_templates_satisfy_contract(tmp_path: Path) -> None:
    del tmp_path
    generic_templates = (
        SKILL_DIR / "assets" / "output-template-beginner.md",
        SKILL_DIR / "assets" / "output-template-full.md",
        SKILL_DIR / "assets" / "output-template-review.md",
        SKILL_DIR / "assets" / "output-template-refactoring.md",
    )
    sql = SKILL_DIR.parent / "stats-sql-comprehension" / "assets" / "output-template-sql.md"
    stats = SKILL_DIR.parent / "stats-sql-comprehension" / "assets" / "output-template-stats.md"
    for generic in generic_templates:
        result = run_validator(generic)
        assert result.returncode == 0, f"{generic}: {result.stderr}"
    sql_result = run_validator(sql, "sql")
    assert sql_result.returncode == 0, sql_result.stderr
    stats_result = run_validator(stats, "stats")
    assert stats_result.returncode == 0, stats_result.stderr
