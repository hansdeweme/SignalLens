"""Bounded display preview, independent of forensic pixels and analysis workers.

Workers hold values only, never widgets. Delivery is queued to the receiver's Qt
thread and guarded by a monotonic request plus session/invocation identity.
"""
from dataclasses import dataclass
import hashlib
from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Qt, QSize, pyqtSignal
from PyQt6.QtGui import QImage, QImageReader, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QGraphicsView, QGraphicsScene, QSizePolicy)
from gui_components import label
from gui_design_system import SPACE, COLORS

_pool = None


def preview_pool():
    global _pool
    if _pool is None:
        _pool = QThreadPool()
        _pool.setMaxThreadCount(2)
    return _pool


def fingerprint(path):
    stat = Path(path).stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


@dataclass(frozen=True)
class PreviewResult:
    request: tuple
    image: QImage
    dimensions: tuple[int, int] | None
    stamp: tuple | None
    message: str


def read_preview(request, path, expected_sha):
    """Header + streamed hash + bounded decode. No QPixmap outside GUI thread."""
    try:
        before = fingerprint(path)
        digest = hashlib.sha256()
        with open(path, 'rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        if expected_sha and digest.hexdigest() != expected_sha:
            raise ValueError('Source changed since selection or analysis. Reselect the image; recorded findings remain historical.')
        reader = QImageReader(str(path))
        reader.setAutoTransform(True)
        size = reader.size()
        if size.width() * size.height() > 100_000_000:
            raise ValueError('Source exceeds the 100 megapixel preview limit. Analysis results remain available.')
        if max(size.width(), size.height()) > 2048:
            reader.setScaledSize(size.scaled(QSize(2048, 2048), Qt.AspectRatioMode.KeepAspectRatio))
        image = reader.read()
        if image.isNull():
            raise ValueError('Preview unavailable: ' + reader.errorString())
        if fingerprint(path) != before:
            raise ValueError('Source changed during preview loading. Reselect the image.')
        # Header dimensions are the encoded source dimensions, before EXIF orientation.
        return PreviewResult(request, image, (size.width(), size.height()), before, '')
    except (OSError, ValueError) as error:
        return PreviewResult(request, QImage(), None, None,
            'Source image unavailable. Locate or reselect the original image.' if isinstance(error, OSError) else str(error))


class _Delivery(QObject):
    completed = pyqtSignal(object)


class _Load(QRunnable):
    def __init__(self, request, path, digest):
        super().__init__()
        self.request, self.path, self.digest = request, path, digest
        self.delivery = _Delivery()

    def run(self):
        self.delivery.completed.emit(read_preview(self.request, self.path, self.digest))


class _Canvas(QGraphicsView):
    resized = pyqtSignal()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()


class SourceImageViewer(QWidget):
    information_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QPixmap()
        self._serial = 0
        self._request = None
        self._path = None
        self._digest = None
        self._stamp = None
        self.dimensions = None
        self.fit_mode = True
        self.zoom_factor = 1.0
        body = QVBoxLayout(self)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(SPACE[1])
        self.canvas = _Canvas()
        self.canvas.setScene(QGraphicsScene(self.canvas))
        self.canvas.setBackgroundBrush(QColor(COLORS.background))
        self.canvas.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.canvas.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.canvas.setMinimumSize(180, 220)
        self.canvas.setAccessibleName('Source image preview; drag to pan when zoomed')
        self.canvas.resized.connect(self._refit)
        body.addWidget(self.canvas, 1)
        self.message = label('Choose an image to begin.', 'caption')
        body.addWidget(self.message)
        tools = QHBoxLayout()
        self.zoom_out = QPushButton('−')
        self.zoom_in = QPushButton('+')
        self.fit_button = QPushButton('Fit / Reset')
        self.zoom_out.setAccessibleName('Zoom out source preview')
        self.zoom_in.setAccessibleName('Zoom in source preview')
        self.zoom_out.clicked.connect(lambda: self.zoom(1 / 1.25))
        self.zoom_in.clicked.connect(lambda: self.zoom(1.25))
        self.fit_button.clicked.connect(self.fit)
        for item in (self.zoom_out, self.zoom_in, self.fit_button):
            tools.addWidget(item)
        self.scale_label = label('Fit', 'caption')
        tools.addWidget(self.scale_label)
        tools.addStretch()
        body.addLayout(tools)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._enable(False)
        self.monitor = QTimer(self)
        self.monitor.setInterval(2000)
        self.monitor.timeout.connect(self.check_source)
        self.monitor.start()

    def _enable(self, enabled):
        for item in (self.zoom_out, self.zoom_in, self.fit_button):
            item.setEnabled(enabled)
            item.setToolTip('Bounded preview only; zoom does not load full-resolution forensic pixels.' if enabled else 'A valid source preview is required.')

    def _clear(self, message):
        self._image = QPixmap()
        self.canvas.scene().clear()
        self.dimensions = None
        self._stamp = None
        self._enable(False)
        self.message.setText(message)
        self.information_changed.emit(message)

    def set_source(self, path, identity, expected_sha=None):
        path = str(path) if path else None
        key = (path, tuple(identity), expected_sha)
        if self._request and self._request[1:] == key:
            self.check_source()
            return
        # Reuse only a verified unchanged preview of exactly the same source.
        reusable = path == self._path and expected_sha == self._digest and not self._image.isNull()
        try:
            reusable = reusable and fingerprint(path) == self._stamp
        except OSError:
            reusable = False
        self._serial += 1
        self._request = (self._serial, *key)
        self._path, self._digest = path, expected_sha
        if reusable:
            return
        self._clear('Loading source preview…' if path else 'Choose an image to begin.')
        if not path:
            return
        # Tiny fixtures/icons are bounded and cheaper than a thread dispatch.
        # Real photographs and any expensive hash/decode use the worker pool.
        reader = QImageReader(path)
        size = reader.size()
        try:
            tiny = fingerprint(path)[0] <= 262144 and 0 < size.width() * size.height() <= 262144
        except OSError:
            tiny = False
        if tiny:
            self.accept_preview(read_preview(self._request, path, expected_sha))
        else:
            job = _Load(self._request, path, expected_sha)
            job.delivery.completed.connect(self.accept_preview, Qt.ConnectionType.QueuedConnection)
            preview_pool().start(job)

    def accept_preview(self, result):
        if result.request != self._request:
            return False
        if result.image.isNull():
            self._clear(result.message)
            return True
        try:
            current = fingerprint(self._path) == result.stamp
        except OSError:
            current = False
        if not current:
            self._clear('Source missing or changed before preview delivery. Reselect the original image.')
            return True
        self._image = QPixmap.fromImage(result.image)
        self.dimensions, self._stamp = result.dimensions, result.stamp
        self.canvas.scene().clear()
        self.canvas.scene().addPixmap(self._image)
        self.canvas.scene().setSceneRect(0, 0, self._image.width(), self._image.height())
        self._enable(True)
        self.fit()
        text = f'{self.dimensions[0]} × {self.dimensions[1]} encoded pixels · bounded preview'
        if not self._digest:
            text += ' · historical source identity unrecorded'
        self.message.setText(text)
        self.information_changed.emit(text)
        return True

    def check_source(self):
        if not self._path or self._stamp is None:
            return
        try:
            unchanged = fingerprint(self._path) == self._stamp
        except OSError:
            unchanged = False
        if not unchanged:
            self._clear('Source missing or changed. Reselect the original image; findings refer to the recorded source.')

    def fit(self):
        self.fit_mode = True
        self.zoom_factor = 1.0
        self._refit()

    def _refit(self):
        if self.fit_mode and not self._image.isNull():
            self.canvas.fitInView(self.canvas.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.scale_label.setText('Fit')

    def zoom(self, factor):
        if self._image.isNull():
            return
        new = max(0.25, min(8.0, self.zoom_factor * factor))
        self.canvas.scale(new / self.zoom_factor, new / self.zoom_factor)
        self.zoom_factor, self.fit_mode = new, False
        self.scale_label.setText(f'{new:.2g}× fit')
