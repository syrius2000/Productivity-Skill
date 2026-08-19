from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from detect_unresolved_markers import scan
from common import slugify
from validate_review_case import unresolved_required


def test_slugify():
    assert slugify("Patient Normalization") == "patient-normalization"


def test_detect_required(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text("<!-- REQUIRED:AUTHOR-RESPONSE:QA-1 -->\n", encoding="utf-8")
    hits = scan(tmp_path)
    assert hits and hits[0][0] == p


def test_no_required(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text("review complete\n", encoding="utf-8")
    assert scan(tmp_path) == []


def test_resolved_required_is_not_reported(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text("RESOLVED:REQUIRED:AUTHOR-RESPONSE:QA-1-F1:CYCLE-1\n", encoding="utf-8")
    assert scan(tmp_path) == []
    assert unresolved_required(p.read_text(encoding="utf-8")) is False


def test_unresolved_required_remains_blocking():
    assert unresolved_required("REQUIRED:AUTHOR-RESPONSE:QA-1-F1:CYCLE-1") is True
