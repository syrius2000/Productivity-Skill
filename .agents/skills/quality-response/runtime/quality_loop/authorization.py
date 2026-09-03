from __future__ import annotations

from .errors import QualityLoopError


def validate_create_authorization(payload: dict) -> None:
    role = payload.get("role")
    if role != "owner":
        raise QualityLoopError(
            "role-not-allowed",
            "create-caseはOwnerだけが実行できます。",
            remediation="roleをownerにし、OwnerのInvocationから実行してください。",
        )


def validate_operation_role(
    operation: str,
    requested_role: str,
    expected_role: str,
) -> None:
    if requested_role != expected_role:
        raise QualityLoopError(
            "wrong-role",
            f"操作 {operation} に必要なRoleは {expected_role} です（要求Role: {requested_role}）。",
            remediation=f"Roleを {expected_role} に変更して実行してください。",
        )


def validate_status_transition_authorization(
    role: str,
    operation: str,
    target_case_status: str,
) -> None:
    if role == "implementer":
        if target_case_status in {"accepted", "closed", "accepted-with-risk", "rejected"}:
            raise QualityLoopError(
                "self-close-not-allowed",
                "Implementerは案件の受入・クローズ・終端状態変更を行うことはできません。",
                remediation="回答および修正Evidenceを提出し、Reviewerの独立検証へ回してください。",
            )
    elif role == "reviewer":
        if target_case_status in {"accepted", "accepted-with-risk", "rejected", "rework-requested"}:
            raise QualityLoopError(
                "role-not-allowed",
                "Reviewerは案件の最終裁定を行うことはできません。",
                remediation="技術検証（verified / not-verified）を登録し、Owner裁定へ回してください。",
            )


def validate_target_modification_authorization(
    role: str,
    changed_targets: list[str],
    allowed_targets: list[str],
) -> None:
    if not changed_targets:
        return
    if role == "reviewer":
        raise QualityLoopError(
            "artifact-modification-not-allowed",
            "Reviewerは対象成果物を修正することはできません。",
            remediation="Findingを作成し、Implementerへ修正を依頼してください。",
        )
    if role == "implementer":
        allowed_set = set(allowed_targets or [])
        unauthorized = sorted(set(changed_targets) - allowed_set)
        if unauthorized:
            raise QualityLoopError(
                "unauthorized-target-modification",
                f"許可外のファイル変更を検出しました: {', '.join(unauthorized)}",
                remediation="許可範囲（allowed_targets）内のファイルのみを変更してください。",
            )


def validate_authorization(authorization: object) -> dict:
    if not isinstance(authorization, dict):
        raise QualityLoopError(
            "invalid-authorization",
            "implementation_authorizationはobjectで指定してください。",
        )
    required = ("allowed", "finding_ids", "allowed_targets")
    missing = [field for field in required if field not in authorization]
    if missing:
        raise QualityLoopError(
            "invalid-authorization",
            f"実装許可の必須項目が不足しています: {', '.join(missing)}",
        )
    if not isinstance(authorization["allowed"], bool):
        raise QualityLoopError("invalid-authorization", "allowedはbooleanで指定してください。")
    for field in ("finding_ids", "allowed_targets"):
        values = authorization[field]
        if not isinstance(values, list) or any(
            not isinstance(item, str) or not item for item in values
        ):
            raise QualityLoopError(
                "invalid-authorization",
                f"{field}は空文字を含まない文字列配列で指定してください。",
            )
    if not authorization["allowed"] and (
        authorization["finding_ids"] or authorization["allowed_targets"]
    ):
        raise QualityLoopError(
            "invalid-authorization",
            "allowedがfalseの場合は許可対象を空にしてください。",
        )
    return {
        "allowed": authorization["allowed"],
        "finding_ids": list(dict.fromkeys(authorization["finding_ids"])),
        "allowed_targets": list(dict.fromkeys(authorization["allowed_targets"])),
    }


def validate_changed_targets(
    authorization: dict,
    *,
    finding_ids: set[str],
    changed_targets: object,
) -> list[str]:
    if not isinstance(changed_targets, list) or any(
        not isinstance(item, str) or not item for item in changed_targets
    ):
        raise QualityLoopError(
            "invalid-input",
            "changed_targetsは空文字を含まない文字列配列で指定してください。",
        )
    unique_targets = list(dict.fromkeys(changed_targets))
    if not unique_targets:
        return unique_targets
    if not authorization.get("allowed", False):
        raise QualityLoopError(
            "implementation-not-authorized",
            "Ownerによる実装許可がありません。",
            remediation="Ownerへ実装範囲の裁定を依頼してください。",
        )
    allowed_targets = set(authorization.get("allowed_targets", []))
    unauthorized_targets = sorted(set(unique_targets) - allowed_targets)
    if unauthorized_targets:
        raise QualityLoopError(
            "unauthorized-change-detected",
            f"許可外の変更対象です: {', '.join(unauthorized_targets)}",
            remediation="変更を戻すか、Ownerへ許可範囲の裁定を依頼してください。",
        )
    authorized_findings = set(authorization.get("finding_ids", []))
    if authorized_findings and not finding_ids.issubset(authorized_findings):
        unauthorized_findings = sorted(finding_ids - authorized_findings)
        raise QualityLoopError(
            "implementation-not-authorized",
            f"実装許可のないFindingです: {', '.join(unauthorized_findings)}",
        )
    return unique_targets
