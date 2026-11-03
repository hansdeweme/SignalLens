"""Read-only input verification; all generated outputs stay under UI-1."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from signallens_controller import SignalLensController
from summary_synthesizer import build_summary_result
from summary_persistence import persist_summary_result
from dataclasses import asdict
from investigation_session import InvestigationSession
from investigation_presenters import build_presentation
from investigation_reports import create_report_snapshot, persist_report_snapshot
from signallens_settings import load_settings

label = sys.argv[1]
references = {
    'instagram': 'test_images/insta_fake/Curvy Leggings Outfit.jpg',
    'midjourney': 'test_images/midjourney/theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png',
}
results = {}
for name, relative in references.items():
    source = ROOT / relative
    if not source.is_file():
        results[name] = {'unavailable': relative}
        continue
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    output = Path(__file__).parent / f'reference_{label}' / name
    settings = load_settings()
    session = InvestigationSession.selected(source)
    session.source_sha256 = digest
    invocation = session.begin_analysis('normal', {}, settings, output)
    if label == 'after':
        output = Path(invocation.output_dir)
    controller = SignalLensController(settings_snapshot=settings) if label == 'after' else SignalLensController()
    state = controller.run_analysis(source, output, output / f'{source.stem}_exif_signals.json')
    summary = build_summary_result(state)
    persist_summary_result(summary, output)
    trace = summary.reasoning_trace
    if label == 'after':
        assert session.complete(invocation, state, summary)
        before_projection = session.summary_json
        view = build_presentation(session)
        for assessment, projected in zip(trace['hypothesis_assessments'], view.hypotheses, strict=True):
            assert projected.hypothesis_id == assessment['hypothesis_id']
            assert projected.confidence_tier == assessment['confidence_tier']
            for role in ('supporting_evidence', 'contradicting_evidence', 'moderating_evidence', 'contextual_evidence'):
                assert getattr(projected, role) == tuple(assessment[role])
        assert view.summary.confidence_tier == summary.overall_confidence
        assert view.summary.primary_hypothesis == trace['decision']['primary_hypothesis']
        assert [(s.stage_id, s.status, s.reason) for s in view.stages] == [
            (name, values['status'], values.get('reason')) for name, values in sorted(state.stage_statuses.items())]
        report = create_report_snapshot(session)
        assert report.payload()['investigation']['image_path'] == str(source.resolve())
        assert report.payload()['investigation']['analysis_id'] == invocation.analysis_id
        assert report.payload()['reasoning_trace'] == trace
        persist_report_snapshot(session, report, output)
        assert session.summary_json == before_projection
        (output / 'presentation_snapshot.json').write_text(json.dumps(asdict(view), indent=2), encoding='utf-8')
    results[name] = {
        'source': relative, 'sha256_before': digest,
        'sha256_after': hashlib.sha256(source.read_bytes()).hexdigest(),
        'suspicious_score': trace['scorecard']['suspicious_score'],
        'benign_score': trace['scorecard']['benign_score'],
        'pattern': summary.overall_pattern, 'confidence': summary.overall_confidence,
        'hypotheses': trace['hypothesis_assessments'],
        'coverage': state.analysis_coverage,
    }
target = Path(__file__).parent / f'reference_{label}.json'
target.write_text(json.dumps(results, indent=2), encoding='utf-8')
if label == 'after':
    before = json.loads((Path(__file__).parent / 'reference_before.json').read_text(encoding='utf-8'))
    comparison = {}
    for name, result in results.items():
        keys = ('suspicious_score', 'benign_score', 'pattern', 'confidence', 'hypotheses', 'sha256_before', 'sha256_after')
        comparison[name] = {key: before[name].get(key) == result.get(key) for key in keys}
        assert all(comparison[name].values()), (name, comparison[name])
    (Path(__file__).parent / 'reference_comparison.json').write_text(json.dumps(comparison, indent=2), encoding='utf-8')
print(json.dumps({k: {f:v for f,v in r.items() if f not in ('hypotheses',)} for k,r in results.items()}, indent=2))
