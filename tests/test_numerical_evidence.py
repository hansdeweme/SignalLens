"""Production numerical identity/restatement allocation and independent replay."""
from copy import deepcopy
import json
from math import fsum

import pytest

import decision_logic as logic
from evidence_lineage import Addition, EvidenceSpec, Family, Kind, validate_registry
from numerical_evidence import allocate_base_evidence
from reasoning_persistence import build_reasoning_trace_text
from scorecard_integrity import ScorecardIntegrityError, reconstruct_scorecard_calculation, validate_scorecard
from test_reasoning import metadata, section
from test_scorecard_integrity import boundary_sections, calculate


def overlap_sections():
    data = boundary_sections()
    data['boundary'] = section('boundary', 'possible_boundary_fragment_convergence', status='weak')
    data.update({key: section(key, 'inconclusive', status='inconclusive', polarity='neutral')
                 for key in ('ela', 'noise')})
    return data


def allocations(card):
    return {a['section']: a for a in card.calculation['numerical_deduplication']['contributions']}


@pytest.mark.parametrize('polarity', ['suspicious', 'benign'])
def test_identical_observation_repeated_in_production_gets_one_base_credit(polarity):
    observation = section('measurement', 'observed', polarity=polarity)
    single = calculate({'one': observation})
    repeated = calculate({'three': observation, 'one': observation, 'two': observation})
    assert repeated.suspicious_score == single.suspicious_score
    assert repeated.benign_score == single.benign_score
    assert sum(a['credited_contribution'] for a in allocations(repeated).values()) == 3
    assert sorted(a['classification'] for a in allocations(repeated).values()) == ['A', 'A', 'D']


def test_registered_key_wins_alias_identity_without_affecting_real_primary():
    primary = section('sensor', 'camera_like_acquisition_supported', polarity='benign')
    card = calculate({'aaa_alias': primary, 'sensor_origin': primary})
    assert allocations(card)['sensor_origin']['credited_contribution'] == 3
    assert allocations(card)['aaa_alias']['suppressed_contribution'] == 3
    assert card.benign_score == 3


def test_equal_valued_distinct_measurements_are_not_deduplicated_by_content():
    first = section('measurement', 'observed')
    card = calculate({'one': first, 'two': deepcopy(first)})
    assert card.suspicious_score == 6
    assert all(a['credited_contribution'] == 3 for a in allocations(card).values())


def test_fragment_restatement_and_its_domain_are_suppressed_in_public_synthesis():
    data = overlap_sections()
    output = logic.synthesize_overall(data)
    assert len(output) == 5
    card = calculate(data)
    audit = allocations(card)
    assert audit['boundary']['classification'] == 'B'
    assert audit['boundary']['raw_contribution'] == .5
    assert audit['boundary']['credited_contribution'] == 0
    assert audit['boundary']['previously_credited_evidence'] == ['evidence:cross_signal']
    assert card.calculation['base_suspicious'] == 3
    assert card.suspicious_domains == {'cross'}
    assert output[4]['scorecard']['suspicious_score'] == card.suspicious_score
    # The same restatement cannot re-enter via mechanism or conversion paths.
    assert card.local_edit_support_score == 1.0
    assert card.edit_boost == pytest.approx(.18)
    component_rows = card.calculation['numerical_deduplication']['component_allocations']
    assert [r['raw_contribution'] for r in component_rows] == [.5, .5]
    recon = card.calculation['numerical_deduplication']['aggregate_reconciliation']['suspicious']
    assert recon['suppressed_base_weight'] == .5
    assert recon['raw_domain_bonus'] - recon['credited_domain_bonus'] == .25


@pytest.mark.parametrize('status', ['not_run', 'unavailable', 'skipped', 'failed', 'error', 'inconclusive'])
def test_inactive_source_cannot_erase_a_standalone_observed_overlap(status):
    data = overlap_sections()
    data['cross_signal'].status = status
    card = calculate(data)
    assert allocations(card)['boundary']['credited_contribution'] == .5
    assert 'cross_signal' not in allocations(card)


def test_missing_source_preserves_one_observed_representation_without_invented_ancestry():
    data = overlap_sections()
    del data['cross_signal']
    del data['ela']
    del data['noise']
    row = allocations(calculate(data))['boundary']
    assert row['credited_contribution'] == .5
    assert row['measurement_ancestry'] == []
    assert row['missing_dependencies'] and row['unresolved']


def test_measured_contour_and_localization_keep_full_existing_contributions():
    data = boundary_sections()
    data.update({key: section(key, 'inconclusive', status='inconclusive', polarity='neutral')
                 for key in ('ela', 'noise')})
    data['boundary_focus'] = section('focus', 'boundary_focused_processing_mismatch', status='medium')
    data['patch_similarity'] = section('patch', 'possible_clone_reuse', status='medium')
    data['patch_spatial'] = section('spatial', 'subject_localized_patch_recurrence', status='medium')
    data['segmentation_alignment'] = section('alignment', 'boundary_aligned_processing_artifacts')
    rows = allocations(calculate(data))
    for key in ('boundary', 'cross_signal', 'boundary_focus', 'patch_spatial', 'segmentation_alignment'):
        assert rows[key]['classification'] == 'C'
        assert rows[key]['credited_contribution'] == rows[key]['raw_contribution']
        assert rows[key]['suppressed_contribution'] == 0


def test_uncertain_shared_surface_information_is_preserved_and_flagged():
    data = overlap_sections()
    data['subject_texture_consistency'] = section('texture', 'subject_texture_inconsistency', status='medium')
    data['subject_process_asymmetry'] = section('asymmetry', 'subject_process_asymmetry_strong')
    row = allocations(calculate(data))['subject_process_asymmetry']
    assert row['classification'] == 'D' and row['unresolved']
    assert row['credited_contribution'] == row['raw_contribution']
    assert 'measurement:masked_hybrid_texture_descriptors' in row['measurement_ancestry']


def test_contradictory_polarity_is_not_erased_by_related_supporting_measurement():
    data = overlap_sections()
    data['cross_signal'].polarity = 'benign'
    card = calculate(data)
    assert allocations(card)['boundary']['credited_contribution'] == .5
    assert card.benign_score == 3


def test_mixed_provenance_and_visual_measurements_remain_distinct_and_unverified():
    data = overlap_sections()
    data['metadata'] = metadata('DECLARED_SYNTHETIC')
    result = logic.synthesize_overall(data)
    row = allocations(calculate(data))['metadata']
    assert row['credited_contribution'] == row['raw_contribution']
    synthetic = next(h for h in result[4]['hypothesis_assessments'] if h['hypothesis_id'] == 'synthetic_origin')
    assert synthetic['confidence_policy_rule'] == 'synthetic.unverified_generation_declaration'


def test_rejected_mask_does_not_create_a_new_region_contribution():
    data = overlap_sections()
    data['region_masks'].status = 'unavailable'
    data['patch_spatial'] = section('spatial', 'subject_localized_patch_recurrence', status='unavailable')
    card = calculate(data)
    assert 'patch_spatial' not in allocations(card)
    assert card.edit_boost == 0
    assert card.local_edit_support_score == 0


def test_order_repeated_evaluation_and_inputs_are_stable():
    data = overlap_sections()
    before = deepcopy(data)
    first = logic.synthesize_overall(data)
    assert first == logic.synthesize_overall(dict(reversed(list(data.items()))))
    assert first == logic.synthesize_overall(data)
    assert data == before


def test_shadow_corroboration_and_policy_receive_adjusted_production_score():
    data = overlap_sections()
    plain = logic.synthesize_overall(data)
    shadow = logic.synthesize_overall(data, evidence_dependency_shadow=True)
    diag = shadow[4].pop('evidence_dependency_analysis')
    assert shadow == plain
    assert diag['comparison']['suspicious_score']['difference'] == 0
    assert diag['domain_accounting']['production_suspicious_bonus'] == 0
    assert 'evidence:boundary' not in diag['corroboration_gates']['suspicious_domain_bonus']['production_indicator_ids']
    suppressed = [r for r in diag['component_lineage'] if r['difference'] < 0]
    assert len(suppressed) == 2 and all(r['raw_contribution'] == .5 for r in suppressed)
    facts = logic.build_decision_env(data)
    assert facts.card.suspicious_score == plain[4]['scorecard']['suspicious_score']
    assert plain[4]['corroboration_audit']
    assert plain[4]['confidence_policy']


def test_adjusted_ledger_independently_reconstructs_after_json_serialization():
    card = calculate(overlap_sections())
    calc = json.loads(json.dumps(card.calculation, allow_nan=False))
    rows = calc['base_evidence']
    bases = {}
    for polarity in ('suspicious', 'benign'):
        selected = [r for r in rows if r['polarity'] == polarity]
        domains = {r['domain'] for r in selected if r['credited_weight'] and r['domain']}
        bases[polarity] = fsum(r['credited_weight'] for r in selected) + .25 * max(0, len(domains) - 1)
    components = dict.fromkeys(calc['raw_contributions'], 0.)
    for op in calc['component_operations']:
        field, value = op['field'], op['operand']
        if op['operation'] == 'add': components[field] += value
        elif op['operation'] == 'multiply': components[field] *= value
        else: components[field] = max(components[field], value)
    t = calc['aggregate_transforms']
    q = bases['suspicious'] + fsum(components[k] for k in ('edit_boost', 'synthetic_boost', 'provenance_boost', 'sensor_boost', 'compression_boost'))
    expected = max(0, q * t['camera_multiplier'] - components['caution_penalty']) * t['geometry_multiplier'] * t['photo_context_multiplier']
    assert card.suspicious_score == pytest.approx(expected)
    assert reconstruct_scorecard_calculation(calc)['suspicious_score'] == pytest.approx(expected)
    text = build_reasoning_trace_text(logic.synthesize_overall(overlap_sections())[4])
    assert 'Production Numerical Evidence Allocation' in text and 'suppressed=0.5' in text


@pytest.mark.parametrize('mutation', ['credit', 'suppressed', 'category', 'missing_audit', 'domain'])
def test_corrupted_allocation_cannot_pass_integrity_validation(mutation):
    card = calculate(overlap_sections())
    calc = card.calculation
    row = calc['numerical_deduplication']['contributions'][0]
    if mutation == 'credit': row['credited_contribution'] = .25
    elif mutation == 'suppressed': row['suppressed_contribution'] = 10
    elif mutation == 'category': row['classification'] = 'D'
    elif mutation == 'missing_audit': del calc['numerical_deduplication']
    else: calc['numerical_deduplication']['aggregate_reconciliation']['suspicious']['credited_domain_bonus'] = 99
    with pytest.raises(ScorecardIntegrityError): validate_scorecard(card)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf'), True])
def test_invalid_numerical_input_remains_controlled_in_public_synthesis(value):
    data = overlap_sections()
    data['cross_signal'].score = value
    result = logic.synthesize_overall(data)
    assert result[0] == 'scorecard_invalid'
    assert result[2:4] == ('Inconclusive', 'neutral')
    assert result[4]['confidence_policy']


def test_registered_pure_restatement_descendants_share_one_counted_ancestor():
    specs = [EvidenceSpec('p', 'test.primary', Family.PROCESSING, ('m',), hypotheses=('localized_editing',))]
    for i in range(3):
        specs.append(EvidenceSpec('child' + str(i), 'test.restatement', Family.PROCESSING, (), ('p',),
                                  hypotheses=('localized_editing',), kind=Kind.DERIVED, addition=Addition.RESTATEMENT))
    registry = validate_registry(specs)
    data = {s.key: section(s.key, 'observed') for s in specs}
    rows = [{'section': k, 'status': s.status, 'polarity': s.polarity, 'domain': s.domain, 'weight': 3.}
            for k, s in data.items()]
    allocated, audit = allocate_base_evidence(data, rows, registry=registry)
    assert sum(r['credited_weight'] for r in allocated) == 3
    assert sum(a['suppressed_contribution'] for a in audit['contributions']) == 9
    data['p'].status = 'unavailable'
    allocated, _ = allocate_base_evidence(data, [r for r in rows if r['section'] != 'p'], registry=registry)
    assert sum(r['credited_weight'] for r in allocated) == 0


def test_historical_2a_ledger_still_reconstructs_without_new_fields():
    card = calculate(boundary_sections())
    calc = deepcopy(card.calculation)
    del calc['numerical_deduplication']
    for row in calc['base_evidence']: del row['credited_weight']
    assert reconstruct_scorecard_calculation(calc)['suspicious_score'] == card.suspicious_score


@pytest.mark.parametrize('mutation', ['operand', 'raw_operand', 'factor', 'missing'])
def test_component_restatement_adjustment_is_independently_validated(mutation):
    card = calculate(overlap_sections())
    audit = card.calculation['numerical_deduplication']
    row = audit['component_allocations'][0]
    op = card.calculation['component_operations'][row['ledger_index']]
    if mutation == 'operand': op['operand'] = .5
    elif mutation == 'raw_operand': op['raw_operand'] = .4
    elif mutation == 'factor': row['reliability_multiplier'] = .5
    else: audit['component_allocations'] = []
    with pytest.raises(ScorecardIntegrityError): validate_scorecard(card)


def test_duplicate_contribution_identifier_is_rejected_before_allocation():
    row = {'section': 'p', 'status': 'strong', 'polarity': 'suspicious', 'domain': 'p', 'weight': 3.}
    with pytest.raises(ScorecardIntegrityError):
        allocate_base_evidence({'p': section('p', 'observed')}, [row, row])


def test_no_positive_component_credit_is_created_for_rejected_or_missing_masks():
    data = overlap_sections()
    del data['region_masks']
    card = calculate(data)
    assert card.edit_boost == card.local_edit_support_score == 0
    assert all(r['final_adjusted_contribution'] == 0 for r in card.calculation['numerical_deduplication']['component_allocations'])
