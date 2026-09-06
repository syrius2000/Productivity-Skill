from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = REPOSITORY_ROOT / ".agents/skills/quality-review/bin/quality-review-cli"


def run_cli(case_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(LAUNCHER), "--case-root", str(case_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def result_of(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout)


class QualityReviewStandaloneCliTest(unittest.TestCase):
    def test_help_exposes_standalone_entrypoint_and_aliases(self) -> None:
        completed = subprocess.run(
            [str(LAUNCHER), "review-standalone", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("--target", completed.stdout)
        self.assertIn("--artifact", completed.stdout)
        self.assertIn("--owner", completed.stdout)

    def test_bootstrap_then_formal_review_returns_owner_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "Implementation_agy_001.md"
            target.write_text("# 実装結果\n\n確認対象です。\n", encoding="utf-8")
            before = hashlib.sha256(target.read_bytes()).hexdigest()
            case_root = root / "cases"

            boot = run_cli(
                case_root,
                "review-standalone",
                "--artifact",
                str(target),
                "--owner",
                "owner-yamaguchi",
            )
            self.assertEqual(0, boot.returncode, boot.stderr)
            boot_result = result_of(boot)
            self.assertEqual("review-standalone", boot_result["entrypoint"])
            self.assertEqual(1, boot_result["case_revision"])
            self.assertEqual("reviewer", boot_result["next_role"])
            self.assertEqual("review", boot_result["next_action"])
            self.assertEqual([str(target.absolute())], boot_result["review_context"]["targets"])

            case_path = case_root / boot_result["case_id"] / "case.json"
            case = json.loads(case_path.read_text(encoding="utf-8"))
            self.assertEqual("reviewer-action", case["case_metadata"]["status"])
            self.assertEqual(
                {"allowed": False, "finding_ids": [], "allowed_targets": []},
                case["implementation_authorization"],
            )
            self.assertEqual("generated-minimum", boot_result["review_context"]["baseline_source"])
            self.assertIn(
                "原要求・原受入基準が未提示の場合、ドメイン適合や受入を判定しない",
                case["baseline"]["exclusions"],
            )

            review_input = root / "review.json"
            review_input.write_text(
                json.dumps(
                    {
                        "operation_id": "review-standalone-test-001",
                        "actor_id": "reviewer-test",
                        "role": "reviewer",
                        "invocation_id": "reviewer-invocation-001",
                        "previous_handoff_id": boot_result["handoff"]["handoff_id"],
                        "expected_case_revision": 1,
                        "findings": [],
                        "evidence": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            reviewed = run_cli(
                case_root,
                "review",
                "--case-id",
                boot_result["case_id"],
                "--input",
                str(review_input),
            )
            self.assertEqual(0, reviewed.returncode, reviewed.stderr)
            reviewed_result = result_of(reviewed)
            self.assertEqual(2, reviewed_result["case_revision"])
            self.assertEqual("owner", reviewed_result["next_role"])
            self.assertEqual("adjudicate", reviewed_result["next_action"])
            self.assertEqual(before, hashlib.sha256(target.read_bytes()).hexdigest())

    def test_high_finding_from_standalone_case_uses_formal_plan_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "artifact.md"
            target.write_text("# 対象\n", encoding="utf-8")
            case_root = root / "cases"
            boot = result_of(
                run_cli(
                    case_root,
                    "review-standalone",
                    "--target",
                    str(target),
                    "--owner",
                    "owner-001",
                    "--case-id",
                    "standalone-test-001",
                )
            )
            review_input = root / "review.json"
            review_input.write_text(
                json.dumps(
                    {
                        "operation_id": "review-standalone-test-002",
                        "actor_id": "reviewer-001",
                        "role": "reviewer",
                        "invocation_id": "reviewer-invocation-002",
                        "previous_handoff_id": boot["handoff"]["handoff_id"],
                        "expected_case_revision": 1,
                        "findings": [
                            {
                                "finding_id": "F-001",
                                "classification": "requirement-violation",
                                "severity": "high",
                                "requirement_ref": "STANDALONE-SCOPE-001",
                                "observed_fact": "確認Evidenceがない",
                                "impact": "第三者が結果を再確認できない",
                                "expected_state": "確認可能なEvidenceがある",
                                "verification_method": "Evidence参照を確認する",
                                "evidence_refs": [],
                            }
                        ],
                        "evidence": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            reviewed = run_cli(
                case_root,
                "review",
                "--case-id",
                "standalone-test-001",
                "--input",
                str(review_input),
            )
            self.assertEqual(0, reviewed.returncode, reviewed.stderr)
            reviewed_result = result_of(reviewed)
            self.assertEqual("implementer", reviewed_result["next_role"])
            self.assertEqual("submit-plan", reviewed_result["next_action"])
            self.assertEqual(["F-001"], reviewed_result["handoff"]["open_items"])

    def test_custom_baseline_and_repeated_bootstrap_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "artifact.md"
            target.write_text("# 対象\n", encoding="utf-8")
            case_root = root / "cases"
            baseline_path = root / "baseline.json"
            baseline_path.write_text(
                json.dumps(
                    {
                        "purpose": "実装結果の文書QA",
                        "intended_use": {"users": "開発者", "environment": "ローカル"},
                        "risk_context": {"criticality": "medium"},
                        "requirements": [{"requirement_id": "REQ-001", "text": "記載がある"}],
                        "acceptance_criteria": ["記載を確認できる"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            arguments = (
                "review-standalone",
                "--target",
                str(target),
                "--owner",
                "owner-001",
                "--baseline-input",
                str(baseline_path),
            )
            first = run_cli(case_root, *arguments)
            second = run_cli(case_root, *arguments)
            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual(0, second.returncode, second.stderr)
            first_result = result_of(first)
            second_result = result_of(second)
            self.assertEqual(first_result["case_id"], second_result["case_id"])
            self.assertEqual("already-processed", second_result["status"])
            self.assertEqual(1, second_result["case_revision"])
            case = json.loads(
                (case_root / first_result["case_id"] / "case.json").read_text(encoding="utf-8")
            )
            self.assertEqual("実装結果の文書QA", case["baseline"]["purpose"])
            self.assertEqual("medium", case["baseline"]["risk_context"]["criticality"])

    def test_invalid_target_and_existing_case_mismatch_do_not_create_or_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_root = root / "cases"
            missing = root / "missing.md"
            failed = run_cli(
                case_root,
                "review-standalone",
                "--target",
                str(missing),
                "--owner",
                "owner-001",
            )
            self.assertEqual(3, failed.returncode)
            self.assertEqual("manifest-target-not-found", result_of(failed)["error_code"])
            self.assertFalse(case_root.exists())

            first_target = root / "first.md"
            second_target = root / "second.md"
            first_target.write_text("first\n", encoding="utf-8")
            second_target.write_text("second\n", encoding="utf-8")
            first = run_cli(
                case_root,
                "review-standalone",
                "--target",
                str(first_target),
                "--owner",
                "owner-001",
                "--case-id",
                "explicit-case-001",
            )
            self.assertEqual(0, first.returncode, first.stderr)
            mismatch = run_cli(
                case_root,
                "review-standalone",
                "--target",
                str(second_target),
                "--owner",
                "owner-001",
                "--case-id",
                "explicit-case-001",
            )
            self.assertEqual(3, mismatch.returncode)
            self.assertEqual("standalone-case-mismatch", result_of(mismatch)["error_code"])


if __name__ == "__main__":
    unittest.main()
