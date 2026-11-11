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


def generation_result():
    from reasoning_helpers import comfy_graph
    from summary_sections import build_metadata_section
    graph = comfy_graph()
    graph['1']['inputs']['ckpt_name'] = 'flux.2-klein.safetensors'
    # A disconnected loader cannot corroborate a different family.
    graph['90'] = {'class_type': 'UNETLoader', 'inputs': {'unet_name': 'sdxl.safetensors'}}
    data = structured_result()
    data['sections']['metadata'] = asdict(build_metadata_section({'signals': [
        {'id': 'EMBEDDED_GENERATION_PROMPT', 'evidence': [
            {'raw_key': 'PNG:Prompt', 'group': 'PNG', 'tag': 'Prompt', 'value': json.dumps(graph)}]}]}))
    return data


def test_source_verification_receipt_revisions_and_stale_evidence(tmp_path, monkeypatch):
    """Gap: downloaded bytes, authenticated association and retained artifact health."""
    from source_verification_helpers import image_bytes, wire, response
    from source_image_verification import retrieve, retain, validate, digest
    from osint_reverse_search import create_empty_osint_result, add_manual_match
    source = tmp_path / 'source.png'
    source.write_bytes(image_bytes())
    notes = create_empty_osint_result(source)
    add_manual_match(notes, 'other', 'https://example.com/post', title='Creator declaration',
                     image_url='https://example.com/asset', claim_process='full_image_generation')
    session = InvestigationSession.selected(source, notes)
    invocation = session.begin_analysis('normal', {}, {}, tmp_path / 'analysis')
    session.complete(invocation, object(), generation_result())
    frozen = session.summary_json
    output = Path(invocation.output_dir)
    old = persist_report_snapshot(session, create_report_snapshot(session), output)
    old_bytes = Path(old['final_summary_json']).read_bytes()
    connections, resolutions, sent, sni = wire(monkeypatch, [response(source.read_bytes())])
    record, downloaded = retrieve(source, session.source_sha256, asdict(notes.matches[0]))[0]
    assert record['association'] == 'byte_identical' and record['source_sha256'] == digest(source.read_bytes())
    assert connections == [('93.184.216.34', 443)] and resolutions == ['example.com'] and sni == ['example.com']
    assert b'Host: example.com' in b''.join(sent) and b'Authorization:' not in b''.join(sent)
    with pytest.raises(ValueError, match='not issued'):
        retain(output.parent, dict(record, association='visually_verified'), downloaded, asdict(notes.matches[0]), session.session_id, 1)
    notes.matches[0].verification = retain(output.parent, record, downloaded, asdict(notes.matches[0]), session.session_id, 1)
    session.commit_annotations(notes)
    synthesis = session.investigation_synthesis()
    cross = synthesis['external_source_corroboration']['cross_source_assessment']
    assert cross['relationships'][0]['image_association'] == 'byte_identical'
    assert cross['assessment_status'] == 'corroborated_declaration'
    assert cross['relationships'][0]['independence'] == 'not_established'
    assert synthesis['technical_provenance_authenticity']['status'] == 'unverified'
    saved = persist_report_snapshot(session, create_report_snapshot(session), output)
    restored = load_investigation(saved['final_summary_json'])
    assert restored.investigation_synthesis() == synthesis
    assert restored.summary_json == frozen and Path(old['final_summary_json']).read_bytes() == old_bytes
    match = asdict(notes.matches[0])
    changed = dict(match, page_url='https://example.com/new-publication-page')
    assert validate(changed, session.source_sha256) == {k: v for k, v in record.items() if k != '_issuer_mac'} | {
        'record_id': match['record_id'], 'source_image_url': match['image_url'],
        'source_page_url': match['page_url'], 'investigation_id': session.session_id, 'evidence_revision': 1}
    assert validate(dict(match, image_url='https://example.com/other'), session.source_sha256) is None
    assert validate(dict(match, record_id='different-record'), session.source_sha256) is None
    assert validate(dict(match, image_association='rejected'), session.source_sha256) is None
    assert validate(match, 'f'*64) is None
    asset = Path(match['verification']['root']) / (record['source_sha256'] + '.image')
    asset.write_bytes(b'corrupted')
    degraded = restored.investigation_synthesis()
    assert degraded['external_source_corroboration']['assessment_status'] == 'insufficient_association'
    assert degraded['revision_id'] != synthesis['revision_id']
    assert 'corrupted' in ' '.join(degraded['external_source_corroboration']['cross_source_assessment']['relationships'][0]['limitations'])
    assert Path(old['final_summary_json']).read_bytes() == old_bytes and restored.summary_json == frozen


@pytest.mark.parametrize('fmt', ['JPEG', 'WEBP'])
def test_source_verification_transforms_require_distributed_visual_agreement(fmt):
    """Gap: reproducible transformed-copy acceptance versus same-background changes."""
    import io
    from PIL import Image, ImageDraw
    from source_verification_helpers import image_bytes
    from source_image_verification import compare, digest
    local, transformed = image_bytes(), image_bytes(fmt, transformed=True)
    assert digest(local) != digest(transformed)
    status, metrics = compare(local, transformed)
    assert status == 'visually_verified' and metrics['sha256_equal'] is False
    # Counterfactual: retain the scene/background but replace the central subject.
    im = Image.open(io.BytesIO(transformed))
    ImageDraw.Draw(im).rectangle((90, 90, 210, 210), fill=(230, 20, 30))
    stream = io.BytesIO()
    im.save(stream, format=fmt)
    assert compare(local, stream.getvalue())[0] not in {'byte_identical', 'visually_verified'}


@pytest.mark.parametrize('boundary', ['scheme', 'private_dns', 'unsafe_redirect', 'different_peer'])
def test_source_retrieval_blocks_unsafe_connection_boundaries(boundary, monkeypatch):
    """Gap: actual pinned destination and each redirect must satisfy SSRF policy."""
    import threading, time
    from source_image_verification import SafeHTTP
    from source_verification_helpers import wire, response
    redirect = b'HTTP/1.1 302 Found\r\nLocation: http://private.example/asset\r\nContent-Length: 0\r\n\r\n'
    connections, resolutions, _, _ = wire(monkeypatch,
        [redirect if boundary == 'unsafe_redirect' else response(b'image')],
        private_host='private.example', wrong_peer=boundary == 'different_peer')
    url = {'scheme': 'file:///C:/secret', 'private_dns': 'http://private.example/a'}.get(boundary, 'https://example.com/a')
    with pytest.raises(ValueError):
        SafeHTTP().fetch(url, threading.Event(), time.monotonic() + 10)
    assert len(connections) == (1 if boundary in {'unsafe_redirect', 'different_peer'} else 0)
    if boundary == 'unsafe_redirect':
        assert resolutions == ['example.com', 'private.example']


def test_source_page_candidates_are_bounded_and_failures_are_not_mismatches(tmp_path, monkeypatch):
    """Gap: HTML discovery must compare each bounded asset, not bless a whole post."""
    from source_image_verification import retrieve, digest
    from source_verification_helpers import image_bytes, wire, response
    source = tmp_path / 'source.png'
    source.write_bytes(image_bytes())
    html = ''.join(f'<img src="/{i}.png">' for i in range(8)).encode()
    connections, _, _, _ = wire(monkeypatch, [response(html, 'text/html'),
        response(b'not an image'), response(source.read_bytes()),
        b'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n', response(b'<html>', 'text/html')])
    rows = retrieve(source, digest(source.read_bytes()), {'page_url': 'https://example.com/post#lightbox'})
    assert len(rows) == 4 and len(connections) == 5
    assert [r['status'] for r, _ in rows] == ['image_decode_failed', 'verification_completed', 'download_failed', 'unsupported_response']
    assert [r['association'] for r, _ in rows] == ['unestablished', 'byte_identical', 'unestablished', 'unestablished']
    assert rows[1][0]['requested_url'] == 'https://example.com/1.png'


@pytest.mark.parametrize('association,process,expected,agreement', [
    pytest.param('analyst_associated', 'full_image_generation', 'corroborated_declaration', 'compatible', id='associated-compatible-declarations'),
    pytest.param('unestablished', 'full_image_generation', 'insufficient_association', 'compatible', id='reviewed-url-is-not-image-identity'),
    pytest.param('analyst_associated', 'unmodified_camera_capture', 'conflicting_claims', 'conflicting', id='preserve-conflicting-creation-claims'),
])
def test_cross_source_claim_relationships_are_qualified(association, process, expected, agreement):
    """New gap: semantic agreement, image association and dependence were not compared."""
    from investigation_synthesis import build_synthesis, synthesis_text
    data = generation_result()
    original = deepcopy(data)
    notes = {'image_sha256': 'a'*64, 'analyst_reviewed': True, 'review_status': 'reviewed_matches_found',
        'matches': [{'page_url': 'https://example.com/source', 'image_url': 'https://example.com/image.png',
            'title': 'Creator account', 'claim_text': 'Reported creation process', 'claim_process': process,
            'model_family': 'FLUX.2 Klein', 'claimed_by': 'creator', 'attribution': 'Reported creator',
            'image_association': association, 'association_method': 'analyst_visual_check',
            'association_details': 'Analyst compared the depicted scene', 'similarity_score': None,
            'source_dependency': 'same_creator'}]}
    record = build_synthesis(data, notes, 'a'*64)
    cross = record['external_source_corroboration']['cross_source_assessment']
    rel = cross['relationships'][0]
    assert cross['assessment_status'] == rel['status'] == expected
    assert rel['agreement'] == agreement and rel['image_association'] == association
    assert rel['model_agreement'] == 'compatible'
    assert rel['source_dependency'] == 'same_creator' and rel['independence'] == 'not_established'
    assert {c['process'] for c in cross['claims']} == {'full_image_generation', process}
    assert len(cross['claims'][0]['model_details']) == 1  # ignores the disconnected SDXL node
    assert cross['claims'][1]['verification_status'] == 'unverified'
    assert record['technical_provenance_authenticity']['status'] == 'unverified'
    assert record['separate_edit_assessment']['status'] == 'not_established'
    assert data == original
    text = synthesis_text(record)
    assert 'https://example.com/source' in text and expected in text and agreement in text
    assert 'not_established' in text
    if expected == 'corroborated_declaration':
        assert record['origin_assessment']['status'] == 'cross_source_corroborated_generation_declaration'
    else:
        assert record['origin_assessment']['status'] != 'cross_source_corroborated_generation_declaration'
    if association == 'unestablished':
        # Even a maximal manual score and an unsupported verification assertion
        # cannot replace a reproducible source-image comparison.
        notes['matches'][0].update(image_association='byte_identical', similarity_score=1.0)
        guarded = build_synthesis(data, notes, 'a'*64)['external_source_corroboration']['cross_source_assessment']
        assert guarded['assessment_status'] == 'insufficient_association'
        assert guarded['relationships'][0]['image_association'] == 'unestablished'
        assert 'no supported reproducible verifier' in ' '.join(guarded['relationships'][0]['limitations'])
        notes['matches'][0]['source_type'] = 'ai_gallery'
        photo = build_synthesis(structured_result(), notes, 'a'*64)
        assert photo['origin_assessment']['status'] == 'not_established'
        assert not any(ref.startswith('osint:') for ref in photo['origin_assessment']['supporting_observations'])


def test_review_before_and_after_analysis_yields_equivalent_investigation(tmp_path):
    """New contract: evidence timing changes revision metadata, not conclusion/facts."""
    from osint_reverse_search import create_empty_osint_result, add_manual_match
    from investigation_session import json_snapshot
    source = tmp_path / 'image.jpg'
    source.write_bytes(b'associated source')
    empty = create_empty_osint_result(source)
    reviewed = deepcopy(empty)
    add_manual_match(reviewed, 'other', 'https://example.com/source', source_type='ai_gallery',
                     title='Published as generated', similarity_score=1.0)
    data = structured_result()
    before = InvestigationSession.selected(source, reviewed)
    token = before.begin_analysis('normal', {}, {}, tmp_path)
    assert before.complete(token, None, data)
    after = InvestigationSession.selected(source, empty)
    token = after.begin_analysis('normal', {}, {}, tmp_path)
    assert after.complete(token, None, data)
    old = create_report_snapshot(after)
    assert after.commit_annotations(reviewed)
    a, b = before.investigation_synthesis(), after.investigation_synthesis()
    assert a['origin_assessment'] == b['origin_assessment']
    assert a['external_source_corroboration'] == b['external_source_corroboration']
    assert a['lead'] == b['lead']
    assert b['external_source_corroboration']['source_image_match_status'] == 'manual_similarity_unverified'
    assert b['external_source_corroboration']['assessment_status'] != 'corroborated_declaration'
    assert b['technical_provenance_authenticity']['status'] == 'unverified'
    assert after.summary_json == before.summary_json == json_snapshot(data)
    assert old.payload()['investigation_synthesis']['external_source_corroboration']['status'] == 'not_recorded'
    assert not snapshot_is_current(after, old)
    exported = create_report_snapshot(after).payload()
    assert exported['investigation_synthesis'] == b and 'Published as generated' in exported['full_text']


def test_empty_unique_selection_and_same_image_investigations(tmp_path):
    empty = InvestigationSession()
    assert empty.state == InvestigationState.EMPTY
    with pytest.raises(ValueError):
        empty.begin_analysis('normal', {}, {}, tmp_path)
    a, b = [InvestigationSession.selected(tmp_path / 'a.jpg') for _ in range(2)]
    assert a.session_id != b.session_id
    assert a.image_path == b.image_path
    assert a.state == InvestigationState.IMAGE_SELECTED
    first = a.storage_directory(tmp_path / 'output')
    second = b.storage_directory(tmp_path / 'output')
    assert first != second  # unknown source identity must never merge sessions


def test_compact_storage_names_and_collisions_preserve_full_identity(tmp_path):
    """Previously unprotected Windows naming and collision-safe allocation contract."""
    from concurrent.futures import ThreadPoolExecutor
    from investigation_storage import image_folder_name, investigation_directory, allocate_run, read_json
    for raw, expected in [('CON.jpg', '_CON'), ('NUL.notes.png', '_NUL.notes'),
                          ('portrait .png', 'portrait'), ('..\\..\\photo.png', 'photo'),
                          ('bad<>name?.png', 'bad__name_'), ('海辺の写真.png', '海辺の写真')]:
        assert image_folder_name(raw) == expected, raw
    assert len(image_folder_name('😀' * 80 + '.png').encode('utf-16-le')) <= 96
    root = tmp_path / 'output'
    name = 'Recognizable portrait wording ' * 3 + '.png'
    a = investigation_directory(root, name, '0' * 64, 'session-a')
    assert a.parent.name.startswith('Recognizable portrait') and len(a.parent.name) <= 48
    assert read_json(a.parent / 'manifest.json')['original_filename'] == name
    b = investigation_directory(root, name.upper(), 'a' * 64, 'session-b')
    c = investigation_directory(root, name, 'a' * 8 + '1' * 56, 'session-c')
    assert b.parent != c.parent != a.parent
    assert b.parent.name.endswith('--aaaaaaaa') and c.parent.name.endswith('--aaaaaaaa1111')
    # Same full content identity reuses the image container, never the independent investigation.
    d = investigation_directory(root, 'renamed.png', '0' * 64, 'session-d')
    assert d.parent == a.parent and d != a
    with ThreadPoolExecutor(max_workers=2) as pool:
        runs = list(pool.map(lambda n: allocate_run(a, str(n), '0' * 64, 'session-a'), range(2)))
    assert len(set(runs)) == 2
    assert {read_json(p / 'run_identity.json')['analysis_id'] for p in runs} == {'0', '1'}


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
    result['reasoning_trace']['causal_interpretation'] = {
        'lead_title': 'Declared creation and regional observations',
        'lead_explanation': 'Workflow declaration remains unverified.',
        'confidence_scope': 'Local support is not editing-history certainty.'}
    original = deepcopy(result)
    session = completed(tmp_path, result)
    view = build_presentation(session, result)
    assert view == build_presentation(session, result)
    assert view.summary.lead_explanation == 'Workflow declaration remains unverified.'
    assert view.summary.confidence_scope == 'Local support is not editing-history certainty.'
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
    session = completed(tmp_path, generation_result())
    session.source_sha256 = 'a'*64
    frozen = session.summary_json
    old = create_report_snapshot(session)
    output = Path(session.invocation.output_dir)
    first = persist_report_snapshot(session, old, output)
    first_bytes = Path(first['final_summary_json']).read_bytes()
    assert Path(first['current_report']) == output.parent / 'latest.json'
    assert Path(first['final_summary_json']).parent.name == 'rev_001'
    assert session.report_current
    revisions = []
    for n in range(3):
        annotations = {'notes': f'edit {n}', 'image_sha256': session.source_sha256,
            'analyst_reviewed': True, 'review_status': 'reviewed_matches_found',
            'matches': [{'page_url': 'https://example.com/claim', 'title': 'Explicit claim',
                'claim_process': 'full_image_generation' if n == 0 else 'unmodified_camera_capture',
                'image_association': 'analyst_associated', 'association_method': 'analyst_visual_check',
                'association_details': 'Reviewed scene match'}] if n < 2 else []}
        assert session.commit_annotations(annotations)
        assert session.annotation_revision == n+1
        assert not session.report_current
        assert not snapshot_is_current(session, old)
        with pytest.raises(ValueError, match='stale'):
            persist_report_snapshot(session, old, output)
        revisions.append(create_report_snapshot(session))
        assert revisions[-1].payload()['investigation_synthesis']['external_source_corroboration']['assessment_status'] == (
            'corroborated_declaration', 'conflicting_claims', 'not_assessed')[n]
    assert session.summary_json == frozen
    assert not session.commit_annotations(annotations)
    assert len({s.payload()['investigation_synthesis']['revision_id'] for s in revisions}) == 3
    assert revisions[0].payload()['investigation_synthesis']['external_source_corroboration']['assessment_status'] == 'corroborated_declaration'
    current = create_report_snapshot(session)
    paths = persist_report_snapshot(session, current, output)
    payload = json.loads(Path(paths['final_summary_json']).read_text(encoding='utf-8'))
    assert payload['annotations']['notes'] == 'edit 2'
    assert payload['investigation']['annotation_revision'] == 3
    assert payload['reasoning_trace'] == json.loads(frozen)['reasoning_trace']
    assert Path(first['final_summary_json']).is_file()
    assert Path(first['final_summary_json']).read_bytes() == first_bytes
    assert Path(paths['final_summary_json']).parent.name == 'rev_002'
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
    output = Path(session.invocation.output_dir)
    paths = persist_report_snapshot(session, create_report_snapshot(session), output)
    pointer = Path(paths['current_report'])
    before = pointer.read_bytes()
    session.commit_annotations({'notes': 'new'})
    writer = reports.persist_reasoning_trace_text
    monkeypatch.setattr(reports, 'persist_reasoning_trace_text', lambda *args, **kwargs: (_ for _ in ()).throw(OSError('disk full')))
    with pytest.raises(OSError, match='disk full'):
        persist_report_snapshot(session, create_report_snapshot(session), output)
    assert pointer.read_bytes() == before
    assert sorted(p.name for p in (pointer.parent / 'reports').iterdir()) == ['rev_001']
    assert not session.report_current
    # A transient Windows reader lock may delay replacement, never force an
    # in-place truncate or discard the valid previous pointer.
    monkeypatch.setattr(reports, 'persist_reasoning_trace_text', writer)
    replace = Path.replace
    attempts = []
    def sharing_retry(path, destination):
        if destination == pointer:
            attempts.append(1)
            if len(attempts) == 1:
                raise PermissionError('reader sharing lock')
        return replace(path, destination)
    monkeypatch.setattr(Path, 'replace', sharing_retry)
    persist_report_snapshot(session, create_report_snapshot(session), output)
    assert len(attempts) == 2 and session.report_current


def test_new_report_load_preserves_forensic_fields_and_does_not_reappend_old_annotations(tmp_path):
    from osint_reverse_search import create_empty_osint_result
    source = tmp_path / 'a.jpg'
    source.write_bytes(b'input')
    session = completed(tmp_path)
    session.image_path = str(source)
    annotations = create_empty_osint_result(source)
    annotations.analyst_notes.append('Recorded analyst note')
    session.source_sha256 = annotations.image_sha256  # same identity captured by GUI selection
    session.commit_annotations(annotations)
    paths = persist_report_snapshot(session, create_report_snapshot(session), session.invocation.output_dir)
    imported = load_investigation(paths['current_report'])
    assert imported.session_id != session.session_id
    assert imported.invocation is None and imported.annotation_revision == 0
    assert imported.summary_data() == session.summary_data()
    assert imported.investigation_synthesis() == session.investigation_synthesis()
    assert json.loads(imported.annotations_json)['analyst_notes'] == ['Recorded analyst note']
    assert json.loads(imported.historical_identity_json)['annotation_revision'] == 1
    assert create_report_snapshot(imported).payload()['full_text'].count('Current OSINT annotations') == 1
    altered = json.loads(Path(paths['final_summary_json']).read_text(encoding='utf-8'))
    altered['investigation_synthesis']['technical_provenance_authenticity']['status'] = 'verified'
    tampered = tmp_path / 'altered.json'
    tampered.write_text(json.dumps(altered), encoding='utf-8')
    assert load_investigation(tampered).investigation_synthesis()['technical_provenance_authenticity']['status'] == 'unverified'


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
