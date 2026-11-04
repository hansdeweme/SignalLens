"""Collect per-node pytest inventory and measured timings with no dependencies.

Use --output doc/test_quality/baseline.json (or final.json), followed by pytest
arguments. Reuses the established sandbox temporary-directory runner unchanged.
"""
import argparse
import ast
from collections import Counter
import inspect
import json
from pathlib import Path
import runpy
import sys
import time
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

DOMAINS = {
    'test_mask_pipeline':'Forensic detectors and signal extraction',
    'test_reasoning':'Reasoning and hypothesis selection',
    'test_hypothesis_scoping':'Reasoning and hypothesis selection',
    'test_scorecard_integrity':'Scorecard calculation',
    'test_numerical_evidence':'Scorecard calculation',
    'test_evidence_lineage':'Evidence lineage and corroboration',
    'test_production_corroboration':'Evidence lineage and corroboration',
    'test_confidence_policy':'Confidence policy',
    'test_investigation_contracts':'Investigation sessions',
    'test_investigation_gui':'Worker lifecycle',
    'test_workspace_shell':'GUI navigation and state',
    'test_overview_workspace':'GUI navigation and state',
    'test_forensic_workspace':'Image artifact viewing',
    'test_explorer_workspace':'Evidence and Reasoning explorers',
    'test_provenance_reporting':'OSINT and report consistency',
}


def domain(module,name):
    if any(token in name for token in ('legacy','stored','load_saved','loaded_summary','corrupted_import','new_report_load')):
        return 'Stored-result compatibility'
    if any(token in name for token in ('report','annotation','osint','export')):
        return 'OSINT and report consistency'
    if module=='test_overview_workspace' and any(token in name for token in ('preview','decode','source_monitor','unavailable_source')):
        return 'Image artifact viewing'
    return DOMAINS.get(module,'Unclassified')


class ReportPlugin:
    def __init__(self,path):
        self.path=path
        self.rows={}
        self.warnings=[]
        self.started=time.perf_counter()

    def pytest_collection_modifyitems(self,items):
        for item in items:
            obj=item.obj
            source=inspect.getsource(obj)
            tree=ast.parse(textwrap.dedent(source))
            calls=tuple(dict.fromkeys(ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n,ast.Call)))
            asserts=tuple(ast.unparse(n.test) for n in ast.walk(tree) if isinstance(n,ast.Assert))
            module=Path(str(item.path)).stem
            fixtures=[]
            for name in item.fixturenames:
                definitions=item._fixtureinfo.name2fixturedefs.get(name,())
                func=definitions[-1].func if definitions else None
                location=inspect.getsourcefile(func) if func else None
                fixtures.append({'name':name,'source':str(Path(location).relative_to(ROOT)) if location and Path(location).is_relative_to(ROOT) else location})
            self.rows[item.nodeid]={'nodeid':item.nodeid,'module':str(item.path.relative_to(ROOT)),
                'group':item.originalname or item.name,'line':item.location[1]+1,
                'domain':domain(module,item.originalname or item.name),
                'category':'GUI integration' if 'window' in item.fixturenames else 'GUI unit' if 'app' in item.fixturenames else
                           'reference regression' if 'reference' in item.name or 'trace_regression' in item.name else 'unit/integration',
                'requirement':(item.originalname or item.name).removeprefix('test_').replace('_',' '),
                'calls':calls,'assertions':asserts,'fixtures':fixtures,'duration':0.0,'phases':{},'outcome':'not run'}

    def pytest_runtest_logreport(self,report):
        if report.nodeid not in self.rows:return
        row=self.rows[report.nodeid]
        row['duration']+=report.duration
        row['phases'][report.when]={'outcome':report.outcome,'duration':report.duration}
        if report.when=='call' or report.failed or report.skipped:row['outcome']=report.outcome

    def pytest_warning_recorded(self,warning_message,when,nodeid,location):
        self.warnings.append({'message':str(warning_message.message),'when':when,'nodeid':nodeid})

    def pytest_sessionfinish(self,session,exitstatus):
        rows=list(self.rows.values())
        self.path.parent.mkdir(parents=True,exist_ok=True)
        result={'collected':len(rows),'outcomes':dict(Counter(row['outcome'] for row in rows)),
            'duration_seconds':time.perf_counter()-self.started,'exitstatus':int(exitstatus),
            'warnings':self.warnings,'module_counts':dict(Counter(row['module'] for row in rows)),
            'domain_counts':dict(Counter(row['domain'] for row in rows)),
            'slowest':sorted(({'nodeid':row['nodeid'],'duration':row['duration']} for row in rows),key=lambda row:-row['duration'])[:20],
            'tests':rows}
        self.path.write_text(json.dumps(result,indent=2),encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args,pytest_args=parser.parse_known_args()
    import pytest
    temp=runpy.run_path(str(ROOT/'doc/gui_modernization/ui4/run_validation.py'),run_name='test_temp_support')['TempPlugin']()
    raise SystemExit(pytest.main(['-p','no:cacheprovider',*(pytest_args or ['tests','-q']),
        '--durations=15'],plugins=[temp,ReportPlugin(args.output)]))
