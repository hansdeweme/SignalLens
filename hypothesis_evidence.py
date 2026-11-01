"""Explicit evidence relationships for reporting; never changes scores or tiers."""
# hypothesis_evidence.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#


from dataclasses import dataclass
from typing import Literal

from gui_semantics import ModuleSummary
from hypothesis_engine import HypothesisAssessment
from metadata_evidence import (
    GENERATION_PATTERNS, ENHANCEMENT_PATTERNS, MISSING_METADATA_PATTERNS,
    GENERATION_SIGNAL_IDS, ENHANCEMENT_SIGNAL_IDS,
)
from signal_language import humanize_signal
from scorecard_integrity import usable_observation

Role = Literal["supporting_evidence", "contradicting_evidence", "moderating_evidence", "contextual_evidence"]
ROLE_TITLES = {
    "supporting_evidence": "Supporting Signals",
    "contradicting_evidence": "Contradicting Signals",
    "moderating_evidence": "Moderating Signals",
    "contextual_evidence": "Contextual Signals",
}
EVIDENCE_LABELS = {
    "declared_synthetic_candidate": "explicit generation declaration in metadata",
    "declared_enhancement_candidate": "explicit enhancement declaration in metadata",
    "embedded_generation_prompt_detected": "embedded generation prompt or workflow",
    "creator_identity_present": "creator attribution metadata",
}


@dataclass(frozen=True)
class EvidenceUse:
    hypothesis: str
    role: Role
    interpretation: str
    requires: Literal["visual_generation", "spatial_reuse", "boundary_mechanism"] | None = None
    fallback: str | None = None


# Each family lists exact section/pattern pairs. A section's polarity alone is
# never enough to infer which hypothesis it supports or challenges.
BOUNDARY_ANOMALIES = {
    "boundary": ("possible_foreground_background_processing_mismatch", "possible_boundary_fragment_convergence"),
    "boundary_focus": ("boundary_focused_transition_anomaly", "boundary_focused_processing_mismatch"),
    "subject_boundary": ("possible_subject_background_segmentation_artifact", "possible_boundary_transition_inconsistency"),
    "segmentation_alignment": ("segmentation_boundary_alignment",),
    "cross_signal": ("strong_hotspot_convergence", "partial_hotspot_convergence"),
    "region_fft": ("boundary_band_frequency_mismatch", "subject_background_frequency_mismatch"),
    "sensor_origin": ("localized_sensor_trace_inconsistency",),
    "cfa_demosaic": ("localized_cfa_inconsistency",),
    "compression_history": ("localized_compression_inconsistency",),
}
SPATIAL_REUSE = (
    "cross_region_patch_recurrence", "boundary_correlated_patch_recurrence",
    "subject_localized_patch_recurrence", "subject_internal_patch_recurrence",
)
GENERATION_STRUCTURE = {
    "fft": ("possible_decoder_grid_signature", "fft_grid_detected", "structured_frequency_anomaly"),
    "patch_similarity": ("possible_synthetic_texture_repetition", "structured_patch_recurrence"),
    "patch_spatial": ("subject_internal_synthetic_recurrence",),
    "subject_texture_consistency": ("subject_internal_stochastic_repetition", "subject_texture_stochastic_regularization"),
    "subject_material_realism": (
        "subject_material_realism_failure_strong", "subject_material_realism_failure",
        "subject_material_regularization_dominant", "subject_structure_without_stochasticity",
    ),
    "subject_process_asymmetry": (
        "subject_process_asymmetry_strong", "subject_surface_regularization_dominant",
        "subject_background_texture_asymmetry",
    ),
}
CAMERA_SUPPORT = {
    "sensor_origin": ("camera_like_acquisition_supported", "weak_camera_pipeline_supported"),
    "cfa_demosaic": ("camera_like_cfa_supported", "weak_camera_cfa_supported"),
}

def _rules() -> dict[tuple[str, str], tuple[EvidenceUse, ...]]:
    rules = {}
    for section, patterns in BOUNDARY_ANOMALIES.items():
        for pattern in patterns:
            rules[section, pattern] = (
                EvidenceUse("localized_editing", "supporting_evidence",
                            "A regional processing anomaly supports localized-processing concern; it does not identify AI use."),
            )
    for pattern in SPATIAL_REUSE:
        rules["patch_spatial", pattern] = (
            EvidenceUse("localized_editing", "supporting_evidence",
                        "Spatially localized patch recurrence supports regional reuse or differential processing; generation is not established."),
        )
    rules["patch_similarity", "possible_clone_reuse"] = (
        EvidenceUse("localized_editing", "supporting_evidence",
                    "Similar separated regions with spatial corroboration support possible local duplication, not synthetic origin.",
                    "spatial_reuse", "Similar regions were detected, but spatial corroboration is insufficient to establish copy-move reuse."),
    )
    for section, patterns in GENERATION_STRUCTURE.items():
        for pattern in patterns:
            uses = [EvidenceUse(
                "synthetic_origin", "supporting_evidence",
                "This structural observation contributes to the supported visual synthetic-structure finding; it is not proof of generation.",
                "visual_generation", "Structural regularity is present but nonspecific; it does not independently establish synthetic origin.",
            )]
            if section in {"subject_process_asymmetry", "subject_texture_consistency", "subject_material_realism"}:
                uses.append(EvidenceUse("localized_editing", "contextual_evidence",
                                        "Subject structure or processing differs, but this observation does not establish a compositing or copy-move mechanism."))
            rules[section, pattern] = tuple(uses)
    for section, patterns in CAMERA_SUPPORT.items():
        for pattern in patterns:
            rules[section, pattern] = (
                EvidenceUse("camera_acquisition", "supporting_evidence",
                            "Measured structure is compatible with camera acquisition; it does not authenticate the image."),
                EvidenceUse("synthetic_origin", "moderating_evidence",
                            "Camera-compatible structure may coexist with synthetic creation or editing; it does not refute a generation declaration."),
                EvidenceUse("localized_editing", "moderating_evidence",
                            "Camera-compatible structure may describe the base image and does not rule out later localized editing."),
            )
    rules["boundary_focus", "boundary_processing_convergence_supported"] = (
        EvidenceUse("localized_editing", "contradicting_evidence",
                    "The measured boundary band is consistent with surrounding regions, weakening a boundary-mismatch mechanism without excluding other edits.",
                    "boundary_mechanism", "Boundary-band processing appears consistent; no specific boundary-mismatch mechanism is selected."),
    )
    for section, pattern in (
        ("subject_process_asymmetry", "subject_background_process_convergence_supported"),
        ("region_fft", "region_frequency_convergence_supported"),
        ("patch_spatial", "patch_spatial_convergence_supported"),
        ("compression_history", "single_history_jpeg_consistent"),
    ):
        rules[section, pattern] = (
            EvidenceUse("localized_editing", "moderating_evidence",
                        "This check shows processing consistency; it limits the corresponding concern but cannot exclude all localized edits."),
        )
    for section, pattern in (
        ("sensor_origin", "localized_sensor_trace_inconsistency"),
        ("cfa_demosaic", "localized_cfa_inconsistency"),
    ):
        rules[section, pattern] += (
            EvidenceUse("camera_acquisition", "moderating_evidence",
                        "Regional pipeline inconsistency limits a uniform acquisition interpretation, but can coexist with a camera-origin base image."),
        )
    rules["osint", "ai_gallery"] = (
        EvidenceUse("synthetic_origin", "supporting_evidence",
                    "An AI-gallery source supplies contextual support for synthetic origin without authenticating this image's history."),
    )
    rules["subject_boundary", "image_edge_boundary_observation"] = (
        EvidenceUse("localized_editing", "contextual_evidence",
                    "Image-edge measurements lack validated person alignment and cannot establish person-specific segmentation artifacts."),
    )
    return rules


EVIDENCE_RELATIONSHIPS = _rules()

def scope_hypothesis_evidence(
    sections: dict[str, ModuleSummary], assessments: list[HypothesisAssessment], *,
    visual_generation: bool, boundary_mechanism: bool,
) -> None:
    """Populate authoritative evidence records without changing assessments' tiers."""
    by_id = {a.hypothesis_id: a for a in assessments}
    for assessment in assessments:
        for role in ROLE_TITLES:
            getattr(assessment, role).clear()
        assessment.evidence_details.clear()

    spatial = sections.get("patch_spatial")
    gates = {
        "visual_generation": visual_generation,
        "boundary_mechanism": boundary_mechanism,
        "spatial_reuse": bool(spatial and spatial.pattern in SPATIAL_REUSE
                              and spatial.polarity == "suspicious"
                              and spatial.status not in {"not_run", "inconclusive"}),
    }

    def add(hypothesis, role, evidence_id, section_key, pattern, interpretation, observations=None):
        assessment = by_id.get(hypothesis)
        if assessment is None:
            return
        if evidence_id not in getattr(assessment, role):
            getattr(assessment, role).append(evidence_id)
        assessment.evidence_details[evidence_id] = {
            "section": section_key, "pattern": pattern, "role": role,
            "interpretation": interpretation, "observations": observations or [],
            "label": EVIDENCE_LABELS.get(pattern, humanize_signal(pattern)),
            "observed_status": sections[section_key].status,
            "observed_score": sections[section_key].score,
        }

    for section_key, section in sorted(sections.items()):
        if not usable_observation(section):
            continue
        for use in EVIDENCE_RELATIONSHIPS.get((section_key, section.pattern), ()):
            role, interpretation = use.role, use.interpretation
            # The family identifies relevance; observed polarity identifies
            # whether the measurement actually reported an anomaly/compatibility.
            expected = "benign" if section_key in CAMERA_SUPPORT and section.pattern in CAMERA_SUPPORT[section_key] else None
            if role == "supporting_evidence" and section.polarity != (expected or "suspicious"):
                continue
            if use.requires and not gates[use.requires]:
                role, interpretation = "contextual_evidence", use.fallback
            add(use.hypothesis, role, f"{section_key}:{section.pattern}", section_key,
                section.pattern, interpretation)

    metadata = sections.get("metadata")
    if metadata and (usable_observation(metadata) or metadata.status == "inconclusive"):
        metadata_active = usable_observation(metadata)
        details = metadata.details or {}
        signals = {s["id"]: s for s in details.get("metadata_signals", []) if isinstance(s, dict) and s.get("id")}
        ids = set(details.get("signal_ids", []))
        if not ids:
            ids = {metadata.pattern}
        for signal_id in sorted(ids):
            observations = signals.get(signal_id, {}).get("evidence", [])
            if metadata_active and (signal_id in GENERATION_SIGNAL_IDS or signal_id in GENERATION_PATTERNS):
                pattern = ("embedded_generation_prompt_detected" if signal_id in {"EMBEDDED_GENERATION_PROMPT", "embedded_generation_prompt_detected"}
                           else "declared_synthetic_candidate")
                add("synthetic_origin", "supporting_evidence", f"metadata:{signal_id}", "metadata", pattern,
                    "Embedded metadata explicitly declares generation; metadata authenticity remains unverified.", observations)
                add("localized_editing", "contextual_evidence", f"metadata:{signal_id}", "metadata", pattern,
                    "A generation declaration does not identify a localized editing mechanism.", observations)
                add("camera_acquisition", "contextual_evidence", f"metadata:{signal_id}", "metadata", pattern,
                    "A generation declaration can coexist with camera-compatible structure; it does not authenticate acquisition history.", observations)
            elif metadata_active and (signal_id in ENHANCEMENT_SIGNAL_IDS or signal_id in ENHANCEMENT_PATTERNS):
                add("synthetic_origin", "supporting_evidence", f"metadata:{signal_id}", "metadata", "declared_enhancement_candidate",
                    "Metadata declares enhancement or generative editing; authenticity is unverified and whole-image generation is not established.", observations)
                add("localized_editing", "contextual_evidence", f"metadata:{signal_id}", "metadata", "declared_enhancement_candidate",
                    "An enhancement declaration does not establish where or how a localized edit occurred.", observations)
            elif signal_id in {"CREATOR_IDENTITY_PRESENT", "C2PA_PRESENT", "AI_TOOL_NAME_MATCH", "ENHANCEMENT_TOOL_NAME_MATCH", "AMBIGUOUS_WORKFLOW_METADATA", "GENERIC_EDITING_SOFTWARE_PRESENT", "provenance_present_unverified", "edited_or_processed_but_inconclusive"}:
                context_patterns = {
                    "CREATOR_IDENTITY_PRESENT": "creator_identity_present",
                    "C2PA_PRESENT": "provenance_present_unverified",
                    "AI_TOOL_NAME_MATCH": "ambiguous_generation_tool_metadata",
                    "ENHANCEMENT_TOOL_NAME_MATCH": "ambiguous_enhancement_tool_metadata",
                    "AMBIGUOUS_WORKFLOW_METADATA": "ambiguous_workflow_metadata",
                    "GENERIC_EDITING_SOFTWARE_PRESENT": "edited_or_processed_but_inconclusive",
                }
                interpretations = {
                    "CREATOR_IDENTITY_PRESENT": "Creator attribution is present but does not declare generation.",
                    "C2PA_PRESENT": "Potential C2PA metadata is present; no cryptographic validation has been performed.",
                    "provenance_present_unverified": "Potential provenance metadata is present; no cryptographic validation has been performed.",
                }
                add("synthetic_origin", "contextual_evidence", f"metadata:{signal_id}", "metadata", context_patterns.get(signal_id, signal_id),
                    interpretations.get(signal_id, "Tool or workflow metadata is ambiguous and does not establish generation."), observations)
        if metadata.pattern in MISSING_METADATA_PATTERNS:
            for hypothesis in ("synthetic_origin", "camera_acquisition"):
                add(hypothesis, "contextual_evidence", f"metadata:{metadata.pattern}", "metadata", metadata.pattern,
                    "Missing provenance coverage limits assessment and supports neither synthetic nor photographic origin.",
                    signals.get("METADATA_STRIPPED_OR_SPARSE", {}).get("evidence", []))
        if metadata_active and (metadata.pattern == "camera_metadata_present" or details.get("camera_metadata_present")):
            observations = signals.get("CAMERA_METADATA_RICH", {}).get("evidence", [])
            for hypothesis, role, interpretation in (
                ("camera_acquisition", "supporting_evidence", "Camera metadata is compatible with acquisition, but its authenticity is unverified."),
                ("synthetic_origin", "moderating_evidence", "Camera metadata may describe a base image and does not refute a generation declaration."),
                ("localized_editing", "moderating_evidence", "Camera metadata does not exclude edits after acquisition."),
            ):
                add(hypothesis, role, "metadata:camera_metadata_present", "metadata", "camera_metadata_present", interpretation, observations)

    # Unknown anomalies remain visible as anomalies, never an invented mechanism.
    unresolved = by_id.get("unresolved_anomaly")
    if unresolved:
        for key, section in sorted(sections.items()):
            if usable_observation(section) and section.polarity == "suspicious" and section.pattern not in MISSING_METADATA_PATTERNS:
                add("unresolved_anomaly", "supporting_evidence", f"{key}:{section.pattern}", key, section.pattern,
                    "An anomalous observation is present; its cause is unresolved and it does not establish generation or a specific edit.")
    for assessment in assessments:
        for role in ROLE_TITLES:
            getattr(assessment, role).sort()

def evidence_presentation(assessment: HypothesisAssessment | dict | None) -> dict:
    """Shared projection for JSON, GUI narrative and text reports."""
    data = assessment if isinstance(assessment, dict) else vars(assessment) if assessment else {}
    details = data.get("evidence_details", {})
    result = {}
    for role in ROLE_TITLES:
        ids = list(data.get(role, []))
        patterns = [details.get(eid, {}).get("pattern", eid.partition(":")[2] or eid) for eid in ids]
        result[role] = ids
        result[role.replace("_evidence", "_signals")] = list(dict.fromkeys(patterns))
        result[role.replace("_evidence", "_explanations")] = [
            f"{details[eid].get('label', humanize_signal(pattern))}: {details[eid]['interpretation']}" if eid in details
            else humanize_signal(pattern) for eid, pattern in zip(ids, patterns)
        ]
    result["limitations"] = list(data.get("limitations", []))
    result["evidence_details"] = details
    return result

def append_hypothesis_evidence(text: str, assessment: HypothesisAssessment) -> str:
    presentation = evidence_presentation(assessment)
    for role, title in ROLE_TITLES.items():
        items = presentation[role.replace("_evidence", "_explanations")]
        if items:
            text = text.rstrip() + f"\n{title}:\n" + "\n".join(f"- {item}" for item in items) + "\n"
    return text
