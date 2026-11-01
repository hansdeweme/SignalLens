#hypothesis_engine.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from dataclasses import dataclass, field, replace
from math import fsum
from typing import Optional
# local imports to avoid circular dependencies
from gui_semantics import ModuleSummary
from numerical_evidence import allocate_base_evidence, add_fragment_component, finalize_component_allocations
from metadata_evidence import (
    ProvenanceState, MISSING_METADATA_PATTERNS, metadata_provenance_state,
)
from scorecard_integrity import (
    STATUS_WEIGHTS, COMPONENT_FIELDS, BOOST_FIELDS, ComponentLedger,
    available_sections, usable_observation, validate_score_inputs,
    validate_derived_signals, validate_scorecard,
    camera_attenuation,
    ScorecardIntegrityError,
    validate_score_context,
)

STATUS_WEIGHT = STATUS_WEIGHTS

@dataclass
class HypothesisContext:
    natural_repetition: bool = False
    decorative_geometric: bool = False
    smartphone_computational: bool = False
    screen_origin: bool = False

@dataclass
class EvidenceSnapshot:
    metadata: ModuleSummary | None = None
    osint: ModuleSummary | None = None
    ela: ModuleSummary | None = None
    noise: ModuleSummary | None = None
    sensor_origin: ModuleSummary | None = None
    cfa_demosaic: ModuleSummary | None = None
    region_masks: ModuleSummary | None = None
    region_segmentation: ModuleSummary | None = None
    segmentation_alignment: ModuleSummary | None = None
    compression_history: ModuleSummary | None = None
    patch_similarity: ModuleSummary | None = None
    patch_spatial: ModuleSummary | None = None
    cross_signal: ModuleSummary | None = None
    boundary: ModuleSummary | None = None
    subject_texture_consistency: ModuleSummary | None = None
    subject_boundary: ModuleSummary | None = None
    subject_process_asymmetry: ModuleSummary | None = None
    subject_material_realism: ModuleSummary | None = None
    fft: ModuleSummary | None = None
    
@dataclass
class DerivedSignals:
    camera_like_support: bool = False
    sensor_trace_inconsistency: bool = False
    cfa_camera_like_support: bool = False
    cfa_inconsistency: bool = False    
    compression_consistent: bool = False
    compression_inconsistency: bool = False
    double_jpeg_suspect: bool = False
    block_history_anomaly: bool = False
    subject_boundary_strong: bool = False
    subject_boundary_medium: bool = False
    subject_texture_strong: bool = False
    subject_texture_moderate: bool = False    
    subject_process_asymmetry_moderate: bool = False
    subject_process_asymmetry_strong: bool = False
    material_realism_strong: bool = False
    material_realism_medium: bool = False
    material_realism_weak: bool = False
    material_realism_low: bool = False        
    metadata_synthetic: bool = False
    metadata_enhancement: bool = False
    metadata_missing: bool = False
    provenance_state: str = ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE.value
    metadata_clean: bool = True
    metadata_camera_like: bool = False
    osint_ai_context: bool = False
    osint_clean: bool = True
    provenance_clean: bool = True
    strong_local_edit: bool = False
    fragmented_local_edit: bool = False
    strong_cross: bool = False
    local_signals_weak: bool = False
    fft_structured: bool = False
    patch_structured: bool = False
    segmentation_fragmented: bool = False
    segmentation_clean: bool = False
    segmentation_natural: bool = False
    segmentation_boundary_strong: bool = False
    segmentation_boundary_medium: bool = False
    segmentation_boundary_score: float = 0.0
    fft_score: float = 0.0
    peak_periodicity: float = 0.0
    peak_symmetry: float = 0.0
    peak_count: int = 0
    axis_bias: float = 0.0
    patch_score: float = 0.0
    repetition_score: float = 0.0
    coverage_ratio: float = 0.0
    pair_count: int = 0
    separated_pair_count: int = 0
    mean_similarity: float = 0.0
    max_similarity: float = 0.0
    region_geometry_unreliable: bool = False
    person_mask_reliable: bool = False
    subject_area_ratio: float = 0.0
    boundary_support_ratio: float = 0.0
    boundary_support_low: bool = False
    boundary_reliability_score: float = 1.0    
    
@dataclass
class ScoreCard:
    camera_counter_support: float = 0.0
    suspicious_score: float = 0.0
    benign_score: float = 0.0
    local_edit_support_score: float = 0.0
    clone_support_score: float = 0.0
    synthetic_boost: float = 0.0
    edit_boost: float = 0.0
    provenance_boost: float = 0.0
    sensor_boost: float = 0.0
    compression_boost: float = 0.0
    caution_penalty: float = 0.0
    clone_candidate: bool = False
    clone_ambiguous: bool = False
    contextual_false_positive_risk: bool = False
    synthetic_supported_by_other_domains: bool = False
    suspicious_domains: set[str] = field(default_factory=set)
    benign_domains: set[str] = field(default_factory=set)
    is_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)
    calculation: dict = field(default_factory=dict, repr=False, metadata={"trace_exclude": True})


@dataclass
class HypothesisAssessment:
    hypothesis_id: str
    polarity: str = "neutral"
    confidence_tier: str = "Inconclusive"
    supporting_evidence: list[str] = field(default_factory=list)
    moderating_evidence: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    decision_branch: str | None = None
    explanation: str = "No substantive support established for this hypothesis."
    contradicting_evidence: list[str] = field(default_factory=list)
    contextual_evidence: list[str] = field(default_factory=list)
    evidence_details: dict[str, dict] = field(default_factory=dict)
    confidence_policy_rule: str | None = None
    confidence_rationale: list[str] = field(default_factory=list)

def weight(section: ModuleSummary | None) -> float:
    if section is None:
        return 0.0
    return STATUS_WEIGHT.get(section.status, 0.0)

def is_suspicious(section: ModuleSummary | None) -> bool:
    return (section is not None and section.pattern not in MISSING_METADATA_PATTERNS
            and section.polarity == "suspicious" and weight(section) > 0)

def is_benign(section: ModuleSummary | None) -> bool:
    return (section is not None and section.pattern not in MISSING_METADATA_PATTERNS
            and section.polarity == "benign" and weight(section) > 0)

def detail(section: ModuleSummary | None, key: str, default=0):
    if not usable_observation(section) or not getattr(section, "details", None):
        return default
    value = section.details.get(key, default)
    return default if value is None else value

def build_context(scene_context: dict | None) -> HypothesisContext:
    scene_context = scene_context or {}
    return HypothesisContext(
        natural_repetition=scene_context.get("natural_repetition", False),
        decorative_geometric=scene_context.get("decorative_geometric", False),
        smartphone_computational=scene_context.get("smartphone_computational", False),
        screen_origin=scene_context.get("screen_origin", False),
    )

def build_evidence_snapshot(sections: dict[str, ModuleSummary]) -> EvidenceSnapshot:
    sections = available_sections(sections)
    return EvidenceSnapshot(
        metadata=sections.get("metadata"),
        osint=sections.get("osint"),
        ela=sections.get("ela"),
        noise=sections.get("noise"),
        sensor_origin=sections.get("sensor_origin"),
        region_masks=sections.get("region_masks"),
        region_segmentation=sections.get("region_masks"),
        segmentation_alignment=sections.get("segmentation_alignment"),
        cfa_demosaic=sections.get("cfa_demosaic"),
        compression_history=sections.get("compression_history"),
        patch_similarity=sections.get("patch_similarity"),
        patch_spatial=sections.get("patch_spatial"),
        cross_signal=sections.get("cross_signal"),
        boundary=sections.get("boundary"),
        subject_boundary=sections.get("subject_boundary"),
        subject_texture_consistency=sections.get("subject_texture_consistency"),
        subject_process_asymmetry=sections.get("subject_process_asymmetry"),
        subject_material_realism=sections.get("subject_material_realism"),
        fft=sections.get("fft"),        
    )

def derive_signals(ev: EvidenceSnapshot) -> DerivedSignals:
    ev = replace(ev, **{key: value if usable_observation(value) else None for key, value in vars(ev).items()})
    validate_score_inputs(vars(ev))
    d = DerivedSignals()
    d.camera_like_support = (ev.sensor_origin is not None and ev.sensor_origin.pattern == "camera_like_acquisition_supported")
    d.cfa_camera_like_support = (ev.cfa_demosaic is not None and ev.cfa_demosaic.pattern == "camera_like_cfa_supported")
    d.sensor_trace_inconsistency = (ev.sensor_origin is not None and ev.sensor_origin.pattern == "localized_sensor_trace_inconsistency")
    d.cfa_inconsistency = (ev.cfa_demosaic is not None and ev.cfa_demosaic.pattern == "localized_cfa_inconsistency")      
    d.compression_consistent = (ev.compression_history is not None and ev.compression_history.pattern == "single_history_jpeg_consistent")
    d.compression_inconsistency = (ev.compression_history is not None and ev.compression_history.pattern == "localized_compression_inconsistency")
    d.double_jpeg_suspect = (ev.compression_history is not None and ev.compression_history.pattern == "possible_double_jpeg_history")
    d.block_history_anomaly = (ev.compression_history is not None and ev.compression_history.pattern == "block_grid_history_anomaly")
    d.subject_boundary_strong = (ev.subject_boundary is not None and ev.subject_boundary.pattern == "possible_subject_background_segmentation_artifact")
    d.subject_boundary_medium = (ev.subject_boundary is not None and ev.subject_boundary.pattern == "possible_boundary_transition_inconsistency")    
    d.subject_texture_strong = (ev.subject_texture_consistency is not None and ev.subject_texture_consistency.pattern == "subject_internal_stochastic_repetition")
    d.subject_texture_moderate = (ev.subject_texture_consistency is not None and ev.subject_texture_consistency.pattern == "subject_texture_stochastic_regularization")    
    d.subject_process_asymmetry_strong = (ev.subject_process_asymmetry is not None and ev.subject_process_asymmetry.pattern == "subject_process_asymmetry_strong")
    d.subject_process_asymmetry_moderate = (ev.subject_process_asymmetry is not None and ev.subject_process_asymmetry.pattern in {
            "subject_surface_regularization_dominant", "subject_background_texture_asymmetry", } )   
    seg = ev.region_segmentation
    d.segmentation_fragmented = (seg is not None and seg.pattern == "fragmented_subject_mask")
    d.segmentation_clean = (seg is not None and seg.pattern == "unnaturally_clean_segmentation")
    d.segmentation_natural = (seg is not None and seg.polarity == "benign")
    # --- segmentation alignment ---
    seg_align = ev.segmentation_alignment
    seg_score = 0.0
    if seg_align is not None and seg_align.score is not None:
        seg_score = float(seg_align.score)
    d.segmentation_boundary_score = seg_score
    d.segmentation_boundary_strong = seg_score >= 0.55
    d.segmentation_boundary_medium = 0.35 <= seg_score < 0.55   
    # --------------------------------------------------
    # Subject material realism
    # --------------------------------------------------
    mat = ev.subject_material_realism
    mat_score = mat.score if mat and mat.score is not None else 0.0
    d.material_realism_strong = mat_score >= 0.58
    d.material_realism_medium = 0.44 <= mat_score < 0.58
    d.material_realism_weak = 0.30 <= mat_score < 0.44
    d.material_realism_low = bool(
        mat is not None and mat.score is not None
        and mat.status not in {"not_run", "inconclusive"} and mat_score <= 0.20
    )
    d.fft_score = detail(ev.fft, "fft_anomaly_score", 0.0)
    d.peak_periodicity = detail(ev.fft, "peak_periodicity_score", 0.0)
    d.peak_symmetry = detail(ev.fft, "peak_symmetry_score", 0.0)
    d.peak_count = detail(ev.fft, "peak_count", 0)
    d.axis_bias = detail(ev.fft, "axis_bias_score", 0.0)
    d.patch_score = ev.patch_similarity.score or 0.0 if ev.patch_similarity else 0.0
    d.repetition_score = detail(ev.patch_similarity, "repetition_score", 0.0)
    d.coverage_ratio = detail(ev.patch_similarity, "coverage_ratio", 0.0)
    d.pair_count = detail(ev.patch_similarity, "pair_count", 0)
    d.separated_pair_count = detail(ev.patch_similarity, "spatially_separated_pair_count", 0)
    d.mean_similarity = detail(ev.patch_similarity, "mean_similarity", 0.0)
    d.max_similarity = detail(ev.patch_similarity, "max_similarity", 0.0)
    state = metadata_provenance_state(ev.metadata)
    d.provenance_state = state.value
    d.metadata_synthetic = state == ProvenanceState.UNVERIFIED_GENERATION_DECLARATION
    d.metadata_enhancement = state == ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION
    d.metadata_missing = ev.metadata is not None and ev.metadata.pattern in MISSING_METADATA_PATTERNS
    d.metadata_clean = not (d.metadata_synthetic or d.metadata_enhancement)
    d.metadata_camera_like = bool(ev.metadata and (
        ev.metadata.pattern == "camera_metadata_present"
        or detail(ev.metadata, "camera_metadata_present", False)
    ))
    d.osint_ai_context = ev.osint is not None and ev.osint.pattern == "ai_gallery"
    d.osint_clean = ev.osint is None or ev.osint.pattern not in {"ai_gallery"}
    d.provenance_clean = d.metadata_clean and d.osint_clean
    d.strong_local_edit = (ev.boundary is not None and ev.boundary.pattern == "possible_foreground_background_processing_mismatch")
    d.fragmented_local_edit = (ev.boundary is not None and ev.boundary.pattern == "possible_boundary_fragment_convergence")
    d.strong_cross = (ev.cross_signal is not None and ev.cross_signal.pattern == "strong_hotspot_convergence")
    d.local_signals_weak = (
        (ev.ela is None or ev.ela.status in {"not_run", "inconclusive", "weak"})
        and (ev.noise is None or ev.noise.status in {"not_run", "inconclusive", "weak"})
        and (ev.cross_signal is None or ev.cross_signal.status in {"not_run", "inconclusive", "weak"})
        and not d.strong_local_edit
    )    
    d.fft_structured = ev.fft is not None and ev.fft.pattern in {"possible_decoder_grid_signature", "fft_grid_detected", "structured_frequency_anomaly",}
    d.patch_structured = ev.patch_similarity is not None and ev.patch_similarity.pattern in {"possible_synthetic_texture_repetition", "structured_patch_recurrence",}
    spa = ev.subject_process_asymmetry
    d.region_geometry_unreliable = bool(
        spa and spa.details and spa.details.get("region_geometry_unreliable", False)
    )    
    region = ev.region_segmentation
    region_details = getattr(region, "details", {}) or {}
    d.subject_area_ratio = float(region_details.get("subject_ratio") or 0.0)
    d.boundary_support_ratio = float(region_details.get("boundary_ratio") or 0.0)
    source = region_details.get("source")
    reliability = region_details.get("person_mask_reliability")
    d.person_mask_reliable = (source == "person_subject_mask" and reliability in {"high", "medium"})        
    d.boundary_support_low = d.boundary_support_ratio < 0.015
    if not d.person_mask_reliable:
        d.boundary_reliability_score = 0.0
    elif d.boundary_support_ratio < 0.005:
        d.boundary_reliability_score = 0.25
    elif d.boundary_support_ratio < 0.015:
        d.boundary_reliability_score = 0.50
    elif d.boundary_support_ratio < 0.03:
        d.boundary_reliability_score = 0.75
    else:
        d.boundary_reliability_score = 1.0    
    # print("[DEBUG] ev.region_segmentation:", ev.region_segmentation)        
    return d

def compute_base_scores(sections: dict[str, ModuleSummary], ) -> tuple[float, float, set[str], set[str]]:
    validate_score_inputs(sections)
    _, audit = _allocate_base_scores(sections)
    return _base_totals(audit)


def _allocate_base_scores(sections):
    rows = [
        {"section": key, "status": section.status, "polarity": section.polarity,
         "domain": section.domain, "weight": weight(section)}
        for key, section in sorted(sections.items()) if is_suspicious(section) or is_benign(section)
    ]
    return allocate_base_evidence(sections, rows)


def _base_totals(audit):
    totals = audit['aggregate_reconciliation']
    return (
        totals['suspicious']['credited_base_weight'] + totals['suspicious']['credited_domain_bonus'],
        totals['benign']['credited_base_weight'] + totals['benign']['credited_domain_bonus'],
        set(totals['suspicious']['credited_domains']), set(totals['benign']['credited_domains']),
    )

def compute_scorecard(sections: dict[str, ModuleSummary], ctx: HypothesisContext, ev: EvidenceSnapshot, ds: DerivedSignals,) -> ScoreCard:
    validate_score_inputs(sections)
    validate_derived_signals(ds)
    validate_score_context(ctx)
    ev = replace(ev, **{key: value if usable_observation(value) else None for key, value in vars(ev).items()})
    expected_signals = derive_signals(ev)
    mismatched = [name for name, value in vars(expected_signals).items() if getattr(ds, name) != value]
    if mismatched:
        raise ScorecardIntegrityError("Derived signals do not match available evidence: " + ", ".join(mismatched))
    card = ScoreCard()
    ledger = ComponentLedger(card)
    # --------------------------------------------------
    # Base scores from section status/polarity
    # --------------------------------------------------
    base_evidence, numerical_audit = _allocate_base_scores(sections)
    (
        card.suspicious_score,
        card.benign_score,
        card.suspicious_domains,
        card.benign_domains,
    ) = _base_totals(numerical_audit)
    base_suspicious, base_benign = card.suspicious_score, card.benign_score
    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    asym_strong = bool(getattr(ds, "subject_process_asymmetry_strong", False))
    asym_medium = bool(ds.subject_process_asymmetry_moderate)
    boundary_strong = bool(ds.subject_boundary_strong or ds.segmentation_boundary_strong)
    boundary_medium = bool(ds.subject_boundary_medium or ds.segmentation_boundary_medium)
        
    # --------------------------------------------------
    # 1. Camera / benign counter-support
    # --------------------------------------------------
    if ds.metadata_camera_like:
        ledger.add('camera_counter_support', 1.50, 'ds.metadata_camera_like')
    if ds.camera_like_support:
        ledger.add('camera_counter_support', 1.25, 'ds.camera_like_support')
    if ds.cfa_camera_like_support:
        ledger.add('camera_counter_support', 1.00, 'ds.cfa_camera_like_support')
    # Reward convergence of multiple camera-like signals
    if card.camera_counter_support >= 2.0:
        ledger.add('camera_counter_support', 0.50, 'card.camera_counter_support >= 2.0')
    # Additional benign moderation
    if ds.segmentation_natural and ds.camera_like_support:
        ledger.add('caution_penalty', 0.40, 'ds.segmentation_natural and ds.camera_like_support')
    if ds.material_realism_low and ds.provenance_clean:
        ledger.add('caution_penalty', 0.60, 'ds.material_realism_low and ds.provenance_clean')
    if ds.compression_consistent and ds.provenance_clean and ds.local_signals_weak:
        ledger.add('caution_penalty', 0.40, 'ds.compression_consistent and ds.provenance_clean and ds.local_signals_weak')
    if ds.camera_like_support and ds.provenance_clean:
        ledger.add('caution_penalty', 0.35, 'ds.camera_like_support and ds.provenance_clean')
    if ds.camera_like_support and ds.provenance_clean and ds.local_signals_weak:
        ledger.add('caution_penalty', 0.40, 'ds.camera_like_support and ds.provenance_clean and ds.local_signals_weak')
    if ds.cfa_camera_like_support and ds.provenance_clean and ds.local_signals_weak:
        ledger.add('caution_penalty', 0.25, 'ds.cfa_camera_like_support and ds.provenance_clean and ds.local_signals_weak')
    # --------------------------------------------------
    # 2. Local editing support
    # --------------------------------------------------
    if ds.strong_local_edit:
        ledger.add('local_edit_support_score', 2.0, 'ds.strong_local_edit')
    elif ds.fragmented_local_edit:
        add_fragment_component(ledger, numerical_audit, 'local_edit_support_score', 0.5, 'otherwise / ds.fragmented_local_edit')
    if ds.strong_cross:
        ledger.add('local_edit_support_score', 1.0, 'ds.strong_cross')
    if boundary_strong:
        ledger.add('local_edit_support_score', 0.75, 'boundary_strong')
    elif boundary_medium:
        ledger.add('local_edit_support_score', 0.35, 'otherwise / boundary_medium')
    if ds.sensor_trace_inconsistency:
        ledger.add('local_edit_support_score', 0.50, 'ds.sensor_trace_inconsistency')
    if ds.cfa_inconsistency:
        ledger.add('local_edit_support_score', 0.35, 'ds.cfa_inconsistency')
    if ds.compression_inconsistency:
        ledger.add('local_edit_support_score', 0.40, 'ds.compression_inconsistency')
    if ds.subject_texture_strong:
        ledger.add('local_edit_support_score', 0.75, 'ds.subject_texture_strong')
    elif ds.subject_texture_moderate:
        ledger.add('local_edit_support_score', 0.35, 'otherwise / ds.subject_texture_moderate')
    if asym_strong:
        ledger.add('local_edit_support_score', 0.75, 'asym_strong')
    elif asym_medium:
        ledger.add('local_edit_support_score', 0.40, 'otherwise / asym_medium')
    if ds.material_realism_strong:
        ledger.add('local_edit_support_score', 1.50, 'ds.material_realism_strong')
    elif ds.material_realism_medium:
        ledger.add('local_edit_support_score', 0.75, 'otherwise / ds.material_realism_medium')
    elif ds.material_realism_weak:
        ledger.add('local_edit_support_score', 0.35, 'otherwise / otherwise / ds.material_realism_weak')
    # Camera-like acquisition slightly tempers local-edit interpretation
    if ds.camera_like_support:
        ledger.add('local_edit_support_score', -(0.20), 'ds.camera_like_support')
    if ds.cfa_camera_like_support:
        ledger.add('local_edit_support_score', -(0.20), 'ds.cfa_camera_like_support')
    # --------------------------------------------------
    # 3. Edit boost (what actually affects final suspicious score)
    # --------------------------------------------------
    if ds.subject_texture_strong:
        ledger.add('edit_boost', 0.40, 'ds.subject_texture_strong')
    elif ds.subject_texture_moderate:
        ledger.add('edit_boost', 0.20, 'otherwise / ds.subject_texture_moderate')
    if asym_strong:
        ledger.add('edit_boost', 0.30, 'asym_strong')
    elif asym_medium:
        ledger.add('edit_boost', 0.15, 'otherwise / asym_medium')
    if ds.material_realism_strong:
        ledger.add('edit_boost', 0.75, 'ds.material_realism_strong')
    elif ds.material_realism_medium:
        ledger.add('edit_boost', 0.40, 'otherwise / ds.material_realism_medium')
    if ds.segmentation_boundary_strong:
        ledger.add('edit_boost', 0.25, 'ds.segmentation_boundary_strong')
    elif ds.segmentation_boundary_medium:
        ledger.add('edit_boost', 0.10, 'otherwise / ds.segmentation_boundary_medium')
    # --------------------------------------------------
    # 4. Local-edit synergies
    # --------------------------------------------------
    boundary_stack_strong = (
        ds.strong_local_edit
        and ds.strong_cross
        and boundary_strong
        and ds.fft_structured
    )
    boundary_stack_medium = (
        ds.strong_local_edit
        and ds.strong_cross
        and (boundary_strong or boundary_medium)
    )
    if ds.segmentation_boundary_strong and ds.strong_cross:
        ledger.add('local_edit_support_score', 0.50, 'ds.segmentation_boundary_strong and ds.strong_cross')
        ledger.add('edit_boost', 0.25, 'ds.segmentation_boundary_strong and ds.strong_cross')
    elif ds.segmentation_boundary_medium and ds.strong_cross:
        ledger.add('local_edit_support_score', 0.25, 'otherwise / ds.segmentation_boundary_medium and ds.strong_cross')
        ledger.add('edit_boost', 0.10, 'otherwise / ds.segmentation_boundary_medium and ds.strong_cross')
    if ds.material_realism_strong and ds.strong_cross:
        ledger.add('edit_boost', 0.40, 'ds.material_realism_strong and ds.strong_cross')
    elif ds.material_realism_medium and ds.strong_cross:
        ledger.add('edit_boost', 0.20, 'otherwise / ds.material_realism_medium and ds.strong_cross')
    if ds.material_realism_strong and ds.subject_boundary_strong:
        ledger.add('edit_boost', 0.50, 'ds.material_realism_strong and ds.subject_boundary_strong')
    if ds.material_realism_strong and asym_strong:
        ledger.add('edit_boost', 0.75, 'ds.material_realism_strong and asym_strong')
    elif ds.material_realism_medium and asym_strong:
        ledger.add('edit_boost', 0.40, 'otherwise / ds.material_realism_medium and asym_strong')
    if boundary_stack_strong:
        ledger.add('local_edit_support_score', 1.25, 'boundary_stack_strong')
        ledger.add('edit_boost', 0.50, 'boundary_stack_strong')
    elif boundary_stack_medium:
        ledger.add('local_edit_support_score', 0.60, 'otherwise / boundary_stack_medium')
    if ds.fragmented_local_edit and ds.strong_cross:
        add_fragment_component(ledger, numerical_audit, 'edit_boost', 0.50, 'ds.fragmented_local_edit and ds.strong_cross')
    if ds.subject_boundary_strong and (ds.strong_cross or ds.fragmented_local_edit):
        ledger.add('edit_boost', 0.75, 'ds.subject_boundary_strong and (ds.strong_cross or ds.fragmented_local_edit)')
    elif ds.subject_boundary_medium and (ds.strong_cross or ds.fragmented_local_edit):
        ledger.add('edit_boost', 0.40, 'otherwise / ds.subject_boundary_medium and (ds.strong_cross or ds.fragmented_local_edit)')
    elif ds.subject_boundary_strong and ds.local_signals_weak:
        ledger.add('edit_boost', 0.35, 'otherwise / otherwise / ds.subject_boundary_strong and ds.local_signals_weak')
    # Realism fallback when local signals are otherwise weak
    if (
        ds.material_realism_strong
        and ds.local_signals_weak
        and not ds.strong_local_edit
        and not ds.strong_cross
    ):
        ledger.add('edit_boost', 0.40, 'ds.material_realism_strong and ds.local_signals_weak and (not ds.strong_local_edit) and (not ds.strong_cross)')
    # Convert structural support into a modest effective boost
    ledger.add('edit_boost', 0.18 * card.local_edit_support_score, 'local_support_conversion')
    # ------------------------------------------------------------
    # Clone / patch-reuse support
    # ------------------------------------------------------------
    card.clone_candidate = (
        ev.patch_similarity is not None
        and ev.patch_similarity.pattern == "possible_clone_reuse"
    )
    patch_spatial_inconclusive = (
        ev.patch_spatial is not None
        and ev.patch_spatial.pattern == "spatial_patch_recurrence_inconclusive"
    )
    patch_spatial_supportive = (
        ev.patch_spatial is not None
        and ev.patch_spatial.pattern in {
            "cross_region_patch_recurrence",
            "boundary_correlated_patch_recurrence",
            "subject_localized_patch_recurrence",
            "subject_internal_patch_recurrence",
        }
    )
    camera_benign = (
        ds.metadata_camera_like
        or ds.camera_like_support
    )
    natural_scene_risk = (
        ctx.natural_repetition
        or ctx.decorative_geometric
    )
    card.clone_ambiguous = (
        card.clone_candidate
        and (
            ds.coverage_ratio > 0.18
            or patch_spatial_inconclusive
            or (ev.cross_signal is None or ev.cross_signal.status in {"not_run", "inconclusive", "weak"})
        )
    )
    if usable_observation(ev.patch_similarity):
        # Base candidate support: lower than before, because clone-reuse should earn trust.
        if card.clone_candidate:
            ledger.add('clone_support_score', 1.25, 'usable_observation(ev.patch_similarity) / card.clone_candidate')
        # Strong local similarity still matters.
        if ds.patch_score >= 0.85:
            ledger.add('clone_support_score', 0.50, 'usable_observation(ev.patch_similarity) / ds.patch_score >= 0.85')
        if ds.mean_similarity >= 0.92:
            ledger.add('clone_support_score', 0.35, 'usable_observation(ev.patch_similarity) / ds.mean_similarity >= 0.92')
        if ds.separated_pair_count >= 10:
            ledger.add('clone_support_score', 0.35, 'usable_observation(ev.patch_similarity) / ds.separated_pair_count >= 10')
        # Spatial compactness helps clone interpretation, but broad coverage hurts it.
        if detail(ev.patch_similarity, "coverage_ratio", None) is not None and ds.coverage_ratio <= 0.18:
            ledger.add('clone_support_score', 0.35, "usable_observation(ev.patch_similarity) / detail(ev.patch_similarity, 'coverage_ratio', None) is not None and ds.coverage_ratio <= 0.18")
        elif ds.coverage_ratio > 0.25:
            ledger.add('clone_support_score', -(0.40), 'usable_observation(ev.patch_similarity) / otherwise / ds.coverage_ratio > 0.25')
        # Spatial corroboration is important.
        if patch_spatial_supportive:
            ledger.add('clone_support_score', 0.60, 'usable_observation(ev.patch_similarity) / patch_spatial_supportive')
        if patch_spatial_inconclusive:
            ledger.add('clone_support_score', -(0.75), 'usable_observation(ev.patch_similarity) / patch_spatial_inconclusive')
        # Cross-signal can help, but should not dominate clone interpretation.
        if ds.strong_cross and card.clone_candidate:
            ledger.add('clone_support_score', 0.15, 'usable_observation(ev.patch_similarity) / ds.strong_cross and card.clone_candidate')
        # Local-edit evidence can coexist with clone evidence, but do not reward this much.
        if ds.strong_local_edit and card.clone_candidate:
            ledger.add('clone_support_score', 0.05, 'usable_observation(ev.patch_similarity) / ds.strong_local_edit and card.clone_candidate')
        # Natural scene / repetitive-structure moderation.
        if natural_scene_risk:
            ledger.add('clone_support_score', -(0.85), 'usable_observation(ev.patch_similarity) / natural_scene_risk')
        # Camera-like evidence should substantially damp clone interpretation
        # when spatial corroboration is weak.
        if camera_benign:
            ledger.add('clone_support_score', -(0.90), 'usable_observation(ev.patch_similarity) / camera_benign')
            if patch_spatial_inconclusive:
                ledger.add('clone_support_score', -(0.60), 'usable_observation(ev.patch_similarity) / camera_benign / patch_spatial_inconclusive')
        # Stronger camera damping when metadata is explicitly camera-like and clone is not spatially confirmed.
        if ds.metadata_camera_like and not patch_spatial_supportive:
            ledger.multiply('clone_support_score', 0.35, 'usable_observation(ev.patch_similarity) / ds.metadata_camera_like and (not patch_spatial_supportive)')
        elif ds.metadata_camera_like:
            ledger.multiply('clone_support_score', 0.65, 'usable_observation(ev.patch_similarity) / otherwise / ds.metadata_camera_like')
        ledger.maximum("clone_support_score", 0.0, "clone_floor")
    # --------------------------------------------------
    # 6. Synthetic structure
    # --------------------------------------------------
    if ds.segmentation_fragmented:
        ledger.add('synthetic_boost', 0.50, 'ds.segmentation_fragmented')
    if ds.segmentation_clean:
        ledger.add('synthetic_boost', 0.30, 'ds.segmentation_clean')
    if (
        ds.fft_structured
        and ds.patch_structured
        and ds.fft_score >= 0.80
        and ds.peak_periodicity >= 0.70
        and ds.peak_symmetry >= 0.55
        and ds.peak_count >= 4
        and ds.axis_bias >= 0.60
        and ds.patch_score >= 0.70
        and ds.repetition_score >= 0.60
        and ds.separated_pair_count >= 8
        and ds.pair_count >= 12
        and ds.mean_similarity >= 0.88
        and ds.max_similarity >= 0.92
    ):
        ledger.add('synthetic_boost', 1.00, 'ds.fft_structured and ds.patch_structured and (ds.fft_score >= 0.8) and (ds.peak_periodicity >= 0.7) and (ds.peak_symmetry >= 0.55) and (ds.peak_count >= 4) and (ds.axis_bias >= 0.6) and (ds.patch_score >= 0.7) and (ds.repetition_score >= 0.6) and (ds.separated_pair_count >= 8) and (ds.pair_count >= 12) and (ds.mean_similarity >= 0.88) and (ds.max_similarity >= 0.92)')
        if ds.local_signals_weak and ds.coverage_ratio >= 0.18 and ds.provenance_clean:
            ledger.add('caution_penalty', 1.50, 'ds.fft_structured and ds.patch_structured and (ds.fft_score >= 0.8) and (ds.peak_periodicity >= 0.7) and (ds.peak_symmetry >= 0.55) and (ds.peak_count >= 4) and (ds.axis_bias >= 0.6) and (ds.patch_score >= 0.7) and (ds.repetition_score >= 0.6) and (ds.separated_pair_count >= 8) and (ds.pair_count >= 12) and (ds.mean_similarity >= 0.88) and (ds.max_similarity >= 0.92) / ds.local_signals_weak and ds.coverage_ratio >= 0.18 and ds.provenance_clean')
    if ds.material_realism_strong:
        ledger.add('synthetic_boost', 0.75, 'ds.material_realism_strong')
    elif ds.material_realism_medium:
        ledger.add('synthetic_boost', 0.40, 'otherwise / ds.material_realism_medium')
    # Context moderation of synthetic structure
    if card.synthetic_boost > 0:
        if ctx.natural_repetition:
            ledger.multiply('synthetic_boost', 0.75, 'card.synthetic_boost > 0 / ctx.natural_repetition')
        if ctx.decorative_geometric:
            ledger.multiply('synthetic_boost', 0.85, 'card.synthetic_boost > 0 / ctx.decorative_geometric')
        if ctx.smartphone_computational:
            ledger.multiply('synthetic_boost', 0.85, 'card.synthetic_boost > 0 / ctx.smartphone_computational')
        if ctx.screen_origin:
            ledger.multiply('synthetic_boost', 0.50, 'card.synthetic_boost > 0 / ctx.screen_origin')
        if ds.metadata_camera_like:
            ledger.multiply('synthetic_boost', 0.60, 'card.synthetic_boost > 0 / ds.metadata_camera_like')
    # --------------------------------------------------
    # 7. Provenance
    # --------------------------------------------------
    if (ds.metadata_synthetic or ds.metadata_enhancement) and ds.osint_ai_context:
        ledger.add('provenance_boost', 1.25, '(ds.metadata_synthetic or ds.metadata_enhancement) and ds.osint_ai_context')
    elif ds.metadata_synthetic or ds.metadata_enhancement:
        ledger.add('provenance_boost', 0.75, 'otherwise / ds.metadata_synthetic or ds.metadata_enhancement')
    elif ds.osint_ai_context:
        ledger.add('provenance_boost', 0.50, 'otherwise / otherwise / ds.osint_ai_context')
    # --------------------------------------------------
    # 8. Sensor / compression
    # --------------------------------------------------
    if ds.sensor_trace_inconsistency and (ds.strong_cross or ds.strong_local_edit):
        ledger.add('sensor_boost', 0.75, 'ds.sensor_trace_inconsistency and (ds.strong_cross or ds.strong_local_edit)')
    if ds.cfa_inconsistency and (ds.strong_cross or ds.strong_local_edit):
        ledger.add('sensor_boost', 0.40, 'ds.cfa_inconsistency and (ds.strong_cross or ds.strong_local_edit)')
    if ds.compression_inconsistency and (
        ds.strong_cross or ds.strong_local_edit or ds.subject_boundary_strong
    ):
        ledger.add('compression_boost', 0.75, 'ds.compression_inconsistency and (ds.strong_cross or ds.strong_local_edit or ds.subject_boundary_strong)')
    elif ds.double_jpeg_suspect:
        ledger.add('compression_boost', 0.40, 'otherwise / ds.double_jpeg_suspect')
    elif ds.block_history_anomaly and (ds.fft_structured or ds.patch_structured):
        ledger.add('compression_boost', 0.35, 'otherwise / otherwise / ds.block_history_anomaly and (ds.fft_structured or ds.patch_structured)')
    # --------------------------------------------------
    # 9. Contextual false-positive risk
    # --------------------------------------------------
    card.contextual_false_positive_risk = (
        ds.camera_like_support
        and (
            ctx.natural_repetition
            or ctx.decorative_geometric
            or ctx.smartphone_computational
            or ctx.screen_origin
        )
        and not ds.sensor_trace_inconsistency
        and not ds.strong_local_edit
        and not ds.strong_cross
        and not ds.subject_boundary_strong
    )
    if ds.coverage_ratio > 0.20 and ds.separated_pair_count >= 8:
        ledger.add('caution_penalty', 0.50, 'ds.coverage_ratio > 0.2 and ds.separated_pair_count >= 8')
    if ds.coverage_ratio > 0.28 and ds.local_signals_weak and ds.provenance_clean:
        ledger.add('caution_penalty', 1.00, 'ds.coverage_ratio > 0.28 and ds.local_signals_weak and ds.provenance_clean')
    if ctx.natural_repetition:
        ledger.add('caution_penalty', 0.75, 'ctx.natural_repetition')
    if ctx.decorative_geometric and ds.fft_structured:
        ledger.add('caution_penalty', 0.50, 'ctx.decorative_geometric and ds.fft_structured')
    if ctx.smartphone_computational:
        ledger.add('caution_penalty', 0.40, 'ctx.smartphone_computational')
    if ctx.screen_origin:
        ledger.add('caution_penalty', 1.00, 'ctx.screen_origin')
    # Also include camera counter-support as caution
    ledger.add('caution_penalty', card.camera_counter_support, 'measured_camera_caution')
    # Raw mechanism values include existing within-mechanism context transforms.
    raw_contributions = {name: getattr(card, name) for name in COMPONENT_FIELDS}
    raw_operation_count = len(ledger.operations)
    measured_camera_support = card.camera_counter_support
    photo_prior = has_real_photo_context_prior(ctx, ev, ds)
    if photo_prior:
        ledger.add("camera_counter_support", 1.5, "photo_context_routing_bonus")
        ledger.add("caution_penalty", 1.0, "photo_context_caution")

    # Reliability applies to observed local/edit support, not to an absent sensor.
    boundary_applicable = card.local_edit_support_score > 0 or card.edit_boost > 0
    if ds.region_geometry_unreliable:
        ledger.multiply("local_edit_support_score", 0.45, "region_geometry_reliability")
        ledger.multiply("edit_boost", 0.45, "region_geometry_reliability")
        ledger.add("caution_penalty", 1.0, "region_geometry_caution")
        card.contextual_false_positive_risk = True
    if boundary_applicable and ds.boundary_reliability_score < 1.0:
        ledger.multiply("local_edit_support_score", ds.boundary_reliability_score, "boundary_reliability")
        ledger.multiply("edit_boost", ds.boundary_reliability_score, "boundary_reliability")
        ledger.add("caution_penalty", 1.0 - ds.boundary_reliability_score, "boundary_reliability_caution")

    # The routing context bonus is separate from measured camera evidence. Keep
    # the original measured-camera attenuation and explicit photo-prior factor.
    camera_multiplier = camera_attenuation(measured_camera_support)
    geometry_multiplier = 0.75 if ds.region_geometry_unreliable else 1.0
    photo_multiplier = 0.70 if photo_prior else 1.0
    subtotal = fsum([base_suspicious, *(getattr(card, name) for name in BOOST_FIELDS)])
    card.suspicious_score = max(0.0, subtotal * camera_multiplier - card.caution_penalty) * geometry_multiplier * photo_multiplier
    card.benign_score = base_benign
    card.synthetic_supported_by_other_domains = (
        ds.metadata_synthetic or ds.osint_ai_context or ds.material_realism_strong
    )
    finalize_component_allocations(numerical_audit, ledger.operations)
    card.calculation = {
        "calculation_version": "2a", "status": "valid",
        "base_suspicious": base_suspicious, "base_benign": base_benign,
        "base_evidence": base_evidence,
        "numerical_deduplication": numerical_audit,
        "domain_bonus": 0.25,
        "component_operations": ledger.operations,
        "raw_operation_count": raw_operation_count,
        "raw_contributions": raw_contributions,
        "final_contributions": {name: getattr(card, name) for name in COMPONENT_FIELDS},
        "reliability_adjustments": {
            "boundary_reliability": ds.boundary_reliability_score,
            "boundary_adjustment_applicable": boundary_applicable,
            "region_geometry_unreliable": ds.region_geometry_unreliable,
            "geometry_mechanism_multiplier": 0.45 if ds.region_geometry_unreliable else 1.0,
        },
        "penalties": [item for item in ledger.operations if item["field"] == "caution_penalty"],
        "aggregate_transforms": {
            "measured_camera_support": measured_camera_support,
            "camera_multiplier": camera_multiplier,
            "geometry_multiplier": geometry_multiplier,
            "photo_context_multiplier": photo_multiplier,
            "photo_context_prior": photo_prior,
            "suspicious_floor": 0.0,
        },
        "aggregate_scores": {"suspicious_score": card.suspicious_score, "benign_score": card.benign_score},
    }
    validate_scorecard(card)
    return card


def has_real_photo_context_prior(ctx: HypothesisContext, ev: EvidenceSnapshot, ds: DerivedSignals) -> bool:
    return bool(
        ds.provenance_clean and not ds.metadata_synthetic
        and ev.metadata is not None and ev.metadata.pattern == "camera_metadata_present"
        and ctx.smartphone_computational
    )
