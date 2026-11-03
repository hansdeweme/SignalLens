"""Validate existing production reference artifacts, without rerunning detectors."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from artifact_presenter import digest_file, discovery_context, discover_artifacts
from investigation_presenters import build_presentation
from source_image_viewer import preview_pool
from signallens_settings import load_settings


def wait_until(predicate):
    deadline = time.monotonic()+15
    while not predicate() and time.monotonic()<deadline:
        app.processEvents()
        time.sleep(.01)
    assert predicate(), 'Asynchronous inspection timed out'
    app.processEvents()


def capture(name):
    for _ in range(5): app.processEvents()
    target = OUT/'screenshots'/f'{name}_offscreen.png'
    assert window.grab().save(str(target))
    manifest.append({'file':target.name,'size':[window.width(),window.height()],
                     'platform':app.platformName(),'native':False,'dpr':window.devicePixelRatioF()})


def select(detector, key=None):
    for index in range(workspace.tree.topLevelItemCount()):
        group = workspace.tree.topLevelItem(index)
        for child in range(group.childCount()):
            item = group.child(child)
            artifact = item.data(0,Qt.ItemDataRole.UserRole)
            if artifact.detector_id == detector and (key is None or artifact.artifact_id.endswith('/'+key)):
                workspace.tree.setCurrentItem(item)
                if artifact.available and artifact.path:
                    wait_until(lambda:not workspace.artifact._image.isNull())
                return artifact
    raise AssertionError((detector,key))


app = QApplication([])
for filename in ('segoeui.ttf','segoeuib.ttf','consola.ttf'):
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+filename)
settings = deepcopy(load_settings())
settings['output_root'] = str(OUT/'validation_output')
gui.load_settings = lambda:deepcopy(settings)
(OUT/'screenshots').mkdir(exist_ok=True)
window = gui.SignalLensGui(ui_settings=QSettings(str(OUT/'capture_preferences.ini'),QSettings.Format.IniFormat))
window.resize(1280,900)
window.show()
window.workspace.navigate('Image Forensics')
workspace = window.workspace.forensics
manifest,results = [],{}
capture('01_empty')
references = json.loads((OUT.parent/'ui3/reference_verification.json').read_text())
for name,reference in references.items():
    pointer = Path(reference['report_pointer'])
    assert window.load_stored_summary(pointer)
    wait_until(lambda:bool(workspace.artifacts) and not workspace.source._image.isNull())
    data = window.session.summary_data()
    assert digest_file(ROOT/reference['source']) == reference['sha256']
    assert data['reasoning_trace']['decision']['dominant_pattern'] == reference['pattern']
    assert data['reasoning_trace']['decision']['confidence_tier'] == reference['confidence']
    for key in ('suspicious_score','benign_score'):
        assert data['reasoning_trace']['scorecard'][key] == reference[key]
    results[name] = {'source':reference['source'],'sha256':reference['sha256'],
        'pattern':reference['pattern'],'confidence':reference['confidence'],
        'suspicious_score':reference['suspicious_score'],'benign_score':reference['benign_score'],
        'report_pointer':str(pointer),'validation':'Existing production UI-3 run reopened; no detectors executed',
        'counts':dict(Counter(a.artifact_type for a in workspace.artifacts)),
        'registrations':dict(Counter(a.registration.value for a in workspace.artifacts)),
        'artifact_count':len(workspace.artifacts),'detector_count':len(set(a.detector_id for a in workspace.artifacts)),
        'artifacts':[asdict(a) for a in workspace.artifacts]}
    select('ela','ela_image_path')
    capture(name+'_02_side_by_side')
    workspace.mode.setCurrentIndex(1)
    workspace.source.zoom(1.25)
    capture(name+'_03_synchronized')
    workspace.mode.setCurrentIndex(2)
    assert workspace._overlay_items
    capture(name+'_04_overlay')
    select('fft')
    assert not workspace.mode.model().item(2).isEnabled()
    capture(name+'_05_frequency')
    select('region_masks')
    capture(name+'_06_mask_or_structured')
    window.resize(1040,720)
    select('noise','residual_image_path')
    capture(name+'_07_minimum')
    window.resize(1280,900)
    # A synthetic unavailable descriptor exercises empty handling without touching reference files.
    unavailable = replace(workspace.artifacts[0],artifact_type='E',available=False,
                          reason='Validation fixture: recorded artifact is unavailable')
    item = workspace.tree.topLevelItem(0).child(0)
    item.setData(0,Qt.ItemDataRole.UserRole,unavailable)
    workspace.tree.setCurrentItem(item)
    capture(name+'_08_unavailable_fixture')
preview_pool().waitForDone()
app.processEvents()
(OUT/'reference_validation.json').write_text(json.dumps(results,indent=2,default=str),encoding='utf-8')
(OUT/'capture_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
samples = ['# Decoded reference artifact inventory','',
           'Actual stored production paths are in reference_validation.json. Dimensions below are decoded native width × height; D/E rows may have no raster. B/UNKNOWN rows are independently inspectable spatial candidates, not demonstrated transforms.','',
           '| Reference | Producer / field | Type | Dimensions | Registration | Evidence IDs |',
           '|---|---|---|---|---|---|']
for case,data in results.items():
    for artifact in data['artifacts']:
        samples.append('| '+ ' | '.join((case,artifact['artifact_id'],artifact['artifact_type'],
            f"{artifact['width']} × {artifact['height']}",artifact['registration'],', '.join(artifact['evidence_ids']) or 'Not recorded'))+' |')
(OUT/'artifact_samples.md').write_text('\n'.join(samples)+'\n',encoding='utf-8')
window.close()
print(json.dumps({name:{k:v for k,v in data.items() if k in ('artifact_count','detector_count','counts','registrations','pattern','confidence')} for name,data in results.items()},indent=2))
