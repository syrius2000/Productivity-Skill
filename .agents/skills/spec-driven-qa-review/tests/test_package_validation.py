from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_package import compare_package


def test_manifest_ignores_generated_files(tmp_path: Path):
    (tmp_path / "MANIFEST.txt").write_text("MANIFEST.txt\nSKILL.md\n", encoding="utf-8")
    (tmp_path / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "x.pyc").write_bytes(b"generated")
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache" / "cache").write_text("generated", encoding="utf-8")
    assert compare_package(tmp_path) == (set(), set())


def test_manifest_reports_missing_and_extra_files(tmp_path: Path):
    (tmp_path / "MANIFEST.txt").write_text("MANIFEST.txt\nSKILL.md\nmissing.md\n", encoding="utf-8")
    (tmp_path / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (tmp_path / "extra.md").write_text("extra\n", encoding="utf-8")
    missing, extra = compare_package(tmp_path)
    assert missing == {"missing.md"}
    assert extra == {"extra.md"}
