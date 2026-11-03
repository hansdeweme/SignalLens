"""Read-only source index and preservation check for UI-0. Writes only here."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
index = {}
for path in sorted(ROOT.glob('*.py')):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    index[path.name] = {
        'classes': [{'name': n.name, 'line': n.lineno,
                     'bases': [ast.unparse(b) for b in n.bases],
                     'methods': {m.name: m.lineno for m in n.body if isinstance(m, ast.FunctionDef)}}
                    for n in tree.body if isinstance(n, ast.ClassDef)],
        'functions': {n.name: n.lineno for n in tree.body if isinstance(n, ast.FunctionDef)},
        'imports': [ast.unparse(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))],
    }
(OUT / 'source_index.json').write_text(json.dumps(index, indent=2), encoding='utf-8')
baseline = json.loads((OUT / 'protected_baseline.json').read_text(encoding='utf-8'))
changed = [name for name, digest in baseline.items()
           if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
(OUT / 'preservation_check.json').write_text(json.dumps({'tracked_files_checked': len(baseline), 'changed_since_audit_start': changed}, indent=2), encoding='utf-8')
print(f'Indexed {len(index)} source modules; changed protected files: {changed}')
