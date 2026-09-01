from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import QualityLoop
from .errors import QualityLoopError


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise QualityLoopError(
            "invalid-cli-arguments",
            message,
            remediation="--helpで引数を確認してください。",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description="人間中心の最小QMS協働ループ")
    parser.add_argument("--case-root", type=Path, default=Path("qms-cases"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-case")
    create.add_argument("--input", required=True)

    for command in ("review", "submit-plan", "review-plan", "submit-response", "verify", "assess-risk", "adjudicate"):
        operation = subparsers.add_parser(command)
        operation.add_argument("--case-id", required=False, default=None)
        operation.add_argument("--input", required=True)

    status = subparsers.add_parser("status")
    status.add_argument("--case-id", required=False, default=None)
    status.add_argument("--resume-format", choices=("markdown",))
    return parser


def read_payload(path_text: str) -> dict:
    try:
        if path_text == "-":
            payload = json.load(sys.stdin)
        else:
            with Path(path_text).open(encoding="utf-8") as handle:
                payload = json.load(handle)
    except FileNotFoundError as exc:
        raise QualityLoopError(
            "input-not-found",
            f"入力ファイルが見つかりません: {path_text}",
            exit_code=3,
            remediation="入力ファイルのパスを確認してください。",
        ) from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise QualityLoopError(
            "input-unreadable",
            "入力JSONを読み取れません。",
            exit_code=3,
            remediation="ファイル権限とJSON構文を確認してください。",
        ) from exc
    if not isinstance(payload, dict):
        raise QualityLoopError("invalid-input", "入力JSONはobjectで指定してください。")
    return payload


def resolve_case_id(loop: QualityLoop, specified_id: str | None) -> str:
    if specified_id:
        return specified_id
    active_cases = loop.store.list_active_cases()
    if len(active_cases) == 1:
        return active_cases[0]
    if len(active_cases) == 0:
        all_cases = loop.store.list_cases()
        if len(all_cases) == 1:
            return all_cases[0]
        if len(all_cases) == 0:
            raise QualityLoopError(
                "no-cases-found",
                "案件が存在しません。まずはcreate-caseを実行してください。",
                exit_code=3,
                remediation="create-case で新しい品質案件を作成してください。",
            )
        raise QualityLoopError(
            "no-active-cases-found",
            f"進行中のアクティブ案件がありません（終了済み案件: {', '.join(all_cases)}）。--case-id を明示してください。",
            exit_code=3,
            remediation="--case-id <case_id> を指定して実行してください。",
        )
    raise QualityLoopError(
        "multiple-active-cases",
        f"複数のアクティブ案件が存在します（{', '.join(active_cases)}）。--case-id を明示してください。",
        exit_code=3,
        remediation="--case-id <case_id> を指定して対象案件を選択してください。",
    )


def run(argv: list[str] | None = None) -> int:
    case_id: str | None = None
    try:
        args = build_parser().parse_args(argv)
        loop = QualityLoop(args.case_root)
        if args.command == "create-case":
            result = loop.create_case(read_payload(args.input))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        case_id = resolve_case_id(loop, getattr(args, "case_id", None))
        if args.command == "review":
            result = loop.review(case_id, read_payload(args.input))
        elif args.command == "submit-plan":
            result = loop.submit_plan(case_id, read_payload(args.input))
        elif args.command == "review-plan":
            result = loop.review_plan(case_id, read_payload(args.input))
        elif args.command == "submit-response":
            result = loop.submit_response(case_id, read_payload(args.input))
        elif args.command == "verify":
            result = loop.verify(case_id, read_payload(args.input))
        elif args.command == "assess-risk":
            result = loop.assess_risk(case_id, read_payload(args.input))
        elif args.command == "adjudicate":
            result = loop.adjudicate(case_id, read_payload(args.input))
        else:
            result = loop.status(case_id, resume_format=args.resume_format)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except QualityLoopError as exc:
        print(json.dumps(exc.as_result(case_id), ensure_ascii=False, indent=2))
        return exc.exit_code
    except Exception:
        result = {
            "status": "error",
            "error_code": "internal-error",
            "message": "予期しない内部エラーが発生しました。",
            "remediation": "入力を保存し、実装者へ調査を依頼してください。",
            "case_id": case_id,
            "case_revision": None,
            "state_changed": False,
            "next_role": None,
            "next_action": None,
            "handoff": None,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 4


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
