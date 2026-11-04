#vf_boundary_focus.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import cv2
import numpy as np

def _load_mask(path: str | Path) -> np.ndarray:
    m = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"Failed to load mask: {path}")
    return (m > 127).astype(np.uint8)

def _safe_mean(arr: np.ndarray, mask: np.ndarray) -> float:
    vals = arr[mask > 0]
    if vals.size == 0:
        return 0.0
    return float(np.mean(vals))

def _safe_std(arr: np.ndarray, mask: np.ndarray) -> float:
    vals = arr[mask > 0]
    if vals.size == 0:
        return 0.0
    return float(np.std(vals))

def _safe_ratio(a: float, b: float) -> float:
    return float(a / (b + 1e-6))

def _normalize_to_u8(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype(np.float32)
    lo = float(arr.min())
    hi = float(arr.max())
    if hi <= lo:
        return np.zeros_like(arr, dtype=np.uint8)
    out = (arr - lo) / (hi - lo)
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    return out

def _extract_ela_map(ela_payload: Dict[str, Any]) -> np.ndarray:
    """
    Extract a usable ELA intensity map from the actual vf_ela payload.
    Prefer the raw ELA image itself over hotspot overlays.
    """
    ela = ela_payload.get("ela", {})
    # First try the real ELA visualization
    for key in (
        "ela_image_path",
        "hotspot_overlay_diff_path",
        "hotspot_overlay_original_path",
    ):
        path = ela.get(key)
        if path and Path(path).exists():
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                return img.astype(np.float32)
    # Optional fallback if a numeric map is ever embedded later
    for key in ("ela_map", "ela_score_map", "ela_block_map"):
        arr = ela.get(key)
        if arr is not None:
            arr = np.asarray(arr, dtype=np.float32)
            if arr.ndim == 2:
                return arr
    raise ValueError("Could not extract usable ELA map from payload.")

def _extract_noise_map(noise_payload: Dict[str, Any]) -> np.ndarray:
    """
    Extract a usable residual/noise map from the actual vf_noise payload.
    Prefer the residual image itself over overlays.
    """
    noise = noise_payload.get("noise", {})
    for key in (
        "residual_image_path",
        "noise_overlay_residual_path",
        "noise_overlay_original_path",
    ):
        path = noise.get(key)
        if path and Path(path).exists():
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                return img.astype(np.float32)
    for key in ("noise_map", "residual_map", "noise_score_map", "noise_block_map"):
        arr = noise.get(key)
        if arr is not None:
            arr = np.asarray(arr, dtype=np.float32)
            if arr.ndim == 2:
                return arr
    raise ValueError("Could not extract usable residual/noise map from payload.")

def _resize_to_mask_shape(arr: np.ndarray, shape_hw: tuple[int, int]) -> np.ndarray:
    h, w = shape_hw
    if arr.shape[:2] == (h, w):
        return arr.astype(np.float32)
    return cv2.resize(arr.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)

def _make_preview(
    ela_map: np.ndarray,
    noise_map: np.ndarray,
    subject_mask: np.ndarray,
    boundary_mask: np.ndarray,
    background_mask: np.ndarray,
) -> np.ndarray:
    """
    RGB preview:
    - red   = ELA intensity
    - green = residual intensity
    - boundary outline emphasized
    """
    ela_u8 = _normalize_to_u8(ela_map)
    noise_u8 = _normalize_to_u8(noise_map)
    h, w = ela_u8.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    out[..., 0] = ela_u8
    out[..., 1] = noise_u8
    out[..., 2] = ((subject_mask * 60) + (background_mask * 20)).astype(np.uint8)
    # emphasize boundary band
    out[boundary_mask > 0] = np.maximum(out[boundary_mask > 0], np.array([255, 180, 60], dtype=np.uint8))
    return out

def run_boundary_focus_analysis(
    image_path: str | Path,
    region_masks_payload: Dict[str, Any],
    ela_payload: Dict[str, Any],
    noise_payload: Dict[str, Any],
    output_dir: str | Path,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    masks = region_masks_payload["region_masks"]
    subject_mask = _load_mask(masks["subject_mask_path"])
    boundary_mask = _load_mask(masks["boundary_band_path"])
    background_mask = _load_mask(masks["background_mask_path"])
    ela_map = _extract_ela_map(ela_payload)
    noise_map = _extract_noise_map(noise_payload)
    target_shape = subject_mask.shape
    ela_map = _resize_to_mask_shape(ela_map, target_shape)
    noise_map = _resize_to_mask_shape(noise_map, target_shape)
    # --------------------------------------------------
    # Region stats
    # --------------------------------------------------
    ela_subject_mean = _safe_mean(ela_map, subject_mask)
    ela_boundary_mean = _safe_mean(ela_map, boundary_mask)
    ela_background_mean = _safe_mean(ela_map, background_mask)
    noise_subject_mean = _safe_mean(noise_map, subject_mask)
    noise_boundary_mean = _safe_mean(noise_map, boundary_mask)
    noise_background_mean = _safe_mean(noise_map, background_mask)
    ela_subject_std = _safe_std(ela_map, subject_mask)
    ela_boundary_std = _safe_std(ela_map, boundary_mask)
    ela_background_std = _safe_std(ela_map, background_mask)
    noise_subject_std = _safe_std(noise_map, subject_mask)
    noise_boundary_std = _safe_std(noise_map, boundary_mask)
    noise_background_std = _safe_std(noise_map, background_mask)
    # --------------------------------------------------
    # Comparative features
    # --------------------------------------------------
    ela_boundary_boost = ela_boundary_mean - max(ela_subject_mean, ela_background_mean)
    noise_boundary_boost = noise_boundary_mean - max(noise_subject_mean, noise_background_mean)
    ela_boundary_ratio = _safe_ratio(ela_boundary_mean, max(ela_subject_mean, ela_background_mean))
    noise_boundary_ratio = _safe_ratio(noise_boundary_mean, max(noise_subject_mean, noise_background_mean))
    combined_boundary_boost = 0.5 * ela_boundary_boost + 0.5 * noise_boundary_boost
    combined_boundary_ratio = 0.5 * ela_boundary_ratio + 0.5 * noise_boundary_ratio
    # transition anomaly: boundary elevated relative to BOTH sides
    transition_anomaly_score = float(
        0.5 * (ela_boundary_mean - 0.5 * (ela_subject_mean + ela_background_mean)) +
        0.5 * (noise_boundary_mean - 0.5 * (noise_subject_mean + noise_background_mean))
    )
    # --------------------------------------------------
    # Interpretation
    # --------------------------------------------------
    pattern = "boundary_processing_inconclusive"
    if (
        combined_boundary_ratio >= 1.35
        and combined_boundary_boost > 8.0
        and transition_anomaly_score > 6.0
    ):
        pattern = "boundary_focused_transition_anomaly"
    elif (
        (ela_boundary_ratio >= 1.22 and ela_boundary_boost > 5.0) or
        (noise_boundary_ratio >= 1.22 and noise_boundary_boost > 5.0) or
        (combined_boundary_ratio >= 1.20 and combined_boundary_boost > 4.0)
    ):
        pattern = "boundary_focused_processing_mismatch"
    elif (
        0.92 <= ela_boundary_ratio <= 1.08 and
        0.92 <= noise_boundary_ratio <= 1.08 and
        abs(ela_boundary_boost) < 2.0 and
        abs(noise_boundary_boost) < 2.0
    ):
        pattern = "boundary_processing_convergence_supported"
    # --------------------------------------------------
    # Artifacts
    # --------------------------------------------------
    preview = _make_preview(
        ela_map=ela_map,
        noise_map=noise_map,
        subject_mask=subject_mask,
        boundary_mask=boundary_mask,
        background_mask=background_mask,
    )
    preview_path = output_dir / f"{image_path.stem}_boundary_focus_preview.png"
    cv2.imwrite(str(preview_path), cv2.cvtColor(preview, cv2.COLOR_RGB2BGR))
    return {
        "boundary_focus": {
            "pattern": pattern,
            "region_stats": {
                "ela_subject_mean": float(ela_subject_mean),
                "ela_boundary_mean": float(ela_boundary_mean),
                "ela_background_mean": float(ela_background_mean),
                "noise_subject_mean": float(noise_subject_mean),
                "noise_boundary_mean": float(noise_boundary_mean),
                "noise_background_mean": float(noise_background_mean),
                "ela_subject_std": float(ela_subject_std),
                "ela_boundary_std": float(ela_boundary_std),
                "ela_background_std": float(ela_background_std),
                "noise_subject_std": float(noise_subject_std),
                "noise_boundary_std": float(noise_boundary_std),
                "noise_background_std": float(noise_background_std),
            },
            "comparative_features": {
                "ela_boundary_boost": float(ela_boundary_boost),
                "noise_boundary_boost": float(noise_boundary_boost),
                "ela_boundary_ratio": float(ela_boundary_ratio),
                "noise_boundary_ratio": float(noise_boundary_ratio),
                "combined_boundary_boost": float(combined_boundary_boost),
                "combined_boundary_ratio": float(combined_boundary_ratio),
                "transition_anomaly_score": float(transition_anomaly_score),
            },
            "artifacts": {
                "boundary_focus_preview_path": str(preview_path),
            },
        }
    }