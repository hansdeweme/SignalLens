"""Read-only acceptance probes; artifacts are confined to ignored analyzed/."""
import contextlib
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from signallens_controller import SignalLensController
from summary_synthesizer import build_summary_result
from summary_persistence import persist_summary_result
from reasoning_persistence import persist_reasoning_trace, persist_reasoning_trace_text

OUT = ROOT / 'analyzed/phase2b4_validation'
CASES = {
    'instagram': 'test_images/insta_fake/Curvy Leggings Outfit.jpg',
    'midjourney': 'test_images/midjourney/theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png',
}


def independent_replay(t):
    # No production arithmetic helper is imported or called here.
    c = t['scorecard_calculation']
    close = lambda a, b: math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
    weights = {'weak': .5, 'medium': 1.5, 'strong': 3.0}
    bases = {}
    for polarity in ['suspicious', 'benign']:
        rows = [r for r in c['base_evidence'] if r['polarity'] == polarity]
        assert all(r['weight'] == weights[r['status']] for r in rows)
        domains = {r['domain'] for r in rows if r['domain'] and r['credited_weight'] > 0}
        bases[polarity] = math.fsum(r['credited_weight'] for r in rows) + .25 * max(0, len(domains)-1)
        assert close(bases[polarity], c['base_' + polarity])
    components = dict.fromkeys(c['raw_contributions'], 0.)
    n = c['raw_operation_count']
    if n == 0:
        assert components == c['raw_contributions']
    for i, op in enumerate(c['component_operations'], 1):
        key, v = op['field'], op['operand']
        if op['operation'] == 'add': components[key] += v
        elif op['operation'] == 'multiply': components[key] *= v
        elif op['operation'] == 'maximum': components[key] = max(components[key], v)
        else: raise AssertionError(op)
        if i == n:
            assert all(close(v, c['raw_contributions'][k]) for k, v in components.items())
    assert all(close(v, c['final_contributions'][k]) and close(v, t['scorecard'][k]) for k, v in components.items())
    a, tr = c['reliability_adjustments'], c['aggregate_transforms']
    raw = c['raw_contributions']
    applicable = raw['local_edit_support_score'] > 0 or raw['edit_boost'] > 0
    assert a['boundary_adjustment_applicable'] == applicable
    expected = []
    for field in ['local_edit_support_score', 'edit_boost']:
        if a['region_geometry_unreliable']: expected.append((field, 'region_geometry_reliability', .45))
        if applicable and a['boundary_reliability'] < 1: expected.append((field, 'boundary_reliability', a['boundary_reliability']))
    actual = [(o['field'], o['reason'], o['operand']) for o in c['component_operations'] if o['reason'] in ['region_geometry_reliability', 'boundary_reliability']]
    assert sorted(actual) == sorted(expected)
    measured = tr['measured_camera_support']
    m = .55 if measured >= 3 else .7 if measured >= 2 else .85 if measured >= 1 else 1.
    g = .75 if a['region_geometry_unreliable'] else 1.
    p = .7 if tr['photo_context_prior'] else 1.
    assert (tr['camera_multiplier'], tr['geometry_multiplier'], tr['photo_context_multiplier']) == (m, g, p)
    q = math.fsum([bases['suspicious']] + [components[k] for k in ['synthetic_boost', 'edit_boost', 'provenance_boost', 'sensor_boost', 'compression_boost']])
    suspicious = max(0., q*m-components['caution_penalty'])*g*p
    assert close(suspicious, t['scorecard']['suspicious_score'])
    assert close(bases['benign'], t['scorecard']['benign_score'])
    assert all(close(t['scorecard'][k], c['aggregate_scores'][k]) for k in ['suspicious_score', 'benign_score'])
    return dict(base_suspicious=bases['suspicious'], base_benign=bases['benign'], subtotal=q,
                camera_multiplier=m, penalty=components['caution_penalty'], geometry_multiplier=g,
                photo_context_multiplier=p, suspicious=suspicious, benign=bases['benign'],
                raw_final_replay=True, reliability_operations_once=True)


results = {}
for name, relative in CASES.items():
    image = ROOT / relative
    before = hashlib.sha256(image.read_bytes()).hexdigest()
    out = OUT / name
    out.mkdir(parents=True, exist_ok=True)
    with (out/'console.txt').open('w', encoding='utf-8') as console:
        with contextlib.redirect_stdout(console), contextlib.redirect_stderr(console):
            state = SignalLensController().run_analysis(image, out, out/'exif_signals.json', analysis_mode='subject_based')
            plain = build_summary_result(state)
            shadow = build_summary_result(state, evidence_dependency_shadow=True)
            repeated = build_summary_result(state)
            assert plain.reasoning_trace == repeated.reasoning_trace
            for key in ['scorecard', 'decision', 'hypothesis_assessments', 'confidence_policy', 'corroboration_audit']:
                assert plain.reasoning_trace[key] == shadow.reasoning_trace[key], key
            persist_summary_result(plain, out)
            persist_reasoning_trace(shadow.reasoning_trace, out)
            persist_reasoning_trace_text(shadow.reasoning_trace, out)
    assert before == hashlib.sha256(image.read_bytes()).hexdigest()
    t = plain.reasoning_trace
    baseline = json.loads((ROOT/f'analyzed/phase3_validation/{name}/summary/reasoning_trace.json').read_text(encoding='utf-8'))
    results[name] = dict(image_sha256=before, image_unchanged=True,
        stages=dict(Counter(s['status'] for s in state.stage_statuses.values())), errors=state.errors,
        coverage=state.analysis_coverage, mask=state.mask_diagnostics,
        decision=t['decision'], confidence_policy=t['confidence_policy'],
        hypotheses=t['hypothesis_assessments'], math=independent_replay(t), numerical_deduplication=t['scorecard_calculation']['numerical_deduplication'], base_evidence=t['scorecard_calculation']['base_evidence'], scorecard=t['scorecard'], route_trace=t['decision_route_trace'],
        baseline_scores_equal=all(t['scorecard'][k] == baseline['scorecard'][k] for k in ['suspicious_score','benign_score']),
        shadow_production_equal=True, repeated_summary_deterministic=True,
        rendered_confidence_present=plain.overall_confidence in plain.full_text and plain.overall_confidence in plain.full_html)
    (OUT/'reference_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(name, json.dumps({k: results[name][k] for k in ['stages','errors','math','baseline_scores_equal','shadow_production_equal']}), flush=True)
