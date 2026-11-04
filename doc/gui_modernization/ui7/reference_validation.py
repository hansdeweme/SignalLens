"""Fresh saved-reference integration verification; no detectors are rerun."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from copy import deepcopy
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from signallens_settings import load_settings
from artifact_presenter import digest_file
from osint_reverse_search import add_manual_match
from source_image_viewer import preview_pool
from report_workspace import export_pool

app=QApplication([])
for font in ('segoeui.ttf','segoeuib.ttf','consola.ttf'):QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+font)
settings=deepcopy(load_settings());settings['output_root']=str(OUT/'validation_output/references')
gui.load_settings=lambda:deepcopy(settings)
window=gui.SignalLensGui(ui_settings=QSettings(str(OUT/'validation_output/reference_preferences.ini'),QSettings.Format.IniFormat))
window.resize(1280,900);window.show()
def settle(predicate=lambda:True):
    end=time.monotonic()+30
    while time.monotonic()<end:
        app.processEvents()
        if predicate():break
        time.sleep(.01)
    assert predicate(),'Integration delivery timeout'
    for _ in range(4):app.processEvents()

results={}
references=json.loads((OUT.parent/'ui3/reference_verification.json').read_text())
for name,ref in references.items():
    pointer=Path(ref['report_pointer']);before=digest_file(pointer)
    assert window.load_stored_summary(pointer)
    settle(lambda:window.workspace.provenance.note is not None and bool(window.workspace.forensics.artifacts))
    frozen=window.session.summary_json
    data=window.session.summary_data();trace=data['reasoning_trace']
    assert digest_file(ROOT/ref['source'])==ref['sha256']
    assert window.view_snapshot.source.profile=='normal'
    assert trace['scorecard']['suspicious_score']==ref['suspicious_score']
    assert trace['scorecard']['benign_score']==ref['benign_score']
    assert trace['decision']['dominant_pattern']==ref['pattern']
    assert window.view_snapshot.summary.confidence_tier==ref['confidence']
    for destination in window.workspace.destinations:
        window.workspace.navigate(destination);settle()
        assert window.workspace.current_destination==destination
        path=OUT/'screenshots'/(name+'_'+destination.replace(' ','_')+'_offscreen.png')
        assert window.grab().save(str(path))
    draft=deepcopy(window.osint_result)
    add_manual_match(draft,'other','https://example.com/ui7-validation',title='UI-7 contextual fixture',notes='Local QA; not verified evidence')
    assert window._commit_osint(window.session.session_id,draft)
    assert window.session.annotation_revision==1 and window.session.summary_json==frozen
    reports=window.workspace.reports
    reports.output.setText(str(OUT/'validation_output/reference_exports'))
    assert reports.start_export();settle(lambda:not reports.pending)
    paths=reports.saved_paths;presentation=reports.presentation
    assert Path(paths['final_summary_html']).read_text(encoding='utf-8')==presentation.html
    assert Path(paths['final_summary_txt']).read_text(encoding='utf-8')==presentation.text
    assert Path(paths['final_summary_json']).read_text(encoding='utf-8')==presentation.structured_json
    assert digest_file(pointer)==before and window.session.summary_json==frozen
    results[name]={'source_sha256':ref['sha256'],'profile':'normal','suspicious_score':ref['suspicious_score'],
        'benign_score':ref['benign_score'],'pattern':ref['pattern'],'confidence':ref['confidence'],
        'primary_hypothesis':trace['decision'].get('primary_hypothesis'),'all_six_workspaces':True,
        'annotation_revision':1,'preview_export_bytes_equal':True,'original_pointer_unchanged':True,'detectors_rerun':False}
preview_pool().waitForDone();export_pool().waitForDone();window.close()
(OUT/'reference_validation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
