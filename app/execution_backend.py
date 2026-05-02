from typing import Any, Dict

from app.report_builder import build_doc
from app.staged_pipeline import run_staged_pipeline


class ExecutionBackend:
    def build_report(self, submission_id: int, submission_data: Dict[str, Any], force: bool = False) -> bytes:
        raise NotImplementedError


class LegacyBackend(ExecutionBackend):
    def build_report(self, submission_id: int, submission_data: Dict[str, Any], force: bool = False) -> bytes:
        return build_doc(submission_data, submission_id, force=force)


class StagedBackend(ExecutionBackend):
    def build_report(self, submission_id: int, submission_data: Dict[str, Any], force: bool = False) -> bytes:
        return run_staged_pipeline(submission_id, submission_data, force=force)
