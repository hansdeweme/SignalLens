"""Bounded read-only score comparison and inherited-work inventory for UI-2."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
paths = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')) - {''}
paths.update(str(p.relative_to(ROOT)).replace('\\', '/') for p in ROOT.glob('*.py'))
paths.update(str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / 'tests').glob('*.py'))
for folder in ('audit', 'ui1'):
    paths.update(str(p.relative_to(ROOT)).replace('\\', '/') for p in (OUT.parent / folder).glob('*') if p.is_file())
baseline = {'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
            'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True).splitlines(),
            'hashes': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(paths) if (ROOT/name).is_file()}}
(OUT / 'inherited_baseline.json').write_text(json.dumps(baseline, indent=2), encoding='utf-8')
comparison = {}
for case in ('instagram', 'midjourney'):
    old_path = ROOT / 'doc/final_acceptance_audit' / case / 'summary/final_summary.json'
    new_path = next((ROOT / 'doc/gui_modernization/ui1/reference_after' / case).rglob('final_summary.json'))
    old = json.loads(old_path.read_text(encoding='utf-8'))
    new = json.loads(new_path.read_text(encoding='utf-8'))
    ot, nt = old['reasoning_trace'], new['reasoning_trace']
    differences = {key: {'historical': ot['scorecard'].get(key), 'ui1': nt['scorecard'].get(key)}
                   for key in set(ot['scorecard']) | set(nt['scorecard']) if ot['scorecard'].get(key) != nt['scorecard'].get(key)}
    sections = {key: {'historical': ot['section_snapshot'].get(key), 'ui1': nt['section_snapshot'].get(key)}
                for key in set(ot['section_snapshot']) | set(nt['section_snapshot'])
                if ot['section_snapshot'].get(key) != nt['section_snapshot'].get(key)}
    comparison[case] = {
        'historical_path': str(old_path.relative_to(ROOT)), 'ui1_path': str(new_path.relative_to(ROOT)),
        'historical_mode': ot.get('analysis_mode'), 'ui1_mode': nt.get('analysis_mode'),
        'historical_context': ot.get('context'), 'ui1_context': nt.get('context'),
        'historical_stages': ot.get('pipeline_status'), 'ui1_stages': nt.get('pipeline_status'),
        'scorecard_differences': differences, 'section_differences': sections,
        'historical_calculation': ot.get('scorecard_calculation'), 'ui1_calculation': nt.get('scorecard_calculation'),
    }
(OUT / 'score_diagnostic_data.json').write_text(json.dumps(comparison, indent=2), encoding='utf-8')
for case, data in comparison.items():
    print(case, json.dumps(data['scorecard_differences'], indent=2))
    print('section differences:', list(data['section_differences']))
