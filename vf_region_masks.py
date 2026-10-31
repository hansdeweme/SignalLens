#vf_region_masks.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#
import numpy as np
import cv2
from pathlib import Path
from typing import Any, Dict

def _normalize_to_u8(img: np.ndarray) -> np.ndarray:
    img = img.astype(np.float32)
    mn, mx = img.min(), img.max()
    if mx - mn < 1e-8:
        return np.zeros_like(img, dtype=np.uint8)
    return ((img - mn) / (mx - mn) * 255).astype(np.uint8)

def _largest_connected_component(mask: np.ndarray) -> np.ndarray:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num_labels <= 1:
        return mask

    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    return (labels == largest).astype(np.uint8)

def _create_boundary_band(subject_mask: np.ndarray, width: int) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (width, width))
    dilated = cv2.dilate(subject_mask, kernel)
    eroded = cv2.erode(subject_mask, kernel)
    band = dilated - eroded
    band = np.clip(band, 0, 1)
    return band.astype(np.uint8)

def _create_preview(image: np.ndarray, subject, boundary, background) -> np.ndarray:
    """
    RGB overlay:
    - subject → green
    - boundary → red
    - background → blue (very light)
    """
    preview = image.copy().astype(np.float32)
    # normalize image if needed
    if preview.max() <= 1.0:
        preview *= 255.0
    # overlays
    preview[subject == 1] *= [0.6, 1.0, 0.6]
    preview[boundary == 1] *= [1.0, 0.6, 0.6]
    preview[background == 1] *= [0.9, 0.9, 1.0]
    return np.clip(preview, 0, 255).astype(np.uint8)

def run_region_mask_analysis(image_path: str | Path, output_dir: str | Path, boundary_width_px: int = 18, ) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        raise ValueError(f"Failed to load image: {image_path}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    # --------------------------------------------------
    # Step 1: Edge + saliency proxy
    # --------------------------------------------------
    edges = cv2.Canny(gray, 60, 120)
    # blur to create coarse saliency
    saliency = cv2.GaussianBlur(edges.astype(np.float32), (0, 0), sigmaX=5)
    saliency_u8 = _normalize_to_u8(saliency)
    # --------------------------------------------------
    # Step 2: Threshold → foreground
    # --------------------------------------------------
    _, mask = cv2.threshold(saliency_u8, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # --------------------------------------------------
    # Step 3: Keep largest component
    # --------------------------------------------------
    subject_mask = _largest_connected_component(mask)
    # --------------------------------------------------
    # Step 4: Clean mask
    # --------------------------------------------------
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    subject_mask = cv2.morphologyEx(subject_mask, cv2.MORPH_CLOSE, kernel)
    subject_mask = cv2.morphologyEx(subject_mask, cv2.MORPH_OPEN, kernel)
    subject_mask = (subject_mask > 0).astype(np.uint8)
    # --------------------------------------------------
    # Step 5: Boundary band
    # --------------------------------------------------
    boundary_band = _create_boundary_band(subject_mask, boundary_width_px)
    # --------------------------------------------------
    # Step 6: Background
    # --------------------------------------------------
    background_mask = (1 - np.clip(subject_mask + boundary_band, 0, 1)).astype(np.uint8)
    # --------------------------------------------------
    # Step 7: Save masks
    # --------------------------------------------------
    subject_path = output_dir / f"{image_path.stem}_subject_mask.png"
    boundary_path = output_dir / f"{image_path.stem}_boundary_band.png"
    background_path = output_dir / f"{image_path.stem}_background_mask.png"
    preview_path = output_dir / f"{image_path.stem}_region_preview.png"
    cv2.imwrite(str(subject_path), subject_mask * 255)
    cv2.imwrite(str(boundary_path), boundary_band * 255)
    cv2.imwrite(str(background_path), background_mask * 255)
    preview = _create_preview(img_rgb, subject_mask, boundary_band, background_mask)
    cv2.imwrite(str(preview_path), cv2.cvtColor(preview, cv2.COLOR_RGB2BGR))
    # --------------------------------------------------
    # Step 8: stats
    # --------------------------------------------------
    total = float(h * w)
    ratios = {
        "subject": float(np.sum(subject_mask) / total),
        "boundary": float(np.sum(boundary_band) / total),
        "background": float(np.sum(background_mask) / total),
    }
    return {
        "region_masks": {
            "subject_mask_path": str(subject_path),
            "boundary_band_path": str(boundary_path),
            "background_mask_path": str(background_path),
            "preview_path": str(preview_path),
            "shape": [h, w],
            "ratios": ratios,
        }
    }