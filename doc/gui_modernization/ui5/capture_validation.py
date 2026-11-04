"""Inspect production stored investigations and explicitly labeled UI fixtures."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from collections import Counter
from copy import deepcopy
from dataclasses import replace
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
from artifact_presenter import digest_file
from explorer_presenter import build_explorer
from signallens_settings import load_settings
from source_image_viewer import preview_pool


def settle(predicate=lambda:True):
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        app.processEvents()
        if predicate():break
        time.sleep(.01)
    assert predicate(),'Asynchronous work did not finish'
    for i in range(5):app.processEvents()


def capture(name,fixture=False):
    settle()
    path=OUT/'screenshots'/(name+'_offscreen.png')
    assert window.grab().save(str(path))
    manifest.append({'file':path.name,'fixture':fixture,'platform':app.platformName(),
        'size':[window.width(),window.height()],'dpr':window.devicePixelRatioF(),
        'maximized_state':window.isMaximized(),'native_desktop':False})


def select_role(role):
    e=shell.evidence
    e.clear_filters()
    match=next((row for row in e.snapshot.evidence if row.role==role),None)
    if match:
        e.focus(match.hypothesis_id,match.evidence_id,role)
        return True
    return False


app=QApplication([])
for filename in ('segoeui.ttf','segoeuib.ttf','consola.ttf'):
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+filename)
settings=deepcopy(load_settings())
gui.load_settings=lambda:deepcopy(settings)
(OUT/'screenshots').mkdir(exist_ok=True)
window=gui.SignalLensGui(ui_settings=QSettings(str(OUT/'capture_preferences.ini'),QSettings.Format.IniFormat))
window.showNormal()
window.resize(1280,900)
window.show()
shell=window.workspace
shell.navigate('Evidence')
manifest,results=[],{}
capture('01_empty_evidence')
references=json.loads((OUT.parent/'ui3/reference_verification.json').read_text())
for case,reference in references.items():
    pointer=Path(reference['report_pointer'])
    pointer_before=digest_file(pointer)
    assert window.load_stored_summary(pointer)
    settle(lambda:bool(shell.forensics.artifacts))
    data=window.session.summary_data()
    frozen=window.session.summary_json
    trace=data['reasoning_trace']
    snapshot=shell.explorer_snapshot
    assert digest_file(ROOT/reference['source'])==reference['sha256']
    assert window.view_snapshot.source.profile=='normal'
    for key in ('suspicious_score','benign_score'):
        assert trace['scorecard'][key]==reference[key]
    assert snapshot.primary_finding==reference['pattern']
    expected_roles={(a['hypothesis_id'],role,eid) for a in trace['hypothesis_assessments']
        for role in ('supporting_evidence','contradicting_evidence','moderating_evidence','contextual_evidence')
        for eid in a.get(role,[])}
    assert {row.key for row in snapshot.evidence}==expected_roles
    reconciliation=next(row for row in snapshot.score_records if row.record_id=='reconciliation')
    assert reconciliation.outcome=='Reconciled',reconciliation
    shell.navigate('Evidence')
    shell.evidence.clear_filters()
    capture(case+'_02_evidence')
    select_role('supporting_evidence')
    capture(case+'_03_supporting')
    select_role('moderating_evidence')
    capture(case+'_04_moderating')
    # Actual compound processing node, with schema direct parents clearly labeled.
    shared=next((row for row in snapshot.evidence if row.lineage_id=='evidence:boundary'),None)
    if shared:
        shell.evidence.focus(shared.hypothesis_id,shared.evidence_id,shared.role)
        shell.evidence.tabs.setCurrentIndex(1)
        capture(case+'_05_lineage')
        shell.evidence.tabs.setCurrentIndex(0)
    links=[row for row in snapshot.evidence if row.artifact_ids]
    navigation=None
    if links:
        row=links[0]
        assert shell.navigate_context('Evidence',snapshot.identity,hypothesis=row.hypothesis_id,evidence=row.evidence_id,role=row.role)
        shell.evidence.show_artifact()
        assert shell.current_destination=='Image Forensics'
        assert shell.forensics.selected.artifact_id in row.artifact_ids
        navigation={'evidence_id':row.evidence_id,'artifact_id':shell.forensics.selected.artifact_id}
        shell.forensics.open_context('Evidence')
        assert shell.current_destination=='Evidence'
    shell.navigate_context('Reasoning',snapshot.identity,hypothesis=snapshot.primary_hypothesis)
    for tab in ('Hypotheses','Routes','Corroboration','Confidence','Scorecard'):
        shell.reasoning.focus(snapshot.primary_hypothesis,tab)
        capture(case+'_06_'+tab.lower())
    shell.reasoning.score_kind.setCurrentIndex(1)
    capture(case+'_07_calculation_audit')
    shell.reasoning.score_kind.setCurrentIndex(0)
    window.resize(1040,720)
    shell.navigate('Evidence')
    capture(case+'_08_minimum')
    window.resize(1280,900)
    assert frozen==window.session.summary_json and pointer_before==digest_file(pointer)
    results[case]={'source_sha256':reference['sha256'],'profile':'normal',
        'suspicious_score':trace['scorecard']['suspicious_score'],'benign_score':trace['scorecard']['benign_score'],
        'pattern':snapshot.primary_finding,'confidence':reference['confidence'],
        'hypothesis_count':len(snapshot.hypotheses),'evidence_role_count':len(snapshot.evidence),
        'roles':dict(Counter(row.role for row in snapshot.evidence)),
        'route_count':len(snapshot.routes),'gate_count':len(snapshot.corroboration),
        'contribution_count':len(snapshot.contributions),'reconciliation':reconciliation.outcome,
        'confidence_rules':{row.hypothesis_id:row.explanation for row in snapshot.confidence},
        'linked_evidence_count':len(links),'navigation_checked':navigation,
        'unchanged_summary_and_report_pointer':True,'detectors_rerun':False}

# UI fixtures are isolated in projection values; original stored investigations stay frozen.
original=shell.explorer_snapshot
base=original.evidence[0]
contradiction=replace(base,evidence_id='fixture:contradicting',role='contradicting_evidence',
    label='UI fixture: contradicting evidence',interpretation='Synthetic backend-role fixture for display validation.',
    artifact_ids=(),lineage_id=None)
shell.navigate('Evidence')
shell.evidence.bind(replace(original,evidence=(contradiction,)))
capture('fixture_09_contradicting',True)
shell.evidence.tabs.setCurrentIndex(1)
capture('fixture_10_missing_lineage',True)
shell.evidence.tabs.setCurrentIndex(0)
shell.evidence.bind(original)
shell.navigate('Reasoning')
shell.reasoning.focus(tab='Scorecard')
if original.contributions:
    row=replace(original.contributions[0],raw='3.0',credited='0.0',final='0.0',suppressed='3.0',classification='A',
        reason='UI fixture: confirmed duplicate numerical credit',
        fields=(('fixture','Synthetic confirmed-duplicate presentation example'),('raw','3.0'),
                ('credited','0.0'),('suppressed','3.0'),('reason','Confirmed duplicate numerical credit')))
    shell.reasoning.bind(replace(original,contributions=(row,)))
    shell.reasoning.focus(tab='Scorecard')
    shell.reasoning.message.setText('UI fixture: confirmed duplicate numerical credit; production results are unchanged.')
    capture('fixture_11_numerical_deduplication',True)
legacy=build_explorer(window.view_snapshot,{'full_text':'Legacy narrative retained; no structured trace.'})
shell.reasoning.bind(legacy)
shell.reasoning.message.setText('UI fixture: legacy narrative-only result. No structured records are invented.')
capture('fixture_12_legacy_result',True)
shell.reasoning.bind(original)
shell.reasoning.focus(tab='Confidence')
window.showMaximized()
capture('13_maximized_qt_state')
window.showNormal()
settle()
window.resize(1920,1080)
capture('14_expanded_logical_window')
window.resize(1280,900)
preview_pool().waitForDone()
settle()
(OUT/'reference_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
(OUT/'capture_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
window.close()
print(json.dumps(results,indent=2))
