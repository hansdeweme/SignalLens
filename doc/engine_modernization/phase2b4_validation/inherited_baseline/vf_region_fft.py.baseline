#vf_region_fft.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#

import numpy as np
import cv2
from pathlib import Path
from typing import Any, Dict, Tuple
# locaal import, reuse existing FFT helpers
from vf_fft import run_fft_analysis


def _load_mask(path: str | Path) -> np.ndarray:
    m = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"Failed to load mask: {path}")
    return (m > 127).astype(np.uint8)

def _extract_fft_metrics(payload: Dict[str, Any]) -> Dict[str, float]:
    fft = payload["fft"]
    return {
        "fft_anomaly_score": float(fft.get("fft_anomaly_score", 0.0)),
        "peak_periodicity_score": float(fft.get("peak_periodicity_score", 0.0)),
        "peak_symmetry_score": float(fft.get("peak_symmetry_score", 0.0)),
        "anisotropy_score": float(fft.get("anisotropy_score", 0.0)),
        "axis_bias_score": float(fft.get("axis_bias_score", 0.0)),
        "grid_response_score": float(fft.get("grid_response_score", 0.0)),
    }

def _mask_bbox(mask: np.ndarray) -> Tuple[int, int, int, int] | None:
    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        return None
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    return x0, y0, x1, y1

def _expand_bbox(
    bbox: Tuple[int, int, int, int],
    shape: Tuple[int, int],
    pad: int = 24,
) -> Tuple[int, int, int, int]:
    h, w = shape
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(w - 1, x1 + pad)
    y1 = min(h - 1, y1 + pad)
    return x0, y0, x1, y1

def _soften_mask(mask_crop: np.ndarray, blur_sigma: float = 5.0) -> np.ndarray:
    """
    Convert binary crop mask to soft mask in [0,1].
    """
    m = mask_crop.astype(np.float32)
    if blur_sigma > 0:
        m = cv2.GaussianBlur(m, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)
    m = np.clip(m, 0.0, 1.0)
    return m

def _extract_soft_region_crop(
    image_gray: np.ndarray,
    mask: np.ndarray,
    pad: int = 24,
    blur_sigma: float = 5.0,
    fill_mode: str = "mean",
) -> np.ndarray:
    """
    Extract a cropped softly-masked patch for FFT analysis.
    fill_mode:
        "mean"  -> fill outside region with mean intensity from inside region
        "blur"  -> fill outside region with a blurred local crop
    """
    bbox = _mask_bbox(mask)
    if bbox is None:
        raise ValueError("Mask is empty; cannot extract region crop.")
    x0, y0, x1, y1 = _expand_bbox(bbox, image_gray.shape, pad=pad)
    img_crop = image_gray[y0:y1 + 1, x0:x1 + 1].astype(np.float32)
    mask_crop = mask[y0:y1 + 1, x0:x1 + 1].astype(np.uint8)
    soft_mask = _soften_mask(mask_crop, blur_sigma=blur_sigma)
    inside_vals = img_crop[mask_crop > 0]
    region_mean = float(np.mean(inside_vals)) if inside_vals.size else float(np.mean(img_crop))
    if fill_mode == "blur":
        background_fill = cv2.GaussianBlur(img_crop, (0, 0), sigmaX=7.0, sigmaY=7.0)
    else:
        background_fill = np.full_like(img_crop, region_mean, dtype=np.float32)
    out = img_crop * soft_mask + background_fill * (1.0 - soft_mask)
    # normalize back to uint8-safe grayscale range
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out

def _align_mask_to_image(mask: np.ndarray, image_gray: np.ndarray) -> np.ndarray:
    if mask.shape == image_gray.shape:
        return mask.astype(np.uint8)
    return cv2.resize(
        mask.astype(np.uint8),
        (image_gray.shape[1], image_gray.shape[0]),
        interpolation=cv2.INTER_NEAREST,
    )

def run_region_fft_analysis(image_path: str | Path, region_masks_payload: Dict[str, Any], output_dir: str | Path, ) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    # --------------------------------------------------
    # Load masks
    # --------------------------------------------------
    masks = region_masks_payload["region_masks"]
    subject_mask = _load_mask(masks["subject_mask_path"])
    boundary_mask = _load_mask(masks["boundary_band_path"])
    background_mask = _load_mask(masks["background_mask_path"])
    # align masks and log initial mismatch
    if subject_mask.shape != img.shape:
        print(f"[RegionFFT] Aligning mask from {subject_mask.shape} to image {img.shape}")    
    subject_mask = _align_mask_to_image(subject_mask, img)
    boundary_mask = _align_mask_to_image(boundary_mask, img)
    background_mask = _align_mask_to_image(background_mask, img)        
    # --------------------------------------------------
    # Apply masks
    # --------------------------------------------------
    subject_img = _extract_soft_region_crop(
        image_gray=img,
        mask=subject_mask,
        pad=24,
        blur_sigma=5.0, 
        fill_mode="mean",
    )
    boundary_img = _extract_soft_region_crop(
        image_gray=img,
        mask=boundary_mask,
        pad=20,
        blur_sigma=4.0,
        fill_mode="mean",
    )
    background_img = _extract_soft_region_crop(
        image_gray=img,
        mask=background_mask,
        pad=24,
        blur_sigma=5.0,
        fill_mode="mean",
    )
    # --------------------------------------------------
    # Save temporary masked images
    # (so we can reuse existing FFT pipeline)
    # --------------------------------------------------
    subject_path = output_dir / f"{image_path.stem}_subject_tmp.png"
    boundary_path = output_dir / f"{image_path.stem}_boundary_tmp.png"
    background_path = output_dir / f"{image_path.stem}_background_tmp.png"
    cv2.imwrite(str(subject_path), subject_img)
    cv2.imwrite(str(boundary_path), boundary_img)
    cv2.imwrite(str(background_path), background_img)
    # --------------------------------------------------
    # Run FFT per region
    # --------------------------------------------------
    subject_fft = run_fft_analysis(subject_path, output_dir, presentation_mode_override=False)
    boundary_fft = run_fft_analysis(boundary_path, output_dir, presentation_mode_override=False)
    background_fft = run_fft_analysis(background_path, output_dir, presentation_mode_override=False)
    # --------------------------------------------------
    # Extract comparable metrics
    # --------------------------------------------------
    subject_metrics = _extract_fft_metrics(subject_fft)
    boundary_metrics = _extract_fft_metrics(boundary_fft)
    background_metrics = _extract_fft_metrics(background_fft)
    # --------------------------------------------------
    # Comparative features
    # --------------------------------------------------
    def safe_ratio(a, b):
        return float(a / (b + 1e-6))
    features = {
        "subject_vs_background_fft_gap":
            subject_metrics["fft_anomaly_score"] - background_metrics["fft_anomaly_score"],
        "boundary_vs_subject_fft_gap":
            boundary_metrics["fft_anomaly_score"] - subject_metrics["fft_anomaly_score"],
        "boundary_vs_background_fft_gap":
            boundary_metrics["fft_anomaly_score"] - background_metrics["fft_anomaly_score"],
        "subject_grid_response_ratio":
            safe_ratio(subject_metrics["grid_response_score"], background_metrics["grid_response_score"]),
        "boundary_grid_response_ratio":
            safe_ratio(boundary_metrics["grid_response_score"], background_metrics["grid_response_score"]),
        "boundary_minus_subject_grid_response":
            boundary_metrics["grid_response_score"] - subject_metrics["grid_response_score"],            
    }
    # --------------------------------------------------
    # Interpretation (very conservative)
    # --------------------------------------------------
    b_gap = features["boundary_vs_background_fft_gap"]
    s_gap = features["subject_vs_background_fft_gap"]
    bs_gap = features["boundary_vs_subject_fft_gap"]
    b_ratio = features["boundary_grid_response_ratio"]
    s_ratio = features["subject_grid_response_ratio"]
    pattern = "region_frequency_inconclusive"
    # Strong localized mismatch at contour band
    if (
        b_ratio >= 1.35
        and bs_gap >= 0.0
    ):
        pattern = "boundary_band_frequency_mismatch"
    # Subject and boundary both elevated relative to background
    elif (
        s_ratio >= 1.40
        and b_ratio >= 1.35
    ):
        pattern = "region_frequency_elevated"
    # Subject clearly elevated relative to background
    elif s_ratio >= 1.30:
        pattern = "subject_background_frequency_mismatch"
    # Near-convergence
    elif (
        0.90 <= s_ratio <= 1.10
        and 0.90 <= b_ratio <= 1.10
        and abs(s_gap) < 0.03
        and abs(b_gap) < 0.03
    ):
        pattern = "region_frequency_convergence_supported"
    #print("[DEBUG][region_fft] subject_metrics:", subject_metrics)
    #print("[DEBUG][region_fft] boundary_metrics:", boundary_metrics)
    #print("[DEBUG][region_fft] background_metrics:", background_metrics)
    #print("[DEBUG][region_fft] features:", features)
    #print("[DEBUG][region_fft] pattern:", pattern)    
    # --------------------------------------------------
    # Output
    # --------------------------------------------------
    return {
        "region_fft": {
            "pattern": pattern,
            "subject_metrics": subject_metrics,
            "boundary_metrics": boundary_metrics,
            "background_metrics": background_metrics,
            "comparative_features": features,
            "artifacts": {
                "subject_input": str(subject_path),
                "boundary_input": str(boundary_path),
                "background_input": str(background_path),
            }
        }
    }