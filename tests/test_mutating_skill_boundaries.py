from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


def test_artifacts_archiver_requires_inventory_and_explicit_approval() -> None:
    text = (SKILLS / "artifacts-archiver/SKILL.md").read_text(encoding="utf-8")
    assert "読み取り専用" in text
    assert "対象一覧" in text
    assert "明示承認" in text
    assert "復元情報" in text
    assert "再帰削除は行わない" in text


def test_domain_modeling_separates_proposal_from_writes() -> None:
    text = (SKILLS / "domain-modeling/SKILL.md").read_text(encoding="utf-8")
    assert "only after the user approves" in text
    assert "Do not create or edit a file until the user explicitly approves" in text
    assert "Create it only after explicit user approval" in text
