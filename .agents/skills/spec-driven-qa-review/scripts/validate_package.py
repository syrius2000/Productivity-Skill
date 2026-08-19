#!/usr/bin/env python3
"""Validate the canonical files listed by a Skill package MANIFEST.txt."""
from __future__ import annotations

import argparse
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}
SKIP_NAMES = {".DS_Store", "Thumbs.db"}


def manifest_entries(root: Path) -> set[str]:
    manifest = root / "MANIFEST.txt"
    entries = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.add(line)
    return entries


def actual_entries(root: Path) -> set[str]:
    entries = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.name in SKIP_NAMES or path.suffix.lower() == ".pyc":
            continue
        entries.add(relative.as_posix())
    return entries


def compare_package(root: Path) -> tuple[set[str], set[str]]:
    expected = manifest_entries(root)
    actual = actual_entries(root)
    return expected - actual, actual - expected


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Skill package against MANIFEST.txt")
    parser.add_argument("root", nargs="?", default=".", help="Skill package root")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not (root / "MANIFEST.txt").is_file():
        print(f"MANIFEST.txt not found: {root}")
        return 2

    missing, extra = compare_package(root)
    if missing or extra:
        print("Package manifest mismatch")
        for path in sorted(missing):
            print(f"missing: {path}")
        for path in sorted(extra):
            print(f"extra: {path}")
        return 1

    print(f"Package manifest valid: {len(actual_entries(root))} canonical files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
