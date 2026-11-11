# vf_subject_texture_consistency.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from investigation_storage import artifact_stem
from pathlib import Path
from typing import Any, Dict, List, Tuple
import cv2
import numpy as np
from sklearn.neighbors import NearestNeighbors

DEFAULT_MAX_DIM = 768
DEFAULT_PATCH_SIZE = 16
DEFAULT_STRIDE = 8
DEFAULT_DESCRIPTOR_SIZE = 8
DEFAULT_SUBJECT_COVERAGE_MIN = 0.75
DEFAULT_K_NEIGHBORS = 6
SUBJECT_TEXTURE_CONFIG: dict[str, dict[str, float | str]] = {
    "gradient_component_weight": {
        "default": 1.0,
        "min": 0.0,
        "max": 3.0,
        "description": "Weight of gradient-structure features in the patch descriptor. Higher values emphasize folds, edges, and local surface flow."
    },
    "dct_component_weight": {
        "default": 1.0,
        "min": 0.0,
        "max": 3.0,
        "description": "Weight of low/mid-frequency DCT features in the patch descriptor. Higher values emphasize diffusion-like frequency regularity and smooth structured texture."
    },
    "residual_stats_weight": {
        "default": 1.0,
        "min": 0.0,
        "max": 3.0,
        "description": "Weight of residual and microtexture statistics in the patch descriptor. Higher values emphasize local variance, Laplacian energy, and entropy-style texture cues."
    },
    "mean_weight": {
        "default": 0.40,
        "min": 0.0,
        "max": 1.0,
        "description": "Weight of mean neighbor similarity in the soft recurrence score. Higher values make the detector more sensitive to broad internal similarity."
    },
    "p90_weight": {
        "default": 0.30,
        "min": 0.0,
        "max": 1.0,
        "description": "Weight of the 90th-percentile neighbor similarity in the soft recurrence score. Higher values emphasize the stronger end of the similarity distribution."
    },
    "dense_weight": {
        "default": 0.20,
        "min": 0.0,
        "max": 1.0,
        "description": "Weight of the dense-similarity ratio in the soft recurrence score. Higher values emphasize how many patch comparisons clear the high-similarity threshold."
    },
    "coverage_weight": {
        "default": 0.10,
        "min": 0.0,
        "max": 1.0,
        "description": "Weight of region support coverage in the soft recurrence score. Higher values reward broader spatial support inside the analyzed region."
    },
    "subject_surface_sat_thresh": {
        "default": 55.0,
        "min": 0.0,
        "max": 255.0,
        "description": "Minimum HSV saturation for the subject-surface color branch. Lower values include more muted clothing and skin-adjacent regions."
    },
    "subject_surface_grad_thresh": {
        "default": 0.06,
        "min": 0.0,
        "max": 1.0,
        "description": "Minimum normalized gradient magnitude for the subject-surface structure branch. Lower values include smoother subject surfaces."
    },
    "background_texture_sat_thresh": {
        "default": 40.0,
        "min": 0.0,
        "max": 255.0,
        "description": "Minimum HSV saturation for the background control mask. Lower values include more muted background texture."
    },
}

CLOTHING_FOCUSED_PROFILE = {
    # Descriptor weights
    "gradient_component_weight": 1.4,
    "dct_component_weight": 1.1,
    "residual_stats_weight": 0.8,
    # Scoring weights
    "mean_weight": 0.45,
    "p90_weight": 0.30,
    "dense_weight": 0.20,
    "coverage_weight": 0.05,
    # Mask thresholds
    "subject_surface_sat_thresh": 65.0,
    "subject_surface_grad_thresh": 0.07,
    "background_texture_sat_thresh": 45.0,
}

SKIN_FOCUSED_PROFILE = {
    # Descriptor weights
    "gradient_component_weight": 0.7,
    "dct_component_weight": 1.4,
    "residual_stats_weight": 1.5,
    # Scoring weights
    "mean_weight": 0.30,
    "p90_weight": 0.35,
    "dense_weight": 0.25,
    "coverage_weight": 0.10,
    # Mask thresholds
    "subject_surface_sat_thresh": 35.0,
    "subject_surface_grad_thresh": 0.04,
    "background_texture_sat_thresh": 30.0,
}

SUBJECT_TEXTURE_PROFILE_PRESETS: dict[str, dict[str, float]] = {
    "clothing_focused": {
        "gradient_component_weight": 1.4,
        "dct_component_weight": 1.1,
        "residual_stats_weight": 0.8,
        "mean_weight": 0.45,
        "p90_weight": 0.30,
        "dense_weight": 0.20,
        "coverage_weight": 0.05,
        "subject_surface_sat_thresh": 65.0,
        "subject_surface_grad_thresh": 0.07,
        "background_texture_sat_thresh": 45.0,
    },
    "skin_focused": {
        "gradient_component_weight": 0.7,
        "dct_component_weight": 1.4,
        "residual_stats_weight": 1.5,
        "mean_weight": 0.30,
        "p90_weight": 0.35,
        "dense_weight": 0.25,
        "coverage_weight": 0.10,
        "subject_surface_sat_thresh": 35.0,
        "subject_surface_grad_thresh": 0.04,
        "background_texture_sat_thresh": 30.0,
    },
    "mixed": {
        "gradient_component_weight": 1.0,
        "dct_component_weight": 1.25,
        "residual_stats_weight": 1.1,
        "mean_weight": 0.35,
        "p90_weight": 0.33,
        "dense_weight": 0.22,
        "coverage_weight": 0.10,
        "subject_surface_sat_thresh": 45.0,
        "subject_surface_grad_thresh": 0.05,
        "background_texture_sat_thresh": 35.0,
    },
}

# cfg = _build_subject_texture_runtime_config(CLOTHING_FOCUSED_PROFILE)
# cfg = _build_subject_texture_runtime_config(SKIN_FOCUSED_PROFILE)

def _analyze_subject_surface_regime(
    rgb: np.ndarray,
    gray: np.ndarray,
    subject_mask: np.ndarray,
) -> dict[str, float | str]:
    hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV)
    s = hsv[..., 1].astype(np.float32)
    gx = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.sqrt(gx * gx + gy * gy)
    grad_norm = grad_mag / max(float(np.max(grad_mag)), 1e-6)
    active = subject_mask > 0
    if not np.any(active):
        return {
            "profile_name": "clothing_focused",
            "mean_saturation": 0.0,
            "high_saturation_ratio": 0.0,
            "gradient_active_ratio": 0.0,
            "surface_coverage_ratio": 0.0,
        }
    s_vals = s[active]
    g_vals = grad_norm[active]
    mean_saturation = float(np.mean(s_vals))
    high_saturation_ratio = float(np.mean(s_vals >= 60.0))
    gradient_active_ratio = float(np.mean(g_vals >= 0.06))
    surface_coverage_ratio = float(np.mean(active))
    clothing_score = (
        0.45 * min(mean_saturation / 120.0, 1.0) +
        0.30 * high_saturation_ratio +
        0.25 * gradient_active_ratio
    )
    skin_score = (
        0.45 * (1.0 - min(mean_saturation / 120.0, 1.0)) +
        0.30 * (1.0 - high_saturation_ratio) +
        0.25 * (1.0 - gradient_active_ratio)
    )
    if clothing_score >= skin_score + 0.08:
        profile_name = "clothing_focused"
    elif skin_score >= clothing_score + 0.08:
        profile_name = "skin_focused"
    else:
        profile_name = "mixed"
    return {
        "profile_name": profile_name,
        "mean_saturation": mean_saturation,
        "high_saturation_ratio": high_saturation_ratio,
        "gradient_active_ratio": gradient_active_ratio,
        "surface_coverage_ratio": surface_coverage_ratio,
        "clothing_score": float(clothing_score),
        "skin_score": float(skin_score),
    }

def _get_cfg_value(name: str) -> float:
    return float(SUBJECT_TEXTURE_CONFIG[name]["default"])


def _build_subject_texture_runtime_config(overrides: dict[str, float] | None = None) -> dict[str, float]:
    cfg = {key: float(meta["default"]) for key, meta in SUBJECT_TEXTURE_CONFIG.items()}
    if not overrides:
        return cfg

    for key, value in overrides.items():
        if key not in SUBJECT_TEXTURE_CONFIG:
            continue
        meta = SUBJECT_TEXTURE_CONFIG[key]
        lo = float(meta["min"])
        hi = float(meta["max"])
        cfg[key] = max(lo, min(hi, float(value)))
    return cfg

def _load_mask(path: str | Path) -> np.ndarray:
    m = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"Failed to load mask: {path}")
    return (m > 127).astype(np.uint8)

def _load_gray_image_exact(image_path: str | Path, shape_hw: Tuple[int, int]) -> np.ndarray:
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    h, w = shape_hw
    if img.shape != (h, w):
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return img.astype(np.float32) / 255.0


def _load_rgb_image_exact(image_path: str | Path, shape_hw: Tuple[int, int]) -> np.ndarray:
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = shape_hw
    if img.shape[:2] != (h, w):
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return img

def _validate_analysis_geometry(
    gray: np.ndarray,
    rgb: np.ndarray,
    subject_mask: np.ndarray,
    background_mask: np.ndarray,
    expected_shape_hw: Tuple[int, int],
) -> None:
    h, w = expected_shape_hw
    if gray.shape != (h, w):
        raise ValueError(f"Gray image shape mismatch: got {gray.shape}, expected {(h, w)}")
    if rgb.shape[:2] != (h, w):
        raise ValueError(f"RGB image shape mismatch: got {rgb.shape[:2]}, expected {(h, w)}")
    if subject_mask.shape != (h, w):
        raise ValueError(f"Subject mask shape mismatch: got {subject_mask.shape}, expected {(h, w)}")
    if background_mask.shape != (h, w):
        raise ValueError(f"Background mask shape mismatch: got {background_mask.shape}, expected {(h, w)}")

def _largest_connected_component(mask: np.ndarray) -> np.ndarray:
    mask_u8 = (mask > 0).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
    if num_labels <= 1:
        return mask_u8

    best_label = 0
    best_area = 0
    for label in range(1, num_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area > best_area:
            best_area = area
            best_label = label

    out = (labels == best_label).astype(np.uint8)
    return out

def _build_subject_surface_focus_mask(
    rgb: np.ndarray,
    gray: np.ndarray,
    subject_mask: np.ndarray,
    sat_thresh: float,
    grad_thresh: float,
    value_min: float = 30.0,
    keep_largest_component: bool = False,
) -> np.ndarray:
    """
    Build a subject-surface focus mask for stochastic regularity analysis.
    Includes both:
    - more saturated subject regions such as garments
    - structurally active subject regions such as skin/fabric folds and contours
    """
    hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV)
    s = hsv[..., 1].astype(np.float32)
    v = hsv[..., 2].astype(np.float32)
    gx = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.sqrt(gx * gx + gy * gy)
    grad_norm = grad_mag / max(float(np.max(grad_mag)), 1e-6)
    color_branch = (
        (subject_mask > 0)
        & (s >= sat_thresh)
        & (v >= value_min)
    )
    structure_branch = (
        (subject_mask > 0)
        & (v >= value_min)
        & (grad_norm >= grad_thresh)
    )
    candidate = (color_branch | structure_branch).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, kernel)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, kernel)
    if keep_largest_component and np.count_nonzero(candidate) > 0:
        candidate = _largest_connected_component(candidate)
    if np.count_nonzero(candidate) < 0.12 * max(np.count_nonzero(subject_mask), 1):
        ys, xs = np.where(subject_mask > 0)
        if len(xs) > 0 and len(ys) > 0:
            x0, x1 = int(xs.min()), int(xs.max())
            y0, y1 = int(ys.min()), int(ys.max())
            y_start = int(round(y0 + 0.20 * (y1 - y0)))
            fallback = np.zeros_like(subject_mask, dtype=np.uint8)
            fallback[y_start:y1 + 1, x0:x1 + 1] = 1
            candidate = ((subject_mask > 0) & (fallback > 0)).astype(np.uint8)
    return candidate.astype(np.uint8)

def _save_mask_overlay(
    gray: np.ndarray,
    mask: np.ndarray,
    out_path: str | Path,
) -> None:
    base = np.clip(gray * 255.0, 0, 255).astype(np.uint8)
    base_rgb = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)
    contours, _ = cv2.findContours(
        (mask > 0).astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    cv2.drawContours(base_rgb, contours, -1, (80, 220, 120), 2)
    cv2.imwrite(str(out_path), base_rgb)

def _resize_mask(mask: np.ndarray, shape_hw: Tuple[int, int]) -> np.ndarray:
    h, w = shape_hw
    if mask.shape == (h, w):
        return mask.astype(np.uint8)
    out = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
    return (out > 0).astype(np.uint8)

def _patch_to_descriptor(
    patch: np.ndarray,
    descriptor_size: int,
    cfg: dict[str, float],
) -> np.ndarray:
    """
    Hybrid descriptor for subject-surface stochastic regularity:
    - gradient magnitude structure
    - low/mid-frequency DCT
    - residual / microtexture statistics
    """
    patch = patch.astype(np.float32)
    gradient_component_weight = cfg["gradient_component_weight"]
    dct_component_weight = cfg["dct_component_weight"]
    residual_stats_weight = cfg["residual_stats_weight"]
    # 1. Gradient magnitude component
    gx = cv2.Sobel(patch, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(patch, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.sqrt(gx * gx + gy * gy)
    grad_small = cv2.resize(
        grad_mag,
        (descriptor_size, descriptor_size),
        interpolation=cv2.INTER_AREA,
    )
    grad_vec = grad_small.flatten().astype(np.float32) * gradient_component_weight
    # 2. DCT frequency component
    patch_small = cv2.resize(
        patch,
        (descriptor_size, descriptor_size),
        interpolation=cv2.INTER_AREA,
    )
    mean = float(np.mean(patch_small))
    std = float(np.std(patch_small))
    if std < 1e-6:
        norm_patch = patch_small - mean
    else:
        norm_patch = (patch_small - mean) / std
    dct = cv2.dct(norm_patch.astype(np.float32))
    dct_block = dct[0:4, 0:4].flatten()[1:]  # remove DC
    dct_block = dct_block.astype(np.float32) * dct_component_weight
    # 3. Residual / microtexture statistics
    lap = cv2.Laplacian(patch, cv2.CV_32F)
    lap_abs_mean = float(np.mean(np.abs(lap)))
    local_var = float(np.var(patch))
    hist = np.histogram(patch, bins=16, range=(0.0, 1.0))[0].astype(np.float32)
    hist /= max(np.sum(hist), 1e-6)
    entropy = float(-np.sum(hist * np.log(hist + 1e-6)))
    stats_vec = np.array(
        [lap_abs_mean, local_var, entropy],
        dtype=np.float32,
    ) * residual_stats_weight
    vec = np.concatenate([grad_vec, dct_block, stats_vec]).astype(np.float32)
    mean = float(np.mean(vec))
    std = float(np.std(vec))
    if std < 1e-6:
        vec = vec - mean
    else:
        vec = (vec - mean) / std
    norm = float(np.linalg.norm(vec))
    if norm > 1e-8:
        vec /= norm
    return vec

def _extract_masked_patch_descriptors(
    gray: np.ndarray,
    region_mask: np.ndarray,
    patch_size: int,
    stride: int,
    descriptor_size: int,
    coverage_min: float,
    cfg: dict[str, float],
) -> Tuple[List[np.ndarray], List[Tuple[int, int]], np.ndarray]:
    h, w = gray.shape
    descriptors: List[np.ndarray] = []
    coords: List[Tuple[int, int]] = []
    support_map = np.zeros((h, w), dtype=np.float32)
    for y in range(0, h - patch_size + 1, stride):
        for x in range(0, w - patch_size + 1, stride):
            mask_patch = region_mask[y:y + patch_size, x:x + patch_size]
            coverage = float(np.mean(mask_patch > 0))
            if coverage < coverage_min:
                continue

            patch = gray[y:y + patch_size, x:x + patch_size]
            desc = _patch_to_descriptor(
                patch,
                descriptor_size=descriptor_size,
                cfg=cfg,
            )
            descriptors.append(desc)
            coords.append((x, y))
            support_map[y:y + patch_size, x:x + patch_size] += 1.0
    return descriptors, coords, support_map

def _build_background_texture_focus_mask(
    rgb: np.ndarray,
    gray: np.ndarray,
    subject_mask: np.ndarray,
    background_mask: np.ndarray,
    sat_thresh: float = 40.0,
    value_min: float = 25.0,
    grad_min: float = 0.02,
    grad_max: float = 0.12,
    keep_largest_component: bool = False,
) -> np.ndarray:
    """
    Build a background control mask for texture comparison.

    Goal:
    - stay inside background
    - prefer usable naturalistic texture
    - avoid very flat unusable regions
    - avoid highly repetitive architectural/grid-heavy regions
    """
    hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV)
    s = hsv[..., 1].astype(np.float32)
    v = hsv[..., 2].astype(np.float32)

    gx = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.sqrt(gx * gx + gy * gy)
    grad_norm = grad_mag / max(float(np.max(grad_mag)), 1e-6)

    candidate = (
        (background_mask > 0)
        & (v >= value_min)
        & (s >= sat_thresh)
        & (grad_norm >= grad_min)
        & (grad_norm <= grad_max)
    ).astype(np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, kernel)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, kernel)

    if keep_largest_component and np.count_nonzero(candidate) > 0:
        candidate = _largest_connected_component(candidate)

    # fallback: if too little survives, use a band-passed version of the raw background
    if np.count_nonzero(candidate) < 0.05 * max(np.count_nonzero(background_mask), 1):
        candidate = (
            (background_mask > 0)
            & (v >= value_min)
            & (grad_norm >= grad_min)
            & (grad_norm <= grad_max)
        ).astype(np.uint8)

    return candidate.astype(np.uint8)

def _cap_mask_area(mask: np.ndarray, target_area: int) -> np.ndarray:
    """
    Reduce a mask to approximately target_area pixels by keeping the most central
    connected components first. This prevents the background control region from
    dominating the subject region by sheer size.
    """
    mask_u8 = (mask > 0).astype(np.uint8)
    current_area = int(np.count_nonzero(mask_u8))
    if current_area <= target_area or target_area <= 0:
        return mask_u8

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
    if num_labels <= 1:
        ys, xs = np.where(mask_u8 > 0)
        if len(xs) == 0 or len(ys) == 0:
            return mask_u8
        cx = float(np.mean(xs))
        cy = float(np.mean(ys))
        d2 = (xs - cx) ** 2 + (ys - cy) ** 2
        keep_idx = np.argsort(d2)[:target_area]
        out = np.zeros_like(mask_u8)
        out[ys[keep_idx], xs[keep_idx]] = 1
        return out

    h, w = mask_u8.shape
    img_cx = w / 2.0
    img_cy = h / 2.0

    parts = []
    for label in range(1, num_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area <= 0:
            continue
        cx, cy = centroids[label]
        d2 = (cx - img_cx) ** 2 + (cy - img_cy) ** 2
        parts.append((d2, -area, label))

    parts.sort()

    out = np.zeros_like(mask_u8)
    kept = 0
    for _, _, label in parts:
        comp = (labels == label).astype(np.uint8)
        comp_area = int(np.count_nonzero(comp))
        if kept + comp_area <= target_area:
            out[comp > 0] = 1
            kept += comp_area
        else:
            ys, xs = np.where(comp > 0)
            remaining = target_area - kept
            if remaining > 0 and len(xs) > 0:
                cx = float(np.mean(xs))
                cy = float(np.mean(ys))
                d2 = (xs - cx) ** 2 + (ys - cy) ** 2
                keep_idx = np.argsort(d2)[:remaining]
                out[ys[keep_idx], xs[keep_idx]] = 1
                kept += len(keep_idx)
            break

    return out.astype(np.uint8)

def _compute_region_texture_scores(
    gray: np.ndarray,
    region_mask: np.ndarray,
    patch_size: int,
    stride: int,
    descriptor_size: int,
    coverage_min: float,
    k_neighbors: int,
    cfg: dict[str, float],
) -> Dict[str, Any]:
    descriptors, coords, support_map = _extract_masked_patch_descriptors(
        gray=gray,
        region_mask=region_mask,
        patch_size=patch_size,
        stride=stride,
        descriptor_size=descriptor_size,
        coverage_min=coverage_min,
        cfg=cfg,
    )

    patch_count = len(descriptors)
    if patch_count < max(12, k_neighbors + 1):
        return {
            "patch_count": int(patch_count),
            "mean_neighbor_similarity": 0.0,
            "p90_neighbor_similarity": 0.0,
            "dense_similarity_ratio": 0.0,
            "soft_recurrence_score": 0.0,
            "region_support_coverage": 0.0,
            "coords": coords,
            "support_map": support_map,
            "patch_scores": np.zeros((0,), dtype=np.float32),
            "sim_map": np.zeros_like(gray, dtype=np.float32),
        }

    feature_matrix = np.asarray(descriptors, dtype=np.float32)
    nn = NearestNeighbors(
        n_neighbors=min(k_neighbors + 1, patch_count),
        algorithm="auto",
        metric="euclidean",
    )
    nn.fit(feature_matrix)
    distances, indices = nn.kneighbors(feature_matrix)

    neighbor_sims: List[float] = []
    patch_scores = np.zeros((patch_count,), dtype=np.float32)

    for i in range(patch_count):
        sims_i: List[float] = []
        for j_pos in range(1, distances.shape[1]):
            j = int(indices[i, j_pos])
            sim = _cosine_from_unit_vectors(feature_matrix[i], feature_matrix[j])
            sims_i.append(sim)

        if not sims_i:
            continue

        sims_arr = np.asarray(sims_i, dtype=np.float32)
        neighbor_sims.extend(sims_i)

        mean_sim = float(np.mean(sims_arr))
        p80_sim = float(np.percentile(sims_arr, 80))
        patch_scores[i] = 0.6 * mean_sim + 0.4 * p80_sim

    neighbor_sims_arr = np.asarray(neighbor_sims, dtype=np.float32)
    mean_neighbor_similarity = float(np.mean(neighbor_sims_arr)) if neighbor_sims_arr.size else 0.0
    p90_neighbor_similarity = float(np.percentile(neighbor_sims_arr, 90)) if neighbor_sims_arr.size else 0.0
    dense_similarity_ratio = float(np.mean(neighbor_sims_arr >= 0.90)) if neighbor_sims_arr.size else 0.0

    sim_map = _build_subject_similarity_map(
        shape_hw=gray.shape,
        coords=coords,
        patch_scores=patch_scores,
        patch_size=patch_size,
    )

    active_region = region_mask > 0
    region_support_coverage = float(np.mean(support_map[active_region] > 0)) if np.any(active_region) else 0.0

    mean_weight = cfg["mean_weight"]
    p90_weight = cfg["p90_weight"]
    dense_weight = cfg["dense_weight"]
    coverage_weight = cfg["coverage_weight"]

    soft_recurrence_score = float(np.clip(
        mean_weight * max(0.0, (mean_neighbor_similarity - 0.68) / 0.18) +
        p90_weight * max(0.0, (p90_neighbor_similarity - 0.84) / 0.10) +
        dense_weight * min(dense_similarity_ratio / 0.10, 1.0) +
        coverage_weight * min(region_support_coverage / 0.75, 1.0),
        0.0,
        1.0
    ))

    return {
        "patch_count": int(patch_count),
        "mean_neighbor_similarity": float(mean_neighbor_similarity),
        "p90_neighbor_similarity": float(p90_neighbor_similarity),
        "dense_similarity_ratio": float(dense_similarity_ratio),
        "soft_recurrence_score": float(soft_recurrence_score),
        "region_support_coverage": float(region_support_coverage),
        "coords": coords,
        "support_map": support_map,
        "patch_scores": patch_scores,
        "sim_map": sim_map,
    }

def _cosine_from_unit_vectors(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.clip(np.dot(a, b), -1.0, 1.0))

def _build_subject_similarity_map(shape_hw: Tuple[int, int], coords: List[Tuple[int, int]], patch_scores: np.ndarray, patch_size: int, ) -> np.ndarray:
    h, w = shape_hw
    sim_map = np.zeros((h, w), dtype=np.float32)
    count_map = np.zeros((h, w), dtype=np.float32)
    for (x, y), score in zip(coords, patch_scores):
        sim_map[y:y + patch_size, x:x + patch_size] += float(score)
        count_map[y:y + patch_size, x:x + patch_size] += 1.0
    out = np.divide(sim_map, np.maximum(count_map, 1e-6))
    return out

def _normalize_to_u8(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype(np.float32)
    lo = float(np.min(arr))
    hi = float(np.max(arr))
    if hi <= lo:
        return np.zeros_like(arr, dtype=np.uint8)
    out = (arr - lo) / (hi - lo)
    return np.clip(out * 255.0, 0, 255).astype(np.uint8)

def _save_subject_similarity_overlay(gray: np.ndarray, sim_map: np.ndarray, subject_mask: np.ndarray,  out_path: str | Path, ) -> None:
    base = np.clip(gray * 255.0, 0, 255).astype(np.uint8)
    base_rgb = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)
    heat = _normalize_to_u8(sim_map)
    heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    alpha = 0.45
    overlay = base_rgb.copy()
    subject_idx = subject_mask > 0
    overlay[subject_idx] = cv2.addWeighted(
        base_rgb[subject_idx], 1.0 - alpha,
        heat_color[subject_idx], alpha,
        0.0,
    )
    # faint subject boundary
    contours, _ = cv2.findContours(
        (subject_mask * 255).astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    cv2.drawContours(overlay, contours, -1, (180, 220, 180), 1)
    cv2.imwrite(str(out_path), overlay)

def run_subject_texture_consistency_analysis(
    image_path: str | Path,
    region_masks_payload: Dict[str, Any],
    output_dir: str | Path,
    analysis_shape_hw: tuple[int, int] | None = None,
    analysis_scale: float | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
    stride: int = DEFAULT_STRIDE,
    descriptor_size: int = DEFAULT_DESCRIPTOR_SIZE,
    subject_coverage_min: float = DEFAULT_SUBJECT_COVERAGE_MIN,
    k_neighbors: int = DEFAULT_K_NEIGHBORS,
    config_overrides: dict[str, float] | None = None,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if analysis_shape_hw is None:
        raise ValueError(
            "analysis_shape_hw must be provided by the gatekeeper so that "
            "image, RGB view, grayscale view, and masks share one explicit analysis geometry."
        )
    gray = _load_gray_image_exact(image_path, analysis_shape_hw)
    rgb = _load_rgb_image_exact(image_path, analysis_shape_hw)
    masks = region_masks_payload["region_masks"]
    subject_mask_full = _load_mask(masks["subject_mask_path"])
    background_mask_full = _load_mask(masks["background_mask_path"])
    subject_mask = _resize_mask(subject_mask_full, analysis_shape_hw)
    background_mask = _resize_mask(background_mask_full, analysis_shape_hw)
    _validate_analysis_geometry(
        gray=gray,
        rgb=rgb,
        subject_mask=subject_mask,
        background_mask=background_mask,
        expected_shape_hw=analysis_shape_hw,
    )
        
    # Analyze subject surface regime to guide profile selection (dress or skin focussed) and mask thresholds
    regime = _analyze_subject_surface_regime(
        rgb=rgb,
        gray=gray,
        subject_mask=subject_mask,
    )
    auto_profile_name = str(regime["profile_name"])
    auto_profile_overrides = SUBJECT_TEXTURE_PROFILE_PRESETS.get(auto_profile_name, {})
    merged_overrides = dict(auto_profile_overrides)
    if config_overrides:
        merged_overrides.update(config_overrides)
    cfg = _build_subject_texture_runtime_config(merged_overrides)
    texture_focus_mask = _build_subject_surface_focus_mask(
        rgb=rgb,
        gray=gray,
        subject_mask=subject_mask,
        sat_thresh=cfg["subject_surface_sat_thresh"],
        grad_thresh=cfg["subject_surface_grad_thresh"],
        value_min=30.0,
        keep_largest_component=False,
    )    
    subject_area = int(np.count_nonzero(subject_mask))
    texture_focus_area = int(np.count_nonzero(texture_focus_mask))
    focus_to_subject_ratio = texture_focus_area / max(subject_area, 1)
    focus_to_image_ratio = texture_focus_area / max(gray.size, 1)
    if focus_to_subject_ratio < 0.15 or focus_to_image_ratio < 0.01:
        pattern = "subject_texture_support_insufficient"
        note = (
            "Subject texture analysis did not have enough representative subject-surface support. "
            "The texture-focus mask covers only a small fraction of the segmented subject or image, "
            "so this result should not be interpreted as a stable subject-level texture finding."
        )

        stem = artifact_stem(image_path)
        mask_overlay_path = output_dir / f"{stem}_subject_texture_focus_mask.png"
        _save_mask_overlay(
            gray=gray,
            mask=texture_focus_mask,
            out_path=mask_overlay_path,
        )

        return {
            "subject_texture_consistency": {
                "config": {k: float(v) for k, v in cfg.items()},
                "pattern": pattern,
                "note": note,
                "scores": {
                    "patch_count": 0,
                    "mean_neighbor_similarity": 0.0,
                    "p90_neighbor_similarity": 0.0,
                    "dense_similarity_ratio": 0.0,
                    "soft_recurrence_score": 0.0,
                    "subject_support_coverage": 0.0,
                    "texture_focus_area": texture_focus_area,
                    "full_subject_area": subject_area,
                    "focus_to_subject_ratio": float(focus_to_subject_ratio),
                    "focus_to_image_ratio": float(focus_to_image_ratio),
                    "support_reliable": False,
                },
                "profile": {
                    "auto_profile_name": auto_profile_name,
                    "mean_saturation": float(regime["mean_saturation"]),
                    "high_saturation_ratio": float(regime["high_saturation_ratio"]),
                    "gradient_active_ratio": float(regime["gradient_active_ratio"]),
                    "surface_coverage_ratio": float(regime["surface_coverage_ratio"]),
                    "clothing_score": float(regime["clothing_score"]),
                    "skin_score": float(regime["skin_score"]),
                },
                "artifacts": {
                    "subject_texture_focus_mask_overlay": str(mask_overlay_path),
                },
            }
        }
    
    background_texture_focus_mask = _build_background_texture_focus_mask(
        rgb=rgb,
        gray=gray,
        subject_mask=subject_mask,
        background_mask=background_mask,
        sat_thresh=cfg["background_texture_sat_thresh"],
        value_min=25.0,
        grad_min=0.02,
        grad_max=0.12,
        keep_largest_component=False,
    )
    subject_focus_area = int(np.count_nonzero(texture_focus_mask))
    max_background_area = int(max(subject_focus_area * 1.75, 1))
    background_texture_focus_mask = _cap_mask_area(
        background_texture_focus_mask,
        target_area=max_background_area,
    )    
    subject_scores = _compute_region_texture_scores(
        gray=gray,
        region_mask=texture_focus_mask,
        patch_size=patch_size,
        stride=stride,
        descriptor_size=descriptor_size,
        coverage_min=subject_coverage_min,
        k_neighbors=k_neighbors,
        cfg=cfg,
    )
    background_scores = _compute_region_texture_scores(
        gray=gray,
        region_mask=background_texture_focus_mask,
        patch_size=patch_size,
        stride=stride,
        descriptor_size=descriptor_size,
        coverage_min=subject_coverage_min,
        k_neighbors=k_neighbors,
        cfg=cfg,
    )
    patch_count = subject_scores["patch_count"]
    mean_neighbor_similarity = subject_scores["mean_neighbor_similarity"]
    p90_neighbor_similarity = subject_scores["p90_neighbor_similarity"]
    dense_similarity_ratio = subject_scores["dense_similarity_ratio"]
    soft_recurrence_score = subject_scores["soft_recurrence_score"]
    subject_support_coverage = subject_scores["region_support_coverage"]
    sim_map = subject_scores["sim_map"]

    bg_patch_count = background_scores["patch_count"]
    bg_mean_neighbor_similarity = background_scores["mean_neighbor_similarity"]
    bg_p90_neighbor_similarity = background_scores["p90_neighbor_similarity"]
    bg_dense_similarity_ratio = background_scores["dense_similarity_ratio"]
    bg_soft_recurrence_score = background_scores["soft_recurrence_score"]
    background_support_coverage = background_scores["region_support_coverage"]

    subject_background_mean_gap = mean_neighbor_similarity - bg_mean_neighbor_similarity
    subject_background_p90_gap = p90_neighbor_similarity - bg_p90_neighbor_similarity
    subject_background_dense_gap = dense_similarity_ratio - bg_dense_similarity_ratio
    subject_background_soft_gap = soft_recurrence_score - bg_soft_recurrence_score
    background_is_highly_repetitive = (
        bg_soft_recurrence_score >= 0.85
        and bg_mean_neighbor_similarity >= 0.88
        and bg_dense_similarity_ratio >= 0.35
    )
    
    focus_area = int(np.count_nonzero(texture_focus_mask))
    subject_area = int(np.count_nonzero(subject_mask))
    focus_to_subject_ratio = focus_area / max(subject_area, 1)

    if focus_to_subject_ratio < 0.15:
        pattern = "subject_texture_support_insufficient"
        note = (
            "Subject texture analysis did not have enough representative subject-surface support. "
            "The texture-focus mask covers only a small fraction of the segmented subject, so this result "
            "should not be interpreted as a stable subject-level texture finding."
        )
    
    elif (
        background_is_highly_repetitive
        and soft_recurrence_score >= 0.10
        and mean_neighbor_similarity >= 0.67
        and p90_neighbor_similarity >= 0.83
        and dense_similarity_ratio >= 0.03
    ):
        pattern = "subject_texture_stochastic_regularization"
        note = (
            "Subject-only texture analysis finds moderately elevated internal soft self-similarity in the "
            "texture-focused subject region. This is compatible with stochastic regularization of subject-surface texture."
        )
    elif (
        soft_recurrence_score >= 0.38
        and mean_neighbor_similarity >= 0.70
        and p90_neighbor_similarity >= 0.87
        and dense_similarity_ratio >= 0.05
    ):
        if background_is_highly_repetitive:
            pattern = "subject_internal_stochastic_repetition"
            note = (
                "Subject-only texture analysis finds elevated soft self-similarity across the texture-focused "
                "subject region. The background control region is also highly repetitive, so the comparative "
                "baseline is treated cautiously. Even so, the subject signal supports subject-internal stochastic "
                "repetition consistent with diffusion-generated or AI-enhanced subject-surface structure."
            )
        elif subject_background_soft_gap >= -0.10:
            pattern = "subject_internal_stochastic_repetition"
            note = (
                "Subject-only texture analysis finds elevated soft self-similarity across the texture-focused "
                "subject region. This supports subject-internal stochastic repetition consistent with "
                "diffusion-generated or AI-enhanced subject-surface structure."
            )
        else:
            pattern = "subject_texture_stochastic_regularization"
            note = (
                "Subject-only texture analysis finds elevated internal soft self-similarity in the texture-focused "
                "subject region, but the background control region remains more regular. This supports "
                "subject-surface stochastic regularization, though the comparison baseline is not clean enough "
                "for the stronger synthetic-texture conclusion."
            )

    elif (
        soft_recurrence_score >= 0.30
        and mean_neighbor_similarity >= 0.69
        and p90_neighbor_similarity >= 0.83
    ):
        if background_is_highly_repetitive:
            pattern = "subject_texture_stochastic_regularization"
            note = (
                "Subject-only texture analysis finds moderately elevated internal soft self-similarity in the "
                "texture-focused subject region. The background control region is highly repetitive, so the "
                "comparison baseline is treated cautiously. The result is compatible with stochastic "
                "regularization of subject-surface texture."
            )
        elif subject_background_soft_gap >= -0.20:
            pattern = "subject_texture_stochastic_regularization"
            note = (
                "Subject-only texture analysis finds moderately elevated internal soft self-similarity in the "
                "texture-focused subject region. This is compatible with stochastic regularization of "
                "subject-surface texture, but not strong enough for a more specific synthetic-texture conclusion."
            )
        else:
            pattern = "subject_texture_consistency_inconclusive"
            note = (
                "Subject-only texture analysis finds some internal regularity, but the background control region "
                "remains substantially more repetitive. The result stays inconclusive."
            )

    elif (
        mean_neighbor_similarity <= 0.62
        and p90_neighbor_similarity <= 0.78
        and dense_similarity_ratio <= 0.03
        and not background_is_highly_repetitive
        and subject_background_soft_gap <= 0.02
    ):
        pattern = "subject_texture_natural_variation_supported"
        note = (
            "Subject-only texture analysis does not show unusually dense internal self-similarity relative "
            "to the background control region; the subject texture remains broadly compatible with natural local variation."
        )
    else:
        pattern = "subject_texture_consistency_inconclusive"
        note = (
            "Subject-only texture analysis completed, but internal self-similarity is not sufficiently elevated "
            "for a specific synthetic-texture conclusion."
        )
                    
    stem = artifact_stem(image_path)
    overlay_path = output_dir / f"{stem}_subject_texture_consistency_overlay.png"
    _save_subject_similarity_overlay(
        gray=gray,
        sim_map=sim_map,
        subject_mask=texture_focus_mask,
        out_path=overlay_path,
    )
    mask_overlay_path = output_dir / f"{stem}_subject_texture_focus_mask.png"
    _save_mask_overlay(
        gray=gray,
        mask=texture_focus_mask,
        out_path=mask_overlay_path,
    )    
    bg_mask_overlay_path = output_dir / f"{stem}_background_texture_focus_mask.png"
    _save_mask_overlay(
        gray=gray,
        mask=background_texture_focus_mask,
        out_path=bg_mask_overlay_path,
    )    
    """
    print("[DEBUG][subject_texture_consistency]", {
        "patch_count": patch_count,
        "mean_neighbor_similarity": round(mean_neighbor_similarity, 4),
        "p90_neighbor_similarity": round(p90_neighbor_similarity, 4),
        "dense_similarity_ratio": round(dense_similarity_ratio, 4),
        "soft_recurrence_score": round(soft_recurrence_score, 4),
        "bg_patch_count": bg_patch_count,
        "bg_mean_neighbor_similarity": round(bg_mean_neighbor_similarity, 4),
        "bg_p90_neighbor_similarity": round(bg_p90_neighbor_similarity, 4),
        "bg_dense_similarity_ratio": round(bg_dense_similarity_ratio, 4),
        "bg_soft_recurrence_score": round(bg_soft_recurrence_score, 4),
        "subject_background_soft_gap": round(subject_background_soft_gap, 4),
        "subject_support_coverage": round(subject_support_coverage, 4),
        "background_support_coverage": round(background_support_coverage, 4),
        "texture_focus_area": int(np.count_nonzero(texture_focus_mask)),
        "background_texture_focus_area": int(np.count_nonzero(background_texture_focus_mask)),
        "background_area_cap": int(max_background_area),
        "pattern": pattern,
        "auto_profile_name": auto_profile_name,
        "background_is_highly_repetitive": bool(background_is_highly_repetitive)
    })    
    """
    return {
        "subject_texture_consistency": {
            "analysis_geometry": {
                "height": int(gray.shape[0]),
                "width": int(gray.shape[1]),
                "analysis_scale": float(analysis_scale) if analysis_scale is not None else None,
                "image_path_used": str(image_path),
            },            
            "focus_to_subject_ratio": float(focus_to_subject_ratio),
            "focus_to_image_ratio": float(focus_to_image_ratio),
            "support_reliable": True,            
            "config": {k: float(v) for k, v in cfg.items()},
            "pattern": pattern,
            "note": note,
            "scores": {
                "patch_count": int(patch_count),
                "mean_neighbor_similarity": float(mean_neighbor_similarity),
                "p90_neighbor_similarity": float(p90_neighbor_similarity),
                "dense_similarity_ratio": float(dense_similarity_ratio),
                "soft_recurrence_score": float(soft_recurrence_score),
                "subject_support_coverage": float(subject_support_coverage),
                "texture_focus_area": int(np.count_nonzero(texture_focus_mask)),
                "full_subject_area": int(np.count_nonzero(subject_mask)),
                "bg_patch_count": int(bg_patch_count),
                "bg_mean_neighbor_similarity": float(bg_mean_neighbor_similarity),
                "bg_p90_neighbor_similarity": float(bg_p90_neighbor_similarity),
                "bg_dense_similarity_ratio": float(bg_dense_similarity_ratio),
                "bg_soft_recurrence_score": float(bg_soft_recurrence_score),
                "background_support_coverage": float(background_support_coverage),
                "background_texture_focus_area": int(np.count_nonzero(background_texture_focus_mask)),
                "subject_background_mean_gap": float(subject_background_mean_gap),
                "subject_background_p90_gap": float(subject_background_p90_gap),
                "subject_background_dense_gap": float(subject_background_dense_gap),
                "subject_background_soft_gap": float(subject_background_soft_gap),
                "background_is_highly_repetitive": bool(background_is_highly_repetitive),
            },
            "profile": {
                "auto_profile_name": auto_profile_name,
                "mean_saturation": float(regime["mean_saturation"]),
                "high_saturation_ratio": float(regime["high_saturation_ratio"]),
                "gradient_active_ratio": float(regime["gradient_active_ratio"]),
                "surface_coverage_ratio": float(regime["surface_coverage_ratio"]),
                "clothing_score": float(regime["clothing_score"]),
                "skin_score": float(regime["skin_score"]),
            },            
            "artifacts": {
                "subject_texture_consistency_overlay": str(overlay_path),
                "subject_texture_focus_mask_overlay": str(mask_overlay_path),
                "background_texture_focus_mask_overlay": str(bg_mask_overlay_path),
            },
            "mask_support": {
                "subject_area": int(np.count_nonzero(subject_mask)),
                "texture_focus_area": int(np.count_nonzero(texture_focus_mask)),
                "focus_to_subject_ratio": float(focus_to_subject_ratio),
                "focus_to_image_ratio": float(focus_area / max(gray.size, 1)),
            }
        }
    }