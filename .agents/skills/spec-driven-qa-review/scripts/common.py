from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def git_revision(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True, stderr=subprocess.DEVNULL
        ).strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "review"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def parse_simple_frontmatter(text: str) -> dict[str, str]:
    """Parse only simple top-level YAML scalar fields used by validator.

    This intentionally avoids a PyYAML runtime dependency. It is not a general YAML parser.
    """
    if not text.startswith("---\n"):
        return {}
    try:
        _, block, _ = text.split("---\n", 2)
    except ValueError:
        return {}
    result: dict[str, str] = {}
    for line in block.splitlines():
        if not line or line.startswith(" ") or line.startswith("\t") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        result[key.strip()] = value
    return result


def next_case_number(qa_root: Path) -> int:
    mx = 0
    if qa_root.exists():
        for p in qa_root.iterdir():
            m = re.match(r"QA-(\d+)-", p.name)
            if m:
                mx = max(mx, int(m.group(1)))
    return mx + 1
