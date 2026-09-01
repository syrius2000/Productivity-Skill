from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

from .errors import QualityLoopError


EVIDENCE_LEVELS = {"observed", "reproduced", "derived", "reported", "unverified"}


def validate_evidence(
    case_dir: Path,
    evidence_items: object,
    existing_ids: set[str],
) -> list[dict]:
    if not isinstance(evidence_items, list):
        raise QualityLoopError("invalid-evidence", "evidenceは配列で指定してください。")
    validated: list[dict] = []
    observed_ids = set(existing_ids)
    for item in evidence_items:
        if not isinstance(item, dict):
            raise QualityLoopError("invalid-evidence", "Evidenceはobjectで指定してください。")
        required = ("evidence_id", "level", "target_revision", "method", "result")
        missing = [field for field in required if not item.get(field)]
        if missing:
            raise QualityLoopError(
                "invalid-evidence",
                f"Evidence必須項目が不足しています: {', '.join(missing)}",
            )
        evidence_id = item["evidence_id"]
        if evidence_id in observed_ids:
            raise QualityLoopError(
                "duplicate-evidence-id",
                f"Evidence ID {evidence_id} は既に存在します。",
            )
        if item["level"] not in EVIDENCE_LEVELS:
            raise QualityLoopError("invalid-evidence", "未対応のEvidence水準です。")
        if "path" in item:
            relative_path = Path(item["path"])
            if relative_path.is_absolute():
                raise QualityLoopError("evidence-path-outside-case", "Evidenceは相対パスで指定してください。")
            resolved = (case_dir / relative_path).resolve()
            if not resolved.is_relative_to(case_dir.resolve()):
                raise QualityLoopError(
                    "evidence-path-outside-case",
                    "Evidence参照が案件ディレクトリ外を指しています。",
                )
            if not resolved.is_file():
                raise QualityLoopError(
                    "evidence-not-found",
                    f"Evidenceファイルが見つかりません: {item['path']}",
                    exit_code=3,
                )
            expected_hash = item.get("sha256")
            if not expected_hash:
                raise QualityLoopError("invalid-evidence", "ファイルEvidenceにはsha256が必要です。")
            actual_hash = hashlib.sha256(resolved.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise QualityLoopError(
                    "evidence-digest-mismatch",
                    f"Evidence {evidence_id} のSHA-256が一致しません。",
                    exit_code=3,
                )
        elif not item.get("summary"):
            raise QualityLoopError(
                "invalid-evidence",
                "Evidenceにはpathまたはsummaryが必要です。",
            )
        observed_ids.add(evidence_id)
        validated.append(deepcopy(item))
    return validated
