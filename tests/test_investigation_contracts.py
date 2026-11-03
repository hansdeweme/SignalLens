"""UI-1 contracts: identity, faithful projection, annotation/report revisions."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict
import json
from pathlib import Path

import pytest

from investigation_session import InvestigationSession, InvestigationState
from investigation_presenters import build_presentation
from investigation_reports import (create_report_snapshot, persist_report_snapshot,
                                   load_investigation, snapshot_is_current)


def structured_result():
    return {
        'full_text': 'Original forensic narrative', 'full_html': '<p>Original forensic narrative</p>',
        'overall_confidence': 'Low', 'sections': {'metadata': {'note': 'Declaration unverified'}},
        'reasoning_trace': {
            'decision': {'primary_hypothesis': 'localized_editing', 'dominant_pattern': 'localized_processing_inconclusive',
                         'confidence_tier': 'Low'},
            'hypothesis_assessments': [
                {'hypothesis_id': 'localized_editing', 'confidence_tier': 'Low', 'explanation': 'Mechanism not established',
                 'supporting_evidence': ['boundary:observation'], 'contradicting_evidence': ['sensor:camera'],
                 'moderating_evidence': ['metadata:camera'], 'contextual_evidence': [],
                 'limitations': ['Coverage limited'],
                 'evidence_details': {'boundary:observation': {'section': 'boundary', 'label': 'Boundary observation',
                     'lineage_reference': 'evidence:boundary', 'reliability': 'limited', 'interpretation': 'Regional observation'}}},
                {'hypothesis_id': 'synthetic_origin', 'confidence_tier': 'Inconclusive',
                 'supporting_evidence': [], 'contradicting_evidence': [], 'moderating_evidence': [], 'contextual_evidence': []},
            ],
            'confidence_policy': {'assessments': [{'hypothesis': 'localized_editing', 'tier': 'Low',
                'policy_rule': 'recorded_rule', 'rationale': ['Recorded explanation'],
                'reliability_limitations': ['Geometry unavailable']}]},
            'provenance_evidence': {'state': 'provenance_present_unverified', 'metadata_authenticity_verified': False},
            'pipeline_status': {'coverage': {'status': 'partial'}, 'stages': {'Region FFT': {
                'status': 'skipped', 'reason': 'No person mask', 'assign_attr': 'region_fft_payload'}}},
            'scorecard': {'suspicious_score': 5.4},
        },
    }


def completed(tmp_path, result=None):
    session = InvestigationSession.selected(tmp_path / 'image.jpg')
    invocation = session.begin_analysis('normal', {'screen_origin': False}, {}, tmp_path)
    assert session.complete(invocation, object(), result or structured_result())
    return session


def test_empty_unique_selection_and_same_image_investigations(tmp_path):
    empty = InvestigationSession()
    assert empty.state == InvestigationState.EMPTY
    with pytest.raises(ValueError):
        empty.begin_analysis('normal', {}, {}, tmp_path)
    a, b = [InvestigationSession.selected(tmp_path / 'a.jpg') for _ in range(2)]
    assert a.session_id != b.session_id
    assert a.image_path == b.image_path
    assert a.state == InvestigationState.IMAGE_SELECTED


def test_reanalysis_invocations_freeze_inputs_and_reject_every_old_terminal(tmp_path):
    session = InvestigationSession.selected(tmp_path / 'a.jpg')
    settings = {'profiles': {'normal': 1}}
    a = session.begin_analysis('normal', {'screen_origin': False}, settings, tmp_path)
    settings['profiles']['normal'] = 99
    b = session.begin_analysis('subject_based', {'screen_origin': True}, {}, tmp_path)
    assert a.analysis_id != b.analysis_id and a.output_dir != b.output_dir
    assert json.loads(a.settings_json)['profiles']['normal'] == 1
    assert not session.complete(a, None, structured_result())
    assert not session.fail(a, 'late error')
    assert session.complete(b, None, structured_result())
    assert session.result_id == b.analysis_id
    assert not session.fail(b, 'duplicate terminal')
    c = session.begin_analysis('normal', {}, {}, tmp_path)
    assert session.summary_data() is None and session.result_id is None
    assert session.fail(c, 'failure')
    assert session.state == InvestigationState.FAILED
    d = session.begin_analysis('normal', {}, {}, tmp_path)
    assert session.cancel() and not session.cancel()
    assert not session.complete(d, None, structured_result())


def test_presentation_preserves_hypotheses_roles_policy_sources_and_input(tmp_path):
    result = structured_result()
    original = deepcopy(result)
    session = completed(tmp_path, result)
    view = build_presentation(session, result)
    assert view == build_presentation(session, result)
    assert result == original
    assert [h.hypothesis_id for h in view.hypotheses] == ['localized_editing', 'synthetic_origin']
    assert view.hypotheses[0].confidence_tier == 'Low'
    assert view.hypotheses[1].confidence_tier == 'Inconclusive'
    assert view.hypotheses[0].confidence_policy_rule == 'recorded_rule'
    assert view.hypotheses[0].contextual_evidence == ()
    assert view.hypotheses[0].contradicting_evidence == ('sensor:camera',)
    assert {e.role for e in view.evidence} == {'supporting_evidence', 'contradicting_evidence', 'moderating_evidence'}
    item = view.evidence[0]
    assert (item.source_detector, item.lineage_reference, item.reliability) == ('boundary', 'evidence:boundary', 'limited')
    assert view.stages[0].status == 'skipped' and view.stages[0].reason == 'No person mask'
    assert view.coverage_status == 'partial'
    assert 'Geometry unavailable' in view.summary.limitations
    with pytest.raises(FrozenInstanceError):
        view.result_id = 'tampered'
    result['reasoning_trace']['decision']['confidence_tier'] = 'High'
    assert build_presentation(session).summary.confidence_tier == 'Low'


@pytest.mark.parametrize('verified,expected', [(True, 'verified'), (False, 'unverified'), (None, 'unknown'), ('true', 'unknown')])
def test_provenance_only_uses_explicit_verification_flag(tmp_path, verified, expected):
    result = structured_result()
    result['reasoning_trace']['provenance_evidence']['metadata_authenticity_verified'] = verified
    assert build_presentation(completed(tmp_path, result)).provenance.verification_status == expected


@pytest.mark.parametrize('data', [{}, {'overall_text': 'High confidence AI-generated'}, {'reasoning_trace': None},
                                  {'reasoning_trace': {'hypothesis_assessments': 'not a list'}}])
def test_missing_structured_fields_are_unknown_not_parsed_from_narrative(tmp_path, data):
    session = completed(tmp_path)
    view = build_presentation(session, data)
    assert view.summary.primary_hypothesis is None
    assert view.summary.confidence_tier is None
    assert view.hypotheses == () and view.evidence == ()
    assert view.provenance.verification_status == 'unknown'


def test_missing_role_differs_from_empty_role_and_policy_is_authoritative(tmp_path):
    result = structured_result()
    del result['reasoning_trace']['hypothesis_assessments'][0]['contradicting_evidence']
    result['reasoning_trace']['hypothesis_assessments'][0]['confidence_tier'] = 'High'
    view = build_presentation(completed(tmp_path, result))
    assert view.hypotheses[0].contradicting_evidence is None
    assert view.hypotheses[0].confidence_tier == view.summary.confidence_tier == 'Low'


def test_annotation_revisions_freeze_forensics_and_invalidate_old_report(tmp_path):
    session = completed(tmp_path)
    frozen = session.summary_json
    old = create_report_snapshot(session)
    first = persist_report_snapshot(session, old, tmp_path / 'reports')
    assert session.report_current
    for n in range(3):
        assert session.commit_annotations({'notes': f'edit {n}'})
        assert session.annotation_revision == n+1
        assert not session.report_current
        assert not snapshot_is_current(session, old)
        with pytest.raises(ValueError, match='stale'):
            persist_report_snapshot(session, old, tmp_path / 'reports')
    assert session.summary_json == frozen
    assert not session.commit_annotations({'notes': 'edit 2'})
    current = create_report_snapshot(session)
    paths = persist_report_snapshot(session, current, tmp_path / 'reports')
    payload = json.loads(Path(paths['final_summary_json']).read_text(encoding='utf-8'))
    assert payload['annotations']['notes'] == 'edit 2'
    assert payload['investigation']['annotation_revision'] == 3
    assert payload['reasoning_trace'] == json.loads(frozen)['reasoning_trace']
    assert Path(first['final_summary_json']).is_file()
    assert 'edit 2' in Path(paths['final_summary_txt']).read_text(encoding='utf-8')
    assert 'edit 2' in Path(paths['final_summary_html']).read_text(encoding='utf-8')
    other = completed(tmp_path)
    assert not snapshot_is_current(other, current)


def test_export_running_or_failed_is_rejected(tmp_path):
    session = InvestigationSession.selected(tmp_path / 'a.jpg')
    invocation = session.begin_analysis('normal', {}, {}, tmp_path)
    for state in (InvestigationState.ANALYZING, InvestigationState.FAILED):
        session.state = state
        with pytest.raises(ValueError, match='completed'):
            create_report_snapshot(session)


def test_failed_bundle_does_not_publish_new_pointer(tmp_path, monkeypatch):
    import investigation_reports as reports
    session = completed(tmp_path)
    paths = persist_report_snapshot(session, create_report_snapshot(session), tmp_path)
    pointer = Path(paths['current_report'])
    before = pointer.read_bytes()
    session.commit_annotations({'notes': 'new'})
    monkeypatch.setattr(reports, 'persist_reasoning_trace_text', lambda *args: (_ for _ in ()).throw(OSError('disk full')))
    with pytest.raises(OSError, match='disk full'):
        persist_report_snapshot(session, create_report_snapshot(session), tmp_path)
    assert pointer.read_bytes() == before
    assert not session.report_current


def test_new_report_load_preserves_forensic_fields_and_does_not_reappend_old_annotations(tmp_path):
    from osint_reverse_search import create_empty_osint_result
    source = tmp_path / 'a.jpg'
    source.write_bytes(b'input')
    session = completed(tmp_path)
    session.image_path = str(source)
    annotations = create_empty_osint_result(source)
    annotations.analyst_notes.append('Recorded analyst note')
    session.commit_annotations(annotations)
    paths = persist_report_snapshot(session, create_report_snapshot(session), tmp_path / 'run')
    imported = load_investigation(paths['current_report'])
    assert imported.session_id != session.session_id
    assert imported.invocation is None and imported.annotation_revision == 0
    assert imported.summary_data() == session.summary_data()
    assert json.loads(imported.annotations_json)['analyst_notes'] == ['Recorded analyst note']
    assert json.loads(imported.historical_identity_json)['annotation_revision'] == 1
    assert create_report_snapshot(imported).payload()['full_text'].count('Current OSINT annotations') == 1


def test_legacy_import_has_explicit_fresh_identity_and_no_source_writes(tmp_path):
    summary = tmp_path / 'summary' / 'final_summary.json'
    summary.parent.mkdir()
    summary.write_text(json.dumps(structured_result()), encoding='utf-8')
    before = summary.read_bytes()
    a, b = load_investigation(summary), load_investigation(summary)
    assert a.session_id != b.session_id
    assert a.historical_identity_json is None and a.image_path is None
    assert a.summary_data() == structured_result()
    assert summary.read_bytes() == before


@pytest.mark.parametrize('data', ['broken json', '[]', '{"sections": []}', '{"full_html": 42}'])
def test_corrupted_import_is_rejected(tmp_path, data):
    path = tmp_path / 'bad.json'
    path.write_text(data, encoding='utf-8')
    with pytest.raises((ValueError, TypeError)):
        load_investigation(path)


def test_object_and_persisted_presentation_match(tmp_path):
    from types import SimpleNamespace
    from dataclasses import make_dataclass
    data = structured_result()
    # The adapter supports the existing dataclass convention as well as JSON.
    Result = make_dataclass('Result', [(key, object) for key in data])
    session = completed(tmp_path, data)
    assert build_presentation(session, Result(**data)) == build_presentation(session, data)


def test_partial_trace_report_exports_recorded_data_without_mutating_it(tmp_path):
    session = completed(tmp_path, {'full_html': '<p>Legacy</p>', 'reasoning_trace': {'decision': {'confidence_tier': 'Low'}}})
    original = session.summary_json
    paths = persist_report_snapshot(session, create_report_snapshot(session), tmp_path)
    assert session.report_current and session.summary_json == original
    assert 'recorded data follows' in Path(paths['reasoning_trace_txt']).read_text(encoding='utf-8')
