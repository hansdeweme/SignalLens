#vf_region_segmentation.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

import cv2
# local imports
from vf_subject_process_asymmetry import _load_mask

def run_region_segmentation_analysis(region_masks_payload) -> dict:
    masks = region_masks_payload.get("region_masks", {})

    subject_mask = _load_mask(masks["subject_mask_path"])
    boundary_mask = _load_mask(masks["boundary_band_path"])
    background_mask = _load_mask(masks["background_mask_path"])

    total_pixels = subject_mask.size

    subject_ratio = float(subject_mask.sum()) / total_pixels
    boundary_ratio = float(boundary_mask.sum()) / total_pixels
    background_ratio = float(background_mask.sum()) / total_pixels

    # --- Fragmentation ---
    num_labels, labels = cv2.connectedComponents(subject_mask)
    component_count = num_labels - 1

    component_sizes = [
        (labels == i).sum() for i in range(1, num_labels)
    ]
    largest_component_ratio = (
        max(component_sizes) / subject_mask.sum()
        if component_sizes else 0.0
    )

    # --- Boundary density ---
    boundary_density = boundary_ratio / (subject_ratio + 1e-6)

    # --- Heuristic scoring ---
    pattern = "segmentation_convergence_supported"
    score = 0.0

    if component_count > 5 and largest_component_ratio < 0.6:
        pattern = "fragmented_subject_mask"
        score = 0.7

    elif boundary_density < 0.05:
        pattern = "unnaturally_clean_segmentation"
        score = 0.6

    elif subject_ratio > 0.85 or subject_ratio < 0.05:
        pattern = "dominant_subject_ratio_anomaly"
        score = 0.5

    return {
        "region_segmentation": {
            "pattern": pattern,
            "score": score,
            "ratios": {
                "subject": subject_ratio,
                "boundary": boundary_ratio,
                "background": background_ratio,
            },
            "metrics": {
                "component_count": component_count,
                "largest_component_ratio": largest_component_ratio,
                "boundary_density": boundary_density,
            },
        }
    }