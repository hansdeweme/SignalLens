"""One immutable report contract for the visible preview and explicit export."""
from dataclasses import dataclass
import json
from investigation_reports import ReportSnapshot,create_report_snapshot
from summary_persistence import _append_generator_to_html,_append_generator_to_text


@dataclass(frozen=True)
class ReportPresentation:
    snapshot: ReportSnapshot
    analysis_id: str | None
    analysis_revision: int
    html: str
    text: str
    structured_json: str
    formats: tuple[str,...]=('HTML','TXT','JSON')


def build_report_presentation(session):
    snapshot=create_report_snapshot(session)
    data=snapshot.payload()
    metadata=data['investigation']
    return ReportPresentation(snapshot,metadata['analysis_id'],metadata['analysis_revision'],
        _append_generator_to_html(data['full_html'],data),
        _append_generator_to_text(data['full_text'],data),
        json.dumps(data,indent=2,ensure_ascii=False))
