# metadata_evidence.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
"""Shared metadata semantics. Presence and declarations are not authentication."""

from enum import Enum

class ProvenanceState(str, Enum):
    VERIFIED_GENERATION_ASSERTION = "verified_generation_assertion"
    UNVERIFIED_GENERATION_DECLARATION = "unverified_generation_declaration"
    UNVERIFIED_ENHANCEMENT_DECLARATION = "unverified_enhancement_declaration"
    AMBIGUOUS_TOOL_OR_WORKFLOW_METADATA = "ambiguous_tool_or_workflow_metadata"
    PROVENANCE_PRESENT_UNVERIFIED = "provenance_present_unverified"
    NO_SUBSTANTIVE_PROVENANCE_EVIDENCE = "no_substantive_provenance_evidence"


GENERATION_PATTERNS = frozenset({
    "declared_synthetic_candidate", "embedded_generation_prompt_detected",
})
ENHANCEMENT_PATTERNS = frozenset({"declared_enhancement_candidate"})
MISSING_METADATA_PATTERNS = frozenset({
    "sparse_or_stripped", "metadata_stripped", "social_media_provenance",
})
GENERATION_SIGNAL_IDS = frozenset({"EMBEDDED_GENERATION_PROMPT", "DECLARED_SYNTHETIC"})
ENHANCEMENT_SIGNAL_IDS = frozenset({"DECLARED_ENHANCEMENT"})
AMBIGUOUS_SIGNAL_IDS = frozenset({
    "AI_TOOL_NAME_MATCH", "ENHANCEMENT_TOOL_NAME_MATCH", "AMBIGUOUS_WORKFLOW_METADATA",
    "GENERIC_EDITING_SOFTWARE_PRESENT",
})

# Exact controlled-vocabulary identifiers, not substring/tool-name matches.
# https://www.iptc.org/std/photometadata/documentation/userguide/
DIGITAL_SOURCE_TYPE_DECLARATIONS = {
    f"{scheme}://cv.iptc.org/newscodes/digitalsourcetype/{term}": signal_id
    for scheme in ("http", "https")
    for term, signal_id in (
        ("trainedAlgorithmicMedia", "DECLARED_SYNTHETIC"),
        ("compositeWithTrainedAlgorithmicMedia", "DECLARED_ENHANCEMENT"),
        ("compositeSynthetic", "DECLARED_ENHANCEMENT"),
    )
}


def classify_metadata_signals(signal_ids) -> dict:
    """Canonical classification for extractor payloads and summary adapters.

    No validator exists in this path. Even a payload claiming verification must
    not be promoted to verified provenance here.
    """
    ids = set(signal_ids)
    generation = bool(ids & GENERATION_SIGNAL_IDS)
    enhancement = bool(ids & ENHANCEMENT_SIGNAL_IDS)
    if generation:
        status = ("embedded_generation_prompt_detected" if "EMBEDDED_GENERATION_PROMPT" in ids
                  else "declared_synthetic_candidate")
        state = ProvenanceState.UNVERIFIED_GENERATION_DECLARATION
    elif enhancement:
        status = "declared_enhancement_candidate"
        state = ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION
    elif "C2PA_PRESENT" in ids:
        status = "provenance_present_unverified"
        state = ProvenanceState.PROVENANCE_PRESENT_UNVERIFIED
    elif ids & AMBIGUOUS_SIGNAL_IDS:
        status = "edited_or_processed_but_inconclusive"
        state = ProvenanceState.AMBIGUOUS_TOOL_OR_WORKFLOW_METADATA
    elif "CAMERA_METADATA_RICH" in ids:
        status = "camera_metadata_present"
        state = ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE
    elif "METADATA_STRIPPED_OR_SPARSE" in ids:
        status = "sparse_or_stripped"
        state = ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE
    else:
        status = "inconclusive"
        state = ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE
    return {
        "metadata_status": status,
        "provenance_state": state.value,
        "stripped": "METADATA_STRIPPED_OR_SPARSE" in ids,
        "declared_generation": generation,
        "declared_enhancement": enhancement,
        "provenance_present": "C2PA_PRESENT" in ids,
        "provenance_verified": False,
    }


def metadata_provenance_state(section) -> ProvenanceState:
    if section is None:
        return ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE
    details = section.details or {}
    ids = details.get("signal_ids")
    if ids:
        return ProvenanceState(classify_metadata_signals(ids)["provenance_state"])
    # Backward compatibility for older ModuleSummary objects without raw IDs.
    if section.pattern in GENERATION_PATTERNS:
        return ProvenanceState.UNVERIFIED_GENERATION_DECLARATION
    if section.pattern in ENHANCEMENT_PATTERNS:
        return ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION
    if section.pattern == "provenance_present_unverified":
        return ProvenanceState.PROVENANCE_PRESENT_UNVERIFIED
    if section.pattern == "edited_or_processed_but_inconclusive":
        return ProvenanceState.AMBIGUOUS_TOOL_OR_WORKFLOW_METADATA
    return ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE


def metadata_creation_context(section):
    """General declaration semantics; detailed graph topology remains optional."""
    details = (getattr(section, 'details', None) or {})
    workflow = details.get('workflow_interpretation') or {}
    state = metadata_provenance_state(section)
    if workflow.get('graph_interpretation_status') == 'coherent':
        kind, process = 'structured_workflow', workflow.get('declared_process')
    elif state == ProvenanceState.UNVERIFIED_GENERATION_DECLARATION:
        kind, process = 'explicit_generation_declaration', 'unspecified_generation_process'
    elif state == ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION:
        kind, process = 'explicit_processing_declaration', 'unspecified_enhancement_process'
    elif state == ProvenanceState.AMBIGUOUS_TOOL_OR_WORKFLOW_METADATA:
        kind, process = 'ambiguous_tool_or_workflow', None
    else:
        kind, process = 'unspecified', None
    return {'kind': kind, 'declared_process': process,
            'provenance_authenticity': 'unverified' if kind != 'unspecified' or state == ProvenanceState.PROVENANCE_PRESENT_UNVERIFIED else 'not_assessed',
            'workflow_interpretation': workflow or None}
