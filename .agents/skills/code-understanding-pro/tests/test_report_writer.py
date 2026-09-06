from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
import tempfile
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
                "TOKEN=plain-secret; echo ok # plain comment",
                "export API_KEY=comment-secret # keep this comment",
                "TOKEN=secret#suffix",
                "TOKEN=secret # separate comment",
            )
        )
        + "\n",
        output_path,
    )

    saved_lines = output_path.read_text(encoding="utf-8").splitlines()
    assert saved_lines == [
        "TOKEN=[REDACTED]; echo ok # plain comment",
        "export API_KEY=[REDACTED] # keep this comment",
        "TOKEN=[REDACTED]",
        "TOKEN=[REDACTED] # separate comment",
    ]
    saved = "\n".join(saved_lines)
    for secret in ("plain-secret", "comment-secret", "secret", "suffix"):
        assert secret not in saved


def test_write_report_rejects_ambiguous_secret_syntax_before_reserving_run(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_root = tmp_path / "out"
    ambiguous_contents = (
        'TOKEN="unterminated',
        'TOKEN="first\nsecond"',
        "TOKEN=$'ansi-secret'",
        "TOKEN=$(read_secret)",
        r"TOKEN=secret\ value",
    )

    for index, content in enumerate(ambiguous_contents):
        try:
            writer.write_markdown_report(
                content,
                mode="full",
                target="src/source.py",
                output_root=output_root,
                run_id=f"ambiguous-{index}",
            )
        except ValueError as error:
            assert "曖昧" in str(error)
        else:
            raise AssertionError(f"曖昧な秘密形式を拒否しなければなりません: {content!r}")

        assert not (output_root / "source" / f"run_ambiguous-{index}").exists()


def test_path_normalization_rewrites_only_standard_darwin_aliases() -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "lexical_abspath", None))

    expected_tmp = Path("/private/tmp/code-understanding") if sys.platform == "darwin" else Path("/tmp/code-understanding")
    assert writer.lexical_abspath(Path("/tmp/code-understanding")) == expected_tmp
    tempfile_path = Path(tempfile.gettempdir()) / "code-understanding"
    assert writer.lexical_abspath(tempfile_path).is_absolute()


def test_write_report_rejects_arbitrary_output_root_symlink(tmp_path: Path) -> None:
    writer = load_writer_module()
    outside = tmp_path / "outside"
    outside.mkdir()
    output_root = tmp_path / "linked-output"
    output_root.symlink_to(outside, target_is_directory=True)

    try:
        writer.write_markdown_report(
            "# report\n",
            mode="full",
            target="src/source.py",
            output_root=output_root,
            run_id="symlink-root",
        )
    except ValueError as error:
        assert "symlink" in str(error)
    else:
        raise AssertionError("任意の出力root symlinkを拒否しなければなりません")

    assert not (outside / "source" / "run_symlink-root").exists()


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


def test_write_report_keeps_incomplete_marker_after_write_failure_and_rejects_reuse(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "reserve_run_directory", None))
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
    assert (run_dir / ".incomplete").exists()
    assert (run_dir / "report.md").read_text(encoding="utf-8") == "# report\n"

    try:
        writer.write_markdown_report(
            "# report\n",
            mode="full",
            target="src/source.py",
            output_root=output_root,
            run_id="retry",
        )
    except FileExistsError:
        pass
    else:
        raise AssertionError("失敗後に残ったrun-idの再利用を拒否しなければなりません")


def test_write_report_does_not_delete_replaced_competing_run_after_failure(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "reserve_run_directory", None))
    output_root = tmp_path / "out"
    target_dir = output_root / "source"
    target_dir.mkdir(parents=True)
    real_reserve = writer.reserve_run_directory

    def reserve_then_replace(parent_fd: int, final_name: str) -> int:
        run_fd = real_reserve(parent_fd, final_name)
        os.rename(final_name, f"{final_name}.original", src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        os.mkdir(final_name, dir_fd=parent_fd)
        competitor_fd = os.open(
            final_name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent_fd,
        )
        try:
            report_fd = os.open("report.md", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=competitor_fd)
            try:
                os.write(report_fd, b"incumbent\n")
            finally:
                os.close(report_fd)
        finally:
            os.close(competitor_fd)
        return run_fd

    def fail_file_write(directory_fd: int, filename: str, text: str) -> None:
        del directory_fd, filename, text
        raise OSError("write failed")

    from pytest import MonkeyPatch

    collision_patch = MonkeyPatch()
    collision_patch.setattr(writer, "reserve_run_directory", reserve_then_replace)
    collision_patch.setattr(writer, "write_file_at", fail_file_write)
    try:
        try:
            writer.write_markdown_report(
                "# candidate\n",
                mode="full",
                target="src/source.py",
                output_root=output_root,
                run_id="collision",
            )
        except OSError as error:
            assert "write failed" in str(error)
        else:
            raise AssertionError("書込み失敗は呼び出し元へ伝播しなければなりません")
    finally:
        collision_patch.undo()

    run_dir = target_dir / "run_collision"
    assert (run_dir / "report.md").read_text(encoding="utf-8") == "incumbent\n"
    assert (target_dir / "run_collision.original").is_dir()


def test_write_report_keeps_writes_inside_opened_ancestor_after_symlink_swap(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "open_directory_path", None))
    assert callable(getattr(writer, "open_child_directory", None))
    ancestor = tmp_path / "ancestor"
    ancestor.mkdir()
    output_root = ancestor / "out"
    moved_ancestor = tmp_path / "moved-ancestor"
    outside = tmp_path / "outside"
    outside.mkdir()
    real_open_child = writer.open_child_directory
    swapped = False

    def open_child_then_swap(parent_fd: int, name: str, *, create: bool) -> int:
        nonlocal swapped
        if name == "source" and not swapped:
            swapped = True
            ancestor.rename(moved_ancestor)
            ancestor.symlink_to(outside, target_is_directory=True)
        return real_open_child(parent_fd, name, create=create)

    from pytest import MonkeyPatch

    swap_patch = MonkeyPatch()
    swap_patch.setattr(writer, "open_child_directory", open_child_then_swap)
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

    assert not (outside / "out" / "source" / "run_symlink-swap").exists()
    assert (
        moved_ancestor / "out" / "source" / "run_symlink-swap" / "report.md"
    ).read_text(encoding="utf-8") == "# report\n"


def test_write_explicit_report_reserves_final_name_without_hard_link(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "reserve_explicit_output_file", None))
    output_path = tmp_path / "output" / "explicit.md"
    output_path.parent.mkdir()
    real_write = writer.write_text_to_fd

    def observe_reserved_name(fd: int, text: str, *, fsync: bool = False) -> None:
        assert output_path.exists()
        real_write(fd, text, fsync=fsync)

    def reject_hard_link(*args: object, **kwargs: object) -> None:
        raise AssertionError("explicit保存はos.linkを使用してはなりません")

    from pytest import MonkeyPatch

    direct_patch = MonkeyPatch()
    direct_patch.setattr(writer, "write_text_to_fd", observe_reserved_name)
    direct_patch.setattr(os, "link", reject_hard_link)
    try:
        writer.write_explicit_report("# candidate\n", output_path)
    finally:
        direct_patch.undo()

    assert output_path.read_text(encoding="utf-8") == "# candidate\n"


def test_write_explicit_report_rejects_existing_file_directory_and_dangling_symlink(tmp_path: Path) -> None:
    writer = load_writer_module()
    parent_dir = tmp_path / "output"
    parent_dir.mkdir()
    outside = tmp_path / "outside.md"

    existing_file = parent_dir / "file.md"
    existing_file.write_text("incumbent\n", encoding="utf-8")
    existing_directory = parent_dir / "directory.md"
    existing_directory.mkdir()
    dangling_symlink = parent_dir / "link.md"
    dangling_symlink.symlink_to(outside)

    for output_path in (existing_file, existing_directory, dangling_symlink):
        try:
            writer.write_explicit_report("# candidate\n", output_path)
        except FileExistsError:
            pass
        else:
            raise AssertionError(f"既存entryを拒否しなければなりません: {output_path.name}")

    assert existing_file.read_text(encoding="utf-8") == "incumbent\n"
    assert existing_directory.is_dir()
    assert dangling_symlink.is_symlink()
    assert not outside.exists()


def test_write_explicit_report_keeps_partial_file_after_write_failure(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_path = tmp_path / "output" / "explicit.md"
    output_path.parent.mkdir()

    def fail_write(fd: int, text: str, *, fsync: bool = False) -> None:
        del fd, text, fsync
        assert output_path.exists()
        raise OSError("write failed")

    from pytest import MonkeyPatch

    failure_patch = MonkeyPatch()
    failure_patch.setattr(writer, "write_text_to_fd", fail_write)
    try:
        try:
            writer.write_explicit_report("# candidate\n", output_path)
        except OSError as error:
            assert "write failed" in str(error)
        else:
            raise AssertionError("書込み失敗は呼び出し元へ伝播しなければなりません")
    finally:
        failure_patch.undo()

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == ""

    try:
        writer.write_explicit_report("# retry\n", output_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("部分explicit出力と同名の再利用を拒否しなければなりません")


def test_write_explicit_report_keeps_replaced_competitor_during_failure_cleanup(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_path = tmp_path / "output" / "explicit.md"
    output_path.parent.mkdir()
    real_reserve = writer.reserve_explicit_output_file

    def reserve_then_replace(parent_fd: int, final_name: str) -> int:
        output_fd = real_reserve(parent_fd, final_name)
        os.rename(final_name, f"{final_name}.original", src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        competitor_fd = os.open(final_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=parent_fd)
        try:
            os.write(competitor_fd, b"incumbent\n")
        finally:
            os.close(competitor_fd)
        return output_fd

    def fail_write(fd: int, text: str, *, fsync: bool = False) -> None:
        del fd, text, fsync
        raise OSError("write failed")

    from pytest import MonkeyPatch

    replacement_patch = MonkeyPatch()
    replacement_patch.setattr(writer, "reserve_explicit_output_file", reserve_then_replace)
    replacement_patch.setattr(writer, "write_text_to_fd", fail_write)
    try:
        try:
            writer.write_explicit_report("# candidate\n", output_path)
        except OSError as error:
            assert "write failed" in str(error)
        else:
            raise AssertionError("書込み失敗は呼び出し元へ伝播しなければなりません")
    finally:
        replacement_patch.undo()

    assert output_path.read_text(encoding="utf-8") == "incumbent\n"
    assert (output_path.parent / "explicit.md.original").exists()


def test_write_explicit_report_keeps_writes_inside_opened_parent_after_symlink_swap(tmp_path: Path) -> None:
    writer = load_writer_module()
    assert callable(getattr(writer, "reserve_explicit_output_file", None))
    ancestor = tmp_path / "ancestor"
    parent_dir = ancestor / "output"
    parent_dir.mkdir(parents=True)
    output_path = parent_dir / "explicit.md"
    moved_ancestor = tmp_path / "moved-ancestor"
    outside = tmp_path / "outside"
    outside.mkdir()
    real_reserve = writer.reserve_explicit_output_file

    def reserve_then_swap(parent_fd: int, final_name: str) -> int:
        output_fd = real_reserve(parent_fd, final_name)
        ancestor.rename(moved_ancestor)
        ancestor.symlink_to(outside, target_is_directory=True)
        return output_fd

    from pytest import MonkeyPatch

    swap_patch = MonkeyPatch()
    swap_patch.setattr(writer, "reserve_explicit_output_file", reserve_then_swap)
    try:
        writer.write_explicit_report("# explicit\n", output_path)
    finally:
        swap_patch.undo()

    assert not (outside / "output" / "explicit.md").exists()
    assert (moved_ancestor / "output" / "explicit.md").read_text(encoding="utf-8") == "# explicit\n"


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


def test_secret_contract_documents_ambiguous_syntax_abort() -> None:
    interface = (SKILL_DIR / "references" / "interface.md").read_text(encoding="utf-8")
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    for document in (interface, skill):
        assert "曖昧な秘密形式" in document
        assert "保存を中止" in document


def test_write_report_rejects_extended_ambiguous_secret_forms_before_reserving_run(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_root = tmp_path / "out"
    ambiguous_contents = (
        "client_secret: |\n  multiline-secret",
        "client_secret: >\n  folded-secret",
        'TOKEN="first""second"',
        "-----BEGIN PRIVATE KEY-----\nprivate-material",
    )

    for index, content in enumerate(ambiguous_contents):
        try:
            writer.write_markdown_report(
                content,
                mode="full",
                target="src/source.py",
                output_root=output_root,
                run_id=f"extended-ambiguous-{index}",
            )
        except ValueError as error:
            assert "曖昧" in str(error) or "伏字" in str(error)
        else:
            raise AssertionError(f"安全に伏字化できない形式を拒否しなければなりません: {content!r}")

        assert not (output_root / "source" / f"run_extended-ambiguous-{index}").exists()


def test_write_report_prepares_source_hash_before_reserving_run(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_root = tmp_path / "out"

    def fail_source_entry(source: str) -> dict[str, object]:
        del source
        raise OSError("source hash failed")

    from pytest import MonkeyPatch

    hash_patch = MonkeyPatch()
    hash_patch.setattr(writer, "source_entry", fail_source_entry)
    hash_patch.setattr(
        writer,
        "reserve_run_directory",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("runを予約してはなりません")),
    )
    try:
        try:
            writer.write_markdown_report(
                "# report\n",
                mode="full",
                target="src/source.py",
                output_root=output_root,
                run_id="hash-failure",
                sources=["src/source.py"],
            )
        except OSError as error:
            assert "source hash failed" in str(error)
        else:
            raise AssertionError("source hash失敗を呼び出し元へ伝播しなければなりません")
    finally:
        hash_patch.undo()

    assert not (output_root / "source" / "run_hash-failure").exists()


def test_successful_run_removes_incomplete_marker(tmp_path: Path) -> None:
    writer = load_writer_module()
    report_path = writer.write_markdown_report(
        "# report\n",
        mode="full",
        target="src/source.py",
        output_root=tmp_path / "out",
        run_id="complete",
    )

    assert report_path.exists()
    assert not (report_path.parent / ".incomplete").exists()


def test_writer_has_no_automatic_recursive_cleanup_helpers() -> None:
    writer = load_writer_module()

    for name in ("remove_tree_contents_at", "cleanup_reserved_run", "cleanup_explicit_output_file"):
        assert not hasattr(writer, name)


def test_output_contract_documents_incomplete_artifacts_and_trust_boundary() -> None:
    interface = (SKILL_DIR / "references" / "interface.md").read_text(encoding="utf-8")
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    for document in (interface, skill):
        assert ".incomplete" in document
        assert "利用者が削除" in document
        assert "信頼済み非共有ディレクトリ" in document
        assert "同一UID" in document


def test_multiline_assignment_and_backtick_command_substitution_fail_before_output(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_root = tmp_path / "out"

    for index, content in enumerate(
        (
            "TOKEN=\nabc def\n",
            "TOKEN=`command-secret`\n",
            "TOKEN=prefix`command-secret`\n",
            'TOKEN="prefix`command-secret`"\n',
            "Authorization: Bearer abc:def\n",
            "Authorization: Bearer abc`command-secret`\n",
        )
    ):
        try:
            writer.write_markdown_report(
                content,
                mode="full",
                target="src/source.py",
                output_root=output_root,
                run_id=f"multiline-{index}",
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"曖昧な秘密形式を拒否しなければなりません: {content!r}")

        assert not (output_root / "source" / f"run_multiline-{index}").exists()


def test_bearer_redaction_preserves_json_syntax(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_path = tmp_path / "authorization.json"
    writer.write_explicit_report('{"authorization":"Bearer abc.def-123","ok":true}\n', output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == {
        "authorization": "Bearer [REDACTED]",
        "ok": True,
    }


def test_complete_pkcs8_private_key_is_redacted(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_path = tmp_path / "private-key.md"
    writer.write_explicit_report(
        "-----BEGIN PRIVATE KEY-----\nTOPSECRET\n-----END PRIVATE KEY-----\n",
        output_path,
    )

    saved = output_path.read_text(encoding="utf-8")
    assert saved == "[REDACTED PRIVATE KEY]\n"
    assert "TOPSECRET" not in saved


def test_run_keeps_incomplete_marker_when_final_directory_fsync_fails(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_root = tmp_path / "out"
    real_fsync_directory = writer.fsync_directory

    from pytest import MonkeyPatch

    for fail_at in (3, 4):
        calls = 0

        def fail_final_directory_fsync(directory_fd: int) -> None:
            nonlocal calls
            calls += 1
            if calls == fail_at:
                raise OSError("directory fsync failed")
            real_fsync_directory(directory_fd)

        patch = MonkeyPatch()
        patch.setattr(writer, "fsync_directory", fail_final_directory_fsync)
        try:
            try:
                writer.write_markdown_report(
                    "# report\n",
                    mode="full",
                    target="src/source.py",
                    output_root=output_root,
                    run_id=f"fsync-failure-{fail_at}",
                )
            except OSError as error:
                assert "directory fsync failed" in str(error)
            else:
                raise AssertionError("directory fsync失敗を伝播しなければなりません")
        finally:
            patch.undo()

        run_dir = output_root / "source" / f"run_fsync-failure-{fail_at}"
        assert (run_dir / ".incomplete").exists()


def test_explicit_directory_fsync_failure_is_propagated(tmp_path: Path) -> None:
    writer = load_writer_module()
    output_path = tmp_path / "explicit.md"

    from pytest import MonkeyPatch

    patch = MonkeyPatch()
    patch.setattr(
        writer,
        "fsync_directory",
        lambda directory_fd: (_ for _ in ()).throw(OSError("directory fsync failed")),
    )
    try:
        try:
            writer.write_explicit_report("# report\n", output_path)
        except OSError as error:
            assert "directory fsync failed" in str(error)
        else:
            raise AssertionError("directory fsync失敗を伝播しなければなりません")
    finally:
        patch.undo()

    assert output_path.exists()
