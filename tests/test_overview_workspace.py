"""UI-3 contracts: bounded source display and faithful structured projections."""
from gui_helpers import publish, wait_for, set_trace
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import threading

import pytest
from PIL import Image
from PyQt6.QtCore import QEventLoop, QTimer, QThreadPool
from PyQt6.QtGui import QImage
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QDialog, QPushButton

from investigation_presenters import build_presentation
from source_image_viewer import SourceImageViewer, PreviewResult, read_preview, fingerprint
import source_image_viewer as viewer_module


@pytest.mark.parametrize('size', [(40, 80), (3000, 50), (50, 3000), (3200, 2400)])
def test_preview_preserves_source_aspect_and_bounds_decode(app, tmp_path, size):
    path = tmp_path / 'source.png'
    Image.new('RGB', size, 'navy').save(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    result = read_preview(('request',), path, digest)
    assert result.dimensions == size and not result.image.isNull()
    assert max(result.image.width(), result.image.height()) <= 2048
    # Integer preview dimensions may round by one pixel, especially panoramas.
    assert abs(result.image.width() * size[1] - result.image.height() * size[0]) <= max(size)
    assert fingerprint(path) == result.stamp


@pytest.mark.parametrize('kind', ['missing', 'corrupt', 'changed'])
def test_unavailable_source_is_explicit(app, tmp_path, kind):
    path = tmp_path / 'source.png'
    digest = None
    if kind == 'corrupt':
        path.write_bytes(b'not an image')
    elif kind == 'changed':
        Image.new('RGB', (20, 20)).save(path)
        digest = '0' * 64
    result = read_preview(('request',), path, digest)
    assert result.image.isNull()
    assert result.message
    assert 'changed' in result.message if kind == 'changed' else 'unavailable' in result.message.lower()


def test_large_decode_runs_off_gui_thread_and_zoom_is_display_only(app, tmp_path, monkeypatch):
    path = tmp_path / 'large.png'
    Image.new('RGB', (4000, 3000), 'silver').save(path)
    gui_thread = threading.get_ident()
    threads = []
    real = viewer_module.read_preview
    def observed(*args):
        threads.append(threading.get_ident())
        return real(*args)
    monkeypatch.setattr(viewer_module, 'read_preview', observed)
    view = SourceImageViewer()
    view.show()
    view.set_source(path, ('session', 'invocation'))
    wait_for(app, lambda: not view._image.isNull())
    assert threads and all(t != gui_thread for t in threads)
    cache = view._image.cacheKey()
    view.zoom_in.click()
    assert not view.fit_mode and view.zoom_factor == 1.25
    view.zoom_out.click()
    view.fit_button.click()
    assert view.fit_mode and view.zoom_factor == 1
    assert view._image.cacheKey() == cache
    view.close()
    view.deleteLater()


def test_obsolete_preview_and_delivery_after_file_change_are_rejected(app, source, tmp_path):
    view = SourceImageViewer()
    view.set_source(source, ('old', None))
    stale = read_preview(view._request, source, None)
    other = tmp_path / 'other.png'
    Image.new('RGB', (80, 20), 'white').save(other)
    view.set_source(other, ('new', None))
    current = view._image.cacheKey()
    assert not view.accept_preview(stale)
    assert view._image.cacheKey() == current
    late = read_preview(view._request, other, None)
    other.unlink()
    assert view.accept_preview(late)
    assert view._image.isNull() and 'changed' in view.message.text()
    view.deleteLater()


def test_source_monitor_clears_changed_or_missing_pixels(app, source):
    view = SourceImageViewer()
    view.set_source(source, ('session', None))
    assert not view._image.isNull()
    Image.new('RGB', (32, 48), 'red').save(source)
    view.check_source()
    assert view._image.isNull() and 'changed' in view.message.text()
    assert not view.zoom_in.isEnabled()
    view.deleteLater()


@pytest.mark.parametrize('primary,tier', [('localized_editing', 'High'), ('synthetic_origin', 'Medium'), ('unresolved_anomaly', 'Inconclusive'), (None, None)])
def test_primary_pattern_and_exact_confidence_are_recorded(window, source, primary, tier):
    publish(window, source)
    trace = window.session.summary_data()['reasoning_trace']
    trace['decision'].update(primary_hypothesis=primary, confidence_tier=tier, dominant_pattern='recorded_pattern')
    trace['confidence_policy'] = {'assessments': [{'hypothesis': primary, 'tier': tier}]}
    set_trace(window, trace)
    overview = window.workspace.overview
    assert overview.confidence.tier == tier
    assert 'recorded_pattern' in overview.pattern.text()
    assert 'not recorded' in overview.finding_title.text().lower() if primary is None else primary.replace('_', ' ').split()[0].lower() in overview.finding_title.text().lower()


def test_three_hypotheses_missing_assessments_and_no_policy_inference(window, source):
    publish(window, source)
    overview = window.workspace.overview
    assert len(overview.cards) == 3
    assert overview.cards['synthetic_origin'].tier.tier == 'Medium'
    for hid in ('localized_editing', 'camera_acquisition'):
        assert overview.cards[hid].tier.tier is None
        assert overview.cards[hid].finding.text() == 'Assessment not recorded.'
    trace = window.session.summary_data()['reasoning_trace']
    trace['decision'].pop('confidence_tier')
    trace['hypothesis_assessments'][0].pop('confidence_tier')
    set_trace(window, trace)
    assert overview.confidence.tier is None
    assert overview.cards['synthetic_origin'].tier.tier is None


def test_evidence_caps_preserve_role_source_and_backend_order(window, source):
    publish(window, source)
    trace = window.session.summary_data()['reasoning_trace']
    assessment = trace['hypothesis_assessments'][0]
    for role in ('supporting_evidence', 'contradicting_evidence', 'moderating_evidence'):
        assessment[role] = [f'{role}:{i}' for i in range(5)]
    set_trace(window, trace)
    rows = window.workspace.overview.evidence_rows
    assert len(rows) == 6
    assert [r.evidence_id for r in rows] == [f'{role}:{i}' for role in ('supporting_evidence', 'contradicting_evidence', 'moderating_evidence') for i in range(2)]
    assert all(r.source_detector is None and r.reliability is None for r in rows)
    assert 'No ranking' in window.workspace.overview.evidence_note.text()


def test_limitations_keep_unverified_provenance_and_unavailable_regions(window, source):
    publish(window, source)
    overview = window.workspace.overview
    assert 'unverified' in overview.limitations.text()
    assert 'No reliable mask' in overview.scope_text
    assert 'Region FFT' in overview.scope_text
    assert 'not negative evidence' in overview.scope_text


def test_navigation_and_narrative_preserve_snapshot_and_annotations(window, source, app):
    publish(window, source)
    frozen = window.session.summary_json
    overview = window.workspace.overview
    for name, action in overview.actions.items():
        assert action.isEnabled()
        action.click()
        assert window.workspace.current_destination == name
    overview.show_narrative()
    app.processEvents()
    assert overview.narrative_dialog.isVisible()
    assert 'Recorded narrative' in window.summary_box.toPlainText()
    overview.narrative_dialog.close()
    window.mark_osint_reviewed_no_match()
    assert window.session.summary_json == frozen
    assert overview.confidence.tier == 'Medium'


@pytest.mark.parametrize('state', ['image_selected', 'analyzing', 'failed', 'cancelled'])
def test_lifecycle_never_retains_old_findings(window, source, state):
    from investigation_session import InvestigationState
    publish(window, source)
    window.session = replace(window.session, state=InvestigationState(state), result_id=None, summary_json=None)
    window.update_summary()
    overview = window.workspace.overview
    assert overview.confidence.tier is None
    assert 'No completed' in overview.finding_title.text()
    assert not overview.evidence_rows
    assert not overview.actions['Reports'].isEnabled()
    assert overview.actions['Reports'].toolTip()


def test_profile_is_captured_and_imported_source_identity_is_preserved(window, source):
    publish(window, source)
    snapshot = window.view_snapshot
    assert snapshot.source.profile == 'normal'
    assert snapshot.source.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
    assert window.refresh_report_snapshot()
    pointer = window._report_paths['current_report']
    source.unlink()
    assert window.load_stored_summary(pointer)
    assert window.view_snapshot.source.stored
    assert window.view_snapshot.source.profile == 'normal'
    assert window.workspace.preview._image.isNull()
    assert window.workspace.confidence.tier == 'Medium'


@pytest.mark.parametrize('width,height', [(1040, 720), (1280, 900), (1600, 1000)])
def test_layout_long_text_wraps_and_controls_stay_reachable(window, source, app, width, height):
    publish(window, source)
    trace = window.session.summary_data()['reasoning_trace']
    trace['hypothesis_assessments'][0]['explanation'] = 'Long structured finding. ' * 400
    set_trace(window, trace)
    window.resize(width, height)
    app.processEvents()
    overview = window.workspace.overview
    assert overview.scroll.horizontalScrollBar().maximum() == 0
    assert len(overview.cards['synthetic_origin'].finding.text()) <= 211
    assert len(overview.finding_explanation.toolTip()) > 1000
    for action in overview.actions.values():
        assert action.width() >= action.minimumSizeHint().width()
    assert overview.preview.canvas.width() >= 180
    overview.scroll.verticalScrollBar().setValue(overview.scroll.verticalScrollBar().maximum())
    app.processEvents()
    assert overview.narrative_button.isVisible()
