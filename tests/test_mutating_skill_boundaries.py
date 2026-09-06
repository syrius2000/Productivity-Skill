from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


def test_artifacts_archiver_requires_inventory_and_explicit_approval() -> None:
    text = (SKILLS / "artifacts-archiver/SKILL.md").read_text(encoding="utf-8")
    assert "### 1. 読み取り調査と対象一覧" in text
    assert "読み取り専用" in text
    assert "対象一覧" in text
    assert "明示承認" in text
    assert "復元情報" in text
    assert "再帰削除は行わない" in text
    assert "パス」「状態」「候補/除外」「根拠」「リンク確認」「復元情報」「必要な承認" in text
    assert "同じ案件・目的の完了文書" in text
    assert "日付や文書別の復元先が異なっても" in text
    assert "対象と結論」「確定した決定と理由」「主要成果と検証の限界" in text


def test_domain_modeling_separates_proposal_from_writes() -> None:
    text = (SKILLS / "domain-modeling/SKILL.md").read_text(encoding="utf-8")
    assert "### 深掘りする衝突を選ぶ" in text
    assert "データ属性または所有者" in text
    assert "状態遷移" in text
    assert "外部APIまたは他コンテキストとの境界" in text
    assert "業務上の判断" in text
    assert "only after the user approves" in text
    assert "Do not create or edit a file until the user explicitly approves" in text
    assert "Create it only after explicit user approval" in text
    assert "名称変更だけ、または未決定の移行方式だけではADRを作らない" in text


def test_grilling_limits_frontier_to_important_decisions() -> None:
    text = (SKILLS / "grilling/SKILL.md").read_text(encoding="utf-8")
    assert "## Start by classifying decisions" in text
    assert "**Critical**" in text
    assert "**Blocking**" in text
    assert "**Assumption**" in text
    assert "Only Critical and Blocking decisions belong on the **frontier**" in text
    assert "user confirms the shared understanding" in text
