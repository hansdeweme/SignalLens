#vf_sensor_origin.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
# CFA colour filter array - demosaicing consistency module
# We use a high-pass residual + 2×2 periodicity consistency approach, real camera images often retain weak CFA / demosaicing / acquisition periodicity
# synthetic images, screenshots, and some heavily manipulated regions may show weaker periodic acquisition traces, spatial inconsistency in those traces
# output patterns: camera_like_acquisition_supported, sensor_origin_inconclusive, weak_or_absent_sensor_origin_traces, localized_sensor_trace_inconsistency
#

from __future__ import annotations
from pathlib import Path
import math
from typing import Any
import cv2
import numpy as np

#----------------------------------------
# Helpers
#----------------------------------------

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def ensure_uint8_gray(image_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    if gray.dtype != np.uint8:
        gray = np.clip(gray, 0, 255).astype(np.uint8)
    return gray

def highpass_residual(gray: np.ndarray) -> np.ndarray:
    gray_f = gray.astype(np.float32)
    blur = cv2.GaussianBlur(gray_f, (0, 0), sigmaX=1.2, sigmaY=1.2)
    resid = gray_f - blur
    return resid

def block_view_shape(h: int, w: int, block_size: int) -> tuple[int, int]:
    return math.ceil(h / block_size), math.ceil(w / block_size)

def compute_block_maps(residual: np.ndarray, block_size: int = 32, ) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
      periodicity_map: blockwise 2x2 acquisition-like periodicity strength
      energy_map: blockwise residual energy
    """
    h, w = residual.shape
    rows, cols = block_view_shape(h, w, block_size)
    periodicity_map = np.zeros((rows, cols), dtype=np.float32)
    energy_map = np.zeros((rows, cols), dtype=np.float32)
    for r in range(rows):
        for c in range(cols):
            y0 = r * block_size
            x0 = c * block_size
            block = residual[y0:y0 + block_size, x0:x0 + block_size]
            if block.size < 16:
                continue
            energy = float(np.mean(np.abs(block)))
            energy_map[r, c] = energy
            # 2x2 phase means
            p00 = float(np.mean(np.abs(block[0::2, 0::2]))) if block[0::2, 0::2].size else 0.0
            p01 = float(np.mean(np.abs(block[0::2, 1::2]))) if block[0::2, 1::2].size else 0.0
            p10 = float(np.mean(np.abs(block[1::2, 0::2]))) if block[1::2, 0::2].size else 0.0
            p11 = float(np.mean(np.abs(block[1::2, 1::2]))) if block[1::2, 1::2].size else 0.0
            phases = np.array([p00, p01, p10, p11], dtype=np.float32)
            mu = float(np.mean(phases)) + 1e-6
            sigma = float(np.std(phases))
            # Relative phase structure: higher can indicate acquisition periodicity
            periodicity = sigma / mu
            periodicity_map[r, c] = periodicity
    return periodicity_map, energy_map

def normalize_map(m: np.ndarray) -> np.ndarray:
    if m.size == 0:
        return m
    lo = float(np.min(m))
    hi = float(np.max(m))
    if hi - lo < 1e-8:
        return np.zeros_like(m, dtype=np.float32)
    return (m - lo) / (hi - lo)

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

def create_sensor_overlay(image_bgr: np.ndarray, score_map: np.ndarray, out_path: Path, block_size: int = 32,) -> str:
    vis = image_bgr.copy()
    rows, cols = score_map.shape
    score_map_n = normalize_map(score_map)
    for r in range(rows):
        for c in range(cols):
            score = float(score_map_n[r, c])
            if score < 0.55:
                continue
            y0 = r * block_size
            x0 = c * block_size
            y1 = min(y0 + block_size, vis.shape[0])
            x1 = min(x0 + block_size, vis.shape[1])
            color = (0, int(255 * (1.0 - score)), int(255 * score))
            cv2.rectangle(vis, (x0, y0), (x1, y1), color, 1)
    cv2.imwrite(str(out_path), vis)
    return str(out_path)

def interpret_sensor_origin(global_trace_strength: float, block_consistency_score: float, localized_inconsistency_score: float,) -> tuple[str, str]:
    # ✅ Camera-like support (phone + DSLR)
    if (
        global_trace_strength >= 0.035
        and block_consistency_score >= 0.65
        and localized_inconsistency_score < 0.35
    ):
        return (
            "camera_like_acquisition_supported",
            "Sensor-origin analysis detects spatially coherent microstructure compatible with a camera capture pipeline."
        )
    # 🚨 Suspicious ONLY if clearly extreme
    if (
        global_trace_strength >= 0.14
        and block_consistency_score < 0.60
        and localized_inconsistency_score >= 0.40
    ):
        return (
            "localized_sensor_trace_inconsistency",
            "Microstructure is unusually strong and spatially inconsistent, which may indicate a disrupted or non-standard acquisition pattern."
        )
    # Very weak → inconclusive (not suspicious!)
    if global_trace_strength < 0.03:
        return (
            "weak_camera_pipeline_supported",
            "Sensor-origin microstructure is weak but not abnormal, which remains compatible with a modern camera processing pipeline."
        )
    return (
        "sensor_origin_inconclusive",
        "Sensor-origin analysis did not produce a strong camera-like or strongly inconsistent reading."
    )
    
#-----------------------------------------------
# Detector Analysis
#-----------------------------------------------
def run_sensor_origin_analysis(image_path: str | Path, output_dir: str | Path, block_size: int = 32,) -> dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = ensure_uint8_gray(image_bgr)
    residual = highpass_residual(gray)
    periodicity_map, energy_map = compute_block_maps(residual, block_size=block_size)
    # Normalize
    periodicity_n = normalize_map(periodicity_map)
    energy_n = normalize_map(energy_map)
    # We care most about periodic residual structure, but only where some residual energy exists
    support_map = periodicity_n * (0.35 + 0.65 * energy_n)
    global_trace_strength = float(np.mean(support_map)) if support_map.size else 0.0
    # Consistency: if support varies too wildly across blocks, consistency drops
    block_std = float(np.std(support_map)) if support_map.size else 0.0
    block_consistency_score = clamp01(1.0 - (block_std / 0.30))
    # Inconsistency: strong if some blocks differ strongly from overall support
    if support_map.size:
        mu = float(np.mean(support_map))
        localized_inconsistency_score = clamp01(float(np.mean(np.abs(support_map - mu))) / 0.22)
    else:
        localized_inconsistency_score = 0.0
    pattern, note = interpret_sensor_origin(
        global_trace_strength=global_trace_strength,
        block_consistency_score=block_consistency_score,
        localized_inconsistency_score=localized_inconsistency_score,
    )
    top_blocks = build_top_blocks(np.abs(support_map - np.mean(support_map)), top_k=12)
    overlay_path = output_dir / f"{image_path.stem}_sensor_origin_overlay.jpg"
    overlay_path_str = create_sensor_overlay(
        image_bgr=image_bgr,
        score_map=np.abs(support_map - np.mean(support_map)),
        out_path=overlay_path,
        block_size=block_size,
    )
    # Debug prints
    #print("global_trace_strength:", global_trace_strength)
    #print("global_periodicity_strength:", float(np.mean(periodicity_n)) if periodicity_n.size else 0.0)
    #print("block_consistency_score:", block_consistency_score)
    #print("localized_inconsistency_score:", localized_inconsistency_score)
    #print("periodicity_map min/max/mean:", float(np.min(periodicity_n)), float(np.max(periodicity_n)), float(np.mean(periodicity_n)))
    #print("energy_map min/max/mean:", float(np.min(energy_n)), float(np.max(energy_n)), float(np.mean(energy_n)))
    #print("support_map min/max/mean:", float(np.min(support_map)), float(np.max(support_map)), float(np.mean(support_map)))   
    return {
        "sensor_origin": {
            "pattern": {
                "sensor_origin_pattern": pattern,
                "sensor_origin_note": note,
            },
            "scores": {
                "global_trace_strength": global_trace_strength,
                "global_periodicity_strength": float(np.mean(periodicity_n)) if periodicity_n.size else 0.0,
                "block_consistency_score": block_consistency_score,
                "localized_inconsistency_score": localized_inconsistency_score,
            },
            "blockwise": {
                "grid_shape": [int(support_map.shape[0]), int(support_map.shape[1])],
                "score_map": support_map.tolist(),
                "top_blocks": top_blocks,
            },
            "artifacts": {
                "sensor_overlay_path": overlay_path_str,
            },
        }
    }
