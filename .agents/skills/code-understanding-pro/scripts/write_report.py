#!/usr/bin/env python3
"""コード理解レポートをrun単位のMarkdown成果物として保存する。"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import stat
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


def reject_ambiguous_secret_syntax(text: str) -> None:
    """安全に構文を保持できない秘密形式は保存前に拒否する。"""
    secret_key = r"(?:api[_-]?key|password|passwd|secret|token)"
    assignment_prefix = rf"(?<![\w-])(?:export\s+)?[\"']?{secret_key}[\"']?\s*[:=]\s*"
    for match in re.finditer(rf"(?im){assignment_prefix}(?P<value>[^\r\n]*)", text):
        value = match.group("value")
        if value.startswith(("'", '"', "\x60")):
            quote = value[0]
            patterns = {
                '"': r'^"(?:\\.|[^"\\\r\n])*"',
                "'": r"^'(?:\\.|''|[^'\\\r\n])*'",
                "\x60": r"^\x60(?:\\.|[^\x60\\\r\n])*\x60",
            }
            if not re.match(patterns[quote], value):
                raise ValueError("曖昧な秘密形式のため保存を中止しました")
        elif value.startswith(("$'", "$(")) or "$(" in value or "\\" in value:
            raise ValueError("曖昧な秘密形式のため保存を中止しました")


def redact_secrets(text: str) -> str:
    """一般的なキー、パスワード、トークンをMarkdown保存前に伏せ字にする。"""
    reject_ambiguous_secret_syntax(text)
    secret_key = r"(?:api[_-]?key|password|passwd|secret|token)"
    assignment_prefix = rf"(?<![\w-])(?:export\s+)?[\"']?{secret_key}[\"']?\s*[:=]\s*"

    def replace_quoted(match: re.Match[str]) -> str:
        return f"{match.group('prefix')}{match.group('quote')}[REDACTED]{match.group('quote')}"

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


def canonicalize_path(path: Path) -> Path:
    """macOSの /tmp と /var aliasを含め、ユーザー入力パスを先に正規化する。"""
    return Path(path).resolve(strict=False)


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
    return canonicalize_path(output_root) / slugify_target(target) / run_name


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
    directory_path = canonicalize_path(path)
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
        write_text_to_fd(fd, text, fsync=True)
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


def reserve_run_directory(parent_fd: int, final_name: str) -> int:
    """最終run名を親fd基準で予約し、部分的に可視なrunへ直接書き込む。"""
    try:
        os.mkdir(final_name, mode=0o700, dir_fd=parent_fd)
    except FileExistsError as error:
        raise FileExistsError(f"出力先が既に存在します（上書きしません）: {final_name}") from error
    created_stat = os.stat(final_name, dir_fd=parent_fd, follow_symlinks=False)
    try:
        run_fd = os.open(final_name, directory_open_flags(), dir_fd=parent_fd)
    except BaseException:
        if entry_matches_stat(parent_fd, final_name, created_stat):
            os.rmdir(final_name, dir_fd=parent_fd)
        raise
    if os.fstat(run_fd).st_ino != created_stat.st_ino or os.fstat(run_fd).st_dev != created_stat.st_dev:
        os.close(run_fd)
        raise OSError(errno.EAGAIN, "runディレクトリが予約後に差し替えられました")
    return run_fd


def entry_matches_stat(parent_fd: int, name: str, expected: os.stat_result) -> bool:
    """親fd直下の名前が、予約済みfdと同じentryを指す場合だけ真を返す。"""
    try:
        current = os.lstat(name, dir_fd=parent_fd)
    except FileNotFoundError:
        return False
    return current.st_dev == expected.st_dev and current.st_ino == expected.st_ino


def remove_tree_contents_at(directory_fd: int) -> None:
    """Python 3.9でも使えるfd相対の再帰cleanup。symlinkは辿らずunlinkする。"""
    for name in os.listdir(directory_fd):
        entry = os.lstat(name, dir_fd=directory_fd)
        if stat.S_ISDIR(entry.st_mode):
            child_fd = os.open(name, directory_open_flags(), dir_fd=directory_fd)
            try:
                remove_tree_contents_at(child_fd)
            finally:
                os.close(child_fd)
            os.rmdir(name, dir_fd=directory_fd)
        else:
            os.unlink(name, dir_fd=directory_fd)


def cleanup_reserved_run(parent_fd: int, final_name: str, run_fd: int, expected: os.stat_result) -> bool:
    """予約runだけをfd基準で掃除し、同名に差し替わった競合物は残す。"""
    if not entry_matches_stat(parent_fd, final_name, expected):
        return False
    remove_tree_contents_at(run_fd)
    if not entry_matches_stat(parent_fd, final_name, expected):
        return False
    os.rmdir(final_name, dir_fd=parent_fd)
    return True


def cleanup_explicit_output_file(
    parent_fd: int, final_name: str, expected: os.stat_result
) -> bool:
    """予約済みexplicit fileだけを削除し、差し替わった同名entryは残す。"""
    if not entry_matches_stat(parent_fd, final_name, expected):
        return False
    os.unlink(final_name, dir_fd=parent_fd)
    return True


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

    canonical_output_root = canonicalize_path(output_root)
    run_dir = run_directory(canonical_output_root, target, run_id or default_run_id())
    output_root_fd = open_directory_path(canonical_output_root, create=True)
    try:
        target_fd = open_child_directory(output_root_fd, slugify_target(target), create=True)
        try:
            # 最終run名を先に予約して直接書くため、成功前には部分runが一時的に見える。
            run_fd = reserve_run_directory(target_fd, run_dir.name)
            reserved_stat = os.fstat(run_fd)
            report_file = REPORT_FILENAMES[mode_key]
            try:
                write_file_at(run_fd, report_file, redact_secrets(content))
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
                    run_fd,
                    "run_meta.json",
                    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                )
                source_manifest = {
                    "interface_version": INTERFACE_VERSION,
                    "sources": [source_entry(source) for source in sources or []],
                }
                write_file_at(
                    run_fd,
                    "source_manifest.json",
                    json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n",
                )
                fsync_directory(run_fd)
                fsync_directory(target_fd)
            except BaseException:
                cleanup_reserved_run(target_fd, run_dir.name, run_fd, reserved_stat)
                try:
                    fsync_directory(target_fd)
                except OSError:
                    pass
                raise
            finally:
                os.close(run_fd)
        finally:
            os.close(target_fd)
    finally:
        os.close(output_root_fd)
    return run_dir / report_file


def write_explicit_report(content: str, output_path: Path) -> Path:
    """後方互換用に、最終名を排他的に予約して指定ファイルへ保存する。"""
    try:
        original_entry = os.lstat(output_path)
    except FileNotFoundError:
        original_entry = None
    if original_entry is not None and stat.S_ISLNK(original_entry.st_mode):
        raise FileExistsError(f"出力ファイルが既に存在します（上書きしません）: {output_path.name}")
    canonical_output_path = canonicalize_path(output_path)
    parent_fd = open_directory_path(canonical_output_path.parent, create=True)
    try:
        output_fd = reserve_explicit_output_file(parent_fd, canonical_output_path.name)
        reserved_stat = os.fstat(output_fd)
        try:
            try:
                write_text_to_fd(output_fd, redact_secrets(content), fsync=True)
            finally:
                os.close(output_fd)
            fsync_directory(parent_fd)
        except BaseException:
            cleanup_explicit_output_file(parent_fd, canonical_output_path.name, reserved_stat)
            try:
                fsync_directory(parent_fd)
            except OSError:
                pass
            raise
    finally:
        os.close(parent_fd)
    return canonical_output_path


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
