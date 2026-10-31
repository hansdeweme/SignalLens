#hypothesis_engine.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
# local imports to avoid circular dependencies
from gui_semantics import ModuleSummary
from metadata_evidence import (
    ProvenanceState, MISSING_METADATA_PATTERNS, metadata_provenance_state,
)

STATUS_WEIGHT = {
    "not_run": 0.0,
    "inconclusive": 0.0,
    "weak": 0.5,
    "medium": 1.5,
    "strong": 3.0,
}

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
    if section is None or not getattr(section, "details", None):
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
    suspicious_sections = [s for s in sections.values() if is_suspicious(s)]
    benign_sections = [s for s in sections.values() if is_benign(s)]
    suspicious_score = sum(weight(s) for s in suspicious_sections)
    benign_score = sum(weight(s) for s in benign_sections)
    suspicious_domains = {s.domain for s in suspicious_sections if getattr(s, "domain", None)}
    benign_domains = {s.domain for s in benign_sections if getattr(s, "domain", None)}
    suspicious_score += max(0, len(suspicious_domains) - 1) * 0.25
    benign_score += max(0, len(benign_domains) - 1) * 0.25
    return suspicious_score, benign_score, suspicious_domains, benign_domains

def compute_scorecard(sections: dict[str, ModuleSummary], ctx: HypothesisContext, ev: EvidenceSnapshot, ds: DerivedSignals,) -> ScoreCard:
    card = ScoreCard()
    # --------------------------------------------------
    # Base scores from section status/polarity
    # --------------------------------------------------
    (
        card.suspicious_score,
        card.benign_score,
        card.suspicious_domains,
        card.benign_domains,
    ) = compute_base_scores(sections)
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
        card.camera_counter_support += 1.50
    if ds.camera_like_support:
        card.camera_counter_support += 1.25
    if ds.cfa_camera_like_support:
        card.camera_counter_support += 1.00
    # Reward convergence of multiple camera-like signals
    if card.camera_counter_support >= 2.0:
        card.camera_counter_support += 0.50
    # Additional benign moderation
    if ds.segmentation_natural and ds.camera_like_support:
        card.caution_penalty += 0.40
    if ds.material_realism_low and ds.provenance_clean:
        card.caution_penalty += 0.60
    if ds.compression_consistent and ds.provenance_clean and ds.local_signals_weak:
        card.caution_penalty += 0.40
    if ds.camera_like_support and ds.provenance_clean:
        card.caution_penalty += 0.35
    if ds.camera_like_support and ds.provenance_clean and ds.local_signals_weak:
        card.caution_penalty += 0.40
    if ds.cfa_camera_like_support and ds.provenance_clean and ds.local_signals_weak:
        card.caution_penalty += 0.25
    # --------------------------------------------------
    # 2. Local editing support
    # --------------------------------------------------
    if ds.strong_local_edit:
        card.local_edit_support_score += 2.0
    elif ds.fragmented_local_edit:
        card.local_edit_support_score += 0.5
    if ds.strong_cross:
        card.local_edit_support_score += 1.0
    if boundary_strong:
        card.local_edit_support_score += 0.75
    elif boundary_medium:
        card.local_edit_support_score += 0.35
    if ds.sensor_trace_inconsistency:
        card.local_edit_support_score += 0.50
    if ds.cfa_inconsistency:
        card.local_edit_support_score += 0.35
    if ds.compression_inconsistency:
        card.local_edit_support_score += 0.40
    if ds.subject_texture_strong:
        card.local_edit_support_score += 0.75
    elif ds.subject_texture_moderate:
        card.local_edit_support_score += 0.35
    if asym_strong:
        card.local_edit_support_score += 0.75
    elif asym_medium:
        card.local_edit_support_score += 0.40
    if ds.material_realism_strong:
        card.local_edit_support_score += 1.50
    elif ds.material_realism_medium:
        card.local_edit_support_score += 0.75
    elif ds.material_realism_weak:
        card.local_edit_support_score += 0.35
    # Camera-like acquisition slightly tempers local-edit interpretation
    if ds.camera_like_support:
        card.local_edit_support_score -= 0.20
    if ds.cfa_camera_like_support:
        card.local_edit_support_score -= 0.20
    # --------------------------------------------------
    # 3. Edit boost (what actually affects final suspicious score)
    # --------------------------------------------------
    if ds.subject_texture_strong:
        card.edit_boost += 0.40
    elif ds.subject_texture_moderate:
        card.edit_boost += 0.20
    if asym_strong:
        card.edit_boost += 0.30
    elif asym_medium:
        card.edit_boost += 0.15
    if ds.material_realism_strong:
        card.edit_boost += 0.75
    elif ds.material_realism_medium:
        card.edit_boost += 0.40
    if ds.segmentation_boundary_strong:
        card.edit_boost += 0.25
    elif ds.segmentation_boundary_medium:
        card.edit_boost += 0.10
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
        card.local_edit_support_score += 0.50
        card.edit_boost += 0.25
    elif ds.segmentation_boundary_medium and ds.strong_cross:
        card.local_edit_support_score += 0.25
        card.edit_boost += 0.10
    if ds.material_realism_strong and ds.strong_cross:
        card.edit_boost += 0.40
    elif ds.material_realism_medium and ds.strong_cross:
        card.edit_boost += 0.20
    if ds.material_realism_strong and ds.subject_boundary_strong:
        card.edit_boost += 0.50
    if ds.material_realism_strong and asym_strong:
        card.edit_boost += 0.75
    elif ds.material_realism_medium and asym_strong:
        card.edit_boost += 0.40
    if boundary_stack_strong:
        card.local_edit_support_score += 1.25
        card.edit_boost += 0.50
    elif boundary_stack_medium:
        card.local_edit_support_score += 0.60
    if ds.fragmented_local_edit and ds.strong_cross:
        card.edit_boost += 0.50
    if ds.subject_boundary_strong and (ds.strong_cross or ds.fragmented_local_edit):
        card.edit_boost += 0.75
    elif ds.subject_boundary_medium and (ds.strong_cross or ds.fragmented_local_edit):
        card.edit_boost += 0.40
    elif ds.subject_boundary_strong and ds.local_signals_weak:
        card.edit_boost += 0.35
    # Realism fallback when local signals are otherwise weak
    if (
        ds.material_realism_strong
        and ds.local_signals_weak
        and not ds.strong_local_edit
        and not ds.strong_cross
    ):
        card.edit_boost += 0.40
    # Convert structural support into a modest effective boost
    card.edit_boost += 0.18 * card.local_edit_support_score
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
    clone_score = 0.0
    # Base candidate support: lower than before, because clone-reuse should earn trust.
    if card.clone_candidate:
        clone_score += 1.25
    # Strong local similarity still matters.
    if ds.patch_score >= 0.85:
        clone_score += 0.50
    if ds.mean_similarity >= 0.92:
        clone_score += 0.35
    if ds.separated_pair_count >= 10:
        clone_score += 0.35
    # Spatial compactness helps clone interpretation, but broad coverage hurts it.
    if ds.coverage_ratio <= 0.18:
        clone_score += 0.35
    elif ds.coverage_ratio > 0.25:
        clone_score -= 0.40
    # Spatial corroboration is important.
    if patch_spatial_supportive:
        clone_score += 0.60
    if patch_spatial_inconclusive:
        clone_score -= 0.75
    # Cross-signal can help, but should not dominate clone interpretation.
    if ds.strong_cross and card.clone_candidate:
        clone_score += 0.15
    # Local-edit evidence can coexist with clone evidence, but do not reward this much.
    if ds.strong_local_edit and card.clone_candidate:
        clone_score += 0.05
    # Natural scene / repetitive-structure moderation.
    if natural_scene_risk:
        clone_score -= 0.85
    # Camera-like evidence should substantially damp clone interpretation
    # when spatial corroboration is weak.
    if camera_benign:
        clone_score -= 0.90
        if patch_spatial_inconclusive:
            clone_score -= 0.60
    # Stronger camera damping when metadata is explicitly camera-like and clone is not spatially confirmed.
    if ds.metadata_camera_like and not patch_spatial_supportive:
        clone_score *= 0.35
    elif ds.metadata_camera_like:
        clone_score *= 0.65
    card.clone_support_score += max(0.0, clone_score)
    # --------------------------------------------------
    # 6. Synthetic structure
    # --------------------------------------------------
    if ds.segmentation_fragmented:
        card.synthetic_boost += 0.50
    if ds.segmentation_clean:
        card.synthetic_boost += 0.30
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
        card.synthetic_boost += 1.00
        if ds.local_signals_weak and ds.coverage_ratio >= 0.18 and ds.provenance_clean:
            card.caution_penalty += 1.50
    if ds.material_realism_strong:
        card.synthetic_boost += 0.75
    elif ds.material_realism_medium:
        card.synthetic_boost += 0.40
    # Context moderation of synthetic structure
    if card.synthetic_boost > 0:
        if ctx.natural_repetition:
            card.synthetic_boost *= 0.75
        if ctx.decorative_geometric:
            card.synthetic_boost *= 0.85
        if ctx.smartphone_computational:
            card.synthetic_boost *= 0.85
        if ctx.screen_origin:
            card.synthetic_boost *= 0.50
        if ds.metadata_camera_like:
            card.synthetic_boost *= 0.60
    # --------------------------------------------------
    # 7. Provenance
    # --------------------------------------------------
    if (ds.metadata_synthetic or ds.metadata_enhancement) and ds.osint_ai_context:
        card.provenance_boost += 1.25
    elif ds.metadata_synthetic or ds.metadata_enhancement:
        card.provenance_boost += 0.75
    elif ds.osint_ai_context:
        card.provenance_boost += 0.50
    # --------------------------------------------------
    # 8. Sensor / compression
    # --------------------------------------------------
    if ds.sensor_trace_inconsistency and (ds.strong_cross or ds.strong_local_edit):
        card.sensor_boost += 0.75
    if ds.cfa_inconsistency and (ds.strong_cross or ds.strong_local_edit):
        card.sensor_boost += 0.40
    if ds.compression_inconsistency and (
        ds.strong_cross or ds.strong_local_edit or ds.subject_boundary_strong
    ):
        card.compression_boost += 0.75
    elif ds.double_jpeg_suspect:
        card.compression_boost += 0.40
    elif ds.block_history_anomaly and (ds.fft_structured or ds.patch_structured):
        card.compression_boost += 0.35
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
        card.caution_penalty += 0.50
    if ds.coverage_ratio > 0.28 and ds.local_signals_weak and ds.provenance_clean:
        card.caution_penalty += 1.00
    if ctx.natural_repetition:
        card.caution_penalty += 0.75
    if ctx.decorative_geometric and ds.fft_structured:
        card.caution_penalty += 0.50
    if ctx.smartphone_computational:
        card.caution_penalty += 0.40
    if ctx.screen_origin:
        card.caution_penalty += 1.00
    # Also include camera counter-support as caution
    card.caution_penalty += card.camera_counter_support
    # --------------------------------------------------
    # 10. Final suspicious score
    # --------------------------------------------------
    card.suspicious_score += (
        card.synthetic_boost
        + card.edit_boost
        + card.provenance_boost
        + card.sensor_boost
        + card.compression_boost
    )
    # Overweighted suspicious scores are best handled by multiplicative compression,
    # not only subtraction. This preserves ranking while preventing runaway inflation.
    if card.camera_counter_support >= 3.0:
        card.suspicious_score *= 0.55
    elif card.camera_counter_support >= 2.0:
        card.suspicious_score *= 0.70
    elif card.camera_counter_support >= 1.0:
        card.suspicious_score *= 0.85
    card.suspicious_score -= card.caution_penalty
    card.suspicious_score = max(0.0, card.suspicious_score)
    # --------------------------------------------------
    # 11. Synthetic support from other domains
    # --------------------------------------------------
    card.synthetic_supported_by_other_domains = (
        ds.metadata_synthetic
        or ds.osint_ai_context
        or ds.material_realism_strong
    )
    #-----------------------------------------------------------
    # reliability
    #-----------------------------------------------------------
    if ds.region_geometry_unreliable:
        card.local_edit_support_score *= 0.45
        card.edit_boost *= 0.45
        card.suspicious_score *= 0.75
        card.caution_penalty += 1.0
        card.contextual_false_positive_risk = True        
    if ds.boundary_reliability_score < 1.0:
        card.local_edit_support_score *= ds.boundary_reliability_score
        card.edit_boost *= ds.boundary_reliability_score
        card.caution_penalty += (1.0 - ds.boundary_reliability_score)
    
    return card
