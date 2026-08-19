#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def finding_counts(path: Path) -> Counter:
    # Lightweight parser for the predictable template format; no PyYAML dependency.
    c=Counter()
    severity=None
    status=None
    for line in path.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if s.startswith("severity:"):
            severity=s.split(":",1)[1].strip()
        elif s.startswith("status:") and line.startswith("    "):
            status=s.split(":",1)[1].strip()
            if severity and status:
                key=f"{severity}:{'resolved' if status in {'fixed-and-verified','closed','not-applicable','risk-accepted'} else 'open'}"
                c[key]+=1
                severity=status=None
    return c


def latest_event(path: Path):
    if not path.exists(): return None
    rows=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    return rows[-1] if rows else None


def main() -> int:
    ap=argparse.ArgumentParser(description="Print a concise QA pulse from case records")
    ap.add_argument("case_dir")
    args=ap.parse_args()
    case=Path(args.case_dir)
    counts=finding_counts(case/"findings.yaml") if (case/"findings.yaml").exists() else Counter()
    event=latest_event(case/"events.jsonl")
    print(f"Case: {case.name}")
    for sev in ["critical","high","medium","low"]:
        print(f"{sev.title()}: open={counts[f'{sev}:open']} resolved={counts[f'{sev}:resolved']}")
    if event:
        print(f"Latest: {event.get('timestamp')} {event.get('actor')} {event.get('action')} -> {event.get('result','')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
