"""Read-only final UI-1 preservation, test and reference evidence checks."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
baseline = json.loads((OUT / 'baseline.json').read_text(encoding='utf-8'))
allowed = {'.gitignore', 'analysis_worker.py', 'signallens_controller.py', 'signallens_gui.py', 'summary_persistence.py'}
changed = [name for name, old in baseline['sha256'].items()
           if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != old]
unexpected = sorted(set(changed) - allowed)
syntax = []
for path in list(ROOT.glob('investigation_*.py')) + [ROOT / 'presentation_models.py'] + [ROOT / p for p in allowed if p.endswith('.py')] + list((ROOT / 'tests').glob('test_investigation_*.py')):
    ast.parse(path.read_text(encoding='utf-8-sig'))
    syntax.append(str(path.relative_to(ROOT)))
suite = ET.parse(OUT / 'regression_results.xml').getroot().find('testsuite')
tests = {key: int(suite.attrib[key]) for key in ('tests', 'failures', 'errors', 'skipped')}
comparison = json.loads((OUT / 'reference_comparison.json').read_text(encoding='utf-8'))
required = ['session_lifecycle_specification.md', 'presentation_contracts.md', 'osint_report_consistency.md',
            'implementation_report.md', 'regression_results.md']
engine = ['hypothesis_engine.py', 'decision_logic.py', 'confidence_policy.py', 'hypothesis_evidence.py',
          'metadata_evidence.py', 'numerical_evidence.py', 'evidence_lineage.py', 'production_corroboration.py']
status = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True).splitlines()
result = {
    'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'baseline_head_unchanged': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == baseline['head'],
    'tracked_files_changed_by_ui1': sorted(changed), 'unexpected_tracked_changes': unexpected,
    'inherited_modified_docx_preserved': 'doc/SignalLens - Modernizing the Forensic Reasoning Engine.docx' not in changed,
    'reasoning_modules_unchanged': all(path not in changed for path in engine),
    'original_test_files_unchanged': all(not name.startswith('tests/') for name in changed),
    'syntax_checked': syntax, 'tests': tests, 'reference_equivalence': comparison,
    'required_documents_present': all((OUT / name).is_file() for name in required),
    'staged_diff': subprocess.check_output(['git', 'diff', '--cached', '--stat'], cwd=ROOT, text=True).strip(),
    'git_status': status,
}
(OUT / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
assert not unexpected and result['baseline_head_unchanged']
assert tests == {'tests': 378, 'failures': 0, 'errors': 0, 'skipped': 0}
assert all(all(checks.values()) for checks in comparison.values())
assert result['required_documents_present'] and not result['staged_diff']
