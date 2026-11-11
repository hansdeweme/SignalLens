#vf_subject_material_realism.py
from __future__ import annotations
from investigation_storage import artifact_stem
from pathlib import Path
from typing import Dict, Any
import cv2
import numpy as np
# local imports
from vf_subject_process_asymmetry import (
    _load_mask,
    _resize_mask,
    _load_bgr_image_exact,
    _validate_region_geometry,
    _sample_region_patches,
    _aggregate_region_metrics,
    _write_overlay,
    _sample_single_region_with_retries
)

# ------------------------------------------------------------
# helpers 
# ------------------------------------------------------------
def _sigmoid(x: float, center: float = 0.5, slope: float = 10.0) -> float:
    return 1.0 / (1.0 + np.exp(-slope * (x - center)))

def _clamp01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))

def _build_subject_variance_heatmap(
    gray: np.ndarray,
    subject_mask: np.ndarray,
    patch_size: int = 32,
    stride: int = 16,
    min_coverage: float = 0.85,
) -> np.ndarray:
    h, w = gray.shape
    heat = np.zeros((h, w), dtype=np.float32)
    weight = np.zeros((h, w), dtype=np.float32)
    for y in range(0, h - patch_size + 1, stride):
        for x in range(0, w - patch_size + 1, stride):
            patch_mask = subject_mask[y:y+patch_size, x:x+patch_size]
            coverage = patch_mask.mean()
            if coverage < min_coverage:
                continue
            patch = gray[y:y+patch_size, x:x+patch_size]
            # variance as proxy for microtexture
            val = float(np.var(patch))
            heat[y:y+patch_size, x:x+patch_size] += val
            weight[y:y+patch_size, x:x+patch_size] += 1.0
    weight = np.maximum(weight, 1e-6)
    heat = heat / weight
    # normalize to 0–1
    heat_min = float(heat.min())
    heat_max = float(heat.max())
    if heat_max > heat_min:
        heat = (heat - heat_min) / (heat_max - heat_min)
    else:
        heat[:] = 0.0
    return heat

# ------------------------------------------------------------
# main entry
# ------------------------------------------------------------

def run_subject_material_realism_analysis(
    profile,
    image_path: str | Path,
    subject_mask_path: str | Path,
    output_dir: str | Path,
    analysis_shape_hw: tuple[int, int] | None = None,
    analysis_scale: float | None = None,
    patch_size: int = 32,
    stride: int = 16,
    min_coverage: float = 0.85,
) -> Dict[str, Any]:
    profile = profile
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if analysis_shape_hw is None:
        raise ValueError(
            "analysis_shape_hw must be provided by the gatekeeper so that "
            "image and subject mask share one explicit analysis geometry."
        )
    image_bgr = _load_bgr_image_exact(image_path, analysis_shape_hw)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    subject_mask_full = _load_mask(subject_mask_path)
    subject_mask = _resize_mask(subject_mask_full, analysis_shape_hw)
    _validate_region_geometry(
        gray=gray,
        subject_mask=subject_mask,
        boundary_mask=None,
        background_mask=None,
        expected_shape_hw=analysis_shape_hw,
    )

    # ------------------------------------------------------------
    # patch sampling
    # ------------------------------------------------------------
    sampling_result = _sample_single_region_with_retries(
        gray=gray,
        region_mask=subject_mask,
        max_patches=None,
        sampling_schedule=[
            (patch_size, stride, min_coverage),
            (24, 12, 0.75),
            (16, 8, 0.65),
        ],
        stratify_bins=6,
        seed=42,
        min_required_patches=12,
        debug_label="SMR",
    )
    subject_patches = sampling_result["patches"]
    effective_patch_size = sampling_result["patch_size"]
    effective_stride = sampling_result["stride"]
    effective_min_coverage = sampling_result["min_coverage"]
    sampling_attempt_index = sampling_result["attempt_index"]
    sampling_rescued = bool(sampling_result["sampling_rescued"])
    subject_metrics = _aggregate_region_metrics(subject_patches)
    patch_count = int(subject_metrics["patch_count"])
    if patch_count < 12:
        print(
            "[DEBUG][SMR][LOW_PATCH_FINAL] "
            f"subject={patch_count} | "
            f"patch_size={effective_patch_size} | "
            f"stride={effective_stride} | "
            f"min_coverage={effective_min_coverage:.2f} | "
            f"attempt={sampling_attempt_index} | "
            f"image_shape={gray.shape} | "
            f"mask_subject_sum={int(subject_mask.sum())}"
        )

    # ------------------------------------------------------------
    # metric extraction (subject-only)
    # ------------------------------------------------------------
    var_mean = float(subject_metrics["variance_mean"])
    res_mean = float(subject_metrics["residual_energy_mean"])
    ent_mean = float(subject_metrics["entropy_mean"])
    var_std = subject_metrics["variance_std"]
    res_std = subject_metrics["residual_energy_std"]
    ent_std = subject_metrics["entropy_std"]  
    grad_std = float(subject_metrics["gradient_std_mean"])
    grad_axis_bias = float(subject_metrics["grad_axis_bias_mean"])
    # grad_mean = float(subject_metrics["gradient_mean"])
    dct_sim = float(subject_metrics["dct_similarity_mean"])
    dct_sim_std = float(subject_metrics["dct_similarity_std"])

    # ------------------------------------------------------------
    # score families
    # ------------------------------------------------------------
    # 1. microtexture suppression
    microtexture_suppression = _clamp01(
        0.4 * _sigmoid(1.0 / (res_mean + 1e-6), center=0.35, slope=6.0) +
        0.3 * _sigmoid(1.0 / (ent_mean + 1e-6), center=0.22, slope=10.0) +
        0.3 * _sigmoid(1.0 / (grad_std + 1e-6), center=0.08, slope=40.0)
    )
    # 2. material homogenization (too stable across patches)
    material_homogenization = _clamp01(
        0.5 * _sigmoid(dct_sim, center=0.85, slope=10.0) +
        0.25 * _sigmoid(1.0 / (var_std + 1e-6), center=0.015, slope=120.0) +
        0.25 * _sigmoid(1.0 / (res_std + 1e-6), center=0.03, slope=80.0)
    )
    # 3. structure without stochasticity
    # Favor regions that still contain organized structure, but where that structure
    # is too directionally stable and too low-noise to read as natural material.
    structure_coherence = _clamp01(
        0.40 * _sigmoid(dct_sim, center=0.84, slope=10.0) +
        0.40 * _sigmoid(grad_axis_bias, center=0.14, slope=14.0) +
        0.20 * _sigmoid(1.0 / (dct_sim_std + 1e-6), center=10.0, slope=0.35)
    )
    stochasticity_suppression = _clamp01(
        0.45 * _sigmoid(1.0 / (res_mean + 1e-6), center=0.35, slope=6.0) +
        0.35 * _sigmoid(1.0 / (ent_mean + 1e-6), center=0.22, slope=10.0) +
        0.20 * _sigmoid(1.0 / (grad_std + 1e-6), center=0.08, slope=40.0)
    )
    structure_ratio = grad_std / (res_mean + 1e-6)
    structure_without_stochasticity = _clamp01(
        0.5 * structure_coherence +
        0.5 * stochasticity_suppression
    )
    # 4. distribution compression (lack of variability)
    # Real subject:      variance_std = high, residual_std = high, entropy_std = high   → distribution_compression ≈ low
    # Synthetic subject: variance_std = low,  residual_std = low,  entropy_std = low    → distribution_compression ≈ high    
    # distribution_compression ≈ global uniformity detector
    # averaging or max-driven logic?
    # consensus logic: “The subject is suspicious if most signals agree” OR anomaly logic “The subject is suspicious if any strong signal exists”    
    averaging = (profile == "normal")
    # print(f"Debug: profile used is {profile}")
    if averaging:      # "all must be compressed"
        distribution_compression = _clamp01(
            0.34 * _sigmoid(1.0 / (subject_metrics["variance_std"] + 1e-6), center=0.015, slope=120.0) +
            0.33 * _sigmoid(1.0 / (subject_metrics["residual_energy_std"] + 1e-6), center=0.03, slope=80.0) +
            0.33 * _sigmoid(1.0 / (subject_metrics["entropy_std"] + 1e-6), center=0.02, slope=100.0)
        )
    else:              # "any strong compression channel"                             
        var_c = _sigmoid(1.0 / (var_std + 1e-6), center=0.002, slope=200.0)
        res_c = _sigmoid(1.0 / (res_std + 1e-6), center=0.15, slope=10.0)
        ent_c = _sigmoid(1.0 / (ent_std + 1e-6), center=1.5, slope=3.0)
        avg_score = 0.34 * var_c + 0.33 * res_c + 0.33 * ent_c
        max_score = max(var_c, res_c, ent_c)
        distribution_compression = _clamp01(0.6 * avg_score + 0.4 * max_score)
    # print(f"Debug: variance_std: {subject_metrics['variance_std']}, residual_energy_std: {subject_metrics['residual_energy_std']}, entropy_std: {subject_metrics['entropy_std']}")
    # print(f"Debug: resulting distribution_compression: {distribution_compression}")
    # ------------------------------------------------------------
    # final realism score
    # ------------------------------------------------------------
    # strongest signals for synthetic subject: structure + distribution, when underweighted we mesure 'smoothing' instead of 'material realism'
    subject_material_realism_score = _clamp01(
        0.20 * microtexture_suppression +
        0.20 * material_homogenization +
        0.30 * structure_without_stochasticity +
        0.30 * distribution_compression
    )
    sampling_reliability_factor = 1.0
    if sampling_attempt_index == 2:
        sampling_reliability_factor = 0.85
    elif sampling_attempt_index >= 3:
        sampling_reliability_factor = 0.70
    subject_material_realism_score *= sampling_reliability_factor    
    
    # ------------------------------------------------------------
    # pattern interpretation
    # ------------------------------------------------------------
    if sampling_attempt_index >= 3 and patch_count < 24:
        if subject_material_realism_score >= 0.44:
            pattern = "subject_material_realism_inconclusive"
            note = (
                "Subject material analysis became measurable only under aggressive rescue sampling. "
                "The resulting material-regularity signal is treated as contextual and not stable enough "
                "for a stronger realism-failure conclusion."
            )        
    elif subject_material_realism_score >= 0.58:
        pattern = "subject_material_realism_failure_strong"
        note = "Subject exhibits strong material realism failure: textures appear over-regularized, physically implausible, or statistically compressed."
    elif subject_material_realism_score >= 0.44:
        pattern = "subject_material_regularization_dominant"
        note = "Subject shows moderate signs of material regularization or homogenization, consistent with synthetic or heavily processed rendering."
    elif subject_material_realism_score >= 0.30:
        pattern = "subject_structure_without_stochasticity"
        note = "Subject retains structural features but lacks natural stochastic microtexture, suggesting possible synthetic surface modeling."
    elif subject_material_realism_score <= 0.18:
        pattern = "subject_material_realism_supported"
        note = "Subject material statistics are broadly consistent with natural photographic surfaces."
    else:
        pattern = "subject_material_realism_inconclusive"
        note = "Subject material realism remains inconclusive; no strong evidence of either natural or synthetic rendering."

    # ------------------------------------------------------------
    # overlay (simple variance heatmap proxy)
    # ------------------------------------------------------------
    heat = _build_subject_variance_heatmap(
        gray=gray,
        subject_mask=subject_mask,
        patch_size=patch_size,
        stride=stride,
        min_coverage=min_coverage,
    )
    overlay_path = output_dir / f"{artifact_stem(image_path)}_subject_material_realism_overlay.jpg"
    overlay_path_str = _write_overlay(image_bgr, heat, overlay_path)

    # ------------------------------------------------------------
    # debug logging
    # ------------------------------------------------------------
    """
    print(
        "[DEBUG][subject_material_realism]",
        {
            "pattern": pattern,
            "score": subject_material_realism_score,
            "microtexture_suppression": microtexture_suppression,
            "material_homogenization": material_homogenization,
            "structure_without_stochasticity": structure_without_stochasticity,
            "distribution_compression": distribution_compression,
            "patch_count": patch_count,
            "variance_mean": var_mean,
            "variance_std": var_std,
            "residual_mean": res_mean,
            "residual_std": res_std,
            "entropy_mean": ent_mean,
            "entropy_std": ent_std,
            "gradient_std": grad_std,
            "grad_axis_bias": grad_axis_bias,
            "dct_similarity": dct_sim,
            "dct_similarity_std": dct_sim_std,
            "structure_coherence": structure_coherence,
            "stochasticity_suppression": stochasticity_suppression,
        }
    )
    """

    def clean_region_metrics(m: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in m.items() if not str(k).startswith("_")}

    return {
        "subject_material_realism": {
            "analysis_geometry": {
                "height": int(gray.shape[0]),
                "width": int(gray.shape[1]),
                "analysis_scale": float(analysis_scale) if analysis_scale is not None else None,
                "image_path_used": str(image_path),
            },            
            "pattern": pattern,
            "note": note,
            "scores": {
                "subject_material_realism_score": subject_material_realism_score,
                "microtexture_suppression": microtexture_suppression,
                "material_homogenization": material_homogenization,
                "structure_without_stochasticity": structure_without_stochasticity,
                "distribution_compression": distribution_compression,
            },
            "subject_metrics": clean_region_metrics(subject_metrics),
            "controls": {
                "patch_count": patch_count,
                "effective_patch_size": int(effective_patch_size),
                "effective_stride": int(effective_stride),
                "effective_min_coverage": float(effective_min_coverage),
                "sampling_attempt_index": int(sampling_attempt_index),
                "sampling_rescued": bool(sampling_rescued),
                "sampling_reliability_factor": float(sampling_reliability_factor),
            },
            "artifacts": {
                "subject_input": str(subject_mask_path),
                "subject_material_realism_overlay": overlay_path_str,
            },
        }
    }
