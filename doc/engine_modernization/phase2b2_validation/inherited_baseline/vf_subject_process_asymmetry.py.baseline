#vf_subject_process_asymmetry.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
# geometry utility owner for the subject-region detector family
#
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import math
import cv2
import numpy as np
from dataclasses import dataclass

# ------------------------------------------------------------
# shared helpers
# ------------------------------------------------------------
def _load_bgr_image_exact(image_path: str | Path, shape_hw: Tuple[int, int]) -> np.ndarray:
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    h, w = shape_hw
    if img.shape[:2] != (h, w):
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return img

def _resize_mask(mask: np.ndarray, shape_hw: Tuple[int, int]) -> np.ndarray:
    h, w = shape_hw
    if mask.shape == (h, w):
        return mask.astype(np.uint8)
    out = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
    return (out > 0).astype(np.uint8)

def _validate_region_geometry(
    gray: np.ndarray,
    subject_mask: np.ndarray,
    boundary_mask: np.ndarray | None,
    background_mask: np.ndarray | None,
    expected_shape_hw: Tuple[int, int],
) -> None:
    h, w = expected_shape_hw
    if gray.shape != (h, w):
        raise ValueError(f"Gray shape mismatch: got {gray.shape}, expected {(h, w)}")
    if subject_mask.shape != (h, w):
        raise ValueError(f"Subject mask mismatch: got {subject_mask.shape}, expected {(h, w)}")
    if boundary_mask is not None and boundary_mask.shape != (h, w):
        raise ValueError(f"Boundary mask mismatch: got {boundary_mask.shape}, expected {(h, w)}")
    if background_mask is not None and background_mask.shape != (h, w):
        raise ValueError(f"Background mask mismatch: got {background_mask.shape}, expected {(h, w)}")

# ------------------------------------------------------------
# basic helpers
# ------------------------------------------------------------
def _load_mask(path: str | Path) -> np.ndarray:
    m = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"Failed to load mask: {path}")
    return (m > 127).astype(np.uint8)

def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def _normalize_map(m: np.ndarray) -> np.ndarray:
    m = m.astype(np.float32)
    mn = float(m.min()) if m.size else 0.0
    mx = float(m.max()) if m.size else 0.0
    if mx - mn < 1e-8:
        return np.zeros_like(m, dtype=np.float32)
    return (m - mn) / (mx - mn)

def _sigmoid(x: float, center: float, slope: float) -> float:
    z = (x - center) * slope
    return 1.0 / (1.0 + math.exp(-z))

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def _ratio(a: float, b: float, eps: float = 1e-6) -> float:
    return float(a) / float(b + eps)

def _hist_distance(values_a: np.ndarray, values_b: np.ndarray, bins: int = 24) -> float:
    """
    Simple normalized L1 histogram distance in [0, 1].
    """
    if values_a.size < 8 or values_b.size < 8:
        return 0.0
    lo = float(min(values_a.min(), values_b.min()))
    hi = float(max(values_a.max(), values_b.max()))
    if hi - lo < 1e-8:
        return 0.0
    hist_a, _ = np.histogram(values_a, bins=bins, range=(lo, hi), density=True)
    hist_b, _ = np.histogram(values_b, bins=bins, range=(lo, hi), density=True)
    dist = 0.5 * np.sum(np.abs(hist_a - hist_b))
    return _clamp01(dist / max(np.sum(hist_a), 1e-6))

# ------------------------------------------------------------
# patch feature extraction
# ------------------------------------------------------------
def _patch_entropy_u8(patch_u8: np.ndarray) -> float:
    hist = cv2.calcHist([patch_u8], [0], None, [32], [0, 256]).ravel().astype(np.float32)
    s = hist.sum()
    if s <= 1e-6:
        return 0.0
    p = hist / s
    p = p[p > 1e-9]
    return float(-(p * np.log2(p)).sum())

def _patch_dct_vector(gray_patch: np.ndarray, keep: int = 4) -> np.ndarray:
    """
    Compact low/mid-band DCT vector.
    We intentionally ignore the DC component.
    """
    patch_f = gray_patch.astype(np.float32) / 255.0
    dct = cv2.dct(patch_f)
    block = dct[:keep, :keep].copy()
    block[0, 0] = 0.0
    vec = block.flatten()
    norm = np.linalg.norm(vec) + 1e-8
    return (vec / norm).astype(np.float32)

def _extract_patch_features(gray_patch: np.ndarray) -> Dict[str, float | np.ndarray]:
    patch_u8 = gray_patch.astype(np.uint8)
    lap = cv2.Laplacian(gray_patch, cv2.CV_32F, ksize=3)
    gx = cv2.Sobel(gray_patch, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_patch, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.sqrt(gx * gx + gy * gy)
    blur = cv2.GaussianBlur(gray_patch, (0, 0), 1.2)
    residual = gray_patch.astype(np.float32) - blur.astype(np.float32)
    variance = float(np.var(gray_patch))
    lap_energy = float(np.mean(np.abs(lap)))
    grad_mean = float(np.mean(grad_mag))
    grad_std = float(np.std(grad_mag))
    residual_energy = float(np.mean(np.abs(residual)))
    entropy = _patch_entropy_u8(patch_u8)
    # directional gradient bias: high value means orientation is overly stable
    gx_abs = float(np.mean(np.abs(gx)))
    gy_abs = float(np.mean(np.abs(gy)))
    grad_axis_bias = abs(gx_abs - gy_abs) / (gx_abs + gy_abs + 1e-6)
    dct_vec = _patch_dct_vector(gray_patch, keep=4)
    return {
        "variance": variance,
        "laplacian_energy": lap_energy,
        "gradient_mean": grad_mean,
        "gradient_std": grad_std,
        "residual_energy": residual_energy,
        "entropy": entropy,
        "grad_axis_bias": float(grad_axis_bias),
        "dct_vec": dct_vec,
    }


@dataclass
class PatchCandidate:
    x: int
    y: int
    coverage: float
    bin_id: tuple[int, int]


def _collect_region_patch_candidates(
    gray: np.ndarray,
    region_mask: np.ndarray,
    patch_size: int = 32,
    stride: int = 16,
    min_coverage: float = 0.85,
    stratify_bins: int = 6,
) -> List[PatchCandidate]:
    h, w = gray.shape[:2]
    candidates: List[PatchCandidate] = []

    max_y = max(1, h - patch_size + 1)
    max_x = max(1, w - patch_size + 1)

    for y in range(0, h - patch_size + 1, stride):
        for x in range(0, w - patch_size + 1, stride):
            m = region_mask[y:y + patch_size, x:x + patch_size]
            coverage = float(m.mean())
            if coverage < min_coverage:
                continue

            # spatial bin for stratified sampling
            by = min(stratify_bins - 1, int((y / max_y) * stratify_bins))
            bx = min(stratify_bins - 1, int((x / max_x) * stratify_bins))

            candidates.append(
                PatchCandidate(
                    x=x,
                    y=y,
                    coverage=coverage,
                    bin_id=(by, bx),
                )
            )
    return candidates


def _select_stratified_candidates(
    candidates: List[PatchCandidate],
    max_patches: int | None = None,
    seed: int = 42,
) -> List[PatchCandidate]:
    if max_patches is None or len(candidates) <= max_patches:
        return candidates

    rng = np.random.default_rng(seed)

    # group by bin
    bins: Dict[tuple[int, int], List[PatchCandidate]] = {}
    for c in candidates:
        bins.setdefault(c.bin_id, []).append(c)

    # sort each bin by coverage descending so very good patches are preferred
    for bin_list in bins.values():
        bin_list.sort(key=lambda c: c.coverage, reverse=True)

    bin_keys = list(bins.keys())
    selected: List[PatchCandidate] = []

    # first pass: guarantee spatial spread
    for bk in bin_keys:
        if len(selected) >= max_patches:
            break
        if bins[bk]:
            selected.append(bins[bk].pop(0))

    if len(selected) >= max_patches:
        return selected[:max_patches]

    # second pass: weighted fill from remaining candidates
    remaining: List[PatchCandidate] = []
    for bin_list in bins.values():
        remaining.extend(bin_list)

    if not remaining:
        return selected

    # slightly favor high-coverage patches but still allow diversity
    weights = np.array([0.25 + c.coverage for c in remaining], dtype=np.float64)
    weights = weights / weights.sum()

    need = max_patches - len(selected)
    if need >= len(remaining):
        selected.extend(remaining)
        return selected

    idx = rng.choice(len(remaining), size=need, replace=False, p=weights)
    selected.extend([remaining[i] for i in idx])
    return selected


def _sample_region_patches(
    gray: np.ndarray,
    region_mask: np.ndarray,
    patch_size: int = 32,
    stride: int = 16,
    min_coverage: float = 0.85,
    max_patches: int | None = None,
    stratify_bins: int = 6,
    seed: int = 42,
) -> List[Dict[str, float | np.ndarray]]:
    candidates = _collect_region_patch_candidates(
        gray=gray,
        region_mask=region_mask,
        patch_size=patch_size,
        stride=stride,
        min_coverage=min_coverage,
        stratify_bins=stratify_bins,
    )

    selected = _select_stratified_candidates(
        candidates=candidates,
        max_patches=max_patches,
        seed=seed,
    )
    features: List[Dict[str, float | np.ndarray]] = []
    for c in selected:
        patch = gray[c.y:c.y + patch_size, c.x:c.x + patch_size]
        f = _extract_patch_features(patch)
        f["x"] = float(c.x)
        f["y"] = float(c.y)
        f["coverage"] = float(c.coverage)
        features.append(f)
    return features

# ------------------------------------------------------------
# aggregation
# ------------------------------------------------------------
def _aggregate_region_metrics(patches: List[Dict[str, float | np.ndarray]]) -> Dict[str, Any]:
    if not patches:
        empty_arr = np.zeros((0,), dtype=np.float32)
        return {
            "patch_count": 0,
            "variance_mean": 0.0,
            "variance_std": 0.0,
            "laplacian_energy_mean": 0.0,
            "gradient_mean_mean": 0.0,
            "gradient_std_mean": 0.0,
            "residual_energy_mean": 0.0,
            "residual_energy_std": 0.0,
            "entropy_mean": 0.0,
            "entropy_std": 0.0,
            "grad_axis_bias_mean": 0.0,
            "dct_similarity_mean": 0.0,
            "dct_similarity_p90": 0.0,
            "dct_similarity_std": 0.0,
            "_variance_values": empty_arr,
            "_lap_values": empty_arr,
            "_grad_values": empty_arr,
            "_residual_values": empty_arr,
            "_entropy_values": empty_arr,
            "_dct_sim_values": empty_arr,
        }

    def arr(key: str) -> np.ndarray:
        return np.array([_safe_float(p.get(key, 0.0)) for p in patches], dtype=np.float32)
    
    variance = arr("variance")
    lap_energy = arr("laplacian_energy")
    grad_mean = arr("gradient_mean")
    grad_std = arr("gradient_std")
    residual_energy = arr("residual_energy")
    entropy = arr("entropy")
    grad_axis_bias = arr("grad_axis_bias")
    dct_vecs = np.stack([p["dct_vec"] for p in patches], axis=0).astype(np.float32)
    dct_sims: List[float] = []
    if len(dct_vecs) >= 2:
        ref = dct_vecs.mean(axis=0)
        ref_norm = np.linalg.norm(ref) + 1e-8
        ref = ref / ref_norm
        for v in dct_vecs:
            sim = float(np.clip(np.dot(v, ref), -1.0, 1.0))
            dct_sims.append(sim)
    dct_sims_a = np.array(dct_sims, dtype=np.float32) if dct_sims else np.zeros((0,), dtype=np.float32)
    return {
        "patch_count": int(len(patches)),
        "variance_mean": float(variance.mean()),
        "variance_std": float(variance.std()),
        "laplacian_energy_mean": float(lap_energy.mean()),
        "gradient_mean_mean": float(grad_mean.mean()),
        "gradient_std_mean": float(grad_std.mean()),
        "residual_energy_mean": float(residual_energy.mean()),
        "residual_energy_std": float(residual_energy.std()),
        "entropy_mean": float(entropy.mean()),
        "entropy_std": float(entropy.std()),
        "grad_axis_bias_mean": float(grad_axis_bias.mean()),
        "dct_similarity_mean": float(dct_sims_a.mean()) if dct_sims_a.size else 0.0,
        "dct_similarity_p90": float(np.percentile(dct_sims_a, 90)) if dct_sims_a.size else 0.0,
        "dct_similarity_std": float(dct_sims_a.std()) if dct_sims_a.size else 0.0,
        # raw arrays for comparative features
        "_variance_values": variance,
        "_lap_values": lap_energy,
        "_grad_values": grad_mean,
        "_residual_values": residual_energy,
        "_entropy_values": entropy,
        "_dct_sim_values": dct_sims_a,
    }

#==================================================================
# flexible version with retries
#===================================================================
def _sample_regions_with_retries(
    gray: np.ndarray,
    subject_mask: np.ndarray,
    boundary_mask: np.ndarray,
    background_mask: np.ndarray,
    subject_budget: int,
    boundary_budget: int,
    background_budget: int,
    sampling_schedule: list[tuple[int, int, float]] | None = None,
    min_subject_patches: int = 12,
    min_boundary_patches: int = 4,
    min_background_patches: int = 12,
    debug: bool = False,
) -> Dict[str, Any]:
    """
    Progressive retry sampler for subject/boundary/background regions.
    Tries progressively smaller patches and lower coverage thresholds until
    enough support is available for the key regions.
    """
    
    if sampling_schedule is None:
        sampling_schedule = [
            (32, 16, 0.85),
            (24, 12, 0.75),
            (16, 8, 0.65),
        ]

    best = None
    for attempt_idx, (patch_size, stride, min_coverage) in enumerate(sampling_schedule, start=1):
        subject_patches = _sample_region_patches(
            gray,
            subject_mask,
            patch_size=patch_size,
            stride=stride,
            min_coverage=min_coverage,
            max_patches=subject_budget,
            stratify_bins=6,
            seed=42,
        )
        boundary_patches = _sample_region_patches(
            gray,
            boundary_mask,
            patch_size=patch_size,
            stride=stride,
            min_coverage=min_coverage,
            max_patches=boundary_budget,
            stratify_bins=6,
            seed=43,
        )
        background_patches = _sample_region_patches(
            gray,
            background_mask,
            patch_size=patch_size,
            stride=stride,
            min_coverage=min_coverage,
            max_patches=background_budget,
            stratify_bins=8,
            seed=44,
        )
        subject_count = len(subject_patches)
        boundary_count = len(boundary_patches)
        background_count = len(background_patches)
        if debug and (attempt_idx > 1):
            print(
                "[DEBUG][SPA][SAMPLING_ATTEMPT] "
                f"attempt={attempt_idx} | "
                f"patch_size={patch_size} | stride={stride} | min_coverage={min_coverage:.2f} | "
                f"subject={subject_count} | boundary={boundary_count} | background={background_count}"
            )
        attempt_result = {
            "subject_patches": subject_patches,
            "boundary_patches": boundary_patches,
            "background_patches": background_patches,
            "patch_size": patch_size,
            "stride": stride,
            "min_coverage": min_coverage,
            "attempt_index": attempt_idx,
            "subject_count": subject_count,
            "boundary_count": boundary_count,
            "background_count": background_count,
        }
        # Keep the best attempt seen so far, even if it does not fully satisfy thresholds.
        if best is None:
            best = attempt_result
        else:
            prev_score = (
                best["subject_count"] >= min_subject_patches,
                best["background_count"] >= min_background_patches,
                best["boundary_count"] >= min_boundary_patches,
                best["subject_count"] + best["boundary_count"] + best["background_count"],
            )
            new_score = (
                subject_count >= min_subject_patches,
                background_count >= min_background_patches,
                boundary_count >= min_boundary_patches,
                subject_count + boundary_count + background_count,
            )
            if new_score > prev_score:
                best = attempt_result
        # Success condition: subject + background are usable; boundary is allowed to be thinner.
        if (
            subject_count >= min_subject_patches
            and background_count >= min_background_patches
            and boundary_count >= min_boundary_patches
        ):
            return attempt_result
    return best

#=============================================================
# try resue resampling for subject region only 
#=============================================================
def _sample_single_region_with_retries(
    gray: np.ndarray,
    region_mask: np.ndarray,
    max_patches: int | None = None,
    sampling_schedule: list[tuple[int, int, float]] | None = None,
    stratify_bins: int = 6,
    seed: int = 42,
    min_required_patches: int = 12,
    debug_label: str | None = None,
) -> Dict[str, Any]:
    """
    Progressive retry sampler for a single region.
    Tries progressively smaller patches and lower coverage thresholds until
    enough support is available. Returns the best attempt even if thresholds
    are never fully met.
    """
    if sampling_schedule is None:
        sampling_schedule = [
            (32, 16, 0.85),
            (24, 12, 0.75),
            (16, 8, 0.65),
        ]

    best_attempt: Dict[str, Any] | None = None
    for attempt_index, (patch_size, stride, min_coverage) in enumerate(sampling_schedule, start=1):
        patches = _sample_region_patches(
            gray=gray,
            region_mask=region_mask,
            patch_size=patch_size,
            stride=stride,
            min_coverage=min_coverage,
            max_patches=max_patches,
            stratify_bins=stratify_bins,
            seed=seed,
        )
        patch_count = len(patches)
        if debug_label and (attempt_index > 1):
            print(
                f"[DEBUG][{debug_label}][SAMPLING_ATTEMPT] "
                f"attempt={attempt_index} | "
                f"patch_size={patch_size} | "
                f"stride={stride} | "
                f"min_coverage={min_coverage:.2f} | "
                f"patches={patch_count}"
            )
        attempt = {
            "patches": patches,
            "patch_count": patch_count,
            "patch_size": patch_size,
            "stride": stride,
            "min_coverage": min_coverage,
            "attempt_index": attempt_index,
            "sampling_rescued": attempt_index > 1,
        }
        if best_attempt is None or patch_count > best_attempt["patch_count"]:
            best_attempt = attempt
        if patch_count >= min_required_patches:
            return attempt
    return best_attempt if best_attempt is not None else {
        "patches": [],
        "patch_count": 0,
        "patch_size": sampling_schedule[-1][0],
        "stride": sampling_schedule[-1][1],
        "min_coverage": sampling_schedule[-1][2],
        "attempt_index": len(sampling_schedule),
        "sampling_rescued": len(sampling_schedule) > 1,
    }


def _comparative_features(
    subject_metrics: Dict[str, Any],
    boundary_metrics: Dict[str, Any],
    background_metrics: Dict[str, Any],
) -> Dict[str, float]:
    sv = subject_metrics
    bv = boundary_metrics
    bg = background_metrics
    # Lower subject values vs background often imply stronger subject regularization.
    variance_ratio = _ratio(sv["variance_mean"], bg["variance_mean"])
    lap_ratio = _ratio(sv["laplacian_energy_mean"], bg["laplacian_energy_mean"])
    residual_ratio = _ratio(sv["residual_energy_mean"], bg["residual_energy_mean"])
    entropy_ratio = _ratio(sv["entropy_mean"], bg["entropy_mean"])
    grad_std_ratio = _ratio(sv["gradient_std_mean"], bg["gradient_std_mean"])
    dct_similarity_gap = float(sv["dct_similarity_mean"] - bg["dct_similarity_mean"])
    boundary_subject_entropy_gap = float(bv["entropy_mean"] - sv["entropy_mean"])
    boundary_background_entropy_gap = float(bv["entropy_mean"] - bg["entropy_mean"])
    boundary_subject_residual_gap = float(bv["residual_energy_mean"] - sv["residual_energy_mean"])
    boundary_background_residual_gap = float(bv["residual_energy_mean"] - bg["residual_energy_mean"])
    variance_hist_distance = _hist_distance(sv["_variance_values"], bg["_variance_values"])
    residual_hist_distance = _hist_distance(sv["_residual_values"], bg["_residual_values"])
    entropy_hist_distance = _hist_distance(sv["_entropy_values"], bg["_entropy_values"])
    grad_hist_distance = _hist_distance(sv["_grad_values"], bg["_grad_values"])
    dct_hist_distance = _hist_distance(sv["_dct_sim_values"], bg["_dct_sim_values"]) if (
        sv["_dct_sim_values"].size >= 4 and bg["_dct_sim_values"].size >= 4
    ) else 0.0
    return {
        "subject_bg_variance_ratio": float(variance_ratio),
        "subject_bg_laplacian_ratio": float(lap_ratio),
        "subject_bg_residual_ratio": float(residual_ratio),
        "subject_bg_entropy_ratio": float(entropy_ratio),
        "subject_bg_gradient_std_ratio": float(grad_std_ratio),
        "subject_bg_dct_similarity_gap": float(dct_similarity_gap),
        "variance_hist_distance": float(variance_hist_distance),
        "residual_hist_distance": float(residual_hist_distance),
        "entropy_hist_distance": float(entropy_hist_distance),
        "gradient_hist_distance": float(grad_hist_distance),
        "dct_hist_distance": float(dct_hist_distance),
        "boundary_subject_entropy_gap": float(boundary_subject_entropy_gap),
        "boundary_background_entropy_gap": float(boundary_background_entropy_gap),
        "boundary_subject_residual_gap": float(boundary_subject_residual_gap),
        "boundary_background_residual_gap": float(boundary_background_residual_gap),
    }

# ------------------------------------------------------------
# scoring
# ------------------------------------------------------------
def _compute_baseline_reliability(
    subject_count: int,
    boundary_count: int,
    background_count: int,
    subject_texture_payload: Dict[str, Any] | None,
) -> Tuple[float, Dict[str, Any]]:
    penalties = 0.0
    controls: Dict[str, Any] = {
        "background_is_highly_repetitive": False,
        "valid_subject_patch_count": int(subject_count),
        "valid_boundary_patch_count": int(boundary_count),
        "valid_background_patch_count": int(background_count),
    }
    if subject_count < 20:
        penalties += 0.25
    if background_count < 20:
        penalties += 0.30
    if boundary_count < 8:
        penalties += 0.10
    if subject_texture_payload:
        block = subject_texture_payload.get("subject_texture_consistency", {})
        scores = block.get("scores", {})
        bg_high = bool(scores.get("background_is_highly_repetitive", False))
        controls["background_is_highly_repetitive"] = bg_high
        if bg_high:
            penalties += 0.25
        bg_soft = _safe_float(scores.get("bg_soft_recurrence_score", 0.0))
        if bg_soft >= 0.90:
            penalties += 0.15
    return _clamp01(1.0 - penalties), controls

def _compute_scores(
    subject_metrics: Dict[str, Any],
    boundary_metrics: Dict[str, Any],
    background_metrics: Dict[str, Any],
    features: Dict[str, float],
    baseline_reliability_score: float,
    subject_texture_payload: Dict[str, Any] | None = None,
    region_fft_payload: Dict[str, Any] | None = None,
) -> Dict[str, float]:
    # regularization dominance:
    # lower subject microtexture / entropy / residual than background,
    # plus stronger subject DCT stability.
    variance_dom = _sigmoid(1.0 - features["subject_bg_variance_ratio"], center=0.10, slope=8.0)
    residual_dom = _sigmoid(1.0 - features["subject_bg_residual_ratio"], center=0.08, slope=8.0)
    entropy_dom = _sigmoid(1.0 - features["subject_bg_entropy_ratio"], center=0.05, slope=8.0)
    grad_dom = _sigmoid(1.0 - features["subject_bg_gradient_std_ratio"], center=0.08, slope=8.0)
    dct_dom = _sigmoid(features["subject_bg_dct_similarity_gap"], center=0.03, slope=10.0)
    regularization_dominance_score = _clamp01(
        0.24 * variance_dom +
        0.22 * residual_dom +
        0.20 * entropy_dom +
        0.14 * grad_dom +
        0.20 * dct_dom
    )
    # distribution divergence:
    process_divergence_score = _clamp01(
        0.24 * features["variance_hist_distance"] +
        0.24 * features["residual_hist_distance"] +
        0.20 * features["entropy_hist_distance"] +
        0.14 * features["gradient_hist_distance"] +
        0.18 * features["dct_hist_distance"]
    )
    # boundary paradox:
    # boundary roughly tracks background more than subject interior.
    entropy_paradox = _sigmoid(
        abs(features["boundary_subject_entropy_gap"]) - abs(features["boundary_background_entropy_gap"]),
        center=0.05,
        slope=8.0,
    )
    residual_paradox = _sigmoid(
        abs(features["boundary_subject_residual_gap"]) - abs(features["boundary_background_residual_gap"]),
        center=0.75,
        slope=0.8,
    )
    boundary_paradox_score = _clamp01(0.55 * entropy_paradox + 0.45 * residual_paradox)
    # small carry-forward stabilizers
    carry_forward = 0.0
    if subject_texture_payload:
        block = subject_texture_payload.get("subject_texture_consistency", {})
        scores = block.get("scores", {})
        subject_bg_soft_gap = _safe_float(scores.get("subject_background_soft_gap", 0.0))
        carry_forward += 0.08 * _sigmoid(subject_bg_soft_gap, center=0.05, slope=8.0)
    if region_fft_payload:
        block = region_fft_payload.get("region_fft", {})
        comp = block.get("comparative_features", {})
        fft_gap = _safe_float(comp.get("subject_vs_background_fft_gap", 0.0))
        carry_forward += 0.06 * _sigmoid(fft_gap, center=0.03, slope=10.0)
    asymmetry_score = _clamp01(
        (
            0.45 * regularization_dominance_score +
            0.40 * process_divergence_score +
            0.15 * boundary_paradox_score +
            carry_forward
        ) * baseline_reliability_score
    )
    return {
        "regularization_dominance_score": float(regularization_dominance_score),
        "process_divergence_score": float(process_divergence_score),
        "boundary_paradox_score": float(boundary_paradox_score),
        "baseline_reliability_score": float(baseline_reliability_score),
        "asymmetry_score": float(asymmetry_score),
    }

def _interpret_pattern(scores: Dict[str, float], controls: Dict[str, Any], ) -> Tuple[str, str]:
    asym = scores["asymmetry_score"]
    reg = scores["regularization_dominance_score"]
    div = scores["process_divergence_score"]
    par = scores["boundary_paradox_score"]
    rel = scores["baseline_reliability_score"]
    rev = float(scores.get("reverse_asymmetry_score", 0.0) or 0.0)
    bg_high = bool(controls.get("background_is_highly_repetitive", False))
    subj_n = int(controls.get("valid_subject_patch_count", 0))
    bg_n = int(controls.get("valid_background_patch_count", 0))
    # damping if recue resampling was needed
    rescued = bool(scores.get("sampling_rescued", False))
    attempt = int(scores.get("sampling_attempt_index", 1))
    if controls.get("region_geometry_unreliable"):
        return (
            "subject_process_asymmetry_support_unreliable",
            "Subject/background process asymmetry analysis was not considered stable because the subject-region support is too small or unreliable. "
            "The result should not be interpreted as strong subject-level asymmetry.",
        )        
    if rescued and attempt >= 3 and asym >= 0.52:
        return (
            "subject_process_asymmetry_inconclusive",
            "Subject/background asymmetry became measurable only under aggressive rescue sampling. "
            "The result is therefore treated as contextual and not stable enough for a stronger asymmetry interpretation.",
        )        
    if subj_n < 12 or bg_n < 12:
        return (
            "subject_process_asymmetry_inconclusive",
            "Subject/background asymmetry analysis completed, but the available region support is too limited for a stable reading.",
        )
    if rel < 0.45:
        return (
            "subject_process_asymmetry_inconclusive",
            "Some subject/background process asymmetry is present, but the comparison baseline is too unreliable for a stable interpretation.",
        )
    # Strong asymmetry can arise from either: 1. subject smoother (reg) or  2. subject more detailed (reverse)
    if asym >= 0.68 and ( (reg >= 0.50 and div >= 0.50) or (rev >= 0.65 and div >= 0.50) ):
        return (
            "subject_process_asymmetry_strong",
            "Strong subject-vs-background process asymmetry detected. The subject interior appears more regularized and distributionally distinct than the surrounding scene.",
        )
    elif asym >= 0.52 and  (reg >= 0.45 or rev >= 0.55):
        return (
            "subject_surface_regularization_dominant",
            "Moderate subject-surface regularization is present relative to the background, suggesting different rendering or enhancement behavior across regions.",
        )
    if asym >= 0.34 and (reg >= 0.40 or div >= 0.40 or par >= 0.40):
        note = (
            "Meaningful subject/background texture-process asymmetry is present, but the evidence remains contextual rather than decisive."
        )
        if bg_high:
            note += " The background appears highly repetitive, so comparison is treated as a moderator rather than a veto."
        return (
            "subject_background_texture_asymmetry",
            note,
        )
    if asym <= 0.20 and reg <= 0.25 and div <= 0.25:
        return (
            "subject_background_process_convergence_supported",
            "Subject and background region statistics remain broadly compatible with a shared rendering / processing pipeline.",
        )
    return (
        "subject_process_asymmetry_inconclusive",
        "Subject/background asymmetry analysis completed, but no stable process split emerges from the current region comparison.",
    )

# ------------------------------------------------------------
# optional heatmap
# ------------------------------------------------------------
def _build_asymmetry_heatmap(gray: np.ndarray, subject_mask: np.ndarray, background_mask: np.ndarray, patch_size: int = 32, stride: int = 16, min_coverage: float = 0.85, ) -> np.ndarray:
    """
    Light-weight visual aid:
    highlight local residual + entropy suppression relative to the image median.
    """
    h, w = gray.shape[:2]
    heat = np.zeros((h, w), dtype=np.float32)
    counts = np.zeros((h, w), dtype=np.float32)
    global_blur = cv2.GaussianBlur(gray, (0, 0), 1.2)
    global_res = np.abs(gray.astype(np.float32) - global_blur.astype(np.float32))
    for y in range(0, h - patch_size + 1, stride):
        for x in range(0, w - patch_size + 1, stride):
            subj_cov = float(subject_mask[y:y + patch_size, x:x + patch_size].mean())
            bg_cov = float(background_mask[y:y + patch_size, x:x + patch_size].mean())
            if max(subj_cov, bg_cov) < min_coverage:
                continue
            patch = gray[y:y + patch_size, x:x + patch_size]
            patch_u8 = patch.astype(np.uint8)
            entropy = _patch_entropy_u8(patch_u8)
            res_mean = float(global_res[y:y + patch_size, x:x + patch_size].mean())
            # Lower entropy / lower residual = more regularized
            score = (1.0 / (1.0 + entropy)) + (1.0 / (1.0 + res_mean))
            if subj_cov > bg_cov:
                score *= 1.15
            heat[y:y + patch_size, x:x + patch_size] += score
            counts[y:y + patch_size, x:x + patch_size] += 1.0
    heat = heat / np.maximum(counts, 1.0)
    return _normalize_map(heat)

def _write_overlay(image_bgr: np.ndarray, heat: np.ndarray, out_path: Path) -> str:
    heat_u8 = np.clip(heat * 255.0, 0, 255).astype(np.uint8)
    color = cv2.applyColorMap(heat_u8, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(image_bgr, 0.65, color, 0.35, 0.0)
    cv2.imwrite(str(out_path), overlay)
    return str(out_path)

# ------------------------------------------------------------
# main entry
# ------------------------------------------------------------
def run_subject_process_asymmetry_analysis(
    subject,
    boundry,
    background,
    image_path: str | Path,
    subject_mask_path: str | Path,
    boundary_band_path: str | Path,
    background_mask_path: str | Path,
    output_dir: str | Path,
    analysis_shape_hw: tuple[int, int] | None = None,
    analysis_scale: float | None = None,
    subject_texture_payload: Dict[str, Any] | None = None,
    region_fft_payload: Dict[str, Any] | None = None,
    patch_size: int = 32,
    stride: int = 16,
    min_coverage: float = 0.85,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if analysis_shape_hw is None:
        raise ValueError(
            "analysis_shape_hw must be provided by the gatekeeper so that "
            "image and all region masks share one explicit analysis geometry."
        )
    image_bgr = _load_bgr_image_exact(image_path, analysis_shape_hw)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    subject_mask_full = _load_mask(subject_mask_path)
    boundary_mask_full = _load_mask(boundary_band_path)
    background_mask_full = _load_mask(background_mask_path)
    subject_mask = _resize_mask(subject_mask_full, analysis_shape_hw)
    boundary_mask = _resize_mask(boundary_mask_full, analysis_shape_hw)
    background_mask = _resize_mask(background_mask_full, analysis_shape_hw)
    _validate_region_geometry(
        gray=gray,
        subject_mask=subject_mask,
        boundary_mask=boundary_mask,
        background_mask=background_mask,
        expected_shape_hw=analysis_shape_hw,
    )        
    # number of patches for subject, boundry and background depends on analysis_mode 
    # (normal photo versus heavily subject-based Instagram like model)
    sampling_result = _sample_regions_with_retries(
        gray=gray,
        subject_mask=subject_mask,
        boundary_mask=boundary_mask,
        background_mask=background_mask,
        subject_budget=subject,
        boundary_budget=boundry,
        background_budget=background,
        sampling_schedule=[
            (patch_size, stride, min_coverage),
            (24, 12, 0.75),
            (16, 8, 0.65),
        ],
        min_subject_patches=12,
        min_boundary_patches=4,
        min_background_patches=12,
        debug=False
    )

    subject_patches = sampling_result["subject_patches"]
    boundary_patches = sampling_result["boundary_patches"]
    background_patches = sampling_result["background_patches"]

    effective_patch_size = sampling_result["patch_size"]
    effective_stride = sampling_result["stride"]
    effective_min_coverage = sampling_result["min_coverage"]
    sampling_attempt_index = sampling_result["attempt_index"]

    subject_metrics = _aggregate_region_metrics(subject_patches)
    boundary_metrics = _aggregate_region_metrics(boundary_patches)
    background_metrics = _aggregate_region_metrics(background_patches)

    if (
        subject_metrics.get("patch_count", 0) < 12
        or boundary_metrics.get("patch_count", 0) < 4
        or background_metrics.get("patch_count", 0) < 12
    ):
        print(
            "[DEBUG][SPA][LOW_PATCH_FINAL] "
            f"subject={subject_metrics.get('patch_count')} | "
            f"boundary={boundary_metrics.get('patch_count')} | "
            f"background={background_metrics.get('patch_count')} | "
            f"patch_size={effective_patch_size} | "
            f"stride={effective_stride} | "
            f"min_coverage={effective_min_coverage:.2f} | "
            f"attempt={sampling_attempt_index} | "
            f"image_shape={gray.shape} | "
            f"mask_subject_sum={int(subject_mask.sum())} | "
            f"mask_boundary_sum={int(boundary_mask.sum())}"
        )
    
    # Comparative features
    features = _comparative_features(subject_metrics, boundary_metrics, background_metrics)
    # ------------------------------------------------------------
    # Reverse asymmetry: subject more detailed than background
    # ------------------------------------------------------------
    reverse_variance = _sigmoid(features["subject_bg_variance_ratio"], center=1.4, slope=4.0)
    reverse_residual = _sigmoid(features["subject_bg_residual_ratio"], center=2.0, slope=1.2)
    reverse_entropy = _sigmoid(features["subject_bg_entropy_ratio"], center=1.4, slope=4.0)
    reverse_asymmetry_score = _clamp01(0.35 * reverse_variance + 0.35 * reverse_residual + 0.30 * reverse_entropy)        
    
    
    baseline_reliability_score, controls = _compute_baseline_reliability(subject_count=subject_metrics["patch_count"], boundary_count=boundary_metrics["patch_count"],
        background_count=background_metrics["patch_count"], subject_texture_payload=subject_texture_payload,)
    scores = _compute_scores(subject_metrics=subject_metrics, boundary_metrics=boundary_metrics, background_metrics=background_metrics,
        features=features, baseline_reliability_score=baseline_reliability_score, subject_texture_payload=subject_texture_payload, region_fft_payload=region_fft_payload,)
    #================================================================================================
    # if rescue resampling was needed apply a reliability dampening based on which attempt was needed
    #=================================================================================================
    sampling_attempt_index = sampling_result["attempt_index"]
    sampling_reliability_factor = 1.0
    if sampling_attempt_index == 2:
        sampling_reliability_factor = 0.85
    elif sampling_attempt_index >= 3:
        sampling_reliability_factor = 0.70
        
    subject_mask_area = int(np.count_nonzero(subject_mask))
    background_mask_area = int(np.count_nonzero(background_mask))
    image_area = int(gray.shape[0] * gray.shape[1])
    subject_mask_area_ratio = subject_mask_area / max(image_area, 1)
    background_mask_area_ratio = background_mask_area / max(image_area, 1)
    region_geometry_unreliable = subject_mask_area_ratio < 0.08        
        
    scores["asymmetry_score"] *= sampling_reliability_factor
    scores["regularization_dominance_score"] *= sampling_reliability_factor
    scores["process_divergence_score"] *= sampling_reliability_factor
    scores["boundary_paradox_score"] *= sampling_reliability_factor
    scores["sampling_reliability_factor"] = sampling_reliability_factor
    scores["sampling_attempt_index"] = sampling_attempt_index
    scores["sampling_rescued"] = bool(sampling_attempt_index > 1)
    
    if region_geometry_unreliable:
        scores["asymmetry_score"] = min(float(scores["asymmetry_score"]), 0.32)
        scores["regularization_dominance_score"] = min(
            float(scores.get("regularization_dominance_score", 0.0)), 0.32
        )
        controls["region_geometry_unreliable"] = True
        controls["subject_mask_area_ratio"] = float(subject_mask_area_ratio)
        controls["background_mask_area_ratio"] = float(background_mask_area_ratio)
    else:
        controls["region_geometry_unreliable"] = False
        controls["subject_mask_area_ratio"] = float(subject_mask_area_ratio)
        controls["background_mask_area_ratio"] = float(background_mask_area_ratio)    
    
    # ------------------------------------------------------------
    # Subject-dominant / weak-background fallback mode
    # Modern Instagram-style images often have a very large subject and a blurred / trivial background that is a poor baseline.
    # In those cases, allow subject-only regularization cues to lift the final asymmetry interpretation.
    # ------------------------------------------------------------
    subject_count = int(subject_metrics["patch_count"])
    background_count = int(background_metrics["patch_count"])
    total_region_count = max(subject_count + background_count, 1)
    subject_ratio = subject_count / total_region_count
    background_entropy_ratio = float(features.get("subject_bg_entropy_ratio", 1.0) or 1.0)
    background_weak = (background_count < 20 or background_entropy_ratio > 0.90)
    subject_dominant = subject_ratio > 0.60
    use_subject_only_mode = subject_dominant or background_weak
    # Use bounded subject-internal metrics rather than raw "1 - mean", because the raw region metrics are not normalized to [0, 1].
    # These thresholds are heuristic and intended as a first-pass.
    subject_flatness = _sigmoid(1.0 / (subject_metrics["variance_mean"] + 1e-6), center=0.015, slope=120.0,)
    subject_residual_suppression = _sigmoid(1.0 / (subject_metrics["residual_energy_mean"] + 1e-6), center=0.35, slope=6.0,)
    subject_entropy_suppression = _sigmoid(1.0 / (subject_metrics["entropy_mean"] + 1e-6), center=0.22, slope=10.0,)
    subject_dct_stability = _sigmoid(subject_metrics["dct_similarity_mean"], center=0.85, slope=10.0,)
    subject_gradient_suppression = _sigmoid(1.0 / (subject_metrics["gradient_std_mean"] + 1e-6), center=0.08, slope=40.0,)    
    subject_only_score = _clamp01(0.24 * subject_flatness + 0.24 * subject_residual_suppression + 0.18 * subject_entropy_suppression + 0.18 * subject_dct_stability + 0.16 * subject_gradient_suppression)
    # If the background is weak or the subject dominates the frame, allow the subject-only score to support the final score.
    # Do not replace the comparative score; only lift it moderately.
    comparative_asymmetry = float(scores.get("asymmetry_score", 0.0) or 0.0)
    # Combine three regimes:
    # 1. comparative asymmetry (original)
    # 2. subject-only regularization (smooth subject)
    # 3. reverse asymmetry (subject sharper than background)
    combined_asymmetry = comparative_asymmetry
    if use_subject_only_mode:
        combined_asymmetry = max(combined_asymmetry, subject_only_score * 0.90)
    # Reverse asymmetry should ALWAYS be considered (not only in subject-only mode)
    combined_asymmetry = max(combined_asymmetry, reverse_asymmetry_score * 0.85)
    scores["asymmetry_score"] = float(combined_asymmetry)
    scores["subject_only_score"] = float(subject_only_score)
    scores["reverse_asymmetry_score"] = float(reverse_asymmetry_score)
    scores["subject_only_mode_used"] = bool(use_subject_only_mode)
    # Strengthen regularization dominance if subject-only mode was active
    if use_subject_only_mode:
        scores["regularization_dominance_score"] = max(
            float(scores.get("regularization_dominance_score", 0.0) or 0.0),
            subject_only_score * 0.85,
        )
    controls["subject_ratio"] = float(subject_ratio)
    controls["background_weak"] = bool(background_weak)
    controls["subject_dominant"] = bool(subject_dominant)        
    pattern, note = _interpret_pattern(scores, controls)
    # Make the note explicit when subject-only fallback was active.
    if scores.get("subject_only_mode_used"):
        note += (
            " Background baseline was treated as weak or the subject was dominant in frame, "
            "so subject-internal material regularization cues were given additional weight. "
        )
    heat = _build_asymmetry_heatmap(
        gray=gray,
        subject_mask=subject_mask,
        background_mask=background_mask,
        patch_size=patch_size,
        stride=stride,
        min_coverage=min_coverage,
    )
    overlay_path = output_dir / f"{image_path.stem}_subject_process_asymmetry_overlay.jpg"
    overlay_path_str = _write_overlay(image_bgr, heat, overlay_path)
    """
    print(
        "[DEBUG][subject_process_asymmetry]",
        {
            "pattern": pattern,
            "asymmetry_score": scores.get("asymmetry_score"),
            "regularization_dominance_score": scores.get("regularization_dominance_score"),
            "process_divergence_score": scores.get("process_divergence_score"),
            "boundary_paradox_score": scores.get("boundary_paradox_score"),
            "baseline_reliability_score": scores.get("baseline_reliability_score"),
            "subject_only_score": scores.get("subject_only_score"),
            "subject_only_mode_used": scores.get("subject_only_mode_used"),
            "reverse_asymmetry_score": scores.get("reverse_asymmetry_score"),
            "subject_patch_count": subject_metrics.get("patch_count"),
            "boundary_patch_count": boundary_metrics.get("patch_count"),
            "background_patch_count": background_metrics.get("patch_count"),
            "subject_ratio": controls.get("subject_ratio"),
            "background_weak": controls.get("background_weak"),
            "subject_dominant": controls.get("subject_dominant"),
            "subject_bg_variance_ratio": features.get("subject_bg_variance_ratio"),
            "subject_bg_residual_ratio": features.get("subject_bg_residual_ratio"),
            "subject_bg_entropy_ratio": features.get("subject_bg_entropy_ratio"),
            "variance_hist_distance": features.get("variance_hist_distance"),
            "residual_hist_distance": features.get("residual_hist_distance"),
            "entropy_hist_distance": features.get("entropy_hist_distance"),
        }
    )
    """
    def clean_region_metrics(m: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in m.items() if not str(k).startswith("_")}

    return {
        "subject_process_asymmetry": {
            "analysis_geometry": {
                "height": int(gray.shape[0]),
                "width": int(gray.shape[1]),
                "analysis_scale": float(analysis_scale) if analysis_scale is not None else None,
                "image_path_used": str(image_path),
            },            
            "pattern": pattern,
            "note": note,
            "scores": scores,
            "subject_metrics": clean_region_metrics(subject_metrics),
            "boundary_metrics": clean_region_metrics(boundary_metrics),
            "background_metrics": clean_region_metrics(background_metrics),
            "comparative_features": features,
            "controls": {
                **controls,
                "effective_patch_size": int(effective_patch_size),
                "effective_stride": int(effective_stride),
                "effective_min_coverage": float(effective_min_coverage),
                "sampling_attempt_index": int(sampling_attempt_index),
            },
            "artifacts": {
                "subject_input": str(subject_mask_path),
                "boundary_input": str(boundary_band_path),
                "background_input": str(background_mask_path),
                "subject_process_asymmetry_overlay": overlay_path_str,
            },
        }
    }