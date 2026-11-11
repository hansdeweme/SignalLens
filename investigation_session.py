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
import hashlib
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
    _synthesis_json: str | None = field(default=None, repr=False)
    _synthesis_key: tuple | None = field(default=None, repr=False)
    storage_dir: str | None = None

    def storage_directory(self, output_root):
        from investigation_storage import investigation_directory
        directory = investigation_directory(output_root, self.image_path or 'imported',
                                              self.source_sha256, self.session_id)
        self.storage_dir = str(directory)
        return directory

    @classmethod
    def selected(cls, path: str | Path, annotations=None) -> InvestigationSession:
        frozen = json_snapshot(annotations)
        data = json.loads(frozen)
        from osint_reverse_search import sha256_of_file
        source_hash = sha256_of_file(path) if Path(path).is_file() else data.get('image_sha256') if isinstance(data, dict) else None
        if isinstance(data, dict) and data.get('image_sha256') and source_hash and data['image_sha256'] != source_hash:
            raise ValueError('Source annotations belong to a different image SHA-256.')
        return cls(image_path=str(Path(path).resolve()), state=InvestigationState.IMAGE_SELECTED,
                   annotations_json=frozen,
                   source_sha256=source_hash)

    def begin_analysis(self, profile: str, scene_context: dict, settings: dict,
                       output_root: str | Path) -> AnalysisInvocation:
        if not self.image_path or self.state == InvestigationState.EMPTY:
            raise ValueError('Select an image before analysis.')
        if self.state == InvestigationState.ANALYZING:
            self.cancel()  # logical supersession only; owner retains the worker
        analysis_id = uuid4().hex
        from investigation_storage import allocate_run
        output = allocate_run(self.storage_directory(output_root), analysis_id,
                              self.source_sha256, self.session_id)
        invocation = AnalysisInvocation(
            self.session_id, analysis_id, self.image_path, profile,
            tuple(sorted((k, bool(v)) for k, v in scene_context.items())),
            json_snapshot(settings), self.annotations_json, self.annotation_revision,
            str(output),
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
        self.validate_annotations(json.loads(frozen))
        if frozen == self.annotations_json:
            return False
        self.annotations_json = frozen
        self.annotation_revision += 1
        self.report_revision = None
        self.updated_at = utc_now()
        return True

    def validate_annotations(self, annotations):
        data = json.loads(json_snapshot(annotations))
        if isinstance(data, dict) and data.get('image_sha256') and self.source_sha256 and data['image_sha256'] != self.source_sha256:
            raise ValueError('Source evidence belongs to a different image SHA-256.')

    def synthesis_key(self, data=None):
        from investigation_synthesis import POLICY_VERSION
        forensic = json_snapshot(self.summary_data() if data is None else data)
        health = hashlib.sha256(json_snapshot(self.verified_sources()).encode()).hexdigest()
        return (self.result_id, self.source_sha256, self.annotation_revision, POLICY_VERSION, health,
                hashlib.sha256(forensic.encode('utf-8')).hexdigest(),
                hashlib.sha256(self.annotations_json.encode('utf-8')).hexdigest())

    def verified_sources(self):
        from source_image_verification import validate
        notes = json.loads(self.annotations_json) or {}
        return {m['record_id']: record for m in notes.get('matches', [])
                if isinstance(m, dict) and (record := validate(m, self.source_sha256))}

    def investigation_synthesis(self, data=None):
        if self.state != InvestigationState.COMPLETED or not self.result_id:
            return None
        from investigation_synthesis import build_synthesis
        key = self.synthesis_key(data)
        if key != self._synthesis_key:
            if self._synthesis_key and key[4] != self._synthesis_key[4]:
                # Artifact integrity can change without an annotation edit.
                # Keep old report bytes historical, never call their pointer current.
                self.report_revision = None
                self.updated_at = utc_now()
            parent = json.loads(self._synthesis_json).get('revision_id') if self._synthesis_json else None
            record = build_synthesis(self.summary_data() if data is None else data,
                                     json.loads(self.annotations_json), self.source_sha256,
                                     verifications=self.verified_sources())
            historical = json.loads(self.historical_identity_json) if self.historical_identity_json else {}
            record.update(schema_version=1, image_sha256=self.source_sha256,
                forensic_snapshot_id=historical.get('result_id') or self.result_id,
                forensic_fingerprint=key[-2], osint_evidence_fingerprint=key[-1],
                osint_evidence_revision=self.annotation_revision,
                revision_id=hashlib.sha256(json_snapshot(key).encode()).hexdigest()[:24],
                revision_timestamp=self.updated_at, parent_revision_id=parent)
            self._synthesis_json, self._synthesis_key = json_snapshot(record), key
        return json.loads(self._synthesis_json)

    @property
    def revision_key(self) -> tuple[str, int] | None:
        return (self.result_id, self.annotation_revision) if self.result_id else None

    @property
    def report_current(self) -> bool:
        return self.revision_key is not None and self.report_revision == self.revision_key

    def summary_data(self) -> dict | None:
        return json.loads(self.summary_json) if self.summary_json else None
