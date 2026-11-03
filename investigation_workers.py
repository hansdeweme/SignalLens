"""Qt worker ownership with identity-carrying, GUI-thread delivery.

No worker is physically cancelled. Handles survive logical supersession and are
retired only on QThread.finished. Do not destroy this owner while busy.
"""
from PyQt6.QtCore import QObject, QThread, Qt, pyqtSignal, pyqtSlot
from analysis_worker import AnalysisWorker


class InvocationWorker(QObject):
    completed = pyqtSignal(object, object)
    failed = pyqtSignal(object, str)
    status_changed = pyqtSignal(object, str)
    logged = pyqtSignal(object, str, str)
    retired = pyqtSignal(object)

    def __init__(self, invocation, worker, parent):
        super().__init__(parent)
        self.invocation = invocation
        self.worker = worker
        self.thread = QThread(self)
        worker.moveToThread(self.thread)
        self.thread.started.connect(worker.run)
        worker.finished.connect(self._complete, Qt.ConnectionType.QueuedConnection)
        worker.error.connect(self._fail, Qt.ConnectionType.QueuedConnection)
        worker.status.connect(self._status, Qt.ConnectionType.QueuedConnection)
        worker.log.connect(self._log, Qt.ConnectionType.QueuedConnection)
        # quit is thread-safe; the worker is deleted in its own thread on exit.
        worker.finished.connect(self.thread.quit, Qt.ConnectionType.DirectConnection)
        worker.error.connect(self.thread.quit, Qt.ConnectionType.DirectConnection)
        self.thread.finished.connect(worker.deleteLater)
        self.thread.finished.connect(self._retire, Qt.ConnectionType.QueuedConnection)

    @pyqtSlot(object)
    def _complete(self, result):
        self.completed.emit(self.invocation, result)

    @pyqtSlot(str)
    def _fail(self, message):
        self.failed.emit(self.invocation, message)

    @pyqtSlot(str)
    def _status(self, message):
        self.status_changed.emit(self.invocation, message)

    @pyqtSlot(str, str)
    def _log(self, message, level):
        self.logged.emit(self.invocation, message, level)

    @pyqtSlot()
    def _retire(self):
        self.retired.emit(self.invocation)


class InvestigationWorkers(QObject):
    completed = pyqtSignal(object, object)
    failed = pyqtSignal(object, str)
    status_changed = pyqtSignal(object, str)
    logged = pyqtSignal(object, str, str)
    idle = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.handles = {}

    @property
    def busy(self):
        return bool(self.handles)

    def start(self, invocation, worker=None):
        if invocation.analysis_id in self.handles:
            raise ValueError('Invocation already has a worker.')
        if worker is None:
            import json
            from pathlib import Path
            output = Path(invocation.output_dir)
            worker = AnalysisWorker(Path(invocation.image_path), output,
                output / f'{Path(invocation.image_path).stem}_exif_signals.json', invocation.profile,
                settings_snapshot=json.loads(invocation.settings_json))
        handle = InvocationWorker(invocation, worker, self)
        self.handles[invocation.analysis_id] = handle
        handle.completed.connect(self.completed)
        handle.failed.connect(self.failed)
        handle.status_changed.connect(self.status_changed)
        handle.logged.connect(self.logged)
        handle.retired.connect(self._retire)
        try:
            handle.thread.start()
        except Exception:
            self.handles.pop(invocation.analysis_id)
            handle.deleteLater()
            raise
        return handle

    @pyqtSlot(object)
    def _retire(self, invocation):
        handle = self.handles.pop(invocation.analysis_id)
        handle.deleteLater()  # QThread has finished, never delete a live thread
        if not self.handles:
            self.idle.emit()
