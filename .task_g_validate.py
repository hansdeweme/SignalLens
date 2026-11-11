"""Temporary Task G acceptance experiment; not a collected regression suite."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from pathlib import Path
from copy import deepcopy
from dataclasses import asdict
from uuid import uuid4
import contextlib
import io
import json
import hashlib

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QThreadPool
import signallens_gui as gui
from signallens_controller import SignalLensController
from investigation_session import InvestigationSession, AnalysisInvocation, InvestigationState, json_snapshot
from osint_reverse_search import create_empty_osint_result, add_manual_match
from artifact_presenter import discovery_context, discover_artifacts
from investigation_presenters import build_presentation

ROOT = Path(__file__).resolve().parent
validation = ROOT / ('.g_' + uuid4().hex[:8])
validation.mkdir()
reference = json.loads((ROOT / 'doc/reasoning_audit/origin_processing/task_d_reference_comparison.json').read_text())
app = QApplication([])
records = {}


def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def stats(directory):
    files = [p for p in directory.rglob('*') if p.is_file()]
    longest = max(files, key=lambda p: len(str(p)))
    return {'files': len(files), 'directories': sum(p.is_dir() for p in directory.rglob('*')),
            'bytes': sum(p.stat().st_size for p in files), 'longest_path': str(longest),
            'longest_path_characters': len(str(longest)),
            'maximum_directory_depth': max(len(p.relative_to(directory).parts) - 1 for p in files),
            'longest_relative_characters': max(len(str(p.relative_to(directory))) for p in files)}


def run_case(case, compact):
    label = case + ('_new' if compact else '_legacy')
    image = Path(reference[case]['source'])
    settings = deepcopy(reference[case]['settings'])
    output = validation / label
    settings['output_root'] = str(output)
    gui.load_settings = lambda: deepcopy(settings)
    preferences = QSettings(str(validation / (label + '.ini')), QSettings.Format.IniFormat)
    window = gui.SignalLensGui(ui_settings=preferences)
    notes = create_empty_osint_result(image)
    if compact:
        window.set_selected_file(image)
        token = window.session.begin_analysis('normal', {}, settings, output)
        run = Path(token.output_dir)
        metadata = run / 'evidence' / 'metadata.json'
    else:
        session = InvestigationSession.selected(image, notes)
        run = output / image.stem / session.session_id / uuid4().hex
        token = AnalysisInvocation(session.session_id, run.name, str(image), 'normal', (),
            json_snapshot(settings), session.annotations_json, 0, str(run), source_sha256=session.source_sha256)
        session.invocation, session.state = token, InvestigationState.ANALYZING
        window.session = session
        window.selected_file = window.current_image_path = image
        window.osint_result = notes
        metadata = run / (image.stem + '_exif_signals.json')
    window.current_analysis_dir = run
    window._session_dir = run.parent
    state = SignalLensController(settings_snapshot=settings).run_analysis(image, run, metadata, 'normal')
    assert not state.errors, state.errors
    window.on_analysis_finished(token, state)
    assert window.session.report_current, window.status_label.text()
    snapshot = build_presentation(window.session)
    context = discovery_context(window.session, snapshot, state)
    rows = discover_artifacts(context, snapshot)
    workspace = window.workspace.forensics
    assert workspace.accept_catalog(workspace.key, rows)
    assert any(r.detector_id == 'ela' and r.can_overlay for r in rows)
    available = [r for r in rows if r.available and r.path]
    assert available and all(Path(r.path).is_file() for r in available)
    first = dict(window._report_paths)
    first_dir = Path(first['final_summary_json']).parent
    first_hashes = hashes(first_dir)
    data = window.session.summary_data()
    records[label] = {'scope': 'one complete detector invocation, one initial report, GUI artifact catalog',
        'stats': stats(output), 'run': str(run), 'stage_counts': state.analysis_coverage['stage_counts'],
        'scorecard': data['reasoning_trace']['scorecard'], 'primary': data['reasoning_trace']['decision']['primary_hypothesis'],
        'tiers': [(h['hypothesis_id'], h['confidence_tier']) for h in data['reasoning_trace']['hypothesis_assessments']],
        'artifact_count': len(available), 'initial_report': first['final_summary_json']}
    (validation / 'validation_results.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    if compact:
        assert (run / 'evidence' / 'global_fft.json').is_file()
        assert Path(json.loads((run / 'evidence' / 'global_fft.json').read_text())['fft']['input_image']).name == 'global.png'
        frozen = window.session.summary_json
        draft = deepcopy(window.osint_result)
        add_manual_match(draft, 'other', 'https://example.org/reviewed-source', title='Reviewed source context')
        assert window._commit_osint(window.session.session_id, draft)
        assert window.session.summary_json == frozen
        assert hashes(first_dir) == first_hashes
        assert window._report_paths['final_summary_json'] != first['final_summary_json']
        pointer = window._report_paths['current_report']
        assert window.load_stored_summary(pointer)
        assert window.session.summary_json == frozen
        assert len(window.osint_result.matches) == 1
        assert window.refresh_report_snapshot()
        # Re-export from the fresh import must keep the original artifact root.
        exported = window._report_paths['current_report']
        assert window.load_stored_summary(exported)
        restored = discover_artifacts(discovery_context(window.session, window.view_snapshot), window.view_snapshot)
        restored_available = [r for r in restored if r.available and r.path]
        assert {r.sha256 for r in restored_available} == {r.sha256 for r in available}
        assert hashes(first_dir) == first_hashes
        records[label].update(post_osint_no_rerun=True, historical_report_unchanged=True,
            double_restoration_artifacts=len(restored_available), imported_report=exported)
    window.close()
    window.deleteLater()
    QThreadPool.globalInstance().waitForDone()
    app.processEvents()


try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        run_case('midjourney', False)
        run_case('midjourney', True)
        run_case('conventional_photo', True)
    assert records['midjourney_new']['scorecard'] == records['midjourney_legacy']['scorecard']
    records['midjourney_like_for_like_scorecard_equal'] = True
    records['validation_root'] = str(validation)
    (validation / 'validation_results.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(json.dumps(records, indent=2))
except Exception:
    print('VALIDATION ROOT:', validation)
    raise
