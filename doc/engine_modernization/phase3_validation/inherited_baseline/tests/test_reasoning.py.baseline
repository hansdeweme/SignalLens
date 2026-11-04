"""Reasoning regressions using synthetic summaries and mocked metadata only."""

import json
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pytest

import decision_logic as logic
from exiftool_backend import (
    build_signals, derive_classification, extract_watchlist_hits, find_term_matches,
)
from gui_semantics import ModuleSummary
from hypothesis_engine import compute_base_scores, derive_signals, build_evidence_snapshot
from metadata_evidence import ProvenanceState
from reasoning_persistence import build_reasoning_trace_text
from summary_sections import build_metadata_section


def section(name, pattern, *, status="strong", polarity="suspicious", score=0.7, details=None):
    return ModuleSummary(name, status=status, polarity=polarity, domain=name,
                         pattern=pattern, score=score, details=details or {})


def metadata(*ids):
    return build_metadata_section({"signals": [
        {"id": sid, "evidence": [{"tag": "Description", "value": "AI-generated using Midjourney"}]}
        for sid in ids
    ]})


def payload_from_record(record):
    hits = extract_watchlist_hits(record)
    matches = find_term_matches(hits)
    signals = build_signals(Path("synthetic-fixture.png"), record, hits, matches)
    return {"classification": derive_classification(signals), "signals": [asdict(s) for s in signals]}


def reference_env(case):
    """Partial trace reconstruction; supplied legacy card values are injected.

    This is a decision-layer fixture, not a detector/pipeline image replay.
    """
    instagram = case == "instagram"
    sections = {
        "metadata": metadata("METADATA_STRIPPED_OR_SPARSE" if instagram else "DECLARED_SYNTHETIC"),
        "boundary": section("boundary", "possible_foreground_background_processing_mismatch",
                            status="strong" if instagram else "weak"),
        "cross_signal": section("cross_signal", "strong_hotspot_convergence"),
        "region_masks": section("region_masks", "region_mask_available", polarity="neutral", details={
            "source": "person_subject_mask", "person_mask_reliability": "high",
            "boundary_ratio": 0.04 if instagram else 0.025,
        }),
    }
    if instagram:
        sections["boundary_focus"] = section("boundary_focus", "boundary_focus_processing_mismatch")
        sections["subject_boundary"] = section("subject_boundary", "possible_subject_background_segmentation_artifact")
    else:
        sections["sensor_origin"] = section("sensor_origin", "camera_like_acquisition_supported", polarity="benign")
    env = logic.build_decision_env(sections)
    env.card.suspicious_score = 25.4776 if instagram else 22.193
    env.card.local_edit_support_score = 6.70 if instagram else 4.50
    env.card.camera_counter_support = 0.0 if instagram else 1.25
    env.card.provenance_boost = 0.0 if instagram else 0.75
    env.card.clone_support_score = 0.0
    env.card.synthetic_boost = 0.0
    env.card.contextual_false_positive_risk = False
    return env


def assess(env, routes=None):
    result = logic.evaluate_hypotheses(env, routes)
    return logic.finish_decision(env, result)


def hypotheses(trace):
    return {item["hypothesis_id"]: item for item in trace["hypothesis_assessments"]}


def test_midjourney_trace_regression():
    env = reference_env("midjourney")
    original = logic.route_strong_local_edit(env)
    assert (original.pattern, original.confidence, original.polarity) == (
        "localized_processing_inconclusive", "Low", "neutral",
    )
    pattern, text, confidence, polarity, trace = assess(env)
    assert (pattern, confidence, polarity) == ("provenance_supported_synthetic_context", "Medium", "suspicious")
    assert trace["scorecard"]["provenance_boost"] == 0.75
    assert trace["derived_signals"]["boundary_reliability_score"] == 0.75
    hs = hypotheses(trace)
    assert hs["localized_editing"]["confidence_tier"] == "Low"
    assert hs["localized_editing"]["polarity"] == "neutral"
    assert hs["synthetic_origin"]["confidence_tier"] == "Medium"
    assert "metadata:DECLARED_SYNTHETIC" in hs["synthetic_origin"]["supporting_evidence"]
    assert "metadata authenticity is unverified" in text.lower()
    assert trace["provenance_evidence"]["metadata_authenticity_verified"] is False
    assert trace["decision"]["primary_hypothesis"] == "synthetic_origin"


def test_instagram_trace_regression():
    env = reference_env("instagram")
    original = logic.route_strong_local_edit(env)
    assert (original.pattern, original.confidence) == ("possible_foreground_background_processing_mismatch", "High")
    pattern, text, confidence, polarity, trace = assess(env)
    assert (pattern, confidence, polarity) == (original.pattern, "High", "suspicious")
    hs = hypotheses(trace)
    assert hs["localized_editing"]["confidence_tier"] == "High"
    assert hs["synthetic_origin"]["polarity"] == "neutral"
    assert hs["synthetic_origin"]["confidence_tier"] == "Inconclusive"
    assert hs["synthetic_origin"]["supporting_evidence"] == []
    assert trace["derived_signals"]["metadata_missing"] is True
    assert "metadata" not in compute_base_scores(env.sections)[2]
    assert trace["decision"]["primary_hypothesis"] == "localized_editing"
    assert "does not by itself establish AI generation" in text


def test_metadata_only_generation_declaration():
    result = logic.synthesize_overall({"metadata": metadata("DECLARED_SYNTHETIC")})
    assert result[0] == "provenance_supported_synthetic_context"
    assert result[2:4] == ("Medium", "suspicious")
    assert result[4]["scorecard"]["provenance_boost"] == 0.75
    assert "unverified" in result[1]
    assert hypotheses(result[4])["localized_editing"]["confidence_tier"] == "Inconclusive"


@pytest.mark.parametrize("record", [
    {"PNG:Parameters": "a red boat\nSteps: 20, Sampler: Euler, CFG scale: 7, Seed: 42"},
    {"PNG:Prompt": {"1": {"class_type": "KSampler", "inputs": {"seed": 42}}}},
    {"PNG:Workflow": '{"nodes": [{"class_type": "KSamplerAdvanced"}]}'},
    {"PNG:Workflow": {"nodes": [{"type": "KSampler"}]}},
])
def test_embedded_prompt_propagates(record):
    payload = payload_from_record(record)
    assert "EMBEDDED_GENERATION_PROMPT" in {s["id"] for s in payload["signals"]}
    summary = build_metadata_section(payload)
    assert summary.pattern == "embedded_generation_prompt_detected"
    assert summary.status == "medium"
    trace = logic.synthesize_overall({"metadata": summary})[4]
    assert trace["derived_signals"]["metadata_synthetic"] is True
    assert trace["derived_signals"]["provenance_state"] == "unverified_generation_declaration"
    assert "metadata:EMBEDDED_GENERATION_PROMPT" in hypotheses(trace)["synthetic_origin"]["supporting_evidence"]
    assert trace["evidence_snapshot"]["metadata"]["details"]["metadata_signals"] == payload["signals"]


@pytest.mark.parametrize("record", [
    {"XMP:Workflow": "crop, white balance, export for print"},
    {"PNG:Parameters": "width=1024 height=768 quality=90"},
    {"PNG:Prompt": "Please approve the annual report image"},
    {"XMP:Workflow": ""},
    {"XMP:Software": "Midjourney"},
    {"XMP:Software": "Adobe Photoshop"},
])
def test_generic_workflow_or_tool_is_not_generation(record):
    payload = payload_from_record(record)
    assert not payload["classification"]["declared_generation"]
    assert "EMBEDDED_GENERATION_PROMPT" not in {s["id"] for s in payload["signals"]}
    summary = build_metadata_section(payload)
    assert summary.polarity == "neutral"
    trace = logic.synthesize_overall({"metadata": summary})[4]
    assert not trace["derived_signals"]["metadata_synthetic"]
    assert hypotheses(trace)["synthetic_origin"]["confidence_tier"] == "Inconclusive"


def test_stripped_metadata_is_neutral_and_scores_zero():
    summary = metadata("METADATA_STRIPPED_OR_SPARSE")
    assert (summary.pattern, summary.polarity, summary.score) == ("sparse_or_stripped", "neutral", 0.0)
    assert compute_base_scores({"metadata": summary}) == (0.0, 0.0, set(), set())
    # Defensive compatibility: even a stale suspicious sparse summary adds no score/domain.
    summary.polarity = "suspicious"
    assert compute_base_scores({"metadata": summary}) == (0.0, 0.0, set(), set())
    ds = derive_signals(build_evidence_snapshot({"metadata": summary}))
    assert ds.metadata_missing and not ds.metadata_synthetic
    sections = {
        "metadata": metadata("METADATA_STRIPPED_OR_SPARSE"),
        "sensor_origin": section("sensor", "camera_like_acquisition_supported", polarity="benign"),
    }
    result = logic.synthesize_overall(sections)
    assert result[3] == "benign"
    assert result[4]["scorecard"]["suspicious_score"] == 0
    assert "Missing provenance coverage" in result[1]


def test_camera_support_and_synthetic_declaration_coexist():
    sections = {
        "metadata": metadata("DECLARED_SYNTHETIC", "CAMERA_METADATA_RICH"),
        "sensor_origin": section("sensor", "camera_like_acquisition_supported", polarity="benign"),
        "cfa_demosaic": section("cfa", "camera_like_cfa_supported", polarity="benign"),
    }
    result = logic.synthesize_overall(sections)
    hs = hypotheses(result[4])
    assert hs["synthetic_origin"]["polarity"] == "suspicious"
    assert hs["camera_acquisition"]["polarity"] == "benign"
    assert len(hs["camera_acquisition"]["supporting_evidence"]) == 3
    assert len(hs["synthetic_origin"]["moderating_evidence"]) == 3
    assert result[0] == "provenance_supported_synthetic_context"
    assert result[2] == "Medium"


@pytest.mark.parametrize("sections, expected", [
    ({}, "neutral"),
    ({"metadata": metadata("METADATA_STRIPPED_OR_SPARSE")}, "neutral"),
    ({"sensor_origin": section("sensor", "camera_like_acquisition_supported", polarity="benign")}, "benign"),
])
def test_benign_and_inconclusive_still_available(sections, expected):
    assert logic.synthesize_overall(sections)[3] == expected


@pytest.mark.parametrize("case", ["midjourney", "instagram"])
def test_irrelevant_route_order_does_not_change_assessments(case):
    forward = assess(reference_env(case))
    reverse = assess(reference_env(case), tuple(reversed(logic.DECISION_ROUTES)))
    assert forward[:4] == reverse[:4]
    assert forward[4]["hypothesis_assessments"] == reverse[4]["hypothesis_assessments"]
    assert forward[4]["decision"] == reverse[4]["decision"]


def test_json_compatibility_and_text_adapter():
    result = assess(reference_env("midjourney"))
    assert len(result) == 5
    trace = json.loads(json.dumps(result[4], allow_nan=False))
    assert {
        "analysis_mode", "section_snapshot", "context", "contextual_priors", "evidence_snapshot",
        "derived_signals", "scorecard", "decision_route_trace", "decision",
    } <= trace.keys()
    assert {
        "decision_branch", "dominant_pattern", "confidence_tier", "polarity", "supporting_signals",
        "contradicting_signals", "confidence_rationale", "overall_text",
    } <= trace["decision"].keys()
    assert isinstance(trace["scorecard"]["suspicious_domains"], list)
    assert len(trace["decision_route_trace"]) == len(logic.DECISION_ROUTES)
    assert sum(item["selected"] for item in trace["decision_route_trace"]) == 1
    text = build_reasoning_trace_text(trace)
    assert "synthetic_origin" in text and "localized_editing" in text and "camera_acquisition" in text
    assert trace["decision"]["selection_reason"] in text
    # Old traces still render using the existing adapter path.
    legacy = {key: trace[key] for key in ("section_snapshot", "scorecard", "derived_signals", "decision")}
    legacy["decision"] = dict(legacy["decision"])
    legacy["decision"].pop("selection_reason")
    assert "Reasoning Trace" in build_reasoning_trace_text(legacy)


def test_unverified_c2pa_is_neutral_and_never_camera_support():
    payload = payload_from_record({"JUMBF:C2PA": "manifest present"})
    payload["classification"]["provenance_verified"] = True  # No validator: ignore this claim.
    payload["classification"]["provenance_state"] = "verified_generation_assertion"
    summary = build_metadata_section(payload)
    result = logic.synthesize_overall({"metadata": summary})
    trace = result[4]
    assert summary.polarity == "neutral"
    assert not trace["derived_signals"]["metadata_camera_like"]
    assert trace["provenance_evidence"] == {
        "state": "provenance_present_unverified", "metadata_authenticity_verified": False,
    }
    assert result[3] == "neutral"


def test_enhancement_is_distinct_from_generation():
    result = logic.synthesize_overall({"metadata": metadata("DECLARED_ENHANCEMENT")})
    trace = result[4]
    assert trace["derived_signals"]["metadata_enhancement"] is True
    assert trace["derived_signals"]["metadata_synthetic"] is False
    assert trace["provenance_evidence"]["state"] == ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION.value
    assert result[0] == "provenance_supported_enhancement_context"
    assert "not whole-image synthetic generation" in result[1]


@pytest.mark.parametrize("signal_id", ["AI_TOOL_NAME_MATCH", "AMBIGUOUS_WORKFLOW_METADATA", "C2PA_PRESENT", "DECLARED_SYNTHETIC"])
def test_strong_local_edit_is_not_overwritten_by_metadata(signal_id):
    env = reference_env("instagram")
    env.sections["metadata"] = metadata(signal_id)
    env.ev = build_evidence_snapshot(env.sections)
    env.ds = derive_signals(env.ev)
    result = assess(env)
    assert result[0] == "possible_foreground_background_processing_mismatch"
    assert result[2] == "High"
    assert result[4]["decision"]["primary_hypothesis"] == "localized_editing"


@pytest.mark.parametrize("unreliable_geometry", [False, True])
def test_boundary_safeguards_do_not_block_generation(unreliable_geometry):
    env = reference_env("instagram")
    env.sections["metadata"] = metadata("DECLARED_SYNTHETIC")
    env.ev = build_evidence_snapshot(env.sections)
    env.ds = derive_signals(env.ev)
    env.ds.boundary_reliability_score = 0.25
    env.ds.region_geometry_unreliable = unreliable_geometry
    result = assess(env)
    hs = hypotheses(result[4])
    assert hs["localized_editing"]["polarity"] == "neutral"
    assert hs["localized_editing"]["decision_branch"] == "boundary_support_limited_localized_processing"
    assert result[0] == "provenance_supported_synthetic_context"


def test_localized_visual_signals_do_not_become_generation_from_metadata():
    env = reference_env("instagram")
    env.sections["metadata"] = metadata("DECLARED_SYNTHETIC")
    env.ev = build_evidence_snapshot(env.sections)
    env.ds = derive_signals(env.ev)
    env.card.synthetic_boost = 1.50
    env.card.synthetic_supported_by_other_domains = True
    result = assess(env)
    hs = hypotheses(result[4])
    assert hs["synthetic_origin"]["confidence_tier"] == "Medium"
    assert hs["localized_editing"]["confidence_tier"] == "High"


def test_summary_and_render_integration_preserves_interface():
    from summary_synthesizer import build_summary_result

    keys = (
        "ela", "noise", "sensor_origin", "region_masks", "segmentation_alignment", "region_fft",
        "cross_signal", "boundary_focus", "fft", "subject_boundary", "subject_texture_consistency",
        "subject_process_asymmetry", "subject_material_realism", "patch_similarity", "patch_spatial",
        "compression_history", "cfa_demosaic",
    )
    state = SimpleNamespace(**{f"{key}_payload": None for key in keys})
    state.exif_payload = {"signals": [{"id": "DECLARED_SYNTHETIC"}]}
    state.analysis_mode = "full"
    result = build_summary_result(state)
    assert result.overall_pattern == "provenance_supported_synthetic_context"
    assert result.reasoning_trace["analysis_mode"] == "full"
    assert "synthetic_origin" in result.full_text
    assert "synthetic_origin" in result.full_html


def test_sparse_metadata_never_becomes_support_alongside_declaration():
    result = logic.synthesize_overall({"metadata": metadata(
        "DECLARED_SYNTHETIC", "METADATA_STRIPPED_OR_SPARSE", "CREATOR_IDENTITY_PRESENT",
    )})
    assert hypotheses(result[4])["synthetic_origin"]["supporting_evidence"] == ["metadata:DECLARED_SYNTHETIC"]


def test_metadata_absence_does_not_change_scores_or_domains():
    sections = {"sensor_origin": section("sensor", "camera_like_acquisition_supported", polarity="benign")}
    without_metadata = logic.build_decision_env(sections).card
    with_metadata = logic.build_decision_env({**sections, "metadata": metadata("METADATA_STRIPPED_OR_SPARSE")}).card
    assert asdict(with_metadata) == asdict(without_metadata)


def test_correlated_local_evidence_does_not_auto_create_synthetic_hypothesis():
    env = reference_env("instagram")
    env.card.synthetic_boost = 2.0
    env.card.synthetic_supported_by_other_domains = True
    result = assess(env)
    assert hypotheses(result[4])["synthetic_origin"]["confidence_tier"] == "Inconclusive"


def visual_generation_env():
    env = reference_env("midjourney")
    env.sections.pop("metadata")
    env.sections["subject_material_realism"] = section("material", "subject_material_realism_failure", score=0.65)
    env.sections["subject_process_asymmetry"] = section("asymmetry", "subject_process_asymmetry_strong")
    env.ev = build_evidence_snapshot(env.sections)
    env.ds = derive_signals(env.ev)
    env.card.synthetic_boost = 1.5
    env.card.synthetic_supported_by_other_domains = True
    return env


def test_supported_visual_generation_survives_local_uncertainty():
    result = assess(visual_generation_env())
    assert result[0] == "synthetic_multi_signal_convergence"
    hs = hypotheses(result[4])
    assert hs["localized_editing"]["confidence_tier"] == "Low"
    assert hs["synthetic_origin"]["confidence_tier"] == "High"
    assert hs["camera_acquisition"]["supporting_evidence"]


def test_region_unreliability_limits_region_dependent_generation():
    env = visual_generation_env()
    env.ds.region_geometry_unreliable = True
    result = assess(env)
    assert hypotheses(result[4])["synthetic_origin"]["confidence_tier"] == "Inconclusive"
    assert "Unreliable subject-region geometry" in result[1]


def test_clone_reuse_is_independent_of_boundary_safeguards():
    env = reference_env("instagram")
    env.card.clone_support_score = 10.0
    env.ds.boundary_reliability_score = 0.25
    result = assess(env)
    assert result[0] == "possible_clone_reuse"
    assert result[2:4] == ("High", "suspicious")
    assert hypotheses(result[4])["synthetic_origin"]["polarity"] == "neutral"


def test_legacy_embedded_pattern_without_signal_ids():
    summary = build_metadata_section({"classification": {"metadata_status": "embedded_generation_prompt_detected"}})
    result = logic.synthesize_overall({"metadata": summary})
    assert summary.status == "medium" and summary.polarity == "suspicious"
    assert result[4]["derived_signals"]["metadata_synthetic"] is True
    assert result[0] == "provenance_supported_synthetic_context"


MIDJOURNEY_DESCRIPTION = (
    'Portrait of a woman, golden-hour light, shot with a 35mm lens at f/1.4" '
    '--chaos 10 --ar 4:3 --style raw --stylize 1000 --v 6.1 '
    'Job ID: 93a47bc9-aebe-4a35-9249-f9bd564e3d88'
)
IPTC_SOURCE_TYPE = "http://cv.iptc.org/newscodes/digitalsourcetype/"


def test_midjourney_raw_metadata_path_regression():
    # Same embedded field structure as the saved analysis; no source image access.
    payload = payload_from_record({
        "SourceFile": "C:/fixtures/midjourney/portrait.png",
        "PNG:Description": MIDJOURNEY_DESCRIPTION,
        "XMP-iptcExt:DigitalSourceType": IPTC_SOURCE_TYPE + "trainedAlgorithmicMedia",
    })
    ids = {s["id"] for s in payload["signals"]}
    assert {"DECLARED_SYNTHETIC", "EMBEDDED_GENERATION_PROMPT"} <= ids
    assert "AI_TOOL_NAME_MATCH" not in ids  # Folder names are not embedded evidence.
    env = reference_env("midjourney")
    env.sections["metadata"] = build_metadata_section(payload)
    env.ev = build_evidence_snapshot(env.sections)
    env.ds = derive_signals(env.ev)
    result = assess(env)
    assert result[0] == "provenance_supported_synthetic_context"
    assert result[2:4] == ("Medium", "suspicious")
    hs = hypotheses(result[4])
    assert hs["localized_editing"]["confidence_tier"] == "Low"
    assert hs["synthetic_origin"]["confidence_tier"] == "Medium"


@pytest.mark.parametrize("scheme", ["http", "https"])
@pytest.mark.parametrize("term, signal_id, pattern", [
    ("trainedAlgorithmicMedia", "DECLARED_SYNTHETIC", "provenance_supported_synthetic_context"),
    ("compositeWithTrainedAlgorithmicMedia", "DECLARED_ENHANCEMENT", "provenance_supported_enhancement_context"),
    ("compositeSynthetic", "DECLARED_ENHANCEMENT", "provenance_supported_enhancement_context"),
])
def test_iptc_source_type_alone_is_scoped_unverified_declaration(scheme, term, signal_id, pattern):
    payload = payload_from_record({
        "XMP-iptcExt:DigitalSourceType": f"{scheme}://cv.iptc.org/newscodes/digitalsourcetype/{term}",
    })
    assert signal_id in {s["id"] for s in payload["signals"]}
    result = logic.synthesize_overall({"metadata": build_metadata_section(payload)})
    assert result[0] == pattern
    assert result[2:4] == ("Medium", "suspicious")
    assert result[4]["provenance_evidence"]["metadata_authenticity_verified"] is False


@pytest.mark.parametrize("value", [
    IPTC_SOURCE_TYPE + "digitalCapture",
    IPTC_SOURCE_TYPE + "humanEdits",
    IPTC_SOURCE_TYPE + "algorithmicallyEnhanced",
    IPTC_SOURCE_TYPE + "algorithmicMedia",
    "https://example.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    IPTC_SOURCE_TYPE + "trainedAlgorithmicMedia?unrelated=true",
    "some notes about trainedAlgorithmicMedia",
])
def test_other_source_type_values_do_not_declare_ai_generation(value):
    payload = payload_from_record({"XMP-iptcExt:DigitalSourceType": value})
    assert not payload["classification"]["declared_generation"]
    assert not payload["classification"]["declared_enhancement"]


@pytest.mark.parametrize("description, expected", [
    (MIDJOURNEY_DESCRIPTION, True),
    ('A regular photograph --ar 4:3', False),
    ('Job ID: 93a47bc9-aebe-4a35-9249-f9bd564e3d88', False),
    ('Portrait --stylize 1000 --v 6.1', False),
    ('Portrait --stylize 1000 --v 6.1 Job ID: invalid', False),
])
def test_midjourney_prompt_signature_is_not_just_an_arbitrary_description(description, expected):
    payload = payload_from_record({"PNG:Description": description})
    assert ("EMBEDDED_GENERATION_PROMPT" in {s["id"] for s in payload["signals"]}) == expected


@pytest.mark.parametrize("key, value", [
    ("SourceFile", "C:/fixtures/midjourney/ai generated.png"),
    ("System:Directory", "C:/fixtures/created with ai"),
    ("System:FileName", "synthetic.png"),
    ("ExifTool:Warning", "AI generated text in diagnostic output"),
])
def test_host_paths_and_extractor_diagnostics_are_not_embedded_evidence(key, value):
    payload = payload_from_record({key: value})
    assert not payload["classification"]["declared_generation"]
    assert "AI_TOOL_NAME_MATCH" not in {s["id"] for s in payload["signals"]}
    assert not payload["classification"]["declared_enhancement"]
