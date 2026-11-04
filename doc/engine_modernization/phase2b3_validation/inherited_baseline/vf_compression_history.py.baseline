#vf_compression_history.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

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
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.uint8)

def normalize_map(m: np.ndarray) -> np.ndarray:
    if m.size == 0:
        return m.astype(np.float32)
    m = m.astype(np.float32)
    lo = float(np.min(m))
    hi = float(np.max(m))
    if hi - lo < 1e-8:
        return np.zeros_like(m, dtype=np.float32)
    return (m - lo) / (hi - lo)

def block_view_shape(h: int, w: int, block_size: int) -> tuple[int, int]:
    return (h + block_size - 1) // block_size, (w + block_size - 1) // block_size

def jpeg_boundary_maps(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Measure horizontal and vertical boundary strengths at 8-pixel spacing.
    """
    gray_f = gray.astype(np.float32)
    # absolute differences across neighboring pixels
    dx = np.abs(gray_f[:, 1:] - gray_f[:, :-1])
    dy = np.abs(gray_f[1:, :] - gray_f[:-1, :])
    h, w = gray.shape
    v_map = np.zeros_like(gray_f)
    h_map = np.zeros_like(gray_f)
    # vertical boundaries at x = 8k
    for x in range(8, w, 8):
        if x - 1 < dx.shape[1]:
            v_map[:, x] = dx[:, x - 1]
    # horizontal boundaries at y = 8k
    for y in range(8, h, 8):
        if y - 1 < dy.shape[0]:
            h_map[y, :] = dy[y - 1, :]

    return h_map, v_map

def offgrid_boundary_maps(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Same idea, but shifted by 4 pixels.
    Useful to compare whether the observed grid behavior is specifically 8x8 aligned.
    """
    gray_f = gray.astype(np.float32)
    dx = np.abs(gray_f[:, 1:] - gray_f[:, :-1])
    dy = np.abs(gray_f[1:, :] - gray_f[:-1, :])
    h, w = gray.shape
    v_map = np.zeros_like(gray_f)
    h_map = np.zeros_like(gray_f)
    for x in range(4, w, 8):
        if x - 1 < dx.shape[1]:
            v_map[:, x] = dx[:, x - 1]
    for y in range(4, h, 8):
        if y - 1 < dy.shape[0]:
            h_map[y, :] = dy[y - 1, :]
    return h_map, v_map

def local_std_map(gray: np.ndarray, ksize: int = 9) -> np.ndarray:
    gray_f = gray.astype(np.float32)
    mean = cv2.blur(gray_f, (ksize, ksize))
    mean_sq = cv2.blur(gray_f * gray_f, (ksize, ksize))
    var = np.maximum(mean_sq - mean * mean, 0.0)
    return np.sqrt(var)

def compute_block_score_map(gray: np.ndarray, score_img: np.ndarray, block_size: int = 32) -> np.ndarray:
    h, w = gray.shape
    rows, cols = block_view_shape(h, w, block_size)
    out = np.zeros((rows, cols), dtype=np.float32)
    for r in range(rows):
        for c in range(cols):
            y0 = r * block_size
            x0 = c * block_size
            block = score_img[y0:y0 + block_size, x0:x0 + block_size]
            if block.size == 0:
                continue
            out[r, c] = float(np.mean(block))
    return out

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

def create_compression_overlay(image_bgr: np.ndarray, score_map: np.ndarray, out_path: Path, block_size: int = 32, threshold: float = 0.55, ) -> str:
    vis = image_bgr.copy()
    score_n = normalize_map(score_map)
    rows, cols = score_n.shape
    for r in range(rows):
        for c in range(cols):
            s = float(score_n[r, c])
            if s < threshold:
                continue
            y0 = r * block_size
            x0 = c * block_size
            y1 = min(y0 + block_size, vis.shape[0])
            x1 = min(x0 + block_size, vis.shape[1])
            color = (0, int(255 * (1.0 - s)), int(255 * s))
            cv2.rectangle(vis, (x0, y0), (x1, y1), color, 1)
    cv2.imwrite(str(out_path), vis)
    return str(out_path)

def estimate_double_jpeg_likelihood(gray: np.ndarray) -> float:
    """
    Lightweight proxy:
    compare the strength of 8x8-aligned boundary energy vs. off-grid boundary energy,
    normalized by local texture level.
    """
    h_map, v_map = jpeg_boundary_maps(gray)
    h_off, v_off = offgrid_boundary_maps(gray)
    tex = local_std_map(gray, ksize=11)
    tex_n = normalize_map(tex)
    aligned = float(np.mean(h_map + v_map))
    offgrid = float(np.mean(h_off + v_off))
    if aligned <= 1e-6:
        return 0.0
    raw_ratio = max(0.0, aligned - offgrid) / (aligned + 1e-6)
    texture_penalty = 1.0 - 0.35 * float(np.mean(tex_n))
    return clamp01(raw_ratio * texture_penalty * 1.8)

def interpret_compression_history(grid_strength_score: float, grid_consistency_score: float, localized_inconsistency_score: float, double_jpeg_likelihood: float, block_anomaly_score: float,) -> tuple[str, str]:
    if (
        localized_inconsistency_score >= 0.58
        and block_anomaly_score >= 0.55
    ):
        return (
            "localized_compression_inconsistency",
            "Compression-history analysis detects localized inconsistency in block-grid behavior, which may indicate region-specific save-history or editing differences."
        )
    if (
        double_jpeg_likelihood >= 0.62
        and grid_strength_score >= 0.45
    ):
        return (
            "possible_double_jpeg_history",
            "Compression-history analysis indicates a plausible recompression or double-JPEG style save history."
        )
    if (
        grid_strength_score >= 0.40
        and grid_consistency_score < 0.52
    ):
        return (
            "block_grid_history_anomaly",
            "Compression-history analysis detects anomalous JPEG block-grid behavior that is not fully spatially coherent."
        )
    if (
        grid_strength_score >= 0.28
        and grid_consistency_score >= 0.62
        and localized_inconsistency_score < 0.35
    ):
        return (
            "single_history_jpeg_consistent",
            "Compression-history analysis is broadly consistent with a coherent single-history JPEG-style save path."
        )
    return (
        "compression_history_inconclusive",
        "Compression-history analysis did not produce a strong or specific save-history conclusion."
    )

def run_compression_history_analysis(image_path: str | Path, output_dir: str | Path, block_size: int = 32,) -> dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_bgr = ensure_bgr(image_path)
    gray = ensure_gray(image_bgr)
    h_map, v_map = jpeg_boundary_maps(gray)
    h_off, v_off = offgrid_boundary_maps(gray)
    aligned_map = h_map + v_map
    offgrid_map = h_off + v_off
    aligned_n = normalize_map(aligned_map)
    offgrid_n = normalize_map(offgrid_map)
    # texture-aware weighting
    tex = local_std_map(gray, ksize=11)
    tex_n = normalize_map(tex)
    # stronger aligned grid behavior relative to off-grid is suspicious/interesting
    grid_response = np.maximum(aligned_n - 0.65 * offgrid_n, 0.0)
    grid_response *= (0.45 + 0.55 * (1.0 - tex_n))
    grid_strength_score = float(np.mean(grid_response)) if grid_response.size else 0.0
    block_map = compute_block_score_map(gray, grid_response, block_size=block_size)
    block_map_n = normalize_map(block_map)
    block_std = float(np.std(block_map_n)) if block_map_n.size else 0.0
    grid_consistency_score = clamp01(1.0 - block_std / 0.28)
    if block_map_n.size:
        mu = float(np.mean(block_map_n))
        localized_inconsistency_score = clamp01(float(np.mean(np.abs(block_map_n - mu))) / 0.22)
        block_anomaly_score = clamp01(float(np.max(block_map_n)) - mu + localized_inconsistency_score * 0.35)
    else:
        localized_inconsistency_score = 0.0
        block_anomaly_score = 0.0
    double_jpeg_likelihood = estimate_double_jpeg_likelihood(gray)
    pattern, note = interpret_compression_history(
        grid_strength_score=grid_strength_score,
        grid_consistency_score=grid_consistency_score,
        localized_inconsistency_score=localized_inconsistency_score,
        double_jpeg_likelihood=double_jpeg_likelihood,
        block_anomaly_score=block_anomaly_score,
    )
    top_blocks = build_top_blocks(block_map_n, top_k=12)
    overlay_path = output_dir / f"{image_path.stem}_compression_history_overlay.jpg"
    overlay_path_str = create_compression_overlay(
        image_bgr=image_bgr,
        score_map=block_map_n,
        out_path=overlay_path,
        block_size=block_size,
    )
    return {
        "compression_history": {
            "pattern": {
                "compression_history_pattern": pattern,
                "compression_history_note": note,
            },
            "scores": {
                "grid_strength_score": grid_strength_score,
                "grid_consistency_score": grid_consistency_score,
                "localized_inconsistency_score": localized_inconsistency_score,
                "double_jpeg_likelihood": double_jpeg_likelihood,
                "block_anomaly_score": block_anomaly_score,
            },
            "blockwise": {
                "grid_shape": [int(block_map_n.shape[0]), int(block_map_n.shape[1])],
                "score_map": block_map_n.tolist(),
                "top_blocks": top_blocks,
            },
            "artifacts": {
                "compression_overlay_path": overlay_path_str,
            },
        }
    }