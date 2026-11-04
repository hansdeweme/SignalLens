# vf_patch_spatial.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Tuple
import cv2
import numpy as np
# local imports
from vf_patch_similarity import DEFAULT_MAX_PAIRS_TO_KEEP

def _load_mask(path: str | Path) -> np.ndarray:
    m = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"Failed to load mask: {path}")
    return (m > 127).astype(np.uint8)

def _safe_ratio(a: float, b: float) -> float:
    return float(a / (b + 1e-6))

def _point_region(x: int, y: int, subject_mask: np.ndarray, boundary_mask: np.ndarray, background_mask: np.ndarray) -> str:
    h, w = subject_mask.shape
    x = max(0, min(w - 1, int(x)))
    y = max(0, min(h - 1, int(y)))
    if boundary_mask[y, x] > 0:
        return "boundary"
    if subject_mask[y, x] > 0:
        return "subject"
    if background_mask[y, x] > 0:
        return "background"
    # fallback if masks don't perfectly partition
    return "background"

def _pair_category(r1: str, r2: str) -> str:
    if r1 == r2:
        return f"{r1}_{r2}"
    ordered = sorted([r1, r2])
    return f"{ordered[0]}_{ordered[1]}"

def _remap_point_to_mask_space(
    x: int,
    y: int,
    patch_width: int,
    patch_height: int,
    mask_width: int,
    mask_height: int,
) -> tuple[int, int]:
    if patch_width <= 0 or patch_height <= 0:
        return int(x), int(y)

    sx = mask_width / float(patch_width)
    sy = mask_height / float(patch_height)

    xr = int(round(x * sx))
    yr = int(round(y * sy))

    xr = max(0, min(mask_width - 1, xr))
    yr = max(0, min(mask_height - 1, yr))
    return xr, yr

def run_patch_spatial_analysis(patch_similarity_payload: Dict[str, Any], region_masks_payload: Dict[str, Any], output_dir: str | Path,) -> Dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # --------------------------------------------------
    # Load masks
    # --------------------------------------------------
    masks = region_masks_payload["region_masks"]
    subject_mask = _load_mask(masks["subject_mask_path"])
    boundary_mask = _load_mask(masks["boundary_band_path"])
    background_mask = _load_mask(masks["background_mask_path"])
    # --------------------------------------------------
    # Load top matched pairs from patch_similarity payload
    # --------------------------------------------------
    patch = patch_similarity_payload.get("patch_similarity", {})
    patch_size = int(patch.get("patch_size", 24))
    patch_half = patch_size / 2.0    
    top_pairs = patch.get("top_pairs", []) 
    # on error, instead of braking the pipeline return gracefully
    if not top_pairs:
            return {
                "patch_spatial": {
                        "pattern": "spatial_patch_recurrence_inconclusive",
                        "note": "No patch similarity pairs available for spatial analysis.",
        }
    }                
    top_pairs = top_pairs[:DEFAULT_MAX_PAIRS_TO_KEEP]
    # --------------------------------------------------
    # Load patch scale info for remapping coordinates to mask space
    # --------------------------------------------------    
    scale_info = patch.get("scale_info", {})
    patch_width = int(scale_info.get("width", subject_mask.shape[1]))
    patch_height = int(scale_info.get("height", subject_mask.shape[0]))
    # --------------------------------------------------
    # Accumulate counts and weighted scores by region topology
    # --------------------------------------------------
    categories = {
        "subject_subject": {"count": 0, "weight": 0.0},
        "boundary_boundary": {"count": 0, "weight": 0.0},
        "background_background": {"count": 0, "weight": 0.0},
        "boundary_subject": {"count": 0, "weight": 0.0},
        "background_subject": {"count": 0, "weight": 0.0},
        "background_boundary": {"count": 0, "weight": 0.0},
    }
    endpoint_counts = {
        "subject": 0,
        "boundary": 0,
        "background": 0,
    }
    endpoint_weights = {
        "subject": 0.0,
        "boundary": 0.0,
        "background": 0.0,
    }
    for p in top_pairs:
        ax = float(p["ax"]) + patch_half
        ay = float(p["ay"]) + patch_half
        bx = float(p["bx"]) + patch_half
        by = float(p["by"]) + patch_half
        sim = float(p.get("similarity", 0.0))
        # remap endpoints before _point_region
        axr, ayr = _remap_point_to_mask_space(
            ax, ay,
            patch_width=patch_width,
            patch_height=patch_height,
            mask_width=subject_mask.shape[1],
            mask_height=subject_mask.shape[0],
        )
        bxr, byr = _remap_point_to_mask_space(
            bx, by,
            patch_width=patch_width,
            patch_height=patch_height,
            mask_width=subject_mask.shape[1],
            mask_height=subject_mask.shape[0],
        )
        r1 = _point_region(axr, ayr, subject_mask, boundary_mask, background_mask)
        r2 = _point_region(bxr, byr, subject_mask, boundary_mask, background_mask)
                
        cat = _pair_category(r1, r2)
        if cat not in categories:
            categories[cat] = {"count": 0, "weight": 0.0}
        categories[cat]["count"] += 1
        categories[cat]["weight"] += sim
        endpoint_counts[r1] += 1
        endpoint_counts[r2] += 1
        endpoint_weights[r1] += sim
        endpoint_weights[r2] += sim
    total_pair_count = float(len(top_pairs))
    total_pair_weight = float(sum(float(p.get("similarity", 0.0)) for p in top_pairs))
    # --------------------------------------------------
    # Derived region-aware features
    # --------------------------------------------------
    subject_subject_count = categories.get("subject_subject", {}).get("count", 0)
    boundary_boundary_count = categories.get("boundary_boundary", {}).get("count", 0)
    background_background_count = categories.get("background_background", {}).get("count", 0)
    boundary_subject_count = categories.get("boundary_subject", {}).get("count", 0)
    background_subject_count = categories.get("background_subject", {}).get("count", 0)
    background_boundary_count = categories.get("background_boundary", {}).get("count", 0)
    subject_subject_weight = categories.get("subject_subject", {}).get("weight", 0.0)
    boundary_boundary_weight = categories.get("boundary_boundary", {}).get("weight", 0.0)
    background_background_weight = categories.get("background_background", {}).get("weight", 0.0)
    boundary_subject_weight = categories.get("boundary_subject", {}).get("weight", 0.0)
    background_subject_weight = categories.get("background_subject", {}).get("weight", 0.0)
    background_boundary_weight = categories.get("background_boundary", {}).get("weight", 0.0)
    # --------------------------------------------------
    # Subject-internal recurrence metrics (for virtual fashion model etc)
    # --------------------------------------------------
    subject_internal_ratio = _safe_ratio(subject_subject_count, total_pair_count)
    subject_internal_weight_ratio = _safe_ratio(subject_subject_weight, total_pair_weight)
    # --------------------------------------------------
    # Area-normalized endpoint densities
    # --------------------------------------------------
    subject_area = float(np.count_nonzero(subject_mask))
    boundary_area = float(np.count_nonzero(boundary_mask))
    background_area = float(np.count_nonzero(background_mask))
    subject_endpoint_density = endpoint_counts["subject"] / max(subject_area, 1.0)
    boundary_endpoint_density = endpoint_counts["boundary"] / max(boundary_area, 1.0)
    background_endpoint_density = endpoint_counts["background"] / max(background_area, 1.0)
    subject_weight_density = endpoint_weights["subject"] / max(subject_area, 1.0)
    boundary_weight_density = endpoint_weights["boundary"] / max(boundary_area, 1.0)
    background_weight_density = endpoint_weights["background"] / max(background_area, 1.0)
    subject_density_ratio = _safe_ratio(subject_endpoint_density, background_endpoint_density)
    boundary_density_ratio = _safe_ratio(boundary_endpoint_density, background_endpoint_density)
    subject_weight_ratio = _safe_ratio(subject_weight_density, background_weight_density)
    boundary_weight_ratio = _safe_ratio(boundary_weight_density, background_weight_density)
    # --------------------------------------------------
    # Bridge topology metrics
    # --------------------------------------------------
    bridge_count    = (boundary_subject_count + background_subject_count + background_boundary_count)
    bridge_weight   = (boundary_subject_weight + background_subject_weight + background_boundary_weight)
    internal_count  = (subject_subject_count + boundary_boundary_count + background_background_count)
    internal_weight = (subject_subject_weight + boundary_boundary_weight + background_background_weight)
    bridge_ratio = _safe_ratio(bridge_count, internal_count)
    bridge_weight_ratio = _safe_ratio(bridge_weight, internal_weight)
    boundary_involvement_count  = (boundary_boundary_count + boundary_subject_count + background_boundary_count )
    boundary_involvement_weight = (boundary_boundary_weight + boundary_subject_weight + background_boundary_weight)
    boundary_involvement_ratio = _safe_ratio(boundary_involvement_count, total_pair_count)
    boundary_involvement_weight_ratio = _safe_ratio(boundary_involvement_weight, total_pair_weight)
    boundary_correlated_ratio = _safe_ratio(boundary_boundary_count + boundary_subject_count, total_pair_count,)
    boundary_correlated_weight_ratio = _safe_ratio(boundary_boundary_weight + boundary_subject_weight, total_pair_weight,)
    subject_localized_ratio = _safe_ratio(subject_subject_count + boundary_subject_count, total_pair_count,)
    subject_localized_weight_ratio = _safe_ratio(subject_subject_weight + boundary_subject_weight, total_pair_weight,)
    cross_region_patch_reuse_ratio = bridge_ratio
    #---------------------------------------------------
    # Debug prints for key metrics
    #---------------------------------------------------
    '''
    print("[DEBUG][patch_spatial][final]", {
        "bridge_count": bridge_count,
        "internal_count": internal_count,
        "bridge_ratio": bridge_ratio,
        "boundary_involvement_count": boundary_involvement_count,
        "boundary_involvement_ratio": boundary_involvement_ratio,
        "boundary_correlated_ratio": boundary_correlated_ratio,
        "subject_localized_ratio": subject_localized_ratio,
    })
    print("[DEBUG][patch_spatial] pair_category_counts:", {
        "subject_subject": subject_subject_count,
        "boundary_boundary": boundary_boundary_count,
        "background_background": background_background_count,
        "boundary_subject": boundary_subject_count,
        "background_subject": background_subject_count,
        "background_boundary": background_boundary_count,
    })
    print("[DEBUG][patch_spatial] endpoint_counts:", endpoint_counts)
    print("[DEBUG][patch_spatial] areas:", {
        "subject": subject_area,
        "boundary": boundary_area,
        "background": background_area,
    })        
    '''
    # --------------------------------------------------
    # Interpretation
    # --------------------------------------------------
    pattern = "spatial_patch_recurrence_inconclusive"
    # subject-internal synthetic texture recurrence
    # Intended for fashion / virtual-model cases where repeated synthetic fabric
    # structure is concentrated inside the subject rather than bridging regions.
    if (
        subject_subject_count >= 6
        and subject_internal_ratio >= 0.08
        and subject_density_ratio >= 0.75
    ):
        pattern = "subject_internal_synthetic_recurrence"
    # Strongest case: almost all matched pairs bridge different regions
    elif (
        bridge_ratio >= 0.85
        and bridge_weight_ratio >= 0.85
        and boundary_involvement_ratio >= 0.50
        and bridge_count >= 8
    ):
        pattern = "cross_region_patch_recurrence"
    # Contour-band correlated recurrence
    elif (
        boundary_density_ratio >= 1.10
        and boundary_correlated_ratio >= 0.10
        and boundary_involvement_ratio >= 0.20
    ):
        pattern = "boundary_correlated_patch_recurrence"
    # Subject-focused recurrence
    elif (
        subject_density_ratio >= 1.10
        and subject_localized_ratio >= 0.10
    ):
        pattern = "subject_localized_patch_recurrence"
    # Broad recurrence across multiple regions
    elif (
        subject_density_ratio >= 1.02
        and boundary_density_ratio >= 1.02
        and bridge_ratio >= 0.30
    ):
        pattern = "scene_wide_patch_recurrence"
    elif (
        bridge_ratio < 0.30
        and 0.90 <= subject_density_ratio <= 1.10
        and 0.90 <= boundary_density_ratio <= 1.10
    ):
        pattern = "patch_spatial_convergence_supported"
    #--------------------------------------------------
    # Debug print for pattern interpretation
    #--------------------------------------------------
    '''''
    print("[DEBUG][patch_spatial][final]", {
        "bridge_count": bridge_count,
        "internal_count": internal_count,
        "bridge_ratio": bridge_ratio,
        "boundary_involvement_count": boundary_involvement_count,
        "boundary_involvement_ratio": boundary_involvement_ratio,
        "boundary_correlated_ratio": boundary_correlated_ratio,
        "subject_localized_ratio": subject_localized_ratio,
        "subject_subject_count": subject_subject_count,
        "subject_internal_ratio": subject_internal_ratio,
        "subject_internal_weight_ratio": subject_internal_weight_ratio,
    })
    '''''
    # --------------------------------------------------
    # Output
    # --------------------------------------------------
    return {
        "patch_spatial": {
            "pattern": pattern,
            "region_stats": {
                "areas": {
                    "subject": float(subject_area),
                    "boundary": float(boundary_area),
                    "background": float(background_area),
                },
                "endpoint_densities": {
                    "subject": float(subject_endpoint_density),
                    "boundary": float(boundary_endpoint_density),
                    "background": float(background_endpoint_density),
                },
                "weight_densities": {
                    "subject": float(subject_weight_density),
                    "boundary": float(boundary_weight_density),
                    "background": float(background_weight_density),
                },                                                                
                "endpoint_counts": {
                    "subject": int(endpoint_counts["subject"]),
                    "boundary": int(endpoint_counts["boundary"]),
                    "background": int(endpoint_counts["background"]),
                },
                "endpoint_weights": {
                    "subject": float(endpoint_weights["subject"]),
                    "boundary": float(endpoint_weights["boundary"]),
                    "background": float(endpoint_weights["background"]),
                },
                "pair_category_counts": {
                    "subject_subject": int(subject_subject_count),
                    "boundary_boundary": int(boundary_boundary_count),
                    "background_background": int(background_background_count),
                    "boundary_subject": int(boundary_subject_count),
                    "background_subject": int(background_subject_count),
                    "background_boundary": int(background_boundary_count),
                },
                "pair_category_weights": {
                    "subject_subject": float(subject_subject_weight),
                    "boundary_boundary": float(boundary_boundary_weight),
                    "background_background": float(background_background_weight),
                    "boundary_subject": float(boundary_subject_weight),
                    "background_subject": float(background_subject_weight),
                    "background_boundary": float(background_boundary_weight),
                },
                "subject_subject_count": int(subject_subject_count),
                "subject_subject_weight": float(subject_subject_weight),                
                "total_pair_count": int(total_pair_count),
                "total_pair_weight": float(total_pair_weight),
                "bridge_count": int(bridge_count),
                "bridge_weight": float(bridge_weight),
                "internal_count": int(internal_count),
                "internal_weight": float(internal_weight),
                "boundary_involvement_count": int(boundary_involvement_count),
                "boundary_involvement_weight": float(boundary_involvement_weight),                
            },
            "comparative_features": {
                "subject_similarity_ratio": float(subject_density_ratio),
                "boundary_similarity_ratio": float(boundary_density_ratio),
                "subject_weight_ratio": float(subject_weight_ratio),
                "boundary_weight_ratio": float(boundary_weight_ratio),
                "bridge_ratio": float(bridge_ratio),
                "bridge_weight_ratio": float(bridge_weight_ratio),
                "boundary_involvement_ratio": float(boundary_involvement_ratio),
                "boundary_involvement_weight_ratio": float(boundary_involvement_weight_ratio),
                "boundary_correlated_ratio": float(boundary_correlated_ratio),
                "boundary_correlated_weight_ratio": float(boundary_correlated_weight_ratio),
                "subject_localized_ratio": float(subject_localized_ratio),
                "subject_localized_weight_ratio": float(subject_localized_weight_ratio),
                "cross_region_patch_reuse_ratio": float(cross_region_patch_reuse_ratio),
                "subject_internal_ratio": float(subject_internal_ratio),
                "subject_internal_weight_ratio": float(subject_internal_weight_ratio),
            },
            "artifacts": {
                "recurrence_map": patch.get("artifacts", {}).get("patch_similarity_heatmap"),
                "patch_similarity_overlay": patch.get("artifacts", {}).get("patch_similarity_overlay"),
            },
        }
    }