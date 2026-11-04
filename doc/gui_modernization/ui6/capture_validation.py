"""Non-destructive saved-reference provenance/OSINT/report acceptance captures."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from copy import deepcopy
from pathlib import Path
import json
import sys
import time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from artifact_presenter import digest_file
from osint_reverse_search import add_manual_match
from osint_dialogs import OSINTFindingDialog
from report_workspace import export_pool
from source_image_viewer import preview_pool
from signallens_settings import load_settings


def settle(predicate=lambda:True):
    end=time.monotonic()+20
    while time.monotonic()<end:
        app.processEvents()
        if predicate():break
        time.sleep(.01)
    assert predicate(),'Timed out waiting for UI work'
    for _ in range(6):app.processEvents()


def capture(name,fixture=False,widget=None):
    settle()
    widget=widget or window
    path=OUT/'screenshots'/(name+'_offscreen.png')
    assert widget.grab().save(str(path))
    manifest.append({'file':path.name,'platform':app.platformName(),'native':False,'fixture':fixture,
        'size':[widget.width(),widget.height()],'dpr':widget.devicePixelRatioF()})


app=QApplication([])
for font in ('segoeui.ttf','segoeuib.ttf','consola.ttf'):QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+font)
settings=deepcopy(load_settings())
settings['output_root']=str(OUT/'validation_output')
gui.load_settings=lambda:deepcopy(settings)
(OUT/'screenshots').mkdir(exist_ok=True)
window=gui.SignalLensGui(ui_settings=QSettings(str(OUT/'capture_preferences.ini'),QSettings.Format.IniFormat))
window.showNormal();window.resize(1280,900);window.show()
shell=window.workspace
manifest=[];results={}
shell.navigate('Provenance');capture('01_empty_provenance')
shell.navigate('Reports');capture('02_empty_reports')
references=json.loads((OUT.parent/'ui3/reference_verification.json').read_text())
for name,reference in references.items():
    pointer=Path(reference['report_pointer']);before=digest_file(pointer)
    assert window.load_stored_summary(pointer)
    settle(lambda:shell.provenance.note is not None)
    session=window.session
    frozen=session.summary_json
    original=session.summary_data()
    presentation=shell.provenance.presentation
    assert digest_file(ROOT/reference['source'])==reference['sha256']
    assert window.view_snapshot.source.profile=='normal'
    assert presentation.verification=='unverified'
    assert presentation.fields
    shell.navigate('Provenance')
    shell.provenance.tabs.setCurrentIndex(0)
    capture(name+'_03_metadata')
    if name=='midjourney':
        shell.provenance.search.setText('DigitalSourceType')
        capture(name+'_04_unverified_declaration')
        shell.provenance.search.clear()
    shell.provenance.tabs.setCurrentIndex(1)
    dialog=OSINTFindingDialog(window)
    dialog.notes_edit.setPlainText('UI validation draft; cancelling does not commit this entry.')
    dialog.show();capture(name+'_05_osint_edit',True,dialog);dialog.reject()
    revision=session.annotation_revision
    draft=deepcopy(window.osint_result)
    if draft is None:
        # A recorded reference without an annotation object remains valid for reporting.
        raise AssertionError('Reference annotation contract missing')
    add_manual_match(draft,'other','https://example.com/ui6-validation',title='Controlled contextual source',
                     notes='UI validation annotation; external claim, not a forensic measurement.')
    old_report=shell.reports.presentation
    assert window._commit_osint(session.session_id,draft)
    assert session.annotation_revision==revision+1
    assert session.summary_json==frozen
    assert 'Controlled contextual source' in shell.provenance.annotation_detail.toPlainText()
    capture(name+'_06_annotation_revision')
    shell.navigate('Reports')
    current=shell.reports.presentation
    assert current.snapshot.annotation_revision==session.annotation_revision
    assert current.snapshot.payload()['reasoning_trace']==original['reasoning_trace']
    capture(name+'_07_report_ready')
    shell.reports.presentation=old_report
    assert not shell.reports.start_export()
    capture(name+'_08_stale_fixture',True)
    shell.reports.refresh_preview()
    current=shell.reports.presentation
    shell.reports.output.setText(str(OUT/'validation_output'/'exports'))
    assert shell.reports.start_export()
    settle(lambda:not shell.reports.pending)
    paths=shell.reports.saved_paths
    assert paths
    assert Path(paths['final_summary_html']).read_text(encoding='utf-8')==current.html
    assert Path(paths['final_summary_txt']).read_text(encoding='utf-8')==current.text
    assert json.loads(Path(paths['final_summary_json']).read_text(encoding='utf-8'))==current.snapshot.payload()
    capture(name+'_09_export_saved')
    shell.reports.pending['failure-fixture']=current.snapshot
    assert not shell.reports.accept_export('failure-fixture',None,'UI fixture: destination unavailable')
    capture(name+'_10_export_failure_fixture',True)
    shell.reports.refresh_preview()
    window.resize(1040,720)
    shell.navigate('Provenance');shell.provenance.tabs.setCurrentIndex(0);capture(name+'_11_minimum_provenance')
    shell.provenance.tabs.setCurrentIndex(1);capture(name+'_11_minimum_osint')
    shell.navigate('Reports');capture(name+'_12_minimum_reports')
    window.resize(1280,900)
    for key in ('suspicious_score','benign_score'):
        assert session.summary_data()['reasoning_trace']['scorecard'][key]==reference[key]
    assert session.summary_data()['reasoning_trace']['decision']['dominant_pattern']==reference['pattern']
    assert session.summary_json==frozen and digest_file(pointer)==before
    results[name]={'source_sha256':reference['sha256'],'profile':'normal',
        'suspicious_score':reference['suspicious_score'],'benign_score':reference['benign_score'],
        'pattern':reference['pattern'],'confidence':reference['confidence'],
        'metadata_fields':len(presentation.fields),'namespaces':list(dict.fromkeys(f.namespace for f in presentation.fields)),
        'recorded_verification':presentation.verification,'raw_metadata_recovery':shell.provenance.note,
        'annotation_revision_before':revision,'annotation_revision_after':session.annotation_revision,
        'preview_export_snapshot_equal':True,'frozen_summary_and_original_pointer_unchanged':True,
        'export_pointer':paths['current_report'],'detectors_rerun':False}

legacy=OUT/'validation_output'/'legacy_summary.json'
legacy.parent.mkdir(parents=True,exist_ok=True)
legacy.write_text(json.dumps({'full_text':'Legacy recorded narrative; metadata extraction was not recorded.'}),encoding='utf-8')
assert window.load_stored_summary(legacy)
settle(lambda:shell.provenance.note is not None)
shell.navigate('Provenance');capture('fixture_13_legacy_missing_metadata',True)
shell.navigate('Reports');capture('fixture_14_legacy_report',True)
preview_pool().waitForDone();export_pool().waitForDone();settle()
(OUT/'reference_validation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
(OUT/'capture_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
window.close()
print(json.dumps(results,indent=2))
