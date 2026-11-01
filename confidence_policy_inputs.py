# confidence_policy_inputs.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

"""Adapter from existing typed score/derived/gate data to immutable policy facts."""
from confidence_policy import ConfidenceFacts
from metadata_evidence import ProvenanceState


def coverage_limitations(coverage):
    if not coverage or coverage.get('status')!='partial':
        return ()
    return ('Analysis coverage is incomplete. Unavailable stages: '
        + ', '.join(coverage.get('unavailable_stages', []))
        + '. Missing regional evidence supports neither authenticity nor synthetic origin.',)


def snapshot_confidence_facts(sections, card, derived, gates, findings, *, coverage=()):
    gate_by_id={g['gate_id']:g for g in gates}
    generic=gate_by_id.get('confidence.strong_source_diversity',{})
    return ConfidenceFacts(
        valid=card.is_valid,
        findings=tuple((hypothesis,tuple(sorted(set(claims),key=lambda claim:claim.value)))
            for hypothesis,claims in sorted(findings.items())),
        suspicious=card.suspicious_score,local_support=card.local_edit_support_score,
        clone_support=card.clone_support_score,camera_support=card.camera_counter_support,
        synthetic_boost=card.synthetic_boost,
        person_reliable=derived.person_mask_reliable,boundary_reliability=derived.boundary_reliability_score,
        geometry_unreliable=derived.region_geometry_unreliable,context_risk=card.contextual_false_positive_risk,
        boundary_compound=bool(gate_by_id.get('boundary.compound_support',{}).get('gate_passed')),
        generic_source_diversity=bool(generic.get('requirement_satisfied')),
        generic_strong_count=generic.get('observed_strong_indicator_count',0),
        visual_global=bool(gate_by_id.get('synthetic.fft_patch_compound',{}).get('gate_passed')),
        visual_regional=bool(gate_by_id.get('synthetic.material_asymmetry_compound',{}).get('gate_passed')),
        camera_observed=bool(derived.camera_like_support or derived.cfa_camera_like_support or derived.metadata_camera_like),
        provenance=ProvenanceState(derived.provenance_state),osint_ai_context=derived.osint_ai_context,
        missing_detectors=tuple(sorted(key for key in (
            'metadata','region_masks','boundary_focus','segmentation_alignment','subject_boundary','patch_spatial',
            'sensor_origin','cfa_demosaic','fft','patch_similarity','subject_material_realism','subject_process_asymmetry',
        ) if (section:=sections.get(key)) is None or section.status in {'not_run','unavailable','skipped','failed','error'})),
        # No cryptographic validator exists in this production path. Metadata
        # flags or a supplied JSON "verified" state are never a validator result.
        verification=None,
        coverage_limitations=tuple(coverage),
    )
