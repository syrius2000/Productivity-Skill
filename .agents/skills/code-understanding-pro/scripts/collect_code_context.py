#!/usr/bin/env python3
"""
collect_code_context.py

コード理解用に、対象ディレクトリからテキストファイルを収集し、
AIに渡しやすいMarkdownコンテキストを生成する補助スクリプト。

注意:
- ネットワークアクセスは行わない。
- バイナリファイルは除外する。
- 機密情報を含む可能性があるため、出力前に内容を確認すること。

使用例:
    python scripts/collect_code_context.py . --max-bytes 200000 > context.md
    python scripts/collect_code_context.py src tests README.md --ext .py .md > context.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

DEFAULT_EXCLUDES = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".venv", "venv", "node_modules", "dist", "build", ".idea", ".vscode",
    "target", ".ruff_cache", ".quarto", "renv", "packrat"
}

DEFAULT_EXTS = {
    ".py", ".r", ".R", ".sql", ".sh", ".bash", ".zsh",
    ".md", ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg",
    ".txt", ".qmd", ".Rmd", ".cpp", ".hpp", ".c", ".h",
    ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs"
}


def is_probably_binary(path: Path, sample_size: int = 4096) -> bool:
    try:
        data = path.read_bytes()[:sample_size]
    except OSError:
        return True
    return b"\0" in data


def should_skip(path: Path, excludes: set[str]) -> bool:
    return any(part in excludes for part in path.parts)


def iter_files(paths: Iterable[Path], exts: set[str], excludes: set[str]) -> Iterable[Path]:
    for p in paths:
        if not p.exists():
            print(f"警告: 存在しないパスをスキップします: {p}", file=sys.stderr)
            continue
        if p.is_file():
            if p.suffix in exts and not is_probably_binary(p):
                yield p
            continue
        for child in sorted(p.rglob("*")):
            if should_skip(child, excludes):
                continue
            if child.is_file() and child.suffix in exts and not is_probably_binary(child):
                yield child


def read_text_safely(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp932", "shift_jis", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except OSError as e:
            return f"読み込みエラー: {e}"
    return "読み込みエラー: 対応できない文字コード"


def fenced_language(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".py": "python",
        ".r": "r",
        ".sql": "sql",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".md": "markdown",
        ".qmd": "markdown",
        ".rmd": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".toml": "toml",
        ".cpp": "cpp",
        ".hpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".jsx": "jsx",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
    }.get(suffix, "text")


def main() -> int:
    parser = argparse.ArgumentParser(description="コード理解用Markdownコンテキストを生成します。")
    parser.add_argument("paths", nargs="+", help="対象ファイルまたはディレクトリ")
    parser.add_argument("--ext", nargs="*", default=None, help="対象拡張子。例: --ext .py .md")
    parser.add_argument("--exclude", nargs="*", default=None, help="除外ディレクトリ名")
    parser.add_argument("--max-bytes", type=int, default=300_000, help="総出力サイズ上限")
    args = parser.parse_args()

    exts = set(args.ext) if args.ext else DEFAULT_EXTS
    excludes = DEFAULT_EXCLUDES | set(args.exclude or [])
    targets = [Path(p).resolve() for p in args.paths]

    emitted = 0
    print("# Code Context")
    print()
    print("このファイルはコード理解用に自動収集されたコンテキストです。機密情報が含まれていないか確認してください。")
    print()

    for path in iter_files(targets, exts, excludes):
        text = read_text_safely(path)
        block = f"\n## `{path}`\n\n```{fenced_language(path)}\n{text}\n```\n"
        b = block.encode("utf-8", errors="replace")
        if emitted + len(b) > args.max_bytes:
            print("\n<!-- 出力上限に達したため、以降のファイルは省略しました。 -->")
            break
        print(block)
        emitted += len(b)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
