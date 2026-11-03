"""Validate final reference behavior against UI-1, without changing inputs."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from signallens_controller import SignalLensController
from signallens_settings import load_settings
from summary_synthesizer import build_summary_result
from investigation_session import InvestigationSession
from investigation_presenters import build_presentation

baseline = json.loads((OUT.parent/'ui1/reference_after.json').read_text())
results = {}
for case, before in baseline.items():
    source = ROOT/before['source']
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    directory = OUT/'reference_runs'/case
    state = SignalLensController(settings_snapshot=load_settings()).run_analysis(source, directory, directory/f'{source.stem}_exif_signals.json')
    summary = build_summary_result(state)
    trace = summary.reasoning_trace
    session = InvestigationSession.selected(source)
    invocation = session.begin_analysis('normal', {}, load_settings(), directory)
    session.complete(invocation, state, summary)
    view = build_presentation(session)
    result = {'suspicious_score': trace['scorecard']['suspicious_score'], 'benign_score': trace['scorecard']['benign_score'],
              'pattern': summary.overall_pattern, 'confidence': summary.overall_confidence,
              'hypotheses': trace['hypothesis_assessments'], 'sha256': digest,
              'source_unchanged': digest == hashlib.sha256(source.read_bytes()).hexdigest(),
              'coverage_counts': state.analysis_coverage.get('stage_counts'),
              'presentation_tiers_preserved': all(h.confidence_tier == raw['confidence_tier'] for h,raw in zip(view.hypotheses, trace['hypothesis_assessments'], strict=True))}
    for key in ('suspicious_score','benign_score','pattern','confidence','hypotheses'):
        assert result[key] == before[key], (case,key)
    assert digest == before['sha256_after'] and result['source_unchanged'] and result['presentation_tiers_preserved']
    results[case] = result
(OUT/'reference_verification.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print({case: (values['suspicious_score'],values['benign_score'],values['confidence']) for case,values in results.items()})
