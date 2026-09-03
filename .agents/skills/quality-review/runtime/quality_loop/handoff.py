from __future__ import annotations

from uuid import uuid4
from .errors import QualityLoopError


def issue_handoff(
    *,
    case_id: str,
    revision: int | None = None,
    issued_revision: int | None = None,
    next_role: str | None,
    next_action: str | None,
    purpose: str,
    inputs: list[str] | None = None,
    open_items: list[str] | None = None,
    open_issues: list[str] | None = None,
    expected_outputs: list[str] | None = None,
    expected_deliverables: list[str] | None = None,
) -> dict:
    if not case_id:
        raise QualityLoopError("invalid-input", "handoffにはcase_idが必須です。")
    rev = issued_revision if issued_revision is not None else revision or 1
    items = open_issues if open_issues is not None else open_items or []
    outputs = expected_deliverables if expected_deliverables is not None else expected_outputs or []
    return {
        "handoff_id": f"hnd-{uuid4()}",
        "case_id": case_id,
        "issued_revision": rev,
        "next_role": next_role,
        "next_action": next_action,
        "purpose": purpose,
        "inputs": list(inputs or []),
        "open_issues": list(items),
        "open_items": list(items),
        "expected_deliverables": list(outputs),
        "expected_outputs": list(outputs),
        "status": "issued",
    }


def validate_handoff_receipt(
    current_handoff: dict,
    received_handoff_id: str,
    expected_case_revision: int,
    caller_role: str,
) -> None:
    if current_handoff.get("handoff_id") != received_handoff_id:
        raise QualityLoopError(
            "handoff-mismatch",
            f"前handoff IDが一致しません（期待: {current_handoff.get('handoff_id')}, 受信: {received_handoff_id}）。",
            remediation="statusコマンドで最新のhandoff IDを確認してください。",
        )
    if current_handoff.get("issued_revision") != expected_case_revision:
        raise QualityLoopError(
            "revision-conflict",
            f"案件revisionが競合しています（現行: {current_handoff.get('issued_revision')}, 期待: {expected_case_revision}）。",
            remediation="最新の案件正本を確認して再実行してください。",
        )
    if current_handoff.get("next_role") != caller_role:
        raise QualityLoopError(
            "wrong-role",
            f"現在のhandoff対象Roleは {current_handoff.get('next_role')} です（呼出Role: {caller_role}）。",
            remediation=f"Roleを {current_handoff.get('next_role')} に変更してください。",
        )


def terminal_handoff(*, case_id: str, revision: int, result: str) -> dict:
    if not case_id:
        raise QualityLoopError("invalid-input", "terminal handoffにはcase_idが必須です。")
    return {
        "handoff_id": f"hnd-term-{uuid4()}",
        "case_id": case_id,
        "issued_revision": revision,
        "next_role": None,
        "next_action": None,
        "purpose": "Owner裁定により案件を終了する",
        "inputs": ["Reviewer検証", "Owner裁定"],
        "open_issues": [],
        "open_items": [],
        "expected_deliverables": [],
        "expected_outputs": [],
        "status": "terminal",
        "terminal_result": result,
    }
