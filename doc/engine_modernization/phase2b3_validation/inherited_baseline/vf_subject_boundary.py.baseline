# vf_subject_boundary.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images


from __future__ import annotations
from pathlib import Path
from typing import Any
import cv2
import numpy as np


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def ensure_bgr(image_path: str | Path) -> np.ndarray:
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    return img

def ensure_gray(image_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return gray.astype(np.uint8)

def normalize_map(m: np.ndarray) -> np.ndarray:
    if m.size == 0:
        return m.astype(np.float32)
    m = m.astype(np.float32)
    lo = float(np.min(m))
    hi = float(np.max(m))
    if hi - lo < 1e-8:
        return np.zeros_like(m, dtype=np.float32)
    return (m - lo) / (hi - lo)

def local_std_map(gray: np.ndarray, ksize: int = 9) -> np.ndarray:
    gray_f = gray.astype(np.float32)
    mean = cv2.blur(gray_f, (ksize, ksize))
    mean_sq = cv2.blur(gray_f * gray_f, (ksize, ksize))
    var = np.maximum(mean_sq - mean * mean, 0.0)
    return np.sqrt(var)

def gradient_map(gray: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)
    return mag

def estimate_sensor_like_map(gray: np.ndarray) -> np.ndarray:
    """
    Lightweight local microstructure proxy.
    Not full CFA/PRNU; just a local residual-energy style map.
    """
    gray_f = gray.astype(np.float32)
    blur = cv2.GaussianBlur(gray_f, (0, 0), sigmaX=1.2, sigmaY=1.2)
    resid = gray_f - blur
    sensor_like = cv2.blur(np.abs(resid), (7, 7))
    return sensor_like

def make_boundary_mask(gray: np.ndarray) -> np.ndarray:
    grad = gradient_map(gray)
    grad_n = normalize_map(grad)
    # Strong-edge threshold; tune later if needed
    mask = (grad_n >= 0.35).astype(np.uint8) * 255
    # Clean a bit
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)
    return mask

def ring_masks(boundary_mask: np.ndarray, inner_radius: int = 3, outer_radius: int = 9) -> tuple[np.ndarray, np.ndarray]:
    kernel_inner = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (inner_radius * 2 + 1, inner_radius * 2 + 1))
    kernel_outer = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (outer_radius * 2 + 1, outer_radius * 2 + 1))
    dil_inner = cv2.dilate(boundary_mask, kernel_inner)
    dil_outer = cv2.dilate(boundary_mask, kernel_outer)
    inner_ring = cv2.subtract(dil_inner, boundary_mask)
    outer_ring = cv2.subtract(dil_outer, dil_inner)
    return inner_ring, outer_ring

def masked_mean(m: np.ndarray, mask: np.ndarray) -> float:
    vals = m[mask > 0]
    if vals.size == 0:
        return 0.0
    return float(np.mean(vals))

def color_diff_across_rings(image_bgr: np.ndarray, inner_ring: np.ndarray, outer_ring: np.ndarray) -> float:
    image_f = image_bgr.astype(np.float32)
    inner_vals = image_f[inner_ring > 0]
    outer_vals = image_f[outer_ring > 0]
    if inner_vals.size == 0 or outer_vals.size == 0:
        return 0.0
    inner_mean = np.mean(inner_vals, axis=0)
    outer_mean = np.mean(outer_vals, axis=0)
    diff = np.linalg.norm(inner_mean - outer_mean)
    # Normalize roughly to 0..1
    return clamp01(diff / 80.0)

def build_top_blocks(score_map: np.ndarray, top_k: int = 12) -> list[dict[str, Any]]:
    rows, cols = score_map.shape
    items: list[dict[str, Any]] = []
    for r in range(rows):
        for c in range(cols):
            items.append({
                "row": int(r),
                "col": int(c),
                "score": float(score_map[r, c]),
            })
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:top_k]

def block_score_map(gray: np.ndarray, boundary_anomaly_map: np.ndarray, block_size: int = 32) -> np.ndarray:
    h, w = gray.shape
    rows = (h + block_size - 1) // block_size
    cols = (w + block_size - 1) // block_size
    out = np.zeros((rows, cols), dtype=np.float32)
    for r in range(rows):
        for c in range(cols):
            y0 = r * block_size
            x0 = c * block_size
            block = boundary_anomaly_map[y0:y0 + block_size, x0:x0 + block_size]
            if block.size == 0:
                continue
            out[r, c] = float(np.mean(block))
    return out

def create_boundary_overlay(image_bgr: np.ndarray, anomaly_map: np.ndarray, out_path: Path, threshold: float = 0.55,) -> str:
    vis = image_bgr.copy()
    an_n = normalize_map(anomaly_map)
    hot = (an_n >= threshold).astype(np.uint8) * 255
    contours, _ = cv2.findContours(hot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(vis, contours, -1, (0, 0, 255), 2)
    cv2.imwrite(str(out_path), vis)
    return str(out_path)

def interpret_subject_boundary(
    boundary_anomaly_score: float,
    texture_mismatch: float,
    edge_softness_mismatch: float,
    sensor_mismatch: float,
    color_discontinuity: float,
    texture_region_mismatch: float,
    sharpness_region_mismatch: float,
    sensor_region_mismatch: float,
    contrast_region_mismatch: float,
) -> tuple[str, str]:
    strong_local_pair = (
        (texture_mismatch >= 0.40 and sensor_mismatch >= 0.35) or
        (edge_softness_mismatch >= 0.40 and color_discontinuity >= 0.30)
    )
    strong_regime_pair = (
        (texture_region_mismatch >= 0.42 and sharpness_region_mismatch >= 0.35) or
        (sensor_region_mismatch >= 0.35 and contrast_region_mismatch >= 0.30)
    )
    if boundary_anomaly_score >= 0.56 and (strong_local_pair or strong_regime_pair):
        return (
            "possible_subject_background_segmentation_artifact",
            "Boundary-transition analysis indicates a likely subject/background segmentation or replacement artifact, with multiple cues suggesting an implausible cutout-style or background-regime transition."
        )
    if boundary_anomaly_score >= 0.38:
        return (
            "possible_boundary_transition_inconsistency",
            "Boundary-transition analysis detects moderate inconsistency across the subject/background transition, though the evidence is not strong enough for a more specific segmentation-artifact conclusion."
        )
    return (
        "boundary_semantic_inconclusive",
        "Boundary-transition analysis did not reveal a strong subject/background segmentation inconsistency."
    )

def region_masks(boundary_mask: np.ndarray, inner_radius: int = 6, outer_radius: int = 24) -> tuple[np.ndarray, np.ndarray]:
    """
    Build broader subject-adjacent inside/outside regions around the boundary.
    inner_region: close to the boundary, intended to sample subject-side structure
    outer_region: broader outside band, intended to sample background-side structure
    """
    kernel_inner = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (inner_radius * 2 + 1, inner_radius * 2 + 1))
    kernel_outer = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (outer_radius * 2 + 1, outer_radius * 2 + 1))
    dil_inner = cv2.dilate(boundary_mask, kernel_inner)
    dil_outer = cv2.dilate(boundary_mask, kernel_outer)
    near_region = cv2.subtract(dil_inner, boundary_mask)
    wide_outer_region = cv2.subtract(dil_outer, dil_inner)
    return near_region, wide_outer_region

def local_contrast_map(gray: np.ndarray, ksize: int = 9) -> np.ndarray:
    gray_f = gray.astype(np.float32)
    blur = cv2.GaussianBlur(gray_f, (0, 0), sigmaX=max(1.0, ksize / 6.0), sigmaY=max(1.0, ksize / 6.0))
    contrast = np.abs(gray_f - blur)
    return contrast

def run_subject_boundary_analysis(image_path: str | Path, output_dir: str | Path, block_size: int = 32,) -> dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_bgr = ensure_bgr(image_path)
    gray = ensure_gray(image_bgr)
    
    texture = local_std_map(gray, ksize=9)
    grad = gradient_map(gray)
    sensor_like = estimate_sensor_like_map(gray)
    contrast = local_contrast_map(gray, ksize=9)
    texture_n = normalize_map(texture)
    grad_n = normalize_map(grad)
    sensor_n = normalize_map(sensor_like)
    contrast_n = normalize_map(contrast)
    boundary_mask = make_boundary_mask(gray)
    inner_ring, outer_ring = ring_masks(boundary_mask, inner_radius=3, outer_radius=9)
    near_region, wide_outer_region = region_masks(boundary_mask, inner_radius=6, outer_radius=24)
    texture_in = masked_mean(texture_n, inner_ring)
    texture_out = masked_mean(texture_n, outer_ring)
    texture_mismatch = clamp01(abs(texture_in - texture_out) / 0.20)
    grad_in = masked_mean(grad_n, inner_ring)
    grad_out = masked_mean(grad_n, outer_ring)
    edge_softness_mismatch = clamp01(abs(grad_in - grad_out) / 0.20)
    sensor_in = masked_mean(sensor_n, inner_ring)
    sensor_out = masked_mean(sensor_n, outer_ring)
    sensor_mismatch = clamp01(abs(sensor_in - sensor_out) / 0.18)
    color_discontinuity = color_diff_across_rings(image_bgr, inner_ring, outer_ring)
    texture_near = masked_mean(texture_n, near_region)
    texture_wide = masked_mean(texture_n, wide_outer_region)
    texture_region_mismatch = clamp01(abs(texture_near - texture_wide) / 0.18)
    grad_near = masked_mean(grad_n, near_region)
    grad_wide = masked_mean(grad_n, wide_outer_region)
    sharpness_region_mismatch = clamp01(abs(grad_near - grad_wide) / 0.18)
    sensor_near = masked_mean(sensor_n, near_region)
    sensor_wide = masked_mean(sensor_n, wide_outer_region)
    sensor_region_mismatch = clamp01(abs(sensor_near - sensor_wide) / 0.16)
    contrast_near = masked_mean(contrast_n, near_region)
    contrast_wide = masked_mean(contrast_n, wide_outer_region)
    contrast_region_mismatch = clamp01(abs(contrast_near - contrast_wide) / 0.18)
    boundary_anomaly_score = clamp01(
        0.16 * texture_mismatch +
        0.14 * edge_softness_mismatch +
        0.14 * sensor_mismatch +
        0.12 * color_discontinuity +
        0.16 * texture_region_mismatch +
        0.12 * sharpness_region_mismatch +
        0.10 * sensor_region_mismatch +
        0.06 * contrast_region_mismatch
    )
    # Pixelwise anomaly emphasis near boundaries only
    boundary_zone = cv2.dilate(boundary_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    local_map = (
        0.30 * np.abs(texture_n - cv2.blur(texture_n, (15, 15))) +
        0.25 * np.abs(grad_n - cv2.blur(grad_n, (15, 15))) +
        0.25 * np.abs(sensor_n - cv2.blur(sensor_n, (15, 15)))
    ).astype(np.float32)
    local_map *= (boundary_zone > 0).astype(np.float32)
    local_map_n = normalize_map(local_map)
    block_map = block_score_map(gray, local_map_n, block_size=block_size)
    top_blocks = build_top_blocks(block_map, top_k=12)
    overlay_path = output_dir / f"{image_path.stem}_subject_boundary_overlay.jpg"
    overlay_path_str = create_boundary_overlay(image_bgr, local_map_n, overlay_path)
    pattern, note = interpret_subject_boundary(
        boundary_anomaly_score=boundary_anomaly_score,
        texture_mismatch=texture_mismatch,
        edge_softness_mismatch=edge_softness_mismatch,
        sensor_mismatch=sensor_mismatch,
        color_discontinuity=color_discontinuity,
        texture_region_mismatch=texture_region_mismatch,
        sharpness_region_mismatch=sharpness_region_mismatch,
        sensor_region_mismatch=sensor_region_mismatch,
        contrast_region_mismatch=contrast_region_mismatch,
    )
    return {
        "subject_boundary": {
            "pattern": {
                "subject_boundary_pattern": pattern,
                "subject_boundary_note": note,
            },
        "scores": {
            "boundary_anomaly_score": boundary_anomaly_score,
            "texture_mismatch": texture_mismatch,
            "edge_softness_mismatch": edge_softness_mismatch,
            "sensor_mismatch": sensor_mismatch,
            "color_discontinuity": color_discontinuity,
            "texture_region_mismatch": texture_region_mismatch,
            "sharpness_region_mismatch": sharpness_region_mismatch,
            "sensor_region_mismatch": sensor_region_mismatch,
            "contrast_region_mismatch": contrast_region_mismatch,
        },
        "blockwise": {
                "grid_shape": [int(block_map.shape[0]), int(block_map.shape[1])],
                "score_map": block_map.tolist(),
                "top_blocks": top_blocks,
            },
            "artifacts": {
                "subject_boundary_overlay_path": overlay_path_str,
            },
        }
    }