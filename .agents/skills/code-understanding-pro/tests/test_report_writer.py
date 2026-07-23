from __future__ import annotations

import json
import importlib.util
import os
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


def load_writer_module():
    spec = importlib.util.spec_from_file_location("write_report_under_test", WRITER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_write_report_redacts_json_yaml_quoted_and_environment_secret_values(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    secret_values = ("json-api-key", "yaml-password", "quoted-secret", "environment-token")
    content_path.write_text(
        """{
  "api_key": "json-api-key"
}
password: yaml-password
secret: 'quoted-secret'
export TOKEN="environment-token"
""",
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
        "structured-secrets",
    )

    assert result.returncode == 0, result.stderr
    saved = (tmp_path / "out" / "source" / "run_structured-secrets" / "report.md").read_text(
        encoding="utf-8"
    )
    for secret in secret_values:
        assert secret not in saved
    assert saved.count("[REDACTED]") >= len(secret_values)


def test_write_report_redacts_escaped_quoted_secret_values_without_breaking_syntax(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    json_line = r'{"api_key":"first\"second\\path"}'
    content_path.write_text(
        "\n".join(
            (
                json_line,
                r"secret: 'yaml ''single quote'' \\path'",
                r'export TOKEN="env\"quote\\path"',
            )
        )
        + "\n",
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
        "escaped-secrets",
    )

    assert result.returncode == 0, result.stderr
    saved_lines = (
        tmp_path / "out" / "source" / "run_escaped-secrets" / "report.md"
    ).read_text(encoding="utf-8").splitlines()
    assert json.loads(saved_lines[0]) == {"api_key": "[REDACTED]"}
    assert saved_lines[1] == "secret: '[REDACTED]'"
    assert saved_lines[2] == 'export TOKEN="[REDACTED]"'
    saved = "\n".join(saved_lines)
    for fragment in ("first", "second", "path", "yaml", "single", "quote", "env"):
        assert fragment not in saved


def test_write_explicit_report_redacts_shell_values_without_consuming_delimiters(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_path = tmp_path / "explicit.md"

    writer.write_explicit_report(
        "\n".join(
            (
                "TOKEN=`backtick-secret`; echo ok # backtick comment",
                "TOKEN=plain-secret; echo ok # plain comment",
                "export API_KEY=comment-secret # keep this comment",
            )
        )
        + "\n",
        output_path,
    )

    saved_lines = output_path.read_text(encoding="utf-8").splitlines()
    assert saved_lines == [
        "TOKEN=`[REDACTED]`; echo ok # backtick comment",
        "TOKEN=[REDACTED]; echo ok # plain comment",
        "export API_KEY=[REDACTED] # keep this comment",
    ]
    saved = "\n".join(saved_lines)
    for secret in ("backtick-secret", "plain-secret", "comment-secret"):
        assert secret not in saved


def test_write_report_rejects_unsafe_run_ids(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    content_path.write_text("# report\n", encoding="utf-8")

    for run_id in ("../escape", str(tmp_path / "absolute"), "nested/run", r"nested\\run", "run..escape"):
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
            run_id,
        )

        assert result.returncode != 0
        assert "run-id" in result.stderr


def test_write_report_rejects_resolved_output_outside_target_directory(tmp_path: Path) -> None:
    content_path = tmp_path / "content.md"
    content_path.write_text("# report\n", encoding="utf-8")
    output_root = tmp_path / "out"
    output_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (output_root / "source").symlink_to(outside, target_is_directory=True)

    result = run_cli(
        WRITER,
        "--mode",
        "full",
        "--target",
        "src/source.py",
        "--content-file",
        str(content_path),
        "--output-root",
        str(output_root),
        "--run-id",
        "containment",
    )

    assert result.returncode != 0
    assert "出力先" in result.stderr
    assert not (outside / "run_containment").exists()


def test_write_report_cleans_staging_directory_after_failure_and_allows_retry(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_root = tmp_path / "out"
    original_os_write = os.write

    def fail_metadata_write(fd: int, data: bytes) -> int:
        if b'"skill": "code-understanding-pro"' in data:
            raise OSError("metadata write failed")
        return original_os_write(fd, data)

    from pytest import MonkeyPatch

    failing_patch = MonkeyPatch()
    failing_patch.setattr(os, "write", fail_metadata_write)
    try:
        try:
            writer.write_markdown_report(
                "# report\n",
                mode="full",
                target="src/source.py",
                output_root=output_root,
                run_id="retry",
            )
        except OSError as error:
            assert "metadata write failed" in str(error)
        else:
            raise AssertionError("metadata write failure must propagate")
    finally:
        failing_patch.undo()

    run_dir = output_root / "source" / "run_retry"
    assert not run_dir.exists()
    assert not list((output_root / "source").glob(".run_retry.tmp-*"))

    report_path = writer.write_markdown_report(
        "# report\n",
        mode="full",
        target="src/source.py",
        output_root=output_root,
        run_id="retry",
    )
    assert report_path == run_dir / "report.md"
    assert report_path.read_text(encoding="utf-8") == "# report\n"


def test_write_report_preserves_competing_run_and_cleans_staging_directory(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "publish_staging", None))
    output_root = tmp_path / "out"
    target_dir = output_root / "source"
    target_dir.mkdir(parents=True)
    real_publish = writer.publish_staging

    def publish_after_competitor(parent_fd: int, staging_name: str, final_name: str) -> None:
        os.mkdir(final_name, dir_fd=parent_fd)
        final_fd = os.open(
            final_name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent_fd,
        )
        try:
            report_fd = os.open(
                "report.md",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=final_fd,
            )
            try:
                os.write(report_fd, b"incumbent\n")
            finally:
                os.close(report_fd)
        finally:
            os.close(final_fd)
        real_publish(parent_fd, staging_name, final_name)

    from pytest import MonkeyPatch

    collision_patch = MonkeyPatch()
    collision_patch.setattr(writer, "publish_staging", publish_after_competitor)
    try:
        try:
            writer.write_markdown_report(
                "# candidate\n",
                mode="full",
                target="src/source.py",
                output_root=output_root,
                run_id="collision",
            )
        except FileExistsError:
            pass
        else:
            raise AssertionError("競合runがある場合はpublishに失敗しなければなりません")
    finally:
        collision_patch.undo()

    run_dir = target_dir / "run_collision"
    assert (run_dir / "report.md").read_text(encoding="utf-8") == "incumbent\n"
    assert not list(target_dir.glob(".run_collision.tmp-*"))


def test_write_report_keeps_staging_writes_inside_opened_parent_after_symlink_swap(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "create_staging_directory", None))
    output_root = tmp_path / "out"
    target_dir = output_root / "source"
    target_dir.mkdir(parents=True)
    moved_parent = tmp_path / "moved-source"
    outside = tmp_path / "outside"
    outside.mkdir()
    real_create_staging = writer.create_staging_directory

    def create_staging_then_swap(parent_fd: int, run_name: str) -> str:
        staging_name = real_create_staging(parent_fd, run_name)
        target_dir.rename(moved_parent)
        target_dir.symlink_to(outside, target_is_directory=True)
        return staging_name

    from pytest import MonkeyPatch

    swap_patch = MonkeyPatch()
    swap_patch.setattr(writer, "create_staging_directory", create_staging_then_swap)
    try:
        writer.write_markdown_report(
            "# report\n",
            mode="full",
            target="src/source.py",
            output_root=output_root,
            run_id="symlink-swap",
        )
    finally:
        swap_patch.undo()

    assert not (outside / "run_symlink-swap").exists()
    assert (moved_parent / "run_symlink-swap" / "report.md").read_text(encoding="utf-8") == "# report\n"


def test_write_explicit_report_preserves_competing_file_and_cleans_staging_file(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "create_explicit_staging_file", None))
    output_path = tmp_path / "output" / "explicit.md"
    output_path.parent.mkdir()
    real_create_staging = writer.create_explicit_staging_file

    def create_staging_then_compete(parent_fd: int, final_name: str) -> tuple[str, int]:
        staging_name, staging_fd = real_create_staging(parent_fd, final_name)
        competing_fd = os.open(
            final_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_fd,
        )
        try:
            os.write(competing_fd, b"incumbent\n")
        finally:
            os.close(competing_fd)
        return staging_name, staging_fd

    from pytest import MonkeyPatch

    collision_patch = MonkeyPatch()
    collision_patch.setattr(writer, "create_explicit_staging_file", create_staging_then_compete)
    try:
        try:
            writer.write_explicit_report("# candidate\n", output_path)
        except FileExistsError:
            pass
        else:
            raise AssertionError("競合ファイルがある場合はpublishに失敗しなければなりません")
    finally:
        collision_patch.undo()

    assert output_path.read_text(encoding="utf-8") == "incumbent\n"
    assert not list(output_path.parent.glob(".explicit.md.tmp-*"))


def test_write_explicit_report_keeps_writes_inside_opened_parent_after_symlink_swap(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "create_explicit_staging_file", None))
    parent_dir = tmp_path / "output"
    parent_dir.mkdir()
    output_path = parent_dir / "explicit.md"
    moved_parent = tmp_path / "moved-output"
    outside = tmp_path / "outside"
    outside.mkdir()
    real_create_staging = writer.create_explicit_staging_file

    def create_staging_then_swap(parent_fd: int, final_name: str) -> tuple[str, int]:
        staging_name, staging_fd = real_create_staging(parent_fd, final_name)
        parent_dir.rename(moved_parent)
        parent_dir.symlink_to(outside, target_is_directory=True)
        return staging_name, staging_fd

    from pytest import MonkeyPatch

    swap_patch = MonkeyPatch()
    swap_patch.setattr(writer, "create_explicit_staging_file", create_staging_then_swap)
    try:
        writer.write_explicit_report("# explicit\n", output_path)
    finally:
        swap_patch.undo()

    assert not (outside / "explicit.md").exists()
    assert (moved_parent / "explicit.md").read_text(encoding="utf-8") == "# explicit\n"
    assert not list(moved_parent.glob(".explicit.md.tmp-*"))


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


def test_interface_documents_context_metadata_contract() -> None:
    interface = (SKILL_DIR / "references" / "interface.md").read_text(encoding="utf-8")

    assert "`mode`" in interface
    assert "`Context`" in interface
    assert "`report_file`" in interface
    assert "`code_context.md`" in interface
    assert "mode=Context" in interface
    assert "report_file=code_context.md" in interface
