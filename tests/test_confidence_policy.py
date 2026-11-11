"""Phase 3 centralized policy and complete synthesis integration regressions."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict, replace
import json
from types import SimpleNamespace

import pytest

import decision_logic as logic
from confidence_policy import (
    AssessmentEvidence, ConfidenceFacts, Finding, VerifiedGenerationAssertion,
    evaluate_confidence, generic_confidence,
)
from confidence_policy_inputs import snapshot_confidence_facts
from hypothesis_engine import HypothesisAssessment
from metadata_evidence import ProvenanceState
from reasoning_persistence import build_reasoning_trace_text
from scorecard_integrity import reconstruct_scorecard_calculation
from summary_synthesizer import build_summary_result
from test_reasoning import assess, metadata, reference_env, section, visual_generation_env
from test_production_corroboration import measured_boundary


def policy(trace,hypothesis):
    return next(item for item in trace['confidence_policy']['assessments'] if item['hypothesis']==hypothesis)


def hypotheses(trace):
    return {h['hypothesis_id']:h for h in trace['hypothesis_assessments']}


@pytest.mark.parametrize('status,polarity', [('inconclusive', 'neutral'), ('weak', 'benign')])
def test_non_supporting_focus_cannot_supply_compound_strength(status, polarity):
    """Missing negative control: a retained raw intensity is not positive strength."""
    sections = measured_boundary(.04)
    sections['boundary'].score = None
    sections['subject_boundary'] = section('subject', 'possible_boundary_transition_inconsistency', status='medium', score=.393)
    sections['boundary_focus'] = section('focus', 'boundary_processing_inconclusive' if status == 'inconclusive'
        else 'boundary_processing_convergence_supported', status=status, polarity=polarity, score=9.0)
    env = logic.build_decision_env(sections)
    assert not logic._boundary_corroborated(env)
    gate = next(g for g in env.corroboration_gates if g['gate_id'] == 'boundary.compound_support')
    assert not gate['strength_requirement_satisfied'] and gate['strength_witnesses'] == []
    assert gate['eligible_evidence'] == ['evidence:boundary', 'evidence:subject_boundary']
    # Count success must never hide the actual production strength failure.
    conditions = {c['condition_id']: c for c in gate['conditions']}
    assert conditions['indicator_count']['passed'] is True
    assert conditions['supporting_strength']['passed'] is False
    assert gate['failure_reasons'] == [conditions['supporting_strength']['explanation']]
    assert '>= 0.45' in gate['overall_explanation']
    observations = {o['evidence_id']: o for o in gate['strength_observations']}
    assert observations['evidence:subject_boundary']['score'] == .393
    assert not observations['evidence:boundary_focus']['eligible_for_strength']
    assert not snapshot_confidence_facts(sections, env.card, env.ds, env.corroboration_gates, {}).boundary_compound
    text = build_reasoning_trace_text(logic.synthesize_overall(sections)[4])
    assert 'indicator_count: PASS' in text and 'supporting_strength: FAIL' in text
    assert 'Overall FAIL' in text and '0.393' in text and '>= 0.45' in text


def test_unverified_generation_is_bounded_and_identifies_policy_rule():
    result=logic.synthesize_overall({'metadata':metadata('DECLARED_SYNTHETIC')})
    record=policy(result[4],'synthetic_origin')
    assert result[2]==record['tier']=='Medium'
    assert record['policy_rule']=='synthetic.unverified_generation_declaration'
    assert 'unverified' in ' '.join(record['rationale'])
    assert result[4]['provenance_evidence']['metadata_authenticity_verified'] is False


@pytest.mark.parametrize('binding,success',[(True,True),(False,True),(True,False)])
def test_verified_assertion_requires_actual_typed_validator_and_image_binding(binding,success):
    evidence=AssessmentEvidence('synthetic_origin',supporting_evidence=('verified:assertion',))
    verified=VerifiedGenerationAssertion('verified:assertion','fixture-validator',success,binding)
    result=evaluate_confidence(evidence,ConfidenceFacts(verification=verified))
    if binding and success:
        assert result.policy_rule=='synthetic.verified_assertion'
        assert result.tier=='Medium'  # Claim authentication is not pixel-origin proof.
    else: assert result.policy_rule=='synthetic.not_established'


@pytest.mark.parametrize('signal',['C2PA_PRESENT','AI_TOOL_NAME_MATCH','AMBIGUOUS_WORKFLOW_METADATA'])
def test_metadata_verification_flags_and_ambiguity_cannot_create_high(signal):
    summary=metadata(signal)
    summary.details.update(provenance_verified=True,provenance_state='verified_generation_assertion')
    result=logic.synthesize_overall({'metadata':summary})
    assert result[2]!='High'
    assert policy(result[4],'synthetic_origin')['tier']=='Inconclusive'


def test_verification_enum_or_json_dictionary_is_not_a_validator_result():
    evidence=AssessmentEvidence('synthetic_origin')
    result=evaluate_confidence(evidence,ConfidenceFacts(provenance=ProvenanceState.VERIFIED_GENERATION_ASSERTION))
    assert result.tier=='Inconclusive'
    with pytest.raises(ValueError): ConfidenceFacts(verification={'verified':True})


def test_missing_metadata_does_not_change_a_mechanism_confidence():
    sections=measured_boundary(.04)
    sections['subject_boundary']=section('subject','possible_subject_background_segmentation_artifact')
    first=logic.synthesize_overall(sections)
    second=logic.synthesize_overall({**sections,'metadata':metadata('METADATA_STRIPPED_OR_SPARSE')})
    assert first[2]==second[2]=='High'
    assert policy(first[4],'localized_editing')['policy_rule']==policy(second[4],'localized_editing')['policy_rule']
    assert policy(second[4],'synthetic_origin')['tier']=='Inconclusive'


def test_reliable_local_processing_high_is_not_transferred_to_generation():
    result=assess(reference_env('instagram'))
    assert policy(result[4],'localized_editing')['tier']=='High'
    assert policy(result[4],'synthetic_origin')['tier']=='Inconclusive'
    assert result[2]=='High'


def test_rejected_person_geometry_cannot_sustain_high_boundary_policy():
    facts=ConfidenceFacts(findings=(('localized_editing',(Finding.BOUNDARY_DECISIVE,)),),
        suspicious=9,local_support=5,boundary_compound=True,person_reliable=False)
    result=evaluate_confidence(AssessmentEvidence('localized_editing'),facts)
    assert result.tier=='Medium' and result.policy_rule=='localized.required_geometry_cap'
    sections=measured_boundary()
    sections['region_masks'].status='not_run'
    actual=logic.synthesize_overall(sections)
    assert policy(actual[4],'localized_editing')['tier']!='High'


def test_reliability_cap_does_not_depend_on_safeguard_route_presence():
    env=reference_env('instagram')
    env.ds.boundary_reliability_score=.25
    routes=[spec for spec in logic.DECISION_ROUTES if not spec.boundary_safeguard]
    result=logic.finish_decision(env,logic.evaluate_hypotheses(env,routes))
    assert result[2]=='Medium'
    assert policy(result[4],'localized_editing')['policy_rule']=='localized.boundary_support_limited'


@pytest.mark.parametrize('reliability',[0,.25,.5])
def test_existing_limited_boundary_requirement_remains_explicit(reliability):
    env=reference_env('instagram')
    env.ds.boundary_reliability_score=reliability
    result=assess(env)
    assert policy(result[4],'localized_editing')['tier']=='Medium'
    assert policy(result[4],'localized_editing')['policy_rule']=='localized.boundary_support_limited'


def test_descendants_cannot_bypass_general_high_gate_via_a_high_route_label():
    sections=measured_boundary(.02)
    sections['unrelated_status_weight']=section('extra','unspecific',status='strong')
    env=logic.build_decision_env(sections)
    assert logic.route_multi_signal_suspicious(env).confidence=='High'  # legacy only
    result=logic.synthesize_overall(sections)
    record=policy(result[4],'unresolved_anomaly')
    assert record['tier']=='Medium' and result[2]=='Medium'
    assert record['policy_rule']=='generic.one_strong_observation'
    gate=next(g for g in result[4]['corroboration_audit']['evaluated_gates'] if g['gate_id']=='confidence.strong_source_diversity')
    assert gate['corroborating_source_count']==1 and not gate['gate_passed']


def test_distinct_sources_keep_existing_generic_high_rule():
    sections=measured_boundary()
    sections['subject_process_asymmetry']=section('asym','subject_process_asymmetry_strong')
    env=logic.build_decision_env(sections)
    source=next(g for g in env.corroboration_gates if g['gate_id']=='confidence.strong_source_diversity')
    tier,rule=generic_confidence(env.card.suspicious_score,source['observed_strong_indicator_count'],source['requirement_satisfied'])
    assert tier=='High' and rule=='generic.distinct_strong_sources'


def test_strong_visual_generation_and_limited_local_findings_are_assessed_separately():
    result=assess(visual_generation_env())
    assert policy(result[4],'synthetic_origin')['tier']=='High'
    assert policy(result[4],'localized_editing')['tier']=='Low'
    assert result[4]['decision']['primary_hypothesis']=='synthetic_origin'


def test_camera_compatibility_and_generation_declaration_coexist():
    result=logic.synthesize_overall({'metadata':metadata('DECLARED_SYNTHETIC'),
        'sensor_origin':section('sensor','camera_like_acquisition_supported',polarity='benign')})
    syn=policy(result[4],'synthetic_origin');camera=policy(result[4],'camera_acquisition')
    assert syn['tier']==camera['tier']=='Medium'
    assert syn['moderating_evidence'] and not syn['contradicting_evidence']
    assert camera['policy_rule']=='camera.acquisition_compatibility'
    assert 'not photographic authenticity' in ' '.join(camera['rationale'])


def test_direct_contradiction_changes_mechanism_eligibility_without_global_penalty():
    sections=measured_boundary(.04)
    sections.update(boundary_focus=section('focus','boundary_focused_processing_mismatch'),
        compression_history=section('compression','localized_compression_inconsistency'),
        subject_texture_consistency=section('texture','subject_texture_stochastic_regularization'))
    before=logic.synthesize_overall(sections)
    assert before[2]=='High'
    sections['boundary_focus']=section('focus','boundary_processing_convergence_supported',status='weak',polarity='benign',score=0)
    after=logic.synthesize_overall(sections)
    record=policy(after[4],'localized_editing')
    assert record['tier']=='Medium' and record['contradicting_evidence']
    assert 'not a global point deduction' in ' '.join(record['rationale'])
    assert policy(after[4],'synthetic_origin')['tier']=='Inconclusive'


def test_counter_evidence_is_not_deleted_when_other_compound_support_survives():
    env=reference_env('instagram')
    env.sections['boundary_focus']=section('focus','boundary_processing_convergence_supported',status='weak',polarity='benign',score=0)
    result=assess(env)
    record=policy(result[4],'localized_editing')
    assert record['tier']=='High' and record['contradicting_evidence']


def test_missing_regional_coverage_is_limitation_not_declaration_penalty():
    coverage={'status':'partial','unavailable_stages':['Person-derived region masks','Subject texture consistency analysis']}
    sections={'metadata':metadata('DECLARED_SYNTHETIC')}
    plain=logic.synthesize_overall(sections)
    missing=logic.synthesize_overall(sections,analysis_coverage=coverage)
    assert plain[2]==missing[2]=='Medium'
    record=policy(missing[4],'synthetic_origin')
    assert any('Analysis coverage is incomplete' in s for s in record['reliability_limitations'])
    assert missing[4]['decision']['limitations']==hypotheses(missing[4])['synthetic_origin']['limitations']==list(record['reliability_limitations'])


@pytest.mark.parametrize('legacy_tier',['Low','High','Inconclusive'])
def test_tampering_with_every_route_tier_cannot_change_selection_or_policy(monkeypatch,legacy_tier):
    sections=reference_env('instagram').sections
    baseline=logic.synthesize_overall(sections)
    original=logic.DecisionResult
    def provisional(*args,**kwargs):
        return replace(original(*args,**kwargs),confidence=legacy_tier)
    monkeypatch.setattr(logic,'DecisionResult',provisional)
    result=logic.synthesize_overall(sections)
    assert baseline[:4]==result[:4]
    assert baseline[4]['confidence_policy']==result[4]['confidence_policy']
    assert any(item['legacy_confidence']==legacy_tier for item in result[4]['decision_route_trace'] if item['matched'])


def test_branch_names_text_and_legacy_assessment_tier_are_not_policy_inputs():
    assessment=HypothesisAssessment('synthetic_origin',confidence_tier='High',decision_branch='definitely_generated',explanation='High confidence proven')
    result=evaluate_confidence(AssessmentEvidence.from_assessment(assessment),ConfidenceFacts())
    assert result.tier=='Inconclusive'


def test_policy_does_not_promote_the_highest_confidence_secondary_to_primary(monkeypatch):
    original=logic.evaluate_confidence
    def secondary_policy(evidence,facts):
        result=original(evidence,facts)
        return replace(result,tier='High',policy_rule='fixture.secondary_support') if evidence.hypothesis=='camera_acquisition' else result
    monkeypatch.setattr(logic,'evaluate_confidence',secondary_policy)
    env=reference_env('midjourney')
    selected=logic.evaluate_hypotheses(env)
    assert env.primary_hypothesis=='synthetic_origin'
    # Presentation follows the selected hypothesis, not a maximum over tiers.
    camera=next(h for h in env.hypotheses if h.hypothesis_id=='camera_acquisition')
    assert camera.confidence_tier=='High'
    result=logic.finish_decision(env,selected)
    assert result[2]=='Medium' and result[4]['decision']['primary_hypothesis']=='synthetic_origin'


def test_presentation_cannot_be_overridden_by_a_provisional_or_mutated_tier():
    env=reference_env('midjourney')
    selected=logic.evaluate_hypotheses(env)
    for assessment in env.hypotheses: assessment.confidence_tier='High'
    result=logic.finish_decision(env,replace(selected,confidence='High'))
    assert result[2]=='Medium'
    assert all(h['confidence_tier']==policy(result[4],h['hypothesis_id'])['tier'] for h in result[4]['hypothesis_assessments'])


def test_json_and_text_use_one_authoritative_policy_for_all_hypotheses():
    result=assess(reference_env('instagram'))
    trace=json.loads(json.dumps(result[4],allow_nan=False))
    hs=hypotheses(trace)
    assert trace['confidence_policy']['version']=='3'
    for record in trace['confidence_policy']['assessments']:
        h=hs[record['hypothesis']]
        assert h['confidence_tier']==record['tier']
        assert h['confidence_policy_rule']==record['policy_rule']
        for role in ('supporting_evidence','contradicting_evidence','moderating_evidence','contextual_evidence'):
            assert h[role]==record[role]
        assert h['limitations']==record['reliability_limitations']
        assert h['confidence_rationale']==record['rationale']
    primary=trace['decision']['primary_hypothesis']
    assert result[2]==hs[primary]['confidence_tier']==policy(trace,primary)['tier']
    assert 'Confidence Policy' in build_reasoning_trace_text(trace)
    for item in trace['decision_route_trace']:
        if item['matched']: assert item['confidence_source']


def test_summary_gui_consumption_and_coverage_are_compatible():
    keys=('ela','noise','sensor_origin','region_masks','segmentation_alignment','region_fft','cross_signal','boundary_focus','fft','subject_boundary','subject_texture_consistency','subject_process_asymmetry','subject_material_realism','patch_similarity','patch_spatial','compression_history','cfa_demosaic')
    state=SimpleNamespace(**{key+'_payload':None for key in keys})
    state.exif_payload={'signals':[{'id':'DECLARED_SYNTHETIC'}]}
    state.analysis_mode='subject_based';state.analysis_coverage={'status':'partial','unavailable_stages':['Subject texture consistency analysis']}
    summary=build_summary_result(state,evidence_dependency_shadow=True)
    assert summary.overall_confidence=='Medium'
    record=policy(summary.reasoning_trace,'synthetic_origin')
    assert record['tier']==summary.overall_confidence
    assert 'synthetic.unverified_generation_declaration' in summary.full_text
    assert 'synthetic.unverified_generation_declaration' in summary.full_html
    assert summary.reasoning_trace['decision']['limitations']==list(record['reliability_limitations'])
    assert summary.reasoning_trace['evidence_dependency_analysis']['policy']=='structural_restatement_only'


@pytest.mark.parametrize('case',['instagram','midjourney'])
def test_scorecard_shadow_and_corroboration_audits_are_unchanged_by_policy(case):
    env=reference_env(case)
    original=deepcopy(asdict(env.card))
    # Use a recomputed card for replay; the old reference_env deliberately injects legacy values.
    sections=env.sections
    plain=logic.synthesize_overall(sections)
    shadow=logic.synthesize_overall(sections,evidence_dependency_shadow=True)
    assert plain[:4]==shadow[:4]
    assert plain[4]['scorecard_calculation']==shadow[4]['scorecard_calculation']
    assert plain[4]['corroboration_audit']==shadow[4]['corroboration_audit']
    replay=reconstruct_scorecard_calculation(plain[4]['scorecard_calculation'])
    assert replay['suspicious_score']==pytest.approx(plain[4]['scorecard']['suspicious_score'])
    assess(env)
    assert asdict(env.card)==original


def test_invalid_scorecard_has_named_inconclusive_policy_for_every_assessment():
    result=logic.synthesize_overall({'boundary':section('bad','x',score=float('nan'))})
    assert result[2]=='Inconclusive'
    assert all(r['tier']=='Inconclusive' and r['policy_rule']=='integrity.invalid_scorecard' for r in result[4]['confidence_policy']['assessments'])


def test_policy_snapshots_are_immutable_and_unknown_hypothesis_is_conservative():
    facts=ConfidenceFacts()
    with pytest.raises(FrozenInstanceError): facts.suspicious=9
    with pytest.raises(ValueError): AssessmentEvidence('synthetic_origin',supporting_evidence=[])
    with pytest.raises(ValueError): ConfidenceFacts(findings=(('synthetic_origin',('route_high',)),))
    result=evaluate_confidence(AssessmentEvidence('future_hypothesis'),facts)
    assert result.tier=='Inconclusive' and result.policy_rule=='scope.unknown_hypothesis'
