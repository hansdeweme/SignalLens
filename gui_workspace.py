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
        from overview_workspace import OverviewWorkspace
        self.overview = OverviewWorkspace(self.host, self.navigate)
        self.pages['Overview'] = self.overview
        self.stack.addWidget(self.overview)
        self.overview_splitter = self.overview.splitter
        # Compatibility aliases identify the same single production widgets.
        for name in ('preview', 'confidence', 'finding_title', 'finding_explanation', 'limitations'):
            setattr(self, name, getattr(self.overview, name))

    def _forensics(self):
        from image_forensics_workspace import ImageForensicsWorkspace
        self.forensics = ImageForensicsWorkspace(self.host, self.navigate)
        self.pages['Image Forensics'] = self.forensics
        self.stack.addWidget(self.forensics)
        self.artifact_button = self.forensics.artifact_button
        self.stage_details = self.forensics.stage_details

    def _evidence(self):
        from explorer_workspace import EvidenceWorkspace
        self.evidence = EvidenceWorkspace(self.host,self.navigate_context)
        self.pages['Evidence'] = self.evidence
        self.stack.addWidget(self.evidence)
        self.empty_states['Evidence'] = self.evidence.empty
        self.evidence_details = self.evidence.compatibility_details

    def _reasoning(self):
        from explorer_workspace import ReasoningWorkspace
        self.reasoning = ReasoningWorkspace(self.host,self.navigate_context)
        self.pages['Reasoning'] = self.reasoning
        self.stack.addWidget(self.reasoning)
        self.empty_states['Reasoning'] = self.reasoning.empty
        self.trace_button = self.reasoning.trace_button
        self.reasoning_details = self.reasoning.compatibility_details
        self.explorer_snapshot = None
        self.forensics.catalog_changed.connect(self.refresh_explorers)

    def _provenance(self):
        from provenance_workspace import ProvenanceWorkspace
        self.provenance = ProvenanceWorkspace(self.host,self.navigate_context)
        self.pages['Provenance'] = self.provenance
        self.stack.addWidget(self.provenance)
        for name in ('declaration','verification','metadata_description'):
            setattr(self,name,getattr(self.provenance,name))

    def _reports(self):
        from report_workspace import ReportsWorkspace
        self.reports = ReportsWorkspace(self.host,self.navigate_context)
        self.pages['Reports'] = self.reports
        self.stack.addWidget(self.reports)
        self.report_state = self.reports.report_state
        self.report_identity = self.reports.report_identity

    def navigate(self, name, *, focus=False):
        if name not in self.pages:
            return False
        self.current_destination = name
        self.stack.setCurrentWidget(self.pages[name])
        self.nav_items[name].setChecked(True)
        if focus:
            self.nav_items[name].setFocus()
        return True

    def navigate_context(self,name,key=None,*,hypothesis=None,evidence=None,role=None,artifact=None,tab=None,detector=None,
                         annotation_revision=None,field=None):
        from explorer_models import ExplorerIdentity
        session = self.host.session
        current = ExplorerIdentity(session.session_id,session.invocation.analysis_id if session.invocation else None,
            session.result_id,session.analysis_revision,session.state.value)
        if self.host._closing or key is not None and key != current:
            return False
        if annotation_revision is not None and annotation_revision != session.annotation_revision:
            return False
        if not self.explorer_snapshot or self.explorer_snapshot.identity != current:
            return False
        if not self.navigate(name):
            return False
        if name == 'Evidence':
            return self.evidence.focus(hypothesis,evidence,role,detector) if any(
                value is not None for value in (hypothesis,evidence,role,detector)) else True
        if name == 'Reasoning':
            return self.reasoning.focus(hypothesis,tab,detector)
        if name == 'Image Forensics':
            return self.forensics.focus_artifact(artifact) if artifact else True
        if name == 'Provenance':
            if tab == 'OSINT':
                self.provenance.tabs.setCurrentIndex(1)
                return True
            return self.provenance.focus(evidence,field)
        return True

    def refresh_explorers(self):
        from explorer_presenter import build_explorer
        from explorer_models import ExplorerIdentity
        snapshot = self.host.view_snapshot
        session = self.host.session
        current = ExplorerIdentity(session.session_id,session.invocation.analysis_id if session.invocation else None,
            session.result_id,session.analysis_revision,session.state.value)
        if not snapshot or (snapshot.session_id,snapshot.analysis_id,snapshot.result_id,snapshot.analysis_revision,
                            snapshot.summary.status) != (current.session_id,current.analysis_id,current.result_id,
                                                        current.analysis_revision,current.status):
            return
        result = build_explorer(snapshot,self.host.session.summary_data() or {},self.forensics.artifacts)
        if self.explorer_snapshot == result:
            return
        self.explorer_snapshot = result
        self.evidence.bind(result)
        self.reasoning.bind(result)

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
        self.overview.bind(snapshot)
        self.forensics.bind(snapshot)
        self.refresh_explorers()
        self.provenance.bind(snapshot)
        self.reports.bind(snapshot)
        for destination, empty in self.empty_states.items():
            unavailable = not complete or (destination == 'Evidence' and not snapshot.evidence) or (destination == 'Reasoning' and not snapshot.hypotheses)
            empty.setVisible(unavailable)
            empty.set_message('Analysis in progress' if state == 'analyzing' else 'No completed result' if not complete else 'Structured content unavailable',
                'Status and execution details remain available below. No finding is implied.' if state == 'analyzing' else 'Select an image and run analysis, or load a stored summary.' if not complete else 'Read the original investigation narrative or available artifacts; missing fields are not negative evidence.')
        self.stage_details.setPlainText('\n\n'.join(f'{s.stage_id} · {s.status or "Unknown"}' + (f'\n{s.reason}' if s.reason else '') for s in snapshot.stages) if complete else '')
        self.artifact_button.setEnabled(self.artifact_directory() is not None)
        self.evidence_details.setPlainText('\n\n'.join(f'{HYPOTHESIS_LABELS.get(e.hypothesis_id, e.hypothesis_id)} · {e.role.replace("_", " ")}\n{e.label or e.evidence_id}\n{e.interpretation or "Explanation not recorded"}\nID: {e.evidence_id}' for e in snapshot.evidence) if complete else '')
        self.trace_button.setEnabled(complete and h.has_decision_trace())
        self.reasoning_details.setPlainText('\n\n'.join(f'{HYPOTHESIS_LABELS.get(item.hypothesis_id, item.hypothesis_id)} · {item.confidence_tier or "Unavailable"}\n{item.finding or "Explanation not recorded"}\n' + '\n'.join(item.confidence_rationale)
            + '\nLimitations:\n' + ('\n'.join(item.limitations) or 'Not recorded')
            + (f'\nConfidence policy: {item.confidence_policy_rule}' if item.confidence_policy_rule else '')
            for item in snapshot.hypotheses) if complete else '')
        self.declaration.set_value(snapshot.provenance.declaration_status if complete else None)
        self.verification.set_value(snapshot.provenance.verification_status.capitalize() if complete else 'Unknown')
        self.metadata_description.setText(snapshot.provenance.description or 'Metadata details are not recorded.' if complete else 'No metadata result is available. OSINT annotations can be recorded after selecting a source.')
        self.report_state.set_value('Synchronized' if complete and h.session.report_current else 'Needs publication' if complete else 'No completed result')
        self.report_identity.set_value(f'{snapshot.result_id[:8]} / {snapshot.annotation_revision}' if complete else None)
        return True
