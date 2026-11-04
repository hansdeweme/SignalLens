"""Repeatable synthetic/saved-result timings, separate from native UI inspection."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from copy import deepcopy
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PIL import Image
from PyQt6.QtCore import QSettings,QTimer
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication
import signallens_gui as gui
from signallens_settings import load_settings
from investigation_session import InvestigationSession,InvestigationState
from source_image_viewer import preview_pool
from report_workspace import export_pool

class Counters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),('PeakWorkingSetSize',ctypes.c_size_t),
        ('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),
        ('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]

def memory_mb():
    kernel=ctypes.WinDLL('kernel32');kernel.GetCurrentProcess.restype=wintypes.HANDLE
    data=Counters();data.cb=ctypes.sizeof(data)
    query=ctypes.WinDLL('psapi').GetProcessMemoryInfo
    query.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    query(kernel.GetCurrentProcess(),ctypes.byref(data),data.cb)
    return round(data.WorkingSetSize/1024**2,2)

def settle(predicate=lambda:True,timeout=60):
    end=time.perf_counter()+timeout
    while time.perf_counter()<end:
        app.processEvents()
        if predicate():break
        time.sleep(.005)
    assert predicate(),'Benchmark did not finish'
    for _ in range(3):app.processEvents()

def measure(name,action,ready=None):
    settle();gaps.clear();last[0]=time.perf_counter()
    before=memory_mb();start=time.perf_counter()
    action()
    if ready:settle(ready)
    else:app.processEvents()
    elapsed=time.perf_counter()-start
    values[name]={'seconds':elapsed,'max_heartbeat_gap_seconds':max(gaps,default=0),
                  'rss_before_mb':before,'rss_after_mb':memory_mb()}
    print(name,round(elapsed,4),'s',flush=True)

app=QApplication([])
for font in ('segoeui.ttf','segoeuib.ttf','consola.ttf'):QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+font)
if '--eager-baseline' in sys.argv:
    # Reconstruct the pre-fix render behavior without editing production files,
    # keeping fonts, inputs and benchmark environment identical for comparison.
    from report_workspace import ReportsWorkspace
    from gui_design_system import display_html
    def eager_render(self,*args):
        if not self.presentation:self.preview.clear();return
        format=self.format.currentText()
        if format=='HTML':self.preview.setHtml(display_html(self.presentation.html))
        else:self.preview.setPlainText(self.presentation.text if format=='TXT' else self.presentation.structured_json)
    ReportsWorkspace.render=eager_render
settings=deepcopy(load_settings());settings['output_root']=str(OUT/'validation_output/performance')
gui.load_settings=lambda:deepcopy(settings)
work=OUT/'validation_output/performance';work.mkdir(parents=True,exist_ok=True)
values={'font_setup':'explicit Windows Segoe UI/Consolas for offscreen Qt','render_mode':'pre-fix eager layout reconstruction' if '--eager-baseline' in sys.argv else 'current deferred layout'};last=[time.perf_counter()];gaps=[]
timer=QTimer();timer.setInterval(10)
def heartbeat():
    current=time.perf_counter();gaps.append(current-last[0]);last[0]=current
timer.timeout.connect(heartbeat);timer.start()
start=time.perf_counter()
window=gui.SignalLensGui(ui_settings=QSettings(str(work/'preferences.ini'),QSettings.Format.IniFormat))
window.resize(1280,900);window.show();settle()
values['startup']={'seconds':time.perf_counter()-start,'rss_mb':memory_mb()}
window.workspace.navigate('Overview')
refs=json.loads((OUT.parent/'ui3/reference_verification.json').read_text())
measure('typical_stored_load',lambda:window.load_stored_summary(refs['instagram']['report_pointer']),
        lambda:bool(window.workspace.forensics.artifacts) and not window.workspace.preview._image.isNull())
for destination in window.workspace.destinations:
    measure('navigate_'+destination,lambda d=destination:window.workspace.navigate(d))
window.workspace.navigate('Image Forensics')
group=window.workspace.forensics.tree.topLevelItem(1)
measure('typical_artifact_switch',lambda:window.workspace.forensics.tree.setCurrentItem(group.child(0)),
        lambda:not window.workspace.forensics.artifact._image.isNull())
large=work/'large_81mp.png'
if not large.exists():Image.new('RGB',(9000,9000),'navy').save(large)
measure('large_81mp_source_preview',lambda:window.set_selected_file(large),lambda:
    not window.workspace.preview._image.isNull() or 'Loading' not in window.workspace.preview.message.text())
values['large_81mp_source_preview']['decoded_preview_dimensions']=[window.workspace.preview._image.width(),window.workspace.preview._image.height()]
values['large_81mp_source_preview']['message']=window.workspace.preview.message.text()
practical=work/'large_30mp.png'
if not practical.exists():Image.new('RGB',(6000,5000),'navy').save(practical)
measure('large_30mp_source_preview',lambda:window.set_selected_file(practical),lambda:
    not window.workspace.preview._image.isNull() or 'Loading' not in window.workspace.preview.message.text())
values['large_30mp_source_preview']['message']=window.workspace.preview.message.text()

# A deterministic large trace, not a new forensic result or a calibration fixture.
evidence={f'bench:{i}':{'section':'bench','label':f'Benchmark observation {i}','interpretation':'Recorded fixture interpretation'} for i in range(2500)}
trace={'decision':{'primary_hypothesis':'localized_editing','dominant_pattern':'benchmark_fixture','confidence_tier':'Inconclusive'},
    'hypothesis_assessments':[{'hypothesis_id':'localized_editing','explanation':'Synthetic performance fixture',
        'supporting_evidence':list(evidence),'evidence_details':evidence}],
    'decision_route_trace':[{'route':f'fixture_route_{i}','selected':False,'reason':'Benchmark'} for i in range(1000)]}
narrative=('Recorded fixture paragraph; no forensic conclusion is asserted.\n'*32000)
data={'full_text':narrative,'full_html':'<pre>'+narrative+'</pre>','reasoning_trace':trace,'sections':{}}
session=InvestigationSession(state=InvestigationState.COMPLETED,result_id='performance-fixture',analysis_revision=1,
    summary_json=json.dumps(data))
window.clear_analysis_state();window.session=session;window.current_analysis_dir=work/'automatic_report'
if '--profile' in sys.argv:
    import cProfile,pstats
    profile=cProfile.Profile()
    measure('large_trace_and_report_bind',lambda:profile.runcall(window.update_summary))
    with (OUT/'profile_before.txt').open('w') as stream:pstats.Stats(profile,stream=stream).sort_stats('cumulative').print_stats(35)
else:measure('large_trace_and_report_bind',window.update_summary)
window.workspace.navigate('Evidence')
measure('large_evidence_filter',lambda:window.workspace.evidence.search.setText('Benchmark observation 2499'))
window.workspace.navigate('Reasoning')
measure('large_reasoning_route_detail',lambda:window.workspace.reasoning.panes['Routes'].table.selectRow(999))
payload={'raw_watchlist_hits':{'fixture':[{'raw_key':f'XMP:Field{i}','group':'XMP','value':'Recorded text '*50} for i in range(5000)]}}
measure('large_metadata_bind',lambda:(setattr(window.workspace.provenance,'payload',payload),window.workspace.provenance.rebuild()))
window.workspace.navigate('Provenance')
measure('large_metadata_filter',lambda:window.workspace.provenance.search.setText('Field4999'))
measure('large_automatic_report_save',window.refresh_report_snapshot)
window.workspace.navigate('Reports');window.workspace.reports.output.setText(str(work/'explicit_exports'))
measure('large_explicit_export',window.workspace.reports.start_export,lambda:not window.workspace.reports.pending)
values['large_fixture']={'evidence_rows':2500,'route_rows':1000,'metadata_rows':5000,'narrative_characters':len(narrative)}
measure('switch_10_investigations',lambda:[window.set_selected_file(large) for _ in range(10)])
preview_pool().waitForDone();export_pool().waitForDone();settle()
values['post_switch_memory_mb']=memory_mb()
target=OUT/('performance_profile.json' if '--profile' in sys.argv else 'performance_after.json' if '--after' in sys.argv else 'performance_before.json')
target.write_text(json.dumps(values,indent=2),encoding='utf-8')
window.close()
