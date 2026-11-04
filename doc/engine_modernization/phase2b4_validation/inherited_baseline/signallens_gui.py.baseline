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
import sys, time
import platform
import subprocess
from   pathlib import Path
# PyQt6 GUI
from PyQt6.QtCore    import Qt, QThread, QTimer
from PyQt6.QtGui     import QGuiApplication, QDragEnterEvent, QDropEvent, QTextCharFormat, QColor, QTextCursor, QAction, QIcon
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextBrowser, QPushButton, QMessageBox, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QGroupBox,QListWidgetItem, QTextEdit, QCheckBox, QComboBox, QLabel, QFileDialog, QLineEdit, QGridLayout, QMenuBar)
# local imports
from signallens_settings   import load_settings
from osint_reverse_search  import add_manual_match, build_osint_summary_text, delete_match, format_match_label, initialize_osint_for_image
from osint_reverse_search  import load_osint_result, mark_reviewed_no_match, open_reverse_search, replace_match, save_osint_result
from osint_dialogs         import OSINTFindingDialog
from summary_synthesizer   import build_summary_result
from analysis_worker       import AnalysisWorker
from gui_semantics         import color_for_log_level
from summary_persistence   import persist_summary_result
from reasoning_persistence import persist_reasoning_trace, persist_reasoning_trace_text
from audit_manager         import AuditManager
from settings_dialog       import SettingsDialog 
from signallens_version    import VERSION, APP_VERSION, FEEDBACK_URL

class SignalLensGui(QWidget):
    def __init__(self) -> None:
        super().__init__()
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
        self.start = 0.0
        self.setWindowIcon(QIcon("signallens.png"))
        self._build_ui()  # creates the layout 
        self.resize(700, 360)

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

    def _create_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        # File
        file_menu = self.menu_bar.addMenu("File")
        
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
        layout = QVBoxLayout(self)
        self.drop_label = QLabel("Drag and drop an image here, or use 'Choose Image'")
        self._create_menu_bar()
        layout.setMenuBar(self.menu_bar)                
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #888;
                padding: 18px;
                border-radius: 8px;
            }
            """
        )
        layout.addWidget(self.drop_label)
        file_row = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        self.file_edit.setPlaceholderText("No file selected...")
        file_row.addWidget(self.file_edit)
        self.pick_button = QPushButton("Choose Image")
        self.pick_button.clicked.connect(self.pick_file)
        file_row.addWidget(self.pick_button)
        layout.addLayout(file_row)       
        self.context_group = QGroupBox("Scene Context (optional)")
        context_layout = QGridLayout()
        self.chk_natural = QCheckBox("Naturally repetitive scene content")
        self.chk_decorative = QCheckBox("Decorative / geometric repetition")
        self.chk_smartphone = QCheckBox("Smartphone computational-photo conditions")
        self.chk_screen = QCheckBox("Screenshot / display-origin candidate")
        context_layout.addWidget(self.chk_natural, 0, 0)
        context_layout.addWidget(self.chk_decorative, 0, 1)
        context_layout.addWidget(self.chk_smartphone, 1, 0)
        context_layout.addWidget(self.chk_screen, 1, 1)
        context_layout.setHorizontalSpacing(18)
        context_layout.setVerticalSpacing(6)
        self.analysis_mode_combo = QComboBox()
        self.analysis_mode_combo.addItems(["normal", "subject_based"])
        self.analysis_mode_combo.setCurrentText("normal")
        self.analysis_mode_combo.currentTextChanged.connect(self.on_analysis_mode_changed)        
        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Patch profile:"))
        profile_row.addWidget(self.analysis_mode_combo)
        profile_row.addStretch()
        layout.addLayout(profile_row)                
        self.context_group.setLayout(context_layout)
        layout.addWidget(self.context_group)                        
        action_row = QHBoxLayout()
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        self.summary_box.setMinimumHeight(160)
        self.summary_box.setMaximumHeight(220)
        self.summary_box.setPlaceholderText("Analysis summary will appear here...")
        self.summary_box.setStyleSheet("""
        QTextEdit {
            background-color: #1f2937;
            color: #d1d5db;
            border: 1px solid #374151;
            padding: 8px;
        }
        """)
        layout.addWidget(self.summary_box)        
        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self.run_analysis)
        self.run_button.setEnabled(False)
        action_row.addWidget(self.run_button)
        self.open_json_button = QPushButton("Open Results Folder")
        self.open_json_button.clicked.connect(self.open_output_folder)
        self.open_json_button.setEnabled(False)
        action_row.addWidget(self.open_json_button)
        layout.addLayout(action_row)        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(100)
        layout.addWidget(self.log_box)
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)       
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_ui)
        bottom_row.addWidget(self.clear_button)
        layout.addLayout(bottom_row)               
        self.osint_group = self.build_osint_group()
        layout.addWidget(self.osint_group)        

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
        button_row = QHBoxLayout()
        button_row.addWidget(self.btn_google)
        button_row.addWidget(self.btn_yandex)
        button_row.addWidget(self.btn_tineye)
        button_row.addWidget(self.btn_mark_no_match)
        button_row.addWidget(self.btn_add_osint)
        button_row.addWidget(self.btn_edit_osint)
        button_row.addWidget(self.btn_delete_osint)
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
        color = color_for_log_level(level)
        cursor = self.log_box.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.insertText(message + "\n", fmt)
        self.log_box.setTextCursor(cursor)
        self.log_box.ensureCursorVisible()
        
    def update_summary(self) -> None:
        if self.analysis_state is None:
            self.summary_result = None
            self.summary_box.clear()
            return
        scene_context = {
            "natural_repetition": self.chk_natural.isChecked(),
            "decorative_geometric": self.chk_decorative.isChecked(),
            "smartphone_computational": self.chk_smartphone.isChecked(),
            "screen_origin": self.chk_screen.isChecked(),
        }        
        self.summary_result = build_summary_result(self.analysis_state, self.osint_result, scene_context=scene_context)
        # self.summary_box.setPlainText(self.summary_result.full_text)  use html colouring instead of plain text
        self.summary_box.setHtml(self.summary_result.full_html)

    def on_analysis_mode_changed(self, value: str) -> None:
        self.analysis_mode = value
        self.log(f"Patch profile set to: {value}")                
                
    def clear_analysis_state(self) -> None:
        self.exif_payload = None
        self.ela_payload = None
        self.noise_payload = None
        self.cross_signal_payload = None
        self.osint_result = None
        self.fft_payload = None
        self.analysis_state = None
        self.sensor_origin_payload = None
        self.subject_boundary_payload = None
        self.compression_history_payload = None      
        self.cfa_demosaic_payload = None
        self.region_masks_payload = None
        self.region_fft_payload = None        
        self.boundary_focus_payload = None
        self.patch_spatial_payload = None
        self.subject_texture_consistency_payload = None
        self.subject_process_asymmetry_payload = None
        self.subject_material_realism_payload = None
        self.summary_result = None       
    
    def clear_ui(self) -> None:
        self.selected_file = None
        self.file_edit.clear()
        self.clear_analysis_state()
        self.clear_summary()
        self.refresh_osint_ui()
        self.log_box.clear()
        self.chk_natural.setChecked(False)
        self.chk_decorative.setChecked(False)   
        self.chk_smartphone.setChecked(False)
        self.chk_screen.setChecked(False)                               
        self.current_image_path = None
        self.current_analysis_dir = None
        self.output_json = None
        self.run_button.setEnabled(False)
        self.open_json_button.setEnabled(False)
        self.drop_label.setText("Drag and drop an image here, or use 'Choose Image'")
        self.status_label.setText("Ready.")
        self.log("Cleared interface.")
        self.decision_trace_action.setEnabled(False)
        self.open_latest_audit_action.setEnabled(False)
    
    def is_supported_image(self, path: Path) -> bool:
        return path.is_file() and path.suffix.lower() in self.settings.get("supported_extensions")

    def set_selected_file(self, path: Path) -> None:
        self.analysis_state = None
        self.selected_file = path
        self.file_edit.setText(str(path))
        self.run_button.setEnabled(True)
        self.open_json_button.setEnabled(False)
        self.status_label.setText("File selected.")
        self.drop_label.setText(f"Selected:\n{path.name}")
        self.clear_summary()
        self.log_box.clear()
        self.log(f"Selected file: {path}")       
        self.current_image_path = self.selected_file
        output_root = Path(self.settings.get("output_root"))
        output_dir = output_root / self.selected_file.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        self.current_analysis_dir = output_dir         
        output_json = Path(self.selected_file.stem + "_exif_signals.json")          
        self.output_json = output_dir / output_json
        osint_json = Path(self.current_analysis_dir) / "osint_results.json"
        if osint_json.exists():
            self.osint_result = load_osint_result(osint_json)
            self.log("Loaded existing OSINT record.")
            self.refresh_osint_ui()
        else:
            self.osint_result = initialize_osint_for_image(self.selected_file, output_dir)
            self.log("Initialized OSINT record.")
            self.refresh_osint_ui()
          
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
        try:            
            open_reverse_search(provider, self.osint_result)
            save_osint_result(self.osint_result, self.current_analysis_dir)
            self.log(f"Opened reverse-search engine: {provider}")
            self.refresh_osint_ui()
            QMessageBox.information(self, "Reverse Search", "Perform your search in the browser, then click 'Add Finding' to record results.")
        except Exception as e:
            QMessageBox.critical(self, "OSINT Error", str(e))    

    def add_osint_finding(self) -> None:
        if not self.ensure_osint_ready():
            return
        dlg = OSINTFindingDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            add_manual_match(
                self.osint_result,
                provider=data["provider"],
                page_url=data["page_url"],
                title=data["title"],
                image_url=data["image_url"],
                similarity_score=data["similarity_score"],
                first_seen_estimate=data["first_seen_estimate"],
                source_type=data["source_type"],
                notes=data["notes"],
            )
            save_osint_result(self.osint_result, self.current_analysis_dir)
            self.log("Added OSINT finding.")
            self.refresh_osint_ui()
            self.update_summary()

    def edit_selected_osint_finding(self) -> None:
        if not self.ensure_osint_ready():
            return
        row = self.osint_findings_list.currentRow()
        if row < 0 or row >= len(self.osint_result.matches):
            QMessageBox.information(self, "Edit OSINT Finding", "No finding selected. Add a finding first or select one from the list.")
            return
        existing_match = self.osint_result.matches[row]
        dlg = OSINTFindingDialog(self, existing_match=existing_match)
        if dlg.exec():
            data = dlg.get_data()
            replace_match(
                self.osint_result,
                index=row,
                provider=data["provider"],
                page_url=data["page_url"],
                title=data["title"],
                image_url=data["image_url"],
                similarity_score=data["similarity_score"],
                first_seen_estimate=data["first_seen_estimate"],
                source_type=data["source_type"],
                notes=data["notes"],
            )
            save_osint_result(self.osint_result, self.current_analysis_dir)
            self.log("Updated OSINT finding.")
            self.refresh_osint_ui()
            self.update_summary()

    def delete_selected_osint_finding(self) -> None:
        if not self.ensure_osint_ready():
            return
        row = self.osint_findings_list.currentRow()
        if row < 0 or row >= len(self.osint_result.matches):
            QMessageBox.information(self, "Delete OSINT Finding", "Select a finding first.")
            return
        delete_match(self.osint_result, row)
        save_osint_result(self.osint_result, self.current_analysis_dir)
        self.log("Deleted OSINT finding.")
        self.refresh_osint_ui()
        self.update_summary()

    def mark_osint_reviewed_no_match(self) -> None:
        if not self.ensure_osint_ready():
            return
        mark_reviewed_no_match(self.osint_result)
        save_osint_result(self.osint_result, self.current_analysis_dir)
        self.log("Marked OSINT review as completed with no documented match.")
        self.refresh_osint_ui()
        self.update_summary()

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
        if self.current_image_path is None or self.current_analysis_dir is None:
            QMessageBox.information(self, "OSINT", "Load or drop an image first.")
            return False
        if self.osint_result is None:
            self.osint_result = initialize_osint_for_image(self.current_image_path, self.current_analysis_dir)
        return True
    
    #----------------------------------------------------------------
    # This method runs the analysis pipeline: EXIF analysis, ELA, noise analysis, cross-signal analysis, and FFT analysis. 
    # Each step is wrapped in a try-except block to handle errors gracefully without crashing the entire pipeline.
    # It updates the summary and log with results.
    #----------------------------------------------------------------
    def run_analysis(self) -> None:
        if self.selected_file is None:
            QMessageBox.warning(self, "No file", "Please choose or drop an image first.")
            return
        self.start = time.perf_counter()
        self.run_button.setEnabled(False)
        self.status_label.setText("Running analysis...")
        self.thread = QThread()
        self.worker = AnalysisWorker(
            selected_file=self.selected_file,
            output_dir=self.current_analysis_dir,
            output_json=self.output_json,
            analysis_mode=self.analysis_mode,            
        )
        self.worker.moveToThread(self.thread)
        # --- wiring ---
        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.log)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        # cleanup
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()                    

    def on_analysis_finished(self, state):
        self.analysis_state = state
        self.exif_payload = state.exif_payload
        self.ela_payload = state.ela_payload
        self.noise_payload = state.noise_payload
        self.sensor_origin_payload = state.sensor_origin_payload
        self.subject_boundary_payload = state.subject_boundary_payload
        self.cross_signal_payload = state.cross_signal_payload
        self.fft_payload = state.fft_payload
        self.patch_similarity_payload = state.patch_similarity_payload
        self.compression_history_payload = state.compression_history_payload
        self.cfa_demosaic_payload = state.cfa_demosaic_payload
        self.region_masks_payload = state.region_masks_payload
        self.region_fft_payload = state.region_fft_payload        
        self.boundary_focus_payload = state.boundary_focus_payload
        self.patch_spatial_payload = state.patch_spatial_payload
        self.subject_texture_consistency_payload = state.subject_texture_consistency_payload
        self.subject_process_asymmetry_payload = state.subject_process_asymmetry_payload
        self.subject_material_realism_payload = state.subject_material_realism_payload
        self.open_json_button.setEnabled(self.exif_payload is not None)
        self.status_label.setText("Analysis completed")
        duration = time.perf_counter() - self.start
        self.log(f"Total Analysis took {duration:.2f}s")
        self.run_button.setEnabled(True)
        self.update_summary()
        summary_result = getattr(self, "summary_result", None)
        reasoning_trace = getattr(summary_result, "reasoning_trace", None)        
        if summary_result is None:
            return        
        summary_paths = persist_summary_result(self.summary_result, state.output_dir)
        reasoning_trace_path = persist_reasoning_trace(
            getattr(summary_result, "reasoning_trace", None),
            state.output_dir,
        )        
        reasoning_trace_txt_path = persist_reasoning_trace_text(
            reasoning_trace,
            state.output_dir,
        )                
        if getattr(state, "run_recorder", None):
            if reasoning_trace_path:
                state.run_recorder.add_artifact("reasoning_trace_json", reasoning_trace_path)        
        if getattr(state, "run_recorder", None):
            state.run_recorder.add_artifact("summary_outputs", summary_paths)
            if reasoning_trace_path:
                state.run_recorder.add_artifact("reasoning_trace_json", reasoning_trace_path)            
            if reasoning_trace_txt_path:
                state.run_recorder.add_artifact("reasoning_trace_txt", reasoning_trace_txt_path)
            state.run_recorder.log("Persisted final summary outputs", "success")
        if self.has_decision_trace():
            self.status_label.setText("Analysis completed - Decision Trace available")
            self.decision_trace_action.setEnabled(True)    
            self.open_latest_audit_action.setEnabled(True)  
  
    def on_analysis_error(self, message: str):
        QMessageBox.critical(self, "Analysis error", message)
        self.status_label.setText("Error")
        self.run_button.setEnabled(True)
  

    def open_latest_audit_folder(self):
        import os
        from pathlib import Path
        from PyQt6.QtWidgets import QMessageBox

        state = getattr(self, "analysis_state", None)
        output_dir = getattr(state, "output_dir", None) if state else None

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
        if self.selected_file is None:
            return
        output_root = Path(self.settings.get("output_root"))
        output_dir  = output_root / self.selected_file.stem
        json_path   = output_dir / f"{self.selected_file.stem}_exif_signals.json"
        if not json_path.exists():
            QMessageBox.warning(self, "File not found",  f"JSON output file does not exist yet:\n{json_path}")
            return
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(
                    ["explorer", "/select,", str(json_path)],
                    check=False
                )
            elif system == "Darwin":
                subprocess.run(["open", "-R", str(json_path)], check=False)
            else:  # Linux
                subprocess.run(["xdg-open", str(json_path.parent)], check=False)
        except Exception as exc:
            QMessageBox.warning(self, "Could not open folder", str(exc))          

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
            return str(value)

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
                html.append(f"<li><b>{k}:</b> {fmt(v)}</li>")
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
        viewer.setHtml("\n".join(html))
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
        viewer.setHtml(html)
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
    app = QApplication(sys.argv)
    window = SignalLensGui()
    window.show()
    QTimer.singleShot(150, window.place_window_above_taskbar)
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        import traceback
        print("[SignalLens] Fatal startup error:")
        traceback.print_exc()
        input("Press Enter to exit...")