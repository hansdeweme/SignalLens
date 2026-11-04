#vf_segmentation_alignment.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

import numpy as np
import cv2

def _overlap_ratio(a: np.ndarray, b: np.ndarray) -> float:
    # both binary masks (0/1 or 0/255)
    a_bin = (a > 0).astype(np.uint8)
    b_bin = (b > 0).astype(np.uint8)
    inter = (a_bin & b_bin).sum()
    total = a_bin.sum()
    if total == 0:
        return 0.0
    return float(inter) / float(total)

def _load_bin_mask(path) -> np.ndarray:
    m = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        return None
    return (m > 0).astype(np.uint8)

def compute_segmentation_boundary_alignment(cross_payload, region_masks_payload):
    if cross_payload is None or region_masks_payload is None:
        return None
    hotspot = cross_payload.get("hotspot_mask")  # or load from file if you save it
    if hotspot is None:
        return None

    masks = region_masks_payload.get("region_masks", {})
    boundary_path = masks.get("boundary_band_path")
    boundary = _load_bin_mask(boundary_path)
    if boundary is None:
        return None
    # Hotspots use the ELA/residual image grid. Person masks may use a resized
    # gatekeeper image; align coordinates instead of cropping the hotspot grid.
    original_hotspot_shape = list(hotspot.shape)
    if hotspot.shape != boundary.shape:
        hotspot = cv2.resize(hotspot.astype(np.uint8), (boundary.shape[1], boundary.shape[0]), interpolation=cv2.INTER_NEAREST)

    # Raw overlap: how much of hotspots sit on boundary
    raw_align = _overlap_ratio(hotspot, boundary)

    # Normalize by boundary size to avoid trivial hits
    boundary_coverage = boundary.sum() / (hotspot.size + 1e-6)

    # Final score (penalize huge boundaries)
    score = raw_align * (1.0 - np.clip(boundary_coverage, 0.0, 0.7))

    return {
        "alignment_score": float(score),
        "raw_overlap": float(raw_align),
        "boundary_coverage": float(boundary_coverage),
        "hotspot_input_shape": original_hotspot_shape,
        "boundary_shape": list(boundary.shape),
    }
    
