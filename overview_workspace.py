"""Image-centered projection of immutable presentation contracts; no inference."""
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSplitter, QPushButton, QTextEdit, QDialog, QDialogButtonBox, QLineEdit)
from gui_components import label, Panel, ConfidenceIndicator, StatusMessage, scroll_area
from gui_design_system import SPACE, apply_theme, font
from source_image_viewer import SourceImageViewer

HYPOTHESES = {'synthetic_origin': 'Synthetic origin', 'localized_editing': 'Localized editing',
              'camera_acquisition': 'Camera-acquisition compatibility'}


class _OverviewSplit(QSplitter):
    """Use wrapped content height at the actual panel widths, not QLabel's
    initial narrow size hint. This keeps the source prominent without padding
    the first row by hundreds of pixels in a vertical scroll container.
    """
    def sizeHint(self):
        hint = super().sizeHint()
        heights = [self.minimumSizeHint().height()]
        for index in range(self.count()):
            child = self.widget(index)
            layout = child.layout()
            if layout and layout.hasHeightForWidth():
                heights.append(layout.totalHeightForWidth(max(child.width(), child.minimumSizeHint().width())))
        return QSize(hint.width(), max(heights))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGeometry()


def excerpt(text, limit=260):
    return text if len(text) <= limit else text[:limit].rstrip() + '…'


class HypothesisCard(Panel):
    def __init__(self, name, navigate):
        super().__init__(name)
        self.tier = ConfidenceIndicator()
        self.finding = label('', 'secondary')
        self.limitation = label('', 'caption')
        self.body.addWidget(self.tier, 0, Qt.AlignmentFlag.AlignLeft)
        self.body.addWidget(self.finding)
        self.body.addWidget(self.limitation)
        self.body.addStretch()
        self.open = QPushButton('Open reasoning')
        self.hypothesis_id = None
        self.open.clicked.connect(lambda: navigate('Reasoning',hypothesis=self.hypothesis_id))
        self.body.addWidget(self.open)
        self.setMinimumWidth(0)

    def bind(self, item, complete):
        self.tier.set_tier(item.confidence_tier if item and complete else None)
        text = item.finding if item and item.finding and complete else 'Assessment not recorded.' if complete else 'Awaiting a completed analysis.'
        self.finding.setText(excerpt(text, 210))
        self.finding.setToolTip(text)
        limitations = '\n'.join(item.limitations) if item and complete else ''
        self.limitation.setText(excerpt(limitations, 140) or 'Limitations not recorded.' if complete else '')
        self.limitation.setToolTip(limitations)
        self.open.setEnabled(bool(item and complete))
        self.open.setToolTip('Read the full recorded assessment, limitations and confidence rationale.' if item and complete else 'No structured assessment is available.')


class OverviewWorkspace(QWidget):
    """One scroll surface; horizontal image/finding splitter remains persistent."""
    def __init__(self, host, navigate):
        super().__init__()
        self.host, self.navigate = host, navigate
        body = QVBoxLayout(self)
        body.setContentsMargins(SPACE[3], SPACE[1], 0, 0)
        body.setSpacing(SPACE[2])
        self.heading = StatusMessage('Investigation overview')
        self.heading.setFont(font('section', bold=True))
        body.addWidget(self.heading)
        self.header = label('', 'caption')
        body.addWidget(self.header)
        commands = QHBoxLayout()
        self.actions = {}
        for destination, title in (('Image Forensics', 'Image forensics'), ('Evidence', 'Evidence'),
                                   ('Reasoning', 'Reasoning'), ('Provenance', 'Provenance'), ('Reports', 'Reports')):
            action = QPushButton(title)
            action.clicked.connect(lambda checked=False, name=destination: self.open_context(name))
            commands.addWidget(action)
            self.actions[destination] = action
        body.addLayout(commands)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE[2])
        self.splitter = _OverviewSplit(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        identity_button = QPushButton('Source identity')
        identity_button.clicked.connect(self.show_identity)
        source = Panel('Investigation source', toolbar=(identity_button,))
        self.preview = SourceImageViewer()
        source.body.addWidget(self.preview, 1)
        host.drop_label = label("Drag an image here, or choose an image above.", 'caption')
        host.drop_label.setParent(self)
        host.drop_label.hide()  # Path/filename already appear in persistent commands/header.
        self.source_identity = QLineEdit(self)
        self.source_identity.setReadOnly(True)
        self.source_identity.setAccessibleName('Recorded source SHA-256; select and copy')
        self.source_identity.hide()  # Full copyable identity is available in the source dialog.
        self.finding_panel = Panel('Primary finding')
        self.finding_title = label('No completed finding', 'section', bold=True)
        self.confidence = ConfidenceIndicator()
        self.pattern = label('', 'caption')
        self.finding_explanation = label('', 'body')
        self.qualifier = label('', 'caption')
        for widget in (self.finding_title, self.confidence, self.pattern, self.finding_explanation, self.qualifier):
            self.finding_panel.body.addWidget(widget)
        self.finding_panel.body.addStretch()
        reasoning = QPushButton('Read full reasoning')
        reasoning.clicked.connect(lambda: self.open_context('Reasoning'))
        self.finding_panel.body.addWidget(reasoning)
        self.primary_reasoning = reasoning
        self.splitter.addWidget(source)
        self.splitter.addWidget(self.finding_panel)
        self.splitter.setSizes([500, 420])
        layout.addWidget(self.splitter)
        layout.addWidget(label('Three separate forensic hypotheses', 'card', bold=True))
        grid = QGridLayout()
        self.cards = {}
        for index, (hid, name) in enumerate(HYPOTHESES.items()):
            card = HypothesisCard(name, self.open_context)
            card.hypothesis_id = hid
            self.cards[hid] = card
            grid.addWidget(card, 0, index)
            grid.setColumnStretch(index, 1)
        layout.addLayout(grid)
        layout.addWidget(label('Camera compatibility does not establish authenticity or exclude synthetic creation or editing.', 'caption'))
        self.evidence_panel = Panel('Key recorded evidence')
        self.evidence_note = label('', 'caption')
        self.evidence_panel.body.addWidget(self.evidence_note)
        self.evidence_grid = QGridLayout()
        self.evidence_panel.body.addLayout(self.evidence_grid)
        self.evidence_rows = []
        layout.addWidget(self.evidence_panel)
        self.scope = Panel('Limitations and coverage')
        self.limitations = label('', 'secondary')
        self.scope.body.addWidget(self.limitations)
        detail = QPushButton('Read all limitations and stage availability')
        detail.clicked.connect(self.show_scope)
        self.scope.body.addWidget(detail)
        self.scope_button = detail
        layout.addWidget(self.scope)
        narrative = QPushButton('Open full investigation narrative')
        narrative.clicked.connect(self.show_narrative)
        self.narrative_button = narrative
        layout.addWidget(narrative)
        layout.addStretch()
        self.scroll = scroll_area(content)
        body.addWidget(self.scroll, 1)
        # The existing narrative widget and update path remain single-owned.
        self.narrative_dialog = QDialog(host)
        self.narrative_dialog.setWindowTitle('Full investigation narrative')
        self.narrative_dialog.resize(900, 700)
        narrative_layout = QVBoxLayout(self.narrative_dialog)
        host.summary_box = QTextEdit()
        host.summary_box.setReadOnly(True)
        host.summary_box.setAccessibleName('Current investigation narrative')
        narrative_layout.addWidget(host.summary_box)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.narrative_dialog.reject)
        narrative_layout.addWidget(close)
        apply_theme(self.narrative_dialog)
        self.snapshot = None

    def open_context(self,destination,hypothesis=None):
        from explorer_presenter import identity
        if destination in ('Evidence','Reasoning') and self.snapshot:
            return self.host.workspace.navigate_context(destination,identity(self.snapshot),
                hypothesis=hypothesis or self.snapshot.summary.primary_hypothesis,
                tab='Hypotheses' if destination=='Reasoning' else None)
        return self.navigate(destination)

    def show_narrative(self):
        self.narrative_dialog.show()
        self.narrative_dialog.raise_()
        self.narrative_dialog.activateWindow()

    def show_detail(self, title, text):
        dialog = QDialog(self.host)
        dialog.setWindowTitle(title)
        dialog.resize(720, 520)
        body = QVBoxLayout(dialog)
        view = QTextEdit()
        view.setReadOnly(True)
        view.setPlainText(text)
        body.addWidget(view)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(dialog.reject)
        body.addWidget(close)
        apply_theme(dialog)
        dialog.exec()

    def show_scope(self):
        self.show_detail('Recorded limitations and coverage', self.scope_text)

    def show_identity(self):
        source = self.snapshot.source if self.snapshot else None
        self.show_detail('Recorded source identity',
            f'Path: {source.path if source else "Not recorded"}\n\nSHA-256: {source.sha256 if source and source.sha256 else "Not recorded; source cannot be authenticated against this historical result"}\n\n'
            f'Captured profile: {source.profile if source and source.profile else "Not recorded"}\n\n'
            + self.preview.message.text())

    def evidence_detail(self, item):
        self.show_detail('Recorded evidence', '\n\n'.join((
            item.label or item.evidence_id, f'Hypothesis: {item.hypothesis_id}', f'Role: {item.role}',
            f'ID: {item.evidence_id}', f'Source: {item.source_detector or "Not recorded"}',
            f'Reliability: {item.reliability or "Not recorded"}',
            item.interpretation or 'Interpretation not recorded.',
            f'Lineage reference: {item.lineage_reference or "Not recorded; inspect the original decision trace"}')))

    def bind(self, snapshot):
        self.snapshot = snapshot
        summary = snapshot.summary
        complete = summary.status == 'completed' and snapshot.result_id is not None
        source = snapshot.source
        self.heading.setText(summary.image_name or 'Investigation overview')
        self.header.setText(f'{"Stored result · " if source and source.stored else ""}{summary.status.replace("_", " ").capitalize()} · '
            f'Profile: {source.profile if source and source.profile else "Not captured yet / unavailable"} · '
            f'Source {(source.sha256[:12] if source and source.sha256 else "identity unrecorded")} · '
            f'{"Recorded result available" if complete else "No completed result"}')
        self.header.setToolTip(f'Session: {snapshot.session_id}\nInvocation: {snapshot.analysis_id or "Not recorded"}\nResult: {snapshot.result_id or "Unavailable"}')
        self.source_identity.setText(source.sha256 if source and source.sha256 else 'Source SHA-256 not recorded')
        self.source_identity.setToolTip('Recorded source SHA-256. Preview bytes must match this identity when available.')
        self.preview.set_source(source.path if source else None, (snapshot.session_id, snapshot.analysis_id), source.sha256 if source else None)
        self.confidence.set_tier(summary.confidence_tier if complete else None)
        self.finding_title.setText(HYPOTHESES.get(summary.primary_hypothesis, summary.primary_hypothesis or 'Primary hypothesis not recorded') if complete else 'No completed finding')
        self.pattern.setText(('Dominant pattern · ' + (summary.primary_finding or 'Not recorded')) if complete else '')
        primary = next((h for h in snapshot.hypotheses if h.hypothesis_id == summary.primary_hypothesis), None)
        states = {'empty': 'Choose an image to begin an investigation.',
                  'image_selected': 'Source selected. Configure and run analysis to obtain findings.',
                  'analyzing': 'Analysis in progress. No conclusion is available for this invocation.',
                  'failed': 'Analysis failed. Review the execution log, check the source and settings, then run again.',
                  'cancelled': 'Analysis cancelled or superseded. No completed finding is available.'}
        explanation = (primary.finding if primary and primary.finding else 'Structured interpretation not recorded. Open the full narrative for any available historical content.') if complete else states.get(summary.status, 'No completed finding.')
        if not complete and source and source.error:
            explanation += '\n' + source.error
        self.finding_explanation.setText(excerpt(explanation, 440))
        self.finding_explanation.setToolTip(explanation)
        self.qualifier.setText(excerpt('\n'.join(summary.limitations), 210) if complete and summary.limitations else 'Confidence is a support tier, not a probability or proof of authenticity.')
        self.qualifier.setToolTip('\n'.join(summary.limitations))
        for hid, card in self.cards.items():
            card.bind(next((item for item in snapshot.hypotheses if item.hypothesis_id == hid), None), complete)
        self.primary_reasoning.setEnabled(complete and bool(snapshot.hypotheses))
        self.primary_reasoning.setToolTip('Read the full recorded reasoning.' if complete and snapshot.hypotheses else 'No structured reasoning is available.')
        for destination, action in self.actions.items():
            enabled = complete or (destination == 'Provenance' and summary.status != 'empty')
            action.setEnabled(enabled)
            action.setToolTip('Open the existing workspace for this investigation.' if enabled else 'Available after a completed analysis; use the sidebar to inspect the workspace now.')
        self.narrative_button.setEnabled(complete)
        self.narrative_button.setToolTip('Open the retained narrative, including current annotation appendix.' if complete else 'No completed narrative is available.')
        self._bind_evidence(snapshot, complete)
        lines = [f'Coverage: {snapshot.coverage_status or "Not recorded"}',
                 f'Provenance verification: {snapshot.provenance.verification_status}',
                 f'Provenance declaration: {snapshot.provenance.declaration_status or "Not recorded"}']
        for item in snapshot.hypotheses:
            lines.extend(f'{HYPOTHESES.get(item.hypothesis_id, item.hypothesis_id)}: {value}' for value in item.limitations)
        stages = [f'{s.stage_id} · {s.status or "Not recorded"}' + (f' — {s.reason}' if s.reason else '') for s in snapshot.stages if s.status != 'success']
        self.scope_text = '\n\n'.join(lines + stages + ['Missing measurements are unavailable information, not negative evidence.']) if complete else 'No completed coverage or limitations are available.'
        overview_lines = lines[:3] + list(summary.limitations[:3])
        if stages:
            overview_lines += [f'{len(stages)} stages are not successful. ' + excerpt(stages[0], 180)]
        self.limitations.setText('\n'.join(overview_lines) + '\nMissing measurements do not establish authenticity.' if complete else self.scope_text)
        self.scope_button.setEnabled(complete)
        self.scope_button.setToolTip('Read all recorded hypothesis limitations and non-success stage reasons.' if complete else 'No completed coverage is available.')

    def _bind_evidence(self, snapshot, complete):
        while self.evidence_grid.count():
            widget = self.evidence_grid.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self.evidence_rows = []
        self.evidence_note.setText('First two observations per role, in recorded hypothesis/source order. No ranking or independent vote count. Contextual observations and all remaining entries are in Evidence.' if complete else 'Evidence appears after analysis. Missing observations imply no conclusion.')
        for column, (role, title) in enumerate((('supporting_evidence', 'Supporting'), ('contradicting_evidence', 'Contradicting'), ('moderating_evidence', 'Moderating'))):
            panel = Panel(title)
            items = [e for e in snapshot.evidence if e.role == role][:2] if complete else []
            for item in items:
                row = QWidget()
                layout = QVBoxLayout(row)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(label(excerpt(item.label or item.evidence_id, 110), 'secondary', bold=True))
                layout.addWidget(label(f'{HYPOTHESES.get(item.hypothesis_id, item.hypothesis_id)} · {item.source_detector or "Source not recorded"}', 'caption'))
                layout.addWidget(label(excerpt(item.interpretation or 'Interpretation not recorded.', 150), 'caption'))
                button = QPushButton('Observation details')
                button.setToolTip(item.evidence_id)
                button.clicked.connect(lambda checked=False, evidence=item: self.evidence_detail(evidence))
                layout.addWidget(button)
                panel.body.addWidget(row)
                self.evidence_rows.append(item)
            if not items:
                panel.body.addWidget(label('No observations recorded for this role.' if complete else 'Awaiting analysis.', 'caption'))
            panel.body.addStretch()
            self.evidence_grid.addWidget(panel, 0, column)
            self.evidence_grid.setColumnStretch(column, 1)
