"""Final UI-2 artifact, preservation and regression evidence validation."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
baseline = json.loads((OUT/'inherited_baseline.json').read_text(encoding='utf-8'))
allowed = {'.gitignore', 'signallens_gui.py', 'settings_dialog.py', 'osint_dialogs.py'}
changed = sorted(name for name, digest in baseline['hashes'].items()
                 if not (ROOT/name).is_file() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest)
new_source = ['gui_design_system.py','gui_components.py','gui_workspace.py','gui_workspace_state.py','tests/test_workspace_shell.py']
for name in new_source + sorted(allowed - {'.gitignore'}):
    ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))
suite = ET.parse(OUT/'regression_results.xml').getroot().find('testsuite')
tests = {key:int(suite.attrib[key]) for key in ('tests','failures','errors','skipped')}
documents = ['design_system_specification.md','workspace_architecture.md','component_inventory.md',
             'legacy_migration_map.md','visual_validation.md','implementation_report.md',
             'regression_results.md','score_baseline_diagnostic.md']
captures = []
for path in sorted((OUT/'screenshots').iterdir()):
    if path.suffix.lower() not in ('.jpg','.png'):
        continue
    with Image.open(path) as image:
        captures.append({'file': path.name, 'width':image.width, 'height':image.height, 'format':image.format,
                         'capture': 'native Windows' if 'native_' in path.name else 'offscreen Qt'})
(OUT/'screenshot_manifest.json').write_text(json.dumps(captures,indent=2),encoding='utf-8')
ui1 = ['analysis_worker.py','signallens_controller.py','summary_persistence.py','investigation_session.py',
       'investigation_presenters.py','investigation_workers.py','investigation_reports.py','presentation_models.py']
result = {
    'branch': subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
    'head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'ui2_existing_files_changed': changed, 'unexpected_inherited_changes': sorted(set(changed)-allowed),
    'new_ui2_source_files':new_source, 'ui1_core_modules_unchanged':all(name not in changed for name in ui1),
    'inherited_test_files_unchanged': all(not name.startswith('tests/') for name in changed),
    'inherited_documents_unchanged':all(not name.startswith('doc/') for name in changed),
    'settings_and_dependencies_unchanged':all(name not in changed for name in ('signallens_settings.json','DEPENDENCIES.md')),
    'required_documents_present':all((OUT/name).is_file() for name in documents),
    'tests':tests, 'offscreen_captures':sum(c['capture']=='offscreen Qt' for c in captures),
    'native_captures':sum(c['capture']=='native Windows' for c in captures),
    'reference_verification_present':(OUT/'reference_verification.json').is_file(),
    'staged_diff':subprocess.check_output(['git','diff','--cached','--stat'],cwd=ROOT,text=True).strip(),
    'git_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True).splitlines(),
    'whitespace_check':subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True).returncode,
}
(OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
assert not result['unexpected_inherited_changes']
assert result['head']==baseline['head'] and result['branch']==baseline['branch']
assert tests == {'tests':406,'failures':0,'errors':0,'skipped':0}
assert result['required_documents_present'] and result['reference_verification_present']
assert result['native_captures']==5 and result['offscreen_captures']==13
assert not result['staged_diff'] and result['whitespace_check']==0
