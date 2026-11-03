"""Pure projections of recorded fields; no engine imports or narrative parsing."""
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from pathlib import Path
import json

from investigation_session import InvestigationSession
from presentation_models import (
    EvidenceView, HypothesisView, InvestigationSummaryView,
    InvestigationViewSnapshot, ProvenanceView, StageView, SourceIdentityView,
)


def mapping(value):
    if is_dataclass(value):
        return asdict(value)
    return value if isinstance(value, Mapping) else {}


def records(value):
    return value if isinstance(value, (list, tuple)) else ()


def strings(value):
    return tuple(item for item in records(value) if isinstance(item, str))


def optional_roles(data, key):
    return strings(data[key]) if isinstance(data.get(key), (list, tuple)) else None


def build_presentation(session: InvestigationSession, result=None) -> InvestigationViewSnapshot:
    data = mapping(result) if result is not None else mapping(session.summary_data())
    trace = mapping(data.get('reasoning_trace'))
    decision = mapping(trace.get('decision'))
    policy = mapping(trace.get('confidence_policy'))
    policies = {p['hypothesis']: p for item in records(policy.get('assessments'))
                if (p := mapping(item)) and isinstance(p.get('hypothesis'), str)}
    hypotheses, evidence = [], []
    for item in records(trace.get('hypothesis_assessments')):
        h = mapping(item)
        hid = h.get('hypothesis_id')
        if not isinstance(hid, str):
            continue
        p = policies.get(hid, {})
        hypotheses.append(HypothesisView(
            hid, h.get('explanation'), p.get('tier', h.get('confidence_tier')),
            *(optional_roles(h, role) for role in ('supporting_evidence', 'contradicting_evidence', 'moderating_evidence', 'contextual_evidence')),
            strings(h.get('limitations')) + strings(p.get('reliability_limitations')),
            p.get('policy_rule', h.get('confidence_policy_rule')),
            strings(p.get('rationale', h.get('confidence_rationale'))),
        ))
        details = mapping(h.get('evidence_details'))
        for role in ('supporting_evidence', 'contradicting_evidence', 'moderating_evidence', 'contextual_evidence'):
            for eid in strings(h.get(role)):
                detail = mapping(details.get(eid))
                evidence.append(EvidenceView(eid, hid, detail.get('label'), role,
                    detail.get('reliability'), detail.get('section'),
                    detail.get('lineage_reference'), detail.get('interpretation')))
    primary = decision.get('primary_hypothesis')
    primary_view = next((h for h in hypotheses if h.hypothesis_id == primary), None)
    primary_policy = policies.get(primary, {})
    pipeline = mapping(trace.get('pipeline_status'))
    coverage = mapping(pipeline.get('coverage'))
    stages = tuple(StageView(name, s.get('status'), s.get('reason'), s.get('assign_attr'))
                   for name, raw in mapping(pipeline.get('stages')).items()
                   if (s := mapping(raw)))
    provenance = mapping(trace.get('provenance_evidence'))
    verified = provenance.get('metadata_authenticity_verified')
    return InvestigationViewSnapshot(
        session.session_id, session.invocation.analysis_id if session.invocation else None,
        session.analysis_revision, session.annotation_revision, session.result_id,
        InvestigationSummaryView(session.session_id, Path(session.image_path).name if session.image_path else None,
            primary, decision.get('dominant_pattern'),
            primary_policy.get('tier', decision.get('confidence_tier')),
            session.state.value, primary_view.limitations if primary_view else strings(decision.get('limitations'))),
        tuple(hypotheses), tuple(evidence),
        ProvenanceView(provenance.get('state'), 'verified' if verified is True else 'unverified' if verified is False else 'unknown',
                       mapping(mapping(data.get('sections')).get('metadata')).get('note'), ()),
        coverage.get('status'), stages, session.annotations_json,
        session.invocation.annotation_revision if session.invocation else None,
        SourceIdentityView(session.image_path, session.source_sha256,
            session.invocation.profile if session.invocation else
            mapping(json.loads(session.historical_identity_json)).get('profile') if session.historical_identity_json else None,
            bool(session.imported_from), session.error),
    )
