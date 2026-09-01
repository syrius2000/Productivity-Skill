from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from .authorization import validate_authorization, validate_changed_targets
from .case_store import CaseStore
from .errors import QualityLoopError
from .evidence import validate_evidence
from .handoff import issue_handoff, terminal_handoff
from .model import RESOLVED_VERIFICATION_RESULTS, validate_findings
from .transitions import ALLOWED_FIELDS, EXPECTED_ROLE, EXPECTED_STATE


CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class QualityLoop:
    def __init__(self, case_root: Path) -> None:
        self.store = CaseStore(case_root)

    def create_case(self, payload: dict) -> dict:
        self._validate_create(payload)
        case_id = payload["case_id"]
        if self.store.case_path(case_id).is_file():
            current = self.store.load(case_id)
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return duplicate
        now = utc_now()
        handoff = issue_handoff(
            case_id=case_id,
            revision=1,
            next_role="reviewer",
            next_action="review",
            purpose="baselineと対象成果物を独立レビューする",
            inputs=["baseline", "対象成果物", "利用可能なEvidence"],
            open_items=[],
            expected_outputs=["FindingまたはFindingなしの根拠", "次工程handoff"],
        )
        result = self._result(
            case_id=case_id,
            revision=1,
            state_changed=True,
            next_role="reviewer",
            next_action="review",
            handoff=handoff,
        )
        case = {
            "schema_version": "1.0",
            "case_metadata": {
                "case_id": case_id,
                "revision": 1,
                "status": "reviewer-action",
                "owner": payload["owner"],
                "cycle_count": 0,
                "cycle_limit": payload.get("cycle_limit", 3),
                "created_at": now,
                "updated_at": now,
            },
            "baseline": deepcopy(payload["baseline"]),
            "implementation_authorization": validate_authorization(
                payload.get(
                    "implementation_authorization",
                    {"allowed": False, "finding_ids": [], "allowed_targets": []},
                )
            ),
            "change_observation": deepcopy(
                payload.get(
                    "change_observation",
                    {
                        "method": "external",
                        "scope": [],
                        "baseline_evidence_id": None,
                        "exclusions": [],
                        "limitations": ["開始時の変更観測Evidenceが未登録"],
                    },
                )
            ),
            "findings": [],
            "evidence": [],
            "plans": [],
            "plan_reviews": [],
            "responses": [],
            "verifications": [],
            "final_risk_assessments": [],
            "adjudications": [],
            "events": [
                {
                    "operation_id": payload["operation_id"],
                    "actor_id": payload["actor_id"],
                    "role": "owner",
                    "invocation_id": payload["invocation_id"],
                    "operation": "create-case",
                    "revision": 1,
                    "timestamp": now,
                    "result": deepcopy(result),
                }
            ],
            "handoff": handoff,
        }
        self.store.create(case_id, case)
        return result

    def review(self, case_id: str, payload: dict) -> dict:
        def mutation(current: dict) -> tuple[dict | None, dict]:
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return None, duplicate
            self._validate_update(current, payload, "review")
            findings = validate_findings(
                payload.get("findings"),
                {item["finding_id"] for item in current["findings"]},
            )
            evidence = validate_evidence(
                self.store.case_dir(case_id),
                payload.get("evidence", []),
                {item["evidence_id"] for item in current["evidence"]},
            )
            available_evidence_ids = {
                item["evidence_id"] for item in current["evidence"] + evidence
            }
            for finding in findings:
                unknown_refs = set(finding["evidence_refs"]) - available_evidence_ids
                if unknown_refs:
                    raise QualityLoopError(
                        "unknown-evidence-id",
                        f"未知のEvidence IDです: {', '.join(sorted(unknown_refs))}",
                    )
            updated = deepcopy(current)
            updated["findings"].extend(deepcopy(findings))
            updated["evidence"].extend(evidence)
            revision = current["case_metadata"]["revision"] + 1
            blocking_findings = [
                item
                for item in findings
                if item["classification"] != "improvement-proposal"
            ]
            if blocking_findings:
                plan_needed = any(item.get("plan_required", False) for item in blocking_findings)
                if plan_needed:
                    next_role = "implementer"
                    next_action = "submit-plan"
                    state = "implementer-plan"
                    purpose = "重要Findingへの修正方針・反証計画(Response Plan)を提出する"
                    expected_outputs = ["Response Plan", "次工程handoff"]
                else:
                    next_role = "implementer"
                    next_action = "submit-response"
                    state = "implementer-action"
                    purpose = "Findingごとに回答し、許可範囲だけを修正する"
                    expected_outputs = ["Finding別回答", "変更Evidence", "次工程handoff"]
                open_items = [item["finding_id"] for item in blocking_findings]
            else:
                next_role = "owner"
                next_action = "adjudicate"
                state = "owner-adjudication"
                purpose = "Findingなしのレビュー結果を裁定する"
                open_items = []
                expected_outputs = ["Owner裁定"]
            handoff = issue_handoff(
                case_id=case_id,
                revision=revision,
                next_role=next_role,
                next_action=next_action,
                purpose=purpose,
                inputs=["baseline", "review結果", "Evidence"],
                open_items=open_items,
                expected_outputs=expected_outputs,
            )
            result = self._result(
                case_id=case_id,
                revision=revision,
                state_changed=True,
                next_role=next_role,
                next_action=next_action,
                handoff=handoff,
            )
            self._finish_update(
                updated=updated,
                payload=payload,
                operation="review",
                revision=revision,
                state=state,
                handoff=handoff,
                result=result,
            )
            return updated, result

        return self.store.mutate(case_id, mutation)

    def submit_plan(self, case_id: str, payload: dict) -> dict:
        def mutation(current: dict) -> tuple[dict | None, dict]:
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return None, duplicate
            self._validate_update(current, payload, "submit-plan")
            plans = self._validate_plans(current, payload.get("plans"))
            plan_finding_ids = {item["finding_id"] for item in plans}
            evidence = validate_evidence(
                self.store.case_dir(case_id),
                payload.get("evidence", []),
                {item["evidence_id"] for item in current["evidence"]},
            )
            available_evidence_ids = {
                item["evidence_id"] for item in current["evidence"] + evidence
            }
            for plan in plans:
                unknown_refs = set(plan.get("evidence_refs", [])) - available_evidence_ids
                if unknown_refs:
                    raise QualityLoopError(
                        "unknown-evidence-id",
                        f"未知のEvidence IDです: {', '.join(sorted(unknown_refs))}",
                    )
            updated = deepcopy(current)
            revision = current["case_metadata"]["revision"] + 1
            for plan in plans:
                record = deepcopy(plan)
                record["submission_revision"] = revision
                updated["plans"].append(record)
            updated["evidence"].extend(evidence)
            for finding in updated["findings"]:
                if finding["finding_id"] in plan_finding_ids:
                    finding["status"] = "plan-submitted"
            next_role = "reviewer"
            next_action = "review-plan"
            state = "reviewer-plan-review"
            purpose = "Implementerが提出したResponse Planを評価・合意する"
            expected_outputs = ["Plan Review結果", "次工程handoff"]
            handoff = issue_handoff(
                case_id=case_id,
                revision=revision,
                next_role=next_role,
                next_action=next_action,
                purpose=purpose,
                inputs=["Finding", "Response Plan", "Evidence"],
                open_items=sorted(plan_finding_ids),
                expected_outputs=expected_outputs,
            )
            result = self._result(
                case_id=case_id,
                revision=revision,
                state_changed=True,
                next_role=next_role,
                next_action=next_action,
                handoff=handoff,
            )
            self._finish_update(
                updated=updated,
                payload=payload,
                operation="submit-plan",
                revision=revision,
                state=state,
                handoff=handoff,
                result=result,
            )
            return updated, result

        return self.store.mutate(case_id, mutation)

    def review_plan(self, case_id: str, payload: dict) -> dict:
        def mutation(current: dict) -> tuple[dict | None, dict]:
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return None, duplicate
            self._validate_update(current, payload, "review-plan")
            latest_submission_rev = max(
                (item.get("submission_revision", 1) for item in current["plans"]),
                default=1,
            )
            submitted_plans = [
                item
                for item in current["plans"]
                if item.get("submission_revision") == latest_submission_rev
            ]
            plan_reviews = self._validate_plan_reviews(submitted_plans, payload.get("plan_reviews"))
            evidence = validate_evidence(
                self.store.case_dir(case_id),
                payload.get("evidence", []),
                {item["evidence_id"] for item in current["evidence"]},
            )
            available_evidence_ids = {
                item["evidence_id"] for item in current["evidence"] + evidence
            }
            for review in plan_reviews:
                unknown_refs = set(review.get("evidence_refs", [])) - available_evidence_ids
                if unknown_refs:
                    raise QualityLoopError(
                        "unknown-evidence-id",
                        f"未知のEvidence IDです: {', '.join(sorted(unknown_refs))}",
                    )
            updated = deepcopy(current)
            revision = current["case_metadata"]["revision"] + 1
            review_by_id = {item["finding_id"]: item for item in plan_reviews}
            for review in plan_reviews:
                record = deepcopy(review)
                record["review_revision"] = revision
                updated["plan_reviews"].append(record)
            for finding in updated["findings"]:
                review = review_by_id.get(finding["finding_id"])
                if review is not None:
                    outcome = review["outcome"]
                    if outcome in {"finding-withdrawn", "converted-to-suggestion", "not-applicable"}:
                        finding["status"] = outcome
                    elif outcome in {"plan-accepted", "plan-accepted-with-comments"}:
                        finding["status"] = "plan-approved"
                    elif outcome == "plan-revision-required":
                        finding["status"] = "plan-revision-required"
                    elif outcome == "owner-decision-required":
                        finding["status"] = "owner-decision-required"
            updated["evidence"].extend(evidence)

            # Determine next routing. A partial Plan is allowed, but the
            # implementation phase is not opened until every required Finding
            # has its own approved Plan.
            revision_needed = any(
                item["outcome"] == "plan-revision-required" for item in plan_reviews
            )
            owner_needed = any(
                item["outcome"] == "owner-decision-required" for item in plan_reviews
            )
            pending_required = self._pending_required_plan_finding_ids(updated)
            fix_executable = [
                item["finding_id"]
                for item in plan_reviews
                if item["outcome"] in {"plan-accepted", "plan-accepted-with-comments"}
            ]

            from .model import RESOLVED_VERIFICATION_RESULTS
            open_items = [
                item["finding_id"]
                for item in updated["findings"]
                if item.get("status") not in RESOLVED_VERIFICATION_RESULTS
                and item.get("classification") != "improvement-proposal"
            ]

            if owner_needed:
                next_role = "owner"
                next_action = "adjudicate"
                state = "owner-adjudication"
                purpose = "Planレビューでの要判断事項についてOwnerが裁定する"
                expected_outputs = ["Owner裁定"]
            elif revision_needed or pending_required:
                next_role = "implementer"
                next_action = "submit-plan"
                state = "implementer-plan"
                purpose = "未承認のrequired FindingについてResponse Planを提出または再提出する"
                expected_outputs = ["未承認Finding別Response Plan", "次工程handoff"]
            elif fix_executable:
                next_role = "implementer"
                next_action = "submit-response"
                state = "implementer-action"
                purpose = "承認されたPlanおよびOwner許可範囲に基づき修正とEvidenceを提出する"
                expected_outputs = ["Finding別修正提出", "変更Evidence", "次工程handoff"]
            else:
                # All plans resulted in finding-withdrawn, converted-to-suggestion, etc.
                next_role = "owner"
                next_action = "adjudicate"
                state = "owner-adjudication"
                purpose = "全Plan合意・自己訂正完了に伴い最終裁定を行う"
                expected_outputs = ["Owner裁定"]

            handoff = issue_handoff(
                case_id=case_id,
                revision=revision,
                next_role=next_role,
                next_action=next_action,
                purpose=purpose,
                inputs=["Response Plan", "Plan Review結果", "Evidence"],
                open_items=(sorted(pending_required) if next_action == "submit-plan" else open_items),
                expected_outputs=expected_outputs,
            )
            result = self._result(
                case_id=case_id,
                revision=revision,
                state_changed=True,
                next_role=next_role,
                next_action=next_action,
                handoff=handoff,
            )
            self._finish_update(
                updated=updated,
                payload=payload,
                operation="review-plan",
                revision=revision,
                state=state,
                handoff=handoff,
                result=result,
            )
            return updated, result

        return self.store.mutate(case_id, mutation)

    def submit_response(self, case_id: str, payload: dict) -> dict:
        def mutation(current: dict) -> tuple[dict | None, dict]:
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return None, duplicate
            self._validate_update(current, payload, "submit-response")
            responses = self._validate_responses(current, payload.get("responses"))
            response_finding_ids = {item["finding_id"] for item in responses}
            missing_plan_approval = sorted(
                response_finding_ids & self._pending_required_plan_finding_ids(current)
            )
            if missing_plan_approval:
                raise QualityLoopError(
                    "plan-approval-required",
                    "Plan-required Findingは対象Finding自身のPlan承認後にResponseを提出できます: "
                    + ", ".join(missing_plan_approval),
                    remediation="未承認FindingのResponse Planを提出し、ReviewerのPlan承認を取得してください。",
                )
            changed_targets = validate_changed_targets(
                current["implementation_authorization"],
                finding_ids=response_finding_ids,
                changed_targets=payload.get("changed_targets"),
            )
            if any(
                item["disposition"] == "fix-submitted" for item in responses
            ) and not changed_targets:
                raise QualityLoopError(
                    "invalid-response",
                    "fix-submittedにはchanged_targetsが必要です。",
                )
            evidence = validate_evidence(
                self.store.case_dir(case_id),
                payload.get("evidence", []),
                {item["evidence_id"] for item in current["evidence"]},
            )
            available_evidence_ids = {
                item["evidence_id"] for item in current["evidence"] + evidence
            }
            for response in responses:
                unknown_refs = set(response["evidence_refs"]) - available_evidence_ids
                if unknown_refs:
                    raise QualityLoopError(
                        "unknown-evidence-id",
                        f"未知のEvidence IDです: {', '.join(sorted(unknown_refs))}",
                    )
            updated = deepcopy(current)
            revision = current["case_metadata"]["revision"] + 1
            for response in responses:
                record = deepcopy(response)
                record["changed_targets"] = list(changed_targets)
                record["submission_revision"] = revision
                updated["responses"].append(record)
            updated["evidence"].extend(evidence)
            for finding in updated["findings"]:
                if finding["finding_id"] in response_finding_ids:
                    finding["status"] = "response-submitted"
            baseline_change_requested = any(
                item["disposition"] == "baseline-change-requested"
                for item in responses
            )
            if baseline_change_requested:
                next_role = "owner"
                next_action = "adjudicate"
                state = "owner-adjudication"
                purpose = "baseline変更要求をOwnerが裁定する"
                expected_outputs = ["baseline維持・変更・保留のOwner裁定"]
            else:
                next_role = "reviewer"
                next_action = "verify"
                state = "reviewer-verification"
                purpose = "Implementer提出と修正結果を独立検証する"
                expected_outputs = ["Finding別検証", "変更範囲照合", "次工程handoff"]
            handoff = issue_handoff(
                case_id=case_id,
                revision=revision,
                next_role=next_role,
                next_action=next_action,
                purpose=purpose,
                inputs=["Finding", "Implementer回答", "変更Evidence", "変更観測"],
                open_items=sorted(response_finding_ids),
                expected_outputs=expected_outputs,
            )
            result = self._result(
                case_id=case_id,
                revision=revision,
                state_changed=True,
                next_role=next_role,
                next_action=next_action,
                handoff=handoff,
            )
            self._finish_update(
                updated=updated,
                payload=payload,
                operation="submit-response",
                revision=revision,
                state=state,
                handoff=handoff,
                result=result,
            )
            return updated, result

        return self.store.mutate(case_id, mutation)

    def verify(self, case_id: str, payload: dict) -> dict:
        def mutation(current: dict) -> tuple[dict | None, dict]:
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return None, duplicate
            self._validate_update(current, payload, "verify")
            latest_submit_event = next(
                event
                for event in reversed(current["events"])
                if event["operation"] == "submit-response"
            )
            if latest_submit_event["invocation_id"] == payload["invocation_id"]:
                raise QualityLoopError(
                    "verification-not-independent",
                    "verifyは対象submit-responseと異なるInvocationで実行してください。",
                )
            submission_revision = latest_submit_event["revision"]
            submitted_responses = [
                item
                for item in current["responses"]
                if item["submission_revision"] == submission_revision
            ]
            verifications = self._validate_verifications(
                submitted_responses, payload.get("verifications")
            )
            new_findings = validate_findings(
                payload.get("new_findings", []),
                {item["finding_id"] for item in current["findings"]},
            )
            evidence = validate_evidence(
                self.store.case_dir(case_id),
                payload.get("evidence", []),
                {item["evidence_id"] for item in current["evidence"]},
            )
            available_evidence_ids = {
                item["evidence_id"] for item in current["evidence"] + evidence
            }
            for verification in verifications:
                unknown_refs = set(verification["evidence_refs"]) - available_evidence_ids
                if unknown_refs:
                    raise QualityLoopError(
                        "unknown-evidence-id",
                        f"未知のEvidence IDです: {', '.join(sorted(unknown_refs))}",
                    )
            observation = self._validate_change_observation(
                current=current,
                responses=submitted_responses,
                observation=payload.get("change_observation"),
                evidence_ids=available_evidence_ids,
            )
            updated = deepcopy(current)
            revision = current["case_metadata"]["revision"] + 1
            verification_by_id = {
                item["finding_id"]: item for item in verifications
            }
            for verification in verifications:
                record = deepcopy(verification)
                record["verification_revision"] = revision
                record["change_observation"] = deepcopy(observation)
                updated["verifications"].append(record)
            for finding in updated["findings"]:
                verification = verification_by_id.get(finding["finding_id"])
                if verification is not None:
                    finding["status"] = verification["result"]
            updated["findings"].extend(deepcopy(new_findings))
            updated["evidence"].extend(evidence)
            cycle_count = current["case_metadata"].get("cycle_count", 0) + 1
            updated["case_metadata"]["cycle_count"] = cycle_count
            material_unresolved = self._material_unresolved_finding_ids(updated)
            all_resolved = not material_unresolved
            pending_plan_required = self._pending_required_plan_finding_ids(updated)
            cycle_limit = current["case_metadata"].get("cycle_limit", 3)
            early_risk = bool(payload.get("early_risk_assessment"))
            has_unresolved_critical = any(
                f.get("severity") == "critical"
                for f in updated["findings"]
                if f.get("status") not in RESOLVED_VERIFICATION_RESULTS
            )
            if early_risk:
                early_rationale = str(payload.get("early_risk_rationale", "")).strip()
                if not early_rationale:
                    raise QualityLoopError(
                        "invalid-input",
                        "early_risk_assessment を指定する場合は early_risk_rationale (移行理由) が必須です。",
                        remediation="早期リスク評価へ移行する根拠と妥当性を early_risk_rationale に記載してください。",
                    )
                if has_unresolved_critical:
                    raise QualityLoopError(
                        "critical-finding-unresolved",
                        "未解決のCritical指摘が存在するため、早期Final Risk Assessmentへ移行できません。",
                        remediation="Critical指摘を解消するか、Ownerによる明示的指示を受けてください。",
                    )

            if (cycle_count >= cycle_limit or early_risk) and not all_resolved:
                next_role = "reviewer"
                next_action = "assess-risk"
                state = "reviewer-final-assessment"
                reason_note = "サイクル上限到達" if cycle_count >= cycle_limit else "早期リスク移行判定"
                purpose = f"{reason_note}に伴い残余リスク評価(Final Risk Assessment)を実施する"
                expected_outputs = ["Final Risk Assessment", "次工程handoff"]
            elif all_resolved:
                next_role = "owner"
                next_action = "adjudicate"
                state = "owner-adjudication"
                purpose = "独立検証結果と残余リスクを裁定する"
                expected_outputs = ["Owner裁定"]
            elif pending_plan_required:
                next_role = "implementer"
                next_action = "submit-plan"
                state = "implementer-plan"
                purpose = "未承認のPlan-required Findingについて次のResponse Planを提出する"
                expected_outputs = ["未承認Finding別Response Plan", "次工程handoff"]
            else:
                next_role = "implementer"
                next_action = "submit-response"
                state = "implementer-action"
                purpose = "未解決または新規Findingへ回答する"
                expected_outputs = ["Finding別回答", "変更Evidence"]
            open_items = [
                item["finding_id"]
                for item in updated["findings"]
                if item.get("status") not in RESOLVED_VERIFICATION_RESULTS
                and item.get("classification") != "improvement-proposal"
            ]
            if next_action == "submit-plan":
                open_items = sorted(pending_plan_required)
            handoff = issue_handoff(
                case_id=case_id,
                revision=revision,
                next_role=next_role,
                next_action=next_action,
                purpose=purpose,
                inputs=["Finding", "Implementer回答", "Reviewer検証", "Evidence"],
                open_items=open_items,
                expected_outputs=expected_outputs,
            )
            result = self._result(
                case_id=case_id,
                revision=revision,
                state_changed=True,
                next_role=next_role,
                next_action=next_action,
                handoff=handoff,
            )
            self._finish_update(
                updated=updated,
                payload=payload,
                operation="verify",
                revision=revision,
                state=state,
                handoff=handoff,
                result=result,
            )
            return updated, result

        return self.store.mutate(case_id, mutation)

    def assess_risk(self, case_id: str, payload: dict) -> dict:
        def mutation(current: dict) -> tuple[dict | None, dict]:
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return None, duplicate
            self._validate_update(current, payload, "assess-risk")
            overall_rec = payload.get("overall_recommendation")
            allowed_recs = {"accept", "accept-with-conditions", "require-remediation", "defer"}
            if overall_rec not in allowed_recs:
                raise QualityLoopError(
                    "invalid-input",
                    f"overall_recommendationが不正です: {overall_rec}",
                )
            if not payload.get("rationale"):
                raise QualityLoopError(
                    "invalid-input",
                    "assess-riskにはrationaleが必要です。",
                )
            residual_risks = self._validate_residual_risks(current, payload.get("residual_risks", []))

            updated = deepcopy(current)
            revision = current["case_metadata"]["revision"] + 1
            record = {
                "operation_id": payload["operation_id"],
                "actor_id": payload["actor_id"],
                "role": payload["role"],
                "invocation_id": payload["invocation_id"],
                "revision": revision,
                "overall_recommendation": overall_rec,
                "rationale": payload["rationale"],
                "residual_risks": residual_risks,
            }
            updated["final_risk_assessments"].append(record)

            next_role = "owner"
            next_action = "adjudicate"
            state = "owner-adjudication"
            purpose = "ReviewerのFinal Risk Assessmentを評価し、受入・条件・再作業を裁定する"
            expected_outputs = ["Owner裁定"]

            from .model import RESOLVED_VERIFICATION_RESULTS
            open_items = [
                item["finding_id"]
                for item in updated["findings"]
                if item.get("status") not in RESOLVED_VERIFICATION_RESULTS
                and item.get("classification") != "improvement-proposal"
            ]
            handoff = issue_handoff(
                case_id=case_id,
                revision=revision,
                next_role=next_role,
                next_action=next_action,
                purpose=purpose,
                inputs=["Final Risk Assessment", "Finding", "Reviewer検証"],
                open_items=open_items,
                expected_outputs=expected_outputs,
            )
            result = self._result(
                case_id=case_id,
                revision=revision,
                state_changed=True,
                next_role=next_role,
                next_action=next_action,
                handoff=handoff,
            )
            self._finish_update(
                updated=updated,
                payload=payload,
                operation="assess-risk",
                revision=revision,
                state=state,
                handoff=handoff,
                result=result,
            )
            # Generate final-risk-assessment.md as a derived artifact
            from .markdown_report import generate_final_risk_assessment_markdown
            md_text = generate_final_risk_assessment_markdown(updated)
            self.store.atomic_write_text(
                self.store.case_dir(case_id) / "final-risk-assessment.md", md_text
            )
            return updated, result

        return self.store.mutate(case_id, mutation)

    def adjudicate(self, case_id: str, payload: dict) -> dict:
        def mutation(current: dict) -> tuple[dict | None, dict]:
            duplicate = self._duplicate_result(current, payload.get("operation_id"))
            if duplicate is not None:
                return None, duplicate
            self._validate_update(current, payload, "adjudicate")
            decision = payload.get("decision")
            allowed_decisions = {
                "accepted",
                "accepted-with-risk",
                "held",
                "rejected",
                "rework-requested",
            }
            if decision not in allowed_decisions:
                raise QualityLoopError(
                    "invalid-adjudication",
                    "未対応のOwner裁定です。",
                )
            if not payload.get("rationale"):
                raise QualityLoopError(
                    "invalid-adjudication", "Owner裁定にはrationaleが必要です。"
                )
            from .model import RESOLVED_VERIFICATION_RESULTS
            unresolved = [
                item["finding_id"]
                for item in current["findings"]
                if item.get("status") not in RESOLVED_VERIFICATION_RESULTS
                and item.get("classification") != "improvement-proposal"
            ]
            if decision == "accepted" and unresolved:
                raise QualityLoopError(
                    "unresolved-findings",
                    f"未解決Findingがあるため通常受入できません: {', '.join(unresolved)}",
                    remediation="再作業、保留、却下、または残余リスク付き受入を裁定してください。",
                )
            if decision == "accepted-with-risk":
                if not payload.get("residual_risks"):
                    raise QualityLoopError(
                        "residual-risk-required",
                        "リスク付き受入にはresidual_risksが必要です。",
                    )
                if not payload.get("conditions"):
                    raise QualityLoopError(
                        "conditions-required",
                        "リスク付き受入には補償策または再確認トリガーとなるconditionsが必要です。",
                    )
            baseline_update = payload.get("baseline_update")
            if baseline_update is not None:
                if decision != "rework-requested":
                    raise QualityLoopError(
                        "invalid-adjudication",
                        "baseline変更はrework-requestedと組み合わせてください。",
                    )
                self._validate_baseline(baseline_update)
            cycle_count = current["case_metadata"].get("cycle_count", 0)
            cycle_limit = current["case_metadata"].get("cycle_limit", 3)
            additional_cycles = payload.get("additional_cycles")
            if decision == "rework-requested" and cycle_count >= cycle_limit:
                if not isinstance(additional_cycles, int) or isinstance(
                    additional_cycles, bool
                ) or additional_cycles <= 0:
                    raise QualityLoopError(
                        "additional-cycles-required",
                        "3サイクル到達後の再作業にはOwnerによる正の追加サイクル数が必要です。",
                    )
            elif additional_cycles is not None:
                raise QualityLoopError(
                    "invalid-adjudication",
                    "additional_cyclesはサイクル上限到達後のrework-requestedだけで指定できます。",
                )
            authorization_update = payload.get("implementation_authorization")
            if authorization_update is not None:
                authorization_update = validate_authorization(authorization_update)
            dry_run = payload.get("dry_run", False)
            terminal_decisions = {"accepted", "accepted-with-risk", "rejected"}
            if not isinstance(dry_run, bool) or not isinstance(
                payload.get("confirm", False), bool
            ):
                raise QualityLoopError(
                    "invalid-adjudication",
                    "dry_runとconfirmはbooleanで指定してください。",
                )
            if dry_run:
                preview = self._result(
                    case_id=case_id,
                    revision=current["case_metadata"]["revision"],
                    state_changed=False,
                    next_role=current["handoff"]["next_role"],
                    next_action=current["handoff"]["next_action"],
                    handoff=current["handoff"],
                    status="dry-run",
                )
                preview["dry_run"] = True
                preview["preview_decision"] = decision
                preview["unresolved_findings"] = unresolved
                return None, preview
            if decision in terminal_decisions and not payload.get("confirm", False):
                raise QualityLoopError(
                    "confirmation-required",
                    "終端裁定にはconfirm: trueが必要です。",
                    remediation="dry-runの内容を確認後、confirm: trueで再実行してください。",
                )
            updated = deepcopy(current)
            revision = current["case_metadata"]["revision"] + 1
            adjudication = {
                "decision": decision,
                "rationale": payload["rationale"],
                "conditions": deepcopy(payload.get("conditions", [])),
                "residual_risks": deepcopy(payload.get("residual_risks", [])),
                "adjudication_revision": revision,
            }
            updated["adjudications"].append(adjudication)
            if additional_cycles is not None:
                updated["case_metadata"]["cycle_limit"] = cycle_count + additional_cycles
            if authorization_update is not None:
                updated["implementation_authorization"] = authorization_update
            if baseline_update is not None:
                updated["baseline"] = deepcopy(baseline_update)
                for item in updated["findings"]:
                    if item.get("classification") != "improvement-proposal":
                        item["status"] = "requires-rereview"
                next_role = "reviewer"
                next_action = "review"
                state = "reviewer-action"
                handoff = issue_handoff(
                    case_id=case_id,
                    revision=revision,
                    next_role=next_role,
                    next_action=next_action,
                    purpose="Owner変更後のbaselineで対象を再レビューする",
                    inputs=["baseline変更差分", "影響するFinding", "対象成果物"],
                    open_items=unresolved,
                    expected_outputs=["再評価したFinding", "次工程handoff"],
                )
            elif decision == "rework-requested":
                next_role = "implementer"
                pending_plan_required = self._pending_required_plan_finding_ids(updated)
                if pending_plan_required:
                    next_action = "submit-plan"
                    state = "implementer-plan"
                    purpose = "Owner裁定に基づき未承認のPlan-required FindingへResponse Planを提出する"
                    expected_outputs = ["Response Plan"]
                else:
                    next_action = "submit-response"
                    state = "implementer-action"
                    purpose = "Owner裁定に基づき追加改善を提出する"
                    expected_outputs = ["Finding別回答", "変更Evidence"]
                handoff = issue_handoff(
                    case_id=case_id,
                    revision=revision,
                    next_role=next_role,
                    next_action=next_action,
                    purpose=purpose,
                    inputs=["Owner裁定", "未解決Finding"],
                    open_items=unresolved,
                    expected_outputs=expected_outputs,
                )
            elif decision == "held":
                next_role = "owner"
                next_action = "adjudicate"
                state = "held"
                handoff = issue_handoff(
                    case_id=case_id,
                    revision=revision,
                    next_role=next_role,
                    next_action=next_action,
                    purpose="不足する判断材料を確認し、Owner裁定を再開する",
                    inputs=["保留理由", "必要な追加情報", "残余リスク"],
                    open_items=unresolved,
                    expected_outputs=["再開後のOwner裁定"],
                )
            else:
                next_role = None
                next_action = None
                state = decision
                handoff = terminal_handoff(case_id=case_id, revision=revision, result=decision)
            result = self._result(
                case_id=case_id,
                revision=revision,
                state_changed=True,
                next_role=next_role,
                next_action=next_action,
                handoff=handoff,
            )
            self._finish_update(
                updated=updated,
                payload=payload,
                operation="adjudicate",
                revision=revision,
                state=state,
                handoff=handoff,
                result=result,
            )
            return updated, result

        return self.store.mutate(case_id, mutation)

    def status(self, case_id: str, *, resume_format: str | None = None) -> dict:
        case = self.store.load(case_id)
        metadata = case["case_metadata"]
        handoff = deepcopy(case["handoff"])
        from .model import RESOLVED_VERIFICATION_RESULTS
        open_findings = [
            item["finding_id"]
            for item in case["findings"]
            if item.get("status") not in RESOLVED_VERIFICATION_RESULTS
            and item.get("classification") != "improvement-proposal"
        ]
        evidence_gaps = [
            item["finding_id"]
            for item in case["findings"]
            if item.get("classification") == "evidence-gap"
            and item.get("status") not in RESOLVED_VERIFICATION_RESULTS
        ]
        result = self._result(
            case_id=case_id,
            revision=metadata["revision"],
            state_changed=False,
            next_role=handoff["next_role"],
            next_action=handoff["next_action"],
            handoff=handoff,
        )
        result.update(
            {
                "current_state": metadata["status"],
                "last_completed_operation": case["events"][-1]["operation"],
                "open_findings": open_findings,
                "evidence_gaps": evidence_gaps,
                "owner_decisions_required": metadata["status"]
                in {"owner-adjudication", "held-for-owner", "held"},
                "implementation_authorization": deepcopy(
                    case["implementation_authorization"]
                ),
            }
        )
        if resume_format is not None:
            if resume_format != "markdown":
                raise QualityLoopError(
                    "invalid-resume-format",
                    "resume-formatはmarkdownだけを指定できます。",
                )
            from .markdown_report import generate_resume_markdown
            text = generate_resume_markdown(case)
            self.store.atomic_write_text(self.store.case_dir(case_id) / "resume.md", text)
            result["resume_path"] = "resume.md"
        return result

    @staticmethod
    def _validate_create(payload: dict) -> None:
        required = (
            "operation_id",
            "actor_id",
            "role",
            "invocation_id",
            "case_id",
            "owner",
            "baseline",
        )
        missing = [key for key in required if not payload.get(key)]
        if missing:
            raise QualityLoopError(
                "invalid-input",
                f"必須項目が不足しています: {', '.join(missing)}",
                remediation="create-caseの必須項目を補完してください。",
            )
        if payload["role"] != "owner":
            raise QualityLoopError(
                "role-not-allowed",
                "create-caseはOwnerだけが実行できます。",
                remediation="roleをownerにし、OwnerのInvocationから実行してください。",
            )
        if not CASE_ID_PATTERN.fullmatch(payload["case_id"]):
            raise QualityLoopError(
                "invalid-case-id",
                "case_idは英数字で始まる英数字・ドット・ハイフン・下線だけを使用してください。",
                remediation="安全なcase_idへ変更してください。",
            )
        if "cycle_limit" in payload:
            cycle_limit = payload["cycle_limit"]
            if not isinstance(cycle_limit, int) or cycle_limit < 1:
                raise QualityLoopError(
                    "invalid-input",
                    "cycle_limitは1以上の整数で指定してください。",
                )
        QualityLoop._validate_baseline(payload["baseline"])

    @staticmethod
    def _validate_plans(case: dict, plans: object) -> list[dict]:
        if not isinstance(plans, list) or not plans:
            raise QualityLoopError(
                "invalid-plan",
                "plansにはFinding別のResponse Planが必要です。",
            )
        allowed_intents = {
            "fix",
            "disagree-with-evidence",
            "cannot-verify",
            "baseline-change-request",
        }
        known_ids = {item["finding_id"] for item in case["findings"]}
        seen_ids: set[str] = set()
        validated: list[dict] = []
        for plan in plans:
            if not isinstance(plan, dict):
                raise QualityLoopError("invalid-plan", "Planはobjectで指定してください。")
            required = ("finding_id", "understanding", "disposition_intent", "proposed_actions")
            missing = [field for field in required if field not in plan]
            if missing:
                raise QualityLoopError(
                    "invalid-plan",
                    f"Plan必須項目が不足しています: {', '.join(missing)}",
                )
            finding_id = plan["finding_id"]
            if finding_id not in known_ids:
                raise QualityLoopError(
                    "unknown-finding-id",
                    f"未知のFinding IDです: {finding_id}",
                )
            if finding_id in seen_ids:
                raise QualityLoopError(
                    "duplicate-plan",
                    f"Finding {finding_id} へのPlanが重複しています。",
                )
            if plan["disposition_intent"] not in allowed_intents:
                raise QualityLoopError("invalid-plan", "未対応のDisposition Intentです。")
            implementation_status = plan.get("implementation_status", "not-started")
            if implementation_status != "not-started":
                raise QualityLoopError(
                    "invalid-plan-status",
                    "submit-planのimplementation_statusはnot-startedだけを指定できます。",
                    remediation="実装後の状態はsubmit-responseとEvidenceで提出してください。",
                )
            normalized = deepcopy(plan)
            normalized["implementation_status"] = "not-started"
            seen_ids.add(finding_id)
            validated.append(normalized)
        return validated

    @staticmethod
    def _validate_plan_reviews(plans: list[dict], plan_reviews: object) -> list[dict]:
        if not isinstance(plan_reviews, list) or not plan_reviews:
            raise QualityLoopError(
                "invalid-plan-review",
                "plan_reviewsにはPlan別のReview結果が必要です。",
            )
        allowed_outcomes = {
            "plan-accepted",
            "plan-accepted-with-comments",
            "plan-revision-required",
            "finding-withdrawn",
            "converted-to-suggestion",
            "not-applicable",
            "owner-decision-required",
        }
        expected_ids = {item["finding_id"] for item in plans}
        seen_ids: set[str] = set()
        validated: list[dict] = []
        for review in plan_reviews:
            if not isinstance(review, dict):
                raise QualityLoopError(
                    "invalid-plan-review", "PlanReviewはobjectで指定してください。"
                )
            required = ("finding_id", "outcome", "rationale")
            missing = [field for field in required if field not in review]
            if missing:
                raise QualityLoopError(
                    "invalid-plan-review",
                    f"PlanReview必須項目が不足しています: {', '.join(missing)}",
                )
            finding_id = review["finding_id"]
            if finding_id not in expected_ids:
                raise QualityLoopError(
                    "unknown-finding-id",
                    f"今回のPlan提出対象でないFindingです: {finding_id}",
                )
            if finding_id in seen_ids:
                raise QualityLoopError(
                    "duplicate-plan-review",
                    f"Finding {finding_id} のPlanReviewが重複しています。",
                )
            if review["outcome"] not in allowed_outcomes:
                raise QualityLoopError(
                    "invalid-plan-review", "未対応のPlanReview outcomeです。"
                )
            seen_ids.add(finding_id)
            validated.append(deepcopy(review))
        if seen_ids != expected_ids:
            missing_ids = sorted(expected_ids - seen_ids)
            raise QualityLoopError(
                "incomplete-plan-review",
                f"未レビューのPlan提出があります: {', '.join(missing_ids)}",
            )
        return validated

    @staticmethod
    def _validate_residual_risks(case: dict, residual_risks: object) -> list[dict]:
        if not isinstance(residual_risks, list):
            raise QualityLoopError(
                "invalid-input",
                "residual_risksは配列で指定してください。",
            )
        findings_by_id = {
            item["finding_id"]: item for item in case["findings"]
        }
        expected_ids = QualityLoop._material_unresolved_finding_ids(case)
        seen_ids: set[str] = set()
        validated: list[dict] = []
        required = (
            "finding_id",
            "current_status",
            "severity",
            "residual_risk_description",
            "likelihood",
            "impact",
            "qa_recommendation",
            "confidence",
        )
        allowed_likelihoods = {"low", "medium", "high", "unknown"}
        allowed_impacts = {"low", "medium", "high", "critical"}
        allowed_recs = {"accept", "accept-with-conditions", "require-remediation", "defer"}
        allowed_confidences = {"high", "medium", "low", "unknown"}

        for item in residual_risks:
            if not isinstance(item, dict):
                raise QualityLoopError("invalid-input", "各residual_riskはobjectで指定してください。")
            missing = [k for k in required if k not in item]
            if missing:
                raise QualityLoopError(
                    "invalid-input",
                    f"residual_risk必須項目が不足しています: {', '.join(missing)}",
                )
            fid = item["finding_id"]
            if fid not in findings_by_id:
                raise QualityLoopError(
                    "unknown-finding-id",
                    f"未知のFinding IDです: {fid}",
                )
            if fid not in expected_ids:
                raise QualityLoopError(
                    "non-material-residual-risk",
                    f"Finding {fid} はmaterial unresolved residual riskの対象ではありません。",
                    remediation="解決済み、撤回済み、提案扱いのFindingはFinal Risk Assessmentから除外してください。",
                )
            if fid in seen_ids:
                raise QualityLoopError(
                    "invalid-input",
                    f"Finding ID {fid} の残余リスク評価が重複しています。",
                )
            if item["likelihood"] not in allowed_likelihoods:
                raise QualityLoopError("invalid-input", f"likelihoodが不正です: {item['likelihood']}")
            if item["impact"] not in allowed_impacts:
                raise QualityLoopError("invalid-input", f"impactが不正です: {item['impact']}")
            if item["qa_recommendation"] not in allowed_recs:
                raise QualityLoopError("invalid-input", f"qa_recommendationが不正です: {item['qa_recommendation']}")
            if item["confidence"] not in allowed_confidences:
                raise QualityLoopError("invalid-input", f"confidenceが不正です: {item['confidence']}")
            canonical = findings_by_id[fid]
            canonical_status = canonical.get("status", "open")
            if item["current_status"] != canonical_status:
                raise QualityLoopError(
                    "risk-status-mismatch",
                    f"Finding {fid} のcurrent_statusがcanonical stateと一致しません: "
                    f"submitted={item['current_status']}, canonical={canonical_status}",
                    remediation="case.jsonのFinding statusを確認し、最新状態で再提出してください。",
                )
            if item["severity"] != canonical["severity"]:
                raise QualityLoopError(
                    "risk-severity-mismatch",
                    f"Finding {fid} のseverityがcanonical stateと一致しません: "
                    f"submitted={item['severity']}, canonical={canonical['severity']}",
                    remediation="case.jsonのFinding severityを確認し、最新状態で再提出してください。",
                )
            seen_ids.add(fid)
            validated.append(deepcopy(item))
        missing_ids = sorted(expected_ids - seen_ids)
        if missing_ids:
            raise QualityLoopError(
                "residual-risk-coverage-incomplete",
                "material unresolved Findingの残余リスク評価が不足しています: "
                + ", ".join(missing_ids),
                remediation="提示された全Finding IDについて残余リスク評価を追加してください。",
            )
        return validated

    @staticmethod
    def _material_unresolved_finding_ids(case: dict) -> set[str]:
        return {
            finding["finding_id"]
            for finding in case.get("findings", [])
            if finding.get("status", "open") not in RESOLVED_VERIFICATION_RESULTS
            and finding.get("classification") != "improvement-proposal"
        }

    @staticmethod
    def _required_plan_finding_ids(case: dict) -> set[str]:
        return {
            finding["finding_id"]
            for finding in case.get("findings", [])
            if finding.get("plan_required", False)
            and finding.get("status", "open") not in RESOLVED_VERIFICATION_RESULTS
            and finding.get("classification") != "improvement-proposal"
        }

    @staticmethod
    def _approved_plan_finding_ids(case: dict) -> set[str]:
        return {
            finding["finding_id"]
            for finding in case.get("findings", [])
            if finding.get("status") == "plan-approved"
        }

    @staticmethod
    def _pending_required_plan_finding_ids(case: dict) -> set[str]:
        return (
            QualityLoop._required_plan_finding_ids(case)
            - QualityLoop._approved_plan_finding_ids(case)
        )

    @staticmethod
    def _validate_responses(case: dict, responses: object) -> list[dict]:
        if not isinstance(responses, list) or not responses:
            raise QualityLoopError(
                "invalid-response",
                "responsesにはFinding別回答が必要です。",
            )
        allowed_dispositions = {
            "accepted",
            "fix-submitted",
            "disagreed-with-evidence",
            "cannot-verify",
            "baseline-change-requested",
        }
        known_ids = {item["finding_id"] for item in case["findings"]}
        seen_ids: set[str] = set()
        validated: list[dict] = []
        for response in responses:
            if not isinstance(response, dict):
                raise QualityLoopError("invalid-response", "Responseはobjectで指定してください。")
            required = ("finding_id", "disposition", "rationale", "evidence_refs")
            missing = [field for field in required if field not in response]
            if missing:
                raise QualityLoopError(
                    "invalid-response",
                    f"Response必須項目が不足しています: {', '.join(missing)}",
                )
            finding_id = response["finding_id"]
            if finding_id not in known_ids:
                raise QualityLoopError(
                    "unknown-finding-id",
                    f"未知のFinding IDです: {finding_id}",
                )
            if finding_id in seen_ids:
                raise QualityLoopError(
                    "duplicate-finding-response",
                    f"Finding {finding_id} への回答が重複しています。",
                )
            if response["disposition"] not in allowed_dispositions:
                raise QualityLoopError("invalid-response", "未対応のDispositionです。")
            seen_ids.add(finding_id)
            validated.append(deepcopy(response))
        return validated

    @staticmethod
    def _validate_verifications(
        responses: list[dict], verifications: object
    ) -> list[dict]:
        if not isinstance(verifications, list) or not verifications:
            raise QualityLoopError(
                "invalid-verification",
                "verificationsにはFinding別検証が必要です。",
            )
        expected_ids = {item["finding_id"] for item in responses}
        seen_ids: set[str] = set()
        validated: list[dict] = []
        for verification in verifications:
            if not isinstance(verification, dict):
                raise QualityLoopError(
                    "invalid-verification", "Verificationはobjectで指定してください。"
                )
            required = ("finding_id", "result", "rationale", "evidence_refs")
            missing = [field for field in required if field not in verification]
            if missing:
                raise QualityLoopError(
                    "invalid-verification",
                    f"Verification必須項目が不足しています: {', '.join(missing)}",
                )
            finding_id = verification["finding_id"]
            if finding_id not in expected_ids:
                raise QualityLoopError(
                    "unknown-finding-id",
                    f"今回の提出対象でないFindingです: {finding_id}",
                )
            if finding_id in seen_ids:
                raise QualityLoopError(
                    "duplicate-verification",
                    f"Finding {finding_id} の検証が重複しています。",
                )
            from .model import VERIFICATION_RESULTS
            if verification["result"] not in VERIFICATION_RESULTS:
                raise QualityLoopError(
                    "invalid-verification", "未対応のVerification resultです。"
                )
            seen_ids.add(finding_id)
            validated.append(deepcopy(verification))
        if seen_ids != expected_ids:
            missing_ids = sorted(expected_ids - seen_ids)
            raise QualityLoopError(
                "incomplete-verification",
                f"未検証の提出Findingがあります: {', '.join(missing_ids)}",
            )
        return validated

    @staticmethod
    def _validate_change_observation(
        *,
        current: dict,
        responses: list[dict],
        observation: object,
        evidence_ids: set[str],
    ) -> dict:
        declared = {
            target for response in responses for target in response["changed_targets"]
        }
        if not declared:
            return {
                "method": "none",
                "scope": [],
                "observed_changed_targets": [],
                "limitations": [],
            }
        if not isinstance(observation, dict):
            raise QualityLoopError(
                "change-observation-required",
                "変更提出のverifyには独立change_observationが必要です。",
            )
        required = (
            "method",
            "scope",
            "before_evidence_id",
            "after_evidence_id",
            "observed_changed_targets",
            "limitations",
        )
        missing = [field for field in required if field not in observation]
        if missing:
            raise QualityLoopError(
                "invalid-change-observation",
                f"change_observation必須項目が不足しています: {', '.join(missing)}",
            )
        observation_refs = {
            observation["before_evidence_id"],
            observation["after_evidence_id"],
        }
        if not observation_refs.issubset(evidence_ids):
            raise QualityLoopError(
                "unknown-evidence-id",
                "変更観測の開始・終了Evidenceを確認できません。",
            )
        observed = set(observation["observed_changed_targets"])
        undeclared = sorted(observed - declared)
        if undeclared:
            raise QualityLoopError(
                "undeclared-change-detected",
                f"申告外変更を検出しました: {', '.join(undeclared)}",
                remediation="申告外変更を戻すか、Implementer提出を訂正してください。",
            )
        allowed = set(current["implementation_authorization"].get("allowed_targets", []))
        unauthorized = sorted(observed - allowed)
        if unauthorized:
            raise QualityLoopError(
                "unauthorized-change-detected",
                f"許可外変更を検出しました: {', '.join(unauthorized)}",
            )
        unobserved = sorted(declared - observed)
        if unobserved:
            raise QualityLoopError(
                "change-observation-incomplete",
                f"申告された変更を観測できません: {', '.join(unobserved)}",
                remediation="観測範囲を補完するかunverifiedとして再提出してください。",
            )
        return deepcopy(observation)

    @staticmethod
    def _validate_baseline(baseline: object) -> None:
        if not isinstance(baseline, dict):
            raise QualityLoopError("invalid-input", "baselineはobjectで指定してください。")
        baseline_required = (
            "purpose",
            "intended_use",
            "risk_context",
            "requirements",
            "acceptance_criteria",
            "targets",
            "target_revision",
        )
        baseline_missing = [key for key in baseline_required if not baseline.get(key)]
        if baseline_missing:
            raise QualityLoopError(
                "invalid-input",
                f"baseline必須項目が不足しています: {', '.join(baseline_missing)}",
                remediation="Purpose、intended_use、risk_context、要求、受入基準、対象、対象revisionを指定してください。",
            )
        # Quality Intent validation (intended_use and risk_context)
        if not isinstance(baseline.get("intended_use"), dict):
            raise QualityLoopError("invalid-input", "intended_useはobjectで指定してください。")
        if not isinstance(baseline.get("risk_context"), dict) or "criticality" not in baseline["risk_context"]:
            raise QualityLoopError("invalid-input", "risk_contextにはcriticalityが必要です。")
        crit = baseline["risk_context"].get("criticality")
        if crit not in {"low", "medium", "high", "regulated"}:
            raise QualityLoopError(
                "invalid-input",
                f"risk_context.criticalityが不正です: {crit}（対応値: low, medium, high, regulated）",
            )

    @staticmethod
    def _duplicate_result(case: dict, operation_id: object) -> dict | None:
        if not operation_id:
            return None
        for event in case["events"]:
            if event["operation_id"] == operation_id:
                result = deepcopy(event["result"])
                result["status"] = "already-processed"
                result["state_changed"] = False
                return result
        return None

    @staticmethod
    def _validate_update(case: dict, payload: dict, operation: str) -> None:
        required = (
            "operation_id",
            "actor_id",
            "role",
            "invocation_id",
            "previous_handoff_id",
            "expected_case_revision",
        )
        missing = [key for key in required if payload.get(key) is None]
        if missing:
            raise QualityLoopError(
                "invalid-input",
                f"更新操作の必須項目が不足しています: {', '.join(missing)}",
            )
        forbidden = sorted(set(payload) - ALLOWED_FIELDS[operation])
        if forbidden:
            raise QualityLoopError(
                "forbidden-field",
                f"{operation}が更新できない項目です: {', '.join(forbidden)}",
                remediation="Roleに許可された入力Schemaだけを提出してください。",
            )
        expected_role = EXPECTED_ROLE[operation]
        if payload["role"] != expected_role:
            raise QualityLoopError(
                "role-not-allowed",
                f"{operation}は{expected_role} Roleだけが実行できます。",
            )
        if operation == "adjudicate":
            registered_owner = case.get("case_metadata", {}).get("owner")
            if registered_owner and payload.get("actor_id") != registered_owner:
                raise QualityLoopError(
                    "unauthorized-actor",
                    f"案件の登録Owner({registered_owner})と裁定実行者({payload.get('actor_id')})が一致しません。",
                    remediation="登録されたOwnerアカウントから実行してください。",
                )
        for event in case["events"]:
            if (
                event["invocation_id"] == payload["invocation_id"]
                and event["role"] != payload["role"]
            ):
                raise QualityLoopError(
                    "role-conflict",
                    "同一Invocationで複数Roleを兼務できません。",
                )
        current_revision = case["case_metadata"]["revision"]
        if payload["expected_case_revision"] != current_revision:
            raise QualityLoopError(
                "revision-conflict",
                f"期待revision {payload['expected_case_revision']} と現行revision {current_revision} が一致しません。",
                remediation="statusで最新revisionとhandoffを取得してください。",
            )
        expected_states = {EXPECTED_STATE[operation]}
        if operation == "adjudicate":
            expected_states.add("held")
        if case["case_metadata"]["status"] not in expected_states:
            raise QualityLoopError(
                "state-transition-not-allowed",
                f"現在状態では{operation}を実行できません。",
                remediation="statusが示すnext_actionを実行してください。",
            )
        handoff = case["handoff"]
        if (
            payload["previous_handoff_id"] != handoff["handoff_id"]
            or handoff["issued_revision"] != current_revision
            or handoff["next_role"] != payload["role"]
            or handoff["next_action"] != operation
        ):
            raise QualityLoopError(
                "handoff-mismatch",
                "現在handoffと操作入力が一致しません。",
                remediation="statusで最新handoffを取得してください。",
            )

    @staticmethod
    def _finish_update(
        *,
        updated: dict,
        payload: dict,
        operation: str,
        revision: int,
        state: str,
        handoff: dict,
        result: dict,
    ) -> None:
        now = utc_now()
        previous_handoff_id = updated["handoff"]["handoff_id"]
        updated["case_metadata"]["revision"] = revision
        updated["case_metadata"]["status"] = state
        updated["case_metadata"]["updated_at"] = now
        updated["handoff"] = handoff
        updated["events"].append(
            {
                "operation_id": payload["operation_id"],
                "actor_id": payload["actor_id"],
                "role": payload["role"],
                "invocation_id": payload["invocation_id"],
                "operation": operation,
                "revision": revision,
                "previous_handoff_id": previous_handoff_id,
                "handoff_acknowledged": True,
                "timestamp": now,
                "result": deepcopy(result),
            }
        )

    @staticmethod
    def _result(
        *,
        case_id: str,
        revision: int,
        state_changed: bool,
        next_role: str | None,
        next_action: str | None,
        handoff: dict | None,
        status: str = "ok",
    ) -> dict:
        return {
            "status": status,
            "case_id": case_id,
            "case_revision": revision,
            "state_changed": state_changed,
            "next_role": next_role,
            "next_action": next_action,
            "handoff": deepcopy(handoff),
        }
