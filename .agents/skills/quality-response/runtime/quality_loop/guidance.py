from __future__ import annotations


def next_step(next_role: str | None, next_action: str | None, case_id: str, revision: int, handoff: dict | None) -> dict:
    if not next_role or not next_action:
        return {"status": "terminal-or-owner-recorded", "担当": "なし（終端）", "目的": "Owner裁定または保留状態を確認する", "message_template": "案件の終端状態を確認しました。受入・保留・却下の記録と残余リスクを確認してください。", "required_inputs": ["case.jsonの最終状態", "Owner裁定"], "guardrails": ["この表示だけで受入やクローズを推測しない"]}
    labels = {
        ("reviewer", "review-plan"): ("Reviewer", "Response PlanをFinding単位で評価する"),
        ("reviewer", "verify"): ("Reviewer", "修正結果とEvidenceを独立検証する"),
        ("implementer", "submit-plan"): ("Implementer", "Finding別の理解と修正・反証方針を提出する"),
        ("implementer", "submit-response"): ("Implementer", "承認済み範囲だけを修正しEvidenceを提出する"),
        ("owner", "adjudicate"): ("Owner", "Finding、Evidence、残余リスクを確認して裁定する"),
    }
    role_label, purpose = labels.get((next_role, next_action), (next_role, f"{next_action}を実行する"))
    template = f"案件 {case_id} のrevision {revision}、handoff {handoff.get('handoff_id', '不明') if handoff else '不明'}を受け取りました。{purpose}。"
    guardrails = ["表示された担当Role以外の操作を実行しない", "case.jsonを直接編集しない"]
    if next_action == "submit-plan": guardrails.append("Plan承認前にコード変更を開始しない")
    if next_role == "owner": guardrails.append("Owner裁定前に受入・クローズを確定しない")
    return {"status": "action-required", "担当": role_label, "目的": purpose, "message_template": template, "required_inputs": ["case_id", "case_revision", "handoff_id", "handoffのopen_items"], "guardrails": guardrails}
