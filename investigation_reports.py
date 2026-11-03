"""Revision-bound reports and non-destructive legacy loading.

Existing SummaryResult fields and serializers remain compatible. Current OSINT
annotations are an explicitly separate appendix; post-run edits never synthesize
new scores, hypotheses or confidence.
"""
from __future__ import annotations
from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
from uuid import uuid4

from investigation_session import (
    AnalysisInvocation, InvestigationSession, InvestigationState, json_snapshot,
)
from reasoning_persistence import persist_reasoning_trace, persist_reasoning_trace_text
from summary_persistence import persist_summary_result


def annotations_object(data):
    """Restore the existing OSINT types without touching a file or the engine."""
    if data is None:
        return None
    from dataclasses import fields
    from osint_reverse_search import ReverseSearchResult, ReverseSearchMatch, ReverseSearchQueryLinks
    if not isinstance(data, dict):
        raise ValueError('Invalid OSINT annotation record.')
    values = {f.name: data[f.name] for f in fields(ReverseSearchResult) if f.name in data}
    values['matches'] = [ReverseSearchMatch(**m) for m in data.get('matches', [])]
    values['query_links'] = ReverseSearchQueryLinks(**data.get('query_links', {}))
    return ReverseSearchResult(**values)


@dataclass(frozen=True)
class ReportSnapshot:
    session_id: str
    result_id: str
    annotation_revision: int
    payload_json: str

    def payload(self) -> dict:
        return json.loads(self.payload_json)


def forensic_html(data: dict) -> str:
    """Render recorded legacy text literally when no HTML was stored."""
    return data.get('full_html') or '<pre>' + escape(data.get('full_text') or '') + '</pre>'


def annotation_appendix(session: InvestigationSession) -> tuple[str, str]:
    annotations = json.loads(session.annotations_json)
    text = ('Current OSINT annotations — separate from frozen forensic findings\n'
            f'Session: {session.session_id}\nResult: {session.result_id}\n'
            f'Annotation revision: {session.annotation_revision}\n'
            'Post-analysis annotation changes are not incorporated into forensic scores or confidence.\n'
            + json.dumps(annotations, ensure_ascii=False, indent=2))
    return text, '<h3>Current OSINT annotations</h3><pre>' + escape(text) + '</pre>'


def create_report_snapshot(session: InvestigationSession) -> ReportSnapshot:
    if session.state != InvestigationState.COMPLETED or not session.summary_json or not session.result_id:
        raise ValueError('A completed active result is required for report export.')
    data = session.summary_data()
    invocation = session.invocation
    data['investigation'] = {
        'schema_version': 1, 'session_id': session.session_id,
        'image_path': session.image_path, 'analysis_id': invocation.analysis_id if invocation else None,
        'source_sha256': session.source_sha256,
        'result_id': session.result_id, 'analysis_revision': session.analysis_revision,
        'annotation_revision': session.annotation_revision,
        'analysis_annotation_revision': invocation.annotation_revision if invocation else None,
        'configuration': json.loads(invocation.settings_json) if invocation else None,
        'scene_context': dict(invocation.scene_context) if invocation else None,
        'profile': invocation.profile if invocation else None,
        'analysis_annotations': json.loads(invocation.annotations_json) if invocation else None,
        'imported_from': session.imported_from,
        'historical_identity': json.loads(session.historical_identity_json) if session.historical_identity_json else None,
    }
    data['annotations'] = json.loads(session.annotations_json)
    data['forensic_content'] = {'full_text': data.get('full_text') or '',
                                'full_html': data.get('full_html') or ''}
    appendix_text, appendix_html = annotation_appendix(session)
    data['full_text'] = (data.get('full_text') or '') + '\n\n' + appendix_text
    data['full_html'] = forensic_html(data) + appendix_html
    return ReportSnapshot(session.session_id, session.result_id, session.annotation_revision, json_snapshot(data))


def snapshot_is_current(session: InvestigationSession, snapshot: ReportSnapshot) -> bool:
    return (session.state == InvestigationState.COMPLETED and session.session_id == snapshot.session_id
            and session.revision_key == (snapshot.result_id, snapshot.annotation_revision))


def persist_report_snapshot(session: InvestigationSession, snapshot: ReportSnapshot,
                            output_dir: str | Path) -> dict[str, str]:
    if not snapshot_is_current(session, snapshot):
        raise ValueError('Report snapshot is stale or belongs to another investigation.')
    output = Path(output_dir)
    # Write to a new immutable generation. The atomic pointer is the publication
    # boundary, so a failed write never advertises a partly updated report bundle.
    generation = output / 'report_revisions' / f'{snapshot.result_id}-a{snapshot.annotation_revision}-{uuid4().hex}'
    data = snapshot.payload()
    summary_paths = persist_summary_result(data, generation)
    trace = data.get('reasoning_trace')
    trace_json = persist_reasoning_trace(trace, generation)
    try:
        trace_text = persist_reasoning_trace_text(trace, generation)
    except (KeyError, TypeError, ValueError):
        # Older/partial traces may not support the legacy narrative renderer.
        # Preserve exact recorded fields, rather than inventing missing facts.
        fallback = generation / 'reasoning_trace_recorded.txt'
        fallback.write_text('Structured trace fields incomplete; recorded data follows.\n'
                            + json.dumps(trace, indent=2, ensure_ascii=False), encoding='utf-8')
        trace_text = str(fallback)
    (generation / 'osint_results.json').write_text(json.dumps(data['annotations'], indent=2, ensure_ascii=False), encoding='utf-8')
    if not snapshot_is_current(session, snapshot):
        raise ValueError('Investigation revision changed during report generation.')
    pointer = output / 'current_report.json'
    temporary = output / f'.current_report-{uuid4().hex}.tmp'
    temporary.write_text(json.dumps({'schema_version': 1, 'investigation': data['investigation'],
                                    'summary': str(Path(summary_paths['final_summary_json']).relative_to(output))}, indent=2), encoding='utf-8')
    temporary.replace(pointer)
    session.report_revision = (snapshot.result_id, snapshot.annotation_revision)
    return {**summary_paths, 'reasoning_trace_json': trace_json, 'reasoning_trace_txt': trace_text,
            'current_report': str(pointer)}


def load_investigation(path: str | Path, image_path: str | Path | None = None) -> InvestigationSession:
    source = Path(path).resolve()
    data = json.loads(source.read_text(encoding='utf-8'))
    if isinstance(data, dict) and 'summary' in data and 'investigation' in data:
        target = (source.parent / data['summary']).resolve()
        if not target.is_relative_to(source.parent):
            raise ValueError('Report pointer escapes its investigation directory.')
        source = target
        data = json.loads(source.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not any(key in data for key in ('full_text', 'full_html', 'sections', 'reasoning_trace')):
        raise ValueError('Not a stored SignalLens summary.')
    for key in ('sections', 'reasoning_trace', 'investigation'):
        if data.get(key) is not None and not isinstance(data[key], dict):
            raise ValueError(f'Invalid stored {key}.')
    for key in ('full_text', 'full_html'):
        if data.get(key) is not None and not isinstance(data[key], str):
            raise ValueError(f'Invalid stored {key}.')
    metadata = data.get('investigation') or {}
    trace = data.get('reasoning_trace') or {}
    for key in ('decision', 'scorecard', 'derived_signals', 'contextual_priors', 'confidence_policy', 'pipeline_status', 'provenance_evidence'):
        if trace.get(key) is not None and not isinstance(trace[key], dict):
            raise ValueError(f'Invalid stored reasoning field: {key}.')
    for key in ('decision_route_trace', 'hypothesis_assessments'):
        if trace.get(key) is not None and (not isinstance(trace[key], list) or not all(isinstance(row, dict) for row in trace[key])):
            raise ValueError(f'Invalid stored reasoning field: {key}.')
    recorded_path = metadata.get('image_path') or image_path
    run_dir = source.parent.parent
    manifest = run_dir / 'analysis_run.json'
    if not recorded_path and manifest.is_file():
        recorded_path = json.loads(manifest.read_text(encoding='utf-8')).get('input', {}).get('selected_file')
    annotations = data.get('annotations')
    if 'annotations' not in data and (run_dir / 'osint_results.json').is_file():
        annotations = json.loads((run_dir / 'osint_results.json').read_text(encoding='utf-8'))
    if annotations is not None and not isinstance(annotations, dict):
        raise ValueError('Invalid stored annotations.')
    annotations_object(annotations)  # fail before replacing the active GUI session
    # A fresh explicit import identity avoids pretending historical revisions or
    # invocation IDs existed; original identity is preserved as source metadata.
    session = InvestigationSession(image_path=str(recorded_path) if recorded_path else None,
        state=InvestigationState.COMPLETED, result_id=uuid4().hex, analysis_revision=1,
        annotations_json=json_snapshot(annotations), imported_from=str(source),
        historical_identity_json=json_snapshot(metadata) if metadata else None,
        source_sha256=metadata.get('source_sha256') or (annotations or {}).get('image_sha256'))
    original = {key: value for key, value in data.items() if key not in ('investigation', 'annotations')}
    # New-format HTML/text includes the separate appendix. Restore exact frozen
    # forensic text from a recorded copy rather than stripping arbitrary prose.
    if 'forensic_content' in original:
        content = original.pop('forensic_content')
        original['full_text'], original['full_html'] = content['full_text'], content['full_html']
    session.summary_json = json_snapshot(original)
    return session
