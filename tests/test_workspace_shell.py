"""UI-2 native-widget contracts; no pixel-perfect or forensic reclassification tests."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path

import pytest
from PIL import Image
from PyQt6.QtCore import Qt, QSettings, QByteArray, QTimer, QRect
from PyQt6.QtGui import QPalette, QColor, QFontDatabase
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QScrollArea

import signallens_gui as gui
from gui_design_system import COLORS, LIGHT, TYPE, SPACE, GEOMETRY, apply_theme, lifecycle_color
from gui_components import (Panel, SectionHeader, StatusIndicator, ConfidenceIndicator,
                            EmptyState, NavigationItem, MetadataRow, CollapsibleSection, StatusMessage)
from gui_workspace_state import PREFIX, save_workspace, restore_workspace, ensure_visible
from signallens_settings import DEFAULT_SETTINGS
from signallens_controller import AnalysisState
from summary_types import SummaryResult
from settings_dialog import SettingsDialog
from osint_dialogs import OSINTFindingDialog


@pytest.fixture(scope='module')
def app():
    app = QApplication.instance() or QApplication([])
    # The Windows offscreen platform does not enumerate system font files.
    # Register the same installed UI font used by native Windows rendering.
    for filename in ('segoeui.ttf', 'segoeuib.ttf', 'consola.ttf'):
        path = Path('C:/Windows/Fonts') / filename
        if path.is_file():
            QFontDatabase.addApplicationFont(str(path))
    app.setQuitOnLastWindowClosed(False)
    return app


@pytest.fixture
def window(app, tmp_path, monkeypatch):
    settings = deepcopy(DEFAULT_SETTINGS)
    settings['output_root'] = str(tmp_path / 'analysis')
    monkeypatch.setattr(gui, 'load_settings', lambda: settings)
    preferences = QSettings(str(tmp_path / 'workspace.ini'), QSettings.Format.IniFormat)
    w = gui.SignalLensGui(ui_settings=preferences)
    w.resize(1280, 900)
    w.show()
    app.processEvents()
    yield w
    assert not w.workers.busy
    w.close()
    w.deleteLater()
    app.processEvents()


@pytest.fixture
def source(tmp_path):
    path = tmp_path / 'source.png'
    Image.new('RGB', (32, 48), 'gray').save(path)
    return path


def publish(window, source):
    window.set_selected_file(source)
    token = window.session.begin_analysis('normal', {}, window.settings, window.settings['output_root'])
    data = SummaryResult(full_text='Recorded narrative', full_html='<p>Recorded narrative</p>',
        reasoning_trace={'decision': {'primary_hypothesis': 'synthetic_origin', 'confidence_tier': 'Medium',
            'dominant_pattern': 'declared_synthetic_candidate', 'selection_reason': 'Recorded selection'},
            'hypothesis_assessments': [{'hypothesis_id': 'synthetic_origin', 'explanation': 'Unverified generation declaration.',
                'confidence_tier': 'Medium', 'supporting_evidence': ['metadata:DECLARED_SYNTHETIC'],
                'contradicting_evidence': [], 'moderating_evidence': [], 'contextual_evidence': [],
                'limitations': ['Metadata authenticity is unverified.'],
                'evidence_details': {'metadata:DECLARED_SYNTHETIC': {'label': 'Generation declaration', 'section': 'metadata',
                    'interpretation': 'An unverified declaration.'}}}],
            'provenance_evidence': {'state': 'unverified_generation_declaration', 'metadata_authenticity_verified': False},
            'pipeline_status': {'coverage': {'status': 'partial'}, 'stages': {'Region FFT': {'status': 'unavailable', 'reason': 'No reliable mask'}}}})
    state = AnalysisState(Path(token.image_path), Path(token.output_dir))
    state.output_dir.mkdir(parents=True)
    window.session.complete(token, state, data)
    window.analysis_state = state
    window.current_analysis_dir = state.output_dir
    window.update_summary()
    return token


def luminance(color):
    values = [v/255 for v in QColor(color).getRgb()[:3]]
    values = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(values, (.2126,.7152,.0722)))


def test_design_tokens_and_readable_text_contrast():
    for foreground in (COLORS.text, COLORS.secondary_text, COLORS.accent, COLORS.success, COLORS.warning, COLORS.error, COLORS.unavailable):
        for background in (COLORS.background, COLORS.panel):
            a,b = sorted((luminance(foreground),luminance(background)))
            assert (b+.05)/(a+.05) >= 4.5
    assert set(asdict(COLORS)) >= {'background', 'navigation', 'focus', 'selected', 'disabled_text', 'neutral'}
    assert SPACE == tuple(sorted(SPACE)) and TYPE.monospace != TYPE.family


def test_theme_scoped_to_root_and_can_accept_another_palette(app):
    before = app.styleSheet()
    dialog = QDialog()
    apply_theme(dialog)
    assert dialog.property('slTheme') == 'dark'
    assert dialog.palette().color(QPalette.ColorRole.Window).name() == COLORS.background
    assert app.styleSheet() == before
    apply_theme(dialog, LIGHT)
    assert dialog.palette().color(QPalette.ColorRole.Window).name() == LIGHT.background
    dialog.deleteLater()


@pytest.mark.parametrize('state', ['pending', 'analyzing', 'completed', 'failed', 'cancelled', 'unavailable', 'unknown'])
def test_lifecycle_status_is_textual_and_separate_from_confidence(app, state):
    status = StatusIndicator(state)
    confidence = ConfidenceIndicator('Inconclusive')
    assert status.text() and status.accessibleName().startswith('Investigation status:')
    assert 'Inconclusive' in confidence.text()
    assert '%' not in confidence.text()
    assert lifecycle_color('completed') != lifecycle_color('failed')


@pytest.mark.parametrize('tier', ['High', 'Medium', 'Low', 'Inconclusive', None])
def test_confidence_preserves_label_without_color_classification(app, tier):
    item = ConfidenceIndicator(tier)
    assert item.tier == tier
    assert item.text() == 'Confidence · ' + (tier or 'Unavailable')
    assert item.styleSheet() == ConfidenceIndicator('High').styleSheet()


def test_reusable_components_focus_copy_and_disclosure(app):
    panel = Panel('Title')
    header = SectionHeader('Heading', 'Description', status='Pending')
    empty = EmptyState()
    empty.set_message('Unavailable', 'Reason recorded')
    item = NavigationItem('Evidence')
    metadata = MetadataRow('ID', 'abc123')
    section = CollapsibleSection('Technical detail', metadata)
    assert item.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert metadata.value.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByMouse
    assert metadata.value.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByKeyboard
    assert header.status.text() == 'Pending'
    item.set_marker('Unavailable')
    assert 'Unavailable' in item.accessibleName()
    assert section.content.isHidden()
    section.toggle.click()
    assert not section.content.isHidden()
    assert empty.heading.text() == 'Unavailable'
    assert panel.layout().contentsMargins().left() == GEOMETRY.panel_padding


def test_all_destinations_and_keyboard_navigation_do_not_mutate_session(window, app, source):
    publish(window, source)
    before = (window.session.session_id, window.session.summary_json, window.session.annotation_revision)
    assert isinstance(window, QMainWindow)
    assert window.workspace.stack.count() == 6
    for destination in window.workspace.destinations:
        window.workspace.nav_items[destination].click()
        app.processEvents()
        assert window.workspace.current_destination == destination
        assert window.workspace.stack.currentWidget() is window.workspace.pages[destination]
        assert sum(b.isChecked() for b in window.workspace.nav_items.values()) == 1
        assert before == (window.session.session_id, window.session.summary_json, window.session.annotation_revision)
    window.activateWindow()
    window.workspace.nav_items['Reports'].setFocus()
    app.processEvents()
    QTest.keyClick(window, Qt.Key.Key_3, Qt.KeyboardModifier.ControlModifier)
    assert window.workspace.current_destination == 'Evidence'
    assert not window.workspace.navigate('Not a destination')


def test_empty_running_and_complete_states_are_distinct(window, source):
    assert not window.run_button.isEnabled()
    assert 'No completed' in window.workspace.finding_title.text()
    assert window.workspace.preview._image.isNull()
    window.set_selected_file(source)
    assert not window.workspace.preview._image.isNull()
    token = window.session.begin_analysis('normal', {}, window.settings, window.settings['output_root'])
    window.update_summary()
    window._on_worker_status(token, 'Measured stage is running')
    assert window.status_label.text() == 'Measured stage is running'
    assert window.workspace.lifecycle.state == 'analyzing'
    assert not window.workspace.progress.isHidden()
    assert window.workspace.confidence.tier is None
    assert 'Analysis in progress' == window.workspace.empty_states['Evidence'].heading.text()
    publish(window, source)
    assert window.workspace.confidence.tier == 'Medium'
    assert window.workspace.verification.value.text() == 'Unverified'
    assert 'unavailable' in window.workspace.stage_details.toPlainText()


def test_old_callbacks_and_old_snapshot_cannot_populate_new_workspace(window, source, tmp_path):
    old = publish(window, source)
    snapshot = window.view_snapshot
    other = tmp_path / 'other.png'
    Image.new('RGB', (12, 12), 'white').save(other)
    window.set_selected_file(other)
    assert not window.workspace.bind_snapshot(snapshot)
    window._on_worker_status(old, 'old status')
    window.on_analysis_error(old, 'old failure')
    assert window.workspace.evidence_details.toPlainText() == ''
    assert window.workspace.reasoning_details.toPlainText() == ''
    assert window.workspace.confidence.tier is None
    assert window.workspace.verification.value.text() == 'Unknown'
    assert 'old' not in window.status_label.text()


def test_report_and_annotation_snapshot_bind_without_recomputing_findings(window, source):
    publish(window, source)
    frozen = window.session.summary_json
    assert window.workspace.report_state.value.text() == 'Needs publication'
    assert window.refresh_report_snapshot()
    assert window.workspace.report_state.value.text() == 'Synchronized'
    window.mark_osint_reviewed_no_match()
    assert window.session.summary_json == frozen
    assert window.workspace.report_identity.value.text().endswith('/ 1')
    assert window.workspace.confidence.tier == 'Medium'
    assert window.workspace.report_state.value.text() == 'Synchronized'


def test_minimum_layout_keeps_navigation_and_analysis_actions_reachable(window, app):
    window.resize(GEOMETRY.minimum_width, GEOMETRY.minimum_height)
    app.processEvents()
    assert window.width() == GEOMETRY.minimum_width
    assert window.height() == GEOMETRY.minimum_height
    for button in (window.pick_button, window.run_button, window.clear_button, *window.workspace.nav_items.values()):
        assert button.isVisible()
        assert button.width() >= button.minimumSizeHint().width()
    assert window.statusBar().height() <= GEOMETRY.control_height + SPACE[1]
    for destination in window.workspace.destinations:
        window.workspace.navigate(destination)
        app.processEvents()
        assert window.workspace.pages[destination].isVisible()


def test_workspace_preferences_contain_no_forensic_content_and_restore(window, app, source, tmp_path):
    publish(window, source)
    window.workspace.navigate('Reasoning')
    window.workspace.splitter.setSizes([240, 1000])
    window.workspace.overview_splitter.setSizes([220, 350])
    save_workspace(window, window.ui_settings)
    values = {key: str(window.ui_settings.value(key)) for key in window.ui_settings.allKeys()}
    assert all(key.startswith(PREFIX) for key in values)
    assert str(source) not in json.dumps(values) and window.session.session_id not in json.dumps(values)
    other = gui.SignalLensGui(ui_settings=window.ui_settings)
    other.show()
    app.processEvents()
    assert other.workspace.current_destination == 'Reasoning'
    assert abs(other.workspace.splitter.sizes()[0]-window.workspace.splitter.sizes()[0]) < 12
    assert other.session.summary_json is None
    other.close()
    other.deleteLater()


def test_corrupt_and_offscreen_geometry_falls_back_to_visible_area(window, app):
    window.ui_settings.setValue(PREFIX+'geometry', QByteArray(b'not Qt geometry'))
    window.ui_settings.setValue(PREFIX+'destination', 'removed destination')
    window.ui_settings.setValue(PREFIX+'navigation', ['invalid', -40])
    window.move(-50000, -50000)
    restore_workspace(window, window.ui_settings)
    assert window.workspace.current_destination == 'Overview'
    assert any(screen.availableGeometry().contains(window.geometry().topLeft()) for screen in app.screens())


def test_settings_and_osint_dialog_workflows_still_open(window, source, app):
    seen = []
    def close_modal():
        modal = app.activeModalWidget()
        assert isinstance(modal, SettingsDialog)
        seen.append(modal.property('slTheme'))
        assert len(modal.findChildren(QScrollArea)) == 3
        modal.reject()
    QTimer.singleShot(0, close_modal)
    window.show_settings_dialog()
    assert seen == ['dark']
    window.set_selected_file(source)
    def cancel_osint():
        modal = app.activeModalWidget()
        assert isinstance(modal, OSINTFindingDialog)
        seen.append(modal.page_url_edit.text())
        modal.reject()
    QTimer.singleShot(0, cancel_osint)
    window.add_osint_finding()
    assert seen == ['dark', ''] and window.session.annotation_revision == 0


def test_legacy_narrative_and_artifact_access_still_available(window, source):
    publish(window, source)
    assert window.workspace.artifact_button.isEnabled()
    assert window.workspace.artifact_directory() == window.current_analysis_dir
    assert 'Recorded narrative' in window.summary_box.toPlainText()
    assert window.workspace.trace_button.isEnabled()
    assert 'Generation declaration' in window.workspace.evidence_details.toPlainText()
    assert 'Unverified generation declaration' in window.workspace.reasoning_details.toPlainText()


def test_status_text_remains_exact_but_layout_is_bounded(app):
    status = StatusMessage('Long status ' * 200)
    assert status.text() == 'Long status ' * 200
    assert status.toolTip() == status.text()
    assert status.minimumSizeHint().width() == 0
    assert status.height() == GEOMETRY.control_height


def test_maximized_preference_restores_without_investigation_data(window, app):
    window.showMaximized()
    app.processEvents()
    save_workspace(window, window.ui_settings)
    other = gui.SignalLensGui(ui_settings=window.ui_settings)
    assert other.windowState() & Qt.WindowState.WindowMaximized
    assert other.session.image_path is None and other.session.summary_json is None
    other.close()
    other.deleteLater()


def test_loaded_summary_updates_all_shell_views_without_new_analysis(window, source):
    publish(window, source)
    assert window.refresh_report_snapshot()
    pointer = window._report_paths['current_report']
    old_session = window.session.session_id
    assert window.load_stored_summary(pointer)
    assert window.session.session_id != old_session
    assert window.workspace.lifecycle.state == 'completed'
    assert window.workspace.confidence.tier == 'Medium'
    assert 'Generation declaration' in window.workspace.evidence_details.toPlainText()
    assert window.workspace.report_state.value.text() == 'Needs publication'
    assert window.workspace.artifact_button.isEnabled()


def test_same_session_superseded_analyzing_snapshot_is_rejected(window, source):
    window.set_selected_file(source)
    old = window.session.begin_analysis('normal', {}, window.settings, window.settings['output_root'])
    window.update_summary()
    old_snapshot = window.view_snapshot
    current = window.session.begin_analysis('subject_based', {}, window.settings, window.settings['output_root'])
    window.update_summary()
    assert old.session_id == current.session_id and old.analysis_id != current.analysis_id
    assert old_snapshot.result_id is window.view_snapshot.result_id is None
    assert not window.workspace.bind_snapshot(old_snapshot)
    assert window.workspace.lifecycle.state == 'analyzing'
