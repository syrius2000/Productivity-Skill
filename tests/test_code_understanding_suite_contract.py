from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


def test_suite_roles_and_output_contract_are_consistent() -> None:
    pro = (SKILLS / "code-understanding-pro/SKILL.md").read_text(encoding="utf-8")
    pyramid = (SKILLS / "code-understanding-pyramid/SKILL.md").read_text(encoding="utf-8")
    specialist = (SKILLS / "stats-sql-comprehension/SKILL.md").read_text(encoding="utf-8")

    assert "親Skill" in pro
    assert "references/interface.md" in pro
    assert "report.md" in pro
    assert "source_manifest.json" in pro
    assert "Do not create an independent output directory." in pyramid
    assert "code-understanding-pro" in specialist
    assert "`sql`" in specialist
    assert "`stats`" in specialist


def test_suite_has_no_legacy_report_filenames() -> None:
    legacy_names = (
        "code_understanding_report.md",
        "code_review_report.md",
        "code_documentation.md",
        "refactoring_proposal.md",
    )
    files = (
        SKILLS / "code-understanding-pro/SKILL.md",
        SKILLS / "code-understanding-pro/README.md",
        SKILLS / "code-understanding-pro/examples/example-prompts.md",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
    for legacy_name in legacy_names:
        assert legacy_name not in combined


def test_suite_manifests_reference_existing_files_and_matching_versions() -> None:
    for skill_name in ("code-understanding-pro", "stats-sql-comprehension"):
        skill_dir = SKILLS / skill_name
        manifest = json.loads((skill_dir / "manifest.json").read_text(encoding="utf-8"))
        missing = [item for item in manifest["files"] if not (skill_dir / item).is_file()]
        assert not missing, f"{skill_name}: {missing}"
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        version_match = re.search(r'^version:\s*["\']?([^"\']+)["\']?$', skill_text, re.MULTILINE)
        assert version_match
        assert manifest["version"] == version_match.group(1)
