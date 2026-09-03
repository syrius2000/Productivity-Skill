#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import append_jsonl, now_iso


def main() -> int:
    ap = argparse.ArgumentParser(description="Append an event to a QA case events.jsonl")
    ap.add_argument("case_dir")
    ap.add_argument("--cycle", type=int, required=True)
    ap.add_argument("--actor", required=True)
    ap.add_argument("--role", required=True, choices=["implementer", "reviewer", "adjudicator", "human", "system"])
    ap.add_argument("--action", required=True)
    ap.add_argument("--revision", default=None)
    ap.add_argument("--result", default=None)
    args = ap.parse_args()

    event = {
        "timestamp": now_iso(),
        "cycle": args.cycle,
        "actor": args.actor,
        "role": args.role,
        "action": args.action,
    }
    if args.revision:
        event["revision"] = args.revision
    if args.result:
        event["result"] = args.result
    append_jsonl(Path(args.case_dir) / "events.jsonl", event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
