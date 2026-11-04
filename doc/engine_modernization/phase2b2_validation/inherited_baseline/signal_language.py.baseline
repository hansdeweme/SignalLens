
#signal_language.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

def humanize_signal(pattern: str) -> str:
    entry = SIGNAL_LANGUAGE.get(pattern)
    if not entry:
        return pattern.replace("_", " ")  # fallback
    return entry["label"]

def explain_pattern(pattern: str) -> str:
    entry = SIGNAL_LANGUAGE.get(pattern)
    if entry and "explanation" in entry:
        return entry["explanation"]
    return humanize_signal(pattern)

SIGNAL_LANGUAGE = {

    # --------------------------------------------------
    # METADATA / PROVENANCE
    # --------------------------------------------------

    "declared_synthetic_candidate": {
        "label": "metadata indicates declared or tool-attributed synthetic generation",
        "short": "metadata synthetic",
        "polarity": "suspicious",
    },
    "declared_enhancement_candidate": {
        "label": "metadata indicates declared or tool-attributed enhancement or generative editing",
        "short": "metadata enhancement",
        "polarity": "suspicious",
    },
    "provenance_present_unverified": {
        "label": "provenance-related metadata is present but not verified",
        "short": "unverified provenance",
        "polarity": "benign",
    },
    "edited_or_processed_but_inconclusive": {
        "label": "metadata indicates editing or processing, but not specific to AI use",
        "short": "generic editing metadata",
        "polarity": "neutral",
    },
    "sparse_or_stripped": {
        "label": "metadata is sparse or stripped and provides no provenance clues",
        "short": "metadata missing",
        "polarity": "neutral",
    },
    "inconclusive": {
        "label": "metadata does not provide meaningful evidence",
        "short": "metadata inconclusive",
        "polarity": "neutral",
    },

    # --------------------------------------------------
    # SENSOR / CFA
    # --------------------------------------------------

    "camera_like_acquisition_supported": {
        "label": "low-level signals are consistent with a camera acquisition pipeline",
        "short": "camera-like acquisition",
        "polarity": "benign",
    },
    "localized_sensor_trace_inconsistency": {
        "label": "sensor-origin traces are inconsistent across regions",
        "short": "sensor inconsistency",
        "polarity": "suspicious",
    },
    "weak_or_absent_sensor_origin_traces": {
        "label": "sensor-origin traces are weak or absent",
        "short": "weak sensor traces",
        "polarity": "neutral",
    },
    "sensor_origin_inconclusive": {
        "label": "sensor-origin analysis does not provide a clear signal",
        "short": "sensor inconclusive",
        "polarity": "neutral",
    },

    "camera_like_cfa_supported": {
        "label": "CFA / demosaicing structure is consistent with a camera pipeline",
        "short": "camera-like CFA",
        "polarity": "benign",
    },
    "localized_cfa_inconsistency": {
        "label": "CFA / demosaicing patterns are inconsistent across regions",
        "short": "CFA inconsistency",
        "polarity": "suspicious",
    },

    # --------------------------------------------------
    # CROSS SIGNAL / BOUNDARY
    # --------------------------------------------------

    "strong_hotspot_convergence": {
        "label": "multiple forensic signals converge on the same localized regions",
        "short": "strong signal convergence",
        "polarity": "suspicious",
    },
    "partial_hotspot_convergence": {
        "label": "some forensic signals converge on localized regions",
        "short": "partial convergence",
        "polarity": "suspicious",
    },
    "no_meaningful_convergence": {
        "label": "independent forensic signals do not converge meaningfully",
        "short": "no convergence",
        "polarity": "neutral",
    },

    "possible_foreground_background_processing_mismatch": {
        "label": "foreground and background appear to have been processed differently",
        "short": "foreground/background mismatch",
        "polarity": "suspicious",
    },
    "possible_boundary_fragment_convergence": {
        "label": "fragmented boundary regions show signs of localized processing",
        "short": "fragmented boundary anomaly",
        "polarity": "suspicious",
    },

    # --------------------------------------------------
    # BOUNDARY FOCUS
    # --------------------------------------------------

    "boundary_focused_transition_anomaly": {
        "label": "strong transition anomaly is present along the subject boundary",
        "short": "boundary transition anomaly",
        "polarity": "suspicious",
    },
    "boundary_focused_processing_mismatch": {
        "label": "boundary region shows elevated processing relative to subject and background",
        "short": "boundary processing mismatch",
        "polarity": "suspicious",
    },
    "boundary_processing_convergence_supported": {
        "label": "boundary processing is consistent with surrounding regions",
        "short": "boundary consistent",
        "polarity": "benign",
    },

    # --------------------------------------------------
    # FREQUENCY (FFT)
    # --------------------------------------------------

    "possible_decoder_grid_signature": {
        "label": "frequency structure suggests a grid-like or decoder-driven generation process",
        "short": "decoder grid signature",
        "polarity": "suspicious",
    },
    "fft_grid_detected": {
        "label": "strong grid-like frequency structure is detected",
        "short": "FFT grid detected",
        "polarity": "suspicious",
    },
    "structured_frequency_anomaly": {
        "label": "frequency analysis reveals structured anomaly patterns",
        "short": "frequency anomaly",
        "polarity": "suspicious",
    },
    "mild_structured_periodicity": {
        "label": "mild structured periodicity is present",
        "short": "mild periodicity",
        "polarity": "neutral",
    },

    # --------------------------------------------------
    # REGION FFT
    # --------------------------------------------------

    "boundary_band_frequency_mismatch": {
        "label": "frequency structure differs significantly at the subject boundary",
        "short": "boundary frequency mismatch",
        "polarity": "suspicious",
    },
    "subject_background_frequency_mismatch": {
        "label": "frequency structure differs between subject and background",
        "short": "subject/background frequency mismatch",
        "polarity": "suspicious",
    },
    "region_frequency_convergence_supported": {
        "label": "frequency characteristics are consistent across regions",
        "short": "region frequency consistent",
        "polarity": "benign",
    },

    # --------------------------------------------------
    # PATCH SPATIAL
    # --------------------------------------------------

    "subject_internal_synthetic_recurrence": {
        "label": "repeated patch structures are concentrated within the subject",
        "short": "subject-internal recurrence",
        "polarity": "suspicious",
    },
    "cross_region_patch_recurrence": {
        "label": "patch similarity spans subject, boundary, and background regions",
        "short": "cross-region recurrence",
        "polarity": "suspicious",
    },
    "boundary_correlated_patch_recurrence": {
        "label": "patch similarity is concentrated along the subject boundary",
        "short": "boundary-correlated recurrence",
        "polarity": "suspicious",
    },
    "subject_localized_patch_recurrence": {
        "label": "patch similarity is concentrated within the subject region",
        "short": "subject-local recurrence",
        "polarity": "suspicious",
    },
    "scene_wide_patch_recurrence": {
        "label": "patch similarity is distributed across the entire scene",
        "short": "scene-wide recurrence",
        "polarity": "neutral",
    },
    "patch_spatial_convergence_supported": {
        "label": "no meaningful spatial localization differences are detected",
        "short": "spatial consistent",
        "polarity": "benign",
    },
    "spatial_patch_recurrence_inconclusive": {
        "label": "spatial patch recurrence is present but not strongly localized",
        "short": "weak spatial recurrence",
        "polarity": "neutral",
    },

    # --------------------------------------------------
    # PATCH SIMILARITY
    # --------------------------------------------------

    "possible_clone_reuse": {
        "label": "highly similar regions suggest possible copy-move reuse",
        "short": "clone reuse",
        "polarity": "suspicious",
    },
    "possible_synthetic_texture_repetition": {
        "label": "repeated texture motifs suggest synthetic or generated content",
        "short": "synthetic texture repetition",
        "polarity": "suspicious",
    },
    "structured_patch_recurrence": {
        "label": "repeated structured patch motifs are present",
        "short": "structured patch repetition",
        "polarity": "suspicious",
    },
    "localized_repetition_detected": {
        "label": "localized repetition is detected but not clearly anomalous",
        "short": "localized repetition",
        "polarity": "neutral",
    },

    # --------------------------------------------------
    # SUBJECT TEXTURE
    # --------------------------------------------------

    "subject_internal_stochastic_repetition": {
        "label": "subject texture shows repeated stochastic patterns",
        "short": "stochastic repetition",
        "polarity": "suspicious",
    },
    "subject_texture_stochastic_regularization": {
        "label": "subject texture appears regularized and less naturally variable",
        "short": "texture regularization",
        "polarity": "suspicious",
    },
    "subject_texture_natural_variation_supported": {
        "label": "subject texture is consistent with natural variation",
        "short": "natural texture",
        "polarity": "benign",
    },

    # --------------------------------------------------
    # SUBJECT BOUNDARY
    # --------------------------------------------------

    "possible_subject_background_segmentation_artifact": {
        "label": "subject boundary suggests a segmentation or cutout artifact",
        "short": "segmentation artifact",
        "polarity": "suspicious",
    },
    "possible_boundary_transition_inconsistency": {
        "label": "transition between subject and background appears inconsistent",
        "short": "boundary inconsistency",
        "polarity": "suspicious",
    },

    # --------------------------------------------------
    # PROCESS ASYMMETRY
    # --------------------------------------------------

    "subject_process_asymmetry_strong": {
        "label": "strong processing differences exist between subject and background",
        "short": "strong asymmetry",
        "polarity": "suspicious",
    },
    "subject_surface_regularization_dominant": {
        "label": "subject surface shows dominant regularization effects",
        "short": "surface regularization",
        "polarity": "suspicious",
    },
    "subject_background_texture_asymmetry": {
        "label": "texture characteristics differ between subject and background",
        "short": "texture asymmetry",
        "polarity": "suspicious",
    },
    "subject_background_process_convergence_supported": {
        "label": "subject and background processing are consistent",
        "short": "process consistent",
        "polarity": "benign",
    },
    "subject_process_asymmetry_inconclusive": {
        "label": "subject/background processing differences are inconclusive",
        "short": "asymmetry inconclusive",
        "polarity": "neutral",
    },

    # --------------------------------------------------
    # MATERIAL REALISM
    # --------------------------------------------------

    "subject_material_realism_failure_strong": {
        "label": "subject material properties strongly deviate from natural behavior",
        "short": "material realism failure",
        "polarity": "suspicious",
    },
    "subject_material_regularization_dominant": {
        "label": "subject material appears overly regularized and lacks natural variability",
        "short": "material regularization",
        "polarity": "suspicious",
    },
    "subject_structure_without_stochasticity": {
        "label": "subject structure lacks natural stochastic variation",
        "short": "structure without noise",
        "polarity": "suspicious",
    },
    "subject_material_realism_supported": {
        "label": "subject material properties are consistent with natural appearance",
        "short": "material realistic",
        "polarity": "benign",
    },

    # --------------------------------------------------
    # COMPRESSION
    # --------------------------------------------------

    "single_history_jpeg_consistent": {
        "label": "compression history is consistent with a single save pipeline",
        "short": "single compression",
        "polarity": "benign",
    },
    "localized_compression_inconsistency": {
        "label": "compression artifacts vary across regions",
        "short": "compression inconsistency",
        "polarity": "suspicious",
    },
    "possible_double_jpeg_history": {
        "label": "image may have undergone multiple JPEG compressions",
        "short": "double JPEG",
        "polarity": "suspicious",
    },
    "block_grid_history_anomaly": {
        "label": "compression grid structure suggests prior processing",
        "short": "compression grid anomaly",
        "polarity": "suspicious",
    },
}