"""Phase 1.1: evidence interpretation and reporting, independent of private images."""

import json
from dataclasses import asdict
from types import SimpleNamespace

import pytest

import decision_logic as logic
from hypothesis_evidence import ROLE_TITLES, evidence_presentation
from reasoning_persistence import build_reasoning_trace_text
from summary_sections import build_metadata_section
from summary_synthesizer import build_summary_result
from test_reasoning import (
    MIDJOURNEY_DESCRIPTION, IPTC_SOURCE_TYPE, assess, hypotheses, metadata,
    payload_from_record, reference_env, section,
)


def primary(trace):
    return hypotheses(trace)[trace["decision"]["primary_hypothesis"]]


def test_midjourney_support_and_counterevidence_are_scoped():
    env = reference_env("midjourney")
    env.sections["metadata"] = build_metadata_section(payload_from_record({
        "PNG:Description": MIDJOURNEY_DESCRIPTION,
        "XMP-iptcExt:DigitalSourceType": IPTC_SOURCE_TYPE + "trainedAlgorithmicMedia",
    }))
    env.sections["patch_similarity"] = section("patch", "possible_clone_reuse")
    env.sections["boundary_focus"] = section(
        "boundary_focus", "boundary_processing_convergence_supported", status="weak", polarity="benign", score=0.0,
    )
    # Preserve the supplied local/camera card, but derive metadata from extraction.
    env.ev = logic.build_evidence_snapshot(env.sections)
    env.ds = logic.derive_signals(env.ev)
    result = assess(env)
    assert result[0] == "provenance_supported_synthetic_context"
    assert result[2:4] == ("Medium", "suspicious")
    trace = result[4]
    hs = hypotheses(trace)
    assert trace["decision"]["supporting_signals"] == ["declared_synthetic_candidate", "embedded_generation_prompt_detected"]
    assert trace["decision"]["contradicting_signals"] == []
    assert "sensor_origin:camera_like_acquisition_supported" in hs["synthetic_origin"]["moderating_evidence"]
    assert "boundary_focus:boundary_processing_convergence_supported" in hs["localized_editing"]["contradicting_evidence"]
    assert "patch_similarity:possible_clone_reuse" in hs["localized_editing"]["contextual_evidence"]
    assert hs["localized_editing"]["confidence_tier"] == "Low"
    assert hs["camera_acquisition"]["confidence_tier"] == "Medium"
    overall = result[1].split("\nsynthetic_origin:")[0]
    assert "copy-move" not in overall
    assert "boundary processing is consistent" not in overall


def test_instagram_support_is_localized_and_metadata_stays_neutral():
    env = reference_env("instagram")
    env.sections["boundary_focus"] = section("boundary_focus", "boundary_focused_processing_mismatch")
    env.sections["compression_history"] = section("compression", "localized_compression_inconsistency")
    result = assess(env)
    assert result[0] == "possible_foreground_background_processing_mismatch"
    assert result[2:4] == ("High", "suspicious")
    d = result[4]["decision"]
    assert d["primary_hypothesis"] == "localized_editing"
    assert {"boundary_focused_processing_mismatch", "localized_compression_inconsistency"} <= set(d["supporting_signals"])
    assert "sparse_or_stripped" not in d["supporting_signals"]
    assert hypotheses(result[4])["synthetic_origin"]["supporting_evidence"] == []
    assert logic.compute_base_scores({"metadata": env.sections["metadata"]})[:3] == (0.0, 0.0, set())


def test_all_three_hypotheses_remain_visible_and_deterministic():
    env = reference_env("instagram")
    env.sections["metadata"] = metadata("DECLARED_SYNTHETIC")
    env.sections["sensor_origin"] = section("sensor", "camera_like_acquisition_supported", polarity="benign")
    env = logic.build_decision_env(env.sections)
    forward = assess(env)
    reverse = assess(logic.build_decision_env(env.sections), reversed(logic.DECISION_ROUTES))
    assert forward[:4] == reverse[:4]
    assert forward[4]["decision"] == reverse[4]["decision"]
    assert forward[4]["hypothesis_assessments"] == reverse[4]["hypothesis_assessments"]
    hs = hypotheses(forward[4])
    assert (hs["synthetic_origin"]["confidence_tier"], hs["synthetic_origin"]["polarity"]) == ("Medium", "suspicious")
    assert (hs["localized_editing"]["confidence_tier"], hs["localized_editing"]["polarity"]) == ("High", "suspicious")
    assert hs["camera_acquisition"]["polarity"] == "benign"
    assert "declared_synthetic_candidate" not in forward[4]["decision"]["supporting_signals"]
    assert "metadata:DECLARED_SYNTHETIC" in hs["localized_editing"]["contextual_evidence"]
    assert "metadata:DECLARED_SYNTHETIC" not in hs["localized_editing"]["contradicting_evidence"]


def test_no_meaningful_evidence_has_no_invented_support_or_contradictions():
    result = logic.synthesize_overall({})
    assert result[0] == "inconclusive"
    assert result[2:4] == ("Inconclusive", "neutral")
    for h in result[4]["hypothesis_assessments"]:
        assert h["supporting_evidence"] == []
        assert h["contradicting_evidence"] == []
    assert result[4]["decision"]["supporting_signals"] == []
    assert result[4]["decision"]["contradicting_signals"] == []
    assert "independent forensic domains" not in result[1]
    assert "little to no strong contradicting" not in result[1]
    assert "Boundary reliability is reduced" not in result[1]
    assert "evidence still favors" not in result[1]


@pytest.mark.parametrize("record, signal_id, role, expected_polarity", [
    ({"PNG:Description": MIDJOURNEY_DESCRIPTION}, "EMBEDDED_GENERATION_PROMPT", "supporting_evidence", "suspicious"),
    ({"XMP-iptcExt:DigitalSourceType": IPTC_SOURCE_TYPE + "trainedAlgorithmicMedia"}, "DECLARED_SYNTHETIC", "supporting_evidence", "suspicious"),
    ({"XMP:Workflow": "crop and white balance for print"}, "AMBIGUOUS_WORKFLOW_METADATA", "contextual_evidence", "neutral"),
    ({"PNG:Author": "Example creator"}, "CREATOR_IDENTITY_PRESENT", "contextual_evidence", "neutral"),
    ({"File:ImageWidth": 256}, "METADATA_STRIPPED_OR_SPARSE", "contextual_evidence", "neutral"),
    ({"JUMBF:C2PA": "unverified manifest"}, "C2PA_PRESENT", "contextual_evidence", "neutral"),
])
def test_raw_metadata_to_final_assessment_preserves_original_evidence(record, signal_id, role, expected_polarity):
    payload = payload_from_record(record)
    summary = build_metadata_section(payload)
    result = logic.synthesize_overall({"metadata": summary})
    trace = json.loads(json.dumps(result[4], allow_nan=False))
    assert trace["decision"]["polarity"] == expected_polarity
    assert trace["provenance_evidence"]["metadata_authenticity_verified"] is False
    original = next(s for s in payload["signals"] if s["id"] == signal_id)
    h = hypotheses(trace)["synthetic_origin"]
    eid = "metadata:sparse_or_stripped" if signal_id == "METADATA_STRIPPED_OR_SPARSE" else f"metadata:{signal_id}"
    assert eid in h[role]
    assert h["evidence_details"][eid]["observations"] == original["evidence"]
    assert trace["evidence_snapshot"]["metadata"]["details"]["metadata_signals"] == payload["signals"]
    assert trace["derived_signals"]["metadata_synthetic"] == (expected_polarity == "suspicious")
    if role != "supporting_evidence":
        assert h["supporting_evidence"] == []


def test_ai_text_only_in_paths_does_not_survive_as_generation_evidence():
    payload = payload_from_record({
        "SourceFile": "C:/fixtures/midjourney/AI generated/example.png",
        "System:Directory": "C:/fixtures/midjourney",
    })
    trace = logic.synthesize_overall({"metadata": build_metadata_section(payload)})[4]
    h = hypotheses(trace)["synthetic_origin"]
    assert h["supporting_evidence"] == []
    assert "midjourney" not in json.dumps(h).lower()
    assert "SourceFile" not in json.dumps(h)
    assert not trace["derived_signals"]["metadata_synthetic"]


def test_conflicting_camera_metadata_and_declaration_both_survive_extraction():
    payload = payload_from_record({
        "XMP-iptcExt:DigitalSourceType": IPTC_SOURCE_TYPE + "trainedAlgorithmicMedia",
        "IFD0:Make": "Example", "IFD0:Model": "Camera", "ExifIFD:ISO": 200,
        "ExifIFD:CreateDate": "2026:01:01 12:00:00",
    })
    result = logic.synthesize_overall({"metadata": build_metadata_section(payload)})
    hs = hypotheses(result[4])
    assert "metadata:DECLARED_SYNTHETIC" in hs["synthetic_origin"]["supporting_evidence"]
    assert "metadata:camera_metadata_present" in hs["camera_acquisition"]["supporting_evidence"]
    assert "metadata:camera_metadata_present" in hs["synthetic_origin"]["moderating_evidence"]
    assert hs["synthetic_origin"]["contradicting_evidence"] == []
    assert result[2:4] == ("Medium", "suspicious")


@pytest.mark.parametrize("value", [
    "trainedAlgorithmicMedia", "Generated image", IPTC_SOURCE_TYPE + "digitalCapture",
    "https://not-iptc.example/trainedAlgorithmicMedia",
])
def test_populated_source_type_is_not_enough_for_a_generation_declaration(value):
    payload = payload_from_record({"XMP-iptcExt:DigitalSourceType": value})
    assert not payload['classification']['declared_generation']
    assert not payload['classification']['declared_enhancement']
    result = logic.synthesize_overall({"metadata": build_metadata_section(payload)})
    assert hypotheses(result[4])["synthetic_origin"]["supporting_evidence"] == []
    assert result[3] == "neutral"


def test_weak_zero_score_boundary_counterevidence_is_not_hidden():
    env = reference_env("instagram")
    env.sections["boundary_focus"] = section("focus", "boundary_processing_convergence_supported", status="weak", polarity="benign", score=0.0)
    result = assess(env)
    h = primary(result[4])
    assert result[2] == "High"  # Reporting does not recalibrate existing tiers.
    assert h["contradicting_evidence"] == ["boundary_focus:boundary_processing_convergence_supported"]
    assert h["evidence_details"][h["contradicting_evidence"][0]]["observed_score"] == 0.0
    assert "weakening a boundary-mismatch mechanism" in result[1]


def test_boundary_consistency_is_not_a_contradiction_of_clone_reuse():
    env = reference_env("instagram")
    env.card.clone_support_score = 10
    env.sections["boundary_focus"] = section("focus", "boundary_processing_convergence_supported", status="weak", polarity="benign", score=0.0)
    result = assess(env)
    assert result[0] == "possible_clone_reuse"
    assert primary(result[4])["contradicting_evidence"] == []
    assert "boundary_focus:boundary_processing_convergence_supported" in primary(result[4])["contextual_evidence"]


def test_spatial_corroboration_is_needed_to_present_copy_move_support():
    env = reference_env("instagram")
    env.sections["patch_similarity"] = section("patch", "possible_clone_reuse")
    env.sections["patch_spatial"] = section("spatial", "cross_region_patch_recurrence")
    result = assess(env)
    local = hypotheses(result[4])["localized_editing"]
    synthetic = hypotheses(result[4])["synthetic_origin"]
    assert "patch_similarity:possible_clone_reuse" in local["supporting_evidence"]
    assert "patch_similarity:possible_clone_reuse" not in synthetic["supporting_evidence"]


def test_unknown_pattern_names_do_not_infer_hypothesis_relevance():
    env = reference_env("midjourney")
    env.sections["fft"] = section("fft", "synthetic_origin_definitely_proven_by_unknown_pattern")
    env.sections["boundary_focus"] = section("focus", "boundary_anomaly_from_unknown_source")
    trace = assess(env)[4]
    assert "fft:synthetic_origin_definitely_proven_by_unknown_pattern" not in hypotheses(trace)["synthetic_origin"]["supporting_evidence"]
    assert "boundary_focus:boundary_anomaly_from_unknown_source" not in hypotheses(trace)["localized_editing"]["supporting_evidence"]


@pytest.mark.parametrize("case", ["midjourney", "instagram"])
def test_json_and_all_narratives_use_the_authoritative_assessment(case):
    result = assess(reference_env(case))
    trace = json.loads(json.dumps(result[4], allow_nan=False))
    h = primary(trace)
    presentation = evidence_presentation(h)
    d = trace["decision"]
    assert (d["confidence_tier"], d["polarity"], d["dominant_pattern"]) == (result[2], result[3], result[0])
    assert (h["confidence_tier"], h["polarity"]) == (result[2], result[3])
    top_narrative = result[1].split("\nsynthetic_origin:")[0]
    text_report = build_reasoning_trace_text(trace)
    for role in ROLE_TITLES:
        for suffix in ("evidence", "signals", "explanations"):
            key = role.replace("evidence", suffix)
            assert d[key] == presentation[key]
        for explanation in presentation[role.replace("evidence", "explanations")]:
            assert explanation in top_narrative
            assert explanation in text_report
    assert d["limitations"] == h["limitations"]
    for limitation in h["limitations"]:
        assert limitation in top_narrative
    rationale = " ".join(d["confidence_rationale"])
    for reason in d["confidence_rationale"]:
        assert reason in top_narrative
    assert "independent forensic domains" not in rationale
    assert "counterbalance" not in rationale


def test_rendering_through_summary_builders_includes_scoped_lists():
    keys = (
        "ela", "noise", "sensor_origin", "region_masks", "segmentation_alignment", "region_fft",
        "cross_signal", "boundary_focus", "fft", "subject_boundary", "subject_texture_consistency",
        "subject_process_asymmetry", "subject_material_realism", "patch_similarity", "patch_spatial",
        "compression_history", "cfa_demosaic",
    )
    state = SimpleNamespace(**{f"{key}_payload": None for key in keys})
    state.exif_payload = payload_from_record({"PNG:Description": MIDJOURNEY_DESCRIPTION})
    state.analysis_mode = "normal"
    summary = build_summary_result(state)
    assert summary.overall_pattern == "provenance_supported_synthetic_context"
    assert len(logic.synthesize_overall(summary.sections)) == 5
    assert "Supporting Signals:" in summary.full_text
    assert "Supporting Signals" in summary.full_html
    assert "metadata authenticity remains unverified" in summary.full_text
    assert "metadata authenticity remains unverified" in summary.full_html
    assert summary.reasoning_trace["analysis_mode"] == "normal"


def test_legacy_trace_without_new_evidence_fields_still_renders():
    legacy = {
        "section_snapshot": {}, "scorecard": {}, "derived_signals": {},
        "decision": {"dominant_pattern": "inconclusive", "confidence_tier": "Low", "polarity": "neutral",
                     "supporting_signals": ["legacy_pattern"], "contradicting_signals": []},
        "hypothesis_assessments": [{"hypothesis_id": "synthetic_origin", "supporting_evidence": ["metadata:legacy_pattern"]}],
    }
    assert "legacy_pattern" in build_reasoning_trace_text(legacy)


def test_general_anomaly_rationale_does_not_assert_module_independence():
    env = logic.build_decision_env({"cross_signal": section("cross", "strong_hotspot_convergence")})
    env.card.suspicious_score = 9.0
    result = assess(env)
    assert result[4]["decision"]["primary_hypothesis"] == "unresolved_anomaly"
    assert "checks that may be correlated" in result[1]
    assert "independent forensic domains" not in result[1]
    assert "strong camera-acquisition signals counterbalance" not in result[1]


def test_creator_context_does_not_inherit_a_simultaneous_generation_label():
    payload = payload_from_record({"PNG:Author": "Example creator", "PNG:Description": MIDJOURNEY_DESCRIPTION})
    trace = logic.synthesize_overall({"metadata": build_metadata_section(payload)})[4]
    h = hypotheses(trace)["synthetic_origin"]
    assert h["evidence_details"]["metadata:CREATOR_IDENTITY_PRESENT"]["pattern"] == "creator_identity_present"
    assert trace["decision"]["contextual_signals"] == ["creator_identity_present"]
    assert trace["decision"]["supporting_signals"] == ["embedded_generation_prompt_detected"]
