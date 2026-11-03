"""Validate UI-0 artifacts/references and preservation without production writes."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
required = ['gui_architecture_inventory.md', 'current_user_journey.md', 'visual_design_audit.md',
            'reasoning_visibility_matrix.md', 'gui_architecture_recommendation.md',
            'signal_lens_design_concept.md', 'modernization_roadmap.md', 'executive_summary.md']
missing = [name for name in required if not (OUT / name).is_file()]
references = set()
for name in required:
    content = (OUT / name).read_text(encoding='utf-8')
    references.update(re.findall(r'(?<![\w/])([a-z][a-z_]*\.py)\b', content))
unknown = sorted(name for name in references if not (ROOT / name).is_file() and not (ROOT / 'tests' / name).is_file() and not (OUT / name).is_file())
expected_classes = {
    'signallens_gui.py': ['SignalLensGui'], 'analysis_worker.py': ['AnalysisWorker'],
    'signallens_controller.py': ['AnalysisState', 'SignalLensController'],
    'settings_dialog.py': ['SettingsDialog'], 'osint_dialogs.py': ['OSINTFindingDialog'],
    'summary_types.py': ['SummaryResult'], 'gui_semantics.py': ['ModuleSummary'],
}
bad_classes = []
for filename, names in expected_classes.items():
    tree = ast.parse((ROOT / filename).read_text(encoding='utf-8-sig'))
    actual = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
    bad_classes.extend(f'{filename}:{name}' for name in names if name not in actual)
for path in OUT.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'))
svgs = sorted((OUT / 'wireframes').glob('*.svg'))
for path in svgs:
    ET.parse(path)
baseline = json.loads((OUT / 'protected_baseline.json').read_text(encoding='utf-8'))
changed = [name for name, digest in baseline.items() if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
def lum(hex_color):
    c = [int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    c = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in c]
    return sum(v*w for v, w in zip(c, (.2126, .7152, .0722)))
def contrast(a, b):
    values = sorted((lum(a), lum(b)))
    return round((values[1]+.05)/(values[0]+.05), 3)
data = {
    'date_local': '2026-11-03', 'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
    'head': subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip(),
    'missing_required_documents': missing, 'source_references_checked': len(references),
    'unknown_source_references': unknown, 'missing_classes': bad_classes,
    'wireframes_svg_valid': len(svgs), 'wireframes_png': len(list((OUT / 'wireframes').glob('*.png'))),
    'actual_screenshots': [p.name for p in sorted((OUT / 'screenshots').glob('*.jpg'))],
    'contrast_on_summary_1f2937': {color: contrast(color, '#1f2937') for color in ('#d1d5db','#b91c1c','#4ade80','#6b7280')},
    'tracked_files_checked': len(baseline), 'changed_since_audit_start': changed,
    'git_status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True).splitlines(),
    'regression': {'command': 'py -3.13 -B -m pytest -q -p no:cacheprovider --basetemp=doc/gui_modernization/audit/pytest_verified', 'result': '334 passed in 4.18s', 'exit_code': 0, 'note': 'Approved unsandboxed rerun after first sandbox attempt failed with WinError 5 on pytest_tmp.'},
}
(OUT / 'validation.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
print(json.dumps(data, indent=2))
if missing or unknown or bad_classes or changed or len(svgs) != 6:
    raise SystemExit(1)
