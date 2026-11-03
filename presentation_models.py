"""Immutable, Qt-free UI contracts. None means not recorded, never negative."""
from dataclasses import dataclass


@dataclass(frozen=True)
class InvestigationSummaryView:
    session_id: str
    image_name: str | None
    primary_hypothesis: str | None
    primary_finding: str | None
    confidence_tier: str | None
    status: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class HypothesisView:
    hypothesis_id: str
    finding: str | None
    confidence_tier: str | None
    supporting_evidence: tuple[str, ...] | None
    contradicting_evidence: tuple[str, ...] | None
    moderating_evidence: tuple[str, ...] | None
    contextual_evidence: tuple[str, ...] | None
    limitations: tuple[str, ...]
    confidence_policy_rule: str | None
    confidence_rationale: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceView:
    evidence_id: str
    hypothesis_id: str
    label: str | None
    role: str
    reliability: str | None
    source_detector: str | None
    lineage_reference: str | None
    interpretation: str | None


@dataclass(frozen=True)
class ProvenanceView:
    declaration_status: str | None
    verification_status: str  # verified / unverified / unknown; explicit boolean only
    description: str | None
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class StageView:
    stage_id: str
    status: str | None
    reason: str | None
    detector: str | None


@dataclass(frozen=True)
class InvestigationViewSnapshot:
    session_id: str
    analysis_id: str | None
    analysis_revision: int
    annotation_revision: int
    result_id: str | None
    summary: InvestigationSummaryView
    hypotheses: tuple[HypothesisView, ...]
    evidence: tuple[EvidenceView, ...]
    provenance: ProvenanceView
    coverage_status: str | None
    stages: tuple[StageView, ...]
    annotations_json: str
    analysis_annotation_revision: int | None
