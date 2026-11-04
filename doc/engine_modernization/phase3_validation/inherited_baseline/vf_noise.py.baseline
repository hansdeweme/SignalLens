#vf_noise.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages#
#
# For each image: residual map, overlay on original, overlay on residual map, JSON summary - this mirrors ELA design in vf_ela.py
# Unlike ELA, this is not about JPEG compression mismatch.This is more about: local texture inconsistency, smoothing mismatch, different “noise character” between regions
# So if: face is very smooth, background is textured, inserted object has different residual behavior, AI-enhanced region is over-cleaned, 
#    we may see localized hotspots or unusual patterns.

from __future__ import annotations
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
# local imports 
from vf_overlay import create_hotspot_overlay

@dataclass
class NoiseMetrics:
    input_format: str
    blur_radius: float
    mean_residual: float
    std_residual: float
    max_residual: int
    p95_residual: float
    high_residual_pixel_ratio: float
    residual_scale_factor: float
    status: str
    note: str

def load_rgb_image(path: Path) -> Image.Image:
    img = Image.open(path)
    return img.convert("RGB")

def rgb_to_luminance_array(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img, dtype=np.float32)
    # ITU-R BT.601 luminance approximation
    y = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    return y

def compute_residual_array(luma: np.ndarray, blur_radius: float = 1.5) -> np.ndarray:
    """
    Residual = |original luminance - blurred luminance|
    """
    luma_img = Image.fromarray(np.clip(luma, 0, 255).astype(np.uint8))
    blurred_img = luma_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred = np.asarray(blurred_img, dtype=np.float32)
    residual = np.abs(luma - blurred)
    return residual.astype(np.float32)

def compute_scale_factor(arr: np.ndarray, min_scale: float = 1.0, fallback_scale: float = 10.0) -> float:
    max_val = float(arr.max()) if arr.size else 0.0
    if max_val <= 0:
        return fallback_scale
    return max(min_scale, 255.0 / max_val)

def create_residual_visual(residual: np.ndarray, scale_factor: float) -> Image.Image:
    vis = np.clip(residual * scale_factor, 0, 255).astype(np.uint8)
    return Image.fromarray(vis, mode="L")

def compute_noise_metrics(
    residual: np.ndarray,
    input_format: str,
    blur_radius: float,
    scale_factor: float,
) -> NoiseMetrics:
    mean_residual = float(residual.mean())
    std_residual = float(residual.std())
    max_residual = int(residual.max()) if residual.size else 0
    p95_residual = float(np.percentile(residual, 95)) if residual.size else 0.0
    high_threshold = 20
    high_residual_pixel_ratio = float((residual >= high_threshold).mean()) if residual.size else 0.0
    return NoiseMetrics(
        input_format=input_format,
        blur_radius=blur_radius,
        mean_residual=mean_residual,
        std_residual=std_residual,
        max_residual=max_residual,
        p95_residual=p95_residual,
        high_residual_pixel_ratio=high_residual_pixel_ratio,
        residual_scale_factor=scale_factor,
        status="ok",
        note="Residual analysis completed using luminance minus Gaussian-blurred luminance.",
    )

def compute_blockwise_residual_stats(
    residual: np.ndarray,
    block_size: int = 64,
    top_n: int = 10,
) -> Dict[str, Any]:
    h, w = residual.shape
    grid_rows = math.ceil(h / block_size)
    grid_cols = math.ceil(w / block_size)
    blocks: List[Dict[str, Any]] = []
    block_means: List[float] = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            y0 = row * block_size
            y1 = min((row + 1) * block_size, h)
            x0 = col * block_size
            x1 = min((col + 1) * block_size, w)
            block = residual[y0:y1, x0:x1]
            block_mean = float(block.mean()) if block.size else 0.0
            block_max = float(block.max()) if block.size else 0.0
            block_p95 = float(np.percentile(block, 95)) if block.size else 0.0
            blocks.append({
                "row": row,
                "col": col,
                "mean": block_mean,
                "max": block_max,
                "p95": block_p95,
            })
            block_means.append(block_mean)
    means = np.array(block_means, dtype=np.float32)
    median_block_mean = float(np.median(means)) if means.size else 0.0
    max_block_mean = float(np.max(means)) if means.size else 0.0
    p95_block_mean = float(np.percentile(means, 95)) if means.size else 0.0
    total_block_energy = float(np.sum(means)) if means.size else 0.0
    if median_block_mean <= 1e-8:
        max_block_to_median_ratio = float("inf") if max_block_mean > 0 else 1.0
    else:
        max_block_to_median_ratio = max_block_mean / median_block_mean
    hot_threshold = max(p95_block_mean, median_block_mean * 2.0)
    hot_mask = means >= hot_threshold if means.size else np.array([], dtype=bool)
    hot_block_ratio = float(hot_mask.mean()) if hot_mask.size else 0.0
    if means.size:
        top_k = max(1, math.ceil(0.05 * len(means)))
        top_vals = np.sort(means)[-top_k:]
        top_5pct_block_energy_share = (
            float(np.sum(top_vals)) / total_block_energy
            if total_block_energy > 1e-8 else 0.0
        )
    else:
        top_5pct_block_energy_share = 0.0
    top_blocks = sorted(blocks, key=lambda b: b["mean"], reverse=True)[:top_n]
    hottest_block = None
    if top_blocks:
        hottest_block = {
            "row": top_blocks[0]["row"],
            "col": top_blocks[0]["col"],
            "mean": top_blocks[0]["mean"],
        }
    return {
        "block_size": block_size,
        "grid_rows": grid_rows,
        "grid_cols": grid_cols,
        "median_block_mean": median_block_mean,
        "max_block_mean": max_block_mean,
        "p95_block_mean": p95_block_mean,
        "max_block_to_median_ratio": max_block_to_median_ratio,
        "hot_block_ratio": hot_block_ratio,
        "top_5pct_block_energy_share": top_5pct_block_energy_share,
        "hottest_block": hottest_block,
        "top_blocks": [
            {"row": b["row"], "col": b["col"], "mean": b["mean"]}
            for b in top_blocks
        ],
    }

def classify_noise_pattern(block_stats: Dict[str, Any]) -> Dict[str, Any]:
    ratio = block_stats["max_block_to_median_ratio"]
    hot_ratio = block_stats["hot_block_ratio"]
    concentration = block_stats["top_5pct_block_energy_share"]
    if ratio >= 4.0 and hot_ratio <= 0.10 and concentration >= 0.30:
        return {
            "noise_pattern": "localized_residual_anomaly",
            "noise_signal_strength": "medium",
            "noise_note": (
                "Residual energy is concentrated in a limited number of blocks, "
                "which may indicate localized smoothing, enhancement, or compositing mismatch."
            ),
        }
    if ratio < 2.0 and hot_ratio > 0.15 and concentration < 0.20:
        return {
            "noise_pattern": "uniform_residual_pattern",
            "noise_signal_strength": "low",
            "noise_note": (
                "Residual activity is relatively spread out, suggesting globally consistent texture/noise behavior."
            ),
        }
    return {
        "noise_pattern": "noise_inconclusive",
        "noise_signal_strength": "low",
        "noise_note": (
            "Residual analysis does not clearly indicate either a localized anomaly or a uniform pattern."
        ),
    }


def run_noise_analysis(
    image_path: Path,
    output_dir: Path,
    blur_radius: float = 1.5,
    block_size: int = 64,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    original = load_rgb_image(image_path)
    input_format = image_path.suffix.lower()
    residual_image_path = output_dir / f"{image_path.stem}_noise_residual.png"
    overlay_original_path = output_dir / f"{image_path.stem}_noise_overlay_original.png"
    overlay_residual_path = output_dir / f"{image_path.stem}_noise_overlay_residual.png"
    noise_json_path = output_dir / f"{image_path.stem}_noise.json"
    luma = rgb_to_luminance_array(original)
    residual = compute_residual_array(luma=luma, blur_radius=blur_radius)
    scale_factor = compute_scale_factor(residual)
    residual_visual = create_residual_visual(residual, scale_factor)
    residual_visual.save(residual_image_path)
    metrics = compute_noise_metrics(
        residual=residual,
        input_format=input_format,
        blur_radius=blur_radius,
        scale_factor=scale_factor,
    )
    block_stats = compute_blockwise_residual_stats(
        residual=residual,
        block_size=block_size,
    )
    pattern = classify_noise_pattern(block_stats)
    create_hotspot_overlay(
        base_image_path=image_path,
        output_path=overlay_original_path,
        top_blocks=block_stats.get("top_blocks", []),
        block_size=block_stats["block_size"],
        max_blocks=10,
    )
    create_hotspot_overlay(
        base_image_path=residual_image_path,
        output_path=overlay_residual_path,
        top_blocks=block_stats.get("top_blocks", []),
        block_size=block_stats["block_size"],
        max_blocks=10,
        outline_color="yellow",
    )
    payload = {
        "file": {
            "input_path": str(image_path),
            "input_name": image_path.name,
        },
        "noise": {
            **asdict(metrics),
            "residual_image_path": str(residual_image_path),
            "noise_overlay_original_path": str(overlay_original_path),
            "noise_overlay_residual_path": str(overlay_residual_path),
            "blockwise": block_stats,
            "pattern": pattern,
        },
    }
    noise_json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload