#vf_cfa_demosaic.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
# CFA / demosaicing consistency detector
# Goal:
# Detect weak 2x2 acquisition-like color-plane periodicity and assess whether it is
# spatially coherent, locally inconsistent, or too weak/inconclusive.
#
# Important:
# - This is a conservative structural detector.
# - It is supportive, not decisive.
# - It complements sensor-origin analysis rather than replacing it.
#

from __future__ import annotations
from pathlib import Path
from typing import Any
import math
import cv2
import numpy as np

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def ensure_bgr(image_path: str | Path) -> np.ndarray:
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    return image

def normalize_map(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    if x.size == 0:
        return x
    mn = float(np.min(x))
    mx = float(np.max(x))
    if mx - mn < 1e-8:
        return np.zeros_like(x, dtype=np.float32)
    return (x - mn) / (mx - mn)

def highpass_residual(channel: np.ndarray, sigma: float) -> np.ndarray:
    """Calculates residual with a dynamic sigma to match image scale."""
    ch = channel.astype(np.float32)
    # sigma determines the 'width' of the Gaussian blur used for subtraction
    blur = cv2.GaussianBlur(ch, (0, 0), sigmaX=sigma, sigmaY=sigma)
    return ch - blur

def block_view_shape(h: int, w: int, block_size: int) -> tuple[int, int]:
    return math.ceil(h / block_size), math.ceil(w / block_size)

def checkerboard_phase_means(block: np.ndarray) -> np.ndarray:
    """
    Mean absolute residual energy for the 4 Bayer-like 2x2 phases:
      (0,0), (0,1), (1,0), (1,1)
    """
    vals = []
    for dy in (0, 1):
        for dx in (0, 1):
            phase = block[dy::2, dx::2]
            if phase.size == 0:
                vals.append(0.0)
            else:
                vals.append(float(np.mean(np.abs(phase))))
    return np.asarray(vals, dtype=np.float32)

def phase_periodicity_score(block: np.ndarray) -> float:
    """
    A simple 2x2 periodicity score:
    if the four CFA-like phases differ systematically, weak acquisition-style
    periodicity may still be present.
    """
    phase_means = checkerboard_phase_means(block)
    mu = float(np.mean(phase_means))
    if mu < 1e-8:
        return 0.0
    spread = float(np.std(phase_means))
    return clamp01(spread / (mu * 0.65 + 1e-8))

def demosaic_directionality_score(channel: np.ndarray) -> float:
    """
    Lightweight directional interpolation proxy:
    compare horizontal vs vertical gradient dominance.
    Real demosaicing often leaves weak directional regularity, though this is subtle.
    """
    ch = channel.astype(np.float32)
    gx = cv2.Sobel(ch, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(ch, cv2.CV_32F, 0, 1, ksize=3)
    ex = float(np.mean(np.abs(gx)))
    ey = float(np.mean(np.abs(gy)))
    denom = ex + ey + 1e-8
    return clamp01(abs(ex - ey) / denom)

def build_top_blocks(score_map: np.ndarray, top_k: int = 12) -> list[dict[str, float | int]]:
    rows, cols = score_map.shape
    items: list[dict[str, float | int]] = []
    for r in range(rows):
        for c in range(cols):
            items.append(
                {
                    "row": int(r),
                    "col": int(c),
                    "score": float(score_map[r, c]),
                }
            )
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:top_k]

def create_overlay(image_bgr: np.ndarray, score_map: np.ndarray, out_path: Path, block_size: int = 32, threshold: float = 0.58,) -> str:
    vis = image_bgr.copy()
    rows, cols = score_map.shape
    score_map_n = normalize_map(score_map)
    for r in range(rows):
        for c in range(cols):
            score = float(score_map_n[r, c])
            if score < threshold:
                continue
            y0 = r * block_size
            x0 = c * block_size
            y1 = min(y0 + block_size, vis.shape[0])
            x1 = min(x0 + block_size, vis.shape[1])
            color = (0, int(255 * (1.0 - score)), int(255 * score))
            cv2.rectangle(vis, (x0, y0), (x1, y1), color, 1)
    cv2.imwrite(str(out_path), vis)
    return str(out_path)

# -------------------------------------------------------
# Blockwise analysis
# -------------------------------------------------------
def compute_block_maps(image_bgr: np.ndarray, block_size: int = 32,sigma: float = 1.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns:
      cfa_periodicity_map: blockwise 2x2 phase periodicity in chroma residuals
      directional_map: blockwise directional interpolation asymmetry
      energy_map: blockwise chroma residual energy
    """
    b, g, r = cv2.split(image_bgr)
    # Chroma-difference channels often expose demosaicing traces better than luminance alone.
    rg_res = highpass_residual(r.astype(np.float32) - g.astype(np.float32), sigma=sigma)
    bg_res = highpass_residual(b.astype(np.float32) - g.astype(np.float32), sigma=sigma)
    h, w = rg_res.shape
    rows, cols = block_view_shape(h, w, block_size)
    cfa_periodicity_map = np.zeros((rows, cols), dtype=np.float32)
    directional_map = np.zeros((rows, cols), dtype=np.float32)
    energy_map = np.zeros((rows, cols), dtype=np.float32)

    for r_idx in range(rows):
        for c_idx in range(cols):
            y0 = r_idx * block_size
            x0 = c_idx * block_size
            rg_block = rg_res[y0:y0 + block_size, x0:x0 + block_size]
            bg_block = bg_res[y0:y0 + block_size, x0:x0 + block_size]
            if rg_block.size < 64 or bg_block.size < 64:
                continue
            p_rg = phase_periodicity_score(rg_block)
            p_bg = phase_periodicity_score(bg_block)
            cfa_periodicity = 0.5 * (p_rg + p_bg)
            dir_rg = demosaic_directionality_score(rg_block)
            dir_bg = demosaic_directionality_score(bg_block)
            directional = 0.5 * (dir_rg + dir_bg)
            energy = 0.5 * (
                float(np.mean(np.abs(rg_block))) +
                float(np.mean(np.abs(bg_block)))
            )
            cfa_periodicity_map[r_idx, c_idx] = float(cfa_periodicity)
            directional_map[r_idx, c_idx] = float(directional)
            energy_map[r_idx, c_idx] = float(energy)
    return cfa_periodicity_map, directional_map, energy_map

# -------------------------------------------------------
# Interpretation
# -------------------------------------------------------
def interpret_cfa_demosaic(global_cfa_strength: float, block_consistency_score: float, localized_inconsistency_score: float,) -> tuple[str, str]:
    """
    Conservative interpretation.
    """
    if (
        global_cfa_strength >= 0.18
        and block_consistency_score >= 0.64
        and localized_inconsistency_score < 0.33
    ):
        return (
            "camera_like_cfa_supported",
            "CFA / demosaicing analysis detects weak but spatially coherent acquisition-like 2x2 chroma periodicity compatible with a camera capture pipeline.",
        )
    if (
        global_cfa_strength >= 0.22
        and block_consistency_score < 0.60
        and localized_inconsistency_score >= 0.38
    ):
        return (
            "localized_cfa_inconsistency",
            "CFA / demosaicing structure appears spatially inconsistent, which may indicate disrupted acquisition regularity or localized non-camera processing.",
        )
    if global_cfa_strength < 0.10:
        return (
            "weak_camera_cfa_supported",
            "CFA / demosaicing traces are weak, but this remains compatible with a modern camera pipeline or downstream processing."
        )
    return (
        "cfa_demosaic_inconclusive",
        "CFA / demosaicing analysis completed, but the evidence is not strong enough for a confident camera-like or inconsistent reading.",
    )

# -------------------------------------------------------
# Main detector
# -------------------------------------------------------
def run_cfa_demosaic_analysis(image_path: str | Path, output_dir: str | Path, block_size: int = 32,) -> dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_bgr = ensure_bgr(image_path)
    h, w = image_bgr.shape[:2]
    # Dynamic Sigma Calculation
    # Base: sigma 1.2 is tuned for approx 768-1024px max dimension
    base_sigma = 1.2
    base_dim = 1024.0
    current_max_dim = max(h, w)
    # Scale sigma: if image is 2048px, sigma becomes 2.4
    dynamic_sigma = base_sigma * (current_max_dim / base_dim)
    # Ensure sigma doesn't drop too low for very small images
    dynamic_sigma = max(0.5, dynamic_sigma)
    # Pass dynamic_sigma into your processing pipeline
    cfa_periodicity_map, directional_map, energy_map = compute_block_maps(
        image_bgr,
        block_size=block_size,
        sigma=dynamic_sigma 
    )    
    cfa_n = normalize_map(cfa_periodicity_map)
    dir_n = normalize_map(directional_map)
    energy_n = normalize_map(energy_map)
    # Weighted support:
    # CFA-like phase periodicity matters most,
    # directional asymmetry is secondary,
    # both should be discounted where chroma residual energy is too weak.
    support_map = (0.70 * cfa_n + 0.30 * dir_n) * (0.35 + 0.65 * energy_n)
    global_cfa_strength = float(np.mean(support_map)) if support_map.size else 0.0
    block_std = float(np.std(support_map)) if support_map.size else 0.0
    block_consistency_score = clamp01(1.0 - (block_std / 0.28))
    if support_map.size:
        mu = float(np.mean(support_map))
        localized_inconsistency_map = np.abs(support_map - mu)
        localized_inconsistency_score = clamp01(
            float(np.mean(localized_inconsistency_map)) / 0.20
        )
    else:
        localized_inconsistency_map = np.zeros_like(support_map)
        localized_inconsistency_score = 0.0
    pattern, note = interpret_cfa_demosaic(
        global_cfa_strength=global_cfa_strength,
        block_consistency_score=block_consistency_score,
        localized_inconsistency_score=localized_inconsistency_score,
    )
    top_blocks = build_top_blocks(localized_inconsistency_map, top_k=12)
    overlay_path = output_dir / f"{image_path.stem}_cfa_demosaic_overlay.jpg"
    overlay_path_str = create_overlay(
        image_bgr=image_bgr,
        score_map=localized_inconsistency_map,
        out_path=overlay_path,
        block_size=block_size,
    )
    return {
        "cfa_demosaic": {
            "pattern": {
                "cfa_demosaic_pattern": pattern,
                "cfa_demosaic_note": note,
            },
            "scores": {
                "global_cfa_strength": float(global_cfa_strength),
                "block_consistency_score": float(block_consistency_score),
                "localized_inconsistency_score": float(localized_inconsistency_score),
                "mean_periodicity_score": float(np.mean(cfa_n)) if cfa_n.size else 0.0,
                "mean_directionality_score": float(np.mean(dir_n)) if dir_n.size else 0.0,
                "mean_energy_score": float(np.mean(energy_n)) if energy_n.size else 0.0,
            },
            "blockwise": {
                "top_blocks": top_blocks,
            },
            "artifacts": {
                "overlay_path": overlay_path_str,
            },
        }
    }