"""Investigation-bound artifact inspection, built on UI-3's async loader."""
from dataclasses import asdict
import json
from pathlib import Path
from PyQt6.QtCore import Qt, QObject, QRunnable, pyqtSignal
from PyQt6.QtGui import QTransform, QPen, QColor
from PyQt6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QSplitter,QTreeWidget,QTreeWidgetItem,
    QComboBox,QSlider,QPushButton,QPlainTextEdit,QDialog,QDialogButtonBox)
from gui_components import label, Panel
from gui_design_system import SPACE,COLORS,apply_theme
from artifact_presenter import discovery_context,discover_artifacts
from source_image_viewer import preview_pool
from forensic_image_viewer import ForensicImageViewer


class _CatalogDelivery(QObject):
    completed = pyqtSignal(object,object)


class _CatalogJob(QRunnable):
    def __init__(self, key, context, snapshot):
        super().__init__()
        self.key,self.context,self.snapshot = key,context,snapshot
        self.delivery = _CatalogDelivery()

    def run(self):
        try:
            result = discover_artifacts(self.context,self.snapshot)
        except Exception as error:
            result = str(error)
        self.delivery.completed.emit(self.key,result)


class ImageForensicsWorkspace(QWidget):
    def __init__(self, host, navigate):
        super().__init__()
        self.host,self.navigate = host,navigate
        self.key = None
        self.artifacts = ()
        self.selected = None
        self._linking = False
        self._overlay_items = []
        self._catalog_context = None
        body = QVBoxLayout(self)
        body.setContentsMargins(SPACE[3],SPACE[1],0,0)
        body.setSpacing(SPACE[1])
        body.addWidget(label('Image Forensics', 'section', bold=True))
        self.identity = label('Select an image and complete analysis to inspect recorded outputs.','caption')
        body.addWidget(self.identity)
        commands = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItems(('Independent','Synchronized','Overlay'))
        self.mode.setMinimumContentsLength(12)
        self.mode.setAccessibleName('Forensic comparison mode')
        self.mode.currentIndexChanged.connect(self.set_mode)
        commands.addWidget(self.mode)
        commands.addWidget(label('Opacity','caption'))
        self.opacity = QSlider(Qt.Orientation.Horizontal)
        self.opacity.setRange(0,100)
        self.opacity.setValue(50)
        self.opacity.setMaximumWidth(96)
        self.opacity.setAccessibleName('Registered artifact overlay opacity')
        self.opacity.valueChanged.connect(self.set_opacity)
        commands.addWidget(self.opacity)
        self.artifact_button = QPushButton('Artifact folder')
        self.artifact_button.clicked.connect(self.open_folder)
        commands.addWidget(self.artifact_button)
        for destination in ('Evidence','Reasoning','Provenance'):
            button = QPushButton(destination)
            button.clicked.connect(lambda checked=False,name=destination:navigate(name))
            commands.addWidget(button)
        body.addLayout(commands)
        self.vertical = QSplitter(Qt.Orientation.Vertical)
        self.vertical.setChildrenCollapsible(False)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setMinimumWidth(140)
        self.tree.setMaximumWidth(360)
        self.tree.setAccessibleName('Detectors and recorded forensic artifacts')
        self.tree.currentItemChanged.connect(self.select_item)
        self.splitter.addWidget(self.tree)
        self.view_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.view_splitter.setChildrenCollapsible(False)
        source = Panel('Source image')
        source.body.setContentsMargins(*([SPACE[1]]*4))
        self.source = ForensicImageViewer('Source image')
        source.body.addWidget(self.source,1)
        artifact = Panel('Selected detector artifact')
        artifact.body.setContentsMargins(*([SPACE[1]]*4))
        self.artifact = ForensicImageViewer('Detector artifact')
        artifact.body.addWidget(self.artifact,1)
        self.view_splitter.addWidget(source)
        self.view_splitter.addWidget(artifact)
        self.view_splitter.setSizes([400,400])
        self.splitter.addWidget(self.view_splitter)
        self.splitter.setSizes([190,800])
        self.splitter.setStretchFactor(1,1)
        self.vertical.addWidget(self.splitter)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setMinimumHeight(72)
        self.details.setAccessibleName('Artifact identity, reliability, registration and evidence context')
        self.vertical.addWidget(self.details)
        self.vertical.setSizes([500,170])
        body.addWidget(self.vertical,1)
        self.stage_details = QPlainTextEdit(self)
        self.stage_details.hide()  # Existing compatibility slot; full stages available in Details.
        all_details = QPushButton('Full artifact metadata and stage availability')
        all_details.clicked.connect(self.show_details)
        body.addWidget(all_details)
        self.source.image_changed.connect(self.refresh_modes)
        self.source.image_about_to_change.connect(self.remove_overlay)
        self.artifact.image_changed.connect(self.refresh_modes)
        self.source.view_changed.connect(lambda:self.link_view(self.source,self.artifact))
        self.artifact.view_changed.connect(lambda:self.link_view(self.artifact,self.source))
        self.refresh_modes()

    def open_folder(self):
        self.host.workspace.open_artifacts()

    def bind(self, snapshot):
        self.snapshot = snapshot
        complete = snapshot.summary.status == 'completed' and snapshot.result_id
        key = (snapshot.session_id,snapshot.analysis_id,snapshot.result_id,snapshot.analysis_revision,snapshot.summary.status)
        source = snapshot.source
        self.source.set_source(source.path if source else None,key,source.sha256 if source else None)
        self.identity.setText(f'{snapshot.summary.image_name or "No image selected"} · {snapshot.summary.status} · Result {snapshot.result_id or "unavailable"}')
        if key == self.key:
            return
        self.key = key
        self.artifacts = ()
        self.selected = None
        self._catalog_context = None
        self.tree.clear()
        self.artifact.set_source(None,key)
        self.remove_overlay()
        self.mode.setCurrentIndex(0)
        self.details.setPlainText('Loading investigation-bound artifact catalog…' if complete else 'No completed result. Missing measurements imply no forensic conclusion.')
        self.refresh_modes()
        if complete:
            self._catalog_context = discovery_context(self.host.session,snapshot,self.host.analysis_state)
            # Detach all worker inputs from mutable raw state and session.
            context = json.loads(json.dumps(self._catalog_context,default=str))
            job = _CatalogJob(key,context,snapshot)
            job.delivery.completed.connect(self.accept_catalog,Qt.ConnectionType.QueuedConnection)
            preview_pool().start(job)

    def accept_catalog(self,key,result):
        session = self.host.session
        current = (session.session_id,session.invocation.analysis_id if session.invocation else None,
                   session.result_id,session.analysis_revision,session.state.value)
        if key != self.key or key != current or self.host._closing:
            return False
        if isinstance(result,str):
            self.details.setPlainText('Artifact catalog unavailable: '+result)
            return False
        self.artifacts = result
        groups = {}
        first = None
        for artifact in result:
            if artifact.detector_id not in groups:
                group = QTreeWidgetItem(self.tree,[artifact.detector_id.replace('_',' ').title()])
                group.setExpanded(True)
                groups[artifact.detector_id] = group
            status = 'available' if artifact.available else 'unavailable'
            item = QTreeWidgetItem(groups[artifact.detector_id],[f'{artifact.label}\n{artifact.artifact_type} · {status} · {artifact.registration.value}'])
            item.setData(0,Qt.ItemDataRole.UserRole,artifact)
            item.setToolTip(0,f'{artifact.artifact_id}\nReliability: {artifact.reliability or "Not recorded"}\n{artifact.reason or artifact.description}')
            if first is None and artifact.available and artifact.path:
                first = item
        if first:
            self.tree.setCurrentItem(first)
        elif result:
            self.tree.setCurrentItem(self.tree.topLevelItem(0).child(0))
        self.persist_catalog()
        return True

    def persist_catalog(self):
        context = self._catalog_context
        if not context or not context['live'] or not context['root']:
            return
        path = Path(context['root'])/'ui_artifacts_v1.json'
        data = {'schema_version':1,'result_id':context['result_id'],'source_sha256':context['source_sha256'],
                'payloads':context['payloads'],'artifacts':[asdict(a) for a in self.artifacts]}
        try:
            with path.open('x',encoding='utf-8') as stream:
                json.dump(data,stream,ensure_ascii=False,default=str)
        except FileExistsError:
            pass
        except OSError as error:
            self.details.appendPlainText('\nArtifact catalog could not be persisted: '+str(error))

    def select_item(self,item,previous=None):
        artifact = item.data(0,Qt.ItemDataRole.UserRole) if item else None
        if artifact is None:
            self.mode.setCurrentIndex(0)
            self.remove_overlay()
            self.selected = None
            self.artifact.set_source(None,self.key or ())
            self.refresh_modes()
            return
        self.mode.setCurrentIndex(0)
        self.remove_overlay()
        self.selected = artifact
        self.artifact.expected_dimensions = (artifact.width,artifact.height) if artifact.width else None
        self.artifact.registration_transform = None
        identity = (*self.key,artifact.artifact_id,artifact.sha256)
        self.artifact.set_source(artifact.path if artifact.available else None,identity,artifact.sha256)
        if not artifact.path or not artifact.available:
            self.artifact._clear(artifact.reason or 'Structured evidence only; no image visualization recorded.')
        self.details.setPlainText(f'{artifact.detector_id} · {artifact.label}\n'
            f'Reliability: {artifact.reliability or "Not recorded"} · Registration: {artifact.registration.value} · Stage: {artifact.stage_status or "Not recorded"}\n'
            f'{artifact.description}\n{artifact.reason or ""}\n'
            f'Evidence: {", ".join(artifact.evidence_ids) or "No structured evidence linkage recorded"}\n'
            f'Hypotheses: {", ".join(artifact.hypothesis_ids) or "Not recorded"}')
        self.refresh_modes()

    def refresh_modes(self):
        ready = (self.selected and not self.source._image.isNull() and not self.artifact._image.isNull())
        sync = bool(ready and self.selected.can_sync)
        overlay = bool(ready and self.selected.can_overlay)
        self.mode.model().item(1).setEnabled(sync)
        self.mode.model().item(2).setEnabled(overlay)
        self.mode.setToolTip('Linked modes require verified geometry, matching content and a valid source preview. FFT/unknown/rejected outputs remain independent.')
        if self.mode.currentIndex() and not sync:
            self.mode.setCurrentIndex(0)
        self.opacity.setEnabled(overlay and self.mode.currentIndex()==2)
        self.opacity.setToolTip('Linear blend of the recorded visualization; not an authenticity probability.')

    def remove_overlay(self):
        scene = self.source.canvas.scene()
        for item in self._overlay_items:
            # Source reload may already have deleted the underlying Qt items.
            try:
                if item.scene() is scene:
                    scene.removeItem(item)
            except RuntimeError:
                pass
        self._overlay_items = []

    def set_mode(self,index):
        self.remove_overlay()
        eligible = self.selected and self.selected.can_sync and not self.source._image.isNull() and not self.artifact._image.isNull()
        if index and (not eligible or index==2 and not self.selected.can_overlay):
            self.mode.setCurrentIndex(0)
            return
        self._linking = True
        try:
            self.artifact.configure_grid(self.selected.transform if index and self.selected else None)
        finally:
            self._linking = False
        if index:
            self.link_view(self.source,self.artifact)
        if index == 2:
            t = self.selected.transform.inverse()
            item = self.source.canvas.scene().addPixmap(self.artifact._image)
            item.setTransform(QTransform.fromScale(self.selected.width/self.artifact._image.width(),self.selected.height/self.artifact._image.height()) * QTransform(t.a,t.b,t.c,t.d,t.tx,t.ty))
            item.setOpacity(self.opacity.value()/100)
            item.setZValue(1)
            rect = item.mapRectToScene(item.boundingRect())
            border = self.source.canvas.scene().addRect(rect,QPen(QColor(COLORS.accent),1,Qt.PenStyle.DashLine))
            border.setZValue(2)
            self._overlay_items = [item,border]
            self.details.appendPlainText('\nOverlay legend: '+self.selected.overlay_legend+'; dashed outline = registered extent. Opacity is a display blend, not confidence.')
        self.refresh_modes()

    def set_opacity(self,value):
        if self._overlay_items:
            self._overlay_items[0].setOpacity(value/100)

    def link_view(self,origin,target):
        if self._linking or not self.mode.currentIndex() or not self.selected or not self.selected.can_sync:
            return
        self._linking = True
        try:
            target.set_view(origin.point_at_center(),origin.canvas.transform())
        finally:
            self._linking = False

    def show_details(self):
        dialog = QDialog(self.host)
        dialog.setWindowTitle('Artifact metadata and stage availability')
        dialog.resize(800,600)
        layout = QVBoxLayout(dialog)
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText((json.dumps(asdict(self.selected),indent=2,default=str) if self.selected else 'No artifact selected')+'\n\n'+self.stage_details.toPlainText())
        layout.addWidget(text)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        apply_theme(dialog)
        dialog.exec()
