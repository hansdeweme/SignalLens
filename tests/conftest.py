"""Shared deterministic Qt lifetime and isolated ordinary workspace fixtures."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')

from copy import deepcopy
from pathlib import Path

import pytest
from PIL import Image
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

import signallens_gui as gui
from signallens_settings import DEFAULT_SETTINGS


@pytest.fixture(scope='session')
def app():
    application=QApplication.instance() or QApplication([])
    for filename in ('segoeui.ttf','segoeuib.ttf','consola.ttf'):
        path=Path('C:/Windows/Fonts')/filename
        if path.is_file():QFontDatabase.addApplicationFont(str(path))
    application.setQuitOnLastWindowClosed(False)
    return application


@pytest.fixture
def window(app,tmp_path,monkeypatch):
    settings=deepcopy(DEFAULT_SETTINGS)
    settings['output_root']=str(tmp_path/'analysis')
    monkeypatch.setattr(gui,'load_settings',lambda:settings)
    preferences=QSettings(str(tmp_path/'workspace.ini'),QSettings.Format.IniFormat)
    widget=gui.SignalLensGui(ui_settings=preferences)
    widget.resize(1280,900)
    widget.show()
    app.processEvents()
    yield widget
    assert not widget.workers.busy
    widget.close()
    widget.deleteLater()
    app.processEvents()


@pytest.fixture
def source(tmp_path):
    path=tmp_path/'source.png'
    Image.new('RGB',(32,48),'gray').save(path)
    return path
