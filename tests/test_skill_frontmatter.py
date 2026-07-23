from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
USE_WHEN_SKILLS = {
    "code-understanding-pro",
    "code-understanding-pyramid",
    "stats-sql-comprehension",
    "teach",
    "writing-great-skills",
}


def read_frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"frontmatter start missing: {path}"
    marker = "\n---\n"
    end = text.find(marker, 4)
    assert end >= 0, f"frontmatter end missing: {path}"
    frontmatter = text[4:end]
    assert len(("---\n" + frontmatter + marker).encode("utf-8")) <= 1024
    return frontmatter


def frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    assert match, f"{key} missing"
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def test_all_skill_frontmatter_has_valid_discovery_fields() -> None:
    skill_files = sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    assert skill_files
    for path in skill_files:
        frontmatter = read_frontmatter(path)
        name = frontmatter_value(frontmatter, "name")
        description = frontmatter_value(frontmatter, "description")
        assert name == path.parent.name
        assert re.fullmatch(r"[a-z0-9-]+", name)
        assert description
        if name in USE_WHEN_SKILLS:
            assert description.startswith("Use when")
