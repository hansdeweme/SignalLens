"""SignalLens native-widget design tokens. No forensic outcome logic."""
from dataclasses import dataclass
import re

from PyQt6.QtGui import QColor, QFont, QPalette


@dataclass(frozen=True)
class ColorTokens:
    background: str = '#11161e'
    navigation: str = '#151c26'
    panel: str = '#1b2431'
    secondary_panel: str = '#202c3b'
    elevated: str = '#29384b'
    border: str = '#53647b'
    divider: str = '#344258'
    text: str = '#edf2f8'
    secondary_text: str = '#b9c6d8'
    disabled_text: str = '#8795a8'
    accent: str = '#8cccf2'
    hover: str = '#27394d'
    selected: str = '#233c53'
    focus: str = '#a3d9fa'
    success: str = '#9cdbb7'
    warning: str = '#f1ce82'
    error: str = '#f3abae'
    neutral: str = '#bfcbdd'
    unavailable: str = '#b7b3cf'


@dataclass(frozen=True)
class TypographyTokens:
    family: str = 'Segoe UI'
    monospace: str = 'Consolas'
    display: int = 20
    section: int = 15
    card: int = 11
    body: int = 10
    secondary: int = 10
    caption: int = 9
    technical: int = 9


@dataclass(frozen=True)
class GeometryTokens:
    radius: int = 6
    control_height: int = 32
    navigation_width: int = 208
    navigation_min: int = 184
    navigation_max: int = 280
    panel_padding: int = 16
    icon_size: int = 18
    border_width: int = 1
    minimum_width: int = 1040
    minimum_height: int = 720
    normal_width: int = 1280
    normal_height: int = 900
    preview_height: int = 160
    indicator_padding_y: int = 5
    indicator_padding_x: int = 10


COLORS = ColorTokens()
TYPE = TypographyTokens()
GEOMETRY = GeometryTokens()
SPACE = (4, 8, 12, 16, 24, 32)

# A second palette is injectable through the same rendering boundary. UI-2 ships
# dark-first; exposing/certifying a light-mode preference is separate work.
LIGHT = ColorTokens(background='#eef2f6', navigation='#e3eaf2', panel='#ffffff',
    secondary_panel='#f1f5fa', elevated='#e8eef6', border='#66758a', divider='#cad4e1',
    text='#172033', secondary_text='#49566b', disabled_text='#66758a', accent='#155b89',
    hover='#dbe7f4', selected='#d5e7f5', focus='#1d4ed8', success='#166534',
    warning='#854d0e', error='#991b1b', neutral='#49566b', unavailable='#655c7f')

LIFECYCLE_LABELS = {
    'empty': 'No image', 'image_selected': 'Image selected', 'pending': 'Pending',
    'analyzing': 'Analyzing', 'completed': 'Completed', 'failed': 'Failed',
    'cancelled': 'Cancelled', 'unavailable': 'Unavailable', 'unknown': 'Unknown',
}
CONFIDENCE_LABELS = ('High', 'Medium', 'Low', 'Inconclusive', 'Unavailable')


def lifecycle_color(state: str, colors=COLORS) -> str:
    return {'analyzing': colors.accent, 'completed': colors.success,
            'failed': colors.error, 'cancelled': colors.warning,
            'unavailable': colors.unavailable}.get(state, colors.neutral)


def log_color(level: str, colors=COLORS) -> str:
    return {'info': colors.secondary_text, 'success': colors.success,
            'warn': colors.warning, 'error': colors.error, 'finding': colors.accent}.get(level, colors.text)


def indicator_style(foreground, colors=COLORS):
    g = GEOMETRY
    return (f'color: {foreground}; padding: {g.indicator_padding_y}px {g.indicator_padding_x}px; '
            f'border: {g.border_width}px solid {colors.border}; border-radius: {g.radius}px;')


def font(role='body', *, bold=False) -> QFont:
    f = QFont(TYPE.monospace if role == 'technical' else TYPE.family, getattr(TYPE, role))
    f.setBold(bold)
    return f


def stylesheet(c=COLORS) -> str:
    g = GEOMETRY
    return f'''
    QWidget {{ color: {c.text}; font-family: "{TYPE.family}"; }}
    QLabel[slRole="display"] {{ font-size: {TYPE.display}pt; font-weight: 600; }}
    QLabel[slRole="section"] {{ font-size: {TYPE.section}pt; font-weight: 600; }}
    QLabel[slRole="card"] {{ font-size: {TYPE.card}pt; font-weight: 600; }}
    QLabel[slRole="caption"] {{ font-size: {TYPE.caption}pt; }}
    QLabel[slRole="technical"] {{ font-family: "{TYPE.monospace}"; font-size: {TYPE.technical}pt; }}
    QMainWindow, QDialog, QWidget#workspaceRoot {{ background: {c.background}; }}
    QFrame[slPanel="true"] {{ background: {c.panel}; border: {g.border_width}px solid {c.border}; border-radius: {g.radius}px; }}
    QFrame#workspaceNavigation {{ background: {c.navigation}; border: none; }}
    QLabel {{ background: transparent; border: none; }}
    QLabel[slRole="secondary"], QLabel[slRole="caption"] {{ color: {c.secondary_text}; }}
    QPushButton, QToolButton {{ background: {c.secondary_panel}; border: 1px solid {c.border}; border-radius: {g.radius}px; padding: 5px 12px; min-height: 20px; }}
    QPushButton:hover, QToolButton:hover {{ background: {c.hover}; }}
    QPushButton:pressed, QToolButton:pressed {{ background: {c.selected}; }}
    QPushButton:disabled, QToolButton:disabled {{ color: {c.disabled_text}; border-color: {c.divider}; }}
    QPushButton:focus, QToolButton:focus, QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QListWidget:focus {{ border: 2px solid {c.focus}; }}
    QPushButton[slPrimary="true"] {{ background: {c.selected}; color: {c.accent}; border-color: {c.accent}; font-weight: 600; }}
    QPushButton[slPrimary="true"]:disabled {{ background: {c.secondary_panel}; color: {c.disabled_text}; border-color: {c.divider}; }}
    QPushButton[slNavigation="true"] {{ text-align: left; border: 1px solid transparent; padding: 10px 12px; border-radius: {g.radius}px; }}
    QPushButton[slNavigation="true"]:checked {{ background: {c.selected}; color: {c.accent}; border-left: 3px solid {c.accent}; font-weight: 600; }}
    QPushButton[slNavigation="true"]:focus {{ border: 2px solid {c.focus}; }}
    QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser, QListWidget, QTreeWidget, QTableView, QSpinBox, QDoubleSpinBox, QComboBox {{ background: {c.background}; color: {c.text}; selection-background-color: {c.selected}; selection-color: {c.text}; border: 1px solid {c.border}; border-radius: 4px; padding: 5px; }}
    QTableView {{ gridline-color: {c.divider}; }}
    QHeaderView::section {{ background: {c.secondary_panel}; color: {c.text}; border: 1px solid {c.divider}; padding: 6px; }}
    QTableView:focus {{ border: 2px solid {c.focus}; }}
    QTreeWidget::item {{ padding: 5px 2px; }}
    QTreeWidget::item:selected {{ background: {c.selected}; color: {c.text}; }}
    QTreeWidget:focus {{ border: 2px solid {c.focus}; }}
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{ min-height: 22px; }}
    QComboBox QAbstractItemView {{ background: {c.panel}; color: {c.text}; selection-background-color: {c.selected}; }}
    QGroupBox {{ background: {c.panel}; border: 1px solid {c.border}; border-radius: {g.radius}px; margin-top: 12px; padding: 14px 10px 10px 10px; }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; color: {c.secondary_text}; }}
    QCheckBox {{ spacing: 8px; padding: 3px; }}
    QCheckBox:focus {{ outline: 2px solid {c.focus}; }}
    QTabWidget::pane {{ border: 1px solid {c.border}; }}
    QTabBar::tab {{ background: {c.secondary_panel}; color: {c.secondary_text}; padding: 10px 14px; border: 1px solid {c.divider}; }}
    QTabBar::tab:selected {{ background: {c.selected}; color: {c.text}; border-bottom: 2px solid {c.accent}; }}
    QSplitter::handle {{ background: {c.divider}; }}
    QSplitter::handle:hover {{ background: {c.accent}; }}
    QScrollArea {{ background: transparent; border: none; }}
    QWidget#workspaceScrollContent, QWidget#workspaceScrollViewport {{ background: {c.background}; }}
    QScrollBar:vertical {{ background: {c.navigation}; width: 12px; }}
    QScrollBar::handle:vertical {{ background: {c.border}; min-height: 24px; border-radius: 4px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QScrollBar:horizontal {{ background: {c.navigation}; height: 12px; }}
    QScrollBar::handle:horizontal {{ background: {c.border}; min-width: 24px; border-radius: 4px; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
    QMenuBar, QMenu, QStatusBar {{ background: {c.navigation}; color: {c.text}; }}
    QMenuBar::item:selected, QMenu::item:selected {{ background: {c.selected}; }}
    QMenu::item:disabled {{ color: {c.disabled_text}; }}
    QMenu::item {{ padding: 7px 24px; }}
    QProgressBar {{ background: {c.navigation}; border: 1px solid {c.border}; border-radius: 4px; max-height: 6px; }}
    QProgressBar::chunk {{ background: {c.accent}; }}
    QToolTip {{ background: {c.elevated}; color: {c.text}; border: 1px solid {c.border}; padding: 6px; }}
    '''


def apply_theme(widget, colors=COLORS):
    """Scope palette/QSS to this root and its owned widgets, never QApplication."""
    palette = QPalette()
    for role, color in ((QPalette.ColorRole.Window, colors.background),
                        (QPalette.ColorRole.WindowText, colors.text), (QPalette.ColorRole.Text, colors.text),
                        (QPalette.ColorRole.Base, colors.background), (QPalette.ColorRole.AlternateBase, colors.panel),
                        (QPalette.ColorRole.Button, colors.secondary_panel), (QPalette.ColorRole.ButtonText, colors.text),
                        (QPalette.ColorRole.Highlight, colors.selected), (QPalette.ColorRole.HighlightedText, colors.text),
                        (QPalette.ColorRole.PlaceholderText, colors.secondary_text)):
        palette.setColor(role, QColor(color))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(colors.disabled_text))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(colors.disabled_text))
    widget.setPalette(palette)
    widget.setFont(font())
    widget.setStyleSheet(stylesheet(colors))
    widget.setProperty('slTheme', 'dark' if colors == COLORS else 'light')


def display_html(html, colors=COLORS):
    """Theme the retained QTextDocument view only; stored/exported HTML is intact."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    replacements = {'#b91c1c': colors.error, '#b45309': colors.warning, '#a16207': colors.warning,
                    '#15803d': colors.success, '#166534': colors.success, '#4ade80': colors.success,
                    '#bbf7d0': colors.success, '#6b7280': colors.secondary_text, '#9ca3af': colors.secondary_text,
                    '#d1d5db': colors.text, '#111827': colors.text}
    html = re.sub(r'(?<![-\w])color\s*:\s*(#[a-fA-F0-9]{6})',
                  lambda match: 'color:' + replacements.get(match[1].lower(), match[1]), html)
    for old, new in (('#e5e7eb', colors.secondary_panel), ('#dcfce7', colors.selected), ('#f9fafb', colors.panel)):
        html = html.replace(old, new)
    # Confidence is displayed with neutral typography, independent of polarity.
    html = re.sub(r'(<b>Confidence Tier:</b>\s*<span style=[\'"])color:[^;]+',
                  lambda match: match[1]+'color:'+colors.text, html)
    return f'<div style="font-family:{TYPE.family};font-size:{TYPE.body}pt;color:{colors.text};">' + html + '</div>'
