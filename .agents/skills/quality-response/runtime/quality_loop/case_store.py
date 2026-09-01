from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator

import fcntl

from .errors import QualityLoopError


class CaseStore:
    def __init__(self, case_root: Path) -> None:
        self.case_root = Path(case_root).resolve()

    def case_dir(self, case_id: str) -> Path:
        return self.case_root / case_id

    def case_path(self, case_id: str) -> Path:
        return self.case_dir(case_id) / "case.json"

    def create(self, case_id: str, case: dict) -> None:
        self.case_root.mkdir(parents=True, exist_ok=True)
        case_dir = self.case_dir(case_id)
        try:
            case_dir.mkdir(parents=False, exist_ok=False)
        except FileExistsError as exc:
            raise QualityLoopError(
                "case-already-exists",
                f"案件 {case_id} は既に存在します。",
                remediation="別のcase_idを指定してください。",
            ) from exc
        try:
            (case_dir / "evidence").mkdir()
            self._atomic_write_json(self.case_path(case_id), case)
        except OSError as exc:
            raise QualityLoopError(
                "case-create-failed",
                f"案件 {case_id} の正本を作成できませんでした。",
                exit_code=4,
                remediation="案件ディレクトリの権限と空き容量を確認してください。",
            ) from exc

    def load(self, case_id: str) -> dict:
        path = self.case_path(case_id)
        try:
            with path.open(encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError as exc:
            raise QualityLoopError(
                "case-not-found",
                f"案件 {case_id} が見つかりません。",
                exit_code=3,
                remediation="case_idとcase-rootを確認してください。",
            ) from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise QualityLoopError(
                "case-unreadable",
                f"案件 {case_id} の正本を読み取れません。",
                exit_code=3,
                remediation="case.jsonの存在、権限、JSON整合性を確認してください。",
            ) from exc

    def list_cases(self) -> list[str]:
        if not self.case_root.is_dir():
            return []
        cases = []
        for child in sorted(self.case_root.iterdir()):
            if child.is_dir() and (child / "case.json").is_file():
                cases.append(child.name)
        return cases

    def list_active_cases(self) -> list[str]:
        active = []
        for case_id in self.list_cases():
            try:
                data = self.load(case_id)
                status = data.get("case_metadata", {}).get("status")
                if status not in {"accepted", "accepted-with-risk", "rejected", "held"}:
                    active.append(case_id)
            except Exception:
                continue
        return active

    def init_case(self, case_id: str, case: dict) -> None:
        self.create(case_id, case)

    def mutate(
        self,
        case_id: str,
        mutation: Callable[[dict], tuple[dict | None, dict]],
    ) -> dict:
        with self._exclusive_lock(case_id):
            current = self.load(case_id)
            updated, result = mutation(current)
            if updated is None:
                return result
            try:
                self._atomic_write_json(
                    self.case_dir(case_id) / "case.json.bak", current
                )
            except OSError as exc:
                raise QualityLoopError(
                    "case-backup-failed",
                    "更新前の正本バックアップを保存できませんでした。",
                    exit_code=4,
                    remediation="case.jsonは未更新です。権限と空き容量を確認してください。",
                ) from exc
            try:
                self._atomic_write_json(self.case_path(case_id), updated)
            except OSError as exc:
                raise QualityLoopError(
                    "case-write-failed",
                    "案件正本の更新に失敗しました。",
                    exit_code=4,
                    remediation="case.jsonは前revisionのままです。case.json.bakも確認してください。",
                ) from exc
            persisted = self.load(case_id)
            target_rev = result.get("case_revision", result.get("rev"))
            if target_rev is not None:
                persisted_rev = persisted.get("case_metadata", {}).get("case_revision", persisted.get("case_metadata", {}).get("revision"))
                if persisted_rev != target_rev:
                    raise QualityLoopError(
                        "post-write-verification-failed",
                        "更新後のrevisionを確認できません。",
                        exit_code=4,
                        remediation="case.jsonとcase.json.bakを確認してください。",
                    )
            return result

    @contextmanager
    def _exclusive_lock(self, case_id: str) -> Iterator[None]:
        case_dir = self.case_dir(case_id)
        if not case_dir.is_dir():
            raise QualityLoopError(
                "case-not-found",
                f"案件 {case_id} が見つかりません。",
                exit_code=3,
                remediation="case_idとcase-rootを確認してください。",
            )
        lock_path = case_dir / ".case.lock"
        try:
            lock_handle = lock_path.open("a+")
        except OSError as exc:
            raise QualityLoopError(
                "case-backup-failed",
                "案件ディレクトリへの書込み権限がありません。",
                exit_code=4,
            ) from exc

        with lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
                # ロックファイルは削除しない。排他待ちの別プロセスが同じ
                # inodeを保持している間にパスをunlinkすると、後続プロセスが
                # 別inodeを作成して排他制御を分裂させるためである。

    @staticmethod
    def _atomic_write_json(path: Path, payload: dict) -> None:
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
            temporary_path = None
            directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            directory_fd = os.open(path.parent, directory_flags)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass

    @staticmethod
    def atomic_write_text(path: Path, text: str) -> None:
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass
