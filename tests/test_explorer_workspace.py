"""UI-5 projections and session-bound navigation, without forensic recalculation."""
from gui_helpers import publish, set_trace
from copy import deepcopy
from dataclasses import replace, FrozenInstanceError
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image
from PyQt6.QtCore import Qt

from investigation_presenters import build_presentation
from explorer_presenter import build_explorer,identity,number,check_recorded_calculation
from explorer_models import ExplorerIdentity
from investigation_session import InvestigationSession, InvestigationState


@pytest.fixture
def trace():
    assessments = []
    for hid,role in (('synthetic_origin','supporting_evidence'),('localized_editing','contradicting_evidence'),
                     ('camera_acquisition','moderating_evidence')):
        assessments.append({'hypothesis_id':hid,'explanation':'Recorded assessment '+hid,'confidence_tier':'Low',
            role:['shared:id','shared:id'],'evidence_details':{'shared:id':{'section':'boundary','label':'Contour observation',
                'reliability':'limited','observed_status':'strong','observed_score':.12345678901234567,
                'observations':['Measured contour property'],'interpretation':'Recorded inference',
                'limitations':['A recorded limitation']}}})
    return {'decision':{'primary_hypothesis':'localized_editing','dominant_pattern':'recorded_pattern'},
        'hypothesis_assessments':assessments,
        'decision_route_trace':[{'route':'first','matched':False,'selected':False,'reason':'condition_not_met'},
                                {'route':'second','matched':True,'selected':True,'reason':'recorded selection'},
                                {'route':'third','matched':True,'selected':False,'disposition':'superseded'}],
        'confidence_policy':{'assessments':[{'hypothesis':'localized_editing','tier':'High',
            'policy_rule':'test.recorded_rule','rationale':['Recorded confidence rationale'],
            'reliability_limitations':['Recorded cap'],'supporting_evidence':['shared:id']}]},
        'corroboration_audit':{'evaluated_gates':[{'gate_id':'compound','hypothesis':'localized_editing',
            'requirement_kind':'compound_interpretations','gate_passed':True,'shared_ancestry':{'measurement:shared':['evidence:a','evidence:b']},
            'explanation':'Related sources permitted; independence not verified','considered_evidence':['evidence:boundary']}]},
        'scorecard':{'suspicious_score':6.675,'benign_score':1.5,'is_valid':True},
        'scorecard_calculation':{'status':'valid','base_suspicious':7.0,'base_benign':1.5,'domain_bonus':.25,
            'component_operations':[{'field':'edit_boost','operation':'add','operand':.5,'reason':'Recorded rule'}],
            'aggregate_transforms':{'camera_multiplier':.85},'penalties':[{'field':'caution_penalty','operand':.2}],
            'numerical_deduplication':{'contributions':[{'evidence_id':'evidence:boundary','section':'boundary',
                'polarity':'suspicious','raw_contribution':3.0,'credited_contribution':0.0,
                'reliability_multiplier':1.0,'final_adjusted_contribution':0.0,'suppressed_contribution':3.0,
                'classification':'A','reason':'Confirmed duplicate numerical credit',
                'measurement_ancestry':['measurement:shared']}]}}}


@pytest.fixture
def populated(window,source,trace):
    publish(window,source)
    set_trace(window,trace)
    return window


@pytest.fixture
def projection(trace):
    """Pure presenter inputs; do not create a desktop window to inspect values."""
    data={'reasoning_trace':trace}
    session=InvestigationSession(state=InvestigationState.COMPLETED,result_id='fixture-result',
        analysis_revision=1,summary_json=json.dumps(data))
    view=build_presentation(session)
    return SimpleNamespace(session=session,view=view,data=data,snapshot=build_explorer(view,data))


def test_projection_is_immutable_and_does_not_mutate_recorded_result(projection):
    frozen = projection.session.summary_json
    snapshot = projection.snapshot
    assert len(snapshot.evidence)==3
    with pytest.raises(FrozenInstanceError):snapshot.primary_finding='changed'
    assert projection.session.summary_json == frozen
    assert len({r.key for r in snapshot.evidence})==3


@pytest.mark.parametrize('hid,role',[('synthetic_origin','supporting_evidence'),
    ('localized_editing','contradicting_evidence'),('camera_acquisition','moderating_evidence')])
def test_hypothesis_scoping_preserves_roles(populated,hid,role):
    workspace = populated.workspace.evidence
    assert workspace.focus(hid)
    assert len(workspace.model.rows)==1
    assert workspace.current.role==role and workspace.current.evidence_id=='shared:id'
    assert 'Measured observation' in workspace.details.toPlainText()
    assert 'Derived inference' in workspace.details.toPlainText()
    assert 'Recorded inference' in workspace.details.toPlainText()


@pytest.mark.parametrize('name,value', [('role','contradicting_evidence'),('detector','boundary'),
    ('reliability','limited'),('availability','strong')])
def test_filters_are_explicit_backend_values(populated,name,value):
    workspace=populated.workspace.evidence
    # A control that ignores its filter must not pass on three identical rows.
    if name!='role':
        snapshot=workspace.snapshot
        distractor=replace(snapshot.evidence[-1],detector_id='other_detector',
                           reliability='high',availability='unavailable')
        workspace.bind(replace(snapshot,evidence=(*snapshot.evidence[:-1],distractor)))
    workspace.filters[name].setCurrentIndex(workspace.filters[name].findData(value))
    expected=workspace.snapshot.evidence[1:2] if name=='role' else workspace.snapshot.evidence[:2]
    assert workspace.model.rows==expected


def test_search_and_no_match_clear_details(populated):
    workspace=populated.workspace.evidence
    workspace.search.setText('not-a-record')
    assert not workspace.model.rows and workspace.current is None
    assert 'No evidence matches' in workspace.details.toPlainText()
    assert not workspace.open_artifact.isEnabled()
    workspace.clear_filters()
    assert len(workspace.model.rows)==3


def test_recorded_policy_wins_and_does_not_change_scores(projection):
    snapshot=projection.snapshot
    h=next(r for r in snapshot.hypotheses if r.hypothesis_id=='localized_editing')
    c=next(r for r in snapshot.confidence if r.hypothesis_id=='localized_editing')
    assert h.outcome==c.outcome=='High'
    assert c.explanation=='test.recorded_rule'
    assert 'Recorded cap' in str(c.fields)
    assert '6.675' in snapshot.score_summary and '%' not in snapshot.score_summary


def test_routes_keep_order_and_recorded_dispositions(projection):
    rows=projection.snapshot.routes
    assert [r.title for r in rows]==['first','second','third']
    assert [r.outcome for r in rows]==['Not selected','Selected','superseded']
    assert 'disproven' not in str(rows).lower()


def test_compound_gate_never_implies_independence(projection):
    row=projection.snapshot.corroboration[0]
    assert row.outcome=='Passed'
    assert 'compound_interpretations' in str(row.fields)
    assert 'independence not verified' in row.explanation


def test_ledger_preserves_zero_suppression_and_exact_values(projection):
    snapshot=projection.snapshot
    row=snapshot.contributions[0]
    assert (row.raw,row.credited,row.final,row.suppressed)==('3.0','0.0','0.0','3.0')
    assert row.classification=='A'
    assert 'confirmed duplicate' in row.reason.lower()
    assert {'component_operations','penalties','aggregate_transforms'} <= {r.title for r in snapshot.score_records}
    assert number(.12345678901234567)==repr(.12345678901234567)


@pytest.mark.parametrize('value,expected',[(None,None),('wrong',None),(True,None),
    (float('inf'),'Invalid non-finite value'),(float('nan'),'Invalid non-finite value')])
def test_invalid_numeric_values_are_not_silently_zero(value,expected):
    assert number(value)==expected


def test_schema_lineage_is_separate_from_recorded_measurements(populated):
    nodes={n.node_id:n for n in populated.workspace.explorer_snapshot.lineage}
    boundary=nodes['evidence:boundary']
    assert boundary.parents==('evidence:ela','evidence:noise')
    assert boundary.measurements==('measurement:shared',)
    assert 'registry schema' in boundary.origin
    workspace=populated.workspace.evidence
    workspace.focus('localized_editing','shared:id')
    assert 'statistical redundancy' in workspace.lineage.details.toPlainText()


def test_persisted_cycles_and_intermediate_nodes_are_bounded(populated,trace):
    trace['evidence_dependency_analysis']={'lineage':[{'evidence_id':'evidence:boundary',
        'direct_dependencies':['evidence:boundary','intermediate:missing'],'optional_dependencies':[],
        'measurement_ancestry':['measurement:shared'],'kind':'composite','family':'processing_residual'}]}
    set_trace(populated,trace)
    workspace=populated.workspace.evidence
    workspace.focus('localized_editing','shared:id')
    assert len(workspace.lineage.model.rows)<10
    index=next(i for i,r in enumerate(workspace.lineage.model.rows) if r.record_id=='intermediate:missing')
    workspace.follow_lineage(workspace.lineage.model.index(index,0))
    assert 'intermediate' in workspace.message.text().lower()


def test_missing_lineage_does_not_infer_from_evidence_id(populated,trace):
    trace['hypothesis_assessments'][0]['evidence_details']['shared:id'].pop('section')
    set_trace(populated,trace)
    workspace=populated.workspace.evidence
    workspace.focus('synthetic_origin','shared:id')
    assert workspace.current.lineage_id is None
    assert 'No structured lineage' in workspace.lineage.details.toPlainText()


@pytest.mark.parametrize('trace_value',[{}, {'hypothesis_assessments':'bad'},
    {'scorecard_calculation':{'base_evidence':[None,'bad',{}]}},
    {'hypothesis_assessments':[None,{},'bad']},
    {'confidence_policy':{'assessments':[{'hypothesis':'synthetic_origin','tier':'Low'}]}}])
def test_partial_and_malformed_results_remain_accessible(window,source,trace_value):
    publish(window,source)
    set_trace(window,trace_value)
    assert window.workspace.explorer_snapshot is not None
    assert 'not probabilities' in window.workspace.explorer_snapshot.score_summary


def test_missing_target_is_explicit(populated):
    shell=populated.workspace
    key=shell.explorer_snapshot.identity
    assert not shell.navigate_context('Evidence',key,evidence='does-not-exist')
    assert shell.evidence.current is None and not shell.evidence.model.rows
    assert 'unavailable' in shell.evidence.details.toPlainText()
    assert not shell.navigate_context('Image Forensics',key,artifact='missing/artifact')
    assert shell.forensics.selected is None


def test_cross_navigation_preserves_scoped_evidence(populated):
    shell=populated.workspace
    key=shell.explorer_snapshot.identity
    assert shell.navigate_context('Evidence',key,hypothesis='localized_editing',evidence='shared:id')
    shell.evidence.show_reasoning('Confidence')
    assert shell.current_destination=='Reasoning'
    assert shell.reasoning.active_hypothesis=='localized_editing'
    assert shell.reasoning.tabs.tabText(shell.reasoning.tabs.currentIndex())=='Confidence'
    shell.reasoning.show_evidence()
    assert shell.current_destination=='Evidence' and shell.evidence.current.evidence_id=='shared:id'


def test_overview_card_targets_its_hypothesis(populated):
    populated.workspace.overview.cards['camera_acquisition'].open.click()
    assert populated.workspace.reasoning.active_hypothesis=='camera_acquisition'


def test_old_navigation_cannot_replace_new_result(populated,tmp_path):
    shell=populated.workspace
    key=shell.explorer_snapshot.identity
    other=tmp_path/'new.png'
    Image.new('RGB',(20,30)).save(other)
    populated.set_selected_file(other)
    assert not shell.navigate_context('Evidence',key,evidence='shared:id')
    assert not shell.evidence.model.rows and not shell.reasoning.panes['Confidence'].model.rows


def test_annotation_refresh_preserves_selection(populated):
    workspace=populated.workspace.evidence
    workspace.focus('camera_acquisition','shared:id')
    before=workspace.current.key
    frozen=populated.session.summary_json
    populated.session.annotation_revision+=1
    populated._publish_snapshot()
    assert workspace.current.key==before and populated.session.summary_json==frozen


def test_reanalysis_invalidates_content_and_old_navigation(populated):
    shell=populated.workspace
    key=shell.explorer_snapshot.identity
    populated.session.begin_analysis('normal',{},populated.settings,populated.settings['output_root'])
    populated.update_summary()
    assert not shell.evidence.model.rows
    assert not shell.navigate_context('Reasoning',key,hypothesis='localized_editing')


def test_artifact_links_require_explicit_same_result_identity(projection):
    snapshot=projection.view
    data=projection.data
    artifact=SimpleNamespace(artifact_id='boundary/overlay',session_id=snapshot.session_id,
        result_id=snapshot.result_id,analysis_revision=snapshot.analysis_revision,evidence_ids=('shared:id',))
    result=build_explorer(snapshot,data,(artifact,))
    assert result.evidence[0].artifact_ids==('boundary/overlay',)
    artifact.result_id='old'
    assert not build_explorer(snapshot,data,(artifact,)).evidence[0].artifact_ids


def test_unknown_reliability_is_filterable_and_malformed_details_safe(populated,trace):
    detail=trace['hypothesis_assessments'][0]['evidence_details']['shared:id']
    detail.update(label=[],reliability={},availability=[],interpretation={})
    set_trace(populated,trace)
    workspace=populated.workspace.evidence
    workspace.focus('synthetic_origin')
    assert workspace.current.label=='shared:id' and workspace.current.reliability is None


def test_navigation_is_rejected_while_closing(populated):
    populated._closing=True
    assert not populated.workspace.navigate_context('Evidence',populated.workspace.explorer_snapshot.identity)
    populated._closing=False


@pytest.mark.parametrize('case,expected',[('valid','Reconciled'),('mismatch','Mismatch'),
    ('incomplete','Incomplete'),('broken','Unavailable / invalid ledger')])
def test_existing_pure_arithmetic_audit_never_replaces_recorded_totals(case,expected):
    from scorecard_integrity import COMPONENT_FIELDS
    calc={'calculation_version':'2a','status':'valid','base_evidence':[],
        'domain_bonus':.25,'component_operations':[],
        'aggregate_transforms':{'camera_multiplier':1.0,'geometry_multiplier':1.0,'photo_context_multiplier':1.0}}
    card={name:0.0 for name in (*COMPONENT_FIELDS,'suspicious_score','benign_score')}
    if case=='mismatch':card['suspicious_score']=6.675
    if case=='incomplete':card.pop('benign_score')
    if case=='broken':calc['component_operations']=[{'operation':'unknown'}]
    before=deepcopy((calc,card))
    audit=check_recorded_calculation(calc,card)
    assert audit.outcome==expected
    assert (calc,card)==before


def test_back_navigation_and_selection_stay_within_result(populated):
    workspace=populated.workspace.evidence
    workspace.clear_filters()
    workspace.table.selectRow(0)
    first=workspace.current.key
    workspace.table.selectRow(1)
    assert workspace.history
    workspace.go_back()
    assert workspace.current.key==first


def test_missing_confidence_target_does_not_show_unrelated_assessment(populated):
    workspace=populated.workspace.reasoning
    assert not workspace.focus('unknown_hypothesis','Confidence')
    assert not workspace.panes['Confidence'].model.rows
    assert 'unavailable' in workspace.message.text()
