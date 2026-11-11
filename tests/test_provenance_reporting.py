"""UI-6-only presentation/export boundaries; shared lifecycle owners are reused."""
from copy import deepcopy
import json
from pathlib import Path
import threading

from gui_helpers import publish,wait_for
from investigation_session import InvestigationSession,InvestigationState
from investigation_presenters import build_presentation
from provenance_presenter import build_provenance,recover_metadata
from report_presentation import build_report_presentation
from report_workspace import write_export


def recorded():
    field={'raw_key':'XMP:Declaration','group':'XMP','value':'Original\nclaim'}
    data={'full_text':'Recorded forensic narrative','full_html':'<p>Recorded forensic narrative</p>',
        'sections':{'metadata':{'details':{'metadata_signals':[{'id':'C2PA_PRESENT','summary':'Presence only',
            'evidence':[field]}]}}},
        'reasoning_trace':{'provenance_evidence':{'state':'provenance_present_unverified','metadata_authenticity_verified':False},
            'hypothesis_assessments':[{'hypothesis_id':'synthetic_origin','supporting_evidence':['metadata:claim'],
                'evidence_details':{'metadata:claim':{'section':'metadata','observations':[field]}}}]}}
    session=InvestigationSession(state=InvestigationState.COMPLETED,result_id='recorded-result',analysis_revision=1,
        summary_json=json.dumps(data))
    return session,data,field


def test_recorded_fields_preserve_original_value_and_unverified_association():
    session,data,field=recorded()
    before=deepcopy(data)
    presentation=build_provenance(build_presentation(session),data)
    row=presentation.fields[0]
    assert row.value=='Original\nclaim' and row.tag=='XMP:Declaration'
    assert row.trust=='Unverified metadata' and row.evidence_ids==('metadata:claim',)
    assert presentation.verification=='unverified'
    assert any('unsupported' in value for value in presentation.limitations)
    assert data==before


def test_metadata_unavailable_execution_does_not_become_missing_provenance():
    session,data,_=recorded()
    data['reasoning_trace']['pipeline_status']={'stages':{'EXIF':{'assign_attr':'exif_payload','status':'failed','reason':'Cannot read container'}}}
    session.summary_json=json.dumps(data)
    failed=build_provenance(build_presentation(session),data)
    assert 'failed' in failed.extraction and 'Cannot read' in failed.extraction
    assert failed.declaration=='provenance_present_unverified'
    data['reasoning_trace']['provenance_evidence']['state']='no_substantive_provenance_evidence'
    data['reasoning_trace'].pop('pipeline_status')
    session.summary_json=json.dumps(data)
    missing=build_provenance(build_presentation(session),data)
    assert missing.declaration=='no_substantive_provenance_evidence' and 'failed' not in missing.extraction


def test_metadata_filter_excludes_nonmatches_and_binary_detail_is_descriptive(window,source):
    publish(window,source)
    workspace=window.workspace.provenance
    payload={'raw_watchlist_hits':{'tags':[{'raw_key':'XMP:Prompt','group':'XMP','value':'Exact text'},
        {'raw_key':'EXIF:Binary','group':'EXIF','value':b'\x00secret'}]}}
    workspace.payload=payload;workspace.rebuild()
    assert len(workspace.model.rows)==2
    workspace.search.setText('prompt')
    assert [row.tag for row in workspace.model.rows]==['XMP:Prompt']
    workspace.search.clear();workspace.namespace.setCurrentIndex(workspace.namespace.findData('EXIF'))
    assert workspace.selected_field().binary
    assert 'secret' not in workspace.details.toPlainText() and 'Binary payload' in workspace.details.toPlainText()


def test_stored_metadata_recovery_requires_both_run_identity_and_source_hash(tmp_path):
    context={'root':str(tmp_path),'source_sha256':'hash','source_path':'sample.jpg',
        'historical':{'result_id':'run'},'live':False}
    manifest=tmp_path/'analysis_run.json'
    manifest.write_text(json.dumps({'artifacts':{'investigation':{'result_id':'run','source_sha256':'hash'}}}))
    payload=tmp_path/'sample_exif_signals.json'
    payload.write_text(json.dumps({'file':{'sha256':'hash'},'raw_watchlist_hits':{}}))
    assert recover_metadata(context)[0] is not None
    context['historical']['result_id']='different-run'
    assert recover_metadata(context)[0] is None
    context['historical']['result_id']='run'
    payload.write_text(json.dumps({'file':{'sha256':'different-source'}}))
    assert recover_metadata(context)[0] is None


def test_osint_workspace_displays_committed_source_and_revision(window,source):
    from osint_reverse_search import add_manual_match
    from osint_dialogs import OSINTFindingDialog
    publish(window,source)
    frozen=window.session.summary_json
    draft=deepcopy(window.osint_result)
    dialog=OSINTFindingDialog()
    dialog.page_url_edit.setText('https://example.com/source')
    dialog.title_edit.setText('External claim')
    dialog.notes_edit.setPlainText('Analyst context')
    fields=dialog.relationship_fields
    fields['claim_process'].setCurrentIndex(fields['claim_process'].findData('full_image_generation'))
    fields['image_association'].setCurrentIndex(fields['image_association'].findData('analyst_associated'))
    fields['association_method'].setCurrentIndex(fields['association_method'].findData('analyst_visual_check'))
    fields['association_details'].setText('Matching distinctive scene reviewed by analyst')
    fields['model_family'].setText('FLUX.2 Klein')
    fields['source_dependency'].setCurrentIndex(fields['source_dependency'].findData('same_creator'))
    add_manual_match(draft,**dialog.get_data())
    restored_dialog=OSINTFindingDialog(existing_match=draft.matches[0])
    assert restored_dialog.get_data()==dialog.get_data()
    restored_dialog.close();dialog.close()
    assert window._commit_osint(window.session.session_id,draft)
    workspace=window.workspace.provenance
    assert 'revision: 1' in workspace.revision.text()
    assert 'https://example.com/source' in workspace.annotation_detail.toPlainText()
    assert 'Analyst context' in workspace.annotation_detail.toPlainText()
    assert 'analyst_associated' in workspace.annotation_detail.toPlainText()
    assert 'FLUX.2 Klein' in workspace.annotation_detail.toPlainText()
    relationships=window.workspace.evidence_relationships.toPlainText()
    assert 'https://example.com/source' in relationships and 'same_creator' in relationships
    assert 'full_image_generation' in relationships
    synthesis=json.loads(window.view_snapshot.investigation_synthesis_json)
    assert synthesis['external_source_corroboration']['assessment_status'] in workspace.external_context.text()
    assert synthesis['revision_id'] in window.workspace.investigation_detail.toPlainText()
    assert window.session.summary_json==frozen
    window.set_selected_file(source)
    assert not window.workspace.evidence_relationships.toPlainText()


def test_osint_verification_action_runs_off_thread_and_publishes_receipt(window, source, app, monkeypatch):
    """Gap: real verification action must publish its worker result through OSINT commit."""
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication
    from osint_reverse_search import add_manual_match
    from source_image_verification import SafeHTTP
    from source_verification_dialog import SourceVerificationDialog
    publish(window, source)
    frozen = window.session.summary_json
    draft = deepcopy(window.osint_result)
    add_manual_match(draft, 'other', 'https://example.com/page', title='Creator claim',
                     image_url='https://example.com/image', claim_process='full_image_generation')
    window._commit_osint(window.session.session_id, draft)
    observed = []
    def fetch(self, url, cancel, deadline):
        observed.append(threading.get_ident())
        return url, 'image/png', source.read_bytes()
    monkeypatch.setattr(SafeHTTP, 'fetch', fetch)
    timer = QTimer()
    def accept_when_ready():
        dialog = QApplication.activeModalWidget()
        if isinstance(dialog, SourceVerificationDialog) and not dialog.workers.busy:
            if dialog.save.isEnabled():
                dialog.save.click()
            else:
                dialog.reject()
    timer.timeout.connect(accept_when_ready)
    timer.start(10)
    try:
        window.btn_verify_osint.click()
    finally:
        timer.stop()
    assert observed and observed[0] != threading.get_ident()
    assert window.session.annotation_revision == 2
    assert window.osint_result.matches[0].verification
    assert 'byte_identical' in window.workspace.provenance.annotation_detail.toPlainText()
    assert 'sha256' in window.workspace.evidence_relationships.toPlainText()
    assert window.session.summary_json == frozen


def test_source_verification_cancellation_discards_worker_result(window, source, app, monkeypatch):
    """Gap: cancelling a source retrieval must wait for retirement and never accept."""
    import source_verification_dialog as module
    from osint_reverse_search import ReverseSearchMatch, sha256_of_file
    entered = threading.Event()
    def pending(path, sha, match, cancel, progress):
        entered.set()
        assert cancel.wait(2), 'cancellation was not delivered'
        raise InterruptedError('Verification cancelled')
    monkeypatch.setattr(module, 'retrieve', pending)
    dialog = module.SourceVerificationDialog(window, str(source), sha256_of_file(source),
        ReverseSearchMatch('other', page_url='https://example.com/page'))
    dialog.show()
    wait_for(app, entered.is_set)
    dialog.reject()
    wait_for(app, lambda: not dialog.workers.busy)
    assert dialog.selected_result is None and dialog.result() == 0 and not dialog.results
    dialog.deleteLater()


def test_preview_export_bytes_share_snapshot_and_legacy_text_fallback(tmp_path):
    session,_,_=recorded()
    session.summary_json=json.dumps({'full_text':'Legacy <literal> narrative'})
    presentation=build_report_presentation(session)
    paths=write_export(presentation.snapshot,tmp_path)
    assert Path(paths['final_summary_html']).read_text(encoding='utf-8')==presentation.html
    assert Path(paths['final_summary_txt']).read_text(encoding='utf-8')==presentation.text
    assert Path(paths['final_summary_json']).read_text(encoding='utf-8')==presentation.structured_json
    assert '&lt;literal&gt;' in presentation.html


def test_background_export_uses_captured_snapshot_off_gui_thread(window,source,tmp_path,app,monkeypatch):
    import report_workspace as module
    publish(window,source)
    workspace=window.workspace.reports
    captured=workspace.presentation.snapshot
    workspace.output.setText(str(tmp_path/'exports'))
    original=module.write_export
    observed=[]
    def observe(snapshot,output):
        observed.append((threading.get_ident(),snapshot))
        return original(snapshot,output)
    monkeypatch.setattr(module,'write_export',observe)
    assert workspace.start_export()
    wait_for(app,lambda:not workspace.pending)
    assert observed and observed[0][0]!=threading.get_ident() and observed[0][1]==captured
    assert json.loads(Path(workspace.saved_paths['final_summary_json']).read_text(encoding='utf-8'))==captured.payload()
    assert 'Export saved' in workspace.status.text()


def test_hidden_report_defers_layout_and_shows_latest_snapshot(window,source,app,monkeypatch):
    publish(window,source)
    workspace=window.workspace.reports
    layouts=[]
    original=workspace.preview.setHtml
    def observe(html):
        layouts.append(html)
        return original(html)
    monkeypatch.setattr(workspace.preview,'setHtml',observe)
    workspace.refresh_preview()
    assert workspace.presentation and workspace._render_pending and not layouts
    window.show()
    window.workspace.navigate('Reports');app.processEvents()
    assert len(layouts)==1 and not workspace._render_pending
    assert workspace.preview.toPlainText()
    window.workspace.navigate('Overview')
    window.clear_ui()
    window.workspace.navigate('Reports');app.processEvents()
    assert not workspace.preview.toPlainText() and not workspace._render_pending


def test_obsolete_preview_and_late_export_cannot_become_current(window,source,tmp_path):
    publish(window,source)
    workspace=window.workspace.reports
    old=workspace.presentation
    window.session.annotation_revision+=1
    assert not workspace.start_export() and 'stale' in workspace.status.text()
    workspace.pending['obsolete']=old.snapshot
    window.clear_ui()
    assert not workspace.accept_export('obsolete',{'current_report':'old'},None)
    assert not workspace.saved_paths and workspace.presentation is None


def test_background_export_failure_never_reports_saved(window,source,tmp_path,app,monkeypatch):
    import report_workspace as module
    publish(window,source)
    workspace=window.workspace.reports
    workspace.output.setText(str(tmp_path/'exports'))
    def fail(*args):raise OSError('Read-only destination')
    monkeypatch.setattr(module,'write_export',fail)
    assert workspace.start_export()
    wait_for(app,lambda:not workspace.pending)
    assert not workspace.saved_paths and 'Export failed' in workspace.status.text()
    assert 'Read-only destination' in workspace.status.text()


def test_provenance_navigation_checks_annotation_revision_and_recorded_field_link(window,source):
    publish(window,source)
    workspace=window.workspace.provenance
    session,data,_=recorded()
    data['full_html']='<p>Existing narrative</p>'
    window.session.summary_json=json.dumps(data)
    window.session.analysis_revision+=1  # Replacing frozen fixture data creates a new result revision.
    window.update_summary()
    key=window.workspace.explorer_snapshot.identity
    assert window.workspace.navigate_context('Provenance',key,evidence='metadata:claim',annotation_revision=0)
    assert workspace.selected_field().tag=='XMP:Declaration'
    assert not window.workspace.navigate_context('Provenance',key,evidence='unrelated',annotation_revision=0)
    assert 'not recorded' in workspace.details.toPlainText()
    window.session.annotation_revision+=1
    assert not window.workspace.navigate_context('Reports',key,annotation_revision=0)
