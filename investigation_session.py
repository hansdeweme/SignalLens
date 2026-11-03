"""Qt-free investigation identity, lifecycle and revision ownership.

Raw detector state is held by reference, never copied. Compact structured summary
and annotation snapshots are stored as JSON so callers cannot mutate the truth
through a widget or a nested mutable dictionary.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_snapshot(value: Any) -> str:
    def convert(item):
        if is_dataclass(item):
            return asdict(item)
        if isinstance(item, Path):
            return str(item)
        raise TypeError(f'Unsupported snapshot value: {type(item).__name__}')
    return json.dumps(value, default=convert, sort_keys=True, ensure_ascii=False, allow_nan=False)


class InvestigationState(str, Enum):
    EMPTY = 'empty'
    IMAGE_SELECTED = 'image_selected'
    ANALYZING = 'analyzing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass(frozen=True)
class AnalysisInvocation:
    session_id: str
    analysis_id: str
    image_path: str
    profile: str
    scene_context: tuple[tuple[str, bool], ...]
    settings_json: str
    annotations_json: str
    annotation_revision: int
    output_dir: str
    started_at: str = field(default_factory=utc_now)
    source_sha256: str | None = None


@dataclass
class InvestigationSession:
    session_id: str = field(default_factory=lambda: uuid4().hex)
    image_path: str | None = None
    state: InvestigationState = InvestigationState.EMPTY
    invocation: AnalysisInvocation | None = None
    analysis_revision: int = 0
    annotation_revision: int = 0
    result_id: str | None = None
    analysis_result: Any = field(default=None, repr=False)
    summary_json: str | None = field(default=None, repr=False)
    annotations_json: str = 'null'
    report_revision: tuple[str, int] | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    imported_from: str | None = None
    historical_identity_json: str | None = None
    error: str | None = None
    source_sha256: str | None = None

    @classmethod
    def selected(cls, path: str | Path, annotations=None) -> InvestigationSession:
        frozen = json_snapshot(annotations)
        data = json.loads(frozen)
        return cls(image_path=str(Path(path).resolve()), state=InvestigationState.IMAGE_SELECTED,
                   annotations_json=frozen,
                   source_sha256=data.get('image_sha256') if isinstance(data, dict) else None)

    def begin_analysis(self, profile: str, scene_context: dict, settings: dict,
                       output_root: str | Path) -> AnalysisInvocation:
        if not self.image_path or self.state == InvestigationState.EMPTY:
            raise ValueError('Select an image before analysis.')
        if self.state == InvestigationState.ANALYZING:
            self.cancel()  # logical supersession only; owner retains the worker
        analysis_id = uuid4().hex
        invocation = AnalysisInvocation(
            self.session_id, analysis_id, self.image_path, profile,
            tuple(sorted((k, bool(v)) for k, v in scene_context.items())),
            json_snapshot(settings), self.annotations_json, self.annotation_revision,
            str(Path(output_root).resolve() / Path(self.image_path).stem / self.session_id / analysis_id),
            source_sha256=self.source_sha256,
        )
        self.invocation = invocation
        self.state = InvestigationState.ANALYZING
        self.analysis_result = self.summary_json = self.result_id = None
        self.report_revision = None
        self.error = None
        self.updated_at = utc_now()
        return invocation

    def accepts(self, invocation: AnalysisInvocation) -> bool:
        return (self.state == InvestigationState.ANALYZING
                and invocation == self.invocation and invocation.session_id == self.session_id)

    def complete(self, invocation: AnalysisInvocation, result: Any, summary: Any) -> bool:
        if not self.accepts(invocation):
            return False
        frozen = json_snapshot(summary)  # validate before publishing a result
        self.analysis_result = result
        self.summary_json = frozen
        self.analysis_revision += 1
        self.result_id = invocation.analysis_id
        self.state = InvestigationState.COMPLETED
        self.report_revision = None
        self.updated_at = utc_now()
        return True

    def fail(self, invocation: AnalysisInvocation, message: str) -> bool:
        if not self.accepts(invocation):
            return False
        self.state = InvestigationState.FAILED
        self.error = message
        self.report_revision = None
        self.updated_at = utc_now()
        return True

    def cancel(self) -> bool:
        if self.state != InvestigationState.ANALYZING:
            return False
        self.state = InvestigationState.CANCELLED
        self.report_revision = None
        self.updated_at = utc_now()
        return True

    def commit_annotations(self, annotations: Any) -> bool:
        frozen = json_snapshot(annotations)
        if frozen == self.annotations_json:
            return False
        self.annotations_json = frozen
        self.annotation_revision += 1
        self.report_revision = None
        self.updated_at = utc_now()
        return True

    @property
    def revision_key(self) -> tuple[str, int] | None:
        return (self.result_id, self.annotation_revision) if self.result_id else None

    @property
    def report_current(self) -> bool:
        return self.revision_key is not None and self.report_revision == self.revision_key

    def summary_data(self) -> dict | None:
        return json.loads(self.summary_json) if self.summary_json else None
