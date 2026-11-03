"""Launch actual native UI with isolated preferences/output for manual GUI QA."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from signallens_settings import load_settings

app = QApplication([])
settings = deepcopy(load_settings())
settings['output_root'] = str(OUT / 'native_run/analysis')
gui.load_settings = lambda: settings
window = gui.SignalLensGui(ui_settings=QSettings(str(OUT/'native_run/native.ini'), QSettings.Format.IniFormat))
window.workspace.navigate('Overview')
window.showNormal()
window.resize(1040, 720) if '--minimum' in sys.argv else window.resize(1280, 900)
if '--stored' in sys.argv:
    import json
    reference = json.loads((OUT/'reference_verification.json').read_text())
    window.load_stored_summary(reference['midjourney']['report_pointer'])
window.show()
print('Native platform:', app.platformName(), 'screens:', [(s.name(), s.devicePixelRatio(), s.logicalDotsPerInch()) for s in app.screens()], flush=True)
sys.exit(app.exec())
