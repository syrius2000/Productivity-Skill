from __future__ import annotations

import hashlib
import subprocess
from copy import deepcopy
from pathlib import Path

from .errors import QualityLoopError


def compute_file_manifest(scope_paths: list[str]) -> dict[str, str]:
    """指定済みの有限ファイル集合をSHA-256で記録する。

    対象集合は呼出し側が明示する。存在しないファイルや読取り不能なファイルを
    Evidenceとして黙って省略せず、安全側へ停止する。
    """
    if not isinstance(scope_paths, list) or not scope_paths or any(
        not isinstance(item, str) or not item for item in scope_paths
    ):
        raise QualityLoopError(
            "invalid-manifest-targets",
            "有限manifestには空でないファイルパス配列が必要です。",
            exit_code=3,
        )

    manifest: dict[str, str] = {}
    for path_str in sorted(set(scope_paths)):
        path = Path(path_str)
        if not path.is_file():
            raise QualityLoopError(
                "manifest-target-not-found",
                f"manifest対象ファイルが見つかりません: {path_str}",
                exit_code=3,
                remediation="対象パスを確認し、削除済みファイルはGit観測で確認してください。",
            )
        try:
            manifest[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise QualityLoopError(
                "manifest-target-unreadable",
                f"manifest対象ファイルを読み取れません: {path_str}",
                exit_code=3,
            ) from exc
    return manifest


def build_file_manifest(root: Path, targets: list[str]) -> dict:
    """Owner指定のroot配下の有限相対パスをmanifest化する互換API。"""
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise QualityLoopError(
            "manifest-root-not-found",
            "有限manifestの対象ディレクトリが見つかりません。",
            exit_code=3,
            remediation="rootを確認してください。",
        )
    if not isinstance(targets, list) or not targets or any(
        not isinstance(target, str) or not target or Path(target).is_absolute()
        for target in targets
    ):
        raise QualityLoopError(
            "invalid-manifest-targets",
            "有限manifestには空でない相対パス配列が必要です。",
            exit_code=3,
        )

    records: list[dict[str, str]] = []
    for target in sorted(set(targets)):
        candidate = (root_path / target).resolve()
        try:
            candidate.relative_to(root_path)
        except ValueError as exc:
            raise QualityLoopError(
                "manifest-path-outside-root",
                f"manifest対象がroot外です: {target}",
                exit_code=3,
                remediation="root配下の相対パスだけを指定してください。",
            ) from exc
        if not candidate.is_file():
            raise QualityLoopError(
                "manifest-target-not-found",
                f"manifest対象ファイルが見つかりません: {target}",
                exit_code=3,
                remediation="対象パスを確認してください。",
            )
        try:
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        except OSError as exc:
            raise QualityLoopError(
                "manifest-target-unreadable",
                f"manifest対象ファイルを読み取れません: {target}",
                exit_code=3,
            ) from exc
        records.append({"path": candidate.relative_to(root_path).as_posix(), "sha256": digest})

    return {
        "method": "finite-manifest",
        "scope": [item["path"] for item in records],
        "files": records,
        "limitations": [
            "Ownerが指定した有限ファイル集合だけを対象とする",
            "未指定ファイル、削除済みファイル、外部サービスの変更は観測範囲外である",
        ],
    }


def detect_manifest_changes(
    before_manifest: dict[str, str],
    after_manifest: dict[str, str],
) -> tuple[list[str], list[str], list[str]]:
    before_keys = set(before_manifest)
    after_keys = set(after_manifest)
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    changed = sorted(
        key for key in before_keys & after_keys if before_manifest[key] != after_manifest[key]
    )
    return changed, added, removed


def observe_git_changes(repo_root: Path, base_ref: str | None = None) -> dict:
    """明示されたbase_refとの差分をGitの読取り専用操作で観測する。

    ``git -C``を使用するため、通常のリポジトリだけでなく、.gitがファイルである
    worktreeも扱える。ignoredファイルとsubmodule内部は保証範囲に含めない。
    """
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise QualityLoopError(
            "git-repository-not-found",
            "Git観測対象のディレクトリが見つかりません。",
            exit_code=3,
        )
    if not isinstance(base_ref, str) or not base_ref.strip():
        raise QualityLoopError(
            "git-base-ref-required",
            "Git観測にはbase_refが必要です。",
            exit_code=3,
            remediation="比較するcommit、tag、またはrefを明示してください。",
        )

    try:
        changed = _git_paths(root, "diff", "--name-only", "-z", base_ref, "--")
        status_records = _git_status_records(root, base_ref)
        untracked = _git_paths(root, "ls-files", "--others", "--exclude-standard", "-z")
    except QualityLoopError:
        raise
    except (OSError, subprocess.SubprocessError) as exc:
        raise QualityLoopError(
            "git-execution-error",
            f"Gitコマンドの実行中にエラーが発生しました: {exc}",
            exit_code=4,
        ) from exc

    deleted = sorted({path for status, path in status_records if status == "D"})
    targets = sorted(set(changed) | set(untracked))
    return {
        "method": "git-readonly",
        "scope": targets,
        "observed_changed_targets": targets,
        "deleted_targets": deleted,
        "limitations": [
            "Gitが観測できる作業ツリーだけを対象とする",
            "ignored、submodule内部、外部サービスの変更は観測範囲外である",
            f"比較基準: {base_ref}",
        ],
    }


def validate_change_observation(
    observation: dict | None,
    declared_changed_targets: set[str],
    allowed_targets: set[str],
    available_evidence_ids: set[str],
) -> dict:
    if observation is None:
        if declared_changed_targets:
            raise QualityLoopError(
                "change-observation-required",
                "変更提出のverifyには独立change_observationが必要です。",
                remediation="Reviewerは独立した変更観測結果を登録してください。",
            )
        return {}
    if not isinstance(observation, dict):
        raise QualityLoopError("invalid-change-observation", "change_observationはobjectで指定してください。")

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
    obs_refs = {observation["before_evidence_id"], observation["after_evidence_id"]}
    if not obs_refs.issubset(available_evidence_ids):
        missing_ev = sorted(obs_refs - available_evidence_ids)
        raise QualityLoopError(
            "unknown-evidence-id",
            f"変更観測のEvidenceを確認できません: {', '.join(missing_ev)}",
        )

    observed = set(observation.get("observed_changed_targets", []))
    undeclared = sorted(observed - declared_changed_targets)
    if undeclared:
        raise QualityLoopError(
            "undeclared-change-detected",
            f"申告外変更を検出しました: {', '.join(undeclared)}",
            remediation="申告外変更を戻すか、Implementer提出を訂正してください。",
        )
    unauthorized = sorted(observed - allowed_targets)
    if unauthorized:
        raise QualityLoopError(
            "unauthorized-change-detected",
            f"許可外変更を検出しました: {', '.join(unauthorized)}",
            remediation="許可されていないファイルの変更を戻してください。",
        )
    unobserved = sorted(declared_changed_targets - observed)
    if unobserved:
        raise QualityLoopError(
            "change-observation-incomplete",
            f"申告された変更を観測できません: {', '.join(unobserved)}",
            remediation="観測範囲を補完するかunverifiedとして再提出してください。",
        )
    return deepcopy(observation)


def _git_paths(root: Path, *args: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
    )
    if completed.returncode:
        stderr = completed.stderr.decode(errors="replace").strip()
        raise QualityLoopError(
            "git-observation-failed",
            f"Git観測に失敗しました: {stderr}",
            exit_code=3,
            remediation="repo_rootとbase_refを確認してください。",
        )
    return [item.decode(errors="surrogateescape") for item in completed.stdout.split(b"\0") if item]


def _git_status_records(root: Path, base_ref: str) -> list[tuple[str, str]]:
    records = _git_paths(root, "diff", "--name-status", "-z", base_ref, "--")
    parsed: list[tuple[str, str]] = []
    index = 0
    while index < len(records):
        status = records[index]
        index += 1
        if status.startswith("R") or status.startswith("C"):
            if index + 1 >= len(records):
                break
            index += 1
            parsed.append((status[0], records[index]))
            index += 1
        elif index < len(records):
            parsed.append((status[0], records[index]))
            index += 1
    return parsed
