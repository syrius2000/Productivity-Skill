from __future__ import annotations

from .errors import QualityLoopError


FINDING_REQUIRED_FIELDS = (
    "finding_id",
    "classification",
    "severity",
    "requirement_ref",
    "observed_fact",
    "impact",
    "expected_state",
    "verification_method",
    "evidence_refs",
)

FINDING_CLASSIFICATIONS = {
    "requirement-violation",
    "purpose-risk",
    "evidence-gap",
    "improvement-proposal",
    "regression",
    "unverified-claim",
}

SEVERITIES = {"critical", "high", "medium", "low"}

PLAN_REQUIRED_SEVERITIES = {"critical", "high"}

VERIFICATION_RESULTS = {
    "verified",
    "not-verified",
    "unverified",
    "remediated",
    "not-remediated",
    "partially-remediated",
    "finding-withdrawn",
    "converted-to-suggestion",
    "not-applicable",
}

RESOLVED_VERIFICATION_RESULTS = {
    "verified",
    "remediated",
    "finding-withdrawn",
    "converted-to-suggestion",
    "not-applicable",
}

FINDING_STATUSES = {
    "open",
    "verified",
    "unverified",
    "remediated",
    "not-remediated",
    "partially-remediated",
    "finding-withdrawn",
    "converted-to-suggestion",
    "not-applicable",
    "requires-rereview",
    "held",
}


def derive_plan_required(finding: dict) -> bool:
    """Findingの内容から、Coreが下げられないPlan要否を導出する。"""
    if finding["classification"] == "improvement-proposal":
        return False
    if finding["severity"] in PLAN_REQUIRED_SEVERITIES:
        return True
    if finding["severity"] == "medium":
        return bool(
            finding.get("multi_file_impact")
            or finding.get("destructive")
            or finding.get("security_impact")
            or finding.get("data_integrity_impact")
            or finding.get("ambiguous_requirements")
        )
    return False


def validate_findings(findings: object, existing_ids: set[str]) -> list[dict]:
    if not isinstance(findings, list):
        raise QualityLoopError(
            "invalid-input",
            "findingsは配列で指定してください。",
            remediation="Finding配列または空配列を指定してください。",
        )
    validated: list[dict] = []
    observed_ids = set(existing_ids)
    for finding in findings:
        if not isinstance(finding, dict):
            raise QualityLoopError("invalid-finding", "Findingはobjectで指定してください。")
        missing = [field for field in FINDING_REQUIRED_FIELDS if field not in finding]
        if missing:
            raise QualityLoopError(
                "invalid-finding",
                f"Finding必須項目が不足しています: {', '.join(missing)}",
                remediation="要求、事実、影響、期待状態、検証方法、Evidence参照を補完してください。",
            )
        finding_id = finding["finding_id"]
        if finding_id in observed_ids:
            raise QualityLoopError(
                "duplicate-finding-id",
                f"Finding ID {finding_id} は既に存在します。",
            )
        if finding["classification"] not in FINDING_CLASSIFICATIONS:
            raise QualityLoopError("invalid-finding", "未対応のFinding分類です。")
        if finding["severity"] not in SEVERITIES:
            raise QualityLoopError("invalid-finding", "未対応のSeverityです。")

        # Review/verifyの入力は新規Findingであり、状態を自己申告させない。
        # Plan approvalや実装済み状態は、それぞれCoreの後続操作でのみ付与する。
        finding["status"] = "open"

        # Adaptive Plan Gate policy is canonicalized by Core. A caller cannot
        # lower a mandatory Critical/High (or risk-triggered Medium) gate.
        derived_plan_required = derive_plan_required(finding)
        if finding["classification"] == "improvement-proposal":
            finding["plan_required"] = False
        elif derived_plan_required:
            finding["plan_required"] = True
        elif "plan_required" not in finding:
            finding["plan_required"] = False

        observed_ids.add(finding_id)
        validated.append(finding)
    return validated
