"""Small reusable Qt widgets, independent of detector and session internals."""
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImageReader, QPainter, QPalette
from PyQt6.QtWidgets import (QFrame, QWidget, QLabel, QPushButton, QToolButton,
                            QVBoxLayout, QHBoxLayout, QSizePolicy, QScrollArea)
from gui_design_system import (COLORS, GEOMETRY, SPACE, font,
                               LIFECYCLE_LABELS, lifecycle_color, indicator_style)


def label(text='', role='body', *, bold=False):
    widget = QLabel(text)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setWordWrap(True)
    widget.setFont(font(role, bold=bold))
    widget.setProperty('slRole', role)
    widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    widget.setMinimumWidth(0)
    return widget


def scroll_area(content):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    content.setObjectName('workspaceScrollContent')
    scroll.viewport().setObjectName('workspaceScrollViewport')
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return scroll


class SectionHeader(QWidget):
    def __init__(self, heading, description='', actions=(), status=None):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, SPACE[2])
        copy = QVBoxLayout()
        self.heading = label(heading, 'section', bold=True)
        self.description = label(description, 'secondary')
        copy.addWidget(self.heading)
        copy.addWidget(self.description)
        row.addLayout(copy, 1)
        self.status = label(status or '', 'caption')
        self.status.setVisible(status is not None)
        row.addWidget(self.status)
        for action in actions:
            row.addWidget(action)


class Panel(QFrame):
    def __init__(self, title=None, toolbar=()):
        super().__init__()
        self.setProperty('slPanel', True)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(*([GEOMETRY.panel_padding]*4))
        self.body.setSpacing(SPACE[2])
        if title:
            heading = QHBoxLayout()
            heading.addWidget(label(title, 'card', bold=True), 1)
            for button in toolbar:
                heading.addWidget(button)
            self.body.addLayout(heading)


class StatusIndicator(QLabel):
    """Execution lifecycle, deliberately separate from forensic confidence."""
    def __init__(self, state='unknown', *, colors=COLORS):
        super().__init__()
        self.colors = colors
        self.setFont(font('caption', bold=True))
        self.set_state(state)

    def set_state(self, state):
        self.state = state
        self.setText(LIFECYCLE_LABELS.get(state, 'Unknown'))
        self.setAccessibleName('Investigation status: ' + self.text())
        self.setStyleSheet(indicator_style(lifecycle_color(state, self.colors), self.colors))


class ConfidenceIndicator(QLabel):
    def __init__(self, tier=None, *, colors=COLORS):
        super().__init__()
        self.colors = colors
        self.setFont(font('caption', bold=True))
        self.set_tier(tier)

    def set_tier(self, tier):
        self.tier = tier
        self.setText('Confidence · ' + (tier if isinstance(tier, str) and tier else 'Unavailable'))
        self.setAccessibleName(self.text())
        self.setToolTip('Authoritative support tier for this hypothesis. Not a probability of authenticity.')
        # Identical neutral treatment for all tiers; no suspicious/benign colors.
        self.setStyleSheet(indicator_style(self.colors.text, self.colors))


class EmptyState(QFrame):
    def __init__(self, heading='No image loaded', description='Choose an image to begin a local investigation.'):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([SPACE[3]]*4))
        self.heading = label(heading, 'card', bold=True)
        self.description = label(description, 'secondary')
        layout.addWidget(self.heading)
        layout.addWidget(self.description)

    def set_message(self, heading, description):
        self.heading.setText(heading)
        self.description.setText(description)


class NavigationItem(QPushButton):
    def __init__(self, title, icon=None, marker=None):
        super().__init__(title)
        self.title = title
        self.setProperty('slNavigation', True)
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(title + ' workspace')
        self.setMinimumHeight(GEOMETRY.control_height)
        self.setIconSize(QSize(GEOMETRY.icon_size, GEOMETRY.icon_size))
        if icon:
            self.setIcon(icon)
        self.set_marker(marker)

    def set_marker(self, marker):
        self.setText(self.title + (f' · {marker}' if marker else ''))
        self.setAccessibleName(self.title + ' workspace' + (f', {marker}' if marker else ''))


class MetadataRow(QWidget):
    def __init__(self, name, value='Not recorded'):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACE[2])
        row.addWidget(label(name, 'secondary'), 1)
        self.value = label(value, 'technical')
        self.value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse
                                           | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.value.setAccessibleName(name)
        row.addWidget(self.value, 2)

    def set_value(self, value):
        self.value.setText(str(value) if value is not None else 'Not recorded')


class CollapsibleSection(QWidget):
    def __init__(self, title, content, *, expanded=False):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE[1])
        self.toggle = QToolButton()
        self.toggle.setText(title)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setCheckable(True)
        self.toggle.setChecked(expanded)
        self.content = content
        layout.addWidget(self.toggle)
        layout.addWidget(content)
        self.toggle.toggled.connect(self.set_expanded)
        self.set_expanded(expanded)

    def set_expanded(self, expanded):
        self.toggle.setChecked(expanded)
        self.toggle.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.content.setVisible(expanded)


class SourcePreview(QLabel):
    """Bounded fit-only thumbnail; no overlays, pan or detector comparison."""
    def __init__(self):
        super().__init__('No source image loaded')
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(GEOMETRY.preview_height)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._image = QPixmap()
        self._source = None
        self.setAccessibleName('Source image preview')

    def set_source(self, path, identity):
        key = (identity, str(path))
        if self._source == key:
            return
        self._source = key
        self._image = QPixmap()
        self.clear()
        if path:
            reader = QImageReader(str(path))
            reader.setAutoTransform(True)
            size = reader.size()
            if size.isValid():
                reader.setScaledSize(size.scaled(QSize(2048, 2048), Qt.AspectRatioMode.KeepAspectRatio))
            self._image = QPixmap.fromImage(reader.read())
        if self._image.isNull():
            self.setText('Source preview unavailable' if path else 'No source image loaded')
        else:
            self._fit()

    def _fit(self):
        if not self._image.isNull():
            self.setPixmap(self._image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()


class StatusMessage(QLabel):
    """One-line status with explicit ellipsis and full copy in its tooltip.

    text() retains the exact UI-1 message for accessibility and lifecycle tests.
    """
    def __init__(self, text='Ready.'):
        super().__init__(text)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(0)
        self.setFixedHeight(GEOMETRY.control_height)
        self.setText(text)

    def setText(self, text):
        super().setText(text)
        self.setToolTip(text)
        self.setAccessibleName(text)

    def minimumSizeHint(self):
        return QSize(0, GEOMETRY.control_height)

    def sizeHint(self):
        return QSize(400, GEOMETRY.control_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.palette().color(QPalette.ColorRole.WindowText))
        text = self.fontMetrics().elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
