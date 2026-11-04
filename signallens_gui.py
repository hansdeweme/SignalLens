#signallens_gui.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
from  __future__ import annotations
# silence TensorFlow Lite’s C++ backend:
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "3"
os.environ["ABSL_LOGGING_MIN_LOG_LEVEL"] = "3"
#
import sys
import platform
import subprocess
import json
from copy import deepcopy
from types import SimpleNamespace
from uuid import uuid4
from html import escape
from   pathlib import Path
# PyQt6 GUI
from PyQt6.QtCore    import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui     import QGuiApplication, QDragEnterEvent, QDropEvent, QTextCharFormat, QColor, QTextCursor, QAction, QIcon
from PyQt6.QtWidgets import (QMainWindow, QDialog, QVBoxLayout, QTextBrowser, QPushButton, QMessageBox, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QGroupBox,QListWidgetItem, QTextEdit, QCheckBox, QComboBox, QLabel, QFileDialog, QLineEdit, QGridLayout, QMenuBar)
# local imports
from signallens_settings   import load_settings
from osint_reverse_search  import add_manual_match, build_osint_summary_text, delete_match, format_match_label
from osint_reverse_search  import load_osint_result, mark_reviewed_no_match, open_reverse_search, replace_match, save_osint_result
from osint_dialogs         import OSINTFindingDialog
from summary_synthesizer   import build_summary_result
from gui_design_system import apply_theme, log_color, display_html, GEOMETRY
from gui_workspace import WorkspaceShell
from gui_workspace_state import default_settings, restore_workspace, save_workspace, ensure_visible
from audit_manager         import AuditManager
from settings_dialog       import SettingsDialog 
from signallens_version    import VERSION, APP_VERSION, FEEDBACK_URL
from investigation_session import InvestigationSession, InvestigationState, json_snapshot
from investigation_presenters import build_presentation
from investigation_reports import (annotation_appendix, annotations_object, create_report_snapshot,
                                   persist_report_snapshot, load_investigation, forensic_html)
from investigation_workers import InvestigationWorkers

class SignalLensGui(QMainWindow):
    session_changed = pyqtSignal(object)
    snapshot_changed = pyqtSignal(object)

    def __init__(self, *, ui_settings=None) -> None:
        super().__init__()
        self.ui_settings = ui_settings if ui_settings is not None else default_settings()
        self.session = InvestigationSession()
        self.workers = InvestigationWorkers(self)
        self.workers.completed.connect(self.on_analysis_finished)
        self.workers.failed.connect(self.on_analysis_error)
        self.workers.status_changed.connect(self._on_worker_status)
        self.workers.logged.connect(self._on_worker_log)
        self.workers.idle.connect(self._workers_idle)
        self._closing = False
        self._report_snapshot = None
        self._report_paths = {}
        self._session_dir = None
        self.settings = load_settings()
        if self.settings is None:
            QMessageBox.warning(self, "Settings.json Not Found", "Cannot Start Application!")
            sys.exit()        
        self.setWindowTitle(f"Signal Lens - Local Visual Forensic Reasoning ({VERSION})")
        self.selected_file: Path | None = None
        self.current_image_path: Path | None = None
        self.current_analysis_dir: Path | None = None
        self.output_json: Path | None = None    
        self.osint_result = None
        self.setAcceptDrops(True)
        self.exif_payload = None
        self.ela_payload = None
        self.noise_payload = None
        self.cross_signal_payload = None
        self.fft_payload = None
        self.analysis_state = None
        self.sensor_origin_payload = None
        self.subject_boundary_payload = None
        self.compression_history_payload = None
        self.cfa_demosaic_payload = None
        self.summary_result = None
        self.region_masks_payload = None
        self.region_fft_payload = None
        self.boundary_focus_payload = None
        self.patch_spatial_payload = None
        self.subject_texture_consistency_payload = None
        self.subject_process_asymmetry_payload = None
        self.subject_material_realism_payload = None
        self.analysis_mode = "normal"       # default or subject_based patch profile for patch-based analyses, can be extended in the future with more options
        self.setWindowIcon(QIcon("signallens.png"))
        self._build_ui()  # creates the layout 
        self.setMinimumSize(GEOMETRY.minimum_width, GEOMETRY.minimum_height)
        self.resize(GEOMETRY.normal_width, GEOMETRY.normal_height)
        apply_theme(self)
        restore_workspace(self, self.ui_settings)
        self.refresh_osint_ui()
        self._publish_snapshot()

    def place_window_above_taskbar(self, margin: int = 18):
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        frame = self.frameGeometry()
        frame_width = frame.width()
        frame_height = frame.height()
        max_width = available.width() - (2 * margin)
        max_height = available.height() - (2 * margin)
        # Shrink if the outer frame is too large for the usable screen
        if frame_width > max_width or frame_height > max_height:
            width_delta = frame_width - self.width()
            height_delta = frame_height - self.height()
            new_width = min(self.width(), max_width - width_delta)
            new_height = min(self.height(), max_height - height_delta)
            self.resize(max(400, new_width), max(300, new_height))
            # Re-read after resize
            frame = self.frameGeometry()
            frame_width = frame.width()
            frame_height = frame.height()
        x = available.left() + (available.width() - frame_width) // 2
        y = available.bottom() - frame_height - margin + 1
        if y < available.top() + margin:
            y = available.top() + margin
        self.move(x, y)

    def _publish_snapshot(self):
        self.view_snapshot = build_presentation(self.session)
        snapshot = self.view_snapshot
        lifecycle = (self.session.session_id, self.session.state.value, snapshot.analysis_id)
        self.run_button.setEnabled(not self._closing and bool(self.session.image_path)
                                   and self.session.state != InvestigationState.ANALYZING)
        complete = self.session.state == InvestigationState.COMPLETED
        self.decision_trace_action.setEnabled(complete and self.has_decision_trace())
        self.open_json_button.setEnabled(complete and self.session.report_current)
        self.open_latest_audit_action.setEnabled(complete and self.current_analysis_dir is not None
                                                 and self.current_analysis_dir.is_dir())
        for action in self._archive_actions:
            action.setEnabled(not self.workers.busy and self.session.state != InvestigationState.ANALYZING)
        # Direct signal listeners may change selection. No widget mutations may
        # follow emission of this point-in-time snapshot.
        self.session_changed.emit(lifecycle)
        self.snapshot_changed.emit(snapshot)

    @pyqtSlot(object, str)
    def _on_worker_status(self, invocation, message):
        if not self._closing and self.session.accepts(invocation):
            self.status_label.setText(message)

    @pyqtSlot(object, str, str)
    def _on_worker_log(self, invocation, message, level):
        if not self._closing and self.session.accepts(invocation):
            self.log(message, level)

    def _commit_osint(self, session_id, draft):
        if self._closing or session_id != self.session.session_id:
            return False
        try:
            if json_snapshot(draft) == self.session.annotations_json:
                return False
            staging = self._session_dir / f'.annotation-{uuid4().hex}'
            saved = save_osint_result(draft, staging)
            payload = json.loads(saved.read_text(encoding='utf-8'))
            payload['investigation'] = {'session_id': session_id,
                                       'annotation_revision': self.session.annotation_revision + 1}
            saved.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
            saved.replace(self._session_dir / 'osint_results.json')
            try:
                staging.rmdir()  # empty staging directory; cleanup is not publication
            except OSError:
                pass
        except Exception as exc:
            self.status_label.setText(f'Annotations not saved: {exc}')
            self.log(str(exc), 'error')
            return False
        self.session.commit_annotations(draft)
        self.osint_result = annotations_object(json.loads(self.session.annotations_json))
        self.refresh_osint_ui()
        self.update_summary()
        if self.session.session_id != session_id:
            return True
        if self.session.state == InvestigationState.COMPLETED:
            self.status_label.setText('OSINT annotations updated; forensic findings remain frozen.')
            self.refresh_report_snapshot()
        return True

    def refresh_report_snapshot(self):
        if self._closing or self.session.state != InvestigationState.COMPLETED:
            return False
        try:
            snapshot = create_report_snapshot(self.session)
            self._report_paths = persist_report_snapshot(self.session, snapshot, self.current_analysis_dir)
            self._report_snapshot = snapshot
            recorder = getattr(self.session.analysis_result, 'run_recorder', None)
            if recorder:
                recorder.add_artifact('summary_outputs', self._report_paths)
                recorder.add_artifact('investigation', snapshot.payload()['investigation'])
            self.log(f'Report snapshot synchronized: annotation revision {self.session.annotation_revision}')
        except Exception as exc:
            self.session.report_revision = None
            self._report_snapshot = None
            self.status_label.setText(f'Report not synchronized: {exc}. Use Open Results Folder to retry.')
            self.log(str(exc), 'error')
            self._publish_snapshot()
            # Keep the existing results button available as an explicit retry.
            self.open_json_button.setEnabled(True)
            return False
        self._publish_snapshot()
        return (self.session.session_id == snapshot.session_id
                and self.session.revision_key == (snapshot.result_id, snapshot.annotation_revision))

    def open_stored_summary(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open stored SignalLens summary', '', 'JSON files (*.json)')
        if path:
            self.load_stored_summary(Path(path))

    def load_stored_summary(self, path):
        if self._closing:
            return False
        try:
            imported = load_investigation(path)
            annotations = annotations_object(json.loads(imported.annotations_json))
        except Exception as exc:
            QMessageBox.warning(self, 'Stored result could not be loaded', str(exc))
            return False
        self.session.cancel()
        self.session = imported
        self.clear_analysis_state()
        self.selected_file = self.current_image_path = Path(imported.image_path) if imported.image_path else None
        self._session_dir = (Path(load_settings()['output_root']).resolve()
                             / (self.selected_file.stem if self.selected_file else 'imported') / imported.session_id)
        self.current_analysis_dir = self._session_dir / imported.result_id
        self.output_json = None
        self.osint_result = annotations
        self.file_edit.setText(imported.image_path or 'Source path not recorded in stored result')
        self.drop_label.setText('Stored result loaded — new import identity; no analysis executed')
        self.log_box.clear()
        self.refresh_osint_ui()
        self.update_summary()
        if self.session.session_id != imported.session_id:
            return False
        self.status_label.setText('Stored result loaded. Historical findings preserved; report export creates a new snapshot.')
        self.open_json_button.setEnabled(True)
        return True

    @pyqtSlot()
    def _workers_idle(self):
        if self._closing:
            QTimer.singleShot(0, self.close)
        else:
            self._publish_snapshot()

    def closeEvent(self, event):
        if self.workers.busy:
            self._closing = True
            self.session.cancel()
            self.setEnabled(False)
            self.status_label.setText('Closing: waiting for analysis workers to finish safely…')
            self._publish_snapshot()
            event.ignore()
            return
        save_workspace(self, self.ui_settings)
        event.accept()

    def _create_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        # File
        file_menu = self.menu_bar.addMenu("File")
        load_action = QAction("Open Stored Summary…", self)
        load_action.triggered.connect(self.open_stored_summary)
        file_menu.addAction(load_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # Tools
        tools_menu = self.menu_bar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        tools_menu.addAction(settings_action)        
        tools_menu.addSeparator()
        
        self.decision_trace_action = QAction("Decision Trace", self)
        self.decision_trace_action.triggered.connect(self.show_decision_trace_dialog)
        tools_menu.addAction(self.decision_trace_action)
        self.decision_trace_action.setEnabled(False)
        
        self.open_latest_audit_action = QAction("Open Latest Audit Folder", self)
        self.open_latest_audit_action.setEnabled(False)
        self.open_latest_audit_action.triggered.connect(self.open_latest_audit_folder)
        tools_menu.addAction(self.open_latest_audit_action)
        tools_menu.addSeparator()
        
        audit_overview_action = QAction("Audit Trail Overview", self)
        audit_overview_action.triggered.connect(self.show_audit_trail_overview)
        tools_menu.addAction(audit_overview_action)
        
        cleanup_audit_action = QAction("Cleanup Audit Trails", self)
        cleanup_audit_action.triggered.connect(self.cleanup_audit_trails)
        tools_menu.addAction(cleanup_audit_action)             
        
        delete_old_action = QAction("Delete Audit Trails Older Than 30 Days", self)
        delete_old_action.triggered.connect(self.delete_audit_trails_older_than_30_days)
        tools_menu.addAction(delete_old_action)

        remove_visuals_action = QAction("Remove Visual Artifacts Only", self)
        remove_visuals_action.triggered.connect(self.remove_visual_audit_artifacts)
        tools_menu.addAction(remove_visuals_action)                   
        self._archive_actions = [cleanup_audit_action, delete_old_action, remove_visuals_action]
        # Help
        help_menu = self.menu_bar.addMenu("Help")
        
        about_action = QAction("About SignalLens", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
                
        known_limitations_action = QAction("Known Limitations", self)
        known_limitations_action.triggered.connect(self.show_known_limitations_dialog)
        help_menu.addAction(known_limitations_action)                
        help_menu.addSeparator()

        feedback_action = QAction("Send Feedback", self)
        feedback_action.triggered.connect(self.send_feedback)
        help_menu.addAction(feedback_action)        


    
    def _build_ui(self) -> None:
        self._create_menu_bar()
        self.setMenuBar(self.menu_bar)
        self.workspace = WorkspaceShell(self)
        self.setCentralWidget(self.workspace)
        self.snapshot_changed.connect(self.workspace.bind_snapshot)

    def build_osint_group(self) -> QGroupBox:
        group = QGroupBox("OSINT / Reverse Search")
        self.btn_google = QPushButton("Google Lens")
        self.btn_yandex = QPushButton("Yandex")
        self.btn_tineye = QPushButton("TinEye")
        self.btn_mark_no_match = QPushButton("Mark Reviewed / No Match")
        self.btn_add_osint = QPushButton("Add Finding")
        self.btn_edit_osint = QPushButton("Edit Selected")
        self.btn_delete_osint = QPushButton("Delete Selected")
        self.osint_status_label = QLabel("OSINT status: no image loaded")
        self.osint_findings_list = QListWidget()
        button_row = QGridLayout()
        for index, button in enumerate((self.btn_google, self.btn_yandex, self.btn_tineye,
                self.btn_mark_no_match, self.btn_add_osint, self.btn_edit_osint, self.btn_delete_osint)):
            button_row.addWidget(button, index // 3, index % 3)
        layout = QVBoxLayout(group)
        layout.addLayout(button_row)
        layout.addWidget(self.osint_status_label)
        layout.addWidget(self.osint_findings_list)
        self.osint_findings_list.currentRowChanged.connect(self.update_osint_buttons)
        self.btn_google.clicked.connect(lambda: self.open_osint_engine("google"))
        self.btn_yandex.clicked.connect(lambda: self.open_osint_engine("yandex"))
        self.btn_tineye.clicked.connect(lambda: self.open_osint_engine("tineye"))
        self.btn_mark_no_match.clicked.connect(self.mark_osint_reviewed_no_match)
        self.btn_add_osint.clicked.connect(self.add_osint_finding)
        self.btn_edit_osint.clicked.connect(self.edit_selected_osint_finding)
        self.btn_delete_osint.clicked.connect(self.delete_selected_osint_finding)
        return group

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        self.settings = deepcopy(load_settings())

    def show_about_dialog(self):
        version = VERSION
        version_text = f"SignalLens, {version} \n\nForensic signal analysis for AI-generated, AI-enhanced, hybrid and plain camera-origin images.\n\n© 2025–2026 Hans De Weme"
        QMessageBox.about(self, "About SignalLens", version_text)

    def log(self, message: str, level: str = "info") -> None:
        """
        Append a softly colored log line to the QTextEdit log box.
        Uses semantic colors from gui_semantics.py.
        """
        if not hasattr(self, "log_box") or self.log_box is None:
            return
        color = log_color(level)
        cursor = self.log_box.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.insertText(message + "\n", fmt)
        self.log_box.setTextCursor(cursor)
        self.log_box.ensureCursorVisible()
        
    def update_summary(self) -> None:
        # Rendering is a projection of the frozen analysis, never new synthesis.
        data = self.session.summary_data()
        self.summary_result = SimpleNamespace(**data) if data else None
        if data:
            self.summary_box.setHtml(display_html(forensic_html(data) + annotation_appendix(self.session)[1]))
        else:
            self.summary_box.clear()
        self._report_snapshot = None
        self._publish_snapshot()

    def on_analysis_mode_changed(self, value: str) -> None:
        self.analysis_mode = value
        self.log(f"Patch profile set to: {value}")                
                
    def clear_analysis_state(self) -> None:
        for name in tuple(vars(self)):
            if name.endswith('_payload'):
                setattr(self, name, None)
        self.analysis_state = self.summary_result = None
        self.osint_result = None
        self._report_snapshot = None
        self._report_paths = {}
        self.decision_trace_action.setEnabled(False)
        self.open_latest_audit_action.setEnabled(False)
        self.open_json_button.setEnabled(False)
    
    def clear_ui(self) -> None:
        self.session.cancel()
        self.session = InvestigationSession()
        self.clear_analysis_state()
        self.selected_file = self.current_image_path = self.current_analysis_dir = self.output_json = None
        self._session_dir = None
        self.file_edit.clear()
        self.summary_box.clear()
        self.log_box.clear()
        for checkbox in (self.chk_natural, self.chk_decorative, self.chk_smartphone, self.chk_screen):
            checkbox.setChecked(False)
        self.drop_label.setText("Drag and drop an image here, or use 'Choose Image'")
        self.status_label.setText('Ready. Previous invocation superseded.' if self.workers.busy else 'Ready.')
        self.refresh_osint_ui()
        self._publish_snapshot()
    
    def is_supported_image(self, path: Path) -> bool:
        return path.is_file() and path.suffix.lower() in self.settings.get("supported_extensions")

    def set_selected_file(self, path: Path) -> None:
        if self._closing:
            return
        try:
            self.settings = deepcopy(load_settings())
            path = Path(path).resolve()
            if not self.is_supported_image(path):
                raise ValueError('Select an existing supported image file.')
            from PIL import Image
            with Image.open(path) as image:
                image.verify()
            from osint_reverse_search import create_empty_osint_result
            annotations = create_empty_osint_result(path)
            # Legacy stem folders may collide. Import annotations only when their
            # canonical file hash matches this source; never merge by filename alone.
            legacy = Path(self.settings['output_root']) / path.stem / 'osint_results.json'
            if legacy.is_file():
                candidate = load_osint_result(legacy)
                if candidate.image_sha256 == annotations.image_sha256:
                    annotations = candidate
            session = InvestigationSession.selected(path, annotations)
        except Exception as exc:
            QMessageBox.warning(self, 'Image selection failed', str(exc))
            return
        self.session.cancel()
        self.session = session
        self.clear_analysis_state()
        self.selected_file = self.current_image_path = path
        self._session_dir = Path(self.settings['output_root']).resolve() / path.stem / session.session_id
        self.current_analysis_dir = self._session_dir
        self.output_json = None
        self.osint_result = annotations_object(json.loads(session.annotations_json))
        self.file_edit.setText(str(path))
        self.drop_label.setText(f'Selected:\n{path.name}')
        self.summary_box.clear()
        self.log_box.clear()
        self.log(f'Selected file: {path} — investigation {session.session_id}')
        self.status_label.setText('File selected. No active result.')
        self.refresh_osint_ui()
        self._publish_snapshot()
          
    def pick_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose image file",
            "",
            self.settings.get("file_masks")
        )
        if not file_path:
            return
        path = Path(file_path)
        if not self.is_supported_image(path):
            QMessageBox.warning(self, "Unsupported file", "Please choose a supported image file.")
            return
        self.set_selected_file(path)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime = event.mimeData()
        if not mime.hasUrls():
            event.ignore()
            return
        for url in mime.urls():
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if self.is_supported_image(path):
                event.acceptProposedAction()
                self.drop_label.setText("Drop image to analyze")
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        if self.selected_file is not None:
            self.drop_label.setText(f"Selected:\n{self.selected_file.name}")
        else:
            self.drop_label.setText("Drag and drop an image here, or use 'Choose Image'")
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        mime = event.mimeData()
        if not mime.hasUrls():
            event.ignore()
            return
        for url in mime.urls():
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if self.is_supported_image(path):
                self.set_selected_file(path)
                event.acceptProposedAction()
                return
        QMessageBox.warning(self, "Unsupported file", "No supported image file was found in the dropped items.")
        event.ignore()

    def clear_summary(self) -> None:
        self.summary_box.clear()
        
    #----------------------------------------------------------------   
    # This method opens the selected OSINT reverse-search engine with the current image and OSINT results, 
    # allowing the user to investigate potential matches. It also saves the current OSINT state and refreshes the UI to reflect any changes.
    #----------------------------------------------------------------
    def update_osint_buttons(self) -> None:
        row = self.osint_findings_list.currentRow()
        has_real_selection = (
            self.osint_result is not None
            and len(self.osint_result.matches) > 0
            and 0 <= row < len(self.osint_result.matches)
        )
        self.btn_edit_osint.setEnabled(has_real_selection)
        self.btn_delete_osint.setEnabled(has_real_selection)

    def open_osint_engine(self, provider: str) -> None:
        if not self.ensure_osint_ready():
            return
        session_id = self.session.session_id
        draft = deepcopy(self.osint_result)
        try:
            open_reverse_search(provider, draft)
            self._commit_osint(session_id, draft)
            QMessageBox.information(self, 'Reverse Search', "Perform your search in the browser, then click 'Add Finding' to record results.")
        except Exception as exc:
            QMessageBox.critical(self, 'OSINT Error', str(exc))

    def add_osint_finding(self) -> None:
        if not self.ensure_osint_ready():
            return
        session_id = self.session.session_id
        draft = deepcopy(self.osint_result)
        dialog = OSINTFindingDialog(self)
        if dialog.exec():
            add_manual_match(draft, **dialog.get_data())
            self._commit_osint(session_id, draft)

    def edit_selected_osint_finding(self) -> None:
        if not self.ensure_osint_ready():
            return
        row = self.osint_findings_list.currentRow()
        if not 0 <= row < len(self.osint_result.matches):
            return
        session_id = self.session.session_id
        draft = deepcopy(self.osint_result)
        dialog = OSINTFindingDialog(self, existing_match=draft.matches[row])
        if dialog.exec():
            replace_match(draft, index=row, **dialog.get_data())
            self._commit_osint(session_id, draft)

    def delete_selected_osint_finding(self) -> None:
        if not self.ensure_osint_ready():
            return
        draft = deepcopy(self.osint_result)
        row = self.osint_findings_list.currentRow()
        if 0 <= row < len(draft.matches):
            delete_match(draft, row)
            self._commit_osint(self.session.session_id, draft)

    def mark_osint_reviewed_no_match(self) -> None:
        if not self.ensure_osint_ready():
            return
        draft = deepcopy(self.osint_result)
        mark_reviewed_no_match(draft)
        self._commit_osint(self.session.session_id, draft)

    def refresh_osint_ui(self) -> None:
        self.osint_findings_list.clear()
        if self.osint_result is None:
            self.osint_status_label.setText("OSINT status: no image loaded")
            self.btn_edit_osint.setEnabled(False)
            self.btn_delete_osint.setEnabled(False)
            return
        self.osint_status_label.setText(build_osint_summary_text(self.osint_result))
        has_findings = len(self.osint_result.matches) > 0
        if not has_findings:
            placeholder = QListWidgetItem("(No findings yet — use 'Add Finding')")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.osint_findings_list.addItem(placeholder)
            self.btn_edit_osint.setEnabled(False)
            self.btn_delete_osint.setEnabled(False)
            return
        for match in self.osint_result.matches:
            self.osint_findings_list.addItem(QListWidgetItem(format_match_label(match)))
        self.osint_findings_list.setCurrentRow(0)
        self.update_osint_buttons()
    
    def ensure_osint_ready(self) -> bool:
        if self._closing or self.current_image_path is None or self._session_dir is None:
            QMessageBox.information(self, 'OSINT', 'Load an image with an available source first.')
            return False
        self.osint_result = annotations_object(json.loads(self.session.annotations_json))
        return self.osint_result is not None
    
    #----------------------------------------------------------------
    # This method runs the analysis pipeline: EXIF analysis, ELA, noise analysis, cross-signal analysis, and FFT analysis. 
    # Each step is wrapped in a try-except block to handle errors gracefully without crashing the entire pipeline.
    # It updates the summary and log with results.
    #----------------------------------------------------------------
    def run_analysis(self) -> None:
        if self._closing or not self.session.image_path:
            return
        if not Path(self.session.image_path).is_file():
            self.session.cancel()
            self.session.state = InvestigationState.FAILED
            self.session.error = 'Selected source file no longer exists.'
            self.session.summary_json = self.session.result_id = None
            self.session.analysis_result = None
            self.session.report_revision = None
            self.clear_analysis_state()
            self.update_summary()
            self.status_label.setText(self.session.error)
            return
        self.settings = deepcopy(load_settings())
        from osint_reverse_search import sha256_of_file
        try:
            source_changed = (self.session.source_sha256 is not None
                              and sha256_of_file(self.session.image_path) != self.session.source_sha256)
        except OSError as exc:
            self.clear_ui()
            self.status_label.setText(f'Source file could not be read: {exc}')
            return
        if source_changed:
            self.clear_ui()
            self.status_label.setText('Source file changed. Select it again to begin a new investigation.')
            return
        context = {'natural_repetition': self.chk_natural.isChecked(),
                   'decorative_geometric': self.chk_decorative.isChecked(),
                   'smartphone_computational': self.chk_smartphone.isChecked(),
                   'screen_origin': self.chk_screen.isChecked()}
        invocation = self.session.begin_analysis(self.analysis_mode, context, self.settings, self.settings['output_root'])
        self.current_analysis_dir = Path(invocation.output_dir)
        self._session_dir = self.current_analysis_dir.parent
        self.output_json = self.current_analysis_dir / f'{Path(invocation.image_path).stem}_exif_signals.json'
        self.clear_analysis_state()
        self.osint_result = annotations_object(json.loads(self.session.annotations_json))
        self.summary_box.clear()
        self.status_label.setText('Running analysis…')
        self._publish_snapshot()
        try:
            if not self.session.accepts(invocation):
                return
            self.workers.start(invocation)
        except Exception as exc:
            self.on_analysis_error(invocation, str(exc))

    @pyqtSlot(object, object)
    def on_analysis_finished(self, invocation, state):
        if self._closing or not self.session.accepts(invocation):
            return
        try:
            from osint_reverse_search import sha256_of_file
            if invocation.source_sha256 and sha256_of_file(invocation.image_path) != invocation.source_sha256:
                raise ValueError('Source file changed during analysis; result was not published.')
            if (Path(state.selected_file).resolve() != Path(invocation.image_path).resolve()
                    or Path(state.output_dir).resolve() != Path(invocation.output_dir).resolve()):
                raise ValueError('Worker result does not match its invocation source/output.')
            # This is the existing, authoritative synthesis operation, invoked once
            # using launch-time context and annotations. Post-run edits do not call it.
            summary = build_summary_result(state,
                annotations_object(json.loads(invocation.annotations_json)),
                scene_context=dict(invocation.scene_context))
            if not self.session.complete(invocation, state, summary):
                return
        except Exception as exc:
            self.on_analysis_error(invocation, str(exc))
            return
        self.analysis_state = self.session.analysis_result
        for name in tuple(vars(self)):
            if name.endswith('_payload'):
                setattr(self, name, getattr(state, name, None))
        self.update_summary()
        if self.session.session_id != invocation.session_id or self.session.result_id != invocation.analysis_id:
            return
        self.status_label.setText('Analysis completed. Findings frozen to this invocation.')
        self.refresh_report_snapshot()
  
    @pyqtSlot(object, str)
    def on_analysis_error(self, invocation, message: str):
        if self._closing or not self.session.fail(invocation, message):
            return
        self.clear_analysis_state()
        self.status_label.setText(f'Analysis failed: {message}')
        self.log(message, 'error')
        self.update_summary()
  

    def open_latest_audit_folder(self):
        import os
        from pathlib import Path
        from PyQt6.QtWidgets import QMessageBox

        output_dir = self.current_analysis_dir if self.session.state == InvestigationState.COMPLETED else None

        if not output_dir:
            QMessageBox.information(
                self,
                "Open Audit Folder",
                "No audit folder is available yet. Run an analysis first.",
            )
            return

        path = Path(output_dir).resolve()

        if not path.exists():
            QMessageBox.warning(
                self,
                "Open Audit Folder",
                f"The audit folder no longer exists:\n\n{path}",
            )
            return

        os.startfile(path)
    
  
    #--------------------------------------------------
    # This method attempts to open the output folder containing the analysis results, and selects the JSON file if possible. It handles different operating systems and provides user feedback if the file or folder cannot be opened.
    #--------------------------------------------------
    def open_output_folder(self) -> None:
        if self.session.state != InvestigationState.COMPLETED:
            QMessageBox.information(self, 'Results', 'No completed active result is available.')
            return
        if not self.refresh_report_snapshot():
            return
        path = Path(self._report_paths['final_summary_json']).resolve()
        try:
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['explorer', '/select,', str(path)], check=False)
            elif system == 'Darwin':
                subprocess.run(['open', '-R', str(path)], check=False)
            else:
                subprocess.run(['xdg-open', str(path.parent)], check=False)
        except Exception as exc:
            QMessageBox.warning(self, 'Could not open folder', str(exc))

    #====================================================
    # show to decision trace
    #====================================================
    def show_decision_trace_dialog(self):
        summary_result = getattr(self, "summary_result", None)
        reasoning_trace = getattr(summary_result, "reasoning_trace", None) if summary_result else None
        if not reasoning_trace:
            QMessageBox.information(
                self,
                "Decision Trace",
                "No decision trace is available yet. Run an analysis first.",
            )
            return
        decision = reasoning_trace.get("decision", {}) or {}
        route_trace = reasoning_trace.get("decision_route_trace", []) or []
        scorecard = reasoning_trace.get("scorecard", {}) or {}
        derived = reasoning_trace.get("derived_signals", {}) or {}
        priors = reasoning_trace.get("contextual_priors", {}) or {}

        def fmt(value):
            if isinstance(value, float):
                return f"{value:.4f}"
            if value is None:
                return ""
            return escape(str(value))

        html = [
            """
            <html>
            <body style="font-family: Segoe UI, Arial, sans-serif; font-size: 13px;">
            <h2>SignalLens Decision Trace</h2>
            """
        ]
        html.append("<h3>Final Decision</h3><ul>")
        html.append(f"<li><b>Branch:</b> {fmt(decision.get('decision_branch'))}</li>")
        html.append(f"<li><b>Pattern:</b> {fmt(decision.get('dominant_pattern'))}</li>")
        html.append(f"<li><b>Confidence:</b> {fmt(decision.get('confidence_tier'))}</li>")
        html.append(f"<li><b>Polarity:</b> {fmt(decision.get('polarity'))}</li>")
        html.append("</ul>")
        html.append("<h3>Contextual Priors</h3><ul>")
        if priors:
            for k, v in priors.items():
                html.append(f"<li><b>{escape(str(k))}:</b> {fmt(v)}</li>")
        else:
            html.append("<li>No contextual priors recorded.</li>")
        html.append("</ul>")
        html.append("<h3>Scorecard Highlights</h3><ul>")
        for key in [
            "suspicious_score",
            "benign_score",
            "local_edit_support_score",
            "clone_support_score",
            "camera_counter_support",
            "synthetic_boost",
            "edit_boost",
            "provenance_boost",
            "caution_penalty",
            "contextual_false_positive_risk",
        ]:
            if key in scorecard:
                html.append(f"<li><b>{key}:</b> {fmt(scorecard.get(key))}</li>")
        html.append("</ul>")
        html.append("<h3>Derived Signals</h3><ul>")
        for key in [
            "person_mask_reliable",
            "subject_area_ratio",
            "boundary_support_ratio",
            "boundary_support_low",
            "boundary_reliability_score",
            "strong_local_edit",
            "strong_cross",
            "region_geometry_unreliable",
            "patch_structured",
            "fft_structured",
            "camera_like_support",
            "metadata_synthetic",
            "provenance_clean",
            "local_signals_weak",
        ]:
            if key in derived:
                html.append(f"<li><b>{key}:</b> {fmt(derived.get(key))}</li>")
        html.append("</ul>")
        html.append("<h3>Route Evaluation</h3>")
        html.append(
            """
            <table border="1" cellspacing="0" cellpadding="6" style="border-collapse: collapse; width: 100%;">
            <tr style="background:#e5e7eb;">
                <th align="left">Route</th>
                <th align="left">Matched</th>
                <th align="left">Reason</th>
                <th align="left">Pattern</th>
                <th align="left">Confidence</th>
                <th align="left">Polarity</th>
            </tr>
            """
        )
        if route_trace:
            for item in route_trace:
                matched = bool(item.get("matched"))
                bg = "#dcfce7" if matched else "#f9fafb"
                html.append(f'<tr style="background:{bg};">')
                html.append(f"<td>{fmt(item.get('route'))}</td>")
                html.append(f"<td>{fmt(matched)}</td>")
                html.append(f"<td>{fmt(item.get('reason'))}</td>")
                html.append(f"<td>{fmt(item.get('pattern'))}</td>")
                html.append(f"<td>{fmt(item.get('confidence'))}</td>")
                html.append(f"<td>{fmt(item.get('polarity'))}</td>")
                html.append("</tr>")
        else:
            html.append('<tr><td colspan="6">No route trace recorded.</td></tr>')

        html.append("</table>")
        html.append("</body></html>")
        dialog = QDialog(self)
        dialog.setWindowTitle("SignalLens Decision Trace")
        dialog.resize(1050, 750)
        layout = QVBoxLayout(dialog)
        viewer = QTextBrowser(dialog)
        viewer.setHtml(display_html("\n".join(html)))
        layout.addWidget(viewer)
        close_btn = QPushButton("Close", dialog)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def has_decision_trace(self) -> bool:
        summary_result = getattr(self, "summary_result", None)
        if summary_result is None:
            return False
        trace = getattr(summary_result, "reasoning_trace", None)
        if not isinstance(trace, dict):
            return False
        return bool(trace.get("decision") or trace.get("decision_route_trace"))

    # -------------------------------------------------
    # manage audittrails in output folder: .\analyzed
    #-------------------------------------------------
    def show_audit_trail_overview(self):
        manager = AuditManager("analyzed")
        stats = manager.get_archive_stats()
        runs = manager.list_runs()
        largest = stats.get("largest_run") or {}
        html = f"""
        <h2>Audit Trail Overview</h2>
        <p><b>Archive folder:</b> {stats["analyzed_dir"]}</p>
        <p><b>Analysis folders:</b> {stats["run_count"]}</p>
        <p><b>Total storage:</b> {stats["total_mb"]} MB ({stats["total_gb"]} GB)</p>
        <p><b>Average run size:</b> {stats["average_mb"]} MB</p>
        <p><b>Largest run:</b> {largest.get("name", "-")} ({largest.get("size_mb", "-")} MB)</p>
        <h3>Recent Analysis Runs</h3>
        <table border="1" cellspacing="0" cellpadding="6">
            <tr>
                <th>Folder</th>
                <th>Size MB</th>
                <th>Files</th>
                <th>Folders</th>
                <th>Modified</th>
            </tr>
        """
        for run in runs[:100]:
            html += f"""
            <tr>
                <td>{run.name}</td>
                <td>{run.size_mb}</td>
                <td>{run.file_count}</td>
                <td>{run.folder_count}</td>
                <td>{run.modified_at}</td>
            </tr>
            """
        html += "</table>"
        dialog = QDialog(self)
        dialog.setWindowTitle("Audit Trail Overview")
        dialog.resize(900, 650)
        layout = QVBoxLayout(dialog)
        viewer = QTextBrowser(dialog)
        viewer.setHtml(display_html(html))
        layout.addWidget(viewer)
        close_btn = QPushButton("Close", dialog)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def cleanup_audit_trails(self):
        from PyQt6.QtWidgets import QMessageBox
        manager = AuditManager("analyzed")
        stats = manager.get_archive_stats()
        if stats["run_count"] == 0:
            QMessageBox.information(self, "Cleanup Audit Trails", "No audit trails found.", )
            return
        reply = QMessageBox.warning( self,
            "Cleanup Audit Trails",
            f"This will delete all audit trail folders in:\n\n"
            f"{stats['analyzed_dir']}\n\n"
            f"Analysis folders: {stats['run_count']}\n"
            f"Storage used: {stats['total_mb']} MB\n\n"
            f"This cannot be undone.\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        deleted = manager.delete_all_runs()
        QMessageBox.information(self, "Cleanup Complete", f"Deleted {deleted} audit trail folders.",)

    def delete_audit_trails_older_than_30_days(self):
        from PyQt6.QtWidgets import QMessageBox
        manager = AuditManager("analyzed")
        reply = QMessageBox.warning(
            self,
            "Delete Old Audit Trails",
            "This will permanently delete all audit trail folders older than 30 days.\n\n"
            "This cannot be undone.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        deleted = manager.delete_runs_older_than_days(30)
        QMessageBox.information(self, "Cleanup Complete", f"Deleted {deleted} audit trail folders older than 30 days.",)

    def remove_visual_audit_artifacts(self):
        from PyQt6.QtWidgets import QMessageBox
        manager = AuditManager("analyzed")
        reply = QMessageBox.warning(self,
            "Remove Visual Artifacts",
            "This will delete visual artifact files from all audit trails "
            "(.png, .jpg, .jpeg, .webp, .bmp, .tif, .tiff).\n\n"
            "JSON files, logs, summaries, and reasoning traces will be kept.\n\n"
            "This cannot be undone.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        result = manager.remove_visual_artifacts_only()
        QMessageBox.information(self, "Visual Cleanup Complete",
            f"Deleted {result['deleted_files']} visual artifact files.\n"
            f"Freed {result['deleted_mb']} MB.",
        )

    def show_known_limitations_dialog(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Known Limitations",
            (
                "SignalLens is an analytical support tool, not an absolute truth machine.\n\n"
                "Its conclusions should be interpreted as forensic reasoning based on available "
                "signals, not as final proof that an image is real, edited, synthetic, or AI-generated.\n\n"
                "Current limitations:\n\n"
                "1. No absolute authenticity guarantee\n"
                "SignalLens evaluates signal patterns and produces the most plausible forensic reading.\n\n"
                "2. Hybrid images remain difficult\n"
                "Images may combine camera-origin content, AI-generated regions, manual editing, "
                "upscaling, compression, and platform processing.\n\n"
                "3. Smartphone processing can mimic synthetic artifacts\n"
                "HDR, segmentation, denoising, sharpening, smoothing, and computational relighting "
                "may resemble synthetic-image artifacts.\n\n"
                "4. Metadata can be missing, stripped, edited, or spoofed\n"
                "Metadata is useful, but not always reliable.\n\n"
                "5. Visual overlays are diagnostic aids\n"
                "Heatmaps, masks, FFT plots, ELA outputs, and patch overlays show detected signals. "
                "They do not automatically prove manipulation by themselves.\n\n"
                "6. Current beta status\n"
                "SignalLens is still in beta. Thresholds, reasoning rules, and module behavior may change.\n\n"
                "Recommended interpretation:\n"
                "Use SignalLens to understand evidence, contradictions, and uncertainty — "
                "not to replace expert judgment."
            ),
        )

    def send_feedback(self):
        import platform, urllib.parse, webbrowser

        state = getattr(self, "analysis_state", None)
        output_dir = getattr(state, "output_dir", "") if state else ""
        params = {
            "version": APP_VERSION,
            "os": platform.platform(),
            "audit_folder": str(output_dir) if output_dir else "",
        }
        url = FEEDBACK_URL + "?" + urllib.parse.urlencode(params)
        try:
            opened = webbrowser.open(url)
        except Exception:
            opened = False
        if not opened:
            QMessageBox.information(self, "Send Feedback", f"Please open this feedback page manually:\n\n{url}",)
            
#-----------------------------------------
#--------  bootstrap ---------------------
#-----------------------------------------

def main() -> None:
    # The portable Windows bundle keeps settings/tools next to its executable.
    # Shell/shortcut launchers may otherwise inherit an unrelated, unwritable cwd.
    if getattr(sys, 'frozen', False):
        os.chdir(Path(sys.executable).resolve().parent)
    app = QApplication(sys.argv)
    window = SignalLensGui()
    window.show()
    QTimer.singleShot(150, lambda: ensure_visible(window))
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if getattr(sys, 'frozen', False):
            raise  # Let the windowed bootloader show the original startup error.
        import traceback
        print("[SignalLens] Fatal startup error:")
        traceback.print_exc()
        input("Press Enter to exit...")
