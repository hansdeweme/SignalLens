"""Visible Windows launch with isolated preferences/output; F8 saves QA captures."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PyQt6.QtCore import QSettings,QTimer,QT_VERSION_STR,PYQT_VERSION_STR
from PyQt6.QtGui import QAction,QKeySequence
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from signallens_settings import load_settings

started=time.perf_counter()
app=QApplication([])
settings=deepcopy(load_settings())
settings['output_root']=str(OUT/'validation_output'/'native')
gui.load_settings=lambda:deepcopy(settings)
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
window=gui.SignalLensGui(ui_settings=QSettings(str(OUT/'validation_output/native_preferences.ini'),QSettings.Format.IniFormat))
window.setWindowTitle('SignalLens — UI-7 native validation')
manifest=[]

def capture():
    widget=app.activeModalWidget() or window
    name=f'native_{len(manifest)+1:02d}_{window.workspace.current_destination.replace(" ","_")}'
    path=OUT/'screenshots'/(name+'.png')
    widget.grab().save(str(path))
    manifest.append({'file':path.name,'platform':app.platformName(),'native':app.platformName()=='windows',
        'size':[widget.width(),widget.height()],'dpr':widget.devicePixelRatioF(),
        'screen_dpi':widget.screen().logicalDotsPerInch(),'maximized':window.isMaximized()})
    (OUT/'native_capture_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

action=QAction(window);action.setShortcut(QKeySequence('F8'));action.triggered.connect(capture);window.addAction(action)
window.show()
QTimer.singleShot(0,capture)
(OUT/'native_environment.json').write_text(json.dumps({'platform':app.platformName(),'python':sys.version,
    'qt':QT_VERSION_STR,'pyqt':PYQT_VERSION_STR,'startup_seconds':time.perf_counter()-started,
    'screens':[{'name':s.name(),'dpr':s.devicePixelRatio(),'logical_dpi':s.logicalDotsPerInch(),
        'physical_dpi':s.physicalDotsPerInch(),'geometry':[s.geometry().width(),s.geometry().height()]} for s in app.screens()]},indent=2),encoding='utf-8')
sys.exit(app.exec())
