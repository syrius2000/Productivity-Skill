#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import git_revision, next_case_number, now_iso, slugify


def replace_tokens(text: str, *, case_id: str, title: str, target: str, revision: str, timestamp: str,
                   implementer: str, reviewer: str, profile: str) -> str:
    replacements = {
        "QA-XXXX": case_id,
        "REQUIRED:HUMAN-INPUT:CASE-TITLE": title,
        "REQUIRED:HUMAN-INPUT:TARGET": target,
        "REQUIRED:SYSTEM-REVISION": revision,
        "REQUIRED:SYSTEM-TIMESTAMP": timestamp,
        "REQUIRED:HUMAN-INPUT:IMPLEMENTER-AGENT": implementer,
        "REQUIRED:HUMAN-INPUT:REVIEWER-AGENT": reviewer,
        "qa_profile: standard": f"qa_profile: {profile}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a Spec-Driven QA Review Case")
    ap.add_argument("--root", default=".", help="Repository root")
    ap.add_argument("--title", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--profile", choices=["lite", "standard", "strict"], default="standard")
    ap.add_argument("--implementer", default="ai-1-implementer")
    ap.add_argument("--reviewer", default="ai-2-reviewer")
    args = ap.parse_args()

    repo = Path(args.root).resolve()
    skill_root = Path(__file__).resolve().parents[1]
    qa_root = repo / "docs" / "ADR" / "QA"
    qa_root.mkdir(parents=True, exist_ok=True)

    n = next_case_number(qa_root)
    case_id = f"QA-{n:04d}"
    case_dir = qa_root / f"{case_id}-{slugify(args.title)}"
    if case_dir.exists():
        raise SystemExit(f"Case already exists: {case_dir}")

    (case_dir / "cycles").mkdir(parents=True)
    (case_dir / "evidence").mkdir()
    timestamp = now_iso()
    revision = git_revision(repo)

    mappings = {
        "review-case.md": "review.md",
        "findings.yaml": "findings.yaml",
        "traceability.yaml": "traceability.yaml",
        "events.jsonl": "events.jsonl",
    }
    for src_name, dst_name in mappings.items():
        text = (skill_root / "templates" / src_name).read_text(encoding="utf-8")
        text = replace_tokens(text, case_id=case_id, title=args.title, target=args.target,
                              revision=revision, timestamp=timestamp, implementer=args.implementer,
                              reviewer=args.reviewer, profile=args.profile)
        (case_dir / dst_name).write_text(text, encoding="utf-8")

    (case_dir / "evidence" / "README.md").write_text(
        "# Evidence\n\nStore small reproducible evidence or references here. Do not store secrets.\n",
        encoding="utf-8",
    )
    print(case_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
