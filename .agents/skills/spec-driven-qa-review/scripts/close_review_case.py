#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from detect_unresolved_markers import scan
from validate_review_case import validate_case

TERMINAL_RESULTS = {
    "accepted",
    "accepted-with-residual-risk",
    "conditionally-accepted",
    "rejected",
    "blocked-insufficient-evidence",
    "adjudication-required",
}


def main() -> int:
    ap=argparse.ArgumentParser(description="Check whether a QA case is structurally closable")
    ap.add_argument("case_dir")
    ap.add_argument("--result", required=True, choices=sorted(TERMINAL_RESULTS))
    args=ap.parse_args()
    case=Path(args.case_dir)
    errs=validate_case(case)
    markers=scan(case)
    if markers:
        errs.append(f"{len(markers)} unresolved REQUIRED/HUMAN_INPUT marker(s)")
    if errs:
        print("Case is not closable:")
        for e in errs: print(f"- {e}")
        return 1
    review=case/"review.md"
    text=review.read_text(encoding="utf-8")
    text=re.sub(r"(?m)^status:\s*\S+\s*$", "status: closed", text, count=1)
    text=re.sub(r"(?m)^result:\s*.*$", f"result: {args.result}", text, count=1)
    review.write_text(text, encoding="utf-8")
    print(f"Marked {case} closed with result={args.result}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
