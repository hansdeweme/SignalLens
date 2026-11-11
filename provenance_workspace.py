"""Metadata browsing and existing revision-owned contextual research controls."""
import json
from copy import deepcopy
from PyQt6.QtCore import Qt,QObject,QRunnable,pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QSplitter,QLineEdit,QComboBox,QPushButton,QTabWidget
from gui_components import label,MetadataRow,scroll_area
from gui_design_system import SPACE
from explorer_workspace import table,text_view
from explorer_presenter import identity
from artifact_presenter import discovery_context
from source_image_viewer import preview_pool
from provenance_presenter import build_provenance,recover_metadata


class _MetadataDelivery(QObject):
    completed=pyqtSignal(object,object)


class _MetadataJob(QRunnable):
    def __init__(self,key,context):
        super().__init__()
        self.key,self.context=key,context
        self.delivery=_MetadataDelivery()

    def run(self):
        self.delivery.completed.emit(self.key,recover_metadata(self.context))


class ProvenanceWorkspace(QWidget):
    def __init__(self,host,route):
        super().__init__()
        self.host,self.route=host,route
        self.key=None
        self.presentation=None
        self.snapshot=None
        self.payload=None
        self.note=None
        self.data={}
        body=QVBoxLayout(self)
        body.setContentsMargins(SPACE[3],SPACE[1],0,0)
        body.addWidget(label('Provenance','section',bold=True))
        self.header=label('','caption');body.addWidget(self.header)
        summary=QHBoxLayout()
        self.declaration=MetadataRow('Recorded declaration')
        self.verification=MetadataRow('Recorded verification flag')
        summary.addWidget(self.declaration);summary.addWidget(self.verification)
        body.addLayout(summary)
        self.description=label('','secondary');body.addWidget(self.description)
        self.metadata_description=label('','caption');body.addWidget(self.metadata_description)
        self.tabs=QTabWidget()
        self.external_context=label('','caption')
        body.addWidget(self.external_context)
        metadata=QWidget();layout=QVBoxLayout(metadata)
        self.search=QLineEdit();self.search.setPlaceholderText('Search recorded field names and values')
        self.search.setAccessibleName('Search metadata names and values')
        self.namespace=QComboBox();self.namespace.setAccessibleName('Filter metadata namespace')
        filters=QHBoxLayout();filters.addWidget(self.search,1);filters.addWidget(self.namespace)
        layout.addLayout(filters)
        self.splitter=QSplitter(Qt.Orientation.Vertical)
        self.table,self.model=table((('Namespace',lambda r:r.namespace),('Technical field',lambda r:r.tag),
            ('Recorded value',lambda r:r.preview),('Trust',lambda r:r.trust)),'Recorded metadata fields')
        self.details=text_view('Selected metadata exact value, source, interpretation and limitations')
        self.splitter.addWidget(self.table);self.splitter.addWidget(self.details)
        self.splitter.setSizes([280,180]);layout.addWidget(self.splitter,1)
        actions=QHBoxLayout()
        self.related=QPushButton('Related evidence');self.related.clicked.connect(self.open_evidence)
        actions.addWidget(self.related)
        for title,destination in (('Reasoning','Reasoning'),('Reports','Reports')):
            button=QPushButton(title)
            button.clicked.connect(lambda checked=False,d=destination:self.open_context(d))
            actions.addWidget(button)
        layout.addLayout(actions)
        self.tabs.addTab(metadata,'Recorded metadata')
        research=QWidget();rbody=QVBoxLayout(research)
        rbody.addWidget(label('Contextual research records external claims and analyst notes. Post-analysis edits do not change frozen forensic findings.','secondary'))
        self.revision=label('','caption');rbody.addWidget(self.revision)
        host.osint_group=host.build_osint_group()
        host.osint_group.setMinimumHeight(290)
        host.osint_findings_list.setMinimumHeight(70)
        rbody.addWidget(host.osint_group,1)
        self.annotation_detail=text_view('Selected contextual source, notes and recorded research timestamps')
        self.annotation_detail.setMinimumHeight(150)
        rbody.addWidget(self.annotation_detail,1)
        host.osint_findings_list.currentRowChanged.connect(self.show_annotation)
        self.tabs.addTab(scroll_area(research),'Contextual research / OSINT')
        body.addWidget(self.tabs,1)
        self.message=label('','caption');body.addWidget(self.message)
        self.table.selectionModel().currentRowChanged.connect(self.select_field)
        self.search.textChanged.connect(self.filter_rows)
        self.namespace.currentIndexChanged.connect(self.filter_rows)

    def bind(self,snapshot):
        self.snapshot=snapshot
        key=identity(snapshot)
        self.header.setText(f'Investigation {snapshot.session_id[:8]} · Analysis revision {snapshot.analysis_revision} · Source hash: '+
            ((snapshot.source.sha256 or 'Not recorded') if snapshot.source else 'Not recorded'))
        self.revision.setText(f'Committed annotation revision: {snapshot.annotation_revision} · Research edits use the existing Save/Cancel workflow.')
        self.show_annotation()
        if key==self.key:return
        self.key=key
        self.data=self.host.session.summary_data() or {}
        self.payload=None;self.note=None
        self.search.clear()
        if snapshot.summary.status=='completed':
            raw=getattr(self.host.analysis_state,'exif_payload',None)
            if isinstance(raw,dict):self.payload=deepcopy(raw)
        self.rebuild()
        if snapshot.summary.status=='completed' and self.host.session.imported_from:
            context=discovery_context(self.host.session,snapshot)
            job=_MetadataJob(key,json.loads(json.dumps(context,default=str)))
            job.delivery.completed.connect(self.accept_metadata,Qt.ConnectionType.QueuedConnection)
            preview_pool().start(job)

    def accept_metadata(self,key,result):
        if self.host._closing or key!=self.key or key!=identity(self.host.view_snapshot):return False
        self.payload,self.note=result
        self.rebuild()
        return True

    def rebuild(self):
        self.presentation=build_provenance(self.snapshot,self.data,self.payload,self.note)
        self.declaration.set_value(self.presentation.declaration)
        self.verification.set_value(self.presentation.verification.capitalize())
        self.description.setText(self.presentation.extraction+' · Cryptographic verification unsupported. Presence is not authentication.')
        current=self.namespace.currentData()
        self.namespace.blockSignals(True);self.namespace.clear();self.namespace.addItem('All namespaces',None)
        for value in dict.fromkeys(r.namespace for r in self.presentation.fields):self.namespace.addItem(value,value)
        self.namespace.setCurrentIndex(max(0,self.namespace.findData(current)));self.namespace.blockSignals(False)
        self.filter_rows()

    def filter_rows(self,*args):
        if not self.presentation:return
        current=self.selected_field()
        query=self.search.text().casefold();namespace=self.namespace.currentData()
        rows=tuple(r for r in self.presentation.fields if (namespace is None or r.namespace==namespace)
                   and query in (r.tag+' '+r.value).casefold())
        self.model.set_rows(rows);self.details.clear();self.related.setEnabled(False)
        if rows:
            index=next((i for i,r in enumerate(rows) if current and r.field_id==current.field_id),0)
            self.table.selectRow(index)
            self.table.scrollTo(self.model.index(index,0))
        else:self.details.setPlainText('No recorded fields match this filter.' if self.presentation.fields else
            'No metadata fields are recorded for this result. Missing metadata is not evidence of image origin.')
        self.message.setText('Recorded metadata only · Verification unsupported · Full limitations in field details and this tooltip.')
        self.message.setToolTip('\n'.join(self.presentation.limitations))
        for i,width in enumerate((140,230,330)):self.table.setColumnWidth(i,width)

    def selected_field(self):
        index=self.table.currentIndex()
        return self.model.rows[index.row()] if index.isValid() and index.row()<len(self.model.rows) else None

    def select_field(self,*args):
        row=self.selected_field()
        if not row:return
        self.related.setEnabled(bool(row.evidence_ids))
        value=row.value[:64000]+('\n[Value preview limited to 64,000 characters; original recorded payload retains the complete value.]' if len(row.value)>64000 else '')
        self.details.setPlainText(row.tag+'\nNamespace: '+row.namespace+'\nSource: '+', '.join(row.origins)+
            '\nTrust: '+row.trust+'\n\nRecorded value\n'+value+'\n\nRecorded interpretation\n'+
            ('\n'.join(row.interpretations) or 'Not recorded')+'\n\nRelated evidence: '+(', '.join(row.evidence_ids) or 'No explicit association')+
            '\n\nLimitations\n'+'\n'.join(self.presentation.limitations))

    def show_annotation(self,*args):
        if not self.snapshot:return
        try:annotations=json.loads(self.snapshot.annotations_json) or {}
        except ValueError:annotations={}
        matches=annotations.get('matches') or []
        index=self.host.osint_findings_list.currentRow()
        selected=matches[index] if 0<=index<len(matches) else None
        detail=(f'Committed annotation revision: {self.snapshot.annotation_revision}\n'
            'Research started: '+str(annotations.get('started_at_utc') or 'Not recorded')+
            '\nResearch completed: '+str(annotations.get('completed_at_utc') or 'Not recorded')+
            '\nAnalyst notes: '+str(annotations.get('analyst_notes') or 'Not recorded'))
        if selected:
            from source_image_verification import validate
            verification = validate(selected, annotations.get('image_sha256'))
            detail += '\nSource-image verification: ' + (json.dumps(verification, indent=2) if verification else
                'Unavailable / not established. Missing or stale evidence cannot verify association.')
            detail+='\n\nSelected external claim / analyst observation\n'+'\n'.join(
                title+': '+str(selected.get(key) or 'Not recorded') for key,title in (
                    ('title','Title'),('page_url','Source page URL'),('image_url','Source image URL'),('provider','Research provider'),
                    ('notes','Analyst context'),('source_type','Analyst source classification'),('first_seen_estimate','First seen (estimate)'),
                    ('claim_process','Claimed process'),('claim_text','Relevant source claim'),('model_family','Claimed model'),
                    ('workflow_details','Source workflow details'),('claimed_by','Claim made by'),('attribution','Reported attribution'),
                    ('image_association','Analyst image-association assertion'),('association_method','Association method'),
                    ('association_details','Association basis'),('source_dependency','Source dependence'),('claim_limitations','Remaining uncertainty')))
        else:detail+='\n\nNo contextual source selected.'
        self.annotation_detail.setPlainText(detail)

    def open_evidence(self):
        row=self.selected_field()
        if row and row.evidence_ids:self.route('Evidence',self.key,evidence=row.evidence_ids[0])

    def open_context(self,destination):
        if self.snapshot:self.route(destination,self.key,annotation_revision=self.snapshot.annotation_revision)

    def focus(self,evidence=None,field=None):
        self.tabs.setCurrentIndex(0)
        if not evidence and not field:return True
        self.search.clear();self.namespace.setCurrentIndex(0)
        index=next((i for i,r in enumerate(self.model.rows) if
            (evidence and evidence in r.evidence_ids) or (field and field==r.field_id)),None)
        if index is None:
            self.table.clearSelection();self.table.setCurrentIndex(self.model.index(-1,-1))
            self.details.setPlainText('Requested provenance field association is not recorded in this investigation.')
            self.related.setEnabled(False)
            return False
        self.table.selectRow(index)
        self.table.scrollTo(self.model.index(index,0))
        return True
