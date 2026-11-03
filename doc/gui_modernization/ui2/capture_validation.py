"""Offscreen rendering of real widgets/states, including a real reference run.

Not mockups or native desktop screenshots. No existing result is overwritten.
"""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from copy import deepcopy
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from PyQt6.QtCore import QSettings, QEventLoop, QTimer
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from settings_dialog import SettingsDialog
from osint_dialogs import OSINTFindingDialog
from signallens_settings import load_settings

app = QApplication([])
for filename in ('segoeui.ttf', 'segoeuib.ttf', 'consola.ttf'):
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/' + filename)
settings = deepcopy(load_settings())
settings['output_root'] = str(OUT / 'native_run' / 'offscreen_analysis')
gui.load_settings = lambda: settings
window = gui.SignalLensGui(ui_settings=QSettings(str(OUT/'native_run/render_settings.ini'), QSettings.Format.IniFormat))
window.resize(1280, 900)
window.show()
manifest = []
def capture(name, widget=window, mode='offscreen Qt · 1280×900 requested'):
    app.processEvents()
    target = OUT / 'screenshots' / f'{name}.png'
    assert widget.grab().save(str(target))
    manifest.append({'file': target.name, 'rendering': mode, 'width': widget.width(), 'height': widget.height(),
                     'device_pixel_ratio': widget.devicePixelRatioF(), 'platform': app.platformName()})

window.workspace.navigate('Overview')
capture('01_empty_overview_offscreen')
source = ROOT / 'test_images/insta_fake/Curvy Leggings Outfit.jpg'
window.set_selected_file(source)
capture('02_image_selected_offscreen')
running = [False]
loop = QEventLoop()
def progress(invocation, message):
    if not running[0] and window.session.accepts(invocation):
        running[0] = True
        capture('03_analysis_running_offscreen')
def completed(snapshot):
    if snapshot.summary.status == 'completed' and window.session.report_current:
        loop.quit()
window.workers.status_changed.connect(progress)
window.snapshot_changed.connect(completed)
window.run_analysis()
deadline = QTimer()
deadline.setSingleShot(True)
deadline.timeout.connect(loop.quit)
deadline.start(120000)
loop.exec()
assert window.session.state.value == 'completed' and window.session.report_current
if window.workers.busy:
    window.workers.idle.connect(loop.quit)
    loop.exec()
assert running[0]
capture('04_completed_overview_offscreen')
for index, destination in enumerate(window.workspace.destinations[1:], 5):
    window.workspace.navigate(destination)
    capture(f'{index:02}_{destination.lower().replace(" ", "_")}_offscreen')
dialog = SettingsDialog(window)
dialog.show()
capture('10_settings_offscreen', dialog, 'offscreen Qt · existing SettingsDialog')
dialog.reject()
dialog = OSINTFindingDialog(window)
dialog.show()
capture('11_osint_dialog_offscreen', dialog, 'offscreen Qt · existing OSINTFindingDialog')
dialog.reject()
window.workspace.navigate('Overview')
window.resize(1040, 720)
capture('12_minimum_overview_offscreen', mode='offscreen Qt · minimum supported 1040×720 requested')
window.resize(1600, 1000)
capture('13_large_overview_offscreen', mode='offscreen Qt · large window 1600×1000 requested; not native maximization')
result = window.session.summary_data()['reasoning_trace']
(OUT / 'visual_reference_result.json').write_text(json.dumps({
    'source': str(source.relative_to(ROOT)), 'source_sha256': window.session.source_sha256,
    'scorecard': result['scorecard'], 'hypotheses': result['hypothesis_assessments'],
    'confidence': result['decision']['confidence_tier'], 'report_current': window.session.report_current,
    'native_windows_capture': False,
}, indent=2), encoding='utf-8')
(OUT / 'offscreen_capture_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
window.close()
print(f'Captured {len(manifest)} actual offscreen Qt renders; reference score {result["scorecard"]["suspicious_score"]}.')
