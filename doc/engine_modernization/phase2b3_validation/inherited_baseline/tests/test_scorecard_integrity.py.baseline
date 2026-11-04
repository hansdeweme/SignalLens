"""Mathematical scorecard tests; no private images or dependency additions."""

from copy import deepcopy
from dataclasses import asdict
from math import isclose
import json
import random

import pytest

import decision_logic as logic
from gui_semantics import ModuleSummary
from hypothesis_engine import (
    build_context, build_evidence_snapshot, compute_base_scores, compute_scorecard, derive_signals,
)
from reasoning_persistence import build_reasoning_trace_text
from scorecard_integrity import (
    COMPONENT_FIELDS, ScorecardIntegrityError, camera_attenuation,
    reconstruct_scorecard_calculation, validate_scorecard,
)
from test_reasoning import metadata, section


def calculate(sections=None, context=None):
    sections = sections or {}
    ev = build_evidence_snapshot(sections)
    ds = derive_signals(ev)
    return compute_scorecard(sections, build_context(context), ev, ds)


def boundary_sections(ratio=0.04, geometry_bad=False):
    sections = {
        "boundary": section("boundary", "possible_foreground_background_processing_mismatch"),
        "cross_signal": section("cross", "strong_hotspot_convergence"),
        "region_masks": section("regions", "region_segmentation_generated", polarity="neutral", details={
            "source": "person_subject_mask", "person_mask_reliability": "high",
            "subject_ratio": 0.5, "boundary_ratio": ratio,
        }),
    }
    if geometry_bad:
        sections["subject_process_asymmetry"] = section(
            "geometry", "geometry_diagnostic", polarity="neutral", score=None,
            details={"region_geometry_unreliable": True},
        )
    return sections


def assert_close(actual, expected):
    assert isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (actual, expected)


def independent_reconstruction(calc):
    """Deliberately independent replay: no production calculator/validator calls."""
    weights = {"weak": 0.5, "medium": 1.5, "strong": 3.0}
    bases = {}
    for polarity in ("suspicious", "benign"):
        rows = [row for row in calc["base_evidence"] if row["polarity"] == polarity]
        domains = {row["domain"] for row in rows if row["domain"]}
        bases[polarity] = sum(weights[row["status"]] for row in rows) + max(0, len(domains) - 1) * 0.25
    components = dict.fromkeys(COMPONENT_FIELDS, 0.0)
    for op in calc["component_operations"]:
        field, operand = op["field"], op["operand"]
        if op["operation"] == "add":
            components[field] += operand
        elif op["operation"] == "multiply":
            components[field] *= operand
        elif op["operation"] == "maximum":
            components[field] = max(components[field], operand)
        else:
            pytest.fail("Unexpected arithmetic operation")
    t = calc["aggregate_transforms"]
    subtotal = bases["suspicious"] + sum(components[f] for f in (
        "synthetic_boost", "edit_boost", "provenance_boost", "sensor_boost", "compression_boost",
    ))
    score = max(0, subtotal * t["camera_multiplier"] - components["caution_penalty"])
    return score * t["geometry_multiplier"] * t["photo_context_multiplier"], bases["benign"]


def test_no_evidence_has_no_fabricated_support_or_penalty():
    card = calculate()
    assert all(getattr(card, key) == 0 for key in (*COMPONENT_FIELDS, "suspicious_score", "benign_score"))
    assert card.suspicious_domains == card.benign_domains == set()
    validate_scorecard(card)


@pytest.mark.parametrize("status, expected", [("weak", 0.5), ("medium", 1.5), ("strong", 3.0)])
@pytest.mark.parametrize("polarity", ["suspicious", "benign"])
def test_one_observation_uses_existing_status_weight(status, expected, polarity):
    card = calculate({"measurement": section("one", "measured", status=status, polarity=polarity, score=0.0)})
    assert_close(getattr(card, f"{polarity}_score"), expected)
    other = "benign" if polarity == "suspicious" else "suspicious"
    assert getattr(card, f"{other}_score") == 0


def test_suspicious_and_benign_have_separate_domain_accounting():
    sections = {
        "a": section("a", "observed"), "b": section("b", "observed", status="medium"),
        "c": section("c", "observed", polarity="benign"),
    }
    card = calculate(sections)
    assert_close(card.suspicious_score, 4.75)
    assert_close(card.benign_score, 3.0)
    assert card.suspicious_domains == {"a", "b"}
    assert card.benign_domains == {"c"}


def test_full_reliability_leaves_mechanism_components_unchanged():
    card = calculate(boundary_sections())
    assert_close(card.local_edit_support_score, 3.0)
    assert_close(card.edit_boost, 0.54)
    assert card.caution_penalty == 0
    assert_close(card.suspicious_score, 6.79)


def test_reduced_reliability_changes_components_before_aggregation():
    card = calculate(boundary_sections(0.02))
    assert_close(card.local_edit_support_score, 2.25)
    assert_close(card.edit_boost, 0.405)
    assert_close(card.caution_penalty, 0.25)
    assert_close(card.suspicious_score, 6.405)
    assert card.suspicious_score != 6.79  # The historical stale total.


def test_zero_reliability_removes_unsupported_mechanism_boost():
    sections = boundary_sections()
    del sections["region_masks"]
    card = calculate(sections)
    assert card.local_edit_support_score == card.edit_boost == 0
    assert card.caution_penalty == 1
    assert_close(card.suspicious_score, 5.25)
    assert "regions" not in card.suspicious_domains


def test_multiple_reliability_adjustments_are_applied_once_in_declared_order():
    card = calculate(boundary_sections(0.02, geometry_bad=True))
    assert_close(card.local_edit_support_score, 3.0 * 0.45 * 0.75)
    assert_close(card.edit_boost, 0.54 * 0.45 * 0.75)
    assert_close(card.caution_penalty, 1.25)
    assert_close(card.suspicious_score, (6.25 + 0.54 * 0.45 * 0.75 - 1.25) * 0.75)
    for field in ("local_edit_support_score", "edit_boost"):
        ops = [op for op in card.calculation["component_operations"] if op["field"] == field and op["operation"] == "multiply"]
        assert [op["operand"] for op in ops] == [0.45, 0.75]


def test_context_prior_is_centralized_without_double_counting_measured_camera():
    sections = boundary_sections(0.02, geometry_bad=True)
    sections["metadata"] = metadata("CAMERA_METADATA_RICH")
    context = {"smartphone_computational": True}
    card = calculate(sections, context)
    env = logic.build_decision_env(sections, context)
    assert asdict(card) == asdict(env.card)
    assert card.camera_counter_support == 3.0  # 1.5 measured + 1.5 contextual routing bonus.
    assert_close(card.caution_penalty, 1.5 + 0.4 + 1.0 + 1.0 + 0.25)
    assert card.calculation["aggregate_transforms"]["camera_multiplier"] == 0.85
    expected = max(0, (6.25 + 0.54 * 0.45 * 0.75) * 0.85 - 4.15) * 0.75 * 0.70
    assert_close(card.suspicious_score, expected)


@pytest.mark.parametrize("status", ["not_run", "unavailable", "skipped", "failed", "error", "inconclusive"])
def test_unavailable_and_inconclusive_patterns_do_not_activate_evidence(status):
    sections = {
        "sensor_origin": section("sensor", "camera_like_acquisition_supported", status=status, polarity="benign"),
        "boundary": section("boundary", "possible_foreground_background_processing_mismatch", status=status),
        "patch_similarity": section("patch", "possible_clone_reuse", status=status, score=0.99, details={"coverage_ratio": 0.0}),
        "metadata": section("metadata", "declared_synthetic_candidate", status=status),
    }
    card = calculate(sections)
    assert card.suspicious_score == card.benign_score == 0
    assert all(getattr(card, key) == 0 for key in COMPONENT_FIELDS)
    assert card.suspicious_domains == card.benign_domains == set()
    result = logic.synthesize_overall(sections)
    assert result[3] == "neutral"


def test_missing_metadata_supplies_no_provenance_boost():
    card = calculate({"metadata": None})
    assert card.provenance_boost == 0


def test_null_patch_coverage_is_not_a_compactness_observation():
    missing = calculate({"patch_similarity": section("patch", "no_reuse", polarity="neutral", score=None)})
    null = calculate({"patch_similarity": section("patch", "no_reuse", polarity="neutral", score=None, details={"coverage_ratio": None})})
    zero = calculate({"patch_similarity": section("patch", "no_reuse", polarity="neutral", score=0.0, details={"coverage_ratio": 0.0})})
    assert missing.clone_support_score == null.clone_support_score == 0
    # Preserve the existing coefficient for an actual zero-valued observation.
    assert_close(zero.clone_support_score, 0.35)


def test_null_optional_scores_do_not_create_numeric_material_support():
    card = calculate({"subject_material_realism": section("material", "subject_material_realism_supported", status="weak", polarity="benign", score=None)})
    assert card.synthetic_boost == card.edit_boost == 0
    assert card.benign_score == 0.5  # Qualitative weak observation, not a fabricated zero score.


def test_repeated_evaluation_does_not_mutate_shared_inputs():
    sections = boundary_sections(0.02, True)
    before = deepcopy(sections)
    first = calculate(sections)
    second = calculate(sections)
    assert asdict(first) == asdict(second)
    assert sections == before
    assert first is not second and first.calculation is not second.calculation


def test_evidence_insertion_order_does_not_change_the_calculation():
    sections = boundary_sections(0.02, True)
    sections.update(metadata=metadata("DECLARED_SYNTHETIC"), patch_similarity=section("patch", "possible_clone_reuse", details={"coverage_ratio": 0.12}))
    expected = asdict(calculate(sections))
    rng = random.Random(2026)
    for _ in range(20):
        items = list(sections.items())
        rng.shuffle(items)
        assert asdict(calculate(dict(items))) == expected


@pytest.mark.parametrize("number", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("location", ["score", "detail"])
def test_nonfinite_input_is_rejected_purely_and_withheld_in_production(number, location):
    sections = {"fft": section("fft", "possible_decoder_grid_signature", score=number if location == "score" else 0.9,
                               details={"fft_anomaly_score": number} if location == "detail" else {})}
    with pytest.raises(ScorecardIntegrityError):
        calculate(sections)
    result = logic.synthesize_overall(sections)
    assert result[0] == "scorecard_invalid"
    assert result[2:4] == ("Inconclusive", "neutral")
    trace = json.loads(json.dumps(result[4], allow_nan=False))
    assert trace["scorecard"]["is_valid"] is False
    assert trace["scorecard_calculation"]["status"] == "invalid"
    assert all(h["confidence_tier"] == "Inconclusive" for h in trace["hypothesis_assessments"])


@pytest.mark.parametrize("reliability", [-0.01, 1.01, float("nan"), float("inf")])
def test_invalid_reliability_is_not_arbitrarily_clipped(reliability):
    sections = boundary_sections()
    ev = build_evidence_snapshot(sections)
    ds = derive_signals(ev)
    ds.boundary_reliability_score = reliability
    with pytest.raises(ScorecardIntegrityError):
        compute_scorecard(sections, build_context(None), ev, ds)


@pytest.mark.parametrize("support, expected", [(0, 1), (1 - 1e-9, 1), (1, 0.85), (2 - 1e-9, 0.85), (2, 0.70), (3 - 1e-9, 0.70), (3, 0.55), (100, 0.55)])
def test_existing_camera_attenuation_boundaries(support, expected):
    assert camera_attenuation(support) == expected


def test_existing_zero_floors_are_preserved_without_capping_large_scores():
    card = calculate({"sensor_origin": section("sensor", "camera_like_acquisition_supported", polarity="benign")})
    assert card.suspicious_score == card.clone_support_score == 0
    assert card.local_edit_support_score == -0.2  # Intentional signed camera tempering.
    large = calculate({str(i): section(str(i), "observed") for i in range(20)})
    assert large.suspicious_score > 1
    validate_scorecard(large)


@pytest.mark.parametrize("kind", ["component", "aggregate", "raw", "penalties", "reliability", "duplicate"])
def test_validator_detects_inconsistent_or_duplicated_calculations(kind):
    card = calculate(boundary_sections(0.02, True))
    if kind == "component":
        card.edit_boost += 1
    elif kind == "aggregate":
        card.calculation["aggregate_scores"]["suspicious_score"] += 1
    elif kind == "raw":
        card.calculation["raw_contributions"]["edit_boost"] += 1
    elif kind == "penalties":
        card.calculation["penalties"] = []
    elif kind == "reliability":
        card.calculation["reliability_adjustments"]["boundary_reliability"] = 2
    else:
        operation = next(o for o in card.calculation["component_operations"] if o["reason"] == "boundary_reliability")
        card.calculation["component_operations"].append(dict(operation))
    with pytest.raises(ScorecardIntegrityError):
        validate_scorecard(card)


def test_serialized_trace_is_independently_reconstructable_and_rendered():
    result = logic.synthesize_overall(boundary_sections(0.02, True))
    trace = json.loads(json.dumps(result[4], allow_nan=False))
    calc = trace["scorecard_calculation"]
    expected_suspicious, expected_benign = independent_reconstruction(calc)
    assert_close(trace["scorecard"]["suspicious_score"], expected_suspicious)
    assert_close(trace["scorecard"]["benign_score"], expected_benign)
    assert "calculation" not in trace["scorecard"]  # Audit is stored once at top level.
    assert "Scorecard Calculation" in build_reasoning_trace_text(trace)


def test_unknown_status_is_an_explicit_invalid_contract():
    result = logic.synthesize_overall({"measurement": section("unknown", "observed", status="mystery")})
    assert result[0] == "scorecard_invalid" and result[2] == "Inconclusive"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), "true", 1])
def test_invalid_context_flags_do_not_activate_adjustments(value):
    result = logic.synthesize_overall({"metadata": metadata("CAMERA_METADATA_RICH")}, scene_context={"smartphone_computational": value})
    assert result[0] == "scorecard_invalid"
    assert result[2:4] == ("Inconclusive", "neutral")
    json.dumps(result[4], allow_nan=False)


def test_inconsistent_derived_flags_cannot_invent_support_from_missing_evidence():
    ev = build_evidence_snapshot({})
    ds = derive_signals(ev)
    ds.metadata_synthetic = True
    with pytest.raises(ScorecardIntegrityError, match="do not match available evidence"):
        compute_scorecard({}, build_context(None), ev, ds)


@pytest.mark.parametrize("status", ["not_run", "unavailable", "inconclusive"])
def test_unavailable_nonfinite_stale_values_do_not_affect_valid_evidence(status):
    sections = {
        "metadata": metadata("DECLARED_SYNTHETIC"),
        "fft": section("fft", "possible_decoder_grid_signature", status=status, score=float("nan")),
    }
    result = logic.synthesize_overall(sections)
    assert result[0] == "provenance_supported_synthetic_context"
    assert result[2:4] == ("Medium", "suspicious")
    assert result[4]["scorecard"]["is_valid"]
    json.dumps(result[4], allow_nan=False)


def test_all_boost_families_and_existing_context_multipliers_reconcile():
    sections = boundary_sections(0.02)
    sections.update({
        "region_masks": section("regions", "fragmented_subject_mask", polarity="neutral", details={
            "source": "person_subject_mask", "person_mask_reliability": "high", "boundary_ratio": 0.02,
        }),
        "metadata": metadata("DECLARED_SYNTHETIC", "CAMERA_METADATA_RICH"),
        "sensor_origin": section("sensor", "localized_sensor_trace_inconsistency"),
        "cfa_demosaic": section("cfa", "camera_like_cfa_supported", polarity="benign"),
        "compression_history": section("compression", "localized_compression_inconsistency"),
        "subject_boundary": section("subject", "possible_subject_background_segmentation_artifact"),
        "subject_material_realism": section("material", "subject_material_realism_failure_strong", score=0.65),
        "subject_process_asymmetry": section("asymmetry", "subject_process_asymmetry_strong"),
        "fft": section("fft", "possible_decoder_grid_signature", score=0.95, details={
            "fft_anomaly_score": 0.95, "peak_periodicity_score": 0.8,
            "peak_symmetry_score": 0.8, "peak_count": 8, "axis_bias_score": 0.8,
        }),
        "patch_similarity": section("patch", "possible_synthetic_texture_repetition", score=0.95, details={
            "repetition_score": 0.8, "spatially_separated_pair_count": 12, "pair_count": 20,
            "mean_similarity": 0.95, "max_similarity": 0.99, "coverage_ratio": 0.1,
        }),
    })
    context = {"natural_repetition": True, "decorative_geometric": True, "smartphone_computational": True, "screen_origin": True}
    card = calculate(sections, context)
    assert_close(card.synthetic_boost, 2.25 * 0.75 * 0.85 * 0.85 * 0.50 * 0.60)
    assert card.sensor_boost == card.compression_boost == card.provenance_boost == 0.75
    assert not card.calculation["aggregate_transforms"]["photo_context_prior"]
    reconstructed, benign = independent_reconstruction(card.calculation)
    assert_close(reconstructed, card.suspicious_score)
    assert_close(benign, card.benign_score)


def test_randomized_calculations_are_finite_deterministic_and_reconstructable():
    # Hypothesis is not installed; use deterministic generated combinations.
    rng = random.Random(9137)
    for _ in range(250):
        sections = boundary_sections(rng.choice([0.002, 0.01, 0.02, 0.04]), rng.choice([False, True]))
        for key in list(sections):
            if rng.random() < 0.25:
                del sections[key]
        if rng.random() < 0.6:
            sections["metadata"] = metadata(rng.choice(["DECLARED_SYNTHETIC", "CAMERA_METADATA_RICH", "METADATA_STRIPPED_OR_SPARSE"]))
        if rng.random() < 0.6:
            sections["patch_similarity"] = section("patch", "possible_clone_reuse", score=rng.choice([None, 0, 0.9]), details={"coverage_ratio": rng.choice([None, 0, 0.12, 0.4])})
        if rng.random() < 0.5:
            sections["sensor_origin"] = section("sensor", "camera_like_acquisition_supported", polarity="benign")
        for s in sections.values():
            if rng.random() < 0.15:
                s.status = rng.choice(["not_run", "unavailable", "inconclusive"])
        context = {"smartphone_computational": rng.choice([False, True]), "natural_repetition": rng.choice([False, True])}
        card = calculate(sections, context)
        validate_scorecard(card)
        decoded = json.loads(json.dumps(card.calculation, allow_nan=False))
        result = reconstruct_scorecard_calculation(decoded)
        independent_s, independent_b = independent_reconstruction(decoded)
        assert_close(result["suspicious_score"], independent_s)
        assert_close(result["benign_score"], independent_b)
        assert asdict(card) == asdict(calculate(sections, context))


@pytest.mark.parametrize("case, pattern, tier", [
    ("midjourney", "provenance_supported_synthetic_context", "Medium"),
    ("instagram", "possible_foreground_background_processing_mismatch", "High"),
])
def test_reference_fixtures_use_recomputed_scores_and_valid_audits(case, pattern, tier):
    sections = boundary_sections()
    if case == "midjourney":
        sections["metadata"] = metadata("DECLARED_SYNTHETIC")
        del sections["region_masks"]
    else:
        sections["subject_boundary"] = section("subject", "possible_subject_background_segmentation_artifact")
        sections["boundary_focus"] = section("focus", "boundary_focused_processing_mismatch")
        sections["metadata"] = metadata("METADATA_STRIPPED_OR_SPARSE")
    result = logic.synthesize_overall(sections)
    assert result[0] == pattern and result[2] == tier
    score, benign = independent_reconstruction(result[4]["scorecard_calculation"])
    assert_close(score, result[4]["scorecard"]["suspicious_score"])
    assert_close(benign, result[4]["scorecard"]["benign_score"])
