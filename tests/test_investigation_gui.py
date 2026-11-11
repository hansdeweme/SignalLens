"""Deterministic offscreen Qt tests with semaphore-controlled workers."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from copy import deepcopy
import json
from pathlib import Path

import pytest
from PIL import Image
from PyQt6.QtCore import QObject, QThread, QSemaphore, QEventLoop, QTimer, QSettings, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMessageBox

import signallens_gui as gui
from investigation_session import InvestigationSession, InvestigationState
from investigation_workers import InvestigationWorkers
from osint_reverse_search import add_manual_match
from signallens_controller import AnalysisState
from signallens_settings import DEFAULT_SETTINGS


def until(signal, predicate, action=lambda: None):
    """Wait on emitted state changes; timer is a failure deadline, not a sleep."""
    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)
    def check(*args):
        if predicate():
            loop.quit()
    signal.connect(check)
    timer.timeout.connect(loop.quit)
    timer.start(5000)
    try:
        action()
        if not predicate():
            loop.exec()
        assert predicate(), 'Expected signal-driven condition before deadline'
    finally:
        signal.disconnect(check)
        timer.stop()


class ControlledWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    log = pyqtSignal(str, str)
    entered = pyqtSignal()

    def __init__(self, result=None, error=None):
        super().__init__()
        self.result = result
        self.message = error
        self.gate = QSemaphore(0)
        self.is_entered = False
        self.executed_thread = None

    @pyqtSlot()
    def run(self):
        self.executed_thread = QThread.currentThread()
        self.is_entered = True
        self.entered.emit()
        self.status.emit('working')
        self.gate.acquire()
        self.log.emit('terminal log', 'info')
        self.status.emit('terminal status')
        if self.message:
            self.error.emit(self.message)
        else:
            self.finished.emit(self.result)


@pytest.fixture
def window(app, tmp_path, monkeypatch):
    settings = deepcopy(DEFAULT_SETTINGS)
    settings['output_root'] = str(tmp_path / 'output')
    monkeypatch.setattr(gui, 'load_settings', lambda: settings)
    for name in ('warning', 'critical', 'information'):
        monkeypatch.setattr(QMessageBox, name, lambda *args: QMessageBox.StandardButton.Ok)
    preferences = QSettings(str(tmp_path/'workspace.ini'),QSettings.Format.IniFormat)
    w = gui.SignalLensGui(ui_settings=preferences)
    yield w
    # Never destroy live Qt threads, even when an assertion fails.
    if w.workers.busy:
        handles = list(w.workers.handles.values())
        until(w.workers.idle, lambda: not w.workers.busy,
              lambda: [h.worker.gate.release() for h in handles])
    w.close()
    w.deleteLater()
    app.processEvents()


@pytest.fixture
def images(tmp_path):
    paths = [tmp_path / 'a.png', tmp_path / 'b.png']
    for path in paths:
        Image.new('RGB', (16, 16), 'gray').save(path)
    return paths


def invocation(window, path):
    window.set_selected_file(path)
    return window.session.begin_analysis('normal', {}, window.settings, window.settings['output_root'])


def result_for(token):
    return AnalysisState(Path(token.image_path), Path(token.output_dir))


def test_packaged_main_uses_executable_directory(tmp_path,monkeypatch):
    import signallens_gui as gui
    from types import SimpleNamespace
    bundle=tmp_path/'portable';bundle.mkdir()
    executable=bundle/'SignalLens.exe';executable.write_bytes(b'')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(gui.sys,'frozen',True,raising=False)
    monkeypatch.setattr(gui.sys,'executable',str(executable))
    monkeypatch.setattr(gui,'QApplication',lambda args:SimpleNamespace(exec=lambda:0))
    monkeypatch.setattr(gui,'SignalLensGui',lambda:SimpleNamespace(show=lambda:None))
    monkeypatch.setattr(gui.QTimer,'singleShot',lambda *args:None)
    with pytest.raises(SystemExit) as stopped:gui.main()
    assert stopped.value.code==0 and Path.cwd()==bundle


def test_new_selection_clears_every_prior_trace_result_and_late_callback(window, images):
    token = invocation(window, images[0])
    window.on_analysis_finished(token, result_for(token))
    assert window.session.state == InvestigationState.COMPLETED
    assert window.summary_result is not None
    window.set_selected_file(images[1])
    before = (window.status_label.text(), window.summary_box.toPlainText(), window.session.session_id)
    window.on_analysis_finished(token, result_for(token))
    window.on_analysis_error(token, 'obsolete failure')
    window._on_worker_status(token, 'obsolete progress')
    window._on_worker_log(token, 'obsolete log', 'error')
    assert (window.status_label.text(), window.summary_box.toPlainText(), window.session.session_id) == before
    assert window.summary_result is None and window.analysis_state is None
    assert not window.decision_trace_action.isEnabled()
    assert not window.open_json_button.isEnabled()
    assert 'obsolete' not in window.log_box.toPlainText()


def test_reanalysis_out_of_order_and_context_snapshot(window, images):
    first = invocation(window, images[0])
    second = window.session.begin_analysis('subject_based', {'screen_origin': True}, window.settings, window.settings['output_root'])
    window.on_analysis_finished(second, result_for(second))
    frozen = window.session.summary_json
    window.chk_screen.setChecked(False)
    window.update_summary()
    window.on_analysis_finished(first, result_for(first))
    window.on_analysis_error(first, 'old error')
    assert window.session.result_id == second.analysis_id
    assert window.session.summary_json == frozen
    assert 'screen/display-origin' in window.summary_result.context_info


def test_worker_result_source_mismatch_is_failure(window, images):
    token = invocation(window, images[0])
    state = result_for(token)
    state.selected_file = images[1]
    window.on_analysis_finished(token, state)
    assert window.session.state == InvestigationState.FAILED
    assert window.summary_result is None
    assert 'does not match' in window.status_label.text()


def test_actual_worker_thread_delivers_on_gui_thread_and_cleans_success(window, images, app):
    token = invocation(window, images[0])
    worker = ControlledWorker(result_for(token))
    deliveries = []
    window.workers.status_changed.connect(lambda *args: deliveries.append(QThread.currentThread()))
    handle = window.workers.start(token, worker)
    until(worker.entered, lambda: worker.is_entered)
    assert worker.executed_thread != app.thread()
    until(window.workers.idle, lambda: not window.workers.busy, worker.gate.release)
    assert window.session.state == InvestigationState.COMPLETED
    assert deliveries and all(thread == app.thread() for thread in deliveries)
    assert window.session.report_current


def test_error_thread_cleans_up_and_recovery_is_possible(window, images):
    token = invocation(window, images[0])
    worker = ControlledWorker(error='controlled failure')
    window.workers.start(token, worker)
    until(window.workers.idle, lambda: not window.workers.busy, worker.gate.release)
    assert window.session.state == InvestigationState.FAILED
    assert window.run_button.isEnabled()
    newer = window.session.begin_analysis('normal', {}, {}, window.settings['output_root'])
    window.on_analysis_finished(newer, result_for(newer))
    assert window.session.state == InvestigationState.COMPLETED


def test_two_owned_workers_newer_finishes_first_old_progress_and_error_are_ignored(window, images):
    old = invocation(window, images[0])
    a = ControlledWorker(error='obsolete terminal failure')
    window.workers.start(old, a)
    newer = invocation(window, images[1])
    b = ControlledWorker(result_for(newer))
    window.workers.start(newer, b)
    until(window.snapshot_changed, lambda: window.session.state == InvestigationState.COMPLETED, b.gate.release)
    assert window.workers.busy  # obsolete A still physically owned
    current = (window.status_label.text(), window.session.summary_json)
    until(window.workers.idle, lambda: not window.workers.busy, a.gate.release)
    assert (window.status_label.text(), window.session.summary_json) == current
    assert window.session.result_id == newer.analysis_id


def test_close_defers_destruction_until_worker_finishes_without_publishing(window, images):
    token = invocation(window, images[0])
    worker = ControlledWorker(result_for(token))
    window.workers.start(token, worker)
    assert window.close() is False
    assert window._closing and not window.isEnabled()
    assert window.session.state == InvestigationState.CANCELLED
    until(window.workers.idle, lambda: not window.workers.busy, worker.gate.release)
    assert window.session.summary_data() is None
    assert window.session.result_id is None


def test_osint_edits_refresh_view_and_report_without_any_resynthesis(window, images, monkeypatch):
    token = invocation(window, images[0])
    window.on_analysis_finished(token, result_for(token))
    frozen = window.session.summary_json
    def forbidden(*args, **kwargs):
        raise AssertionError('Post-analysis annotation edit invoked forensic synthesis')
    monkeypatch.setattr(gui, 'build_summary_result', forbidden)
    for n in range(3):
        draft = deepcopy(window.osint_result)
        add_manual_match(draft, 'google', f'https://example.com/{n}', source_type='ai_gallery', notes=f'annotation {n}')
        assert window._commit_osint(window.session.session_id, draft)
        assert window.session.annotation_revision == n+1
        assert window.view_snapshot.annotation_revision == n+1
        assert window.session.report_current
        payload = json.loads(Path(window._report_paths['final_summary_json']).read_text(encoding='utf-8'))
        assert len(payload['annotations']['matches']) == n+1
        assert payload['reasoning_trace'] == json.loads(frozen)['reasoning_trace']
        synthesis = json.loads(window.view_snapshot.investigation_synthesis_json)
        assert payload['investigation_synthesis'] == synthesis
        assert synthesis['external_source_corroboration']['status'] == 'reviewed_manual_match'
        # Source category alone cannot provide image-specific origin support.
        assert 'Origin and editing history unresolved' in window.workspace.overview.finding_title.text()
        assert synthesis['revision_id'] in window.workspace.investigation_detail.toPlainText()
        assert 'annotation '+str(n) in window.summary_box.toPlainText()
    assert window.session.summary_json == frozen

    from osint_reverse_search import create_empty_osint_result
    assert window._commit_osint(window.session.session_id, create_empty_osint_result(images[0]))
    assert json.loads(window.view_snapshot.investigation_synthesis_json)['external_source_corroboration']['status'] == 'not_recorded'
    assert window.session.summary_json == frozen


def test_cancelled_dialog_and_switched_session_cannot_commit_annotations(window, images, monkeypatch):
    window.set_selected_file(images[0])
    first = window.session.session_id
    class Cancelled:
        def __init__(self, *args, **kwargs): pass
        def exec(self): return 0
    monkeypatch.setattr(gui, 'OSINTFindingDialog', Cancelled)
    assert window.workspace.source_context.isEnabled()
    window.workspace.source_context.click()
    assert window.session.annotation_revision == 0
    draft = deepcopy(window.osint_result)
    add_manual_match(draft, 'google', 'https://example.com/old')
    class SwitchDuringDialog(Cancelled):
        def exec(self):
            window.set_selected_file(images[1])
            return 1
        def get_data(self): return {'provider': 'google', 'page_url': 'https://example.com/unsaved'}
    monkeypatch.setattr(gui, 'OSINTFindingDialog', SwitchDuringDialog)
    window.add_osint_finding()
    assert window.session.session_id != first
    assert window.session.annotation_revision == 0 and not window.osint_result.matches
    assert not window._commit_osint(first, draft)
    mismatched = deepcopy(window.osint_result)
    mismatched.image_sha256 = '0' * 64
    revision = window.session.annotation_revision
    assert not window._commit_osint(window.session.session_id, mismatched)
    assert window.session.annotation_revision == revision


def test_annotation_save_failure_does_not_commit_draft(window, images, monkeypatch):
    window.set_selected_file(images[0])
    before = window.session.annotations_json
    draft = deepcopy(window.osint_result)
    add_manual_match(draft, 'google', 'https://example.com')
    def fail(*args): raise OSError('read only')
    monkeypatch.setattr(gui, 'save_osint_result', fail)
    assert not window._commit_osint(window.session.session_id, draft)
    assert window.session.annotation_revision == 0
    assert window.session.annotations_json == before
    assert not window.osint_result.matches


def test_report_failure_invalidates_and_can_retry(window, images, monkeypatch):
    token = invocation(window, images[0])
    window.on_analysis_finished(token, result_for(token))
    writer = gui.persist_report_snapshot
    def fail(*args): raise OSError('disk full')
    monkeypatch.setattr(gui, 'persist_report_snapshot', fail)
    assert not window.refresh_report_snapshot()
    assert not window.session.report_current
    assert window.open_json_button.isEnabled()  # explicit retry, no stale reveal
    monkeypatch.setattr(gui, 'persist_report_snapshot', writer)
    assert window.refresh_report_snapshot()
    assert window.session.report_current


def test_load_saved_result_without_source_and_corrupt_load_preserves_current(window, images, tmp_path):
    token = invocation(window, images[0])
    window.on_analysis_finished(token, result_for(token))
    pointer = window._report_paths['current_report']
    original_summary = window.session.summary_json
    old_id = window.session.session_id
    assert window.load_stored_summary(pointer)
    assert window.session.session_id != old_id
    assert window.session.summary_json == original_summary
    assert window.view_snapshot.summary.primary_hypothesis is not None
    assert window.refresh_report_snapshot()
    bad = tmp_path / 'bad.json'
    bad.write_text('not json', encoding='utf-8')
    active = window.session.session_id
    assert not window.load_stored_summary(bad)
    assert window.session.session_id == active


def test_invalid_selection_missing_source_and_clear_supersession(window, images, tmp_path):
    window.set_selected_file(images[0])
    identity = window.session.session_id
    bad = tmp_path / 'broken.png'
    bad.write_bytes(b'broken image')
    window.set_selected_file(bad)
    assert window.session.session_id == identity
    images[0].unlink()
    window.run_analysis()
    assert window.session.state == InvestigationState.FAILED
    assert window.summary_result is None
    window.set_selected_file(images[1])
    token = window.session.begin_analysis('normal', {}, {}, tmp_path)
    window.clear_ui()
    window._on_worker_status(token, 'late')
    window.on_analysis_finished(token, result_for(token))
    assert window.session.state == InvestigationState.EMPTY
    assert not window.run_button.isEnabled()


def test_real_gui_launch_path_freezes_settings_context_and_run_annotations(window, images, monkeypatch):
    import investigation_workers as workers
    created = []
    def factory(selected_file, output_dir, output_json, analysis_mode, *, settings_snapshot):
        state = AnalysisState(selected_file, output_dir, output_json, analysis_mode=analysis_mode)
        worker = ControlledWorker(state)
        created.append((worker, settings_snapshot))
        return worker
    monkeypatch.setattr(workers, 'AnalysisWorker', factory)
    window.set_selected_file(images[0])
    window.chk_screen.setChecked(True)
    window.run_analysis()
    token = window.session.invocation
    worker = created[0][0]
    # Annotation commits while processing are allowed, but cannot change the
    # launch-time forensic context or annotation version.
    window.mark_osint_reviewed_no_match()
    window.chk_screen.setChecked(False)
    until(window.workers.idle, lambda: not window.workers.busy, worker.gate.release)
    assert window.session.state == InvestigationState.COMPLETED
    assert dict(token.scene_context)['screen_origin'] is True
    assert token.annotation_revision == 0 and window.session.annotation_revision == 1
    payload = json.loads(Path(window._report_paths['final_summary_json']).read_text(encoding='utf-8'))
    assert payload['investigation']['analysis_annotation_revision'] == 0
    assert payload['investigation']['annotation_revision'] == 1
    assert payload['annotations']['analyst_reviewed'] is True
    assert payload['investigation']['analysis_annotations']['analyst_reviewed'] is False


def test_analysis_completes_inside_annotation_dialog_without_corrupting_draft(window, images, monkeypatch):
    token = invocation(window, images[0])
    class CompleteInsideDialog:
        def __init__(self, *args, **kwargs): pass
        def exec(self):
            window.on_analysis_finished(token, result_for(token))
            return 1
        def get_data(self):
            return {'provider': 'google', 'page_url': 'https://example.com/during-dialog'}
    monkeypatch.setattr(gui, 'OSINTFindingDialog', CompleteInsideDialog)
    window.add_osint_finding()
    assert window.session.state == InvestigationState.COMPLETED
    assert window.session.annotation_revision == 1
    assert window.session.report_current
    assert len(window.osint_result.matches) == 1


def test_source_replaced_before_run_or_during_processing_is_not_published(window, images):
    window.set_selected_file(images[0])
    Image.new('RGB', (20, 20), 'red').save(images[0])
    window.run_analysis()
    assert window.session.state == InvestigationState.EMPTY
    assert 'Source file changed' in window.status_label.text()
    token = invocation(window, images[0])
    Image.new('RGB', (21, 21), 'blue').save(images[0])
    window.on_analysis_finished(token, result_for(token))
    assert window.session.state == InvestigationState.FAILED
    assert window.summary_result is None


def test_legacy_annotations_with_same_stem_but_different_hash_are_not_imported(window, images, tmp_path):
    from osint_reverse_search import create_empty_osint_result, save_osint_result
    wrong = create_empty_osint_result(images[1])
    wrong.image_sha256 = 'different source'
    add_manual_match(wrong, 'google', 'https://example.com/wrong')
    save_osint_result(wrong, Path(window.settings['output_root']) / images[0].stem)
    window.set_selected_file(images[0])
    assert not window.osint_result.matches


def test_worker_construction_failure_leaves_retryable_failed_investigation(window, images, monkeypatch):
    def fail(*args): raise RuntimeError('worker construction failed')
    monkeypatch.setattr(window.workers, 'start', fail)
    window.set_selected_file(images[0])
    window.run_analysis()
    assert window.session.state == InvestigationState.FAILED
    assert window.run_button.isEnabled() and not window.workers.busy


def test_snapshot_listener_can_switch_investigation_during_completion(window, images):
    token = invocation(window, images[0])
    def switch(snapshot):
        if snapshot.session_id == token.session_id and snapshot.summary.status == 'completed':
            window.set_selected_file(images[1])
    window.snapshot_changed.connect(switch)
    window.on_analysis_finished(token, result_for(token))
    assert window.session.image_path == str(images[1].resolve())
    assert window.status_label.text() == 'File selected. No active result.'
    assert window.session.summary_json is None
    assert window._report_paths == {}


def test_archive_deletion_disabled_until_superseded_worker_retires(window, images):
    token = invocation(window, images[0])
    worker = ControlledWorker(result_for(token))
    window.workers.start(token, worker)
    window.set_selected_file(images[1])
    assert all(not action.isEnabled() for action in window._archive_actions)
    until(window.workers.idle, lambda: not window.workers.busy, worker.gate.release)
    assert all(action.isEnabled() for action in window._archive_actions)


def test_text_only_legacy_result_is_displayed_and_exported_without_prose_parsing(window, tmp_path):
    path = tmp_path / 'legacy.json'
    path.write_text(json.dumps({'full_text': 'Original narrative <unverified>; no structured hypothesis.'}), encoding='utf-8')
    assert window.load_stored_summary(path)
    assert 'Original narrative <unverified>' in window.summary_box.toPlainText()
    assert window.view_snapshot.summary.primary_hypothesis is None
    assert window.refresh_report_snapshot()
    html = Path(window._report_paths['final_summary_html']).read_text(encoding='utf-8')
    assert '&lt;unverified&gt;' in html
