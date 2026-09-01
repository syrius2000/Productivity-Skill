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
        return {
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
