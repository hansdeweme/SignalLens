"""Structural lineage, diagnostic allocation and production-invariance regressions."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict, replace
import json

import pytest

import decision_logic as logic
import evidence_dependency_analysis as analysis
from evidence_lineage import (
    Addition, EvidenceSpec, Family, Kind, LineageError, REGISTRY,
    build_lineage, lineage_to_json, lineage_from_json, validate_registry,
)
from marginal_corroboration import Contribution, ExperimentalCredits, allocate_marginal
from hypothesis_engine import build_context, build_evidence_snapshot, compute_scorecard, derive_signals
from reasoning_persistence import build_reasoning_trace_text
from test_reasoning import metadata, section
from test_scorecard_integrity import boundary_sections


def card_for(sections):
    ev=build_evidence_snapshot(sections)
    ds=derive_signals(ev)
    return compute_scorecard(sections,build_context(None),ev,ds),ds


def fixture_lineage(*, addition=Addition.RESTATEMENT, missing=False):
    specs=(EvidenceSpec('p','test.primary',Family.PROCESSING,('m1',),hypotheses=('localized_editing',)),
        EvidenceSpec('q','test.primary2',Family.PROCESSING,('m2',),hypotheses=('localized_editing',)),
        EvidenceSpec('child','test.child',Family.PROCESSING,(),('p',),hypotheses=('localized_editing',),kind=Kind.DERIVED,addition=addition),
        EvidenceSpec('child2','test.child2',Family.PROCESSING,(),('p',),hypotheses=('localized_editing',),kind=Kind.COMPOSITE,addition=addition))
    registry=validate_registry(specs)
    sections={k:section(k,'test') for k in ('p','q','child','child2')}
    if missing: sections['p'].status='unavailable'
    return build_lineage(sections,registry=registry)


def credit(key='p', *, polarity='suspicious', hypotheses=('localized_editing',), value=1.5):
    return Contribution('base:'+key,('evidence:'+key,),'base_'+polarity,value,polarity,hypotheses,'d')


def by_id(items):
    return {r['contribution_id']:r for r in items}


def test_one_primary_observation_retains_existing_credit():
    r=allocate_marginal([credit()],fixture_lineage())[0]
    assert r['diagnostic_contribution']==r['marginal_contribution']==1.5
    assert r['difference']==0 and not r['requires_empirical_validation']


def test_primary_and_pure_descendant_suppress_only_restatement_credit():
    rows=by_id(allocate_marginal([credit('child'),credit('p')],fixture_lineage()))
    assert rows['base:p']['diagnostic_contribution']==1.5
    assert rows['base:child']['diagnostic_contribution']==0
    assert rows['base:child']['measurement_ancestry']==('measurement:m1',)


def test_restatement_without_previously_credited_ancestor_is_not_arbitrarily_dropped():
    assert allocate_marginal([credit('child')],fixture_lineage())[0]['diagnostic_contribution']==1.5


def test_two_primary_measurements_in_same_family_remain_distinct():
    records=fixture_lineage()
    result=allocate_marginal([credit('p'),credit('q')],records)
    assert sum(r['diagnostic_contribution'] for r in result)==3
    diag=analysis._corroboration(['evidence:p','evidence:q'],{r.evidence_id:r for r in records})
    assert diag['measurement_ancestry_count']==2
    assert diag['only_one_measurement_family']
    assert diag['independent_observation_count'] is None


def test_composites_sharing_parent_are_visible_without_invented_independence():
    records=fixture_lineage(addition=Addition.INTERPRETATION)
    diag=analysis._corroboration(['evidence:p','evidence:child','evidence:child2'],{r.evidence_id:r for r in records})
    assert diag['supporting_indicator_count']==3 and diag['measurement_ancestry_count']==1
    assert len(diag['shared_ancestry']['measurement:m1'])==3
    assert len(diag['derived_or_composite_indicators'])==2


def test_five_descendants_of_one_measurement_are_not_five_independent_observations():
    base=fixture_lineage()
    node=next(r for r in base if r.evidence_id=='evidence:child')
    records=base+tuple(replace(node,evidence_id='evidence:extra'+str(i)) for i in range(3))
    ids=['evidence:child','evidence:child2',*['evidence:extra'+str(i) for i in range(3)]]
    diag=analysis._corroboration(ids,{r.evidence_id:r for r in records})
    assert diag['supporting_indicator_count']==5 and diag['measurement_ancestry_count']==1
    assert diag['independent_observation_count'] is None


def test_localization_addition_is_represented_without_inventing_numeric_margin():
    row=by_id(allocate_marginal([credit(),credit('child')],fixture_lineage(addition=Addition.LOCALIZATION)))['base:child']
    assert row['diagnostic_contribution']==1.5
    assert row['marginal_contribution'] is None and row['requires_empirical_validation']
    assert 'localization' in row['reason']


@pytest.mark.parametrize('addition',[Addition.RESTATEMENT,Addition.LOCALIZATION,Addition.RELATIONSHIP])
def test_missing_upstream_cannot_create_positive_marginal_credit(addition):
    row=allocate_marginal([credit('child')],fixture_lineage(addition=addition,missing=True))[0]
    assert row['diagnostic_contribution']==row['marginal_contribution']==0


@pytest.mark.parametrize('polarity,hypotheses',[
    ('benign',('localized_editing',)),('suspicious',('camera_acquisition',)),
])
def test_counter_evidence_or_different_hypothesis_is_not_deduplicated(polarity,hypotheses):
    rows=by_id(allocate_marginal([credit(),credit('child',polarity=polarity,hypotheses=hypotheses)],fixture_lineage()))
    assert rows['base:child']['diagnostic_contribution']==1.5


def test_explicit_contradiction_with_same_polarity_and_ancestry_keeps_hypothesis_role():
    child=replace(credit('child'),evidence_role='contradicting_evidence')
    rows=by_id(allocate_marginal([credit(),child],fixture_lineage()))
    assert rows['base:child']['diagnostic_contribution']==1.5
    assert rows['base:child']['evidence_role']=='contradicting_evidence'


def test_specific_subject_boundary_rule_does_not_invent_alignment_dependency():
    sections=boundary_sections()
    sections['subject_boundary']=section('subject','possible_subject_background_segmentation_artifact')
    sections['segmentation_alignment']=section('alignment','segmentation_boundary_alignment',score=.4)
    card,ds=card_for(sections)
    nodes={r.evidence_id:r for r in build_lineage(sections)}
    sources,_=analysis._operation_sources('ds.subject_boundary_strong and ds.strong_cross',[],nodes,ds)
    assert sources==('evidence:cross_signal','evidence:subject_boundary')


def test_unknown_evidence_is_explicit_and_positive_credit_withheld():
    lineage=build_lineage({'future_detector':section('future','unknown')})
    node=next(r for r in lineage if r.evidence_id=='evidence:future_detector')
    assert not node.known and node.family==Family.UNKNOWN
    assert allocate_marginal([credit('future_detector')],lineage)[0]['diagnostic_contribution']==0


@pytest.mark.parametrize('variant',['cycle','duplicate','missing_parent','duplicate_parent'])
def test_invalid_registry_rejected(variant):
    primary=EvidenceSpec('p','test',Family.PROCESSING,('m',))
    with pytest.raises(LineageError):
        if variant=='cycle': specs=(replace(primary,parents=('q',)),replace(primary,key='q',parents=('p',)))
        elif variant=='duplicate': specs=(primary,primary)
        elif variant=='missing_parent': specs=(replace(primary,parents=('q',)),)
        else: specs=(primary,replace(primary,key='q',parents=('p','p')))
        validate_registry(specs)


def test_cyclic_external_lineage_records_rejected():
    lineage=fixture_lineage()
    node=next(r for r in lineage if r.evidence_id=='evidence:p')
    records=tuple(replace(r,direct_dependencies=('evidence:child',)) if r==node else r for r in lineage)
    with pytest.raises(LineageError): allocate_marginal([credit()],records)


def test_immutable_records_and_registry():
    with pytest.raises(TypeError): REGISTRY['new']=REGISTRY['ela']
    with pytest.raises(FrozenInstanceError): fixture_lineage()[0].status='failed'


@pytest.mark.parametrize('change',[
    {'parents':['p']},{'measurements':('m','m')},
    {'addition':Addition.RESTATEMENT,'measurements':('new',)},
])
def test_registration_rejects_mutable_or_inconsistent_measurement_contracts(change):
    with pytest.raises(LineageError): replace(REGISTRY['ela'],**change)


def test_repeated_reversed_inputs_and_json_round_trip_are_deterministic():
    sections=boundary_sections()
    first=build_lineage(sections)
    assert first==build_lineage(dict(reversed(list(sections.items()))))
    inputs=[credit('p'),credit('child')]
    baseline=allocate_marginal(inputs,fixture_lineage())
    assert baseline==allocate_marginal(reversed(inputs),reversed(fixture_lineage()))
    assert json.loads(json.dumps(lineage_to_json(first),allow_nan=False))==json.loads(json.dumps(lineage_to_json(build_lineage(sections)),allow_nan=False))
    assert lineage_from_json(json.loads(json.dumps(lineage_to_json(first),allow_nan=False)))==first


def test_serialized_lineage_rejects_payloads_cycles_and_unknown_enums():
    serialized=json.loads(json.dumps(lineage_to_json(fixture_lineage())))
    for variant in ('payload','cycle','enum'):
        bad=deepcopy(serialized)
        if variant=='payload': bad[0]['pixels']=[[1,2]]
        elif variant=='cycle': bad[0]['direct_dependencies']=[bad[0]['evidence_id']]
        else: bad[0]['family']='unregistered family'
        with pytest.raises(LineageError): lineage_from_json(bad)


def test_missing_detectors_safe_and_do_not_serialize_details():
    import numpy as np
    sections={'ela':section('ela','ela_inconclusive',details={'pixels':np.zeros((8,8)), 'secret':'omit'})}
    serialized=json.dumps(lineage_to_json(build_lineage(sections)),allow_nan=False)
    assert 'secret' not in serialized and 'pixels' not in serialized
    empty=build_lineage({})
    assert all(not r.available for r in empty)


def test_inconclusive_parents_can_have_observed_features_without_base_credit():
    sections={k:section(k,'inconclusive',status='inconclusive') for k in ('ela','noise')}
    sections['cross_signal']=section('cross','strong_hotspot_convergence')
    nodes={r.evidence_id:r for r in build_lineage(sections)}
    assert nodes['evidence:ela'].available and not nodes['evidence:ela'].scoring_available
    assert not nodes['evidence:cross_signal'].missing_dependencies
    assert len(nodes['evidence:cross_signal'].measurement_ancestry)==2


def test_optional_asymmetry_parents_and_actual_material_fft_direction():
    sections=boundary_sections()
    sections['subject_process_asymmetry']=section('asym','subject_process_asymmetry_strong')
    nodes={r.evidence_id:r for r in build_lineage(sections)}
    asym=nodes['evidence:subject_process_asymmetry']
    assert not asym.missing_dependencies
    assert asym.optional_dependencies==('evidence:subject_texture_consistency','evidence:region_fft')
    assert 'evidence:subject_material_realism' not in asym.direct_dependencies+asym.optional_dependencies
    assert 'evidence:fft' not in REGISTRY['region_fft'].parents
    assert 'evidence:subject_process_asymmetry' not in REGISTRY['subject_material_realism'].parents


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-float('inf'),True])
def test_nonfinite_or_boolean_credit_rejected(value):
    with pytest.raises(LineageError): allocate_marginal([credit(value=value)],fixture_lineage())


@pytest.mark.parametrize('name,overrides',[
    ('',(('base:p',0),)),('bad',(('base:p',float('nan')),)),
    ('bad',(('base:p',-1),)),('bad',(('operation:p',0),)),
    ('bad',(('base:p',0),('base:p',1))),
])
def test_experimental_policy_requires_explicit_valid_values(name,overrides):
    with pytest.raises(LineageError): ExperimentalCredits(name,overrides)


def test_explicit_experiment_does_not_become_default_or_add_credit():
    experiment=ExperimentalCredits('test-only',(('base:p',0),))
    assert allocate_marginal([credit()],fixture_lineage(),experimental=experiment)[0]['diagnostic_contribution']==0
    assert allocate_marginal([credit()],fixture_lineage())[0]['diagnostic_contribution']==1.5
    with pytest.raises(LineageError): allocate_marginal([credit()],fixture_lineage(),experimental=ExperimentalCredits('excess',(('base:p',2),)))
    with pytest.raises(LineageError): allocate_marginal([credit()],fixture_lineage(),experimental=ExperimentalCredits('unknown',(('base:missing',0),)))


@pytest.mark.parametrize('case',['instagram','midjourney'])
def test_full_snapshot_card_trace_integration_preserves_entire_production_result(case):
    sections=boundary_sections()
    # Include real measured neutral parents so composite ancestry is available.
    sections.update(ela=section('ela','ela_inconclusive',polarity='neutral',status='weak'),
        noise=section('noise','noise_inconclusive',polarity='neutral',status='weak'))
    if case=='midjourney':
        sections['metadata']=metadata('DECLARED_SYNTHETIC')
        del sections['region_masks']
    else:
        sections['subject_boundary']=section('subject','possible_subject_background_segmentation_artifact')
        sections['boundary_focus']=section('focus','boundary_focused_processing_mismatch')
    before=deepcopy(sections)
    ordinary=logic.synthesize_overall(sections)
    shadow=logic.synthesize_overall(sections,evidence_dependency_shadow=True)
    assert ordinary[:4]==shadow[:4]
    diagnostic=shadow[4].pop('evidence_dependency_analysis')
    assert shadow[4]==ordinary[4] and sections==before
    assert diagnostic['status']=='complete' and diagnostic['production_score_unchanged']
    assert diagnostic['comparison']['suspicious_score']['difference']==0
    assert diagnostic['comparison']['benign_score']['difference']==0
    assert 'confidence_tier' not in diagnostic and 'decision' not in diagnostic
    assert len(diagnostic['component_lineage'])==len(ordinary[4]['scorecard_calculation']['component_operations'])
    json.dumps(diagnostic,allow_nan=False)


def test_pure_sidecar_does_not_mutate_shared_inputs_or_card_and_reconciles_experiment():
    sections=boundary_sections()
    sections.update(ela=section('ela','x',polarity='neutral'),noise=section('noise','x',polarity='neutral'))
    card,ds=card_for(sections)
    initial=deepcopy(asdict(card))
    ordinary=analysis.build_dependency_analysis(sections,card,ds)
    result=analysis.build_dependency_analysis(sections,card,ds,experimental=ExperimentalCredits('base-removal',(('base:cross_signal',0),)))
    assert asdict(card)==initial
    assert ordinary==analysis.build_dependency_analysis(dict(reversed(list(sections.items()))),card,ds)
    assert result['shadow_aggregates']['base_suspicious']==3
    assert result['comparison']['suspicious_score']['difference']==pytest.approx(-3.25)


def test_shadow_failure_does_not_change_production_decision(monkeypatch):
    def fail(*a,**k): raise RuntimeError('diagnostic failure')
    ordinary=logic.synthesize_overall(boundary_sections())
    monkeypatch.setattr(analysis,'build_dependency_analysis',fail)
    shadow=logic.synthesize_overall(boundary_sections(),evidence_dependency_shadow=True)
    assert ordinary[:4]==shadow[:4]
    diagnostic=shadow[4].pop('evidence_dependency_analysis')
    assert shadow[4]==ordinary[4]
    assert diagnostic['status']=='error' and diagnostic['shadow_aggregates']=={}


def test_invalid_production_card_has_no_shadow_score_and_text_is_compatible():
    result=logic.synthesize_overall({'boundary':section('bad','x',score=float('nan'))},evidence_dependency_shadow=True)
    diagnostic=result[4]['evidence_dependency_analysis']
    assert diagnostic['status']=='unavailable' and 'shadow_aggregates' not in diagnostic
    assert 'No shadow confidence tier' in build_reasoning_trace_text(result[4])
    assert build_reasoning_trace_text(logic.synthesize_overall({})[4])


def test_all_derived_signal_aliases_have_explicit_operation_sources():
    from hypothesis_engine import DerivedSignals
    assert set(DerivedSignals.__dataclass_fields__) <= analysis.SIGNAL_SOURCES.keys()


def test_component_identifiers_do_not_depend_on_conditional_operation_position():
    sections=boundary_sections()
    sections.update(ela=section('ela','x',polarity='neutral'),noise=section('noise','x',polarity='neutral'))
    card,ds=card_for(sections)
    before=analysis.build_dependency_analysis(sections,card,ds)['component_lineage']
    sections['sensor_origin']=section('sensor','camera_like_acquisition_supported',polarity='benign')
    card,ds=card_for(sections)
    after=analysis.build_dependency_analysis(sections,card,ds)['component_lineage']
    first={r['condition']:r['contribution_id'] for r in before}
    second={r['condition']:r['contribution_id'] for r in after}
    assert all(first[k]==second[k] for k in first.keys()&second.keys())


def test_unknown_future_component_alias_is_explicitly_partial():
    sections=boundary_sections()
    card,ds=card_for(sections)
    card.calculation['component_operations'][0]['reason']='ds.future_detector_support'
    sidecar=analysis.build_dependency_analysis(sections,card,ds)
    assert sidecar['status']=='partial'
    assert sidecar['lineage_coverage']['unknown_component_rule_ids']


def test_default_corroboration_gates_do_not_claim_independence_or_change_gate_results():
    sections=boundary_sections()
    sections.update(ela=section('ela','x',polarity='neutral'),noise=section('noise','x',polarity='neutral'))
    card,ds=card_for(sections)
    sidecar=analysis.build_dependency_analysis(sections,card,ds)
    gate=sidecar['corroboration_gates']['determine_confidence.strong_signals']
    assert gate['supporting_indicator_count']==2
    assert gate['measurement_ancestry_count']==2
    assert gate['ancestry_review_recommended']
    assert gate['independent_observation_count'] is None
    assert not gate['production_gate_changed'] and gate['counterfactual_gate_result'] is None
