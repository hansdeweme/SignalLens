"""Bounded replay of recorded sections; no detector/scoring changes or tuning."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from PIL import Image
from gui_semantics import ModuleSummary
from decision_logic import synthesize_overall

def pixels(path):
    with Image.open(path) as image:
        rgb = image.convert('RGB')
        return {'size': list(rgb.size), 'rgb_sha256': hashlib.sha256(rgb.tobytes()).hexdigest()}

record = {}
for case in ('instagram', 'midjourney'):
    old_root = ROOT/'doc/final_acceptance_audit'/case
    new_summary = next((ROOT/'doc/gui_modernization/ui1/reference_after'/case).rglob('summary/final_summary.json'))
    new_root = new_summary.parent.parent
    old = json.loads((old_root/'summary/final_summary.json').read_text(encoding='utf-8'))
    new = json.loads(new_summary.read_text(encoding='utf-8'))
    trace = old['reasoning_trace']
    replay = synthesize_overall({key: ModuleSummary(**value) for key,value in old['sections'].items()},
        analysis_mode=trace.get('analysis_mode'), analysis_coverage=trace.get('pipeline_status',{}).get('coverage'))
    image_comparison = {}
    for path in (old_root/'prepared_images').glob('*.png'):
        corresponding = new_root/'prepared_images'/path.name
        if corresponding.is_file():
            image_comparison[path.name] = {'historical': pixels(path), 'ui1': pixels(corresponding),
                                            'equal': pixels(path) == pixels(corresponding)}
    old_patch = json.loads((old_root/'patch_similarity_results.json').read_text())['patch_similarity']
    new_patch = json.loads((new_root/'patch_similarity_results.json').read_text())['patch_similarity']
    record[case] = {
        'historical_mode': trace.get('analysis_mode'), 'ui1_mode': new['reasoning_trace'].get('analysis_mode'),
        'historical_saved_suspicious': trace['scorecard']['suspicious_score'],
        'historical_sections_current_reasoning_replay': replay[4]['scorecard']['suspicious_score'],
        'ui1_normal_suspicious': new['reasoning_trace']['scorecard']['suspicious_score'],
        'historical_patch_size': old_patch.get('patch_size'), 'ui1_patch_size': new_patch.get('patch_size'),
        'historical_patch_pair_count': old_patch.get('pair_count'), 'ui1_pair_count': new_patch.get('pair_count'),
        'prepared_pixel_comparison': image_comparison,
        'replay_ledger': replay[4]['scorecard_calculation'],
        'historical_coverage_counts': trace.get('pipeline_status',{}).get('coverage',{}).get('stage_counts'),
        'ui1_coverage_counts': new['reasoning_trace'].get('pipeline_status',{}).get('coverage',{}).get('stage_counts'),
        'historical_raw_source_sha256': 'not recorded in the inspected historical manifests',
    }
(OUT/'score_profile_replay.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
for case, data in record.items():
    print(case, {key:value for key,value in data.items() if key not in ('replay_ledger','prepared_pixel_comparison')})
    print('Prepared pixel equality:', {key:value['equal'] for key,value in data['prepared_pixel_comparison'].items()})
