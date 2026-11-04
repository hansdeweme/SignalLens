"""Native model/view evidence and reasoning explorers over immutable records."""
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal
from PyQt6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QLineEdit,QPushButton,
    QTableView,QAbstractItemView,QSplitter,QPlainTextEdit,QTabWidget,QDialog,QDialogButtonBox)
from gui_components import label, EmptyState
from gui_design_system import SPACE, apply_theme
from explorer_presenter import display
import json

HYPOTHESES = {'synthetic_origin':'Synthetic origin','localized_editing':'Localized editing',
              'camera_acquisition':'Camera-acquisition compatibility'}
ROLE_NAMES = {'supporting_evidence':'Supporting','contradicting_evidence':'Contradicting',
              'moderating_evidence':'Moderating','contextual_evidence':'Contextual'}


def text_view(name):
    view = QPlainTextEdit()
    view.setReadOnly(True)
    view.setAccessibleName(name)
    return view


class RecordModel(QAbstractTableModel):
    def __init__(self,columns,parent=None):
        super().__init__(parent)
        self.columns = columns
        self.rows = ()

    def set_rows(self,rows):
        self.beginResetModel()
        self.rows = tuple(rows)
        self.endResetModel()

    def rowCount(self,parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self,parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.columns)

    def data(self,index,role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role in (Qt.ItemDataRole.DisplayRole,Qt.ItemDataRole.ToolTipRole):
            return display(self.columns[index.column()][1](self.rows[index.row()]))
        return None

    def headerData(self,section,orientation,role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.columns[section][0]
        return super().headerData(section,orientation,role)


def table(columns,name):
    view = QTableView()
    model = RecordModel(columns,view)
    view.setModel(model)
    view.setAccessibleName(name)
    view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    view.setWordWrap(False)
    view.verticalHeader().hide()
    view.horizontalHeader().setStretchLastSection(True)
    view.setMinimumHeight(100)
    return view,model


def readable_value(value,depth=0):
    if isinstance(value,str):
        return value
    if depth>6:
        return display(value)
    if isinstance(value,list):
        if not value:return 'None recorded'
        return '\n'.join('• '+readable_value(item,depth+1) for item in value)
    if isinstance(value,dict):
        if not value:return 'None recorded'
        return '\n'.join(str(key).replace('_',' ').title()+': '+readable_value(item,depth+1)
                         for key,item in value.items())
    return display(value)


def record_text(row):
    rendered=[]
    priority=('final_confidence_tier','tier','policy_rule','rationale','explanation','limitations',
              'reliability_limitations','reason','supporting_evidence','contradicting_evidence','moderating_evidence')
    order={key:index for index,key in enumerate(priority)}
    for key,value in sorted(row.fields,key=lambda item:order.get(item[0],len(order))):
        try:
            parsed=json.loads(value) if value.startswith(('[','{')) else value
        except (ValueError,TypeError):
            parsed=value
        rendered.append(key.replace('_',' ').title()+':\n'+readable_value(parsed))
    return '\n\n'.join(rendered)


class AuditPane(QWidget):
    selected = pyqtSignal(object)

    def __init__(self,name,columns=None):
        super().__init__()
        body = QVBoxLayout(self)
        body.setContentsMargins(0,0,0,0)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.table,self.model = table(columns or (
            ('Record',lambda r:r.title),('Hypothesis',lambda r:r.hypothesis_id),
            ('Outcome',lambda r:r.outcome),('Explanation',lambda r:r.explanation)),name)
        self.details = text_view(name+' selected record; exact copyable values')
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.details)
        self.splitter.setSizes([320,230])
        body.addWidget(self.splitter)
        self.current = None
        self.table.selectionModel().currentRowChanged.connect(self.select)

    def bind(self,rows):
        selected_id = getattr(self.current,'record_id',getattr(self.current,'evidence_id',None))
        self.current = None
        self.model.set_rows(rows)
        self.details.setPlainText('Structured records unavailable for this result.' if not rows else '')
        if rows:
            index = next((i for i,r in enumerate(rows) if getattr(r,'record_id',getattr(r,'evidence_id',None))==selected_id),0)
            self.table.selectRow(index)
        self.table.resizeColumnsToContents()
        for column in range(self.model.columnCount()-1):
            self.table.setColumnWidth(column,min(260,max(110,self.table.columnWidth(column))))

    def select(self,index,previous=QModelIndex()):
        self.current = self.model.rows[index.row()] if index.isValid() else None
        if self.current:
            row = self.current
            if hasattr(row,'raw'):
                intro = (f'{row.evidence_id}\nRaw base: {row.raw or "Not recorded"} · Credited: {row.credited or "Not recorded"}'
                    f'\nReliability multiplier: {row.reliability_multiplier or "Not recorded"}'
                    f' · Adjusted base: {row.final or "Not recorded"} · Suppressed: {row.suppressed or "Not recorded"}'
                    f'\nRecorded reason: {row.reason or "Not recorded"}\nThese are base-allocation values, before aggregate transforms and penalties.')
            else:
                intro = row.title+'\nOutcome: '+display(row.outcome)+'\n'+(row.explanation or 'Explanation not recorded')
            self.details.setPlainText(intro+'\n\n'+record_text(row))
            self.selected.emit(self.current)


class EvidenceWorkspace(QWidget):
    def __init__(self,host,route):
        super().__init__()
        self.host,self.route = host,route
        self.snapshot = None
        self.current = None
        self.history = []
        self._restoring = False
        body = QVBoxLayout(self)
        body.setContentsMargins(SPACE[3],SPACE[1],0,0)
        body.addWidget(label('Evidence Explorer','section',bold=True))
        self.context = label('No completed result.','caption')
        body.addWidget(self.context)
        self.empty = EmptyState('No completed result','Select an image and run analysis, or load a stored summary.')
        body.addWidget(self.empty)
        filters = QHBoxLayout()
        self.filters = {}
        for key,title in (('hypothesis','Hypothesis'),('role','Role'),('detector','Detector'),
                          ('reliability','Reliability'),('availability','Availability')):
            combo = QComboBox()
            combo.setAccessibleName('Filter evidence by '+title.lower())
            combo.addItem('All '+title.lower(),None)
            combo.setMinimumWidth(80)
            combo.currentIndexChanged.connect(self.filter_rows)
            filters.addWidget(combo,1)
            self.filters[key] = combo
        body.addLayout(filters)
        search = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search evidence ID, label or detector')
        self.search.setAccessibleName('Search recorded evidence')
        self.search.textChanged.connect(self.filter_rows)
        search.addWidget(self.search,1)
        reset = QPushButton('Clear filters')
        reset.clicked.connect(self.clear_filters)
        search.addWidget(reset)
        self.back = QPushButton('Back')
        self.back.clicked.connect(self.go_back)
        search.addWidget(self.back)
        body.addLayout(search)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.table,self.model = table((('Hypothesis',lambda r:HYPOTHESES.get(r.hypothesis_id,r.hypothesis_id)),
            ('Role',lambda r:ROLE_NAMES.get(r.role,r.role)),('Observation',lambda r:r.label),
            ('Detector',lambda r:r.detector_id),('Reliability',lambda r:r.reliability),
            ('Availability',lambda r:r.availability)),'Hypothesis-scoped evidence')
        self.table.selectionModel().currentRowChanged.connect(self.select)
        self.splitter.addWidget(self.table)
        self.tabs = QTabWidget()
        self.details = text_view('Measured observation, derived inference and hypothesis relevance')
        self.tabs.addTab(self.details,'Observation & relevance')
        self.lineage = AuditPane('Direct lineage relationships',(
            ('Relationship',lambda r:r.outcome),('Node ID',lambda r:r.record_id),
            ('Source / availability',lambda r:r.explanation)))
        self.lineage.table.doubleClicked.connect(self.follow_lineage)
        self.tabs.addTab(self.lineage,'Lineage')
        self.technical = text_view('Original evidence fields and numerical references')
        self.tabs.addTab(self.technical,'Technical detail')
        self.splitter.addWidget(self.tabs)
        self.splitter.setSizes([310,300])
        body.addWidget(self.splitter,1)
        actions = QHBoxLayout()
        self.artifacts = QComboBox()
        self.artifacts.setAccessibleName('Explicitly associated forensic artifacts')
        actions.addWidget(self.artifacts,1)
        self.open_artifact = QPushButton('Open artifact')
        self.open_artifact.clicked.connect(self.show_artifact)
        actions.addWidget(self.open_artifact)
        for title,tab in (('Hypothesis','Hypotheses'),('Confidence','Confidence'),('Contributions','Scorecard')):
            button = QPushButton(title)
            button.clicked.connect(lambda checked=False,t=tab:self.show_reasoning(t))
            actions.addWidget(button)
        provenance=QPushButton('Provenance')
        provenance.clicked.connect(self.show_provenance)
        actions.addWidget(provenance)
        body.addLayout(actions)
        self.message = label('','caption')
        body.addWidget(self.message)
        self.compatibility_details = text_view('Legacy evidence projection')
        self.compatibility_details.hide()
        self.compatibility_details.setParent(self)

    def bind(self,snapshot):
        old_identity = self.snapshot.identity if self.snapshot else None
        selected_key = self.current.key if self.current else None
        if old_identity != snapshot.identity:
            self.history.clear()
            selected_key = None
        self.snapshot = snapshot
        self.message.clear()
        self.context.setText('Primary: '+(snapshot.primary_hypothesis or 'Not recorded')+
            ' · Coverage: '+(snapshot.coverage or 'Not recorded')+' · Roles are relative to each hypothesis.')
        values = {'hypothesis':[(k,HYPOTHESES.get(k,k)) for k in dict.fromkeys(r.hypothesis_id for r in snapshot.evidence)],
                  'role':[(k,ROLE_NAMES.get(k,k)) for k in dict.fromkeys(r.role for r in snapshot.evidence)]}
        for name,attribute in (('detector','detector_id'),('reliability','reliability'),('availability','availability')):
            values[name] = [(v or '__unknown__',v or 'Not recorded') for v in dict.fromkeys(getattr(r,attribute) for r in snapshot.evidence)]
        for name,combo in self.filters.items():
            current = combo.currentData() if old_identity == snapshot.identity else None
            combo.blockSignals(True)
            combo.clear()
            combo.addItem('All '+name,None)
            for value,title in values[name]: combo.addItem(title,value)
            combo.setCurrentIndex(max(0,combo.findData(current)))
            combo.blockSignals(False)
        if old_identity != snapshot.identity:
            self.search.blockSignals(True)
            self.search.clear()
            self.search.blockSignals(False)
        self.filter_rows(selected_key=selected_key)

    def clear_filters(self):
        for combo in self.filters.values():
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self.filter_rows()

    def filter_rows(self,*args,selected_key=None):
        if not self.snapshot: return
        selected_key = selected_key or (self.current.key if self.current else None)
        attrs = {'hypothesis':'hypothesis_id','role':'role','detector':'detector_id',
                 'reliability':'reliability','availability':'availability'}
        query = self.search.text().casefold()
        rows = tuple(r for r in self.snapshot.evidence if all(
            combo.currentData() is None or (getattr(r,attrs[name]) or '__unknown__') == combo.currentData()
            for name,combo in self.filters.items()) and query in (r.evidence_id+' '+r.label+' '+(r.detector_id or '')).casefold())
        self.current = None
        self.model.set_rows(rows)
        self.details.clear()
        self.technical.clear()
        self.lineage.bind(())
        self.artifacts.clear()
        self.open_artifact.setEnabled(False)
        if rows:
            index = next((i for i,r in enumerate(rows) if r.key == selected_key),0)
            self.table.selectRow(index)
        else:
            self.details.setPlainText('No evidence matches these filters.' if self.snapshot.evidence else
                                      'Structured evidence unavailable; missing observations imply no conclusion.')
        self.back.setEnabled(bool(self.history))
        for i,width in enumerate((180,115,270,155,115)): self.table.setColumnWidth(i,width)

    def select(self,index,previous=QModelIndex()):
        if not index.isValid() or not self.snapshot: return
        row = self.model.rows[index.row()]
        if self.current and self.current.key != row.key and not self._restoring:
            self.history = (self.history+[self.current.key])[-64:]
        self.current = row
        self.details.setPlainText(f'{row.label}\nID: {row.evidence_id}\n\nMeasured observation\n{row.observation}'
            f'\n\nDerived inference\n{row.interpretation or "Not recorded"}'
            f'\n\nHypothesis relevance\n{HYPOTHESES.get(row.hypothesis_id,row.hypothesis_id)} · {ROLE_NAMES.get(row.role,row.role)}'
            f'\n\nDetector: {row.detector_id or "Not recorded"}\nReliability: {row.reliability or "Not recorded"}'
            f'\nAvailability / observed status: {row.availability or "Not recorded"}'
            '\nLimitations: '+('; '.join(row.limitations) or 'Not recorded in evidence detail; inspect hypothesis constraints.'))
        self.technical.setPlainText(record_text(row))
        self.artifacts.clear()
        for aid in row.artifact_ids: self.artifacts.addItem(aid,aid)
        if not row.artifact_ids: self.artifacts.addItem('No explicit artifact association',None)
        self.open_artifact.setEnabled(bool(row.artifact_ids))
        self.build_lineage(row)
        self.back.setEnabled(bool(self.history))

    def build_lineage(self,row):
        from explorer_models import AuditRecordView
        nodes = {n.node_id:n for n in self.snapshot.lineage}
        node = nodes.get(row.lineage_id)
        records = []
        if node:
            related = [('Selected node',node.node_id)]+[('Required parent',p) for p in node.parents]+[
                ('Optional parent (not proof of run use)',p) for p in node.optional_parents]+[
                ('Descendant',n.node_id) for n in nodes.values() if node.node_id in n.parents+n.optional_parents]
            shared = [(n.node_id,tuple(m for m in n.measurements if m in node.measurements))
                      for n in nodes.values() if n.node_id != node.node_id and set(n.measurements).intersection(node.measurements)]
            related += [('Shared recorded measurement ancestry',nid) for nid,measurements in shared]
            for relation,nid in related:
                n = nodes.get(nid)
                records.append(AuditRecordView(nid,nid,row.hypothesis_id,relation,
                    n.origin if n else 'Intermediate or unrecorded node; not a hypothesis evidence item',
                    (('family',display(n.family if n else None)),('kind',display(n.kind if n else None)),
                     ('measurement ancestry',display(n.measurements if n else None)),
                     ('source',n.origin if n else 'Not recorded'),
                     ('limitation','Shared computational ancestry is not proof of statistical redundancy or independence.'))))
        self.lineage.bind(records)
        if not records:
            self.lineage.details.setPlainText('No structured lineage relationship is recorded for this evidence. No parent is inferred from its ID.')

    def follow_lineage(self,index):
        if not self.snapshot or not index.isValid(): return
        target = self.lineage.model.rows[index.row()].record_id
        evidence = next((r for r in self.snapshot.evidence if r.lineage_id==target and
                         self.current and r.hypothesis_id==self.current.hypothesis_id),None)
        if evidence:
            if self.current: self.history.append(self.current.key)
            self.focus(evidence.hypothesis_id,evidence.evidence_id,evidence.role)
        else:
            self.message.setText('This is an intermediate or unlisted node. No hypothesis evidence item is recorded for it.')

    def focus(self,hypothesis=None,evidence=None,role=None,detector=None):
        self.clear_filters()
        for name,value in (('hypothesis',hypothesis),('role',role),('detector',detector)):
            if value is not None:
                combo = self.filters[name]
                index = combo.findData(value)
                if index < 0:
                    self.unavailable('Requested '+name+' is not recorded in this result.')
                    return False
                combo.setCurrentIndex(index)
        if evidence:
            index = next((i for i,r in enumerate(self.model.rows) if r.evidence_id==evidence),None)
            if index is None:
                self.unavailable('Requested evidence ID is unavailable: '+evidence)
                return False
            self.table.selectRow(index)
        return True

    def unavailable(self,message):
        self.current = None
        self.model.set_rows(())
        self.details.setPlainText(message)
        self.technical.clear()
        self.lineage.bind(())
        self.artifacts.clear()
        self.open_artifact.setEnabled(False)
        self.message.setText(message)

    def go_back(self):
        if not self.history:return
        key = self.history.pop()
        self._restoring = True
        try:self.focus(key[0],key[2],key[1])
        finally:self._restoring = False
        self.back.setEnabled(bool(self.history))

    def show_artifact(self):
        if self.snapshot and self.current:
            self.route('Image Forensics',self.snapshot.identity,artifact=self.artifacts.currentData(),
                       hypothesis=self.current.hypothesis_id,evidence=self.current.evidence_id)

    def show_reasoning(self,tab):
        if self.snapshot and self.current:
            self.route('Reasoning',self.snapshot.identity,hypothesis=self.current.hypothesis_id,
                       evidence=self.current.evidence_id,tab=tab,detector=self.current.detector_id)

    def show_provenance(self):
        if self.snapshot and self.current:
            self.route('Provenance',self.snapshot.identity,evidence=self.current.evidence_id)


class ReasoningWorkspace(QWidget):
    def __init__(self,host,route):
        super().__init__()
        self.host,self.route = host,route
        self.snapshot = None
        self.active_hypothesis = None
        body = QVBoxLayout(self)
        body.setContentsMargins(SPACE[3],SPACE[1],0,0)
        body.addWidget(label('Reasoning Explorer','section',bold=True))
        self.context = label('No completed result.','caption')
        body.addWidget(self.context)
        self.empty = EmptyState('No completed result','Run analysis or load a stored result.')
        body.addWidget(self.empty)
        commands = QHBoxLayout()
        self.hypothesis = QComboBox()
        self.hypothesis.setAccessibleName('Active reasoning hypothesis')
        self.hypothesis.currentIndexChanged.connect(self.change_hypothesis)
        commands.addWidget(self.hypothesis,1)
        evidence_button = QPushButton('Open evidence')
        evidence_button.clicked.connect(self.show_evidence)
        commands.addWidget(evidence_button)
        provenance = QPushButton('Provenance')
        provenance.clicked.connect(self.show_provenance)
        commands.addWidget(provenance)
        self.trace_button = QPushButton('Original Decision Trace')
        self.trace_button.clicked.connect(host.show_decision_trace_dialog)
        commands.addWidget(self.trace_button)
        body.addLayout(commands)
        self.tabs = QTabWidget()
        self.panes = {}
        for name in ('Hypotheses','Routes','Corroboration','Confidence'):
            pane = AuditPane(name)
            pane.selected.connect(lambda row:self.update_references())
            self.panes[name] = pane
            self.tabs.addTab(pane,name)
        self.scorecard = QWidget()
        scorebody = QVBoxLayout(self.scorecard)
        self.score_summary = label('','caption')
        scorebody.addWidget(self.score_summary)
        self.score_kind = QComboBox()
        self.score_kind.addItems(('Base contribution ledger','Recorded operations and reconciliation inputs'))
        self.score_kind.currentIndexChanged.connect(self.bind_scores)
        scorebody.addWidget(self.score_kind)
        self.score_ledger = AuditPane('Numerical contribution ledger',(
            ('Evidence',lambda r:r.evidence_id),('Polarity',lambda r:r.polarity),('Raw',lambda r:r.raw),
            ('Credited',lambda r:r.credited),('Reliability multiplier',lambda r:r.reliability_multiplier),
            ('Adjusted base',lambda r:r.final),('Suppressed',lambda r:r.suppressed),('Class',lambda r:r.classification)))
        self.score_operations = AuditPane('Operations, domain bonuses, penalties and transforms')
        scorebody.addWidget(self.score_ledger,1)
        scorebody.addWidget(self.score_operations,1)
        self.tabs.addTab(self.scorecard,'Scorecard')
        raw = QWidget()
        rawbody = QVBoxLayout(raw)
        rawbody.addWidget(label('The original trace is available for technical audit. Structured tabs show the recorded findings without recalculating them.','secondary'))
        self.raw_button = QPushButton('Open copyable raw trace')
        self.raw_button.clicked.connect(self.show_raw)
        rawbody.addWidget(self.raw_button)
        rawbody.addStretch()
        self.tabs.addTab(raw,'Raw trace')
        body.addWidget(self.tabs,1)
        links = QHBoxLayout()
        self.related_evidence = QComboBox()
        self.related_evidence.setAccessibleName('Evidence references in the selected reasoning record')
        links.addWidget(self.related_evidence,1)
        related = QPushButton('Open selected evidence')
        related.clicked.connect(self.show_evidence)
        links.addWidget(related)
        visual = QPushButton('Related visualization')
        visual.clicked.connect(self.show_artifact)
        links.addWidget(visual)
        body.addLayout(links)
        self.tabs.currentChanged.connect(self.update_references)
        self.message = label('','caption')
        body.addWidget(self.message)
        self.compatibility_details = text_view('Legacy reasoning projection')
        self.compatibility_details.setParent(self)
        self.compatibility_details.hide()

    def bind(self,snapshot):
        old = self.snapshot.identity if self.snapshot else None
        self.snapshot = snapshot
        self.message.setText('\n'.join(snapshot.issues))
        self.context.setText('Primary: '+(snapshot.primary_hypothesis or 'Not recorded')+' · '+
            (snapshot.primary_finding or 'Finding not recorded')+' · Coverage: '+(snapshot.coverage or 'Not recorded'))
        previous = self.hypothesis.currentData() if old == snapshot.identity else snapshot.primary_hypothesis
        self.hypothesis.blockSignals(True)
        self.hypothesis.clear()
        self.hypothesis.addItem('All recorded hypotheses',None)
        choices = {row.hypothesis_id:row for row in (*snapshot.hypotheses,*snapshot.confidence)}
        for row in choices.values():
            title = HYPOTHESES.get(row.hypothesis_id,row.hypothesis_id)
            self.hypothesis.addItem(title+(' · Primary' if row.hypothesis_id==snapshot.primary_hypothesis else ''),row.hypothesis_id)
        self.hypothesis.setCurrentIndex(max(0,self.hypothesis.findData(previous)))
        self.hypothesis.blockSignals(False)
        self.change_hypothesis()
        # Route order and the complete gate evaluation order are never sorted or inferred.
        self.panes['Routes'].bind(snapshot.routes)
        self.panes['Corroboration'].bind(snapshot.corroboration)
        self.bind_scores()
        self.raw_button.setEnabled(snapshot.identity.status=='completed')
        self.update_references()

    def change_hypothesis(self,*args):
        if not self.snapshot:return
        self.active_hypothesis = self.hypothesis.currentData()
        for name,rows in (('Hypotheses',self.snapshot.hypotheses),('Confidence',self.snapshot.confidence)):
            self.panes[name].bind(tuple(r for r in rows if not self.active_hypothesis or r.hypothesis_id==self.active_hypothesis))

    def bind_scores(self,*args):
        if not self.snapshot:return
        self.score_summary.setText(self.snapshot.score_summary)
        base = self.score_kind.currentIndex()==0
        self.score_ledger.setVisible(base)
        self.score_operations.setVisible(not base)
        self.score_ledger.bind(self.snapshot.contributions)
        self.score_operations.bind(self.snapshot.score_records)

    def focus(self,hypothesis=None,tab=None,detector=None):
        if hypothesis:
            index = self.hypothesis.findData(hypothesis)
            if index < 0:
                self.message.setText('Requested hypothesis is unavailable: '+hypothesis)
                self.hypothesis.setCurrentIndex(0)
                self.panes['Hypotheses'].bind(())
                self.panes['Confidence'].bind(())
                return False
            self.hypothesis.setCurrentIndex(index)
        if tab:
            found = False
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i)==tab:
                    self.tabs.setCurrentIndex(i)
                    found = True
            if not found:
                self.message.setText('Requested reasoning section is unavailable: '+tab)
                return False
        if tab=='Scorecard' and detector:
            self.score_kind.setCurrentIndex(0)
            index = next((i for i,r in enumerate(self.score_ledger.model.rows) if r.section==detector),None)
            if index is not None:self.score_ledger.table.selectRow(index)
            else:self.message.setText('No numerical contribution recorded for this detector; no value is inferred.')
        return True

    def show_evidence(self):
        if not self.snapshot:return
        pane = self.panes.get(self.tabs.tabText(self.tabs.currentIndex()))
        row = pane.current if pane else None
        evidence = self.related_evidence.currentData()
        hypothesis = row.hypothesis_id if row and row.hypothesis_id else self.active_hypothesis
        if evidence:
            related = next((r for r in self.snapshot.evidence if
                (r.evidence_id==evidence or r.lineage_id==evidence) and
                (not hypothesis or r.hypothesis_id==hypothesis)),None)
            if related:
                evidence = related.evidence_id
        self.route('Evidence',self.snapshot.identity,hypothesis=hypothesis,evidence=evidence)

    def update_references(self,*args):
        if not hasattr(self,'related_evidence'):return
        previous = self.related_evidence.currentData()
        self.related_evidence.clear()
        pane = self.panes.get(self.tabs.tabText(self.tabs.currentIndex()))
        row = pane.current if pane else None
        for eid in row.evidence_ids if row else ():
            self.related_evidence.addItem(eid,eid)
        if not self.related_evidence.count():
            self.related_evidence.addItem('No explicit evidence reference in this record',None)
        index = self.related_evidence.findData(previous)
        if index>=0:self.related_evidence.setCurrentIndex(index)

    def show_artifact(self):
        if not self.snapshot:return
        eid = self.related_evidence.currentData()
        pane = self.panes.get(self.tabs.tabText(self.tabs.currentIndex()))
        row = pane.current if pane else None
        hypothesis = row.hypothesis_id if row and row.hypothesis_id else self.active_hypothesis
        evidence = next((e for e in self.snapshot.evidence if (e.evidence_id==eid or e.lineage_id==eid)
                         and (not hypothesis or e.hypothesis_id==hypothesis)),None)
        if evidence and evidence.artifact_ids:
            self.route('Image Forensics',self.snapshot.identity,artifact=evidence.artifact_ids[0])
        else:
            self.message.setText('No explicit visualization association is recorded for the selected evidence reference.')

    def show_provenance(self):
        if not self.snapshot:return
        eid=self.related_evidence.currentData()
        evidence=next((e for e in self.snapshot.evidence if e.evidence_id==eid or e.lineage_id==eid),None)
        self.route('Provenance',self.snapshot.identity,evidence=evidence.evidence_id if evidence else None)

    def show_raw(self):
        if not self.snapshot:return
        dialog = QDialog(self.host)
        dialog.setWindowTitle('Recorded reasoning trace')
        dialog.resize(900,650)
        body = QVBoxLayout(dialog)
        view = text_view('Unmodified recorded reasoning trace')
        view.setPlainText(self.snapshot.raw_trace)
        body.addWidget(view)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(dialog.reject)
        body.addWidget(close)
        apply_theme(dialog)
        dialog.exec()
