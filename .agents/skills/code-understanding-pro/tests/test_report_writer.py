from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
WRITER = SKILL_DIR / "scripts" / "write_report.py"
COLLECTOR = SKILL_DIR / "scripts" / "collect_code_context.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(args[0]), *args[1:]],
        text=True,
        capture_output=True,
        check=False,
    )


def test_write_report_creates_markdown_and_metadata(tmp_path: Path) -> None:
    content = """# コード理解レポート

```mermaid
flowchart TD
    A[入力] --> B[出力]
```

| 項目 | 内容 |
|---|---|
| 入力 | source.py |
"""
    content_path = tmp_path / "content.md"
    content_path.write_text(content, encoding="utf-8")

    result = run_cli(
        WRITER,
        "--mode",
        "full",
        "--target",
        "src/source.py",
        "--content-file",
        str(content_path),
        "--output-root",
        str(tmp_path / "out"),
        "--run-id",
        "demo",
        "--adapter",
        "generic",
        "--audience",
        "beginner",
        "--source",
        str(content_path),
    )

    assert result.returncode == 0, result.stderr
    run_dir = tmp_path / "out" / "source" / "run_demo"
    report = run_dir / "report.md"
    assert report.read_text(encoding="utf-8") == content
    metadata = json.loads((run_dir / "run_meta.json").read_text(encoding="utf-8"))
    assert metadata["interface_version"] == "2.0"
    assert metadata["mode"] == "Full"
    assert metadata["adapter"] == "generic"
    assert metadata["audience"] == "beginner"
    assert metadata["target"] == "src/source.py"
    assert metadata["report_file"] == "report.md"
    sources = json.loads((run_dir / "source_manifest.json").read_text(encoding="utf-8"))
    assert sources["sources"][0]["path"] == str(content_path)
    assert sources["sources"][0]["exists"] is True
    assert len(sources["sources"][0]["sha256"]) == 64


def test_write_report_rejects_existing_run_without_overwriting(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    content_path.write_text("# first\n", encoding="utf-8")
    args = (
        WRITER,
        "--mode",
        "review",
        "--target",
        "src/source.py",
        "--content-file",
        str(content_path),
        "--output-root",
        str(tmp_path / "out"),
        "--run-id",
        "same",
    )
    first = run_cli(*args)
    second = run_cli(*args)

    assert first.returncode == 0, first.stderr
    assert second.returncode != 0
    assert "既に存在" in second.stderr
    assert (tmp_path / "out" / "source" / "run_same" / "report.md").read_text(encoding="utf-8") == "# first\n"


def test_write_report_redacts_common_secrets(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    content_path.write_text(
        "api_key=sk-test-example password: hunter2\nAuthorization: Bearer abc.def.ghi\n",
        encoding="utf-8",
    )

    result = run_cli(
        WRITER,
        "--mode",
        "documentation",
        "--target",
        "src/source.py",
        "--content-file",
        str(content_path),
        "--output-root",
        str(tmp_path / "out"),
        "--run-id",
        "secret",
    )

    assert result.returncode == 0, result.stderr
    saved = (tmp_path / "out" / "source" / "run_secret" / "report.md").read_text(encoding="utf-8")
    assert "hunter2" not in saved
    assert "abc.def.ghi" not in saved
    assert "[REDACTED]" in saved


def test_write_report_rejects_quick_mode(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    content_path.write_text("# quick\n", encoding="utf-8")
    result = run_cli(
        WRITER,
        "--mode",
        "quick",
        "--target",
        "src/source.py",
        "--content-file",
        str(content_path),
        "--output-root",
        str(tmp_path / "out"),
        "--run-id",
        "quick",
    )

    assert result.returncode != 0
    assert "Quick Mode" in result.stderr


def test_write_report_records_missing_source_without_failing(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    content_path.write_text("# report\n", encoding="utf-8")
    missing = tmp_path / "missing.py"
    result = run_cli(
        WRITER,
        "--mode",
        "full",
        "--target",
        "src/source.py",
        "--content-file",
        str(content_path),
        "--output-root",
        str(tmp_path / "out"),
        "--run-id",
        "missing",
        "--source",
        str(missing),
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads(
        (tmp_path / "out" / "source" / "run_missing" / "source_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["sources"] == [{"path": str(missing), "exists": False}]


def test_collect_context_can_write_a_run_isolated_markdown(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    source.write_text("print('hello')\n", encoding="utf-8")
    result = run_cli(
        COLLECTOR,
        str(source),
        "--output-root",
        str(tmp_path / "out"),
        "--run-id",
        "context",
    )

    assert result.returncode == 0, result.stderr
    saved = tmp_path / "out" / "source" / "run_context" / "code_context.md"
    assert saved.exists()
    assert "print('hello')" in saved.read_text(encoding="utf-8")


def test_collect_context_records_each_included_file_in_context_manifest(tmp_path: Path) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    source = source_dir / "source.py"
    source.write_text("print('hello')\n", encoding="utf-8")

    result = run_cli(
        COLLECTOR,
        str(source_dir),
        "--output-root",
        str(tmp_path / "out"),
        "--run-id",
        "context-manifest",
    )

    assert result.returncode == 0, result.stderr
    run_dir = tmp_path / "out" / "src" / "run_context-manifest"
    assert (run_dir / "code_context.md").exists()
    metadata = json.loads((run_dir / "run_meta.json").read_text(encoding="utf-8"))
    assert metadata["mode"] == "Context"
    manifest = json.loads((run_dir / "source_manifest.json").read_text(encoding="utf-8"))
    entry = next(item for item in manifest["sources"] if item["path"] == str(source.resolve()))
    assert entry["exists"] is True
    assert entry["size_bytes"] == source.stat().st_size
    assert len(entry["sha256"]) == 64


def test_context_artifact_contract_is_documented_as_validator_incompatible() -> None:
    interface = (SKILL_DIR / "references" / "interface.md").read_text(encoding="utf-8")
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    for document in (interface, skill):
        assert "code_context.md" in document
        assert "Context" in document
        assert "検証CLIの対象外" in document
