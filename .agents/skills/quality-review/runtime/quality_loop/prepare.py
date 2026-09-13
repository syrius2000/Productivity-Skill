from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from .errors import QualityLoopError


ALLOWED_FIELDS = {
    "owner",
    "case_id",
    "request",
    "targets",
    "purpose",
    "intended_use",
    "risk_context",
    "requirements",
    "acceptance_criteria",
    "constraints",
    "applicable_obligations",
    "unacceptable_failures",
    "exclusions",
    "answers",
    "target_revision",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(path)


def _read_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise QualityLoopError(
            "input-unreadable",
            f"prepare-caseの入力を読み取れません: {path}",
            exit_code=3,
            remediation="JSON構文、ファイル権限、入力パスを確認してください。",
        ) from exc
    if not isinstance(payload, dict):
        raise QualityLoopError("invalid-input", "prepare-caseの入力JSONはobjectで指定してください。")
    return payload


def _questions(payload: dict) -> list[str]:
    questions: list[str] = []
    if not payload.get("request"):
        questions.append("何を確認・保証したいQAなのか（目的と対象の期待結果）を教えてください。")
    if not payload.get("intended_use"):
        questions.append("誰が、どの環境・運用で使う成果物なのかを教えてください。")
    if not payload.get("risk_context"):
        questions.append("失敗した場合に何が問題になるか、criticalityを含めて教えてください。")
    if not payload.get("requirements"):
        questions.append("満たすべき要求または受入基準を教えてください。")
    if not payload.get("targets"):
        questions.append("レビュー対象のファイルまたはディレクトリ内の相対パスを教えてください。")
    return questions


def _build_draft(payload: dict, existing: dict | None = None) -> dict:
    unknown = sorted(set(payload) - ALLOWED_FIELDS)
    if unknown:
        raise QualityLoopError(
            "forbidden-field",
            "prepare-caseが受け付けない項目です: " + ", ".join(unknown),
            remediation="目的・対象・Quality Intent・回答だけを指定してください。",
        )
    owner = payload.get("owner") or (existing or {}).get("draft_metadata", {}).get("owner")
    if not isinstance(owner, str) or not owner.strip():
        raise QualityLoopError("invalid-input", "prepare-caseにはownerが必要です。")
    targets = payload.get("targets", (existing or {}).get("proposed_case", {}).get("targets", []))
    if not isinstance(targets, list) or any(not isinstance(item, str) or not item.strip() for item in targets):
        raise QualityLoopError("invalid-input", "targetsは空でない文字列の配列で指定してください。")
    request = payload.get("request", (existing or {}).get("conversation", {}).get("request", ""))
    purpose = payload.get("purpose") or request or "指定対象の品質を確認する"
    intended_use = payload.get("intended_use") or {
        "users": "未確認",
        "environment": "未確認",
        "operational_context": "未確認",
    }
    risk_context = payload.get("risk_context") or {
        "criticality": "未確認",
        "safety_impact": "未確認",
        "data_integrity_impact": "未確認",
        "security_context": "未確認",
    }
    if risk_context.get("criticality") == "未確認":
        criticality = "medium"
    else:
        criticality = risk_context.get("criticality")
    if criticality not in {"low", "medium", "high", "regulated"}:
        raise QualityLoopError("invalid-input", "risk_context.criticalityはlow/medium/high/regulatedで指定してください。")
    risk_context = {**risk_context, "criticality": criticality}
    requirements = payload.get("requirements") or [
        {"requirement_id": "PREPARE-SCOPE-001", "text": "指定対象と確認可能なEvidenceを明示する"}
    ]
    acceptance = payload.get("acceptance_criteria") or ["レビュー範囲、確認結果、未確認事項が記録されること"]
    exclusions = list(payload.get("exclusions") or [])
    exclusions.append("AI下書きだけではcase正本、実装許可、Owner裁定を確定しない")
    exclusions = list(dict.fromkeys(exclusions))
    case_id = payload.get("case_id") or (existing or {}).get("proposed_case", {}).get("case_id")
    if not case_id:
        digest = hashlib.sha256(json.dumps({"owner": owner, "targets": targets, "request": request}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        case_id = f"prepared-{digest[:24]}"
    baseline = {
        "purpose": purpose,
        "intended_use": intended_use,
        "risk_context": risk_context,
        "requirements": requirements,
        "acceptance_criteria": acceptance,
        "constraints": payload.get("constraints", []),
        "applicable_obligations": payload.get("applicable_obligations", []),
        "unacceptable_failures": payload.get("unacceptable_failures", []),
        "exclusions": exclusions,
        "targets": targets,
        "target_revision": "prepare-case-unverified",
    }
    now = _now()
    metadata = (existing or {}).get("draft_metadata", {})
    draft_id = metadata.get("draft_id", f"draft-{uuid4()}")
    answers = payload.get("answers", (existing or {}).get("conversation", {}).get("answers", []))
    return {
        "schema_version": "prepare-case/1.0",
        "draft_metadata": {
            "draft_id": draft_id,
            "revision": int(metadata.get("revision", 0)) + 1,
            "status": "needs-human-review" if not payload.get("owner_confirmed") else "confirmed",
            "owner": owner,
            "created_at": metadata.get("created_at", now),
            "updated_at": now,
        },
        "conversation": {
            "request": request,
        "questions": _questions({**payload, "request": request, "targets": targets, "intended_use": intended_use, "risk_context": payload.get("risk_context"), "requirements": payload.get("requirements")} ),
            "answers": answers,
        },
        "proposed_case": {"case_id": case_id, "owner": owner, "baseline": baseline},
        "missing_information": _questions({**payload, "request": request, "targets": targets, "intended_use": payload.get("intended_use"), "risk_context": payload.get("risk_context"), "requirements": payload.get("requirements")} ),
        "owner_confirmation": {
            "confirmed": bool(payload.get("owner_confirmed", False)),
            "confirmed_by": payload.get("confirmed_by"),
            "confirmed_at": payload.get("confirmed_at"),
        },
        "cli_handoff": {"ready": False, "create_case_input": None},
    }


def prepare_case(input_path: Path, output_path: Path, *, confirm: bool = False, create_input_path: Path | None = None) -> dict:
    payload = _read_json(input_path)
    is_draft = payload.get("schema_version") == "prepare-case/1.0"
    if is_draft:
        if not confirm:
            draft = _build_draft({
                "owner": payload.get("draft_metadata", {}).get("owner"),
                "case_id": payload.get("proposed_case", {}).get("case_id"),
                "request": payload.get("conversation", {}).get("request", ""),
                "targets": payload.get("proposed_case", {}).get("baseline", {}).get("targets", []),
                **payload.get("proposed_case", {}).get("baseline", {}),
                "answers": payload.get("conversation", {}).get("answers", []),
            }, payload)
        else:
            draft = payload
    else:
        if confirm:
            raise QualityLoopError("invalid-input", "初回入力から直接confirmせず、下書きファイルを人が確認してください。")
        draft = _build_draft(payload)
    if not confirm:
        _write_json(output_path, draft)
        return {"status": "draft-created", "draft_path": str(output_path), "draft_revision": draft["draft_metadata"]["revision"], "missing_information": draft["missing_information"], "owner_confirmation_required": True}
    confirmation = draft.get("owner_confirmation", {})
    if confirmation.get("confirmed") is not True:
        raise QualityLoopError("owner-confirmation-required", "Owner確認済みの下書きだけをCLI入力へ変換できます。", remediation="下書きのowner_confirmation.confirmedをtrueにし、confirmed_byを記録してください。")
    owner = draft["draft_metadata"]["owner"]
    case_id = draft["proposed_case"]["case_id"]
    now = _now()
    create_payload = {
        "operation_id": f"prepare-case-create-{draft['draft_metadata']['draft_id']}-{draft['draft_metadata']['revision']}",
        "actor_id": owner,
        "role": "owner",
        "invocation_id": f"prepare-case-invocation-{uuid4()}",
        "case_id": case_id,
        "owner": owner,
        "baseline": draft["proposed_case"]["baseline"],
        "implementation_authorization": {"allowed": False, "finding_ids": [], "allowed_targets": []},
        "change_observation": {"method": "prepare-case", "scope": draft["proposed_case"]["baseline"]["targets"], "baseline_evidence_id": None, "exclusions": [], "limitations": ["prepare-caseは下書き作成であり、対象内容の独立確認ではない"]},
    }
    destination = create_input_path or output_path.with_name(output_path.stem + "-create-input.json")
    _write_json(destination, create_payload)
    draft["draft_metadata"]["status"] = "confirmed"
    draft["cli_handoff"] = {"ready": True, "create_case_input": str(destination), "prepared_at": now}
    _write_json(output_path, draft)
    return {"status": "ready-for-create-case", "draft_path": str(output_path), "create_case_input": str(destination), "case_id": case_id, "owner_confirmation": confirmation}
