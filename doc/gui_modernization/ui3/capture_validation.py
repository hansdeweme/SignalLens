"""Real GUI pipelines and explicitly offscreen Qt captures; no fixture scoring."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from PyQt6.QtCore import QSettings, QEventLoop, QTimer, QThreadPool
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from investigation_session import InvestigationSession, InvestigationState
from signallens_settings import load_settings

app = QApplication([])
for filename in ('segoeui.ttf', 'segoeuib.ttf', 'consola.ttf'):
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/' + filename)
settings = deepcopy(load_settings())
settings['output_root'] = str(OUT / 'reference_runs')
(OUT / 'native_run').mkdir(parents=True, exist_ok=True)
(OUT / 'screenshots').mkdir(parents=True, exist_ok=True)
gui.load_settings = lambda: deepcopy(settings)
window = gui.SignalLensGui(ui_settings=QSettings(str(OUT/'native_run/render.ini'), QSettings.Format.IniFormat))
window.resize(1280, 900)
window.show()
window.workspace.navigate('Overview')
manifest, results = [], {}

def settle(milliseconds=150):
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()

def capture(name):
    settle()
    target = OUT / 'screenshots' / f'{name}_offscreen.png'
    assert window.grab().save(str(target))
    manifest.append({'file': target.name, 'platform': app.platformName(),
        'size': [window.width(), window.height()], 'dpr': window.devicePixelRatioF(),
        'native': False, 'fixture': name in ('06_inconclusive', '07_missing_source', '08_failed', '11_long_content')})

capture('01_empty')
baseline = json.loads((OUT.parent/'ui2/reference_verification.json').read_text())
sources = {
    'instagram': 'test_images/insta_fake/Curvy Leggings Outfit.jpg',
    'midjourney': 'test_images/midjourney/theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png'}
running = [False]
def progress(invocation, message):
    if not running[0] and window.session.accepts(invocation):
        running[0] = True
        capture('03_analyzing')
window.workers.status_changed.connect(progress)
for case, filename in sources.items():
    source = ROOT / filename
    window.set_selected_file(source)
    settle(400)
    if case == 'instagram':
        capture('02_selected')
    loop = QEventLoop()
    def completed(snapshot):
        if snapshot.summary.status in ('completed', 'failed') and not window.workers.busy:
            loop.quit()
    window.snapshot_changed.connect(completed)
    window.workers.idle.connect(loop.quit)
    QTimer.singleShot(120000, loop.quit)
    window.run_analysis()
    loop.exec()
    window.snapshot_changed.disconnect(completed)
    window.workers.idle.disconnect(loop.quit)
    assert window.session.state == InvestigationState.COMPLETED, window.session.error
    assert window.session.report_current
    trace = window.session.summary_data()['reasoning_trace']
    data = window.session.summary_data()
    result = {'source': filename, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'profile': window.session.invocation.profile,
        'settings': json.loads(window.session.invocation.settings_json),
        'scene_context': dict(window.session.invocation.scene_context),
        'suspicious_score': trace['scorecard']['suspicious_score'],
        'benign_score': trace['scorecard']['benign_score'],
        'pattern': data['overall_pattern'], 'confidence': data['overall_confidence'],
        'hypotheses': trace['hypothesis_assessments'],
        'coverage_counts': window.analysis_state.analysis_coverage.get('stage_counts'),
        'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == window.session.source_sha256,
        'report_current': window.session.report_current,
        'report_pointer': window._report_paths['current_report']}
    for key in ('sha256', 'suspicious_score', 'benign_score', 'pattern', 'confidence', 'hypotheses', 'coverage_counts'):
        assert result[key] == baseline[case][key], (case, key)
    assert result['source_unchanged']
    results[case] = result
    capture('04_instagram_complete' if case == 'instagram' else '05_midjourney_complete')

original = window.session
original_summary = original.summary_data()
fixture = deepcopy(original_summary)
fixture['reasoning_trace']['decision'].update(primary_hypothesis='unresolved_anomaly', confidence_tier='Inconclusive', dominant_pattern='inconclusive')
fixture['reasoning_trace']['confidence_policy'] = {}
window.session = replace(original, summary_json=json.dumps(fixture), result_id='visual-inconclusive-fixture')
window.update_summary()
capture('06_inconclusive')
window.session = replace(original, image_path=str(OUT/'native_run/missing_source.png'))
window.update_summary()
settle(500)
capture('07_missing_source')
window.session = replace(original, state=InvestigationState.FAILED, invocation=None, summary_json=None, result_id=None, error='Validation fixture: decoder failure')
window.update_summary()
capture('08_failed')
window.session = original
window.update_summary()
window.resize(1040, 720)
capture('09_minimum')
window.resize(1600, 1000)
capture('10_large')
window.resize(1280, 900)
long = deepcopy(original_summary)
for assessment in long['reasoning_trace']['hypothesis_assessments']:
    assessment['explanation'] = 'Long recorded explanation for wrapping validation. ' * 100
window.session = replace(original, image_path='a_very_long_source_filename_'*12+'.png', summary_json=json.dumps(long))
window.update_summary()
capture('11_long_content')
window.session = original
window.update_summary()
window.workspace.overview.scroll.verticalScrollBar().setValue(window.workspace.overview.scroll.verticalScrollBar().maximum())
capture('12_evidence_scope')
window.workspace.overview.show_narrative()
settle()
assert window.workspace.overview.narrative_dialog.grab().save(str(OUT/'screenshots/13_narrative_offscreen.png'))
window.workspace.overview.narrative_dialog.close()
(OUT/'reference_verification.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
(OUT/'offscreen_capture_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
window.close()
QThreadPool.globalInstance().waitForDone()
print({key: (value['suspicious_score'], value['benign_score'], value['confidence']) for key,value in results.items()})
print(f'{len(manifest)+1} offscreen captures; reference outputs match UI-2.')
