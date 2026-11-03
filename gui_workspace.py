"""Native workspace shell around the single UI-1 owner and existing controls.

This module projects snapshots and routes existing actions. It never synthesizes
findings, runs detectors, owns a second session, or changes report contents.
"""
from pathlib import Path
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QAction, QKeySequence, QDesktopServices
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QPushButton, QLineEdit, QComboBox, QGroupBox, QCheckBox, QDialog,
    QDialogButtonBox, QTextEdit, QPlainTextEdit, QLabel, QSplitter, QStackedWidget,
    QScrollArea, QButtonGroup, QSizePolicy, QProgressBar, QStyle)
from gui_components import (label, SectionHeader, Panel, StatusIndicator, ConfidenceIndicator,
                            EmptyState, NavigationItem, MetadataRow, CollapsibleSection, SourcePreview, StatusMessage, scroll_area)
from gui_design_system import COLORS, GEOMETRY, SPACE, font, apply_theme
from signallens_version import VERSION

HYPOTHESIS_LABELS = {'synthetic_origin': 'Synthetic origin', 'localized_editing': 'Localized editing',
                     'camera_acquisition': 'Camera-acquisition compatibility', 'unresolved_anomaly': 'Unresolved anomaly'}


scroll_content = scroll_area


def text_view():
    view = QPlainTextEdit()
    view.setReadOnly(True)
    view.setMinimumHeight(120)
    view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
    return view


class WorkspaceShell(QWidget):
    destinations = ('Overview', 'Image Forensics', 'Evidence', 'Reasoning', 'Provenance', 'Reports')

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.setObjectName('workspaceRoot')
        self.current_destination = 'Overview'
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE[3], SPACE[2], SPACE[3], SPACE[2])
        layout.setSpacing(SPACE[2])
        brand = QHBoxLayout()
        brand.addWidget(label('SignalLens', 'display', bold=True))
        brand.addWidget(label('FORENSIC WORKBENCH', 'caption'), 1)
        self.lifecycle = StatusIndicator('empty')
        brand.addWidget(self.lifecycle)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setMaximumWidth(80)
        self.progress.setAccessibleName('Analysis processing; no percentage available')
        self.progress.hide()
        brand.addWidget(self.progress)
        settings = QPushButton('Settings')
        settings.clicked.connect(host.show_settings_dialog)
        brand.addWidget(settings)
        layout.addLayout(brand)

        commands = QHBoxLayout()
        host.pick_button = QPushButton('Choose Image')
        host.pick_button.clicked.connect(host.pick_file)
        host.file_edit = QLineEdit()
        host.file_edit.setReadOnly(True)
        host.file_edit.setPlaceholderText('No source image selected')
        host.file_edit.setAccessibleName('Selected image path')
        configure = QPushButton('Configure…')
        configure.clicked.connect(self.show_configuration)
        host.run_button = QPushButton('Run Analysis')
        host.run_button.setProperty('slPrimary', True)
        host.run_button.clicked.connect(host.run_analysis)
        host.clear_button = QPushButton('Clear')
        host.clear_button.clicked.connect(host.clear_ui)
        for widget in (host.pick_button, host.file_edit, configure, host.run_button, host.clear_button):
            commands.addWidget(widget, 1 if widget is host.file_edit else 0)
        layout.addLayout(commands)
        self._configuration()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(SPACE[0])
        navigation = QFrame()
        navigation.setObjectName('workspaceNavigation')
        navigation.setMinimumWidth(GEOMETRY.navigation_min)
        navigation.setMaximumWidth(GEOMETRY.navigation_max)
        nav_layout = QVBoxLayout(navigation)
        nav_layout.setContentsMargins(SPACE[1], SPACE[3], SPACE[1], SPACE[3])
        nav_layout.setSpacing(SPACE[1])
        nav_layout.addWidget(label('INVESTIGATION', 'caption'))
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_items = {}
        icons = ('SP_FileDialogInfoView', 'SP_FileIcon', 'SP_FileDialogListView', 'SP_FileDialogDetailedView', 'SP_DirIcon', 'SP_DialogSaveButton')
        for index, (destination, icon) in enumerate(zip(self.destinations, icons)):
            button = NavigationItem(destination, self.style().standardIcon(getattr(QStyle.StandardPixmap, icon)))
            self.nav_items[destination] = button
            self.nav_group.addButton(button, index)
            nav_layout.addWidget(button)
            shortcut = QAction(self)
            shortcut.setShortcut(QKeySequence(f'Ctrl+{index+1}'))
            shortcut.triggered.connect(lambda checked=False, name=destination: self.navigate(name, focus=True))
            host.addAction(shortcut)
        self.nav_group.idClicked.connect(lambda index: self.navigate(self.destinations[index]))
        nav_layout.addStretch()
        self.identity = label('No active result', 'caption')
        nav_layout.addWidget(self.identity)
        nav_layout.addWidget(label('Local analysis\nForensic interpretation, not certainty.', 'caption'))
        self.stack = QStackedWidget()
        self.stack.setMinimumWidth(0)
        self.splitter.addWidget(navigation)
        self.splitter.addWidget(self.stack)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([GEOMETRY.navigation_width, GEOMETRY.normal_width-GEOMETRY.navigation_width])
        layout.addWidget(self.splitter, 1)

        self.pages = {}
        self.empty_states = {}
        self._overview()
        self._forensics()
        self._evidence()
        self._reasoning()
        self._provenance()
        self._reports()
        host.log_box = QTextEdit()
        host.log_box.setReadOnly(True)
        host.log_box.setMinimumHeight(72)
        host.log_box.setMaximumHeight(140)
        host.log_box.setAccessibleName('Analysis execution log')
        self.log_section = CollapsibleSection('Execution log', host.log_box)
        layout.addWidget(self.log_section)
        host.status_label = StatusMessage('Ready.')
        host.statusBar().addWidget(host.status_label, 1)
        version = label(VERSION, 'caption')
        version.setWordWrap(False)
        host.statusBar().addPermanentWidget(version)
        host.statusBar().setFixedHeight(GEOMETRY.control_height + SPACE[1])
        self.navigate('Overview')

    def _configuration(self):
        h = self.host
        self.configuration = QDialog(h)
        self.configuration.setWindowTitle('Analysis configuration')
        self.configuration.resize(760, 320)
        body = QVBoxLayout(self.configuration)
        body.setContentsMargins(*([SPACE[3]]*4))
        body.addWidget(SectionHeader('Analysis configuration', 'Captured when analysis starts. Changes apply to the next invocation.'))
        profile = QHBoxLayout()
        profile.addWidget(label('Patch profile'))
        h.analysis_mode_combo = QComboBox()
        h.analysis_mode_combo.addItems(['normal', 'subject_based'])
        h.analysis_mode_combo.currentTextChanged.connect(h.on_analysis_mode_changed)
        profile.addWidget(h.analysis_mode_combo, 1)
        body.addLayout(profile)
        h.context_group = QGroupBox('Scene context · optional analyst input')
        grid = QGridLayout(h.context_group)
        checks = [('chk_natural', 'Naturally repetitive scene content'), ('chk_decorative', 'Decorative / geometric repetition'),
                  ('chk_smartphone', 'Smartphone computational-photo conditions'), ('chk_screen', 'Screenshot / display-origin candidate')]
        for index, (name, text) in enumerate(checks):
            checkbox = QCheckBox(text)
            setattr(h, name, checkbox)
            grid.addWidget(checkbox, index//2, index%2)
        body.addWidget(h.context_group)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.configuration.reject)
        body.addWidget(buttons)

    def show_configuration(self):
        self.configuration.exec()

    def _page(self, name, description, *, empty=True):
        page = QWidget()
        body = QVBoxLayout(page)
        body.setContentsMargins(SPACE[3], SPACE[1], 0, 0)
        body.setSpacing(SPACE[2])
        body.addWidget(SectionHeader(name, description))
        if empty:
            state = EmptyState('No analysis result', 'Select an image and run analysis. Recorded content will appear here.')
            self.empty_states[name] = state
            body.addWidget(state)
        self.pages[name] = page
        self.stack.addWidget(page)
        return body

    def _overview(self):
        body = self._page('Overview', 'Source identity, recorded interpretation and the current investigation narrative.', empty=False)
        self.overview_splitter = QSplitter(Qt.Orientation.Vertical)
        self.overview_splitter.setChildrenCollapsible(False)
        self.overview_splitter.setHandleWidth(SPACE[0])
        top = QWidget()
        grid = QGridLayout(top)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(SPACE[2])
        source = Panel('Source image')
        self.preview = SourcePreview()
        source.body.addWidget(self.preview, 1)
        self.host.drop_label = label("Drag and drop an image here, or use 'Choose Image'", 'caption')
        source.body.addWidget(self.host.drop_label)
        finding = Panel('Primary forensic interpretation')
        self.finding_title = label('No completed finding', 'card', bold=True)
        self.confidence = ConfidenceIndicator()
        self.finding_explanation = label('Choose an image to begin. Analysis findings and limitations will remain tied to its investigation.', 'secondary')
        self.hypothesis_summary = label('', 'secondary')
        finding.body.addWidget(self.finding_title)
        finding.body.addWidget(self.confidence, 0, Qt.AlignmentFlag.AlignLeft)
        finding.body.addWidget(self.finding_explanation)
        finding.body.addWidget(self.hypothesis_summary)
        finding.body.addStretch()
        grid.addWidget(source, 0, 0)
        grid.addWidget(finding, 0, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        limitations = Panel('Evidence scope and limitations')
        self.limitations = label('No completed result. Confidence, evidence availability and provenance are separate concepts.', 'secondary')
        limitations.body.addWidget(self.limitations)
        self.supporting_summary = label('Supporting observations are available in the recorded narrative after analysis.', 'caption')
        limitations.body.addWidget(self.supporting_summary)
        grid.addWidget(limitations, 1, 0, 1, 2)
        self.overview_splitter.addWidget(scroll_content(top))
        narrative = Panel('Investigation narrative · retained report view')
        self.host.summary_box = QTextEdit()
        self.host.summary_box.setReadOnly(True)
        self.host.summary_box.setMinimumHeight(160)
        self.host.summary_box.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.host.summary_box.setPlaceholderText('No completed result. Choose an image, configure analysis, then run.')
        self.host.summary_box.setAccessibleName('Current investigation narrative')
        narrative.body.addWidget(self.host.summary_box, 1)
        self.overview_splitter.addWidget(narrative)
        self.overview_splitter.setSizes([360, 360])
        body.addWidget(self.overview_splitter, 1)

    def _forensics(self):
        body = self._page('Image Forensics', 'Existing detector outputs and stage availability. Image comparison arrives in a later phase.')
        panel = Panel('Recorded detector artifacts')
        self.artifact_button = QPushButton('Open existing audit artifacts')
        self.artifact_button.clicked.connect(self.open_artifacts)
        panel.body.addWidget(self.artifact_button, 0, Qt.AlignmentFlag.AlignLeft)
        panel.body.addWidget(label('ELA, residual, FFT, patch, sensor and region outputs remain available as files. No new detector output is generated by this workspace.', 'secondary'))
        self.stage_details = text_view()
        panel.body.addWidget(self.stage_details, 1)
        body.addWidget(panel, 1)

    def _evidence(self):
        body = self._page('Evidence', 'Recorded hypothesis-specific roles. These observations are not independent votes.')
        panel = Panel('Structured evidence · initial view')
        self.evidence_details = text_view()
        panel.body.addWidget(self.evidence_details, 1)
        button = QPushButton('Read investigation narrative')
        button.clicked.connect(lambda: self.navigate('Overview', focus=True))
        panel.body.addWidget(button, 0, Qt.AlignmentFlag.AlignLeft)
        body.addWidget(panel, 1)

    def _reasoning(self):
        body = self._page('Reasoning', 'Authoritative hypothesis and policy explanations, with access to the existing Decision Trace.')
        panel = Panel('Recorded reasoning')
        self.trace_button = QPushButton('Open Decision Trace')
        self.trace_button.clicked.connect(self.host.show_decision_trace_dialog)
        panel.body.addWidget(self.trace_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.reasoning_details = text_view()
        panel.body.addWidget(self.reasoning_details, 1)
        body.addWidget(panel, 1)

    def _provenance(self):
        body = self._page('Provenance', 'Metadata declarations and manual source research. Presence is not authentication.', empty=False)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        panel = Panel('Metadata and provenance')
        self.declaration = MetadataRow('Declaration state')
        self.verification = MetadataRow('Metadata verification', 'Unknown')
        self.metadata_description = label('No metadata result is available.', 'secondary')
        panel.body.addWidget(self.declaration)
        panel.body.addWidget(self.verification)
        panel.body.addWidget(self.metadata_description)
        layout.addWidget(panel)
        self.host.osint_group = self.host.build_osint_group()
        self.host.osint_group.setMinimumHeight(280)
        layout.addWidget(self.host.osint_group)
        layout.addStretch()
        body.addWidget(scroll_content(content), 1)

    def _reports(self):
        body = self._page('Reports', 'Publish the current investigation revision using the existing summary and trace formats.')
        panel = Panel('Report snapshot')
        self.report_state = MetadataRow('Synchronization')
        self.report_identity = MetadataRow('Result / annotation revision')
        panel.body.addWidget(self.report_state)
        panel.body.addWidget(self.report_identity)
        panel.body.addWidget(label('JSON, HTML and text reports retain the frozen forensic findings and separately versioned current annotations. Export always checks the active revision.', 'secondary'))
        self.host.open_json_button = QPushButton('Open Results Folder')
        self.host.open_json_button.clicked.connect(self.host.open_output_folder)
        panel.body.addWidget(self.host.open_json_button, 0, Qt.AlignmentFlag.AlignLeft)
        load = QPushButton('Open stored summary…')
        load.clicked.connect(self.host.open_stored_summary)
        panel.body.addWidget(load, 0, Qt.AlignmentFlag.AlignLeft)
        panel.body.addStretch()
        body.addWidget(panel, 1)

    def navigate(self, name, *, focus=False):
        if name not in self.pages:
            return False
        self.current_destination = name
        self.stack.setCurrentWidget(self.pages[name])
        self.nav_items[name].setChecked(True)
        if focus:
            self.nav_items[name].setFocus()
        return True

    def artifact_directory(self):
        h = self.host
        if h.session.state.value != 'completed':
            return None
        if h.analysis_state is not None:
            folder = Path(h.analysis_state.output_dir)
        elif h.session.imported_from:
            summary = Path(h.session.imported_from)
            folder = summary.parent.parent if summary.parent.name == 'summary' else summary.parent
        else:
            return None
        return folder if folder.is_dir() else None

    def open_artifacts(self):
        folder = self.artifact_directory()
        if folder:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder.resolve())))

    def bind_snapshot(self, snapshot):
        h = self.host
        # Direct signals can reenter selection; reject outdated immutable views.
        if (snapshot.session_id != h.session.session_id or snapshot.result_id != h.session.result_id
                or snapshot.analysis_id != (h.session.invocation.analysis_id if h.session.invocation else None)
                or snapshot.analysis_revision != h.session.analysis_revision
                or snapshot.annotation_revision != h.session.annotation_revision
                or snapshot.summary.status != h.session.state.value):
            return False
        state = snapshot.summary.status
        complete = state == 'completed' and snapshot.result_id is not None
        self.lifecycle.set_state(state)
        self.progress.setVisible(state == 'analyzing')
        self.identity.setText(f'Investigation {snapshot.session_id[:8]}\n{snapshot.summary.image_name or "No image selected"}\n' + ('Current result available' if complete else 'No completed result'))
        self.preview.set_source(h.session.image_path, (snapshot.session_id, snapshot.analysis_id))
        self.confidence.set_tier(snapshot.summary.confidence_tier if complete else None)
        self.finding_title.setText(HYPOTHESIS_LABELS.get(snapshot.summary.primary_hypothesis, snapshot.summary.primary_hypothesis or 'No completed finding'))
        primary = next((item for item in snapshot.hypotheses if item.hypothesis_id == snapshot.summary.primary_hypothesis), None)
        self.finding_explanation.setText(primary.finding if complete and primary and primary.finding else
            ('Analysis is running. No conclusion is available yet.' if state == 'analyzing' else 'No structured interpretation recorded.' if complete else 'Select an image and run analysis to obtain a forensic interpretation.'))
        self.hypothesis_summary.setText('\n'.join(f'{HYPOTHESIS_LABELS.get(item.hypothesis_id, item.hypothesis_id)} · {item.confidence_tier or "Unavailable"}' for item in snapshot.hypotheses) if complete else '')
        self.limitations.setText('\n'.join(snapshot.summary.limitations) if complete and snapshot.summary.limitations else
            'No structured limitations recorded. Read the original narrative.' if complete else 'No completed result. Confidence, availability and verification remain distinct.')
        self.supporting_summary.setText('Supporting observations are listed under their recorded hypotheses in Evidence and the narrative.' if snapshot.evidence else 'No structured evidence is available for this result.' if complete else 'Evidence will be shown only after a completed analysis.')
        for destination, empty in self.empty_states.items():
            unavailable = not complete or (destination == 'Evidence' and not snapshot.evidence) or (destination == 'Reasoning' and not snapshot.hypotheses)
            empty.setVisible(unavailable)
            empty.set_message('Analysis in progress' if state == 'analyzing' else 'No completed result' if not complete else 'Structured content unavailable',
                'Status and execution details remain available below. No finding is implied.' if state == 'analyzing' else 'Select an image and run analysis, or load a stored summary.' if not complete else 'Read the original investigation narrative or available artifacts; missing fields are not negative evidence.')
        self.stage_details.setPlainText('\n\n'.join(f'{s.stage_id} · {s.status or "Unknown"}' + (f'\n{s.reason}' if s.reason else '') for s in snapshot.stages) if complete else '')
        self.artifact_button.setEnabled(self.artifact_directory() is not None)
        self.evidence_details.setPlainText('\n\n'.join(f'{HYPOTHESIS_LABELS.get(e.hypothesis_id, e.hypothesis_id)} · {e.role.replace("_", " ")}\n{e.label or e.evidence_id}\n{e.interpretation or "Explanation not recorded"}\nID: {e.evidence_id}' for e in snapshot.evidence) if complete else '')
        self.trace_button.setEnabled(complete and h.has_decision_trace())
        self.reasoning_details.setPlainText('\n\n'.join(f'{HYPOTHESIS_LABELS.get(item.hypothesis_id, item.hypothesis_id)} · {item.confidence_tier or "Unavailable"}\n{item.finding or "Explanation not recorded"}\n' + '\n'.join(item.confidence_rationale) for item in snapshot.hypotheses) if complete else '')
        self.declaration.set_value(snapshot.provenance.declaration_status if complete else None)
        self.verification.set_value(snapshot.provenance.verification_status.capitalize() if complete else 'Unknown')
        self.metadata_description.setText(snapshot.provenance.description or 'Metadata details are not recorded.' if complete else 'No metadata result is available. OSINT annotations can be recorded after selecting a source.')
        self.report_state.set_value('Synchronized' if complete and h.session.report_current else 'Needs publication' if complete else 'No completed result')
        self.report_identity.set_value(f'{snapshot.result_id[:8]} / {snapshot.annotation_revision}' if complete else None)
        return True
