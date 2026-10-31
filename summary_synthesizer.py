# summary_synthesizer.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
# hypothesis_engine → produces ScoreCard + sections
# ↓
# summary_synthesizer → builds structured summary
# ↓
# narrative_builder → turns into readable text
#

from __future__ import annotations
# local imports to avoid circular dependencies
from decision_logic import synthesize_overall
from narrative_builder import render_summary_html, render_summary_text
from summary_types import SummaryResult
from summary_sections import (
    build_boundary_focus_section,
    build_boundary_section,
    build_compression_history_section,
    build_cross_signal_section,
    build_ela_section,
    build_fft_section,
    build_region_fft_section,
    build_region_fft_section,
    build_region_mask_section,
    build_metadata_section,
    build_noise_section,
    build_osint_section,
    build_patch_similarity_section,
    build_sensor_origin_section,
    build_subject_boundary_section,
    build_cfa_demosaic_section,
    build_subject_texture_consistency_section,
    extract_module_scores,
    extract_overlay_paths,
    build_patch_spatial_section,
    build_subject_process_asymmetry_section,
    build_subject_material_realism_section,
    build_segmentation_alignment_section
)

def build_context_info(scene_context: dict | None) -> str:
    """
    Build a human-readable note describing all active analyst-supplied scene context flags.
    """
    if not scene_context:
        return ""
    labels = []
    if scene_context.get("natural_repetition", False):
        labels.append("natural repetition")
    if scene_context.get("decorative_geometric", False):
        labels.append("decorative or geometric repetition")
    if scene_context.get("smartphone_computational", False):
        labels.append("smartphone computational photography")
    if scene_context.get("screen_origin", False):
        labels.append("possible screen/display-origin structure")
    if not labels:
        return ""
    # Natural language joining
    if len(labels) == 1:
        context_str = labels[0]
    elif len(labels) == 2:
        context_str = f"{labels[0]} and {labels[1]}"
    else:
        context_str = ", ".join(labels[:-1]) + f", and {labels[-1]}"
    return (
        "Interpretation was moderated by analyst-supplied scene context: "
        f"{context_str}."
    )

def build_summary_result(state, osint_result=None, scene_context: dict | None = None) -> SummaryResult:
    """
    Main orchestration entrypoint for building a full SummaryResult.
    Responsibilities:
    1. Build per-module summaries from payloads
    2. Extract overlays and score map
    3. Ask decision_logic for the overall forensic reading
    4. Render plain-text and HTML summaries
    This file intentionally contains orchestration only.
    """
    result = SummaryResult()
    if state is None:
        return result
    result.context_info = build_context_info(scene_context)
    # Per-module sections
    result.sections["osint"] = build_osint_section(osint_result)
    result.sections["metadata"] = build_metadata_section(state.exif_payload)
    result.sections["ela"] = build_ela_section(state.ela_payload)
    result.sections["noise"] = build_noise_section(state.noise_payload)
    result.sections["sensor_origin"] = build_sensor_origin_section(state.sensor_origin_payload)
    result.sections["region_masks"] = build_region_mask_section(state.region_masks_payload)
    result.sections["segmentation_alignment"] = build_segmentation_alignment_section(state.segmentation_alignment_payload)
    result.sections["region_fft"] = build_region_fft_section(state.region_fft_payload)
    result.sections["cross_signal"] = build_cross_signal_section(state.cross_signal_payload)
    result.sections["boundary"] = build_boundary_section(state.cross_signal_payload)
    result.sections["boundary_focus"] = build_boundary_focus_section(state.boundary_focus_payload)
    result.sections["fft"] = build_fft_section(state.fft_payload)
    result.sections["subject_boundary"] = build_subject_boundary_section(state.subject_boundary_payload)
    result.sections["subject_texture_consistency"] = build_subject_texture_consistency_section(state.subject_texture_consistency_payload)
    result.sections["subject_process_asymmetry"] = build_subject_process_asymmetry_section(state.subject_process_asymmetry_payload)
    result.sections["subject_material_realism"] = build_subject_material_realism_section(state.subject_material_realism_payload)    
    result.sections["patch_similarity"] = build_patch_similarity_section(state.patch_similarity_payload)
    result.sections["patch_spatial"] = build_patch_spatial_section(state.patch_spatial_payload)
    result.sections["compression_history"] = build_compression_history_section(state.compression_history_payload)
    result.sections["cfa_demosaic"] = build_cfa_demosaic_section(state.cfa_demosaic_payload)
    # Derived attachments / metadata
    result.overlay_paths = extract_overlay_paths(state.cross_signal_payload)
    result.module_scores = extract_module_scores(result.sections)
    # Overall decision
    analysis_mode=getattr(state, "analysis_mode", None)
    result.overall_pattern, result.overall_text, result.overall_confidence, result.overall_polarity, result.reasoning_trace = synthesize_overall(result.sections, scene_context=scene_context, analysis_mode=analysis_mode, )    # Rendered outputs
    result.full_text = render_summary_text(result)
    result.full_html = render_summary_html(result)
    return result