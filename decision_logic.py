# decision_logic.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Any, Callable
from math import isfinite
# Local imports 
from gui_semantics import ModuleSummary
from hypothesis_engine import (
    build_context,
    build_evidence_snapshot,
    compute_base_scores,
    compute_scorecard,
    derive_signals,
    is_suspicious,
    is_benign,
    weight,
    HypothesisAssessment,
    DerivedSignals,
    ScoreCard,
    has_real_photo_context_prior,
)
from scorecard_integrity import ScorecardIntegrityError, available_sections
from confidence_policy import (
    Finding, Specificity, finding_specificity, AssessmentEvidence,
    ConfidencePolicyResult, evaluate_confidence, generic_confidence,
)
from confidence_policy_inputs import snapshot_confidence_facts, coverage_limitations
from production_corroboration import (
    CorroborationRequirement, RequirementKind, evaluate_corroboration, record_gate,
)
from metadata_evidence import (
    ProvenanceState, metadata_provenance_state,
)
from hypothesis_evidence import scope_hypothesis_evidence, evidence_presentation, append_hypothesis_evidence
from signal_language import humanize_signal

#=============================================
# Helpers tructured reasoning trace
#=============================================
def _section_snapshot(sections: dict[str, ModuleSummary]) -> dict[str, dict]:
    snapshot: dict[str, dict] = {}
    for key, s in sections.items():
        if not s:
            continue
        snapshot[key] = {
            "name": s.name,
            "status": s.status,
            "polarity": s.polarity,
            "pattern": s.pattern,
            "score": _jsonable_scalar(s.score),
            "note": s.note,
        }
    return snapshot

def _object_to_dict(obj) -> dict:
    """
    Convert lightweight dataclass-like or attribute-based objects
    into a json-friendly dict without dragging in large arrays.
    """
    if obj is None:
        return {}
    if hasattr(obj, "__dataclass_fields__"):
        out = {}
        for k in obj.__dataclass_fields__.keys():
            if obj.__dataclass_fields__[k].metadata.get("trace_exclude"):
                continue
            v = getattr(obj, k)
            out[k] = _jsonable_scalar(v)
        return out
    if hasattr(obj, "__dict__"):
        return {k: _jsonable_scalar(v) for k, v in vars(obj).items()}
    return {}

def _jsonable_scalar(v):
    if isinstance(v, float) and not isfinite(v):
        return None
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if hasattr(v, "__dataclass_fields__") or hasattr(v, "__dict__"):
        return _object_to_dict(v)
    if isinstance(v, (list, tuple)):
        return [_jsonable_scalar(x) for x in v]
    if isinstance(v, (set, frozenset)):
        return [_jsonable_scalar(x) for x in sorted(v)]
    if isinstance(v, dict):
        return {str(k): _jsonable_scalar(val) for k, val in v.items()}
    try:
        number = float(v)
        return number if isfinite(number) else None
    except Exception:
        return str(v)

def _build_reasoning_trace(
    sections: dict[str, ModuleSummary],
    ctx,
    ev,
    ds,
    card,
    dominant_pattern: str | None,
    confidence_tier: str,
    polarity: str,
    overall_text: str,
    decision_branch: str | None = None,
    analysis_mode: str | None = None,
    contextual_priors: dict | None = None,
    route_trace: list | None = None,
    hypotheses: list[HypothesisAssessment] | None = None,
    primary_hypothesis: str | None = None,
    selection_reason: str | None = None,
    confidence_rationale: list[str] | None = None,
    corroboration_gates: list[dict] | None = None,
    confidence_policy_results: list[ConfidencePolicyResult] | None = None,
) -> dict:
    assessment = next((h for h in (hypotheses or []) if h.hypothesis_id == primary_hypothesis), None)
    presentation = evidence_presentation(assessment)
    rationale = confidence_rationale if confidence_rationale is not None else build_confidence_rationale(
        card, sections, polarity, assessment=assessment, selection_reason=selection_reason,
    )
    context_dict = _object_to_dict(ctx)
    if analysis_mode is not None:
        context_dict["analysis_mode"] = analysis_mode            
    return {
        "analysis_mode": analysis_mode,
        "section_snapshot": _section_snapshot(sections),
        "context": context_dict,
        "contextual_priors": contextual_priors or {},
        "evidence_snapshot": _object_to_dict(ev),
        "derived_signals": _object_to_dict(ds),
        "scorecard": _object_to_dict(card),
        "scorecard_calculation": _jsonable_scalar(card.calculation),
        "confidence_policy": {
            "version": "3", "primary_hypothesis": primary_hypothesis,
            "assessments": [_object_to_dict(item) for item in (confidence_policy_results or [])],
        },
        "corroboration_audit": {
            "version": "2b3",
            "evaluated_gates": _jsonable_scalar(sorted(corroboration_gates or [], key=lambda item: item['gate_id'])),
            "limitations": [
                "Measurement-disjoint ancestry is a structural diversity check, not statistical independence.",
                "Compound conditions allow related interpretations. Production base-credit allocation is audited separately; shadow policy remains diagnostic.",
            ],
        },
        "decision_route_trace": [
            _object_to_dict(item) for item in (route_trace or [])
        ],        
        "hypothesis_assessments": [_object_to_dict(item) for item in (hypotheses or [])],
        "provenance_evidence": {
            "state": ds.provenance_state,
            "metadata_authenticity_verified": False,
        },
        "decision": {
            "primary_hypothesis": primary_hypothesis,
            "selection_reason": selection_reason,
            "decision_branch": decision_branch,
            "dominant_pattern": dominant_pattern,
            "confidence_tier": confidence_tier,
            "polarity": polarity,
            **_jsonable_scalar(presentation),
            "confidence_rationale": rationale,
            "overall_text": overall_text,
        },
    }

# We have two abstraction layers: 
# Hypothesis Engine:  sections → DerivedSignals → ScoreCard
# Summary / Narrative sections → human-readable narrative
# We do NOT pass DerivedSignals. Instead, re-derive minimal logic from sections.

def determine_dominant_pattern(sections):
    sections = available_sections(sections)
    # ----------------------------
    # Extract sections safely
    # ----------------------------
    def score_of(s):
        return float(s.score) if s and s.score is not None else 0.0

    def pattern_of(s):
        return s.pattern if s else None
    mat = sections.get("subject_material_realism")
    asym = sections.get("subject_process_asymmetry")
    boundary = sections.get("boundary")
    cross = sections.get("cross_signal")
    patch = sections.get("patch_similarity")
    fft = sections.get("fft")
    seg_align = sections.get("segmentation_alignment")
    metadata = sections.get("metadata")
    sensor = sections.get("sensor_origin")
    cfa = sections.get("cfa_demosaic")
    #-----------------------------
    # exif stripped penalty
    #-----------------------------
    is_platform_stripped = metadata and metadata.pattern in {
            "metadata_stripped", 
            "social_media_provenance"
        }    
    # ----------------------------
    # Normalize signals
    # ----------------------------
    mat_score = score_of(mat)
    asym_score = score_of(asym)
    seg_score = score_of(seg_align)
    patch_score = score_of(patch)
    fft_score = score_of(fft)
    # Boolean abstractions
    material_strong = mat_score >= 0.58
    material_medium = 0.44 <= mat_score < 0.58
    asym_strong = pattern_of(asym) == "subject_process_asymmetry_strong"
    asym_medium = asym_score >= 0.4
    boundary_strong = pattern_of(boundary) == "possible_foreground_background_processing_mismatch"
    cross_strong = pattern_of(cross) == "strong_hotspot_convergence"
    segmentation_strong = seg_score >= 0.55
    segmentation_medium = 0.35 <= seg_score < 0.55
    patch_clone = pattern_of(patch) == "possible_clone_reuse"
    patch_structured = patch_score >= 0.7
    fft_structured = fft_score >= 0.7
    metadata_synthetic = metadata_provenance_state(metadata) == ProvenanceState.UNVERIFIED_GENERATION_DECLARATION
    camera_like = (
        metadata and metadata.pattern in {"camera_metadata_present", "camera_metadata_rich"}
        or (sensor and sensor.pattern in {"camera_like_sensor_pattern", "weak_camera_sensor_pattern"})
        or (cfa and cfa.pattern in {"camera_like_cfa_supported", "weak_camera_cfa_supported"})
    )
    # ----------------------------
    # 2. Gate Anomaly Flags
    # ----------------------------
    cfa_anomalous = pattern_of(cfa) == "synthetic_bayer_pattern_absence"    
    # The Penalty: Suppress the anomaly boolean if the platform stripped the metadata
    if is_platform_stripped:
        cfa_anomalous = False        
    # ----------------------------
    # Tier 1 — strong, multi-domain convergence
    # ----------------------------
    # Localized compositing (strongest real-world pattern)
    if (boundary_strong or segmentation_strong) and cross_strong:
        return "possible_foreground_background_processing_mismatch"
    # Clone / copy-move (patch-dominant)
    if patch_clone and patch_score >= 0.75:
        return "possible_clone_reuse"
    # Synthetic structure (global + patch)
    if fft_structured and patch_structured and not camera_like:
        return "synthetic_multi_signal_convergence"
    # Strong subject-level synthetic signal
    if material_strong and asym_strong:
        return "synthetic_subject_compositing_signature"
    # Metadata-declared synthetic
    if metadata_synthetic:
        return "provenance_supported_synthetic_context"
    # ----------------------------
    # Tier 2 — strong single-domain signals
    # ----------------------------
    if material_strong:
        return "subject_material_realism_failure"
    if asym_strong:
        return "subject_process_asymmetry_strong"
    if boundary_strong or segmentation_strong:
        return "possible_subject_background_segmentation_artifact"
    if cross_strong:
        return "strong_cross_signal_anomaly"
    # ----------------------------
    # Tier 3 — moderate signals
    # ----------------------------
    if cfa_anomalous:
        return "synthetic_bayer_pattern_absence"    
    if material_medium:
        return "subject_material_regularization"
    if asym_medium:
        return "subject_process_asymmetry_moderate"
    if segmentation_medium:
        return "boundary_alignment_inconclusive"
    if patch_structured:
        return "structured_patch_recurrence"
    if fft_structured:
        return "structured_frequency_anomaly"
    # ----------------------------
    # New Contextual Tier / Fallback
    # ----------------------------
    # If it was stripped, and it *would* have been a CFA anomaly, output a clear inconclusive pattern
    if is_platform_stripped and pattern_of(cfa) == "synthetic_bayer_pattern_absence":
        return "inconclusive_platform_compressed"
    # ----------------------------
    # Tier 4 — benign override
    # ----------------------------
    if camera_like:
        return "camera_like_acquisition_supported"
    # ----------------------------
    # Fallback
    # ----------------------------
    return "inconclusive"

# same principle
def determine_confidence(card, sections, *, corroboration_gates=None):
    mat = sections.get("subject_material_realism")
    asym = sections.get("subject_process_asymmetry")
    boundary = sections.get("boundary")
    cross = sections.get("cross_signal")
    mat_score = mat.score if mat and mat.score is not None else 0.0
    from numbers import Real
    considered = [key for key, matched in (
        ('subject_material_realism', isinstance(mat_score, Real) and not isinstance(mat_score, bool) and isfinite(mat_score) and mat_score >= 0.58),
        ('subject_process_asymmetry', bool(asym and asym.pattern == 'subject_process_asymmetry_strong')),
        ('boundary', bool(boundary and boundary.pattern == 'possible_foreground_background_processing_mismatch')),
        ('cross_signal', bool(cross and cross.pattern == 'strong_hotspot_convergence')),
    ) if matched]
    active = available_sections(sections)
    strong_signals = sum(key in active and active[key].polarity == 'suspicious' for key in considered)
    source_check = evaluate_corroboration(
        sections, ['evidence:' + key for key in considered],
        CorroborationRequirement('confidence.strong_source_diversity', 'unresolved_anomaly',
            RequirementKind.DISTINCT_SOURCES, minimum_indicators=2, minimum_sources=2),
    )
    score = card.suspicious_score
    source_check.update(observed_strong_indicator_count=strong_signals,
        score_requirement_satisfied=score >= 3.0,
        gate_passed=source_check['requirement_satisfied'] and score >= 3.0,
        production_correction='Replace detector-count diversity with measurement-disjoint indicator witnesses; keep score thresholds unchanged.')
    record_gate(corroboration_gates, source_check)
    # Compatibility helper; authoritative generic thresholds live in the policy.
    return generic_confidence(score, strong_signals, source_check['requirement_satisfied'])[0]

def extract_secondary_patterns(
    sections: dict[str, ModuleSummary],
    primary: str | None,
    target_polarity: str | None = None,
) -> list[str]:
    candidates: list[tuple[str, float]] = []
    priority_patterns: list[str] = []
    provenance_priority = {
        "declared_synthetic_candidate",
        "declared_enhancement_candidate",
    }
    inconclusive_patterns = {
        "ela_inconclusive",
        "noise_inconclusive",
        "frequency_inconclusive",
        "boundary_inconclusive",
    }
    for s in sections.values():
        if not s or not s.pattern:
            continue
        if s.pattern == primary:
            continue
        if s.pattern in inconclusive_patterns:
            continue
        if target_polarity is not None and s.polarity != target_polarity:
            continue
        score = float(s.score) if s.score is not None else 0.0
        if s.pattern in provenance_priority and score >= 0.35:
            priority_patterns.append(s.pattern)
            continue

        if score >= 0.35:
            candidates.append((s.pattern, score))
    priority_patterns = list(dict.fromkeys(priority_patterns))
    candidates.sort(key=lambda x: x[1], reverse=True)
    scored_patterns = [p for p, _ in candidates]
    merged = priority_patterns + [
        p for p in scored_patterns if p not in priority_patterns
    ]
    return merged[:3]

def append_secondary_patterns(text: str, secondary: list[str]) -> str:
    if not secondary:
        return text
    formatted = "\n".join(f"- {humanize_signal(p)}" for p in secondary)
    return (
        text.rstrip()
        + "\nSupporting Signals:\n"
        + formatted
        + "\n"
    )
    
def extract_contradicting_patterns(
    sections: dict[str, ModuleSummary],
    primary: str | None,
    polarity: str,
) -> list[str]:
    candidates: list[tuple[str, float]] = []
    for s in sections.values():
        if not s or not s.pattern:
            continue
        score = float(s.score) if s.score is not None else 0.0
        # Skip weak suspicious signals, but keep benign signals
        if is_suspicious(s) and score < 0.30:
            continue
        # Skip same pattern
        if s.pattern == primary:
            continue
        # Contradiction logic
        if polarity == "suspicious" and is_benign(s):
            candidates.append((s.pattern, score))
        elif polarity == "benign" and is_suspicious(s):
            candidates.append((s.pattern, score))
    # Sort strongest first
    candidates.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in candidates[:2]]  # top 1–2 only

def append_contradicting_patterns(text: str, contradicting: list[str]) -> str:
    if not contradicting:
        return text
    formatted = "\n".join(f"- {humanize_signal(p)}" for p in contradicting)
    return (
        text.rstrip()
        + "\nContradicting Signals:\n"
        + formatted
        + "\n"
    )
    
def build_confidence_rationale(
    card,
    sections: dict[str, ModuleSummary],
    polarity: str,
    assessment: HypothesisAssessment | None = None,
    selection_reason: str | None = None,
) -> list[str]:
    """Explain the existing tier using scoped evidence, without recalculating it.

    The original positional arguments remain for callers. Aggregate scores and
    module counts cannot establish a mechanism or statistical independence.
    """
    reasons = [selection_reason] if selection_reason else []
    if assessment is not None and assessment.confidence_policy_rule:
        return reasons + list(assessment.confidence_rationale)
    if assessment is None:
        reasons.append("No hypothesis-scoped assessment was supplied; aggregate scores alone do not identify a mechanism.")
        return reasons
    explanations = {
        "synthetic_origin": "Confidence concerns generation-relevant evidence; unverified declarations do not authenticate origin.",
        "localized_editing": "Confidence concerns localized processing or reuse, not whether AI was used.",
        "camera_acquisition": "Confidence concerns acquisition compatibility, not image authenticity.",
        "unresolved_anomaly": "Observed anomalies do not establish synthetic origin or a specific editing mechanism.",
    }
    reasons.append(explanations[assessment.hypothesis_id])
    if not assessment.supporting_evidence:
        reasons.append("No direct supporting evidence is established for this hypothesis.")
    if assessment.contradicting_evidence:
        reasons.append("Contradicting observations challenge the assessed mechanism within the limits stated for each observation.")
    if assessment.moderating_evidence:
        reasons.append("Moderating observations qualify this hypothesis; they do not automatically establish or exclude a different origin.")
    if assessment.supporting_evidence:
        reasons.append("Multiple module outputs are not assumed to be statistically independent; support tiers are not probabilities.")
    return reasons


def append_confidence_rationale(text: str, reasons: list[str]) -> str:
    if not reasons:
        return text
    formatted = "\n".join(f"- {r}" for r in reasons)
    return (
        text.rstrip()
        + "\nConfidence Rationale:\n"
        + formatted
        + "\n"
    )

#---------------------------------------------------
# dataclasses supporting lineair reasoning routing
#---------------------------------------------------
@dataclass
class DecisionRouteTraceItem:
    route: str
    matched: bool
    reason: str | None = None
    pattern: str | None = None
    confidence: str | None = None
    polarity: str | None = None
    hypothesis_id: str | None = None
    selected: bool = False
    disposition: str | None = None
    legacy_confidence: str | None = None
    confidence_source: str | None = None

@dataclass
class DecisionEnv:
    sections: dict[str, ModuleSummary]
    ctx: Any
    ev: Any
    ds: Any
    card: Any
    dominant_pattern: str | None
    confidence_tier: str
    real_photo_context_prior: bool
    analysis_mode: str | None = None
    route_trace: list[DecisionRouteTraceItem] | None = None
    hypotheses: list[HypothesisAssessment] = field(default_factory=list)
    primary_hypothesis: str | None = None
    selection_reason: str | None = None
    corroboration_gates: list[dict] = field(default_factory=list)
    confidence_policy_results: list[ConfidencePolicyResult] = field(default_factory=list)
    coverage_limitations: tuple[str, ...] = ()

@dataclass(frozen=True)
class DecisionResult:
    pattern: str | None
    text: str
    confidence: str
    polarity: str
    branch: str
    debug_message: str | None = None
    finding: Finding = Finding.UNSPECIFIED

    @property
    def specificity(self):
        return finding_specificity(self.finding)
    
#---------------------------------------------------
# context info set into the GUI by analist
#---------------------------------------------------
def _contextual_support_notes(env: DecisionEnv) -> list[str]:
    notes: list[str] = []
    ds = env.ds
    ctx = env.ctx
    if ds.camera_like_support:
        notes.append(
            "low-level sensor-origin analysis remains broadly compatible with a camera-like base image"
        )
    if ds.cfa_camera_like_support:
        notes.append(
            "CFA / demosaicing structure remains broadly compatible with a camera-like acquisition pipeline"
        )
    if ds.metadata_camera_like:
        notes.append(
            "Metadata contains detailed camera-acquisition information consistent with a real photographic pipeline"
        )
    scene_bits: list[str] = []
    if ctx.natural_repetition:
        scene_bits.append("natural repetition")
    if ctx.decorative_geometric:
        scene_bits.append("decorative or geometric repetition")
    if ctx.smartphone_computational:
        scene_bits.append("smartphone computational photography")
    if ctx.screen_origin:
        scene_bits.append("possible screen/display-origin structure")
    if scene_bits:
        if len(scene_bits) == 1:
            notes.append(f"analyst-supplied scene context indicates {scene_bits[0]}")
        else:
            notes.append(
                "analyst-supplied scene context indicates "
                + ", ".join(scene_bits[:-1])
                + f", and {scene_bits[-1]}"
            )
    return notes

def enrich_text_with_context(env: DecisionEnv, base_text: str) -> str:
    notes = _contextual_support_notes(env)
    if not notes:
        return base_text
    return (
        base_text
        + "\nContextual factors moderate this interpretation: "
        + "; ".join(notes)
        + "."
    )

#-------------------------------------------------------
# decision support helpers 
#------------------------------------------------------
def _boundary_corroborated(env: DecisionEnv) -> bool:
    boundary_section = env.sections.get("boundary")
    boundary_focus_section = env.sections.get("boundary_focus")
    subject_boundary_section = env.sections.get("subject_boundary")
    segmentation_alignment_section = env.sections.get("segmentation_alignment")
    boundary_signal_strong = (
        boundary_section is not None
        and boundary_section.polarity == "suspicious"
        and boundary_section.status in {"medium", "strong"}
    )
    boundary_focus_strong = (
        boundary_focus_section is not None
        and boundary_focus_section.polarity == "suspicious"
        and boundary_focus_section.status in {"medium", "strong"}
    )
    subject_boundary_strong = (
        subject_boundary_section is not None
        and subject_boundary_section.polarity == "suspicious"
        and subject_boundary_section.status in {"medium", "strong"}
    )
    segmentation_alignment_supportive = (
        segmentation_alignment_section is not None
        and segmentation_alignment_section.polarity == "suspicious"
        and segmentation_alignment_section.status in {"medium", "strong"}
    )
    boundary_corroboration_count = sum([
        boundary_signal_strong,
        boundary_focus_strong,
        subject_boundary_strong,
        segmentation_alignment_supportive,
    ])
    boundary_specific_strength = 0.0
    for section in (boundary_focus_section, subject_boundary_section, boundary_section):
        if section is not None and section.score is not None:
            boundary_specific_strength = max(boundary_specific_strength, float(section.score))
    passed = (
        boundary_corroboration_count >= 2
        and boundary_specific_strength >= 0.45
    )
    check = evaluate_corroboration(
        env.sections, ['evidence:' + key for key, supported in (
            ('boundary', boundary_signal_strong), ('boundary_focus', boundary_focus_strong),
            ('subject_boundary', subject_boundary_strong), ('segmentation_alignment', segmentation_alignment_supportive),
        ) if supported],
        CorroborationRequirement('boundary.compound_support', 'localized_editing',
            RequirementKind.COMPOUND, minimum_indicators=2),
    )
    check.update(strength_requirement_satisfied=boundary_specific_strength >= 0.45,
        gate_passed=passed, production_condition_changed=False,
        interpretation='Related boundary checks establish compound spatial/processing agreement; they are not counted as separate independent measurement sources.')
    record_gate(env.corroboration_gates, check)
    return passed

def _photo_like_clean_signals(env: DecisionEnv) -> bool:
    ev = env.ev
    ds = env.ds
    ela_clean = ev.ela is None or ev.ela.pattern in {
        None,
        "ela_inconclusive",
        "ela_consistent",
    }
    noise_clean = ev.noise is None or ev.noise.pattern in {
        None,
        "noise_inconclusive",
        "noise_uniform_consistent",
    }
    cross_clean = ev.cross_signal is None or ev.cross_signal.pattern in {
        None,
        "no_meaningful_convergence",
    }
    boundary_clean = ev.boundary is None or ev.boundary.pattern in {
        None,
        "boundary_inconclusive",
        "no_boundary_convergence",
    }
    fft_clean = (
        ev.fft is None
        or (
            ev.fft.pattern in {
                None,
                "frequency_inconclusive",
                "organic_frequency_profile",
            }
            and ds.fft_score < 0.20
            and ds.peak_periodicity < 0.25
            and ds.peak_symmetry < 0.25
        )
    )
    patch_clean = ev.patch_similarity is None or ev.patch_similarity.pattern in {
        None,
        "localized_repetition_detected",
    }
    return (
        ela_clean
        and noise_clean
        and cross_clean
        and boundary_clean
        and fft_clean
        and ds.metadata_clean
        and patch_clean
    )

def build_decision_env(
    sections: dict[str, ModuleSummary],
    scene_context: dict | None = None,
    analysis_mode: str | None = None,
) -> DecisionEnv:
    ctx = build_context(scene_context)
    ev = build_evidence_snapshot(sections)
    try:
        ds = derive_signals(ev)
        card = compute_scorecard(sections, ctx, ev, ds)
        real_photo_context_prior = has_real_photo_context_prior(ctx, ev, ds)
        dominant_pattern = determine_dominant_pattern(sections)
    except ScorecardIntegrityError as exc:
        ds = DerivedSignals()
        card = ScoreCard(is_valid=False, validation_errors=[str(exc)], calculation={
            "calculation_version": "2a", "status": "invalid", "errors": [str(exc)],
        })
        dominant_pattern = "scorecard_invalid"
        real_photo_context_prior = False
    if card.camera_counter_support >= 2.5 and ds.local_signals_weak:
        dominant_pattern = "photo_like_consistency_supported"
    corroboration_gates = []
    confidence_tier = determine_confidence(card, sections, corroboration_gates=corroboration_gates) if card.is_valid else "Inconclusive"
    return DecisionEnv(
        sections=sections,
        ctx=ctx,
        ev=ev,
        ds=ds,
        card=card,
        dominant_pattern=dominant_pattern,
        confidence_tier=confidence_tier,
        real_photo_context_prior=real_photo_context_prior,
        analysis_mode=analysis_mode,
        route_trace=[],
        corroboration_gates=corroboration_gates,
    )

def finish_decision(
    env: DecisionEnv,
    result: DecisionResult,
    debug_lines: list[str] | None = None,
    debug: bool = False,
) -> tuple[str | None, str, str, str, dict]:
    if not env.confidence_policy_results:
        if not env.hypotheses:
            env.primary_hypothesis = 'unresolved_anomaly'
            env.hypotheses = [HypothesisAssessment(hypothesis_id='unresolved_anomaly', polarity=result.polarity)]
        result = _apply_confidence_policy(env, (), result)
    authoritative = {item.hypothesis:item for item in env.confidence_policy_results}
    for assessment in env.hypotheses:
        policy = authoritative[assessment.hypothesis_id]
        assessment.confidence_tier = policy.tier
        assessment.confidence_policy_rule = policy.policy_rule
        assessment.confidence_rationale = list(policy.rationale)
    primary_policy = next(h for h in env.hypotheses if h.hypothesis_id == env.primary_hypothesis)
    result = replace(result, confidence=primary_policy.confidence_tier)
    if debug:
        print("\n--- SYNTHESIS DEBUG REPORT ---")
        for line in debug_lines or []:
            print(line)
        print("--- END DEBUG REPORT ---\n")

    pattern = result.pattern
    polarity = result.polarity
    text = result.text
    primary = next((h for h in env.hypotheses if h.hypothesis_id == env.primary_hypothesis), None)
    if primary:
        text = append_hypothesis_evidence(text, primary)
        if primary.limitations:
            text = text.rstrip() + "\nEvidence Limitations:\n" + "\n".join(f"- {item}" for item in primary.limitations) + "\n"
    rationale = build_confidence_rationale(
        env.card, env.sections, polarity, assessment=primary, selection_reason=env.selection_reason,
    )
    text = append_confidence_rationale(text, rationale)
    text = text.strip() + "\n"
    for assessment in env.hypotheses:
        text += (
            f"\n{assessment.hypothesis_id}: {assessment.confidence_tier} "
            f"({assessment.polarity}). {assessment.explanation}\n"
        )
        text = append_hypothesis_evidence(text, assessment)
        if assessment.limitations:
            text += "Limitations: " + " ".join(assessment.limitations) + "\n"
        if assessment.confidence_policy_rule:
            text += "Confidence policy rule: " + assessment.confidence_policy_rule + "\n"
    reasoning_trace = _build_reasoning_trace(
        sections=env.sections,
        ctx=env.ctx,
        ev=env.ev,
        ds=env.ds,
        card=env.card,
        dominant_pattern=pattern,
        confidence_tier=result.confidence,
        polarity=polarity,
        overall_text=text,
        decision_branch=result.branch,
        analysis_mode=env.analysis_mode,
        contextual_priors={"real_photo_context_prior": bool(env.real_photo_context_prior)},
        route_trace=env.route_trace,
        hypotheses=env.hypotheses,
        primary_hypothesis=env.primary_hypothesis,
        selection_reason=env.selection_reason,
        confidence_rationale=rationale,
        corroboration_gates=env.corroboration_gates,
        confidence_policy_results=env.confidence_policy_results,
    )
    return (pattern, text, result.confidence, polarity, reasoning_trace)

#----------------------------------------------------------------
# decision braches turned into routes
#----------------------------------------------------------------
def route_real_photo_context_prior(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.real_photo_context_prior
        and not env.ds.metadata_synthetic
        and env.card.synthetic_boost <= 0.25
    ):
        return DecisionResult(
            "camera_supported_computational_photo_ambiguity",
            "Camera metadata and analyst-supplied smartphone computational-photography context strongly support a real photographic workflow. "
            "Some forensic irregularities remain, but these are plausibly explained by modern smartphone processing, segmentation, compression, or scene geometry rather than by synthetic generation or compositing.",
            "Medium",
            "neutral",
            "real_photo_context_moderates_suspicion",
            finding=Finding.PHOTO_CONTEXT,
        )
    return None

def route_boundary_support_limited(env: DecisionEnv) -> DecisionResult | None:
    if env.ds.strong_local_edit and env.ds.boundary_reliability_score < 0.6:
        return DecisionResult(
            "localized_processing_inconclusive",
            "Boundary-focused processing signals are present, but boundary support is too limited "
            "or insufficiently reliable to justify a strong foreground/background mismatch conclusion.",
            "Medium",
            "neutral",
            "boundary_support_limited_localized_processing",
            finding=Finding.BOUNDARY_LIMITED,
        )
    return None

def route_region_geometry_unreliable(env: DecisionEnv) -> DecisionResult | None:
    if env.ds.region_geometry_unreliable and env.ds.strong_local_edit:
        return DecisionResult(
            "localized_processing_inconclusive",
            "Boundary-focused and foreground/background processing signals are present, "
            "but the region geometry used by subject/boundary analysis is unreliable. "
            "Because the subject/background split is not stable enough, the system avoids "
            "a strong compositing or foreground/background mismatch conclusion.",
            "Medium",
            "neutral",
            "region_geometry_unreliable_localized_processing",
            finding=Finding.GEOMETRY_LIMITED,
        )
    return None

def route_localized_multi_mechanism(env: DecisionEnv) -> DecisionResult | None:
    score_gap = abs(env.card.local_edit_support_score - env.card.clone_support_score)
    if (
        env.card.local_edit_support_score >= 3.0
        and env.card.clone_support_score >= 3.0
        and score_gap < 1.0
        and not env.card.contextual_false_positive_risk
    ):
        return DecisionResult(
            "localized_editing_multi_mechanism",
            enrich_text_with_context(
                env,
                "Strong evidence of localized editing is present. "
                "Both duplicated local content and localized foreground/background inconsistency "
                "contribute meaningfully to the forensic reading."
            ),
            "High",
            "suspicious",
            "localized_editing_multi_mechanism",
            "DECISION: localized_editing_multi_mechanism",
            finding=Finding.MULTI_LOCAL,
        )
    return None

def route_strong_local_edit(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.card.local_edit_support_score >= 3.5
        and env.card.local_edit_support_score >= env.card.clone_support_score + 1.0
        and env.card.camera_counter_support < 2.0
        and not env.card.contextual_false_positive_risk
    ):
        if _boundary_corroborated(env):
            return DecisionResult(
                "possible_foreground_background_processing_mismatch",
                enrich_text_with_context(
                    env,
                    "Strong evidence of localized compositing or subject-level editing. "
                    "Boundary-focused forensic signals indicate inconsistent processing "
                    "between foreground and background regions."
                ),
                "High",
                "suspicious",
                "possible_foreground_background_processing_mismatch",
                "DECISION: possible_foreground_background_processing_mismatch",
                finding=Finding.BOUNDARY_DECISIVE,
            )
        confidence = "Low" if env.card.camera_counter_support else "Medium"
        polarity = "neutral" if env.card.camera_counter_support else "suspicious"
        return DecisionResult(
            "localized_processing_inconclusive",
            enrich_text_with_context(
                env,
                "Several localized forensic signals are present, but boundary-focused corroboration is mixed "
                "and camera-acquisition evidence moderates the interpretation. The result is best treated as "
                "localized differential processing that remains inconclusive rather than as a specific editing or compositing finding."
            ),
            confidence,
            polarity,
            "localized_processing_inconclusive",
            "DECISION: localized_processing_inconclusive",
            finding=Finding.LOCAL_UNCERTAIN,
        )
    return None

def route_clone_reuse(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.card.clone_support_score >= 3.5
        and env.card.clone_support_score >= env.card.local_edit_support_score + 1.0
        and env.card.camera_counter_support < 2.0
    ):
        return DecisionResult(
            "possible_clone_reuse",
            "Strong evidence of duplicated local content or copy-move style reuse. "
            "Patch similarity reveals highly similar spatially separated regions, "
            "and the broader evidence is more consistent with localized duplication "
            "than with a broader foreground/background edit.",
            "High",
            "suspicious",
            "possible_clone_reuse",
            "DECISION: possible_clone_reuse",
            finding=Finding.CLONE_DECISIVE,
        )
    return None

def route_moderated_local_edit(env: DecisionEnv) -> DecisionResult | None:
    dominant_localized_score = max(
        env.card.local_edit_support_score,
        env.card.clone_support_score,
    )
    if env.ds.strong_local_edit and dominant_localized_score >= 2.5:
        if _boundary_corroborated(env):
            return DecisionResult(
                "possible_foreground_background_processing_mismatch",
                enrich_text_with_context(
                    env,
                    "Boundary-focused signals indicate a foreground/background transition anomaly, "
                    "but the broader evidence is not sufficient for a fully decisive localized-edit conclusion."
                ),
                "Medium",
                "suspicious",
                "possible_foreground_background_processing_mismatch_moderated",
                "DECISION: possible_foreground_background_processing_mismatch (moderated)",
                finding=Finding.BOUNDARY_SUPPORTED,
            )
        return DecisionResult(
            "localized_editing_inconclusive",
            enrich_text_with_context(
                env,
                "Localized suspicious signals are present, but boundary-focused corroboration remains mixed. "
                "This supports a cautious localized-editing concern rather than a specific foreground/background mismatch conclusion."
            ),
            "Low",
            "suspicious",
            "localized_editing_inconclusive",
            "DECISION: localized_editing_inconclusive",
            finding=Finding.LOCAL_WEAK,
        )
    return None

def route_clone_ambiguous(env: DecisionEnv) -> DecisionResult | None:
    if env.card.clone_ambiguous and env.card.clone_support_score >= 2.0:
        if env.card.camera_counter_support >= 1.5:
            return DecisionResult(
                "structured_recurrence_inconclusive",
                "Repeated structures are present, but camera-acquisition metadata and other benign signals make a clone-based explanation less likely.",
                "Low",
                "neutral",
                "clone_ambiguous → camera counterforce override",
                "DECISION: clone_ambiguous → camera counterforce override",
                finding=Finding.CLONE_CAMERA_AMBIGUOUS,
            )
        if env.ds.material_realism_strong:
            return DecisionResult(
                env.dominant_pattern,
                "Repeated structures are present, but subject-level material analysis suggests synthetic generation rather than direct clone reuse.",
                env.confidence_tier,
                "neutral",
                "clone_ambiguous → realism override",
                "DECISION: clone_ambiguous → realism override",
                finding=Finding.CLONE_MATERIAL_AMBIGUOUS,
            )
        return DecisionResult(
            "possible_clone_reuse",
            "Patch similarity reveals highly similar spatially separated regions, but the current evidence is insufficient to exclude natural scene repetition.",
            "Medium",
            "neutral",
            "possible_clone_reuse (ambiguous)",
            "DECISION: possible_clone_reuse (ambiguous)",
            finding=Finding.CLONE_AMBIGUOUS,
        )
    return None

def route_structured_recurrence_inconclusive(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.ds.fft_structured
        and env.ds.patch_structured
        and env.ds.local_signals_weak
        and env.ds.provenance_clean
        and env.ds.coverage_ratio >= 0.18
        and (
            env.ds.camera_like_support
            or env.ctx.decorative_geometric
            or env.ctx.natural_repetition
            or env.ctx.smartphone_computational
            or env.ctx.screen_origin
        )
    ):
        return DecisionResult(
            "structured_recurrence_inconclusive",
            "Structured recurrence is present, but the current evidence is insufficient "
            "to distinguish real-scene repetition from synthetic recurrence. "
            "Global frequency and patch structure are notable, yet localized forensic "
            "inconsistency remains weak or inconclusive.",
            "Medium",
            "neutral",
            "structured_recurrence_inconclusive",
            "DECISION: structured_recurrence_inconclusive",
            finding=Finding.RECURRENCE_CAUTION,
        )
    return None

def route_synthetic_multi_signal(env: DecisionEnv) -> DecisionResult | None:
    # These are compound patterns / accumulation, not separate-source tests.
    for gate_id, keys, matched, kind in (
        ('synthetic.fft_patch_compound', [('fft', env.ds.fft_structured), ('patch_similarity', env.ds.patch_structured)],
            env.ds.fft_structured and env.ds.patch_structured, RequirementKind.COMPOUND),
        ('synthetic.material_asymmetry_compound', [('subject_material_realism', env.ds.material_realism_strong), ('subject_process_asymmetry', env.ds.subject_process_asymmetry_strong)],
            env.ds.material_realism_strong and env.ds.subject_process_asymmetry_strong and not env.ds.region_geometry_unreliable, RequirementKind.COMPOUND),
        ('synthetic.additional_support_flag', [('metadata', env.ds.metadata_synthetic), ('osint', env.ds.osint_ai_context), ('subject_material_realism', env.ds.material_realism_strong)],
            env.card.synthetic_supported_by_other_domains, RequirementKind.ACCUMULATION),
    ):
        check = evaluate_corroboration(env.sections, ['evidence:' + key for key, active in keys if active],
            CorroborationRequirement(gate_id, 'synthetic_origin', kind, minimum_indicators=2 if kind == RequirementKind.COMPOUND else 1))
        check.update(gate_passed=bool(matched), production_condition_changed=False,
            interpretation='Existing compound/accumulation predicate retained; no claim of independent corroboration.')
        record_gate(env.corroboration_gates, check)
    if (
        env.card.synthetic_boost >= 1.0
        and env.card.suspicious_score >= 5.0
        and env.card.synthetic_supported_by_other_domains
        # Localized anomalies alone do not identify synthetic generation.
        and (
            (env.ds.fft_structured and env.ds.patch_structured)
            or (env.ds.material_realism_strong and env.ds.subject_process_asymmetry_strong
                and not env.ds.region_geometry_unreliable)
        )
        and not (
            env.ds.local_signals_weak
            and env.ds.provenance_clean
            and env.ds.coverage_ratio >= 0.18
        )
    ):
        pattern = "synthetic_multi_signal_convergence"
        return DecisionResult(
            pattern,
            "Multiple visual signals support synthetic or decoder-mediated structure. This is heuristic support, not proof of generation or a probability.",
            "High",
            "suspicious",
            "synthetic_multi_signal_convergence",
            "DECISION: synthetic_multi_signal_convergence",
            finding=Finding.VISUAL_GENERATION,
        )
    return None

def route_localized_processing(env: DecisionEnv) -> DecisionResult | None:
    if env.card.edit_boost >= 0.50 and env.card.suspicious_score >= 4.5:
        return DecisionResult(
            "localized_processing_inconclusive",
            enrich_text_with_context(
                env,
                "Moderate evidence of localized differential processing. "
                "Boundary-focused and cross-signal analysis support a region-specific "
                "editing or compositing interpretation."
            ),
            "Medium",
            "neutral",
            "localized_processing_inconclusive",
            "DECISION: localized_processing_inconclusive",
            finding=Finding.LOCAL_PROCESSING,
        )
    return None

def route_subject_boundary(env: DecisionEnv) -> DecisionResult | None:
    if env.ds.subject_boundary_strong and env.card.suspicious_score >= 4.0:
        return DecisionResult(
            "possible_subject_background_segmentation_artifact",
            "Moderate evidence of subject/background segmentation or replacement artifacts."
            "Boundary-transition analysis indicates an implausible cutout-style transition, "
            "with supporting structural context from other signals.",
            "Medium",
            "suspicious",
            "possible_subject_background_segmentation_artifact",
            "DECISION: possible_subject_background_segmentation_artifact",
            finding=Finding.SUBJECT_BOUNDARY,
        )
    return None

def route_unreliable_boundary_context(env: DecisionEnv) -> DecisionResult | None:
    if (
        not env.ds.person_mask_reliable
        and env.ds.boundary_reliability_score <= 0.10
        and env.dominant_pattern in {
            "possible_boundary_transition_inconsistency",
            "possible_subject_background_segmentation_artifact",
            "possible_foreground_background_processing_mismatch",
        }
    ):
        return DecisionResult(
            "localized_processing_inconclusive",
            "Boundary-transition and subject/background signals are present, but the person mask and boundary support are not reliable enough to sustain a strong boundary-based interpretation. "
            "Analyst-supplied context indicates decorative/geometric repetition and smartphone computational photography, while metadata and camera-pipeline signals support a real photographic workflow. "
            "The result is therefore treated as localized-processing ambiguity rather than evidence of compositing.",
            "Medium",
            "neutral",
            "boundary_evidence_unreliable_context_moderated",
            finding=Finding.UNRELIABLE_BOUNDARY,
        )
    return None

def route_boundary_transition(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.ds.subject_boundary_medium
        and env.card.suspicious_score >= 3.5
        and (env.ds.fragmented_local_edit or env.ds.strong_cross or env.ds.patch_structured)
    ):
        return DecisionResult(
            "possible_boundary_transition_inconsistency",
            "Some evidence of subject/background transition inconsistency is present. "
            "Boundary-transition analysis suggests a potentially implausible cutout or "
            "replacement boundary, but the evidence remains moderate rather than decisive.",
            "Medium",
            "suspicious",
            "possible_boundary_transition_inconsistency",
            "DECISION: possible_boundary_transition_inconsistency",
            finding=Finding.BOUNDARY_TRANSITION,
        )
    return None

def route_provenance(env: DecisionEnv) -> DecisionResult | None:
    state = metadata_provenance_state(env.ev.metadata)
    if state == ProvenanceState.UNVERIFIED_GENERATION_DECLARATION:
        return DecisionResult(
            "provenance_supported_synthetic_context",
            "Metadata contains an explicit generation declaration supporting synthetic or AI-mediated creation. "
            "Metadata authenticity is unverified. This finding does not establish a localized editing mechanism.",
            "Medium",
            "suspicious",
            "provenance_supported_synthetic_context",
            "DECISION: provenance_supported_synthetic_context",
            finding=Finding.GENERATION_DECLARATION,
        )
    if state == ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION:
        return DecisionResult(
            "provenance_supported_enhancement_context",
            "Metadata declares enhancement or generative editing; metadata authenticity is unverified. "
            "This supports a declared processing context, not whole-image synthetic generation or a specific localized mechanism.",
            "Medium", "suspicious", "provenance_supported_enhancement_context",
            finding=Finding.ENHANCEMENT_DECLARATION,
        )
    if env.ds.osint_ai_context:
        return DecisionResult(
            "provenance_supported_synthetic_context",
            "An AI-gallery source provides contextual support for synthetic origin. "
            "Source context does not authenticate this image's creation history.",
            "Low", "suspicious", "osint_synthetic_context",
            finding=Finding.SOURCE_CONTEXT,
        )
    return None

def route_camera_like(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.ds.camera_like_support
        and env.ds.provenance_clean
        and env.ds.local_signals_weak
        and env.card.suspicious_score < 4.0
    ):
        pattern = (
            env.dominant_pattern
            if env.dominant_pattern == "photo_like_consistency_supported"
            else "camera_like_acquisition_supported"
        )
        return DecisionResult(
            pattern,
            "Camera-like acquisition signals are compatible with a photographic workflow, with no strong localized forensic inconsistency dominating the assessment. This is not proof of authenticity.",
            "Medium",
            "benign",
            pattern,
            "DECISION: camera_like_acquisition_supported",
            finding=Finding.CAMERA_COMPATIBLE,
        )
    return None

def route_multi_signal_suspicious(env: DecisionEnv) -> DecisionResult | None:
    high_support_present = (
        env.ds.metadata_synthetic
        or env.ds.osint_ai_context
        or env.ds.strong_cross
        or env.ds.subject_boundary_strong
        or env.ds.compression_inconsistency
    )
    if (
        env.card.suspicious_score >= 7.0
        and high_support_present
        and not env.ds.local_signals_weak
        and not (
            env.ds.camera_like_support
            or env.ctx.natural_repetition
            or env.ctx.decorative_geometric
            or env.ctx.smartphone_computational
            or env.ctx.screen_origin
        )
    ):
        return DecisionResult(
            "multi_signal_suspicious_convergence",
            "Multiple suspicious indicators converge across forensic checks that may be correlated. "
            "The current analysis supports a strong anomalous reading, although the exact "
            "mechanism is not singularly determined.",
            "High",
            "suspicious",
            "multi_signal_suspicious_convergence",
            "DECISION: multi_signal_suspicious_convergence",
            finding=Finding.ANOMALY_ACCUMULATION,
        )
    return None

def route_moderate_suspicious(env: DecisionEnv) -> DecisionResult | None:
    if env.card.suspicious_score >= 3.5:
        return DecisionResult(
            "moderate_suspicious_convergence",
            enrich_text_with_context(
                env,
                "Multiple suspicious indicators are present across the current forensic reading, "
                "but the evidence does not converge strongly enough for a narrower high-confidence interpretation. "
                "A specific generation or localized editing mechanism is not established."
            ),
            env.confidence_tier,
            "suspicious",
            "moderate_suspicious_convergence",
            finding=Finding.GENERAL_ANOMALY,
        )
    return None

def route_photo_like_consistency(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.card.suspicious_score < 1.5
        and env.card.benign_score >= 2.0
        and _photo_like_clean_signals(env)
    ):
        return DecisionResult(
            "photo_like_consistency_supported",
            "The current analysis supports a coherent photo-like reading. "
            "Across metadata, local forensic checks, boundary structure, frequency analysis, "
            "patch inspection, sensor-origin analysis, and compression-history analysis, "
            "no strong artificial signature dominates.",
            "Medium",
            "benign",
            "photo_like_consistency_supported",
            "DECISION: photo_like_consistency_supported",
            finding=Finding.PHOTO_CONSISTENCY,
        )
    return None

def route_fallback(env: DecisionEnv) -> DecisionResult:
    fallback_pattern = (
        env.dominant_pattern
        or determine_dominant_pattern(env.sections)
        or "inconclusive"
    )
    fallback_polarity = "suspicious" if env.card.suspicious_score > 2.5 else "neutral"
    fallback_confidence = env.confidence_tier or "Low"
    return DecisionResult(
        pattern=fallback_pattern,
        text=enrich_text_with_context(
            env,
            "The available evidence does not establish a specific origin or editing mechanism. "
            "This fallback preserves uncertainty and does not establish an alternative explanation."
        ),
        confidence=fallback_confidence,
        polarity=fallback_polarity,
        branch="helper_driven_fallback",
        debug_message="DECISION: helper_driven_fallback",
        finding=Finding.FALLBACK,
    )

@dataclass(frozen=True)
class DecisionRoute:
    evaluate: Callable[[DecisionEnv], DecisionResult | None]
    hypothesis_id: str
    priority: int
    boundary_safeguard: bool = False


# Priority expresses specificity *within* a hypothesis, not evaluation order.
# Boundary safeguards constrain boundary mechanisms, never metadata or clone reuse.
DECISION_ROUTES = (
    DecisionRoute(route_real_photo_context_prior, "localized_editing", 0, True),
    DecisionRoute(route_boundary_support_limited, "localized_editing", 1, True),
    DecisionRoute(route_region_geometry_unreliable, "localized_editing", 2, True),
    DecisionRoute(route_unreliable_boundary_context, "localized_editing", 3, True),
    DecisionRoute(route_localized_multi_mechanism, "localized_editing", 10),
    DecisionRoute(route_strong_local_edit, "localized_editing", 20),
    DecisionRoute(route_clone_reuse, "localized_editing", 30),
    DecisionRoute(route_moderated_local_edit, "localized_editing", 40),
    DecisionRoute(route_clone_ambiguous, "localized_editing", 50),
    DecisionRoute(route_localized_processing, "localized_editing", 60),
    DecisionRoute(route_subject_boundary, "localized_editing", 70),
    DecisionRoute(route_boundary_transition, "localized_editing", 80),
    DecisionRoute(route_structured_recurrence_inconclusive, "synthetic_origin", 0),
    DecisionRoute(route_synthetic_multi_signal, "synthetic_origin", 10),
    DecisionRoute(route_provenance, "synthetic_origin", 20),
    DecisionRoute(route_camera_like, "camera_acquisition", 10),
    DecisionRoute(route_photo_like_consistency, "camera_acquisition", 20),
    DecisionRoute(route_multi_signal_suspicious, "unresolved_anomaly", 10),
    DecisionRoute(route_moderate_suspicious, "unresolved_anomaly", 20),
    DecisionRoute(route_fallback, "unresolved_anomaly", 100),
)


def _specific_finding(result: DecisionResult | None) -> bool:
    return bool(result and result.polarity == "suspicious"
                and result.specificity in {Specificity.SPECIFIC, Specificity.DECISIVE})


def _apply_confidence_policy(env, candidates, selected):
    findings = {}
    for spec, result in candidates:
        findings.setdefault(spec.hypothesis_id, []).append(result.finding)
    facts = snapshot_confidence_facts(env.sections, env.card, env.ds, env.corroboration_gates, findings,
        coverage=env.coverage_limitations)
    policy_results = []
    for assessment in env.hypotheses:
        policy = evaluate_confidence(AssessmentEvidence.from_assessment(assessment), facts)
        assessment.confidence_tier = policy.tier
        assessment.confidence_policy_rule = policy.policy_rule
        assessment.confidence_rationale = list(policy.rationale)
        assessment.limitations = list(policy.reliability_limitations)
        policy_results.append(policy)
    env.confidence_policy_results = policy_results
    by_hypothesis = {item.hypothesis:item for item in policy_results}
    for item in env.route_trace or []:
        if item.matched:
            item.legacy_confidence = item.confidence
            policy = by_hypothesis.get(item.hypothesis_id)
            item.confidence = policy.tier if policy else None
            item.confidence_source = policy.policy_rule if policy else 'legacy_alternative_not_assessed'
    return replace(selected, confidence=by_hypothesis[env.primary_hypothesis].tier)


def evaluate_hypotheses(env: DecisionEnv, routes=None) -> DecisionResult:
    """Evaluate every candidate, then apply scoped safeguards and synthesis rules."""
    # Retain the confidence gate that established env.confidence_tier; rebuild
    # candidate-specific audits so a reused environment cannot retain old gates.
    env.corroboration_gates[:] = [entry for entry in env.corroboration_gates
        if entry['gate_id'] == 'confidence.strong_source_diversity']
    env.confidence_policy_results = []
    if not env.card.is_valid:
        explanation = "Scorecard calculation is invalid; a forensic conclusion is withheld. " + "; ".join(env.card.validation_errors)
        env.primary_hypothesis = "unresolved_anomaly"
        env.selection_reason = explanation
        env.route_trace = []
        env.hypotheses = [HypothesisAssessment(
            hypothesis_id=name, explanation="Assessment withheld because scorecard integrity failed.",
            limitations=list(env.card.validation_errors), decision_branch="scorecard_integrity_failure",
        ) for name in ("synthetic_origin", "localized_editing", "camera_acquisition", "unresolved_anomaly")]
        return _apply_confidence_policy(env, (), DecisionResult("scorecard_invalid", explanation, "Inconclusive", "neutral", "scorecard_integrity_failure", finding=Finding.INVALID))
    candidates: list[tuple[DecisionRoute, DecisionResult]] = []
    env.route_trace = []
    for spec in DECISION_ROUTES if routes is None else routes:
        result = spec.evaluate(env)
        env.route_trace.append(DecisionRouteTraceItem(
            route=spec.evaluate.__name__, matched=result is not None,
            reason=(result.debug_message or result.text) if result else "condition_not_met",
            pattern=result.pattern if result else None,
            confidence=result.confidence if result else None,
            polarity=result.polarity if result else None,
            hypothesis_id=spec.hypothesis_id,
        ))
        if result:
            candidates.append((spec, result))
    candidates.sort(key=lambda pair: (pair[0].priority, pair[0].evaluate.__name__))

    def group(name):
        return [(spec, result) for spec, result in candidates if spec.hypothesis_id == name]

    local = group("localized_editing")
    safeguards = [(s, r) for s, r in local if s.boundary_safeguard]
    if safeguards:
        clone_specific = [(s, r) for s, r in local if s.evaluate == route_clone_reuse]
        local_choice = (clone_specific or safeguards)[0]
    else:
        local_choice = local[0] if local else None
    synthetic = group("synthetic_origin")
    # A recurrence caveat constrains visual recurrence, not a declaration.
    declarations = [(s, r) for s, r in synthetic if s.evaluate == route_provenance]
    visual = [(s, r) for s, r in synthetic if s.evaluate == route_synthetic_multi_signal]
    recurrence_caution = any(s.evaluate == route_structured_recurrence_inconclusive for s, _ in synthetic)
    synthetic_choice = ((visual if not recurrence_caution else []) or declarations or synthetic or [None])[0]
    local_result = local_choice[1] if local_choice else None
    synthetic_result = synthetic_choice[1] if synthetic_choice else None

    # Evidence of a specific local mechanism has priority over unverified metadata;
    # supported visual generation can lead when local corroboration is weaker.
    if _specific_finding(local_result) and local_result.specificity == Specificity.DECISIVE:
        chosen = local_choice
        why = "Corroborated localized-mechanism evidence leads; generation evidence is assessed separately."
    elif _specific_finding(synthetic_result) and synthetic_choice[0].evaluate == route_synthetic_multi_signal:
        chosen = synthetic_choice
        why = "Generation-relevant visual convergence leads; localized-mechanism uncertainty is scoped to localized editing."
    elif _specific_finding(local_result):
        chosen = local_choice
        why = "A supported localized mechanism leads over unverified generation context; neither establishes the other."
    elif _specific_finding(synthetic_result):
        chosen = synthetic_choice
        why = "An explicit unverified declaration supports AI-mediated creation without requiring a conclusive localized-editing result."
    elif local_choice:
        chosen = local_choice
        why = "Localized evidence remains limited by its own corroboration or reliability safeguards."
    elif synthetic_choice:
        chosen = synthetic_choice
        why = "Generation-related evidence remains contextual or inconclusive; no specific localized mechanism is established."
    else:
        camera = group("camera_acquisition")
        general = group("unresolved_anomaly")
        anomaly = [(s, r) for s, r in general if s.evaluate != route_fallback]
        chosen = (anomaly or camera or general)[0]
        why = ("General anomalies do not identify AI generation or a localized mechanism."
               if anomaly else "Camera compatibility or an inconclusive fallback is retained without inferring authenticity.")

    camera_ids = []
    if env.ds.camera_like_support:
        camera_ids.append("sensor_origin:camera_like_acquisition_supported")
    if env.ds.cfa_camera_like_support:
        camera_ids.append("cfa_demosaic:camera_like_cfa_supported")
    if env.ds.metadata_camera_like:
        camera_ids.append("metadata:camera_metadata_present")
    synthetic_limits = ["Heuristic support levels are not probabilities."]
    if env.ds.region_geometry_unreliable:
        synthetic_limits.append("Unreliable subject-region geometry limits region-dependent visual generation evidence.")
    if declarations or metadata_provenance_state(env.ev.metadata) != ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE:
        synthetic_limits.append("Metadata authenticity is unverified; C2PA presence alone is not validation.")
    if env.ds.metadata_enhancement:
        synthetic_limits.append("Enhancement declarations do not establish whole-image synthetic origin.")
    if env.ds.metadata_missing:
        synthetic_limits.append("Missing provenance coverage is a limitation, not positive generation evidence.")
    if not (visual or env.ds.metadata_synthetic or env.ds.metadata_enhancement or env.ds.osint_ai_context):
        synthetic_limits.append("No substantive generation declaration or specific visual generation finding is established.")
    local_limits = ["Localized editing evidence does not by itself establish AI generation."]
    boundary_observed = any(
        s is not None and s.status != "not_run" and s.pattern
        for key in ("boundary", "boundary_focus", "subject_boundary", "region_masks")
        for s in (env.sections.get(key),)
    )
    if boundary_observed and env.ds.boundary_reliability_score < 1.0:
        local_limits.append(f"Boundary reliability is reduced ({env.ds.boundary_reliability_score:.2f}).")
    if env.ds.region_geometry_unreliable:
        local_limits.append("Subject/background region geometry is unreliable.")
    if local_result and "inconclusive" in (local_result.pattern or ""):
        local_limits.append("Localized-mechanism corroboration remains inconclusive.")

    env.hypotheses = [
        HypothesisAssessment(
            hypothesis_id="synthetic_origin",
            polarity=synthetic_result.polarity if synthetic_result else "neutral",
            confidence_tier="Inconclusive",  # Placeholder until scoped policy evaluation.
            limitations=synthetic_limits,
            decision_branch=synthetic_result.branch if synthetic_result else None,
            explanation=synthetic_result.text if synthetic_result else "Synthetic origin is not established by the available evidence.",
        ),
        HypothesisAssessment(
            hypothesis_id="localized_editing",
            polarity=local_result.polarity if local_result else "neutral",
            confidence_tier="Inconclusive",
            limitations=local_limits,
            decision_branch=local_result.branch if local_result else None,
            explanation=local_result.text if local_result else "A specific localized-editing mechanism is not established.",
        ),
        HypothesisAssessment(
            hypothesis_id="camera_acquisition", polarity="benign" if camera_ids else "neutral",
            confidence_tier="Inconclusive",
            limitations=["Camera compatibility does not authenticate an image and may coexist with synthetic creation or later editing."],
            decision_branch="camera_acquisition_compatibility" if camera_ids else None,
            explanation="Camera-like acquisition evidence is present." if camera_ids else "Camera acquisition is not established.",
        ),
    ]
    if chosen[0].hypothesis_id == "unresolved_anomaly":
        env.hypotheses.append(HypothesisAssessment(
            hypothesis_id="unresolved_anomaly", polarity=chosen[1].polarity,
            confidence_tier="Inconclusive", decision_branch=chosen[1].branch,
            explanation=chosen[1].text,
            limitations=["An unresolved anomaly is not evidence of a particular origin or editing mechanism."],
        ))
    elif chosen[0].hypothesis_id == "camera_acquisition":
        camera_assessment = env.hypotheses[2]
        camera_assessment.polarity = chosen[1].polarity
        camera_assessment.decision_branch = chosen[1].branch
        camera_assessment.explanation = chosen[1].text
        if not camera_ids:
            camera_assessment.limitations.append(
                "No direct camera-acquisition evidence was established; the overall reading concerns photo-like consistency only."
            )
    scope_hypothesis_evidence(
        env.sections, env.hypotheses, visual_generation=bool(visual) and not recurrence_caution,
        boundary_mechanism=bool(local_choice and local_choice[0].evaluate in {
            route_real_photo_context_prior, route_boundary_support_limited,
            route_region_geometry_unreliable, route_unreliable_boundary_context,
            route_localized_multi_mechanism, route_strong_local_edit,
            route_moderated_local_edit, route_localized_processing,
            route_subject_boundary, route_boundary_transition,
        }),
    )
    env.primary_hypothesis = chosen[0].hypothesis_id
    env.selection_reason = why
    for item in env.route_trace:
        item.selected = item.route == chosen[0].evaluate.__name__
        if item.matched:
            item.disposition = ("selected_overall" if item.selected else
                                "selected_for_hypothesis" if item.route in {
                                    local_choice[0].evaluate.__name__ if local_choice else "",
                                    synthetic_choice[0].evaluate.__name__ if synthetic_choice else "",
                                } else "alternative_candidate; scoped safeguards and specificity rules apply")
    return _apply_confidence_policy(env, candidates, chosen[1])


def synthesize_overall(
    sections: dict[str, ModuleSummary], 
    scene_context: dict | None = None, 
    debug: bool = False, 
    analysis_mode: str | None = None,
    *,
    evidence_dependency_shadow: bool = False,
    analysis_coverage: dict | None = None,
    ) -> tuple[str | None, str, str, str, dict]:
    """
    Overall synthesis, returns: overall_pattern, overall_text, overall_confidence, overall_polarity, decision
    This module is intentionally the decision layer only.
    Score computation and evidence normalization live in hypothesis_engine.py.
    """
    env = build_decision_env(
        sections=sections,
        scene_context=scene_context,
        analysis_mode=analysis_mode,
    )
    env.coverage_limitations = coverage_limitations(analysis_coverage)
    if env.card.is_valid:
        base_suspicious_score, base_benign_score, suspicious_domains, benign_domains = compute_base_scores(sections)
    else:
        base_suspicious_score, base_benign_score, suspicious_domains, benign_domains = 0.0, 0.0, set(), set()
    debug_lines: list[str] = [
        f"camera_like_support={env.ds.camera_like_support}",
        f"sensor_trace_inconsistency={env.ds.sensor_trace_inconsistency}",
        f"compression_consistent={env.ds.compression_consistent}",
        f"compression_inconsistency={env.ds.compression_inconsistency}",
        f"fft_structured={env.ds.fft_structured}, patch_structured={env.ds.patch_structured}",
        f"local_signals_weak={env.ds.local_signals_weak}, provenance_clean={env.ds.provenance_clean}",
        f"strong_local_edit={env.ds.strong_local_edit}",
        f"fragmented_local_edit={env.ds.fragmented_local_edit}",
        f"strong_cross={env.ds.strong_cross}",
        f"boundary_pattern={env.ev.boundary.pattern if env.ev.boundary else None}",
        f"cross_signal_pattern={env.ev.cross_signal.pattern if env.ev.cross_signal else None}",
        f"sensor_origin_pattern={env.ev.sensor_origin.pattern if env.ev.sensor_origin else None}",
        f"local_edit_support_score={env.card.local_edit_support_score:.2f}",
        f"clone_support_score={env.card.clone_support_score:.2f}",
        f"contextual_false_positive_risk={env.card.contextual_false_positive_risk}",
        f"initial suspicious_score={base_suspicious_score:.2f}",
        f"initial benign_score={base_benign_score:.2f}",
        f"suspicious_domains={sorted(suspicious_domains)}",
        f"benign_domains={sorted(benign_domains)}",
        f"synthetic_boost(raw/damped)={env.card.synthetic_boost:.2f}",
        f"edit_boost={env.card.edit_boost:.2f}",
        f"provenance_boost={env.card.provenance_boost:.2f}",
        f"sensor_boost={env.card.sensor_boost:.2f}",
        f"compression_boost={env.card.compression_boost:.2f}",
        f"caution_penalty={env.card.caution_penalty:.2f}",
        f"final suspicious_score={env.card.suspicious_score:.2f}",
    ]
    result = evaluate_hypotheses(env)
    debug_lines.append(f"PRIMARY HYPOTHESIS: {env.primary_hypothesis}")
    debug_lines.append(f"SELECTION: {env.selection_reason}")
    finished = finish_decision(env, result, debug_lines=debug_lines, debug=debug)
    if evidence_dependency_shadow:
        from evidence_dependency_analysis import safe_dependency_analysis
        finished[4]['evidence_dependency_analysis'] = safe_dependency_analysis(
            sections, env.card, env.ds, context=env.ctx, hypotheses=env.hypotheses,
        )
    return finished
