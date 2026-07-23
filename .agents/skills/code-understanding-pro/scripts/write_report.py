#!/usr/bin/env python3
"""コード理解レポートをrun単位のMarkdown成果物として保存する。"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
import platform
import re
import shutil
import secrets
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SKILL_DIR = Path(__file__).resolve().parents[1]
REPORT_FILENAMES = {
    "full": "report.md",
    "review": "report.md",
    "documentation": "report.md",
    "refactoring": "report.md",
    "context": "code_context.md",
}
DISPLAY_MODES = {
    "full": "Full",
    "review": "Review",
    "documentation": "Documentation",
    "refactoring": "Refactoring",
    "context": "Context",
}
INTERFACE_VERSION = "2.0"


def redact_secrets(text: str) -> str:
    """一般的なキー、パスワード、トークンをMarkdown保存前に伏せ字にする。"""
    secret_key = r"(?:api[_-]?key|password|passwd|secret|token)"
    assignment_prefix = rf"(?<![\w-])(?:export\s+)?[\"']?{secret_key}[\"']?\s*[:=]\s*"

    def replace_quoted(match: re.Match[str]) -> str:
        return f"{match.group('prefix')}{match.group('quote')}[REDACTED]{match.group('quote')}"

    def replace_unclosed_backtick(match: re.Match[str]) -> str:
        return f"{match.group('prefix')}{match.group('quote')}[REDACTED]"

    text = re.sub(
        rf'(?P<prefix>{assignment_prefix})(?P<quote>")(?P<value>(?:\\.|[^"\\\r\n])*)(?P=quote)',
        replace_quoted,
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    text = re.sub(
        rf"(?P<prefix>{assignment_prefix})(?P<quote>')(?P<value>(?:\\.|''|[^'\\\r\n])*)(?P=quote)",
        replace_quoted,
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    text = re.sub(
        rf"(?P<prefix>{assignment_prefix})(?P<quote>\x60)(?P<value>(?:\\.|[^\x60\\\r\n])*)(?P=quote)",
        replace_quoted,
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    text = re.sub(
        rf"(?P<prefix>{assignment_prefix})(?P<quote>\x60)(?P<value>(?:\\.|[^\x60\\\r\n])*)$",
        replace_unclosed_backtick,
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    text = re.sub(
        rf"(?P<prefix>{assignment_prefix})(?![\"'\x60])(?P<value>[^\s,}}\]\x60;|&()<>]+)",
        r"\g<prefix>[REDACTED]",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    text = re.sub(r"(?i)(\bBearer\s+)[^\s`]+", r"\1[REDACTED]", text)
    text = re.sub(
        r"-----BEGIN [^-]+ PRIVATE KEY-----.*?-----END [^-]+ PRIVATE KEY-----",
        "[REDACTED PRIVATE KEY]",
        text,
        flags=re.DOTALL,
    )
    return text


def slugify_target(target: str) -> str:
    path = Path(target)
    name = path.stem if path.suffix else path.name
    name = name or "target"
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")
    return name or "target"


def default_run_id() -> str:
    return datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d_%H%M%S")


def validate_run_id(run_id: str) -> str:
    """run IDを単一の安全なパス要素に限定する。"""
    if (
        not run_id
        or Path(run_id).is_absolute()
        or ".." in run_id
        or "/" in run_id
        or "\\" in run_id
    ):
        raise ValueError("--run-id は絶対パス、..、/、\\ を含まない安全な単一要素にしてください")
    return run_id


def run_directory(output_root: Path, target: str, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    run_name = run_id if run_id.startswith("run_") else f"run_{run_id}"
    return output_root / slugify_target(target) / run_name


def directory_open_flags() -> int:
    """symlinkを辿らずディレクトリfdを開くためのフラグを返す。"""
    directory = getattr(os, "O_DIRECTORY", None)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if directory is None or nofollow is None:
        raise OSError(errno.ENOTSUP, "安全なrun出力に必要なdirectory fd機能を利用できません")
    return os.O_RDONLY | directory | nofollow


def open_child_directory(parent_fd: int, name: str, *, create: bool) -> int:
    """親fdの直下を必要に応じて作成し、symlinkを辿らず開く。"""
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        raise ValueError(f"安全でないディレクトリ名です: {name!r}")
    if create:
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
    try:
        return os.open(name, directory_open_flags(), dir_fd=parent_fd)
    except OSError as error:
        if error.errno in (errno.ELOOP, errno.ENOTDIR):
            raise ValueError("出力先にsymlinkを含めることはできません") from error
        raise


def open_directory_path(path: Path, *, create: bool) -> int:
    """絶対/相対パスをcomponentごとにfdで辿り、祖先symlinkを拒否する。"""
    directory_path = Path(path)
    if directory_path.is_absolute():
        current_fd = os.open("/", directory_open_flags())
        components = directory_path.parts[1:]
    else:
        current_fd = os.open(".", directory_open_flags())
        components = directory_path.parts
    try:
        for component in components:
            if component in ("", "."):
                continue
            if component == "..":
                raise ValueError("ディレクトリパスに .. は使用できません")
            next_fd = open_child_directory(current_fd, component, create=create)
            os.close(current_fd)
            current_fd = next_fd
    except BaseException:
        os.close(current_fd)
        raise
    return current_fd


def fsync_directory(directory_fd: int) -> None:
    """対応するファイルシステムでは親ディレクトリのentry更新も同期する。"""
    try:
        os.fsync(directory_fd)
    except OSError as error:
        if error.errno not in (errno.EINVAL, errno.ENOTSUP, errno.EOPNOTSUPP):
            raise


def create_staging_directory(parent_fd: int, run_name: str) -> str:
    """固定済みの親fd配下に、衝突しないstagingディレクトリを作成する。"""
    for _ in range(100):
        staging_name = f".{run_name}.tmp-{secrets.token_hex(16)}"
        try:
            os.mkdir(staging_name, mode=0o700, dir_fd=parent_fd)
        except FileExistsError:
            continue
        return staging_name
    raise FileExistsError("stagingディレクトリ名を安全に確保できません")


def write_text_to_fd(fd: int, text: str, *, fsync: bool = False) -> None:
    """開かれたfdへ全量を書き込み、必要時は内容を同期する。"""
    data = text.encode("utf-8")
    offset = 0
    while offset < len(data):
        written = os.write(fd, data[offset:])
        if written <= 0:
            raise OSError(errno.EIO, "成果物を書き込めません")
        offset += written
    if fsync:
        os.fsync(fd)


def write_file_at(directory_fd: int, filename: str, text: str) -> None:
    """固定済みのディレクトリfd配下へ新規ファイルを安全に書き込む。"""
    fd = os.open(
        filename,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=directory_fd,
    )
    try:
        write_text_to_fd(fd, text)
    finally:
        os.close(fd)


def reserve_explicit_output_file(parent_fd: int, final_name: str) -> int:
    """最終名を親fd基準で排他的に予約し、既存entryは一切上書きしない。"""
    try:
        return os.open(
            final_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_fd,
        )
    except FileExistsError as error:
        raise FileExistsError(f"出力ファイルが既に存在します（上書きしません）: {final_name}") from error


def cleanup_explicit_output_file(parent_fd: int, final_name: str) -> None:
    """失敗したexplicit保存の最終名予約を、同じ親fdから除去する。"""
    try:
        os.unlink(final_name, dir_fd=parent_fd)
    except FileNotFoundError:
        pass


def cleanup_staging_directory(parent_fd: int, staging_name: str) -> None:
    """固定済みの親fd配下から失敗したstagingを除去する。"""
    try:
        shutil.rmtree(staging_name, dir_fd=parent_fd)
    except FileNotFoundError:
        pass


def entry_exists(parent_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def publish_staging(parent_fd: int, staging_name: str, final_name: str) -> None:
    """no-replace primitiveだけを使ってstagingを最終run名へ公開する。"""
    system = platform.system()
    source = os.fsencode(staging_name)
    destination = os.fsencode(final_name)
    libc = ctypes.CDLL(None, use_errno=True)

    if system == "Darwin":
        operation = libc.renameatx_np
        operation.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
        operation.restype = ctypes.c_int
        ctypes.set_errno(0)
        result = operation(parent_fd, source, parent_fd, destination, 0x00000004 | 0x00000010)
    elif system == "Linux":
        syscall_numbers = {"x86_64": 316, "aarch64": 276, "arm64": 276}
        syscall_number = syscall_numbers.get(platform.machine().lower())
        if syscall_number is None:
            raise OSError(errno.ENOTSUP, "安全なno-replace renameを利用できません")
        operation = libc.syscall
        operation.restype = ctypes.c_long
        ctypes.set_errno(0)
        result = operation(syscall_number, parent_fd, source, parent_fd, destination, 1)
    else:
        raise OSError(errno.ENOTSUP, "安全なno-replace renameを利用できません")

    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number == errno.EEXIST:
        raise FileExistsError(f"出力先が既に存在します（上書きしません）: {final_name}")
    raise OSError(error_number or errno.EIO, "安全なno-replace renameで成果物を公開できません")


def skill_version() -> str:
    version_file = SKILL_DIR / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


def source_entry(source: str) -> dict[str, object]:
    path = Path(source)
    entry: dict[str, object] = {"path": source, "exists": path.exists()}
    if not path.exists():
        return entry
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        entry.update(
            {
                "kind": "file",
                "size_bytes": path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
        )
    else:
        entry["kind"] = "directory"
    return entry


def write_markdown_report(
    content: str,
    *,
    mode: str,
    target: str,
    output_root: Path,
    run_id: str | None = None,
    adapter: str = "generic",
    audience: str = "beginner",
    sources: list[str] | None = None,
) -> Path:
    mode_key = mode.lower()
    if mode_key == "quick":
        raise ValueError("Quick Modeはチャット回答用のため、Markdown保存の対象外です")
    if mode_key not in REPORT_FILENAMES:
        raise ValueError(f"未対応の出力モードです: {mode}")

    run_dir = run_directory(output_root, target, run_id or default_run_id())
    output_root_fd = open_directory_path(output_root, create=True)
    try:
        target_fd = open_child_directory(output_root_fd, slugify_target(target), create=True)
        try:
            if entry_exists(target_fd, run_dir.name):
                raise FileExistsError(f"出力先が既に存在します（上書きしません）: {run_dir}")

            staging_name = create_staging_directory(target_fd, run_dir.name)
            report_file = REPORT_FILENAMES[mode_key]
            try:
                staging_fd = os.open(staging_name, directory_open_flags(), dir_fd=target_fd)
                try:
                    write_file_at(staging_fd, report_file, redact_secrets(content))
                    metadata = {
                        "interface_version": INTERFACE_VERSION,
                        "skill": "code-understanding-pro",
                        "skill_version": skill_version(),
                        "mode": DISPLAY_MODES[mode_key],
                        "adapter": adapter,
                        "audience": audience,
                        "target": target,
                        "report_file": report_file,
                        "generated_at": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
                    }
                    write_file_at(
                        staging_fd,
                        "run_meta.json",
                        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                    )
                    source_manifest = {
                        "interface_version": INTERFACE_VERSION,
                        "sources": [source_entry(source) for source in sources or []],
                    }
                    write_file_at(
                        staging_fd,
                        "source_manifest.json",
                        json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n",
                    )
                finally:
                    os.close(staging_fd)
                publish_staging(target_fd, staging_name, run_dir.name)
                fsync_directory(target_fd)
            except BaseException:
                cleanup_staging_directory(target_fd, staging_name)
                try:
                    fsync_directory(target_fd)
                except OSError:
                    pass
                raise
        finally:
            os.close(target_fd)
    finally:
        os.close(output_root_fd)
    return run_dir / report_file


def write_explicit_report(content: str, output_path: Path) -> Path:
    """後方互換用に、最終名を排他的に予約して指定ファイルへ保存する。"""
    parent_fd = open_directory_path(output_path.parent, create=True)
    try:
        output_fd = reserve_explicit_output_file(parent_fd, output_path.name)
        try:
            try:
                write_text_to_fd(output_fd, redact_secrets(content), fsync=True)
            finally:
                os.close(output_fd)
            fsync_directory(parent_fd)
        except BaseException:
            cleanup_explicit_output_file(parent_fd, output_path.name)
            try:
                fsync_directory(parent_fd)
            except OSError:
                pass
            raise
    finally:
        os.close(parent_fd)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="コード理解Markdownレポートを保存します")
    parser.add_argument("--mode", choices=("quick", "full", "review", "documentation", "refactoring"), required=True)
    parser.add_argument("--target", required=True, help="解析対象のファイルまたはディレクトリ")
    parser.add_argument("--content-file", type=Path, required=True, help="保存するMarkdown本文")
    parser.add_argument("--output-root", type=Path, default=Path("./skill_out/code_understanding"))
    parser.add_argument("--run-id", help="runディレクトリ名に使うID（未指定時はJST時刻）")
    parser.add_argument("--adapter", choices=("generic", "sql", "stats"), default="generic")
    parser.add_argument("--audience", choices=("beginner", "practitioner", "expert"), default="beginner")
    parser.add_argument("--source", action="append", default=[], help="根拠ソースのパス（複数指定可）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        content = args.content_file.read_text(encoding="utf-8")
        path = write_markdown_report(
            content,
            mode=args.mode,
            target=args.target,
            output_root=args.output_root,
            run_id=args.run_id,
            adapter=args.adapter,
            audience=args.audience,
            sources=args.source,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1
    print(path)
    print(path.parent / "run_meta.json")
    print(path.parent / "source_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
