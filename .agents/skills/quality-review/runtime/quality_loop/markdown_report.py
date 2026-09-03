from __future__ import annotations

from typing import Any


def determine_traffic_light(
    *,
    status: str,
    cycle_count: int,
    cycle_limit: int,
    blocking_findings: list[dict[str, Any]],
    gap_findings: list[dict[str, Any]],
    has_reviewed: bool = True,
) -> tuple[str, str]:
    """
    信号機判定（決定論的優先順位:
    1. 赤: 保留/再レビュー/却下/サイクル上限/未解決blocking Findingあり
    2. 白: 初回レビュー未実施 (案件作成直後)
    3. 黄: 観測限界 (evidence-gap) / 残余リスク受容 / 最終リスク評価中
    4. 青: 修正・検証進行中 (blockingなし・gapなし)
    5. 緑: 全件検証完了・安全
    ）
    """
    # 1. 終端状態 (Owner最終裁定) を最優先
    if status == "accepted":
        return "🟢 緑 (受入完了・安全) [Owner裁定: accepted 完了]", "Ownerにより受入裁定が確定しており、案件は安全に完了しています"
    if status == "accepted-with-risk":
        return "🟡 黄 (条件付き受入承認済み) [Owner裁定: accepted-with-risk 承認済み (残余リスク受容)]", "Ownerにより残余リスク付きで条件付き受入が確定しています"
    if status == "rejected":
        return "🔴 赤 (案件却下) [Owner裁定: rejected 完了]", "Ownerにより案件が却下(rejected)されました"

    # 2. 未レビュー状態 (案件作成直後 / 初回レビュー待ち)
    if not has_reviewed or status in ("created", "reviewer-action"):
        return "⚪ 白 (未評価・初回レビュー待ち)", "案件作成済みですが、Reviewerによる初回評価が未実施です"

    # 3. 未解決の重要課題 / 基準変更再レビュー / サイクル上限到達 / 保留 (非終端時)
    if (
        status in ("held", "requires-rereview")
        or len(blocking_findings) > 0
        or cycle_count >= cycle_limit
    ):
        reasons: list[str] = []
        if status == "held":
            reasons.append("案件が保留(held)されています（再開にはOwnerによるadjudicateが必要です）")
        if status == "requires-rereview":
            reasons.append("基準変更に伴う再レビューが必要です")
        if blocking_findings:
            reasons.append(f"未解決の重要課題が {len(blocking_findings)} 件あります")
        if cycle_count >= cycle_limit:
            reasons.append(f"サイクル上限({cycle_limit})に到達しています（Reviewerによる最終リスク評価またはOwner裁定が必要です）")

        return "🔴 赤 (要対応・確認待ち)", " / ".join(reasons) or "要対応事項があります"

    # 4. 黄信号 (観測限界 / 最終リスク評価中)
    if len(gap_findings) > 0 or status == "reviewer-final-assessment":
        if status == "reviewer-final-assessment":
            return "🟡 黄 (最終リスク評価中)", "サイクル上限または残余リスクに伴い、ReviewerによるFinal Risk Assessmentを実施中です"
        return "🟡 黄 (条件付き・外部制約あり)", f"観測限界(evidence-gap)が {len(gap_findings)} 件あります"

    # 5. 進行中状態 (Plan策定中 / 実装中 / 再検証中)
    if status in ("implementer-plan", "reviewer-plan-review", "implementer-action", "reviewer-verification"):
        return "🔵 青 (評価・修正進行中)", f"現在 {status} 工程が進行中です（検証完了前）"

    # 6. 緑信号 (全件検証完了・Owner裁定待ち)
    return "🟢 緑 (検証完了・安全)", "全件の有効性確認が完了しており、不適合はありません"


def generate_action_guide(
    *,
    case_id: str,
    next_role: str | None,
    next_action: str | None,
    handoff_id: str,
    traffic_color: str,
    revision: int = 1,
) -> list[str]:
    lines: list[str] = ["## 4. 次の一手 (Handoff ガイド)"]
    if (
        not next_role
        or not next_action
        or next_role in ("none", "なし (終端)", None)
        or next_action in ("none", "なし (終端)", None)
    ):
        lines.append("- この案件は終端状態に達しており、追加の操作は不要です。")
        return lines

    lines.append(f"- **次の担当**: `{next_role}`")
    lines.append(f"- **実行すべき操作**: `{next_action}`")
    lines.append(f"- **参照Handoff ID**: `{handoff_id}`")
    lines.append("")
    lines.append("### AI/Operator向け実行コマンド例 (入力ファイル方式):")

    if next_role == "owner" and next_action == "adjudicate":
        if "🟢" in traffic_color:
            lines.append("1. **事前確認 (dry-run)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input adjudicate_dry_run.json\n   ```")
            lines.append("2. **受入本承認 (confirm)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input adjudicate_confirm.json\n   ```")
        elif "🟡" in traffic_color:
            lines.append("1. **残余リスク付き受入 (事前dry-run)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input adjudicate_risk_dry_run.json\n   ```")
            lines.append("2. **残余リスク付き受入 (本承認)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input adjudicate_risk_confirm.json\n   ```")
            lines.append("3. **再修正の指示 (追加サイクル付与)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input rework.json\n   ```")
        else:
            lines.append("1. **再作業指示 (追加サイクル付与)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input rework.json\n   ```")
            lines.append("2. **案件の保留 (held)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input hold.json\n   ```")
            lines.append("3. **案件の却下 (rejected)**:")
            lines.append(f"   ```bash\n   python3 -B -m quality_loop.cli adjudicate --case-id {case_id} --input reject.json\n   ```")
    elif next_role == "reviewer" and next_action == "assess-risk":
        lines.append(f"```bash\npython3 -B -m quality_loop.cli assess-risk --case-id {case_id} --input assess_risk.json\n```")
    elif next_role == "implementer" and next_action == "submit-plan":
        lines.append(f"```bash\npython3 -B -m quality_loop.cli submit-plan --case-id {case_id} --input plan.json\n```")
    elif next_role == "reviewer" and next_action == "review-plan":
        lines.append(f"```bash\npython3 -B -m quality_loop.cli review-plan --case-id {case_id} --input plan_review.json\n```")
    elif next_role == "implementer" and next_action == "submit-response":
        lines.append(f"```bash\npython3 -B -m quality_loop.cli submit-response --case-id {case_id} --input response.json\n```")
    elif next_role == "reviewer" and next_action == "verify":
        lines.append(f"```bash\npython3 -B -m quality_loop.cli verify --case-id {case_id} --input verify.json\n```")
    elif next_role == "reviewer" and next_action == "review":
        lines.append(f"```bash\npython3 -B -m quality_loop.cli review --case-id {case_id} --input review.json\n```")
    else:
        lines.append(f"```bash\npython3 -B -m quality_loop.cli {next_action} --case-id {case_id} --input input.json\n```")

    return lines


def generate_resume_markdown(case: dict[str, Any]) -> str:
    meta = case.get("case_metadata", {})
    case_id = meta.get("case_id", "UNKNOWN")
    # 正本フィールド revision を優先し、後方互換で case_revision をフォールバック
    rev = meta.get("revision", meta.get("case_revision", 1))
    status = meta.get("status", "unknown")
    owner = meta.get("owner", "unknown")
    cycle_count = meta.get("cycle_count", 0)
    cycle_limit = meta.get("cycle_limit", 3)

    baseline = case.get("baseline", {})
    purpose = baseline.get("purpose", "")
    targets = baseline.get("targets", [])

    auth = case.get("implementation_authorization", {})
    auth_allowed = auth.get("allowed", False)
    auth_targets = ", ".join(f"`{t}`" for t in auth.get("allowed_targets", [])) or "なし"

    handoff = case.get("handoff", {})
    next_role = handoff.get("next_role") or "なし (終端)"
    next_action = handoff.get("next_action") or "なし (終端)"
    handoff_id = handoff.get("handoff_id", "none")
    last_op = meta.get("last_operation", "なし")

    findings = case.get("findings", [])
    from .model import RESOLVED_VERIFICATION_RESULTS
    blocking_findings = [
        f
        for f in findings
        if f.get("status") not in RESOLVED_VERIFICATION_RESULTS
        and f.get("classification") in ("requirement-violation", "regression", "purpose-risk")
    ]
    gap_findings = [
        f
        for f in findings
        if f.get("status") not in RESOLVED_VERIFICATION_RESULTS and f.get("classification") == "evidence-gap"
    ]
    proposals = [f for f in findings if f.get("classification") == "improvement-proposal"]

    events = case.get("events", [])
    has_reviewed = any(e.get("operation") == "review" for e in events)

    traffic_color, traffic_reason = determine_traffic_light(
        status=status,
        cycle_count=cycle_count,
        cycle_limit=cycle_limit,
        blocking_findings=blocking_findings,
        gap_findings=gap_findings,
        has_reviewed=has_reviewed,
    )

    lines: list[str] = [
        f"# 案件ステータス要約: {case_id} (Revision {rev})",
        "",
        f"### **総合状況**: {traffic_color}",
        f"> **理由・診断**: {traffic_reason}",
        "",
        "---",
        "",
        "## 1. 基本情報 & ガードレール状況",
        f"- **現在の状態**: {status}",
        f"- **サイクル**: {cycle_count}/{cycle_limit}",
        f"- **Owner (統括者)**: {owner}",
        f"- **最後の完了操作**: {last_op}",
        f"- **次のRole**: {next_role}",
        f"- **次の操作**: {next_action}",
        f"- **最新Handoff ID**: `{handoff_id}`",
        f"- **品質目的 (Purpose)**: {purpose}",
        f"- **対象成果物**: {', '.join(f'`{t}`' for t in targets) or 'なし'}",
        f"- **Owner許可範囲**: {auth_targets} (変更許可: {'あり' if auth_allowed else 'なし'})",
        "",
        "## 2. 不適合・課題 (Findings)",
    ]

    all_non_proposals = [f for f in findings if f.get("classification") != "improvement-proposal"]
    if not all_non_proposals:
        lines.append("- （未解決の不適合はありません）")
    else:
        for f in all_non_proposals:
            fid = f.get("finding_id")
            cls = f.get("classification")
            sev = f.get("severity", "medium")
            fact = f.get("observed_fact", "")
            fstatus = f.get("status", "open")
            lines.append(f"- **[{fid}]** ({cls} / Severity: {sev} / Status: `{fstatus}`): {fact}")

    evidence_gap_findings = [
        f for f in findings
        if f.get("status") not in RESOLVED_VERIFICATION_RESULTS
        and f.get("required_evidence")
    ]
    lines.append("")
    lines.append("## 3. 必要Evidence")
    if not evidence_gap_findings:
        lines.append("- なし")
    else:
        for f in evidence_gap_findings:
            lines.append(f"- {f.get('finding_id')}: {f.get('required_evidence')}")

    observation = case.get("change_observation", {})
    scope = observation.get("scope", []) if isinstance(observation, dict) else []
    limitations = observation.get("limitations", []) if isinstance(observation, dict) else []
    lines.append("")
    lines.append("## 4. 変更観測の範囲")
    lines.append(f"- 対象: {', '.join(str(item) for item in scope) or '未設定'}")
    if limitations:
        lines.extend(f"- {item}" for item in limitations)
    else:
        lines.append("- 観測上の制限は未登録です")

    lines.append("")
    lines.append("## 5. 改善提案（次回以降への引き継ぎ事項）")
    if not proposals:
        lines.append("- （改善提案はありません）")
    else:
        for p in proposals:
            pid = p.get("finding_id")
            fact = p.get("observed_fact", "")
            lines.append(f"- **[{pid}]**: {fact}")

    lines.append("")
    action_guide = generate_action_guide(
            case_id=case_id,
            next_role=next_role,
            next_action=next_action,
            handoff_id=handoff_id,
            traffic_color=traffic_color,
            revision=rev,
        )
    # セクション番号は必要Evidence・観測範囲の追加後も一貫させる。
    action_guide[0] = "## 6. 次の一手 (Handoff ガイド)"
    lines.extend(action_guide)

    lines.append("")
    lines.append("---")
    lines.append("*この文書は表示専用であり、案件正本ではありません。正本は `case.json` です。*")
    lines.append("")

    return "\n".join(lines)


def generate_final_risk_assessment_markdown(case: dict[str, Any]) -> str:
    meta = case.get("case_metadata", {})
    case_id = meta.get("case_id", "UNKNOWN")
    rev = meta.get("revision", meta.get("case_revision", 1))
    findings = case.get("findings", [])
    from .model import RESOLVED_VERIFICATION_RESULTS

    resolved = [f for f in findings if f.get("status") in RESOLVED_VERIFICATION_RESULTS]
    residual = [
        f
        for f in findings
        if f.get("status") not in RESOLVED_VERIFICATION_RESULTS
        and f.get("classification") != "improvement-proposal"
    ]
    crit_high = [f for f in residual if f.get("severity") in ("critical", "high")]

    assessments = case.get("final_risk_assessments", [])
    latest_assessment = assessments[-1] if assessments else None

    overall_rec = (
        latest_assessment.get("overall_recommendation", "未評価")
        if latest_assessment
        else "未評価"
    )
    rationale = (
        latest_assessment.get("rationale", "")
        if latest_assessment
        else "リスク評価がまだ実施されていません。"
    )
    risk_by_id = {
        item.get("finding_id"): item
        for item in (latest_assessment or {}).get("residual_risks", [])
    }

    lines = [
        f"# 最終リスク評価報告書: {case_id} (Revision {rev})",
        "",
        "## 1. 概要指標 (Summary Metrics)",
        f"- **解決済み指摘数 (Resolved)**: {len(resolved)} 件",
        f"- **残余指摘数 (Residual)**: {len(residual)} 件",
        f"- **残余Critical/High指摘数**: {len(crit_high)} 件",
        f"- **Final Risk coverage**: {len(risk_by_id)}/{len(residual)} 件",
        f"- **QA総合推奨 (QA Recommendation)**: `{overall_rec}`",
        "",
        "## 2. QA評価所見 (QA Rationale)",
        f"> {rationale}",
        "",
        "## 3. 残余リスク評価詳細 (Residual Risks & Mitigation Details)",
    ]

    if latest_assessment:
        for f in residual:
            fid = f.get("finding_id")
            r = risk_by_id.get(fid)
            if r is None:
                lines.append(f"### 指摘 [{fid}] (Status: `{f.get('status', 'open')}`)")
                lines.append("- **残余リスク評価**: 未提出（Core coverage違反）")
                lines.append("")
                continue
            status = f.get("status", "open")
            desc = r.get("residual_risk_description")
            like = r.get("likelihood")
            imp = r.get("impact")
            qa_rec = r.get("qa_recommendation")
            conf = r.get("confidence")
            prop = r.get("proportionality_assessment", "")
            controls = r.get("implemented_controls", [])
            assumptions = r.get("assumptions_supporting_acceptance", [])
            alternatives = r.get("alternatives", [])
            triggers = r.get("reassessment_triggers", [])

            lines.append(f"### 指摘 [{fid}] (Status: `{status}` / Severity: `{f.get('severity')}`)")
            lines.append(f"- **残余リスク説明**: {desc}")
            lines.append(f"- **リスク評価**: 発生可能性: `{like}` / 影響度: `{imp}` / 確信度: `{conf}`")
            lines.append(f"- **QA推奨**: `{qa_rec}`")
            if controls:
                lines.append(f"- **実装済み対策 (Implemented Controls)**: {', '.join(controls)}")
            if assumptions:
                lines.append(f"- **受入前提条件 (Acceptance Assumptions)**: {', '.join(assumptions)}")
            if alternatives:
                lines.append(f"- **代替策・選択肢 (Alternatives)**: {', '.join(alternatives)}")
            if prop:
                lines.append(f"- **比例性・妥当性評価 (Proportionality)**: {prop}")
            if triggers:
                lines.append(f"- **再評価トリガー (Reassessment Triggers)**: {', '.join(triggers)}")
            lines.append("")
    elif not residual:
        lines.append("- （残余リスクはありません。全件解決済みです）\n")
    else:
        for f in residual:
            lines.append(f"- **[{f.get('finding_id')}]** ({f.get('classification')} / Severity: {f.get('severity')}): {f.get('observed_fact')}")
        lines.append("")

    lines.append("## 4. Owner意思決定オプション (Decision Options)")
    lines.append("1. **受入 (accepted)**: 残余リスクがなく全件適合している場合に承認")
    lines.append("2. **条件付き受入 (accepted-with-risk)**: 上記の受入前提条件・対策を確認の上、残余リスクを受容して承認")
    lines.append("3. **再修正指示 (rework-requested)**: 追加サイクル数を付与して再修正を指示")
    lines.append("4. **保留 (held)** / **却下 (rejected)**: 案件の中断または終了")
    lines.append("")
    lines.append("---")
    lines.append("*この文書は表示専用サマリーです。案件正本は `case.json` です。*")
    lines.append("")

    return "\n".join(lines)
