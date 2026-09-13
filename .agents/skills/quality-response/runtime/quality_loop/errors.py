from __future__ import annotations


class QualityLoopError(Exception):
    """公開契約として返せる失敗。"""

    def __init__(
        self,
        error_code: str,
        message: str,
        *,
        exit_code: int = 2,
        remediation: str = "入力と現在状態を確認してください。",
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.exit_code = exit_code
        self.remediation = remediation

    def as_result(self, case_id: str | None = None) -> dict:
        result = {
            "status": "error",
            "error_code": self.error_code,
            "message": self.message,
            "remediation": self.remediation,
            "case_id": case_id,
            "case_revision": None,
            "state_changed": False,
            "next_role": None,
            "next_action": None,
            "handoff": None,
        }
        if self.error_code == "no-cases-found":
            result["case_setup_required"] = True
            result["next_step"] = {
                "status": "case-setup-required",
                "担当": "OwnerとAI",
                "目的": "対象、QA目的、利用環境、リスク、要求、受入基準を下書きに整理する",
                "message_template": "caseがないため、まずprepare-caseで下書きを作成し、ファイルを確認してからcreate-caseへ渡してください。",
                "required_inputs": ["owner", "request", "targets", "intended_use", "risk_context", "requirements", "acceptance_criteria"],
                "guardrails": ["下書き確認前にcase正本を作成しない", "AIだけでOwner確認を確定しない"],
            }
        return result
