"""Phase 2B.3: source diversity is distinct from compound mechanism evidence."""
from copy import deepcopy
from dataclasses import asdict, replace
import json

import pytest

import decision_logic as logic
from evidence_dependency_analysis import build_dependency_analysis
from evidence_lineage import Addition, EvidenceSpec, Family, Kind, LineageError, build_lineage, validate_registry
from production_corroboration import CorroborationRequirement, RequirementKind, evaluate_corroboration
from reasoning_persistence import build_reasoning_trace_text
from scorecard_integrity import reconstruct_scorecard_calculation, validate_scorecard
from signal_language import humanize_signal
from test_reasoning import metadata, section
from test_scorecard_integrity import boundary_sections


def requirement(kind=RequirementKind.DISTINCT_SOURCES, **kwargs):
    return CorroborationRequirement('test.sources','localized_editing',kind,minimum_indicators=2,minimum_sources=2,**kwargs)


def measured_boundary(ratio=.02):
    sections=boundary_sections(ratio)
    sections['cross_signal'].status='medium'
    sections.update(ela=section('ela','ela_localized_hotspots',polarity='neutral',status='weak'),
        noise=section('noise','noise_localized_hotspots',polarity='neutral',status='weak'))
    return sections


def evaluate(sections, *keys, spec=None, **kwargs):
    return evaluate_corroboration(sections,['evidence:'+key for key in keys],spec or requirement(),**kwargs)


def test_one_primary_counts_once():
    sections={'ela':section('ela','anomaly')}
    result=evaluate(sections,'ela')
    assert result['corroborating_source_count']==1
    assert not result['requirement_satisfied']


def test_primary_and_two_descendants_cannot_be_three_sources():
    sections=measured_boundary()
    sections['ela'].polarity='suspicious'
    result=evaluate(sections,'ela','cross_signal','boundary')
    assert result['corroborating_source_count']==1
    assert not result['requirement_satisfied']
    assert len(result['shared_ancestry']['measurement:ela_recompression_difference'])==3


def test_two_primary_extractions_can_satisfy_existing_two_source_requirement():
    sections={key:section(key,'anomaly') for key in ('ela','noise')}
    result=evaluate(sections,'ela','noise')
    assert result['corroborating_source_count']==2 and result['requirement_satisfied']
    assert result['overlapping_feature_groups']  # Still not statistical independence.


def test_composite_does_not_become_third_source_or_collapse_distinct_primaries():
    sections=measured_boundary()
    sections['ela'].polarity=sections['noise'].polarity='suspicious'
    result=evaluate(sections,'ela','noise','cross_signal')
    assert result['corroborating_source_count']==2
    assert {g['witness'] for g in result['distinct_ancestry_groups']}=={'evidence:ela','evidence:noise'}


def test_true_compound_boundary_condition_is_not_replaced_by_source_uniqueness():
    sections=measured_boundary(.04)
    sections['boundary_focus']=section('focus','boundary_focused_processing_mismatch',score=8)
    sections['segmentation_alignment']=section('alignment','segmentation_boundary_alignment',score=.6)
    separate=evaluate(sections,'boundary','boundary_focus')
    compound=evaluate(sections,'boundary','boundary_focus',spec=requirement(RequirementKind.COMPOUND))
    assert not separate['requirement_satisfied']
    assert compound['requirement_satisfied']
    env=logic.build_decision_env(sections)
    assert logic._boundary_corroborated(env)
    assert logic.route_strong_local_edit(env).confidence=='High'


def test_patch_pair_localization_is_not_another_source():
    sections=measured_boundary()
    sections.update(patch_similarity=section('patch','possible_clone_reuse'),
        patch_spatial=section('spatial','cross_region_patch_recurrence'))
    result=evaluate(sections,'patch_similarity','patch_spatial')
    assert result['corroborating_source_count']==1 and not result['requirement_satisfied']
    assert any(r['addition']=='localization' for r in result['incremental_support_findings'])


def test_texture_and_asymmetry_share_ancestry_while_own_measurements_remain_visible():
    sections=measured_boundary()
    sections.update(subject_texture_consistency=section('texture','subject_internal_stochastic_repetition'),
        subject_process_asymmetry=section('asym','subject_process_asymmetry_strong'))
    result=evaluate(sections,'subject_texture_consistency','subject_process_asymmetry')
    assert result['corroborating_source_count']==1
    assert result['shared_ancestry']['measurement:masked_hybrid_texture_descriptors']


def test_shared_feature_code_is_not_automatically_identical_observation():
    sections=measured_boundary()
    sections.update(subject_material_realism=section('material','subject_material_realism_failure_strong',score=.65),
        subject_process_asymmetry=section('asym','subject_process_asymmetry_strong'))
    result=evaluate(sections,'subject_material_realism','subject_process_asymmetry')
    assert result['corroborating_source_count']==2
    assert 'surface_feature_definitions' in result['overlapping_feature_groups']
    assert 'statistical independence' in ' '.join(result['limitations'])


def test_metadata_and_pixels_are_different_sources_without_authenticating_declaration():
    sections={'metadata':metadata('DECLARED_SYNTHETIC'),'fft':section('fft','possible_decoder_grid_signature')}
    spec=replace(requirement(),hypothesis='synthetic_origin',distinct_families=True)
    result=evaluate(sections,'metadata','fft',spec=spec)
    assert result['requirement_satisfied'] and result['corroborating_source_count']==2
    assert result['distinct_families_required']
    assert logic.synthesize_overall({'metadata':sections['metadata']})[4]['provenance_evidence']['metadata_authenticity_verified'] is False


@pytest.mark.parametrize('status',['not_run','unavailable','skipped','failed','error','inconclusive'])
def test_missing_or_inactive_parent_cannot_supply_extra_source(status):
    sections=measured_boundary()
    sections['noise'].status=status
    if status=='inconclusive':
        # Inconclusive parents may have measured maps. They still add no *third* source.
        result=evaluate(sections,'boundary','cross_signal')
        assert result['corroborating_source_count']==1
    else:
        result=evaluate(sections,'boundary','cross_signal')
        assert result['corroborating_source_count']==0 and result['provisional_lineage']
    assert not result['requirement_satisfied']


def test_unknown_lineage_cannot_confirm_and_original_observation_remains():
    sections={'future':section('future','anomaly'),'ela':section('ela','anomaly')}
    before=deepcopy(sections)
    result=evaluate(sections,'ela','future')
    assert result['corroborating_source_count']==1
    assert 'evidence:future' in result['excluded_evidence']
    assert sections==before


def test_contradictions_remain_scoped_and_are_not_counted_as_support():
    sections={'ela':section('ela','anomaly'),'noise':section('noise','anomaly')}
    result=evaluate(sections,'ela','noise',roles={'evidence:noise':'contradicting_evidence'})
    assert result['evidence_roles']['evidence:noise']=='contradicting_evidence'
    assert result['corroborating_source_count']==1
    assert sections['noise'].pattern=='anomaly'


def test_wrong_hypothesis_does_not_create_support():
    sections={'metadata':metadata('DECLARED_SYNTHETIC'),'ela':section('ela','anomaly')}
    result=evaluate(sections,'metadata','ela')
    assert 'evidence:metadata' in result['excluded_evidence']


def test_order_repeat_and_serialization_are_deterministic():
    sections=measured_boundary()
    sections['ela'].polarity=sections['noise'].polarity='suspicious'
    first=evaluate(sections,'ela','noise','cross_signal')
    assert first==evaluate(dict(reversed(list(sections.items()))),'cross_signal','noise','ela')
    assert first==evaluate(sections,'ela','noise','cross_signal')
    assert json.loads(json.dumps(first,allow_nan=False))==first


def test_corrected_gate_changes_only_generic_high_confidence_eligibility():
    sections=measured_boundary()
    env=logic.build_decision_env(sections)
    before=deepcopy(asdict(env.card))
    assert env.card.suspicious_score==pytest.approx(4.905)
    # Previous predicate: two strong indicator flags plus S>=3 -> High.
    assert env.ds.strong_cross and env.ds.strong_local_edit and env.card.suspicious_score>=3
    assert env.confidence_tier=='Medium'
    result=logic.synthesize_overall(sections,evidence_dependency_shadow=True)
    assert result[0]=='moderate_suspicious_convergence' and result[2]=='Medium'
    assert asdict(env.card)==before
    hs={h['hypothesis_id']:h for h in result[4]['hypothesis_assessments']}
    assert hs['unresolved_anomaly']['confidence_tier']=='Medium'
    assert hs['synthetic_origin']['confidence_tier']=='Inconclusive'
    gates={g['gate_id']:g for g in result[4]['corroboration_audit']['evaluated_gates']}
    gate=gates['confidence.strong_source_diversity']
    assert gate['observed_strong_indicator_count']==2 and gate['corroborating_source_count']==1
    assert not gate['gate_passed'] and gate['score_requirement_satisfied']
    assert result[4]['scorecard_calculation']==env.card.calculation
    validate_scorecard(env.card)
    replay=reconstruct_scorecard_calculation(result[4]['scorecard_calculation'])
    assert replay['suspicious_score']==pytest.approx(result[4]['scorecard']['suspicious_score'])
    assert result[4]['evidence_dependency_analysis']['comparison']['suspicious_score']['difference']==0


def test_distinct_strong_sources_still_qualify_high():
    sections=measured_boundary()
    sections['subject_process_asymmetry']=section('asym','subject_process_asymmetry_strong')
    env=logic.build_decision_env(sections)
    assert env.confidence_tier=='High'
    gate=env.corroboration_gates[0]
    assert gate['corroborating_source_count']==2 and gate['gate_passed']


@pytest.mark.parametrize('status',['unavailable','inconclusive','failed'])
def test_stale_inactive_strong_scores_cannot_manufacture_confidence(status):
    sections={'subject_material_realism':section('material','subject_material_realism_failure_strong',score=.9,status=status),
        'subject_process_asymmetry':section('asym','subject_process_asymmetry_strong',status=status)}
    from hypothesis_engine import ScoreCard
    assert logic.determine_confidence(ScoreCard(suspicious_score=4),sections)=='Low'


def test_compound_material_asymmetry_route_keeps_existing_hypothesis_behavior():
    from test_reasoning import visual_generation_env, assess
    result=assess(visual_generation_env())
    assert result[0]=='synthetic_multi_signal_convergence' and result[2]=='High'
    gates={g['gate_id']:g for g in result[4]['corroboration_audit']['evaluated_gates']}
    assert gates['synthetic.material_asymmetry_compound']['gate_passed']
    assert gates['synthetic.material_asymmetry_compound']['production_condition_changed'] is False


def test_trace_is_compact_and_repeated_environment_evaluation_does_not_accumulate():
    env=logic.build_decision_env(measured_boundary())
    first=logic.finish_decision(env,logic.evaluate_hypotheses(env))
    second=logic.finish_decision(env,logic.evaluate_hypotheses(env))
    assert first==second
    audit=first[4]['corroboration_audit']
    ids=[g['gate_id'] for g in audit['evaluated_gates']]
    assert len(ids)==len(set(ids))
    assert 'lineage' not in audit
    assert 'Production Corroboration Audit' in build_reasoning_trace_text(first[4])
    assert len(first)==5


def test_shadow_policy_and_arithmetic_remain_unmodified_by_production_gate():
    sections=measured_boundary()
    env=logic.build_decision_env(sections)
    before=build_dependency_analysis(sections,env.card,env.ds,context=env.ctx)
    logic.evaluate_hypotheses(env)
    after=build_dependency_analysis(sections,env.card,env.ds,context=env.ctx)
    assert before==after
    assert before['policy']=='structural_restatement_only'


def test_unsupported_independence_language_is_not_emitted():
    assert humanize_signal('no_meaningful_convergence')=='ELA and residual hotspot checks do not meaningfully overlap'
    result=logic.synthesize_overall({'metadata':metadata('DECLARED_SYNTHETIC')})
    assert 'independently of inconclusive' not in result[1]
    assert 'without requiring a conclusive localized-editing result' in result[1]


def test_distinct_family_requirement_is_explicit_not_a_universal_rule():
    sections={k:section(k,'anomaly') for k in ('ela','noise')}
    assert evaluate(sections,'ela','noise')['requirement_satisfied']
    assert not evaluate(sections,'ela','noise',spec=requirement(distinct_families=True))['requirement_satisfied']


def test_bad_requirement_and_duplicate_or_cyclic_external_lineage_fail_clearly():
    with pytest.raises(LineageError): replace(requirement(),minimum_sources=0)
    records=build_lineage(measured_boundary())
    with pytest.raises(LineageError): evaluate(measured_boundary(),'boundary',lineage=records+records[:1])
    cyclic=(replace(records[0],direct_dependencies=(records[0].evidence_id,)),)+records[1:]
    with pytest.raises(LineageError): evaluate(measured_boundary(),'boundary',lineage=cyclic)
