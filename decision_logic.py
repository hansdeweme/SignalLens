# decision_logic.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from dataclasses import dataclass
from typing import Any
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
)
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
            "score": float(s.score) if s.score is not None else None,
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
            v = getattr(obj, k)
            out[k] = _jsonable_scalar(v)
        return out
    if hasattr(obj, "__dict__"):
        return {k: _jsonable_scalar(v) for k, v in vars(obj).items()}
    return {}

def _jsonable_scalar(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if hasattr(v, "__dataclass_fields__") or hasattr(v, "__dict__"):
        return _object_to_dict(v)
    if isinstance(v, (list, tuple)):
        return [_jsonable_scalar(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable_scalar(val) for k, val in v.items()}
    try:
        return float(v)
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
) -> dict:
    primary = dominant_pattern
    supporting = extract_secondary_patterns(
        sections,
        primary,
        target_polarity=polarity if polarity in {"suspicious", "benign"} else None,
    )
    if polarity in {"neutral", "suspicious"}:
        supporting = [
            p for p in supporting
            if p not in {
                "camera_metadata_present",
                "weak_camera_pipeline_supported",
                "weak_camera_cfa_supported",
            }
        ]            
    contradicting = extract_contradicting_patterns(sections, primary, polarity)
    rationale = build_confidence_rationale(card, sections, polarity)
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
        "decision_route_trace": [
            _object_to_dict(item) for item in (route_trace or [])
        ],        
        "decision": {
            "decision_branch": decision_branch,
            "dominant_pattern": dominant_pattern,
            "confidence_tier": confidence_tier,
            "polarity": polarity,
            "supporting_signals": supporting,
            "contradicting_signals": contradicting,
            "confidence_rationale": rationale,
            "overall_text": overall_text,
        },
    }

# We have two abstraction layers: 
# Hypothesis Engine:  sections → DerivedSignals → ScoreCard
# Summary / Narrative sections → human-readable narrative
# We do NOT pass DerivedSignals. Instead, re-derive minimal logic from sections.

def determine_dominant_pattern(sections):
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
    metadata_synthetic = metadata and metadata.pattern in {
        "declared_synthetic_candidate",
        "declared_enhancement_candidate",
    }
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
def determine_confidence(card, sections):
    mat = sections.get("subject_material_realism")
    asym = sections.get("subject_process_asymmetry")
    boundary = sections.get("boundary")
    cross = sections.get("cross_signal")
    mat_score = mat.score if mat and mat.score is not None else 0.0
    strong_signals = sum([
        mat_score >= 0.58,
        bool(asym and asym.pattern == "subject_process_asymmetry_strong"),
        bool(boundary and boundary.pattern == "possible_foreground_background_processing_mismatch"),
        bool(cross and cross.pattern == "strong_hotspot_convergence"),
    ])
    score = card.suspicious_score
    if strong_signals >= 2 and score >= 3.0:
        return "High"
    if strong_signals >= 1 and score >= 2.0:
        return "Medium"
    if score >= 1.2:
        return "Low"
    return "Inconclusive"

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
) -> list[str]:
    reasons: list[str] = []
    #-----------------------------------------------
    # --- signal strength ---    
    #------------------------------------------------
    effective_score = card.suspicious_score
    # print(f"Debug 1: effective_score {effective_score} = card.suspicious_score {card.suspicious_score}")
    if card.camera_counter_support >= 2.0:
        effective_score = card.suspicious_score * 0.55 - card.camera_counter_support
    elif card.camera_counter_support >= 1.0:
        effective_score = card.suspicious_score * 0.70 - card.camera_counter_support
    else:
        effective_score = card.suspicious_score - card.camera_counter_support
    # print(f"Debug 2: effective_score {effective_score}, card.suspicious_score {card.suspicious_score}, card.camera_counter_support {card.camera_counter_support}")
    if card.camera_counter_support >= 2.5:
        effective_score = min(effective_score, 3.2)    
    # print(f"Debug 3: effective_score {effective_score} min(min(effective_score, 3.2)")

    if polarity == "neutral":
        if effective_score >= 2.5:
            reasons.append("some suspicious signals remain, but they are moderated by counter-evidence")
        elif effective_score >= 1.2:
            reasons.append("weak suspicious signals are present, but they remain inconclusive")
        else:
            reasons.append("only limited suspicious signal remains after accounting for counter-evidence")
    else:
        if effective_score >= 4.0:
            reasons.append("multiple strong forensic signals contribute to the overall assessment")
        elif effective_score >= 2.5:
            reasons.append("several moderate forensic signals contribute to the overall assessment")
        elif effective_score >= 1.2:
            reasons.append("limited forensic signals are present, but remain inconclusive")
        else:
            reasons.append("limited forensic signals remain after accounting for counter-evidence")
        
    # --- cross-domain convergence ---
    strong_domains = sum(
        1 for s in sections.values()
        if s and s.score and s.score >= 0.55 and is_suspicious(s)
    )
    if strong_domains >= 2:
        if card.camera_counter_support >= 2.0:
            reasons.append(
                "both suspicious and benign signals are present across multiple independent domains"
            )
        else:
            reasons.append(
                "independent forensic domains show converging evidence"
            )        
    # --- contradiction handling ---
    contradicting = extract_contradicting_patterns(sections, None, polarity)
    if not contradicting:
        if card.camera_counter_support >= 2.0:
            reasons.append(
                "strong camera-acquisition signals counterbalance the suspicious indicators"
            )
        else:        
            reasons.append("little to no strong contradicting evidence is present")
    elif len(contradicting) == 1:
        reasons.append("some contradicting evidence slightly moderates confidence")
    else:
        reasons.append("multiple contradicting signals reduce overall confidence")
    # --- benign reinforcement ---
    if polarity == "benign" and card.benign_score >= 2.0:
        reasons.append("multiple benign indicators support a coherent photo-like interpretation")
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

@dataclass(frozen=True)
class DecisionResult:
    pattern: str | None
    text: str
    confidence: str
    polarity: str
    branch: str
    debug_message: str | None = None
    
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
    return (
        boundary_corroboration_count >= 2
        and boundary_specific_strength >= 0.45
    )

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
    ds = derive_signals(ev)
    card = compute_scorecard(sections, ctx, ev, ds)
    metadata = ev.metadata
    real_photo_context_prior = (
        ds.provenance_clean
        and not ds.metadata_synthetic
        and metadata is not None
        and metadata.pattern == "camera_metadata_present"
        and bool(getattr(ctx, "smartphone_computational", False))
    )
    if real_photo_context_prior:
        card.camera_counter_support += 1.5
        card.caution_penalty += 1.0
        card.suspicious_score *= 0.70
    dominant_pattern = determine_dominant_pattern(sections)
    if card.camera_counter_support >= 2.5 and ds.local_signals_weak:
        dominant_pattern = "photo_like_consistency_supported"
    return DecisionEnv(
        sections=sections,
        ctx=ctx,
        ev=ev,
        ds=ds,
        card=card,
        dominant_pattern=dominant_pattern,
        confidence_tier=determine_confidence(card, sections),
        real_photo_context_prior=real_photo_context_prior,
        analysis_mode=analysis_mode,
        route_trace=[],
    )

def finish_decision(
    env: DecisionEnv,
    result: DecisionResult,
    debug_lines: list[str] | None = None,
    debug: bool = False,
) -> tuple[str | None, str, str, str, dict]:
    if debug:
        print("\n--- SYNTHESIS DEBUG REPORT ---")
        for line in debug_lines or []:
            print(line)
        print("--- END DEBUG REPORT ---\n")

    pattern = result.pattern
    polarity = result.polarity
    text = result.text
    secondary_target_polarity = polarity if polarity in {"suspicious", "benign"} else None
    secondary = extract_secondary_patterns(
        env.sections,
        pattern,
        target_polarity=secondary_target_polarity,
    )
    if polarity == "neutral":
        secondary = [
            p for p in secondary
            if p not in {
                "camera_metadata_present",
                "weak_camera_pipeline_supported",
                "weak_camera_cfa_supported",
            }
        ][:3]
    text = append_secondary_patterns(text, secondary)
    contradicting = extract_contradicting_patterns(env.sections, pattern, polarity)
    text = append_contradicting_patterns(text, contradicting)
    rationale = build_confidence_rationale(env.card, env.sections, polarity)
    text = append_confidence_rationale(text, rationale)
    text = text.strip() + "\n"
    metadata = env.sections.get("metadata")
    if metadata and metadata.pattern == "declared_synthetic_candidate":
        text = text.rstrip() + (
            "\nMetadata also contains explicit provenance cues consistent with declared synthetic generation.\n"
        )
    elif metadata and metadata.pattern == "declared_enhancement_candidate":
        text = text.rstrip() + (
            "\nMetadata also contains explicit provenance cues consistent with declared enhancement or generative editing.\n"
        )
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
            )
        if env.ds.material_realism_strong:
            return DecisionResult(
                env.dominant_pattern,
                "Repeated structures are present, but subject-level material analysis suggests synthetic generation rather than direct clone reuse.",
                env.confidence_tier,
                "neutral",
                "clone_ambiguous → realism override",
                "DECISION: clone_ambiguous → realism override",
            )
        return DecisionResult(
            "possible_clone_reuse",
            "Patch similarity reveals highly similar spatially separated regions, but the current evidence is insufficient to exclude natural scene repetition.",
            "Medium",
            "neutral",
            "possible_clone_reuse (ambiguous)",
            "DECISION: possible_clone_reuse (ambiguous)",
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
        )
    return None

def route_synthetic_multi_signal(env: DecisionEnv) -> DecisionResult | None:
    if (
        env.card.synthetic_boost >= 1.0
        and env.card.suspicious_score >= 5.0
        and env.card.synthetic_supported_by_other_domains
        and not (
            env.ds.local_signals_weak
            and env.ds.provenance_clean
            and env.ds.coverage_ratio >= 0.18
        )
    ):
        pattern = env.dominant_pattern if env.dominant_pattern else "synthetic_multi_signal_convergence"
        return DecisionResult(
            pattern,
            "Multiple independent signals indicate synthetic or decoder-mediated structure.",
            "High",
            "suspicious",
            "synthetic_multi_signal_convergence",
            "DECISION: synthetic_multi_signal_convergence",
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
        )
    return None

def route_provenance(env: DecisionEnv) -> DecisionResult | None:
    if env.card.provenance_boost >= 1.0 and env.card.suspicious_score >= 3.5:
        return DecisionResult(
            "provenance_supported_synthetic_context",
            "Metadata and/or OSINT context support a synthetic or AI-mediated origin."
            "Visual-forensic findings provide additional context, but provenance evidence "
            "is the main driver of this conclusion.",
            "High",
            "suspicious",
            "provenance_supported_synthetic_context",
            "DECISION: provenance_supported_synthetic_context",
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
            "Camera-like acquisition signals and clean provenance support a real photographic workflow, with no strong localized forensic inconsistency dominating the assessment.",
            "Medium",
            "benign",
            pattern,
            "DECISION: camera_like_acquisition_supported",
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
        suspicious_sections = [s for s in env.sections.values() if is_suspicious(s)]
        top = max(suspicious_sections, key=weight) if suspicious_sections else None
        return DecisionResult(
            top.pattern if top and top.pattern else "multi_signal_suspicious_convergence",
            "Multiple suspicious indicators converge across independent forensic domains."
            "The current analysis supports a strong anomalous reading, although the exact "
            "mechanism is not singularly determined.",
            "High",
            "suspicious",
            "multi_signal_suspicious_convergence",
            "DECISION: multi_signal_suspicious_convergence",
        )
    return None

def route_moderate_suspicious(env: DecisionEnv) -> DecisionResult | None:
    if env.card.suspicious_score >= 3.5:
        pattern = determine_dominant_pattern(env.sections)
        return DecisionResult(
            pattern or "moderate_suspicious_convergence",
            enrich_text_with_context(
                env,
                "Multiple suspicious indicators are present across the current forensic reading, "
                "but the evidence does not converge strongly enough for a narrower high-confidence interpretation. "
                "The selected dominant pattern is therefore the most consistent moderate explanation given the available signals."
            ),
            env.confidence_tier,
            "suspicious",
            pattern or "moderate_suspicious_convergence",
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
            "The available signals do not support a stronger specialized routing outcome, "
            "but the current evidence still favors this as the most internally consistent explanation. "
            "This fallback reading should be treated as a cautious synthesis rather than a highly specific conclusion."
        ),
        confidence=fallback_confidence,
        polarity=fallback_polarity,
        branch="helper_driven_fallback",
        debug_message="DECISION: helper_driven_fallback",
    )

def synthesize_overall(
    sections: dict[str, ModuleSummary], 
    scene_context: dict | None = None, 
    debug: bool = False, 
    analysis_mode: str | None = None,
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
    base_suspicious_score, base_benign_score, suspicious_domains, benign_domains = (
        compute_base_scores(sections)
    )
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
    routes = [
        route_real_photo_context_prior,
        route_boundary_support_limited,
        route_region_geometry_unreliable,
        route_localized_multi_mechanism,
        route_strong_local_edit,
        route_clone_reuse,
        route_moderated_local_edit,
        route_clone_ambiguous,
        route_structured_recurrence_inconclusive,
        route_synthetic_multi_signal,
        route_localized_processing,
        route_unreliable_boundary_context,
        route_subject_boundary,
        route_boundary_transition,
        route_provenance,
        route_camera_like,
        route_multi_signal_suspicious,
        route_moderate_suspicious,
        route_photo_like_consistency,
        route_fallback,
    ]
    for route in routes:
        result = route(env)
        route_name = route.__name__
        if result is None:
            if env.route_trace is not None:
                env.route_trace.append(
                    DecisionRouteTraceItem(
                        route=route_name,
                        matched=False,
                        reason="condition_not_met",
                    )
                )
            continue

        if env.route_trace is not None:
            env.route_trace.append(
                DecisionRouteTraceItem(
                    route=route_name,
                    matched=True,
                    reason=result.debug_message or "matched",
                    pattern=result.pattern,
                    confidence=result.confidence,
                    polarity=result.polarity,
                )
            )

        if result.debug_message:
            debug_lines.append(result.debug_message)
        return finish_decision(env, result, debug_lines=debug_lines, debug=debug)

    # Guaranteed terminal fallback
    result = route_fallback(env)
    if env.route_trace is not None:
        env.route_trace.append(
            DecisionRouteTraceItem(
                route="route_fallback",
                matched=True,
                reason=result.debug_message or "fallback",
                pattern=result.pattern,
                confidence=result.confidence,
                polarity=result.polarity,
            )
        )
    if result.debug_message:
        debug_lines.append(result.debug_message)
    return finish_decision(env, result, debug_lines=debug_lines, debug=debug)
