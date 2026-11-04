"""Immutable UI-5 projections; no scoring, routing or confidence calculations."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ExplorerIdentity:
    session_id: str
    analysis_id: str | None
    result_id: str | None
    analysis_revision: int
    status: str


@dataclass(frozen=True)
class EvidenceDetailView:
    evidence_id: str
    hypothesis_id: str
    role: str
    label: str
    detector_id: str | None
    reliability: str | None
    availability: str | None
    observation: str
    interpretation: str | None
    limitations: tuple[str, ...]
    lineage_id: str | None
    artifact_ids: tuple[str, ...]
    fields: tuple[tuple[str, str], ...]

    @property
    def key(self):
        return self.hypothesis_id, self.role, self.evidence_id


@dataclass(frozen=True)
class LineageNodeView:
    node_id: str
    family: str | None
    kind: str | None
    parents: tuple[str, ...]
    optional_parents: tuple[str, ...]
    measurements: tuple[str, ...]
    status: str | None
    origin: str


@dataclass(frozen=True)
class AuditRecordView:
    record_id: str
    title: str
    hypothesis_id: str | None
    outcome: str | None
    explanation: str | None
    fields: tuple[tuple[str, str], ...]
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScoreContributionView:
    evidence_id: str
    section: str | None
    polarity: str | None
    raw: str | None
    credited: str | None
    reliability_multiplier: str | None
    final: str | None
    suppressed: str | None
    classification: str | None
    reason: str | None
    fields: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ExplorerSnapshot:
    identity: ExplorerIdentity
    evidence: tuple[EvidenceDetailView, ...]
    lineage: tuple[LineageNodeView, ...]
    hypotheses: tuple[AuditRecordView, ...]
    routes: tuple[AuditRecordView, ...]
    corroboration: tuple[AuditRecordView, ...]
    confidence: tuple[AuditRecordView, ...]
    contributions: tuple[ScoreContributionView, ...]
    score_records: tuple[AuditRecordView, ...]
    score_summary: str
    primary_hypothesis: str | None
    primary_finding: str | None
    coverage: str | None
    issues: tuple[str, ...]
    raw_trace: str
