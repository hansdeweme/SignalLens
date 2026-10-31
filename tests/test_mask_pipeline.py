"""Mask contracts and pipeline failure paths using synthetic images/masks only."""

import json
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

import signallens_controller as pipeline
import vf_person_subject_mask as person_module
from mask_contract import (
    InvalidMaskPayload, StageUnavailable, normalize_region_masks,
    person_mask_diagnostics, require_person_geometry, validate_region_masks,
)
from summary_sections import build_region_mask_section
from summary_synthesizer import build_summary_result
from reasoning_persistence import build_reasoning_trace_text
from vf_region_masks import run_region_mask_analysis
from vf_segmentation_alignment import compute_segmentation_boundary_alignment
from test_reasoning import payload_from_record, IPTC_SOURCE_TYPE
from gui_semantics import ModuleSummary
from hypothesis_engine import build_evidence_snapshot, derive_signals


REGIONAL_STAGES = {
    "Region segmentation analysis", "Boundary-focused analysis", "Region-aware FFT analysis",
    "Segmentation alignment analysis", "Subject texture consistency analysis",
    "Subject process asymmetry analysis", "Subject material realism analysis", "Patch spatial analysis",
}


def synthetic_person(tmp_path, reliability="high", backend="mediapipe_tasks_image_segmenter"):
    mask = np.zeros((64, 64), dtype=np.uint8)
    if reliability == "high":
        mask[16:48, 16:48] = 1
    elif reliability == "medium":
        mask[2:62, 2:62] = 1
    else:
        mask[:60, :] = 1
    path = tmp_path / "synthetic_person.png"
    cv2.imwrite(str(path), mask * 255)
    quality = person_module._quality_from_mask(mask, True, 0.9)
    assert quality["mask_reliability"] == reliability
    return {"person_subject_mask": {
        "backend": backend, "quality": quality, "mask_path": str(path),
        "image_geometry": {"width": 64, "height": 64},
    }}, mask


def fake_pipeline(monkeypatch, tmp_path, reliability="high", backend="mediapipe_tasks_image_segmenter", error=None):
    image = tmp_path / "synthetic_input.png"
    Image.fromarray(np.tile(np.arange(64, dtype=np.uint8), (64, 1))).convert("RGB").save(image)
    prepared = {"path": str(image), "height": 64, "width": 64, "scale": 1.0}
    monkeypatch.setattr(pipeline, "prepare_analysis_images", lambda **kw: {
        "original": prepared, "prepared": {key: dict(prepared) for key in ("subject", "patch", "global")},
    })
    monkeypatch.setattr(pipeline, "analyze_file_with_exiftool", lambda **kw: payload_from_record({
        "XMP-iptcExt:DigitalSourceType": IPTC_SOURCE_TYPE + "trainedAlgorithmicMedia",
    }))
    blocks = [{"row": r, "col": c} for r in (1, 2) for c in (1, 2, 3)]
    for fn, key, pattern in (("run_ela", "ela", "ela_inconclusive"), ("run_noise_analysis", "noise", "noise_inconclusive")):
        monkeypatch.setattr(pipeline, fn, lambda key=key, pattern=pattern, **kw: {
            key: {"image_geometry": {"height": 64, "width": 64},
                  "blockwise": {"block_size": 8, "top_blocks": blocks},
                  "pattern": {f"{key}_pattern": pattern}},
        })
    for name in (
        "run_sensor_origin_analysis", "run_cfa_demosaic_analysis", "run_subject_boundary_analysis",
        "run_fft_analysis", "run_patch_similarity_analysis", "run_compression_history_analysis",
        "run_region_segmentation_analysis", "run_boundary_focus_analysis", "run_region_fft_analysis",
        "run_subject_texture_consistency_analysis", "run_subject_process_asymmetry_analysis",
        "run_subject_material_realism_analysis", "run_patch_spatial_analysis",
    ):
        monkeypatch.setattr(pipeline, name, lambda *args, **kwargs: {})
    monkeypatch.setattr(pipeline, "create_shared_boundary_overlays", lambda **kw: {})
    if reliability is None:
        payload = None
    else:
        payload, _ = synthetic_person(tmp_path, reliability, backend)
    def run_person(**kw):
        if error:
            raise error
        return payload
    monkeypatch.setattr(pipeline, "run_person_subject_mask_analysis", run_person)
    return image, payload


def run_fake(monkeypatch, tmp_path, reliability="high", backend="mediapipe_tasks_image_segmenter", error=None, legacy=False):
    image, payload = fake_pipeline(monkeypatch, tmp_path, reliability, backend, error)
    controller = pipeline.SignalLensController(use_legacy_region_masks=legacy)
    state = controller.run_analysis(image, tmp_path / "analysis", analysis_mode="normal")
    return state, controller, payload


@pytest.mark.parametrize("reliability, status", [("high", "reliable"), ("medium", "limited")])
def test_high_and_medium_person_masks_retain_regional_execution(monkeypatch, tmp_path, reliability, status):
    state, _, _ = run_fake(monkeypatch, tmp_path, reliability)
    assert not state.errors
    assert state.mask_diagnostics["mask_status"] == status
    assert state.analysis_coverage["status"] == "complete"
    assert all(state.stage_statuses[name]["status"] == "success" for name in REGIONAL_STAGES)
    masks = validate_region_masks(state.region_masks_payload)
    assert masks["person_specific"] and masks["source"] == "person_subject_mask"


def test_low_mask_is_controlled_unavailable_and_independent_stages_continue(monkeypatch, tmp_path):
    state, _, _ = run_fake(monkeypatch, tmp_path, "low")
    assert state.errors == []
    assert state.region_masks_payload is None
    assert state.mask_diagnostics["mask_status"] == "unreliable"
    assert "[0.03, 0.90]" in " ".join(state.mask_diagnostics["rejection_reasons"])
    assert state.stage_statuses["Person-derived region masks"]["status"] == "unavailable"
    assert set(state.mask_diagnostics["disabled_stages"]) == REGIONAL_STAGES
    assert all(state.stage_statuses[name]["status"] == "skipped" for name in REGIONAL_STAGES)
    assert state.cross_signal_payload is not None
    for name in ("EXIF analysis", "ELA analysis", "Noise analysis", "FFT analysis", "Patch similarity analysis", "Compression-history analysis", "Shared boundary overlays"):
        assert state.stage_statuses[name]["status"] == "success"
    assert state.run_recorder.status == "completed_partial"


def test_missing_person_payload_is_not_an_execution_error(monkeypatch, tmp_path):
    state, _, _ = run_fake(monkeypatch, tmp_path, reliability=None)
    assert not state.errors
    assert state.mask_diagnostics["mask_status"] == "unavailable"
    assert state.cross_signal_payload is not None
    assert state.stage_statuses["Person-aware subject mask"]["status"] == "skipped"


def test_unexpected_segmentation_exception_is_recorded_without_pipeline_cascade(monkeypatch, tmp_path):
    state, _, _ = run_fake(monkeypatch, tmp_path, error=RuntimeError("backend unavailable"))
    assert len(state.errors) == 1 and "backend unavailable" in state.errors[0]
    assert state.mask_diagnostics["mask_status"] == "error"
    assert not state.person_mask_reliable
    assert state.stage_statuses["Person-aware subject mask"]["status"] == "failed"
    assert state.cross_signal_payload is not None
    assert state.run_recorder.status == "completed_with_errors"


@pytest.mark.parametrize("missing", ["run_ela", "run_noise_analysis"])
def test_cross_signal_declares_ela_and_residual_dependencies(monkeypatch, tmp_path, missing):
    image, _ = fake_pipeline(monkeypatch, tmp_path, "low")
    monkeypatch.setattr(pipeline, missing, lambda **kw: None)
    state = pipeline.SignalLensController().run_analysis(image, tmp_path / "analysis")
    assert state.stage_statuses["Cross-signal analysis"]["status"] == "skipped"
    assert state.cross_signal_payload is None
    assert not state.errors


def test_cross_signal_uses_signal_geometry_without_any_region_masks(monkeypatch, tmp_path):
    state, _, _ = run_fake(monkeypatch, tmp_path, "low")
    assert state.region_masks_payload is None
    assert state.cross_signal_payload["hotspot_mask"].shape == (64, 64)
    assert state.cross_signal_payload["cross_signal"]["cross_signal_pattern"] == "strong_hotspot_convergence"
    assert np.count_nonzero(state.cross_signal_payload["hotspot_mask"]) > 0


def test_available_legacy_fallback_is_canonical_and_never_person_evidence(monkeypatch, tmp_path):
    image, _ = fake_pipeline(monkeypatch, tmp_path, "low")
    person, _ = synthetic_person(tmp_path, "high")
    raw = person_module.derive_region_masks_from_person_mask(
        person["person_subject_mask"]["mask_path"], image, tmp_path / "fallback", "high",
    )
    approximate = normalize_region_masks(raw, mask_source="legacy_edge_saliency", mask_reliability="low",
                                        mask_status="approximate", person_specific=False, fallback_used=True)
    monkeypatch.setattr(pipeline, "run_region_mask_analysis", lambda **kw: approximate)
    state = pipeline.SignalLensController(use_legacy_region_masks=True).run_analysis(image, tmp_path / "analysis")
    masks = validate_region_masks(state.region_masks_payload)
    assert masks["fallback_used"] and not masks["person_specific"]
    assert masks["mask_source"] == "legacy_edge_saliency"
    assert "usable range" in masks["fallback_reason"]
    assert state.mask_diagnostics["segmentation_outcome"]["mask_status"] == "unreliable"
    assert all(state.stage_statuses[name]["status"] == "skipped" for name in REGIONAL_STAGES)
    summary = build_region_mask_section(state.region_masks_payload)
    assert (summary.status, summary.polarity, summary.pattern) == ("not_run", "neutral", None)
    assert not state.errors


def test_unavailable_legacy_fallback_remains_controlled(monkeypatch, tmp_path):
    image, _ = fake_pipeline(monkeypatch, tmp_path, "low")
    monkeypatch.setattr(pipeline, "run_region_mask_analysis", lambda **kw: None)
    state = pipeline.SignalLensController(use_legacy_region_masks=True).run_analysis(image, tmp_path / "analysis")
    assert state.region_masks_payload is None
    assert state.mask_diagnostics["fallback_selection"] == "Legacy fallback unavailable."
    assert state.cross_signal_payload is not None and not state.errors


def test_hog_box_is_approximate_even_if_geometric_quality_is_high(monkeypatch, tmp_path):
    state, _, _ = run_fake(monkeypatch, tmp_path, "high", "opencv_hog")
    assert state.mask_diagnostics["mask_status"] == "approximate"
    assert not state.person_mask_reliable
    assert not state.region_masks_payload["region_masks"]["person_specific"]
    assert all(state.stage_statuses[name]["status"] == "skipped" for name in REGIONAL_STAGES)


def test_invalid_region_payload_is_validated_once_then_independent_analysis_continues(monkeypatch, tmp_path):
    image, _ = fake_pipeline(monkeypatch, tmp_path, "high")
    monkeypatch.setattr(pipeline, "derive_region_masks_from_person_mask", lambda **kw: {"region_masks": {"shape": [64, 64]}})
    state = pipeline.SignalLensController().run_analysis(image, tmp_path / "analysis")
    assert state.region_masks_payload is None
    assert len(state.errors) == 1
    assert state.mask_diagnostics["mask_status"] == "error"
    assert state.cross_signal_payload is not None


def test_alignment_without_person_boundary_is_explicitly_skipped(monkeypatch, tmp_path):
    state, _, _ = run_fake(monkeypatch, tmp_path, "low")
    assert state.segmentation_alignment_payload is None
    assert state.stage_statuses["Segmentation alignment analysis"]["status"] == "skipped"


def test_partial_coverage_is_persisted_and_missing_regions_are_neutral(monkeypatch, tmp_path):
    state, _, _ = run_fake(monkeypatch, tmp_path, "low")
    result = build_summary_result(state)
    trace = json.loads(json.dumps(result.reasoning_trace, allow_nan=False))
    assert trace["pipeline_status"]["coverage"]["status"] == "partial"
    assert trace["pipeline_status"]["mask_diagnostics"]["mask_status"] == "unreliable"
    assert trace["decision"]["primary_hypothesis"] == "synthetic_origin"
    assert result.overall_polarity == "suspicious"
    for key in ("region_masks", "boundary_focus", "region_fft", "subject_texture_consistency", "subject_material_realism"):
        s = result.sections[key]
        assert (s.status, s.polarity, s.score) == ("not_run", "neutral", None)
        assert "Unavailable" in s.note
    assert "coverage is incomplete" in result.full_text
    assert "coverage is incomplete" in result.full_html
    assert trace["decision"]["overall_text"] == result.overall_text
    assert "Pipeline Coverage" in build_reasoning_trace_text(trace)
    assert "hotspot_mask" not in json.dumps(trace)
    manifest = json.loads(state.run_recorder.manifest_path.read_text(encoding="utf-8"))
    assert manifest["diagnostics"]["mask"]["mask_status"] == "unreliable"
    assert len(manifest["stages"]) == len(state.stage_statuses)


def test_reliable_mask_derivation_preserves_pixels(tmp_path):
    payload, subject = synthetic_person(tmp_path)
    result = person_module.derive_region_masks_from_person_mask(
        payload["person_subject_mask"]["mask_path"], tmp_path / "image.png", tmp_path, "high",
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    expected_boundary = ((cv2.dilate(subject, kernel) > 0) & (cv2.erode(subject, kernel) == 0)).astype(np.uint8)
    masks = validate_region_masks(result)
    assert np.array_equal(cv2.imread(masks["subject_mask_path"], 0) > 0, subject > 0)
    assert np.array_equal(cv2.imread(masks["boundary_band_path"], 0) > 0, expected_boundary > 0)
    assert np.array_equal(cv2.imread(masks["background_mask_path"], 0) > 0, subject == 0)


def test_original_midjourney_coverage_is_rejected_by_unchanged_quality_policy():
    mask = np.ones((100, 100), dtype=np.uint8)
    mask[:8, :] = 0
    quality = person_module._quality_from_mask(mask, True, 0.93)
    assert quality["mask_reliability"] == "low"
    assert "[0.03, 0.90]" in quality["quality_reasons"][0]


def test_backend_exception_inside_person_producer_is_retained(monkeypatch, tmp_path):
    image = tmp_path / "synthetic.png"
    Image.new("RGB", (64, 64)).save(image)
    def broken_backend(**kw):
        raise RuntimeError("synthetic backend exception")
    monkeypatch.setattr(person_module, "_detect_person_mask_mediapipe_tasks", broken_backend)
    monkeypatch.setattr(person_module, "_detect_person_bbox_hog", lambda img: (None, 0.0))
    payload = person_module.run_person_subject_mask_analysis(image, tmp_path / "out")
    block = payload["person_subject_mask"]
    assert block["mask_status"] == "error"
    assert not block["person_specific"]
    assert "synthetic backend exception" in block["backend_errors"][0]["error"]


def test_legacy_producer_has_consistent_contract_without_person_authority(tmp_path):
    image = np.zeros((128, 128, 3), dtype=np.uint8)
    image[24:104, 24:104] = 255
    path = tmp_path / "synthetic.png"
    cv2.imwrite(str(path), image)
    payload = run_region_mask_analysis(path, tmp_path / "legacy")
    masks = validate_region_masks(payload)
    assert masks["mask_status"] == "approximate" and not masks["person_specific"]
    assert masks["ratios"]["subject"] == masks["subject_ratio"]
    with pytest.raises(StageUnavailable):
        require_person_geometry(payload)


def test_alignment_scales_original_hotspots_to_prepared_geometry(tmp_path):
    boundary = np.zeros((32, 32), dtype=np.uint8)
    boundary[:8, :8] = 255
    path = tmp_path / "boundary.png"
    cv2.imwrite(str(path), boundary)
    payload = {"region_masks": {"boundary_band_path": str(path)}}
    result = compute_segmentation_boundary_alignment({"hotspot_mask": np.ones((64, 64), dtype=np.uint8)}, payload)
    assert result["raw_overlap"] == pytest.approx(64 / 1024)
    assert result["hotspot_input_shape"] == [64, 64]
    assert result["boundary_shape"] == [32, 32]


@pytest.mark.parametrize("key, value", [("shape", [0, 64]), ("person_specific", "false"), ("mask_status", "unknown"), ("subject_ratio", float("nan"))])
def test_invalid_canonical_fields_are_rejected(tmp_path, key, value):
    person, _ = synthetic_person(tmp_path)
    payload = person_module.derive_region_masks_from_person_mask(person["person_subject_mask"]["mask_path"], tmp_path / "image.png", tmp_path, "high")
    payload["region_masks"][key] = value
    with pytest.raises(InvalidMaskPayload):
        validate_region_masks(payload)


def test_gatekeeper_failure_does_not_cascade_into_fft_or_patch_none_access(monkeypatch, tmp_path):
    image, _ = fake_pipeline(monkeypatch, tmp_path)
    monkeypatch.setattr(pipeline, "prepare_analysis_images", lambda **kw: None)
    state = pipeline.SignalLensController().run_analysis(image, tmp_path / "analysis")
    assert state.stage_statuses["FFT analysis"]["status"] == "skipped"
    assert state.stage_statuses["Patch similarity analysis"]["status"] == "skipped"
    assert state.cross_signal_payload is not None and not state.errors


@pytest.mark.parametrize("reliability", ["high", "low"])
def test_image_edge_detector_needs_valid_person_geometry_for_person_specific_interpretation(monkeypatch, tmp_path, reliability):
    state, _, _ = run_fake(monkeypatch, tmp_path, reliability)
    state.subject_boundary_payload = {"subject_boundary": {
        "pattern": {"subject_boundary_pattern": "possible_subject_background_segmentation_artifact", "subject_boundary_note": "Unvalidated detector reading."},
        "scores": {"boundary_anomaly_score": 0.66},
    }}
    raw = json.dumps(state.subject_boundary_payload)
    summary = build_summary_result(state)
    s = summary.sections["subject_boundary"]
    assert s.score == 0.66
    assert json.dumps(state.subject_boundary_payload) == raw
    if reliability == "low":
        assert (s.status, s.polarity, s.pattern) == ("weak", "neutral", "image_edge_boundary_observation")
        assert s.details["raw_detector_pattern"] == "possible_subject_background_segmentation_artifact"
        local = next(h for h in summary.reasoning_trace["hypothesis_assessments"] if h["hypothesis_id"] == "localized_editing")
        assert "subject_boundary:image_edge_boundary_observation" in local["contextual_evidence"]
        assert summary.reasoning_trace["decision"]["primary_hypothesis"] == "synthetic_origin"
    else:
        assert (s.status, s.polarity, s.pattern) == ("strong", "suspicious", "possible_subject_background_segmentation_artifact")


def test_non_mask_dependency_skip_is_not_mislabeled_as_mask_quality_failure(monkeypatch, tmp_path):
    image, _ = fake_pipeline(monkeypatch, tmp_path, "high")
    monkeypatch.setattr(pipeline, "run_ela", lambda **kw: None)
    state = pipeline.SignalLensController().run_analysis(image, tmp_path / "analysis")
    assert state.stage_statuses["Boundary-focused analysis"]["status"] == "skipped"
    assert state.mask_diagnostics["disabled_stages"] == []


def test_mismatched_signal_geometry_is_unavailable_not_a_crash(monkeypatch, tmp_path):
    image, _ = fake_pipeline(monkeypatch, tmp_path, "low")
    monkeypatch.setattr(pipeline, "run_ela", lambda **kw: {"ela": {
        "image_geometry": {"height": 128, "width": 64},
        "blockwise": {"block_size": 8, "top_blocks": []}, "pattern": {"ela_pattern": "ela_inconclusive"},
    }})
    state = pipeline.SignalLensController().run_analysis(image, tmp_path / "analysis")
    assert state.stage_statuses["Cross-signal analysis"]["status"] == "skipped"
    assert "geometries do not match" in state.stage_statuses["Cross-signal analysis"]["reason"]
    assert not state.errors


def test_center_fallback_without_person_detection_is_only_a_diagnostic(monkeypatch, tmp_path):
    path = tmp_path / "blank.png"
    Image.new("RGB", (64, 64)).save(path)
    monkeypatch.setattr(person_module, "_detect_person_mask_mediapipe_tasks", lambda **kw: (None, 0.0))
    monkeypatch.setattr(person_module, "_detect_person_bbox_hog", lambda img: (None, 0.0))
    payload = person_module.run_person_subject_mask_analysis(path, tmp_path / "out")
    block = payload["person_subject_mask"]
    assert block["mask_status"] == "unavailable"
    assert not block["person_specific"] and block["fallback_used"]
    assert not block["backend_errors"]


@pytest.mark.parametrize("status, expected", [(None, False), ("not_run", False), ("weak", True)])
def test_unavailable_material_analysis_does_not_invent_benign_counterevidence(status, expected):
    sections = {} if status is None else {"subject_material_realism": ModuleSummary(
        "Material", status=status, polarity="benign", score=0.1, pattern="subject_material_realism_supported",
    )}
    assert derive_signals(build_evidence_snapshot(sections)).material_realism_low is expected
