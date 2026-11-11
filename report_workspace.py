"""Revision-bound preview and background export through the existing publisher."""
from pathlib import Path
from uuid import uuid4
from PyQt6.QtCore import Qt,QObject,QRunnable,QThreadPool,pyqtSignal
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QPushButton,QLineEdit,
    QTextBrowser,QFileDialog)
from gui_components import label,MetadataRow
from gui_design_system import SPACE,display_html
from investigation_session import InvestigationSession,InvestigationState
from investigation_reports import persist_report_snapshot,snapshot_is_current
from report_presentation import build_report_presentation
from explorer_presenter import identity

_pool=None


def export_pool():
    global _pool
    from PyQt6 import sip
    if _pool is None or sip.isdeleted(_pool):
        _pool=QThreadPool();_pool.setMaxThreadCount(1)
    return _pool


def write_export(snapshot,output):
    """Detached owner; each request has its own output/pointer, never a live-run pointer."""
    data=snapshot.payload()
    owner=InvestigationSession(session_id=snapshot.session_id,state=InvestigationState.COMPLETED,
        result_id=snapshot.result_id,annotation_revision=snapshot.annotation_revision,
        analysis_revision=data['investigation']['analysis_revision'],
        image_path=data['investigation'].get('image_path'),
        source_sha256=data['investigation'].get('source_sha256'))
    return persist_report_snapshot(owner,snapshot,owner.storage_directory(output))


class _ExportDelivery(QObject):
    completed=pyqtSignal(str,object,object)


class _ExportJob(QRunnable):
    def __init__(self,request,snapshot,output):
        super().__init__()
        self.request,self.snapshot,self.output=request,snapshot,output
        self.delivery=_ExportDelivery()

    def run(self):
        try:
            result=write_export(self.snapshot,self.output)
            error=None
        except Exception as exc:
            result=None;error=str(exc)
        self.delivery.completed.emit(self.request,result,error)


class _ReportDocument(QTextDocument):
    def loadResource(self,kind,url):
        # Preview never retrieves external URLs or unrelated local resources.
        return None


class ReportsWorkspace(QWidget):
    def __init__(self,host,route):
        super().__init__()
        self.host,self.route=host,route
        self.presentation=None
        self.snapshot=None
        self.key=None
        self.pending={}
        self.saved_paths={}
        self._render_pending=False
        body=QVBoxLayout(self)
        body.setContentsMargins(SPACE[3],SPACE[1],0,0)
        body.addWidget(label('Reports','section',bold=True))
        self.header=label('','caption');body.addWidget(self.header)
        self.report_state=MetadataRow('Run report synchronization')
        self.report_identity=MetadataRow('Result / annotation revision')
        identity_row=QHBoxLayout();identity_row.addWidget(self.report_state);identity_row.addWidget(self.report_identity)
        body.addLayout(identity_row)
        self.status=label('No completed report.','secondary');body.addWidget(self.status)
        commands=QHBoxLayout()
        self.format=QComboBox();self.format.addItems(('HTML','TXT','JSON'))
        self.format.setAccessibleName('Supported report preview format')
        self.format.currentIndexChanged.connect(self.render)
        commands.addWidget(self.format)
        refresh=QPushButton('Refresh preview');refresh.clicked.connect(self.refresh_preview);commands.addWidget(refresh)
        self.export=QPushButton('Export current snapshot');self.export.clicked.connect(self.start_export)
        commands.addWidget(self.export)
        host.open_json_button=QPushButton('Open Results Folder')
        host.open_json_button.clicked.connect(host.open_output_folder);commands.addWidget(host.open_json_button)
        load=QPushButton('Open stored summary…');load.clicked.connect(host.open_stored_summary);commands.addWidget(load)
        body.addLayout(commands)
        output=QHBoxLayout()
        self.output=QLineEdit(str(Path(host.settings['output_root'])/'exports'))
        self.output.setAccessibleName('Report export directory')
        output.addWidget(self.output,1)
        browse=QPushButton('Choose export folder');browse.clicked.connect(self.choose_folder);output.addWidget(browse)
        body.addLayout(output)
        self.preview=QTextBrowser()
        self.preview.setDocument(_ReportDocument(self.preview))
        self.preview.setOpenExternalLinks(False);self.preview.setOpenLinks(False)
        self.preview.setAccessibleName('Current report preview from the export snapshot')
        body.addWidget(self.preview,1)
        links=QHBoxLayout()
        for title,destination in (('Overview','Overview'),('Evidence','Evidence'),('Provenance / OSINT','Provenance')):
            button=QPushButton(title)
            button.clicked.connect(lambda checked=False,d=destination:self.open_context(d))
            links.addWidget(button)
        body.addLayout(links)
        self.details=label('Existing bundle: summary HTML/TXT/JSON, reasoning records and current contextual annotations. Export does not recalculate findings.','caption')
        body.addWidget(self.details)

    def bind(self,snapshot):
        self.snapshot=snapshot
        key=(identity(snapshot),snapshot.annotation_revision)
        self.header.setText(f'Investigation {snapshot.session_id} · Analysis revision {snapshot.analysis_revision} · Annotation revision {snapshot.annotation_revision}')
        if snapshot.source:
            self.header.setToolTip('Source: '+str(snapshot.source.path or 'Not recorded')+
                '\nSHA-256: '+str(snapshot.source.sha256 or 'Not recorded')+
                '\nCaptured profile: '+str(snapshot.source.profile or 'Not recorded'))
        if key==self.key:return
        self.key=key
        self.presentation=None
        self.saved_paths={}
        if snapshot.summary.status=='completed':
            try:
                self.presentation=build_report_presentation(self.host.session)
                self.status.setText('Preview current · Ready to export. Contextual OSINT is a separate revisioned appendix.')
            except (ValueError,TypeError,KeyError) as error:
                self.status.setText('Report preview unavailable: '+str(error))
        else:self.status.setText('No completed current result. Historical previews are cleared during reanalysis or investigation changes.')
        self.export.setEnabled(self.presentation is not None)
        self.render()

    def refresh_preview(self):
        if not self.snapshot:return
        self.key=None
        self.bind(self.host.view_snapshot)

    def render(self,*args):
        if not self.presentation:
            self._render_pending=False
            self.preview.clear();return
        # Building the snapshot remains immediate; Qt document layout is only
        # needed when this workspace is visible. Export uses the snapshot.
        self._render_pending=True
        if not self.isVisible():
            self.preview.clear();return
        self._render_pending=False
        format=self.format.currentText()
        if format=='HTML':self.preview.setHtml(display_html(self.presentation.html))
        else:self.preview.setPlainText(self.presentation.text if format=='TXT' else self.presentation.structured_json)

    def showEvent(self,event):
        super().showEvent(event)
        if self._render_pending:self.render()

    def choose_folder(self):
        path=QFileDialog.getExistingDirectory(self,'Report export directory',self.output.text())
        if path:self.output.setText(path)

    def start_export(self):
        presentation=self.presentation
        if self.host._closing or presentation is None:return False
        if not snapshot_is_current(self.host.session,presentation.snapshot):
            self.status.setText('Preview is stale. Refresh it before exporting.');return False
        if not self.output.text().strip():
            self.status.setText('Choose an export directory.');return False
        if any(snapshot==presentation.snapshot for snapshot in self.pending.values()):
            self.status.setText('This snapshot is already being exported.');return False
        request=uuid4().hex
        target=Path(self.output.text()).expanduser().resolve()/presentation.snapshot.session_id/(
            presentation.snapshot.result_id+'-a'+str(presentation.snapshot.annotation_revision)+'-'+request)
        self.pending[request]=presentation.snapshot
        job=_ExportJob(request,presentation.snapshot,str(target))
        job.delivery.completed.connect(self.accept_export,Qt.ConnectionType.QueuedConnection)
        self.status.setText('Exporting captured snapshot in the background…')
        export_pool().start(job)
        return True

    def accept_export(self,request,paths,error):
        snapshot=self.pending.pop(request,None)
        if snapshot is None or self.host._closing or not snapshot_is_current(self.host.session,snapshot):return False
        if error:
            self.status.setText('Export failed: '+str(error));self.saved_paths={};return False
        self.saved_paths=paths
        self.status.setText('Export saved · Annotation revision '+str(snapshot.annotation_revision)+' · '+str(paths['current_report']))
        return True

    def open_context(self,destination):
        if self.snapshot:self.route(destination,identity(self.snapshot),annotation_revision=self.snapshot.annotation_revision)
