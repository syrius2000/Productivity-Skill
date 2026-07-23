#!/usr/bin/env python3
"""コード理解レポートをrun単位のMarkdown成果物として保存する。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    text = re.sub(
        r"(?i)(\b(?:api[_-]?key|password|passwd|secret|token)\b\s*[:=]\s*)([^\s`]+)",
        r"\1[REDACTED]",
        text,
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


def run_directory(output_root: Path, target: str, run_id: str) -> Path:
    run_name = run_id if run_id.startswith("run_") else f"run_{run_id}"
    return output_root / slugify_target(target) / run_name


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
    if run_dir.exists():
        raise FileExistsError(f"出力先が既に存在します（上書きしません）: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    report_file = REPORT_FILENAMES[mode_key]
    report_path = run_dir / report_file
    report_path.write_text(redact_secrets(content), encoding="utf-8")
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
    (run_dir / "run_meta.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    source_manifest = {
        "interface_version": INTERFACE_VERSION,
        "sources": [source_entry(source) for source in sources or []],
    }
    (run_dir / "source_manifest.json").write_text(
        json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report_path


def write_explicit_report(content: str, output_path: Path) -> Path:
    """後方互換用に、指定された単一ファイルへ保存する。"""
    if output_path.exists():
        raise FileExistsError(f"出力ファイルが既に存在します（上書きしません）: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(redact_secrets(content), encoding="utf-8")
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
