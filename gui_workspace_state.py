"""Versioned, content-free workspace preferences, separate from analysis JSON."""
from pathlib import Path
from PyQt6.QtCore import QSettings, QByteArray, Qt
from PyQt6.QtGui import QGuiApplication
from gui_design_system import GEOMETRY
from app_paths import app_dir

PREFIX = 'workspace/v1/'


def default_settings():
    return QSettings(str(app_dir() / 'signallens_workspace.ini'), QSettings.Format.IniFormat)


def ensure_visible(window):
    screens = [screen.availableGeometry() for screen in QGuiApplication.screens()]
    if not screens:
        return
    rect = window.geometry()
    # Require the title area and a usable portion, not just one intersecting pixel.
    if any(screen.contains(rect.topLeft()) and screen.intersected(rect).width() >= min(400, rect.width())
           and screen.intersected(rect).height() >= min(200, rect.height()) for screen in screens):
        return
    available = screens[0]
    window.resize(min(GEOMETRY.normal_width, available.width()), min(GEOMETRY.normal_height, available.height()))
    window.move(available.left() + max(0, (available.width()-window.width())//2),
                available.top() + max(0, (available.height()-window.height())//2))


def restore_workspace(window, settings):
    geometry = settings.value(PREFIX+'geometry')
    if isinstance(geometry, QByteArray):
        window.restoreGeometry(geometry)
    ensure_visible(window)
    destination = settings.value(PREFIX+'destination', 'Overview')
    window.workspace.navigate(destination if destination in window.workspace.destinations else 'Overview')
    for name, splitter in (('navigation', window.workspace.splitter), ('overview', window.workspace.overview_splitter)):
        sizes = settings.value(PREFIX+name)
        try:
            sizes = [int(size) for size in sizes]
            if len(sizes) == 2 and all(0 < size < 20000 for size in sizes):
                splitter.setSizes(sizes)
        except (TypeError, ValueError):
            pass
    if settings.value(PREFIX+'maximized', False, type=bool):
        window.setWindowState(window.windowState() | Qt.WindowState.WindowMaximized)


def save_workspace(window, settings):
    settings.setValue(PREFIX+'geometry', window.saveGeometry())
    settings.setValue(PREFIX+'maximized', window.isMaximized())
    settings.setValue(PREFIX+'destination', window.workspace.current_destination)
    settings.setValue(PREFIX+'navigation', window.workspace.splitter.sizes())
    settings.setValue(PREFIX+'overview', window.workspace.overview_splitter.sizes())
    settings.sync()
