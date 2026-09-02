#!/usr/bin/env python3
"""code-understanding-proのMarkdown成果物を検証する。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


COMMON_SECTIONS = (
    "結論",
    "対象と前提",
    "全体像",
    "処理フロー",
    "詳細",
    "初学者向け用語解説",
    "注意点・リスク",
    "根拠ファイル・行番号",
)
SQL_SECTIONS = (
    "データ粒度",
    "テーブル・CTE一覧",
    "JOINと行数変化",
    "検証SQL",
)
STATS_SECTIONS = (
    "対象母集団",
    "欠測・除外",
    "推定量・前提",
    "バイアスと妥当性",
    "再現・検証コード",
)


def headings(markdown: str) -> set[str]:
    return {
        match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+?)\s*$", markdown, re.MULTILINE)
    }


def mermaid_blocks_are_balanced(markdown: str) -> bool:
    in_mermaid = False
    found = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if not in_mermaid and stripped == "```mermaid":
            in_mermaid = True
            found = True
        elif in_mermaid and stripped == "```":
            in_mermaid = False
    return found and not in_mermaid


def textual_flow_is_present(markdown: str) -> bool:
    match = re.search(
        r"^##\s+処理フロー\s*$([\s\S]*?)(?=^##\s+|\Z)",
        markdown,
        re.MULTILINE,
    )
    if not match:
        return False
    if "```mermaid" in match.group(1):
        return False
    body = re.sub(r"```mermaid[\s\S]*?```", "", match.group(1), flags=re.MULTILINE)
    return bool(body.strip())


def diagram_or_textual_flow_is_valid(markdown: str, complexity: str) -> bool:
    if mermaid_blocks_are_balanced(markdown):
        return True
    return complexity == "simple" and textual_flow_is_present(markdown)


def validate_report(markdown: str, adapter: str, complexity: str = "simple") -> list[str]:
    errors: list[str] = []
    if not re.search(r"^#\s+\S", markdown, re.MULTILINE):
        errors.append("H1タイトルがありません")
    present = headings(markdown)
    for section in COMMON_SECTIONS:
        if section not in present:
            errors.append(f"必須節がありません: {section}")
    if adapter == "sql":
        for section in SQL_SECTIONS:
            if section not in present:
                errors.append(f"SQL必須節がありません: {section}")
    if adapter == "stats":
        for section in STATS_SECTIONS:
            if section not in present:
                errors.append(f"統計必須節がありません: {section}")
    if not diagram_or_textual_flow_is_valid(markdown, complexity):
        if complexity == "complex":
            errors.append("複雑なレポートには閉じたMermaidコードブロックが必要です")
        else:
            errors.append("処理フローにMermaidまたは説明テキストが必要です")
    evidence_match = re.search(
        r"^##\s+根拠ファイル・行番号\s*$([\s\S]*?)(?=^##\s+|\Z)",
        markdown,
        re.MULTILINE,
    )
    if evidence_match and not re.search(r"`[^`\n]+:\d+`", evidence_match.group(1)):
        errors.append("根拠ファイル・行番号に `path:line` 形式の参照がありません")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="コード理解Markdownレポートを検証します")
    parser.add_argument("report", type=Path)
    parser.add_argument("--adapter", choices=("generic", "sql", "stats"), default="generic")
    parser.add_argument(
        "--complexity",
        choices=("simple", "complex"),
        default="simple",
        help="処理フローの複雑度。complexではMermaidを必須にします",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        markdown = args.report.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1
    errors = validate_report(markdown, args.adapter, args.complexity)
    if errors:
        for error in errors:
            print(f"エラー: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
