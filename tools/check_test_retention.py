"""Isolated in-memory faults demonstrating retained assertions detect defects.

These are review probes, not additional collected regression tests. Production
files are never edited. Each probe runs in a separate Python process.
"""
import argparse
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
PROBES={
    'route_policy_order':'tests/test_reasoning.py::test_irrelevant_route_order_does_not_change_assessments',
    'repeated_evaluation':'tests/test_reasoning.py::test_irrelevant_route_order_does_not_change_assessments',
    'scorecard_mutation':'tests/test_confidence_policy.py::test_scorecard_shadow_and_corroboration_audits_are_unchanged_by_policy',
    'empty_polarity':'tests/test_hypothesis_scoping.py::test_no_meaningful_evidence_has_no_invented_support_or_contradictions',
    'digital_capture_enhancement':'tests/test_hypothesis_scoping.py::test_populated_source_type_is_not_enough_for_a_generation_declaration',
    'ignored_detector_filter':'tests/test_explorer_workspace.py::test_filters_are_explicit_backend_values',
}


def run_probe(name):
    import pytest
    class Fault:
        def __init__(self):
            self.patch=pytest.MonkeyPatch()
            self.failed=[]
            self.errors=[]
            self.calls=0

        @pytest.hookimpl(tryfirst=True)
        def pytest_runtest_call(self,item):
            module=item.module
            if name in ('route_policy_order','repeated_evaluation'):
                original=module.assess
                calls=[0]
                def broken(env,routes=None):
                    result=original(env,routes)
                    calls[0]+=1
                    if routes is not None and name=='route_policy_order' or calls[0]==2 and name=='repeated_evaluation':
                        result[4]['confidence_policy']['injected_fault']=True
                    return result
                self.patch.setattr(module,'assess',broken)
            elif name=='scorecard_mutation':
                original=module.logic.finish_decision
                def broken(env,*args,**kwargs):
                    result=original(env,*args,**kwargs)
                    env.card.suspicious_score+=1
                    return result
                self.patch.setattr(module.logic,'finish_decision',broken)
            elif name=='empty_polarity':
                original=module.logic.synthesize_overall
                def broken(sections,*args,**kwargs):
                    result=list(original(sections,*args,**kwargs))
                    if not sections:result[3]='suspicious'
                    return tuple(result)
                self.patch.setattr(module.logic,'synthesize_overall',broken)
            elif name=='digital_capture_enhancement':
                original=module.payload_from_record
                def broken(record):
                    result=original(record)
                    if record.get('XMP-iptcExt:DigitalSourceType')==module.IPTC_SOURCE_TYPE+'digitalCapture':
                        result['classification']['declared_enhancement']=True
                    return result
                self.patch.setattr(module,'payload_from_record',broken)
            else:
                from explorer_workspace import EvidenceWorkspace
                original=EvidenceWorkspace.filter_rows
                def broken(widget,*args,**kwargs):
                    combo=widget.filters['detector']
                    combo.blockSignals(True)
                    combo.setCurrentIndex(0)
                    combo.blockSignals(False)
                    return original(widget,*args,**kwargs)
                self.patch.setattr(EvidenceWorkspace,'filter_rows',broken)
                # Qt retains the bound callback connected before this call hook.
                widget=item.funcargs['populated'].workspace.evidence
                signal=widget.filters['detector'].currentIndexChanged
                signal.disconnect()
                signal.connect(lambda index:broken(widget))

        @pytest.hookimpl(trylast=True)
        def pytest_runtest_teardown(self,item):
            self.patch.undo()

        def pytest_runtest_logreport(self,report):
            if report.when=='call' and report.failed:
                self.failed.append({'nodeid':report.nodeid,'assertion_failure':
                    'assert ' in report.longreprtext or 'AssertionError' in report.longreprtext})
            elif report.failed:self.errors.append(report.nodeid)

    fault=Fault()
    temp=runpy.run_path(str(ROOT/'doc/gui_modernization/ui4/run_validation.py'),run_name='test_temp_support')['TempPlugin']()
    result=pytest.main(['-p','no:cacheprovider','-q',PROBES[name]],plugins=[temp,fault])
    confirmed=result==1 and bool(fault.failed) and all(row['assertion_failure'] for row in fault.failed) and not fault.errors
    output={'probe':name,'target':PROBES[name],'detected_by_retained_assertion':confirmed,
            'pytest_exit':int(result),'failures':fault.failed,'setup_teardown_errors':fault.errors}
    print('RETENTION_RESULT '+json.dumps(output))
    return 0 if confirmed else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe',choices=PROBES)
    args=parser.parse_args()
    if args.probe:raise SystemExit(run_probe(args.probe))
    results=[]
    for name in PROBES:
        process=subprocess.run([sys.executable,__file__,'--probe',name],cwd=ROOT,capture_output=True,text=True)
        lines=[line.removeprefix('RETENTION_RESULT ') for line in process.stdout.splitlines() if line.startswith('RETENTION_RESULT ')]
        if not lines:
            raise SystemExit('Probe did not finish: '+name+'\n'+process.stdout+process.stderr)
        row=json.loads(lines[-1])
        results.append(row)
        print(name+': '+('detected' if row['detected_by_retained_assertion'] else 'NOT DETECTED'),flush=True)
    output=ROOT/'doc/test_quality/fault_injection_results.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(results,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(row['detected_by_retained_assertion'] for row in results) else 1)
