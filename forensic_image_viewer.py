"""UI-3 loader reused with native pixel coordinates for registered comparison."""
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QTransform
from source_image_viewer import SourceImageViewer


class ForensicImageViewer(SourceImageViewer):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.expected_dimensions = None
        self.registration_transform = None
        self.display_dimensions = None
        # Separate scale information from controls at narrow comparison widths.
        self.layout().itemAt(self.layout().count()-1).layout().removeWidget(self.scale_label)
        self.layout().addWidget(self.scale_label)
        self.scale_label.setWordWrap(False)
        self.canvas.setMinimumSize(120, 140)
        self.canvas.setAccessibleName(name+'; image coordinates, drag to pan')
        for button, action in ((self.zoom_in,'Zoom in'),(self.zoom_out,'Zoom out'),(self.fit_button,'Fit / reset')):
            button.setAccessibleName(action+' '+name)

    def accept_preview(self, result):
        if result.request != self._request:
            return False
        if self.expected_dimensions and not result.image.isNull() and result.dimensions != self.expected_dimensions:
            self._clear('Artifact dimensions differ from the recorded catalog. Reload the investigation.')
            return True
        self.display_dimensions = result.display_dimensions or result.dimensions
        accepted = super().accept_preview(result)
        if accepted and not self._image.isNull():
            self.configure_grid(self.registration_transform)
            self.image_changed.emit()
        return accepted

    def configure_grid(self, source_to_artifact=None):
        self.registration_transform = source_to_artifact
        if self._image.isNull() or not self.dimensions:
            return
        item = next((i for i in self.canvas.scene().items() if hasattr(i,'pixmap')), None)
        if item is None:
            return
        w,h = self.display_dimensions or self.dimensions
        grid = QTransform.fromScale(w/self._image.width(), h/self._image.height())
        if source_to_artifact:
            t = source_to_artifact.inverse()
            grid = grid * QTransform(t.a,t.b,t.c,t.d,t.tx,t.ty)
        item.setTransform(grid)
        self.canvas.scene().setSceneRect(item.mapRectToScene(item.boundingRect()))
        self.fit()

    def point_at_center(self):
        point = self.canvas.mapToScene(self.canvas.viewport().rect().center())
        return point.x(),point.y()

    def set_view(self, center, transform):
        self.fit_mode = False
        self.canvas.setTransform(QTransform(transform))
        self.canvas.centerOn(QPointF(*center))
        self.scale_label.setText(f'{abs(transform.m11()):.3g} display px / image unit')

    def _refit(self):
        super()._refit()
        if hasattr(self,'name') and not self._image.isNull():
            self.scale_label.setText(f'{abs(self.canvas.transform().m11()):.3g} display px / image unit')

    def zoom(self, factor):
        super().zoom(factor)
        if not self._image.isNull():
            self.scale_label.setText(f'{abs(self.canvas.transform().m11()):.3g} display px / image unit')
