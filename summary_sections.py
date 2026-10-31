#summary_sections.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from typing import Optional
# local imports to avoid circular dependencies
from gui_semantics import ModuleSummary
from metadata_evidence import (
    GENERATION_PATTERNS, ENHANCEMENT_PATTERNS, classify_metadata_signals,
)

def build_osint_section(osint_result) -> ModuleSummary:
    section = ModuleSummary(name="OSINT")
    section.domain = "osint"
    section.polarity = "neutral"
    section.status = "not_run"
    section.note = "No reverse-image OSINT review has yet been recorded for this image."
    if osint_result is None:
        return section

    section.note = getattr(osint_result, "summary", "") or "OSINT review recorded."
    section.pattern = getattr(osint_result, "dominant_source_type", None)
    analyst_reviewed = getattr(osint_result, "analyst_reviewed", False)
    matches_found = getattr(osint_result, "matches_found", False)
    source_type = getattr(osint_result, "dominant_source_type", "unknown") or "unknown"
    if not analyst_reviewed and not matches_found:
        section.status = "not_run"
        section.polarity = "neutral"
        return section

    if analyst_reviewed and not matches_found:
        section.status = "inconclusive"
        section.polarity = "neutral"
        return section

    if matches_found:
        if source_type == "ai_gallery":
            section.status = "medium"
            section.polarity = "suspicious"
        elif source_type == "stock":
            section.status = "medium"
            section.polarity = "neutral"
        elif source_type in {"news", "social", "marketplace", "other", "unknown"}:
            section.status = "weak"
            section.polarity = "neutral"
        else:
            section.status = "weak"
            section.polarity = "neutral"
    return section

def build_metadata_section(exif_payload) -> ModuleSummary:
    section = ModuleSummary(name="Metadata")
    section.domain = "metadata"
    section.polarity = "neutral"
    if exif_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    
    classification = exif_payload.get("classification", {})
    signals = [s for s in exif_payload.get("signals", []) if isinstance(s, dict)]
    signal_ids = {s.get("id") for s in signals if isinstance(s, dict)}    
    # Reconcile legacy payload classifications with the actual evidence IDs.
    if signal_ids:
        classification = classify_metadata_signals(signal_ids)
    metadata_status = classification.get("metadata_status", "inconclusive")
    section.details = {
        "signal_ids": sorted(s for s in signal_ids if s),
        "metadata_signals": signals,
        "provenance_state": classification.get("provenance_state"),
        "provenance_verified": False,
        "camera_metadata_present": "CAMERA_METADATA_RICH" in signal_ids,
    }
    section.pattern = metadata_status
    # prompt override
    if "EMBEDDED_GENERATION_PROMPT" in signal_ids:
        section.pattern = "embedded_generation_prompt_detected"
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = 0.75
        section.note = (
            "Embedded generation prompt and/or workflow metadata detected in the image. "
            "Generation-specific structure provides an unverified declaration of AI-mediated creation. "
            "Metadata authenticity has not been verified; this does not establish a localized edit."
        )
        # Optional: surface snippet for UI/debugging
        evidence = [
            e
            for s in signals if s.get("id") == "EMBEDDED_GENERATION_PROMPT"
            for e in (s.get("evidence") or [])
        ]
        if evidence:
            snippet = str(evidence[0])[:300]
            section.details.update({
                "generation_prompt_snippet": snippet,
                "evidence_count": len(evidence),
            })
        return section    
    # creator override
    creator_identity = [
        e
        for s in signals if s.get("id") == "CREATOR_IDENTITY_PRESENT"
        for e in (s.get("evidence") or [])
    ]
    if creator_identity:
        creator_names = [
            str(e.get("value"))[:100]
            for e in creator_identity
            if e.get("value")
        ]
        section.details = section.details or {}
        section.details["creator_identity"] = creator_names[:3]
        section.note += " Creator attribution metadata is present."
    # mapping
    metadata_map = {
        "embedded_generation_prompt_detected": (
            "medium",
            "Metadata contains an embedded generation declaration; metadata authenticity is unverified.",
            0.75,
        ),
        "declared_synthetic_candidate": (
            "medium",
            "Metadata declares synthetic generation; metadata authenticity is unverified.",
            0.75,
        ),
        "declared_enhancement_candidate": (
            "medium",
            "Metadata declares enhancement or generative editing; authenticity is unverified. This does not establish whole-image generation.",
            0.70,
        ),
        "camera_metadata_present": (
            "medium",
            "Metadata contains multiple camera-acquisition fields consistent with a real photographic pipeline.",
            0.70,
        ),
        "provenance_present_unverified": (
            "weak",
            "Provenance-related metadata is present but not yet cryptographically verified.",
            0.45,
        ),
        "edited_or_processed_but_inconclusive": (
            "weak",
            "Editing or processing metadata is present, but it is not specific to AI use.",
            0.25,
        ),
        "sparse_or_stripped": (
            "weak",
            "Metadata is sparse or stripped, limiting provenance assessment. Absence alone does not indicate synthetic origin.",
            0.0,
        ),
        "inconclusive": (
            "inconclusive",
            "No explicit AI-related or provenance-grade metadata signals were found.",
            0.0,
        ),
    }
    section.status, section.note, section.score = metadata_map.get(
        metadata_status,
        ("inconclusive", "Metadata analysis completed.", 0.0),
    )
    if metadata_status in GENERATION_PATTERNS | ENHANCEMENT_PATTERNS:
        section.polarity = "suspicious"
    elif metadata_status == "camera_metadata_present":
        section.polarity = "benign"                
    else:
        section.polarity = "neutral"
    return section

def build_ela_section(ela_payload) -> ModuleSummary:
    section = ModuleSummary(name="ELA")
    section.domain = "local"
    section.polarity = "neutral"
    if ela_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    pattern = ela_payload.get("ela", {}).get("pattern", {})
    section.pattern = pattern.get("ela_pattern")
    section.note = pattern.get("ela_note", "ELA analysis completed.")
    section.status = "weak" if section.pattern else "inconclusive"
    return section

def build_noise_section(noise_payload) -> ModuleSummary:
    section = ModuleSummary(name="Residual")
    section.domain = "local"
    section.polarity = "neutral"
    if noise_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    pattern = noise_payload.get("noise", {}).get("pattern", {})
    section.pattern = pattern.get("noise_pattern")
    section.note = pattern.get("noise_note", "Residual analysis completed.")
    section.status = "weak" if section.pattern else "inconclusive"
    return section

def build_sensor_origin_section(sensor_origin_payload) -> ModuleSummary:
    section = ModuleSummary(name="Sensor Origin")
    section.domain = "sensor"
    section.polarity = "neutral"
    if sensor_origin_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    block = sensor_origin_payload.get("sensor_origin", {})
    pattern_block = block.get("pattern", {})
    scores = block.get("scores", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern_block.get("sensor_origin_pattern")
    section.note = pattern_block.get(
        "sensor_origin_note",
        "Sensor-origin analysis completed.",
    )
    section.score = scores.get("global_trace_strength")
    section.artifacts = artifacts
    section.details = scores
    if section.pattern == "camera_like_acquisition_supported":
        section.status = "medium"
        section.polarity = "benign"
    elif section.pattern == "weak_camera_pipeline_supported":
        section.status = "weak"
        section.polarity = "benign"        
    elif section.pattern == "localized_sensor_trace_inconsistency":
        section.status = "medium"
        section.polarity = "suspicious"
    elif section.pattern == "weak_or_absent_sensor_origin_traces":
        section.status = "weak"
        section.polarity = "neutral"
    elif section.pattern in {
        "microstructure_periodicity_inconclusive",
        "sensor_origin_inconclusive",
    }:
        section.status = "inconclusive"
        section.polarity = "neutral"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    if section.pattern == ("camera_like_acquisition_supported" or "weak_camera_pipeline_supported"):
        section.note += " This supports a camera-like acquisition pipeline but is not definitive on its own."
    elif section.pattern == "localized_sensor_trace_inconsistency":
        section.note += " This should be interpreted together with other forensic domains rather than in isolation."
    return section

def build_cfa_demosaic_section(cfa_demosaic_payload) -> ModuleSummary:
    section = ModuleSummary(name="CFA / Demosaicing")
    section.domain = "sensor_cfa"
    section.polarity = "neutral"
    if cfa_demosaic_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = cfa_demosaic_payload.get("cfa_demosaic", {})
    pattern = block.get("pattern", {})
    scores = block.get("scores", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern.get("cfa_demosaic_pattern")
    section.note = pattern.get("cfa_demosaic_note", "CFA / demosaicing analysis completed.",)
    section.score = scores.get("global_cfa_strength")
    section.artifacts = artifacts
    section.details = scores
    if section.pattern == "camera_like_cfa_supported":
        section.status = "medium"
        section.polarity = "benign"
    elif section.pattern == "weak_camera_cfa_supported":
        section.status = "weak"
        section.polarity = "benign"        
    elif section.pattern == "localized_cfa_inconsistency":
        section.status = "medium"
        section.polarity = "suspicious"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    if section.pattern in {"camera_like_cfa_supported", "weak_camera_cfa_supported"}:
        section.note += (
            " This is a supportive camera-pipeline compatibility signal, "
            "not a definitive authenticity claim."
        )
    elif section.pattern == "localized_cfa_inconsistency":
        section.note += (
            " This should be interpreted together with sensor-origin, "
            "boundary, and compression evidence."
        )
    return section

def build_region_mask_section(region_masks_payload) -> ModuleSummary:
    section = ModuleSummary(name="Region Mask")
    section.domain = "segmentation"
    section.polarity = "neutral"
    if region_masks_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    masks = region_masks_payload.get("region_masks", {})
    # New person-derived format, with fallback to legacy nested ratios.
    legacy_ratios = masks.get("ratios", {}) or {}
    subject = float(masks.get("subject_ratio", legacy_ratios.get("subject", 0.0)) or 0.0)
    boundary = float(masks.get("boundary_ratio", legacy_ratios.get("boundary", 0.0)) or 0.0)
    background = float(masks.get("background_ratio", legacy_ratios.get("background", 0.0)) or 0.0)
    source = masks.get("source", "unknown")
    person_mask_reliability = masks.get("person_mask_reliability")
    section.pattern = "region_segmentation_generated"
    section.score = None
    section.status = "weak"
    section.polarity = "neutral"
    section.note = (
        "Image was segmented into subject, boundary, and background regions "
        f"(subject={subject:.2f}, boundary={boundary:.2f}, background={background:.2f}; "
        f"source={source}"
        + (f", person-mask reliability={person_mask_reliability}" if person_mask_reliability else "")
        + "). "
        "These regions are used for localized forensic analysis."
    )
    section.details = {
        "source": source,
        "person_mask_reliability": person_mask_reliability,
        "subject_ratio": subject,
        "boundary_ratio": boundary,
        "background_ratio": background,
        "shape": masks.get("shape"),
        "height": masks.get("height"),
        "width": masks.get("width"),
        "subject_mask_path": masks.get("subject_mask_path"),
        "boundary_band_path": masks.get("boundary_band_path"),
        "background_mask_path": masks.get("background_mask_path"),
        **{key: masks.get(key) for key in (
            "mask_source", "mask_status", "mask_reliability", "person_specific", "fallback_used", "fallback_reason",
        )},
    }
    if masks.get("mask_status") == "approximate" or masks.get("person_specific") is False:
        section.status = "not_run"
        section.pattern = None
        section.note = (
            f"Approximate regions from {masks.get('mask_source', source)} are available for diagnostics only. "
            "They do not identify reliable person geometry and are not used for person-specific forensic conclusions. "
            f"Fallback reason: {masks.get('fallback_reason') or 'Person contour unavailable.'}"
        )
    elif masks.get("mask_status") == "limited":
        section.note += " Person segmentation is usable with quality limitations."
    return section

def build_segmentation_alignment_section(payload) -> ModuleSummary:
    section = ModuleSummary(name="Segmentation Alignment")
    section.domain = "segmentation"
    section.polarity = "neutral"
    if payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    s = payload.get("alignment_score", 0.0)
    raw = payload.get("raw_overlap", 0.0)
    section.score = float(s)
    section.pattern = "segmentation_boundary_alignment"
    if s >= 0.55:
        section.status = "strong"
        section.polarity = "suspicious"
        section.note = (
            "Cross-signal hotspots concentrate along the subject boundary, "
            "consistent with localized foreground/background processing differences."
        )
    elif s >= 0.35:
        section.status = "medium"
        section.polarity = "suspicious"
        section.note = (
            "Cross-signal hotspots partially align with the subject boundary, "
            "suggesting possible boundary-focused processing differences."
        )
    else:
        section.status = "weak"
        section.polarity = "neutral"
        section.note = (
            "Cross-signal hotspots do not meaningfully align with the subject boundary."
        )
    section.details = {
        "alignment_score": s,
        "raw_overlap": raw,
    }
    return section

def build_region_segmentation_section(payload) -> ModuleSummary:
    section = ModuleSummary(name="Region Segmentation")
    section.domain = "segmentation"
    section.polarity = "neutral"
    if payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = payload.get("region_segmentation", {})
    pattern = block.get("pattern")
    score = block.get("score", 0.0)
    ratios = block.get("ratios", {})
    metrics = block.get("metrics", {})
    section.pattern = pattern
    section.score = score
    section.details = {**ratios, **metrics}
    if pattern == "fragmented_subject_mask":
        section.status = "medium"
        section.polarity = "suspicious"
        section.note = "Subject mask is fragmented into multiple disconnected regions."
    elif pattern == "unnaturally_clean_segmentation":
        section.status = "medium"
        section.polarity = "suspicious"
        section.note = "Segmentation boundaries appear overly clean and uniform."
    elif pattern == "dominant_subject_ratio_anomaly":
        section.status = "weak"
        section.polarity = "suspicious"
        section.note = "Subject occupies an unusual proportion of the image."
    else:
        section.status = "weak"
        section.polarity = "benign"
        section.note = "Segmentation structure appears natural."
    return section

def build_cross_signal_section(cross_signal_payload) -> ModuleSummary:
    section = ModuleSummary(name="Cross-Signal")
    section.domain = "cross_signal"
    section.polarity = "neutral"
    if cross_signal_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    cross = cross_signal_payload.get("cross_signal", {})
    section.pattern = cross.get("cross_signal_pattern")
    section.note = cross.get("cross_signal_note", "Cross-signal analysis completed.")
    if section.pattern == "strong_hotspot_convergence":
        section.status = "medium"
        section.polarity = "suspicious"
    elif section.pattern == "partial_hotspot_convergence":
        section.status = "weak"
        section.polarity = "suspicious"
    elif section.pattern == "no_meaningful_convergence":
        section.status = "inconclusive"
        section.polarity = "neutral"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    return section

def build_boundary_section(cross_signal_payload) -> ModuleSummary:
    section = ModuleSummary(name="Boundary Signal")
    section.domain = "boundary"
    section.polarity = "neutral"
    if cross_signal_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    boundary = cross_signal_payload.get("boundary_signal", {})
    section.pattern = boundary.get("boundary_pattern")
    section.note = boundary.get("boundary_note", "Boundary signal analysis completed.")
    if section.pattern == "possible_foreground_background_processing_mismatch":
        section.status = "strong"
        section.polarity = "suspicious"
    elif section.pattern == "possible_boundary_fragment_convergence":
        section.status = "weak"
        section.polarity = "suspicious"
    elif section.pattern:
        section.status = "weak"
        section.polarity = "neutral"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    return section

def build_boundary_focus_section(boundary_focus_payload) -> ModuleSummary:
    section = ModuleSummary(name="Boundary Focus")
    section.domain = "boundary_focus"
    section.polarity = "neutral"
    if boundary_focus_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = boundary_focus_payload.get("boundary_focus", {})
    pattern = block.get("pattern", "boundary_processing_inconclusive")
    region_stats = block.get("region_stats", {})
    comparative = block.get("comparative_features", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern
    section.artifacts = artifacts
    section.details = {
        "ela_subject_mean": region_stats.get("ela_subject_mean"),
        "ela_boundary_mean": region_stats.get("ela_boundary_mean"),
        "ela_background_mean": region_stats.get("ela_background_mean"),
        "noise_subject_mean": region_stats.get("noise_subject_mean"),
        "noise_boundary_mean": region_stats.get("noise_boundary_mean"),
        "noise_background_mean": region_stats.get("noise_background_mean"),
        "ela_subject_std": region_stats.get("ela_subject_std"),
        "ela_boundary_std": region_stats.get("ela_boundary_std"),
        "ela_background_std": region_stats.get("ela_background_std"),
        "noise_subject_std": region_stats.get("noise_subject_std"),
        "noise_boundary_std": region_stats.get("noise_boundary_std"),
        "noise_background_std": region_stats.get("noise_background_std"),
        "ela_boundary_boost": comparative.get("ela_boundary_boost"),
        "noise_boundary_boost": comparative.get("noise_boundary_boost"),
        "ela_boundary_ratio": comparative.get("ela_boundary_ratio"),
        "noise_boundary_ratio": comparative.get("noise_boundary_ratio"),
        "combined_boundary_boost": comparative.get("combined_boundary_boost"),
        "combined_boundary_ratio": comparative.get("combined_boundary_ratio"),
        "transition_anomaly_score": comparative.get("transition_anomaly_score"),
    }
    ela_boundary_boost = comparative.get("ela_boundary_boost", 0.0) or 0.0
    noise_boundary_boost = comparative.get("noise_boundary_boost", 0.0) or 0.0
    ela_boundary_ratio = comparative.get("ela_boundary_ratio", 1.0) or 1.0
    noise_boundary_ratio = comparative.get("noise_boundary_ratio", 1.0) or 1.0
    combined_boundary_boost = comparative.get("combined_boundary_boost", 0.0) or 0.0
    combined_boundary_ratio = comparative.get("combined_boundary_ratio", 1.0) or 1.0
    transition_anomaly_score = comparative.get("transition_anomaly_score", 0.0) or 0.0
    if pattern == "boundary_focused_transition_anomaly":
        section.status = "strong"
        section.polarity = "suspicious"
        section.score = float(max(combined_boundary_boost, transition_anomaly_score, 0.0))
        section.note = (
            "A pronounced transition anomaly is present along the subject boundary. "
            "This is consistent with localized compositing, masking, or a foreground/background processing mismatch. "
        )
    elif pattern == "boundary_focused_processing_mismatch":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(max(combined_boundary_boost, 0.0))
        section.note = (
            "Processing intensity is elevated in the boundary region relative to both the subject and the background. "
            "This supports a localized boundary mismatch."
        )
    elif pattern == "boundary_processing_convergence_supported":
        section.status = "weak"
        section.polarity = "benign"
        section.score = 0.0
        section.note = (
            "Boundary-focused ELA and residual analysis does not show a meaningful contour-band mismatch relative "
            "to the subject and background regions."
        )
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
        section.score = float(max(combined_boundary_boost, transition_anomaly_score, 0.0))
        section.note = (
            "The boundary region does not differ strongly from the subject and background. "
            "No clear boundary-specific anomaly is detected. "
        )
    section.note += (
        f"Combined boundary ratio={combined_boundary_ratio:.3f}; "
        f"combined boundary boost={combined_boundary_boost:.3f}; "
        f"transition anomaly score={transition_anomaly_score:.3f}; "
        f"ELA boundary ratio={ela_boundary_ratio:.3f}; "
        f"residual boundary ratio={noise_boundary_ratio:.3f}."
    )
    return section

def build_fft_section(fft_payload) -> ModuleSummary:
    section = ModuleSummary(name="Frequency Domain")
    section.domain = "frequency"
    section.polarity = "neutral"
    if fft_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    fft = fft_payload.get("fft", {})
    section.pattern = fft.get("frequency_pattern")
    section.note = fft.get("frequency_note", "Frequency-domain analysis completed.")
    section.score = fft.get("fft_anomaly_score")
    section.artifacts = fft.get("artifacts", {})
    section.details = {
        "fft_anomaly_score": fft.get("fft_anomaly_score"),
        "radial_profile_score": fft.get("radial_profile_score"),
        "midband_excess_score": fft.get("midband_excess_score"),
        "ring_irregularity_score": fft.get("ring_irregularity_score"),
        "peak_periodicity_score": fft.get("peak_periodicity_score"),
        "peak_symmetry_score": fft.get("peak_symmetry_score"),
        "peak_count": fft.get("peak_count"),
        "anisotropy_score": fft.get("anisotropy_score"),
        "axis_bias_score": fft.get("axis_bias_score"),
        "diagonal_bias_score": fft.get("diagonal_bias_score"),
        "grid_hypothesis_present": fft.get("grid_hypothesis_present"),
        "dominant_wavelength_x": fft.get("dominant_wavelength_x"),
        "dominant_wavelength_y": fft.get("dominant_wavelength_y"),
        "grid_hypothesis_strength": fft.get("grid_hypothesis_strength"),
        "grid_response_score": fft.get("grid_response_score"),
        "paired_peak_count": fft.get("paired_peak_count"),        
    }
    if section.pattern in {"possible_decoder_grid_signature", "fft_grid_detected"}:
        section.status = "strong"
        section.polarity = "suspicious"
    elif section.pattern == "structured_frequency_anomaly":
        section.status = "medium"
        section.polarity = "suspicious"
    elif section.pattern == "mild_structured_periodicity":
        section.status = "weak"
        section.polarity = "neutral"
    elif section.pattern:
        section.status = "inconclusive"
        section.polarity = "neutral"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    return section

def build_region_fft_section(region_fft_payload) -> ModuleSummary:
    section = ModuleSummary(name="Region Frequency")
    section.domain = "region_frequency"
    section.polarity = "neutral"
    if region_fft_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = region_fft_payload.get("region_fft", {})
    pattern = block.get("pattern", "region_frequency_inconclusive")
    subject_metrics = block.get("subject_metrics", {})
    boundary_metrics = block.get("boundary_metrics", {})
    background_metrics = block.get("background_metrics", {})
    comparative = block.get("comparative_features", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern
    section.artifacts = artifacts
    section.details = {
        "subject_fft_anomaly_score": subject_metrics.get("fft_anomaly_score"),
        "subject_peak_periodicity_score": subject_metrics.get("peak_periodicity_score"),
        "subject_peak_symmetry_score": subject_metrics.get("peak_symmetry_score"),
        "subject_anisotropy_score": subject_metrics.get("anisotropy_score"),
        "subject_grid_response_score": subject_metrics.get("grid_response_score"),
        "boundary_fft_anomaly_score": boundary_metrics.get("fft_anomaly_score"),
        "boundary_peak_periodicity_score": boundary_metrics.get("peak_periodicity_score"),
        "boundary_peak_symmetry_score": boundary_metrics.get("peak_symmetry_score"),
        "boundary_anisotropy_score": boundary_metrics.get("anisotropy_score"),
        "boundary_grid_response_score": boundary_metrics.get("grid_response_score"),
        "background_fft_anomaly_score": background_metrics.get("fft_anomaly_score"),
        "background_peak_periodicity_score": background_metrics.get("peak_periodicity_score"),
        "background_peak_symmetry_score": background_metrics.get("peak_symmetry_score"),
        "background_anisotropy_score": background_metrics.get("anisotropy_score"),
        "background_grid_response_score": background_metrics.get("grid_response_score"),
        "subject_vs_background_fft_gap": comparative.get("subject_vs_background_fft_gap"),
        "boundary_vs_subject_fft_gap": comparative.get("boundary_vs_subject_fft_gap"),
        "boundary_vs_background_fft_gap": comparative.get("boundary_vs_background_fft_gap"),
        "subject_grid_response_ratio": comparative.get("subject_grid_response_ratio"),
        "boundary_grid_response_ratio": comparative.get("boundary_grid_response_ratio"),
    }
    boundary_gap = comparative.get("boundary_vs_background_fft_gap", 0.0) or 0.0
    subject_gap = comparative.get("subject_vs_background_fft_gap", 0.0) or 0.0
    boundary_ratio = comparative.get("boundary_grid_response_ratio", 1.0) or 1.0
    subject_ratio = comparative.get("subject_grid_response_ratio", 1.0) or 1.0
    if pattern == "boundary_band_frequency_mismatch":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(max(boundary_gap, 0.0))
        section.note = (
            "Structured periodicity is stronger in the boundary region than in the background. "
            "This suggests a boundary-localized processing mismatch."
        )
    elif pattern == "subject_background_frequency_mismatch":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(max(subject_gap, 0.0))
        section.note = (
            "Region-aware frequency analysis finds stronger structured periodicity in the subject region "
            "than in the background, suggesting subject/background processing inconsistency."
        )
    elif pattern == "region_frequency_convergence_supported":
        section.status = "weak"
        section.polarity = "benign"
        section.score = float(
            background_metrics.get("fft_anomaly_score", 0.0) or 0.0
        )
        section.note = (
            "Region-aware frequency analysis does not show a meaningful mismatch between subject, boundary, "
            "and background regions."
        )
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
        section.score = float(max(boundary_gap, subject_gap, 0.0))
        section.note = (
            "Region-aware frequency analysis completed, but the difference between subject, contour band, "
            "and background is not strong enough for a specific conclusion."
        )
    # Add a concise quantitative tail for debugging and inspection.
    section.note += (
        f" Subject/background FFT gap={subject_gap:.3f}; "
        f"boundary/background FFT gap={boundary_gap:.3f}; "
        f"subject grid ratio={subject_ratio:.3f}; "
        f"boundary grid ratio={boundary_ratio:.3f}."
    )
    return section

def build_patch_spatial_section(patch_spatial_payload) -> ModuleSummary:
    section = ModuleSummary(name="Patch Spatial")
    section.domain = "patch_spatial"
    section.polarity = "neutral"
    if patch_spatial_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = patch_spatial_payload.get("patch_spatial", {})
    pattern = block.get("pattern", "spatial_patch_recurrence_inconclusive")
    region_stats = block.get("region_stats", {})
    comparative = block.get("comparative_features", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern
    section.artifacts = artifacts
    section.details = {
        "areas": region_stats.get("areas"),
        "endpoint_counts": region_stats.get("endpoint_counts"),
        "endpoint_weights": region_stats.get("endpoint_weights"),
        "endpoint_densities": region_stats.get("endpoint_densities"),
        "weight_densities": region_stats.get("weight_densities"),
        "pair_category_counts": region_stats.get("pair_category_counts"),
        "pair_category_weights": region_stats.get("pair_category_weights"),
        "total_pair_count": region_stats.get("total_pair_count"),
        "total_pair_weight": region_stats.get("total_pair_weight"),
        "bridge_count": region_stats.get("bridge_count"),
        "bridge_weight": region_stats.get("bridge_weight"),
        "internal_count": region_stats.get("internal_count"),
        "internal_weight": region_stats.get("internal_weight"),
        "subject_similarity_ratio": comparative.get("subject_similarity_ratio"),
        "boundary_similarity_ratio": comparative.get("boundary_similarity_ratio"),
        "subject_weight_ratio": comparative.get("subject_weight_ratio"),
        "boundary_weight_ratio": comparative.get("boundary_weight_ratio"),
        "bridge_ratio": comparative.get("bridge_ratio"),
        "bridge_weight_ratio": comparative.get("bridge_weight_ratio"),
        "boundary_involvement_ratio": comparative.get("boundary_involvement_ratio"),
        "boundary_involvement_weight_ratio": comparative.get("boundary_involvement_weight_ratio"),
        "boundary_correlated_ratio": comparative.get("boundary_correlated_ratio"),
        "boundary_correlated_weight_ratio": comparative.get("boundary_correlated_weight_ratio"),
        "subject_localized_ratio": comparative.get("subject_localized_ratio"),
        "subject_localized_weight_ratio": comparative.get("subject_localized_weight_ratio"),
        "cross_region_patch_reuse_ratio": comparative.get("cross_region_patch_reuse_ratio"),
        "subject_internal_ratio": comparative.get("subject_internal_ratio"),
        "subject_internal_weight_ratio": comparative.get("subject_internal_weight_ratio"),        
    }
    subject_ratio = comparative.get("subject_similarity_ratio", 1.0) or 1.0
    boundary_ratio = comparative.get("boundary_similarity_ratio", 1.0) or 1.0
    subject_weight_ratio = comparative.get("subject_weight_ratio", 1.0) or 1.0
    boundary_weight_ratio = comparative.get("boundary_weight_ratio", 1.0) or 1.0
    bridge_ratio = comparative.get("bridge_ratio", 1.0) or 1.0
    bridge_weight_ratio = comparative.get("bridge_weight_ratio", 1.0) or 1.0
    boundary_involvement_ratio = comparative.get("boundary_involvement_ratio", 1.0) or 1.0
    boundary_corr_ratio = comparative.get("boundary_correlated_ratio", 1.0) or 1.0
    subject_local_ratio = comparative.get("subject_localized_ratio", 1.0) or 1.0
    cross_ratio = comparative.get("cross_region_patch_reuse_ratio", 1.0) or 1.0
    subject_internal_ratio = comparative.get("subject_internal_ratio", 0.0) or 0.0
    subject_internal_weight_ratio = comparative.get("subject_internal_weight_ratio", 0.0) or 0.0    
    if pattern == "subject_internal_synthetic_recurrence":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(max(subject_internal_ratio, subject_internal_weight_ratio, 0.0))
        section.note = (
            "Spatial patch analysis shows repeated high-similarity patch structure concentrated "
            "within the subject region, supporting subject-internal synthetic texture recurrence."
        )
    elif pattern == "cross_region_patch_recurrence":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(max(bridge_ratio, bridge_weight_ratio, boundary_involvement_ratio, 0.0))
        section.note = (
            "Spatial patch analysis shows a high proportion of matched patch pairs bridging subject, "
            "boundary, and background regions, supporting cross-regime structural reuse consistent "
            "with compositing or AI-mediated enhancement."
        )
    elif pattern == "boundary_correlated_patch_recurrence":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(max(boundary_corr_ratio, boundary_ratio, boundary_weight_ratio, 0.0))
        section.note = (
            "Spatial patch analysis shows matched patch pairs concentrated in the contour band "
            "and along the subject-boundary topology, supporting boundary-correlated structural reuse."
        )
    elif pattern == "subject_localized_patch_recurrence":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(max(subject_local_ratio, subject_ratio, subject_weight_ratio, 0.0))
        section.note = (
            "Matched patch pairs are concentrated in the subject region relative to the background. "
            "This supports subject-localized structural reuse consistent with synthetic texture generation."
        )
    elif pattern == "scene_wide_patch_recurrence":
        section.status = "weak"
        section.polarity = "neutral"
        section.score = float(max(subject_ratio, boundary_ratio, bridge_ratio, 0.0))
        section.note = (
            "Patch recurrence is distributed across multiple regions rather than localized. "
            "This may reflect broader scene repetition rather than a localized anomaly."
        )
    elif pattern == "patch_spatial_convergence_supported":
        section.status = "weak"
        section.polarity = "benign"
        section.score = 0.0
        section.note = (
            "Spatial patch analysis does not show a meaningful localization difference between subject, "
            "contour band, and background."
        )
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
        section.score = float(max(subject_ratio, boundary_ratio, cross_ratio, bridge_ratio, 0.0))
        section.note = (
            "Spatial patch analysis completed, but matched patch pairs are not strongly localized enough "
            "to support a specific regional conclusion."
        )
    section.note += (
        f" Subject density ratio={subject_ratio:.3f}; "
        f"boundary density ratio={boundary_ratio:.3f}; "
        f"subject weight ratio={subject_weight_ratio:.3f}; "
        f"boundary weight ratio={boundary_weight_ratio:.3f}; "
        f"bridge ratio={bridge_ratio:.3f}; "
        f"bridge weight ratio={bridge_weight_ratio:.3f}; "
        f"boundary involvement ratio={boundary_involvement_ratio:.3f}; "
        f"boundary-correlated ratio={boundary_corr_ratio:.3f}; "
        f"subject-localized ratio={subject_local_ratio:.3f};"
        f"subject-internal ratio={subject_internal_ratio:.3f}; "
        f"subject-internal weight ratio={subject_internal_weight_ratio:.3f}."        
    )
    return section

def build_subject_texture_consistency_section(subject_texture_consistency_payload) -> ModuleSummary:
    section = ModuleSummary(name="Subject Texture")
    section.domain = "subject_texture"
    section.polarity = "neutral"
    if subject_texture_consistency_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = subject_texture_consistency_payload.get("subject_texture_consistency", {})
    pattern = block.get("pattern", "subject_texture_consistency_inconclusive")
    note = block.get("note", "Subject-only texture analysis completed.")
    scores = block.get("scores", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern
    section.artifacts = artifacts
    section.details = {
        "patch_count": scores.get("patch_count"),
        "mean_neighbor_similarity": scores.get("mean_neighbor_similarity"),
        "p90_neighbor_similarity": scores.get("p90_neighbor_similarity"),
        "dense_similarity_ratio": scores.get("dense_similarity_ratio"),
        "soft_recurrence_score": scores.get("soft_recurrence_score"),
        "subject_support_coverage": scores.get("subject_support_coverage"),
        "texture_focus_area": scores.get("texture_focus_area"),
        "full_subject_area": scores.get("full_subject_area"),
    }
    soft_score = scores.get("soft_recurrence_score", 0.0) or 0.0
    mean_sim = scores.get("mean_neighbor_similarity", 0.0) or 0.0
    p90_sim = scores.get("p90_neighbor_similarity", 0.0) or 0.0
    dense_ratio = scores.get("dense_similarity_ratio", 0.0) or 0.0
    if pattern == "subject_texture_support_insufficient":
        return ModuleSummary(
            name="Subject Texture",
            status="inconclusive",
            polarity="neutral",
            pattern=pattern,
            score=0.0,
            note=note,
            details=scores,
        )    
    elif pattern == "subject_internal_stochastic_repetition":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(soft_score)
        section.note = note
    elif pattern == "subject_texture_stochastic_regularization":
        section.status = "weak"
        section.polarity = "suspicious"
        section.score = float(soft_score)
        section.note = note
    elif pattern == "subject_texture_natural_variation_supported":
        section.status = "weak"
        section.polarity = "benign"
        section.score = 0.0
        section.note = note
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
        section.score = float(soft_score)
        section.note = note
    section.note += (
        f" Soft recurrence score={soft_score:.3f}; "
        f"mean neighbor similarity={mean_sim:.3f}; "
        f"p90 neighbor similarity={p90_sim:.3f}; "
        f"dense similarity ratio={dense_ratio:.3f}."
    )
    return section


def build_subject_boundary_section(subject_boundary_payload) -> ModuleSummary:
    section = ModuleSummary(name="Subject Boundary")
    section.domain = "boundary_semantic"
    section.polarity = "neutral"
    if subject_boundary_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    block = subject_boundary_payload.get("subject_boundary", {})
    pattern = block.get("pattern", {})
    scores = block.get("scores", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern.get("subject_boundary_pattern")
    section.note = pattern.get(
        "subject_boundary_note",
        "Subject-boundary analysis completed.",
    )
    section.score = scores.get("boundary_anomaly_score")
    section.artifacts = artifacts
    section.details = scores
    if section.pattern == "possible_subject_background_segmentation_artifact":
        section.status = "strong"
        section.polarity = "suspicious"
    elif section.pattern == "possible_boundary_transition_inconsistency":
        section.status = "medium"
        section.polarity = "suspicious"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"

    return section

def build_patch_similarity_section(patch_similarity_payload) -> ModuleSummary:
    section = ModuleSummary(name="Patch Similarity")
    section.domain = "patch"
    section.polarity = "neutral"

    if patch_similarity_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    block = patch_similarity_payload.get("patch_similarity", {})
    section.pattern = block.get("similarity_pattern")
    section.note = block.get("similarity_note", "Patch-similarity analysis completed.")
    section.score = block.get("clone_suspicion_score")
    section.artifacts = block.get("artifacts", {})
    section.details = {
        "repetition_score": block.get("repetition_score"),
        "clone_suspicion_score": block.get("clone_suspicion_score"),
        "pair_count": block.get("pair_count"),
        "spatially_separated_pair_count": block.get("spatially_separated_pair_count"),
        "mean_similarity": block.get("mean_similarity"),
        "max_similarity": block.get("max_similarity"),
        "coverage_ratio": block.get("coverage_ratio"),
    }
    if section.pattern == "possible_clone_reuse":
        section.status = "strong"
        section.polarity = "suspicious"
    elif section.pattern in {
        "possible_synthetic_texture_repetition",
        "structured_patch_recurrence",
    }:
        section.status = "medium"
        section.polarity = "suspicious"
    elif section.pattern == "localized_repetition_detected":
        section.status = "weak"
        section.polarity = "neutral"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    return section

def build_subject_process_asymmetry_section(subject_process_asymmetry_payload) -> ModuleSummary:
    section = ModuleSummary(name="Subject Process Asymmetry")
    section.domain = "region_asymmetry"
    section.polarity = "neutral"
    if subject_process_asymmetry_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = subject_process_asymmetry_payload.get("subject_process_asymmetry", {})
    pattern = block.get("pattern", "subject_process_asymmetry_inconclusive")
    note = block.get("note", "Subject/background process asymmetry analysis completed.")
    scores = block.get("scores", {})
    artifacts = block.get("artifacts", {})
    controls = block.get("controls", {})
    section.pattern = pattern
    section.artifacts = artifacts
    section.details = {
        "asymmetry_score": scores.get("asymmetry_score"),
        "regularization_dominance_score": scores.get("regularization_dominance_score"),
        "process_divergence_score": scores.get("process_divergence_score"),
        "boundary_paradox_score": scores.get("boundary_paradox_score"),
        "baseline_reliability_score": scores.get("baseline_reliability_score"),
        "valid_subject_patch_count": controls.get("valid_subject_patch_count"),
        "valid_boundary_patch_count": controls.get("valid_boundary_patch_count"),
        "valid_background_patch_count": controls.get("valid_background_patch_count"),
        "background_is_highly_repetitive": controls.get("background_is_highly_repetitive"),
        "region_geometry_unreliable": controls.get("region_geometry_unreliable", False),
        "subject_mask_area_ratio": controls.get("subject_mask_area_ratio"),
        "background_mask_area_ratio": controls.get("background_mask_area_ratio"),      
    }
    asym = scores.get("asymmetry_score", 0.0) or 0.0
    reg = scores.get("regularization_dominance_score", 0.0) or 0.0
    div = scores.get("process_divergence_score", 0.0) or 0.0
    par = scores.get("boundary_paradox_score", 0.0) or 0.0
    rel = scores.get("baseline_reliability_score", 0.0) or 0.0

    if pattern == "subject_process_asymmetry_support_unreliable":
        section.status = "inconclusive"
        section.polarity = "neutral"
        section.score = 0.00        
    elif pattern == "subject_process_asymmetry_strong":
        section.status = "strong"
        section.polarity = "suspicious"
        section.score = float(asym)
        section.note = note
    elif pattern == "subject_surface_regularization_dominant":
        section.status = "medium"
        section.polarity = "suspicious"
        section.score = float(asym)
        section.note = note
    elif pattern == "subject_background_texture_asymmetry":
        section.status = "weak"
        section.polarity = "suspicious"
        section.score = float(asym)
        section.note = note
    elif pattern == "subject_background_process_convergence_supported":
        section.status = "weak"
        section.polarity = "benign"
        section.score = 0.0
        section.note = note
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
        section.score = float(asym)
        section.note = note
    section.note += (
        f"Asymmetry score={asym:.3f}; "
        f"regularization dominance={reg:.3f}; "
        f"process divergence={div:.3f}; "
        f"boundary paradox={par:.3f}; "
        f"baseline reliability={rel:.3f}."
    )
    return section

def build_subject_material_realism_section(subject_material_realism_payload) -> ModuleSummary:
    section = ModuleSummary(name="Subject Material Realism")
    section.domain = "subject_material"
    section.polarity = "neutral"
    if subject_material_realism_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section
    block = subject_material_realism_payload.get("subject_material_realism", {})
    pattern = block.get("pattern", "subject_material_realism_inconclusive")
    note = block.get("note", "")
    scores = block.get("scores", {})
    artifacts = block.get("artifacts", {})
    controls = block.get("controls", {})
    realism_score = float(scores.get("subject_material_realism_score", 0.0) or 0.0)
    section.pattern = pattern
    section.score = realism_score
    section.artifacts = artifacts
    section.details = {
        "microtexture_suppression": scores.get("microtexture_suppression"),
        "material_homogenization": scores.get("material_homogenization"),
        "structure_without_stochasticity": scores.get("structure_without_stochasticity"),
        "distribution_compression": scores.get("distribution_compression"),
        "patch_count": controls.get("patch_count"),
    }
    # --- mapping ---
    if pattern == "subject_material_realism_failure_strong":
        section.status = "strong"
        section.polarity = "suspicious"
    elif pattern == "subject_material_regularization_dominant":
        section.status = "medium"
        section.polarity = "suspicious"
    elif pattern == "subject_structure_without_stochasticity":
        section.status = "weak"
        section.polarity = "suspicious"
    elif pattern == "subject_material_realism_supported":
        section.status = "weak"
        section.polarity = "benign"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    section.note = note + f" Realism score={realism_score:.3f}."
    return section

def build_compression_history_section(compression_history_payload) -> ModuleSummary:
    section = ModuleSummary(name="Compression History")
    section.domain = "compression"
    section.polarity = "neutral"
    if compression_history_payload is None:
        section.status = "not_run"
        section.note = "Not run yet."
        return section

    block = compression_history_payload.get("compression_history", {})
    pattern = block.get("pattern", {})
    scores = block.get("scores", {})
    artifacts = block.get("artifacts", {})
    section.pattern = pattern.get("compression_history_pattern")
    section.note = pattern.get(
        "compression_history_note",
        "Compression-history analysis completed.",
    )
    section.score = scores.get("grid_strength_score")
    section.artifacts = artifacts
    section.details = scores
    if section.pattern == "single_history_jpeg_consistent":
        section.status = "medium"
        section.polarity = "benign"
    elif section.pattern == "localized_compression_inconsistency":
        section.status = "strong"
        section.polarity = "suspicious"
    elif section.pattern in {
        "possible_double_jpeg_history",
        "block_grid_history_anomaly",
    }:
        section.status = "medium"
        section.polarity = "suspicious"
    else:
        section.status = "inconclusive"
        section.polarity = "neutral"
    return section

def extract_overlay_paths(cross_signal_payload) -> dict[str, str]:
    if not cross_signal_payload:
        return {}
    return cross_signal_payload.get("shared_boundary_overlay_paths", {}) or {}

def extract_module_scores(
    sections: dict[str, ModuleSummary]
) -> dict[str, Optional[float]]:
    return {key: section.score for key, section in sections.items()}
