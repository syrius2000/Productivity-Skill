from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


def _frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"frontmatter start missing: {path}"
    end = text.find("\n---\n", 4)
    assert end >= 0, f"frontmatter end missing: {path}"
    return text[4:end]


def _skill_names() -> set[str]:
    return {path.parent.name for path in SKILLS.glob("*/SKILL.md")}


def test_readme_lists_exactly_all_skill_directories() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    names = _skill_names()
    listed = {name for name in names if f"`{name}`" in readme}

    assert listed == names
    assert re.search(rf"収録スキル一覧 \({len(names)} Skills\)", readme)
    assert re.search(rf"skills/.*\({len(names)} Skills\)", readme)


def test_markdown_links_in_skill_entrypoints_resolve() -> None:
    markdown_link = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    for skill_file in sorted(SKILLS.glob("*/SKILL.md")):
        for raw_target in markdown_link.findall(skill_file.read_text(encoding="utf-8")):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            assert (skill_file.parent / target).is_file(), (
                f"broken local link: {skill_file}: {raw_target}"
            )


def test_declared_package_files_and_versions_are_consistent() -> None:
    for skill_dir in sorted(SKILLS.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue

        frontmatter = _frontmatter(skill_file)
        version_match = re.search(
            r'^version:\s*["\']?([^"\']+)["\']?$', frontmatter, re.MULTILINE
        )
        declared_version = version_match.group(1).strip() if version_match else None

        version_file = skill_dir / "VERSION"
        if version_file.is_file():
            assert declared_version is not None
            assert version_file.read_text(encoding="utf-8").strip() == declared_version

        manifest_file = skill_dir / "manifest.json"
        if not manifest_file.is_file():
            continue

        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        assert manifest["name"] == skill_dir.name
        assert manifest["entrypoint"] == "SKILL.md"
        assert declared_version is not None
        assert manifest["version"] == declared_version
        for relative_path in manifest["files"]:
            assert (skill_dir / relative_path).is_file(), (
                f"manifest references missing file: {skill_dir}: {relative_path}"
            )
