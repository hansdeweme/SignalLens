"""Read the outputs of the actual native portable run; no detectors execute here."""
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
root=OUT/'validation_output/packaged_runs'
refs=json.loads((OUT.parent/'ui3/reference_verification.json').read_text())
ref=refs['instagram']
original_pointer=Path(ref['report_pointer'])
original=json.loads((original_pointer.parent/json.loads(original_pointer.read_text())['summary']).read_text(encoding='utf-8'))
exports=[]
for pointer in (root/'exports').rglob('current_report.json'):
    info=json.loads(pointer.read_text());summary=pointer.parent/info['summary']
    data=json.loads(summary.read_text(encoding='utf-8'))
    assert data['reasoning_trace']==original['reasoning_trace']
    assert summary.with_suffix('.html').exists() and summary.with_suffix('.txt').exists()
    exports.append({'result_id':info['investigation']['result_id'],'annotation_revision':info['investigation']['annotation_revision'],
        'forensic_trace_matches_stored_reference':True,'html_txt_json_exist':True})
assert exports
run_path=next((root/'Curvy Leggings Outfit').rglob('analysis_run.json'))
run=json.loads(run_path.read_text())
counts=dict(Counter(s['status'] for s in run['stages']))
assert run['status']=='completed' and counts=={'success':23}
assert run['artifacts']['investigation']['source_sha256']==ref['sha256']
assert run['artifacts']['investigation']['profile']=='normal'
mask=run['diagnostics']['mask']
assert mask['backend']=='mediapipe_tasks_image_segmenter' and not mask['fallback_used']
info=json.loads((run_path.parent/'current_report.json').read_text())
data=json.loads((run_path.parent/info['summary']).read_text(encoding='utf-8'))
trace=data['reasoning_trace']
assert trace['scorecard']['suspicious_score']==ref['suspicious_score']
assert trace['scorecard']['benign_score']==ref['benign_score']
assert trace['decision']['dominant_pattern']==ref['pattern']
result={'platform':'native Windows portable executable','launch':'PASS','stored_load_preview_export':'PASS',
    'exports':exports,'reanalyzed_source_sha256':ref['sha256'],'reanalysis_status':run['status'],'stage_counts':counts,
    'elapsed_timestamp_seconds':(datetime.fromisoformat(run['finished_at'])-datetime.fromisoformat(run['started_at'])).total_seconds(),
    'mask_backend':mask['backend'],'mask_fallback_used':mask['fallback_used'],'scorecard':{k:trace['scorecard'][k] for k in ('suspicious_score','benign_score')},
    'dominant_pattern':trace['decision']['dominant_pattern'],'confidence':trace['decision']['confidence_tier'],
    'shutdown':'See native desktop close observation in packaging_validation.md'}
(OUT/'packaged_runtime_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
