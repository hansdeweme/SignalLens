"""Source-image review inside OSINT, using the existing owned Qt workers."""
from dataclasses import asdict
import io
import json
from pathlib import Path
import threading
from types import SimpleNamespace
from uuid import uuid4

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QPlainTextEdit
from investigation_workers import InvestigationWorkers
from source_image_verification import retrieve, decode


def preview(data):
    im = decode(data)
    im.thumbnail((360, 280))
    stream = io.BytesIO()
    im.save(stream, format='PNG')
    return stream.getvalue()


class VerificationWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    log = pyqtSignal(str, str)

    def __init__(self, path, sha, match, cancelled):
        super().__init__()
        self.path, self.sha, self.match, self.cancelled = path, sha, match, cancelled

    def run(self):
        try:
            results = retrieve(self.path, self.sha, self.match, self.cancelled, self.status.emit)
            local_preview = preview(Path(self.path).read_bytes())
            candidates = [(record, data, preview(data) if data else None) for record, data in results]
            self.finished.emit((local_preview, candidates))
        except Exception as exc:
            self.error.emit(str(exc))


class SourceVerificationDialog(QDialog):
    def __init__(self, parent, path, sha, match):
        super().__init__(parent)
        self.setWindowTitle('Verify source image')
        self.resize(820, 680)
        self.cancelled = threading.Event()
        self.closing = False
        self.results = []
        self.selected_result = None
        self.match = match
        self.workers = InvestigationWorkers(self)
        self.workers.completed.connect(self.completed)
        self.workers.failed.connect(self.failed)
        self.workers.status_changed.connect(lambda _, text: self.status.setText(text))
        self.workers.idle.connect(self.idle)
        layout = QVBoxLayout(self)
        self.status = QLabel('Retrieving source image; cancellation discards this attempt.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.candidates = QListWidget()
        self.candidates.currentRowChanged.connect(self.select)
        layout.addWidget(self.candidates)
        images = QHBoxLayout()
        self.local, self.remote = QLabel('Local image'), QLabel('Source image')
        for label in (self.local, self.remote):
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            images.addWidget(label)
        layout.addLayout(images)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        layout.addWidget(self.details, 1)
        actions = QHBoxLayout()
        self.save = QPushButton('Accept selected verification')
        self.save.setEnabled(False)
        self.save.clicked.connect(self.accept_selected)
        self.cancel = QPushButton('Cancel')
        self.cancel.clicked.connect(self.reject)
        actions.addWidget(self.save)
        actions.addWidget(self.cancel)
        layout.addLayout(actions)
        invocation = SimpleNamespace(analysis_id=uuid4().hex)
        self.workers.start(invocation, VerificationWorker(path, sha, asdict(match), self.cancelled))

    def completed(self, invocation, result):
        if self.closing:
            return
        local, self.results = result
        pixmap = QPixmap()
        pixmap.loadFromData(local)
        self.local.setPixmap(pixmap)
        for record, data, thumbnail in self.results:
            self.candidates.addItem(f"{record['association']} / {record['status']} — {record['requested_url']}")
        verified = [i for i, (r, _, _) in enumerate(self.results) if r['association'] in {'byte_identical', 'visually_verified'}]
        self.status.setText('Review the compared images, method and limitations before accepting. '
                           + ('Multiple verified assets: choose the intended source.' if len(verified) > 1 else
                              'Unresolved candidates remain manual associations.'))
        self.candidates.setCurrentRow(verified[0] if len(verified) == 1 else (0 if self.results else -1))

    def failed(self, invocation, message):
        self.status.setText('Verification unavailable: ' + message)

    def select(self, row):
        self.remote.clear()
        if not 0 <= row < len(self.results):
            self.save.setEnabled(False)
            return
        record, data, thumbnail = self.results[row]
        self.details.setPlainText(json.dumps({k: v for k, v in record.items() if not k.startswith('_')}, indent=2))
        if thumbnail:
            pixmap = QPixmap()
            pixmap.loadFromData(thumbnail)
            self.remote.setPixmap(pixmap)
        self.save.setText('Record analyst association' if record['association'] == 'ambiguous' else 'Accept selected verification')
        self.save.setEnabled(not self.workers.busy and data is not None and self.match.image_association != 'rejected')
        if self.match.image_association == 'rejected':
            self.status.setText('This source was explicitly rejected. Edit its association before accepting a new verification.')

    def idle(self):
        if self.closing:
            super().reject()
        else:
            self.select(self.candidates.currentRow())

    def accept_selected(self):
        row = self.candidates.currentRow()
        if self.save.isEnabled() and 0 <= row < len(self.results):
            self.selected_result = self.results[row][:2]
            super().accept()

    def reject(self):
        self.cancelled.set()
        if self.workers.busy:
            self.closing = True
            self.save.setEnabled(False)
            self.status.setText('Cancelling; waiting for bounded retrieval cleanup…')
        else:
            super().reject()

    def closeEvent(self, event):
        self.reject()
        if self.workers.busy:
            event.ignore()
        else:
            event.accept()
