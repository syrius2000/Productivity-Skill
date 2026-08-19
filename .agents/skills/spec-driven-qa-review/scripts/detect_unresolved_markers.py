#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

BLOCKING = [
    re.compile(r"REQUIRED:[A-Z0-9_-]+(?:[:][A-Z0-9_-]+)*", re.IGNORECASE),
    re.compile(r"\{\{HUMAN_INPUT", re.IGNORECASE),
]
RESOLVED_REQUIRED = re.compile(r"\bRESOLVED:REQUIRED:", re.IGNORECASE)

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}


def scan(root: Path) -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    if not root.exists():
        return hits
    paths = [root] if root.is_file() else root.rglob("*")
    for path in paths:
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".jsonl"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(lines, 1):
            if RESOLVED_REQUIRED.search(line):
                continue
            if any(p.search(line) for p in BLOCKING):
                hits.append((path, n, line.strip()))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="Fail if unresolved REQUIRED/HUMAN_INPUT markers remain")
    ap.add_argument("path", nargs="?", default="docs/ADR/QA")
    args = ap.parse_args()
    hits = scan(Path(args.path))
    if hits:
        print("Unresolved blocking QA markers:")
        for path, line, text in hits:
            print(f"{path}:{line}: {text}")
        return 1
    print("No unresolved blocking QA markers found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
