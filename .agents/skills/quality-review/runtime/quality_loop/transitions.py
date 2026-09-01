from __future__ import annotations


EXPECTED_STATE = {
    "review": "reviewer-action",
    "submit-plan": "implementer-plan",
    "review-plan": "reviewer-plan-review",
    "submit-response": "implementer-action",
    "verify": "reviewer-verification",
    "assess-risk": "reviewer-final-assessment",
    "adjudicate": "owner-adjudication",
}

EXPECTED_ROLE = {
    "review": "reviewer",
    "submit-plan": "implementer",
    "review-plan": "reviewer",
    "submit-response": "implementer",
    "verify": "reviewer",
    "assess-risk": "reviewer",
    "adjudicate": "owner",
}

COMMON_UPDATE_FIELDS = {
    "operation_id",
    "actor_id",
    "role",
    "invocation_id",
    "previous_handoff_id",
    "expected_case_revision",
}

ALLOWED_FIELDS = {
    "review": COMMON_UPDATE_FIELDS | {"findings", "evidence"},
    "submit-plan": COMMON_UPDATE_FIELDS | {"plans", "evidence"},
    "review-plan": COMMON_UPDATE_FIELDS | {"plan_reviews", "evidence"},
    "submit-response": COMMON_UPDATE_FIELDS
    | {"changed_targets", "responses", "evidence"},
    "verify": COMMON_UPDATE_FIELDS
    | {"verifications", "new_findings", "change_observation", "evidence", "early_risk_assessment", "early_risk_rationale"},
    "assess-risk": COMMON_UPDATE_FIELDS
    | {"overall_recommendation", "rationale", "residual_risks"},
    "adjudicate": COMMON_UPDATE_FIELDS
    | {
        "decision",
        "rationale",
        "conditions",
        "residual_risks",
        "baseline_update",
        "implementation_authorization",
        "additional_cycles",
        "dry_run",
        "confirm",
    },
}
