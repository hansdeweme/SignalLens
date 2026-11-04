#vf_fft.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#
# Like patch-similarity can trigger on legitimate repeated scene geometry: the detector is seeing periodicity, not necessarily syntheticity.
# This module behaves like a “structured periodicity / raster regularity detector”, not a “synthetic image detector”

from __future__ import annotations
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageColor
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# ============================================================
# configuration
# ============================================================

presentation_mode = True # Set to True for more visually compelling output.

DEFAULT_MAX_DIM = 1024
DEFAULT_PEAK_PERCENTILE = 99.7
DEFAULT_CENTER_EXCLUSION_RATIO = 0.08
DEFAULT_EDGE_EXCLUSION_RATIO = 0.03

# ============================================================
# dataclasses
# ============================================================

@dataclass
class PeakPoint:
    y: int
    x: int
    value: float
    radius: float
    angle_deg: float

@dataclass
class GridHypothesis:
    fx: float
    fy: float
    wavelength_x: float | None
    wavelength_y: float | None
    angle_deg: float
    strength: float
    source_peak_count: int

@dataclass
class MultiGridHypothesis:
    hypotheses: List[GridHypothesis]
    combined_strength: float

#============================================================
# helpers
#============================================================

def pair_symmetric_peaks(
    peaks: List[PeakPoint],
    h: int,
    w: int,
    tol_px: float = 3.0,
) -> List[Tuple[PeakPoint, PeakPoint]]:
    """
    Pair peaks that are approximately symmetric around the FFT center.
    """
    cy = h / 2.0
    cx = w / 2.0
    used: set[int] = set()
    pairs: List[Tuple[PeakPoint, PeakPoint]] = []
    for i, p in enumerate(peaks):
        if i in used:
            continue

        target_y = 2.0 * cy - p.y
        target_x = 2.0 * cx - p.x
        best_j = None
        best_dist = float("inf")
        for j, q in enumerate(peaks):
            if j == i or j in used:
                continue
            dist = math.hypot(q.y - target_y, q.x - target_x)
            if dist < best_dist:
                best_dist = dist
                best_j = j
        if best_j is not None and best_dist <= tol_px:
            used.add(i)
            used.add(best_j)
            pairs.append((p, peaks[best_j]))
    return pairs

def select_dominant_grid_hypothesis(peaks: List[PeakPoint], h: int, w: int,) -> GridHypothesis | None:
    """
    Use the strongest approximately symmetric off-center FFT peak pair
    as a simple first grid hypothesis.
    """
    if not peaks:
        return None
    pairs = pair_symmetric_peaks(peaks, h=h, w=w, tol_px=3.0)
    if not pairs:
        return None
    cy = h / 2.0
    cx = w / 2.0

    best_pair = None
    best_strength = -1.0
    for p, q in pairs:
        strength = 0.5 * (float(p.value) + float(q.value))
        if strength > best_strength:
            best_strength = strength
            best_pair = (p, q)
    if best_pair is None:
        return None

    p, q = best_pair
    # Use one side of the pair relative to center.
    dy = float(p.y - cy)
    dx = float(p.x - cx)
    # cycles per pixel in x/y
    fx = abs(dx) / float(w)
    fy = abs(dy) / float(h)
    wavelength_x = (1.0 / fx) if fx > 1e-8 else None
    wavelength_y = (1.0 / fy) if fy > 1e-8 else None
    angle_deg = float(np.degrees(np.arctan2(dy, dx)))
    return GridHypothesis(
        fx=float(fx),
        fy=float(fy),
        wavelength_x=float(wavelength_x) if wavelength_x is not None else None,
        wavelength_y=float(wavelength_y) if wavelength_y is not None else None,
        angle_deg=angle_deg,
        strength=float(best_strength),
        source_peak_count=len(pairs),
    )

def build_spatial_grid_response(image_gray: np.ndarray, hypothesis: GridHypothesis,) -> np.ndarray:
    """
    Project the dominant FFT periodicity hypothesis back into image space and
    correlate it with a lightly high-passed image.
    """
    h, w = image_gray.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    # Two orthogonal sinusoidal components from the inferred x/y frequencies.
    phase = 2.0 * np.pi * (hypothesis.fx * xx + hypothesis.fy * yy)
    grid_wave = np.cos(phase).astype(np.float32)

    img = image_gray.astype(np.float32)
    blur = gaussian_blur_separable(img, sigma=1.2)
    residual = img - blur

    response = np.abs(residual * grid_wave)
    return response

def gaussian_blur_separable(image: np.ndarray, sigma: float = 1.2) -> np.ndarray:
    """
    Lightweight numpy-only Gaussian blur approximation via 1D kernel convolution.
    Keeps vf_fft.py self-contained.
    """
    radius = max(1, int(round(3.0 * sigma)))
    x = np.arange(-radius, radius + 1, dtype=np.float32)
    kernel = np.exp(-(x * x) / (2.0 * sigma * sigma)).astype(np.float32)
    kernel /= np.sum(kernel)
    temp = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), axis=1, arr=image)
    out = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), axis=0, arr=temp)
    return out.astype(np.float32)

def save_grid_response_image(
    response_map: np.ndarray,
    out_path: str | Path,
) -> None:
    u8 = normalize_to_u8(response_map)
    Image.fromarray(u8, mode="L").save(out_path)

def save_grid_overlay_image(
    image_gray: np.ndarray,
    hypothesis: GridHypothesis,
    response_map: np.ndarray,
    out_path: str | Path,
    max_lines: int = 120,
    response_percentile: float = 80.0,
    heat_strength: float = 0.75,
    line_strength_scale: float = 0.85,
) -> None:
    """
    Hybrid FFT grid overlay:
    1. Soft heatmap from the reconstructed spatial grid response
    2. Segmented inferred line families from wavelength_x / wavelength_y
    """
    h, w = image_gray.shape
    # ---- Heatmap base ----
    if presentation_mode:
        heat_strength = 0.85
        response_percentile = 78.0
    base = blend_heatmap_on_grayscale(image_gray=image_gray, response_map=response_map, heat_strength=heat_strength,)
    draw = ImageDraw.Draw(base)
    response_u8 = normalize_to_u8(response_map)
    threshold = np.percentile(response_u8, response_percentile) if response_u8.size else 255
    if presentation_mode:
        threshold = threshold * 1.1
    # =========================================================
    # VERTICAL LINES (from wavelength_x)
    # =========================================================
    if hypothesis.wavelength_x is not None and 4.0 <= hypothesis.wavelength_x <= 256.0:
        step_x = max(1, int(round(hypothesis.wavelength_x)))
        # ---- Phase alignment ----
        best_offset = 0
        best_score = -1.0
        max_offset_scan = min(step_x, w)
        for offset in range(max_offset_scan):
            xs = list(range(offset, w, step_x))
            vals = []
            for x in xs:
                band = response_u8[:, max(0, x - 1):min(w, x + 2)]
                if band.size:
                    vals.append(float(np.mean(band)))
            score = float(np.mean(vals)) if vals else 0.0
            if score > best_score:
                best_score = score
                best_offset = offset
        # ---- Draw segmented vertical lines ----
        count = 0
        for x in range(best_offset, w, step_x):
            if count >= max_lines:
                break
            band = response_u8[:, max(0, x - 1):min(w, x + 2)]
            score = float(np.mean(band)) if band.size else 0.0
            if score < threshold:
                continue
            # Softer color scaling
            s = max(0.0, min(1.0, (score / 255.0) * line_strength_scale))
            color = (
                int(180),
                int(120 + 40 * (1.0 - s)),
                int(120 + 30 * (1.0 - s)),
            )
            # ---- Segmented drawing ----
            for yy in range(0, h, 6):
                segment = response_u8[yy:yy+6, max(0, x-1):min(w, x+2)]
                if segment.size and np.mean(segment) >= threshold:
                    draw.line((x, yy, x, min(h, yy+6)), fill=color, width = 2 if presentation_mode else 1)
            count += 1
    # =========================================================
    # HORIZONTAL LINES (from wavelength_y)
    # =========================================================
    if hypothesis.wavelength_y is not None and 4.0 <= hypothesis.wavelength_y <= 256.0:
        step_y = max(1, int(round(hypothesis.wavelength_y)))
        # ---- Phase alignment ----
        best_offset = 0
        best_score = -1.0
        max_offset_scan = min(step_y, h)
        for offset in range(max_offset_scan):
            ys = list(range(offset, h, step_y))
            vals = []
            for y in ys:
                band = response_u8[max(0, y - 1):min(h, y + 2), :]
                if band.size:
                    vals.append(float(np.mean(band)))
            score = float(np.mean(vals)) if vals else 0.0
            if score > best_score:
                best_score = score
                best_offset = offset
        # ---- Draw segmented horizontal lines ----
        count = 0
        for y in range(best_offset, h, step_y):
            if count >= max_lines:
                break
            band = response_u8[max(0, y - 1):min(h, y + 2), :]
            score = float(np.mean(band)) if band.size else 0.0
            if score < threshold:
                continue
            s = max(0.0, min(1.0, (score / 255.0) * line_strength_scale))
            color = (
                int(120 + 30 * (1.0 - s)),
                int(180),
                int(120 + 40 * (1.0 - s)),
            )
            # ---- Segmented drawing ----
            for xx in range(0, w, 6):
                segment = response_u8[max(0, y-1):min(h, y+2), xx:xx+6]
                if segment.size and np.mean(segment) >= threshold:
                    draw.line((xx, y, min(w, xx+6), y), fill=color, width = 2 if presentation_mode else 1)

            count += 1
    # =========================================================
    # CENTER MARKER (debugging aid)
    # =========================================================
    cx = w // 2
    cy = h // 2
    draw.line((cx - 4, cy, cx + 4, cy), fill=(220, 220, 220), width = 2 if presentation_mode else 1)
    draw.line((cx, cy - 4, cx, cy + 4), fill=(220, 220, 220), width = 2 if presentation_mode else 1)
    # ---- Save result ----
    base.save(out_path)
        
def summarize_grid_hypothesis(hypothesis: GridHypothesis | None, response_map: np.ndarray | None,) -> Dict[str, Any]:
    if hypothesis is None:
        return {
            "grid_hypothesis_present": False,
            "dominant_fx": 0.0,
            "dominant_fy": 0.0,
            "dominant_wavelength_x": None,
            "dominant_wavelength_y": None,
            "dominant_angle_deg": None,
            "grid_hypothesis_strength": 0.0,
            "grid_response_score": 0.0,
            "paired_peak_count": 0,
        }
    grid_response_score = 0.0
    if response_map is not None and response_map.size:
        response_n = response_map.astype(np.float32)
        mx = float(np.max(response_n))
        if mx > 1e-8:
            response_n = response_n / mx
        grid_response_score = float(np.mean(response_n))
    return {
        "grid_hypothesis_present": True,
        "dominant_fx": float(hypothesis.fx),
        "dominant_fy": float(hypothesis.fy),
        "dominant_wavelength_x": hypothesis.wavelength_x,
        "dominant_wavelength_y": hypothesis.wavelength_y,
        "dominant_angle_deg": float(hypothesis.angle_deg),
        "grid_hypothesis_strength": float(hypothesis.strength),
        "grid_response_score": float(clamp01(grid_response_score / 0.20)),
        "paired_peak_count": int(hypothesis.source_peak_count),
    }    

def blend_heatmap_on_grayscale(image_gray: np.ndarray, response_map: np.ndarray, heat_strength: float = 0.42, ) -> Image.Image:
    """
    Create a soft red-yellow heat overlay from the grid response map on top of the
    grayscale source image.
    heat_strength:
        0.0 -> no heatmap
        1.0 -> very strong heatmap
    """
    base_u8 = normalize_to_u8(image_gray)
    resp_u8 = normalize_to_u8(response_map)
    h, w = base_u8.shape
    out = np.stack([base_u8, base_u8, base_u8], axis=-1).astype(np.float32)
    # Normalize response to [0,1]
    resp = resp_u8.astype(np.float32) / 255.0
    # Soft gamma so weaker structure remains visible
    if presentation_mode:
        resp = np.power(resp, 0.35)
        heat_strength = 0.85
        # red = strong, yellow = medium, orange = weak 
        heat_r = 255 * resp
        heat_g = 255 * np.sqrt(resp)
        heat_b = 80 * resp
    else:
        resp = np.power(resp, 0.55)
        # Simple warm heatmap: low  -> transparent, mid  -> orange, high -> red/yellow
        heat_r = 255.0 * np.clip(resp * 1.15, 0.0, 1.0)
        heat_g = 255.0 * np.clip(resp * 0.72, 0.0, 1.0)
        heat_b = 255.0 * np.clip(resp * 0.18, 0.0, 1.0)
    heat = np.stack([heat_r, heat_g, heat_b], axis=-1)
    alpha = (resp * heat_strength)[..., None]
    out = out * (1.0 - alpha) + heat * alpha
    out = np.clip(out, 0, 255).astype(np.uint8)
    return Image.fromarray(out, mode="RGB")

def select_top_grid_hypotheses(peaks: List[PeakPoint], h: int, w: int, max_hypotheses: int = 3, min_relative_strength: float = 0.72,) -> List[GridHypothesis]:
    """
    Select the strongest approximately symmetric FFT peak pairs and convert them
    into a small set of grid hypotheses.
    max_hypotheses:
        hard cap on returned hypotheses
    min_relative_strength:
        keep only pairs whose strength is at least this fraction of the strongest pair
    """
    if not peaks:
        return []
    pairs = pair_symmetric_peaks(peaks, h=h, w=w, tol_px=3.0)
    if not pairs:
        return []
    cy = h / 2.0
    cx = w / 2.0
    pair_records: List[Tuple[float, GridHypothesis]] = []
    for p, q in pairs:
        strength = 0.5 * (float(p.value) + float(q.value))
        dy = float(p.y - cy)
        dx = float(p.x - cx)
        fx = abs(dx) / float(w)
        fy = abs(dy) / float(h)
        wavelength_x = (1.0 / fx) if fx > 1e-8 else None
        wavelength_y = (1.0 / fy) if fy > 1e-8 else None
        angle_deg = float(np.degrees(np.arctan2(dy, dx)))
        hyp = GridHypothesis(
            fx=float(fx),
            fy=float(fy),
            wavelength_x=float(wavelength_x) if wavelength_x is not None else None,
            wavelength_y=float(wavelength_y) if wavelength_y is not None else None,
            angle_deg=angle_deg,
            strength=float(strength),
            source_peak_count=len(pairs),
        )
        pair_records.append((strength, hyp))
    if not pair_records:
        return []

    pair_records.sort(key=lambda t: t[0], reverse=True)
    strongest = pair_records[0][0]
    out: List[GridHypothesis] = []
    used_signatures: set[tuple[int, int]] = set()
    for strength, hyp in pair_records:
        if len(out) >= max_hypotheses:
            break
        if strongest > 1e-8 and (strength / strongest) < min_relative_strength:
            continue
        # Avoid near-duplicate hypotheses with almost identical wavelength families.
        sig = (
            int(round((hyp.wavelength_x or 0.0) / 4.0)),
            int(round((hyp.wavelength_y or 0.0) / 4.0)),
        )
        if sig in used_signatures:
            continue
        used_signatures.add(sig)
        out.append(hyp)
    return out

def build_multi_grid_response(image_gray: np.ndarray, hypotheses: List[GridHypothesis], ) -> np.ndarray:
    """
    Combine several grid hypotheses into a single response map.
    Stronger hypotheses contribute more, but no single hypothesis should dominate completely.
    """
    if not hypotheses:
        return np.zeros_like(image_gray, dtype=np.float32)
    responses = []
    weights = []
    for hyp in hypotheses:
        resp = build_spatial_grid_response(image_gray=image_gray, hypothesis=hyp)
        responses.append(resp.astype(np.float32))
        weight = max(1e-6, float(hyp.strength))
        if presentation_mode:
            weight = weight ** 1.3
        weights.append(weight)
    weights_arr = np.asarray(weights, dtype=np.float32)
    weights_arr /= np.sum(weights_arr)
    stacked = np.stack(responses, axis=0)  # [k, h, w]
    combined = np.tensordot(weights_arr, stacked, axes=(0, 0))
    return combined.astype(np.float32)

def summarize_multi_grid_hypothesis(hypotheses: List[GridHypothesis], response_map: np.ndarray | None, ) -> Dict[str, Any]:
    if not hypotheses:
        return {
            "multi_grid_hypothesis_present": False,
            "multi_grid_count": 0,
            "multi_grid_response_score": 0.0,
            "multi_grid_combined_strength": 0.0,
        }
    response_score = 0.0
    if response_map is not None and response_map.size:
        response_n = response_map.astype(np.float32)
        mx = float(np.max(response_n))
        if mx > 1e-8:
            response_n = response_n / mx
        response_score = float(np.mean(response_n))
    combined_strength = float(sum(h.strength for h in hypotheses))
    return {
        "multi_grid_hypothesis_present": True,
        "multi_grid_count": int(len(hypotheses)),
        "multi_grid_response_score": float(clamp01(response_score / 0.20)),
        "multi_grid_combined_strength": float(combined_strength),
    }

# ============================================================
# public API
# ============================================================

def run_fft_analysis(
    image_path: str | Path,
    out_dir: str | Path,
    max_dim: int = DEFAULT_MAX_DIM,
    apply_window: bool = True,
    peak_percentile: float = DEFAULT_PEAK_PERCENTILE,
    center_exclusion_ratio: float = DEFAULT_CENTER_EXCLUSION_RATIO,
    edge_exclusion_ratio: float = DEFAULT_EDGE_EXCLUSION_RATIO,
    presentation_mode_override: bool | None = None,
) -> Dict[str, Any]:
    """
    Run frequency-domain analysis for SignalLens.
    Returns a JSON-serializable dict and writes:
      - fft_results.json
      - *_fft_spectrum.png
      - *_fft_radial_profile.png
      - *_fft_peakmap.png
    """
    # override presentation mode if specified, otherwise use global default
    pmode = presentation_mode if presentation_mode_override is None else presentation_mode_override
    
    image_path = Path(image_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    image_gray = load_grayscale_image(image_path, max_dim=max_dim)
    original_h, original_w = image_gray.shape

    work = image_gray.copy()
    if apply_window:
        work = apply_hann_window(work)

    spectrum_shifted = compute_fft_log_magnitude(work)
    spectrum_norm_u8 = normalize_to_u8(spectrum_shifted)
    radial_profile = compute_radial_profile(spectrum_shifted)
    radial_features = compute_radial_features(radial_profile)
    peaks, peak_mask = detect_offcenter_peaks(
        spectrum=spectrum_shifted,
        peak_percentile=peak_percentile,
        center_exclusion_ratio=center_exclusion_ratio,
        edge_exclusion_ratio=edge_exclusion_ratio,
    )
    peak_features = compute_peak_features(
        peaks=peaks,
        shape=spectrum_shifted.shape,
    )
    anisotropy_features = compute_anisotropy_features(spectrum_shifted)
    grid_hypothesis = select_dominant_grid_hypothesis(peaks=peaks, h=spectrum_shifted.shape[0], w=spectrum_shifted.shape[1],)
    grid_response = None
    grid_features = summarize_grid_hypothesis(None, None)
    fft_grid_overlay_path = out_dir / f"{image_path.stem}_fft_grid_overlay.png"
    fft_grid_response_path = out_dir / f"{image_path.stem}_fft_grid_response.png"
    if grid_hypothesis is not None:
        grid_response = build_spatial_grid_response(
            image_gray=image_gray,
            hypothesis=grid_hypothesis,
        )
        if pmode:
            grid_response = gaussian_blur_separable(grid_response, sigma=2.5)   # creates continuous bands instead of noise dots            
        grid_features = summarize_grid_hypothesis(
            hypothesis=grid_hypothesis,
            response_map=grid_response,
        )
        save_grid_response_image(grid_response, fft_grid_response_path)
        save_grid_overlay_image(image_gray=image_gray, hypothesis=grid_hypothesis, response_map=grid_response, out_path=fft_grid_overlay_path,)
        #print(f"[DEBUG]Grid hypothesis found: {grid_hypothesis}, grid_response and grid_overlay images saved.")
    else:
        #print(f"[DEBUG]No grid hypothesis found.")
        grid_features = summarize_grid_hypothesis(None, None)
        fft_grid_overlay_path = None
        fft_grid_response_path = None    
        
    top_grid_hypotheses = select_top_grid_hypotheses(
        peaks=peaks,
        h=spectrum_shifted.shape[0],
        w=spectrum_shifted.shape[1],
        max_hypotheses=3,
        min_relative_strength=0.72,
    )
    multi_grid_response = None
    multi_grid_features = summarize_multi_grid_hypothesis([], None)
    fft_multi_grid_response_path = out_dir / f"{image_path.stem}_fft_multi_grid_response.png"
    fft_multi_grid_overlay_path = out_dir / f"{image_path.stem}_fft_multi_grid_overlay.png"
    if top_grid_hypotheses:
        multi_grid_response = build_multi_grid_response(image_gray=image_gray, hypotheses=top_grid_hypotheses,)
        if pmode:
            multi_grid_response = gaussian_blur_separable(multi_grid_response, sigma=2.5)
        multi_grid_features = summarize_multi_grid_hypothesis(hypotheses=top_grid_hypotheses, response_map=multi_grid_response,)
        save_grid_response_image(multi_grid_response, fft_multi_grid_response_path)
        # Reuse the first / strongest hypothesis for spacing guidance in the line layer,
        # but drive visibility from the combined response map.
        save_grid_overlay_image(
            image_gray=image_gray,
            hypothesis=top_grid_hypotheses[0],
            response_map=multi_grid_response,
            out_path=fft_multi_grid_overlay_path,
        )
    else:
        fft_multi_grid_response_path = None
        fft_multi_grid_overlay_path = None        
              
    fft_anomaly_score = combine_fft_scores(
        radial_features=radial_features,
        peak_features=peak_features,
        anisotropy_features=anisotropy_features,
    )
    effective_grid_response_score = max(
        float(grid_features["grid_response_score"]),
        float(multi_grid_features["multi_grid_response_score"]),
    )
    frequency_pattern, frequency_note = interpret_fft_pattern(
        fft_anomaly_score=fft_anomaly_score,
        radial_features=radial_features,
        peak_features=peak_features,
        anisotropy_features=anisotropy_features,
        grid_response_score=effective_grid_response_score,
    )
    stem = image_path.stem
    spectrum_path = out_dir / f"{stem}_fft_spectrum.png"
    radial_plot_path = out_dir / f"{stem}_fft_radial_profile.png"
    peakmap_path = out_dir / f"{stem}_fft_peakmap.png"
    json_path = out_dir / "fft_results.json"
    save_spectrum_image(spectrum_norm_u8, spectrum_path)
    save_radial_profile_plot(
        radial_profile=radial_profile,
        radial_features=radial_features,
        out_path=radial_plot_path,
    )
    save_peakmap_image(
        base_spectrum_u8=spectrum_norm_u8,
        peaks=peaks,
        out_path=peakmap_path,
    )
    result = {
        "fft": {
            "input_image": str(image_path),
            "analysis_width": int(original_w),
            "analysis_height": int(original_h),
            "apply_window": bool(apply_window),
            "fft_anomaly_score": round(float(fft_anomaly_score), 4),
            "radial_profile_score": round(float(radial_features["radial_profile_score"]), 4),
            "midband_excess_score": round(float(radial_features["midband_excess_score"]), 4),
            "ring_irregularity_score": round(float(radial_features["ring_irregularity_score"]), 4),
            "peak_periodicity_score": round(float(peak_features["peak_periodicity_score"]), 4),
            "peak_symmetry_score": round(float(peak_features["peak_symmetry_score"]), 4),
            "peak_count": int(peak_features["peak_count"]),
            "anisotropy_score": round(float(anisotropy_features["anisotropy_score"]), 4),
            "axis_bias_score": round(float(anisotropy_features["axis_bias_score"]), 4),
            "diagonal_bias_score": round(float(anisotropy_features["diagonal_bias_score"]), 4),
            "frequency_pattern": frequency_pattern,
            "frequency_note": frequency_note,
            "grid_hypothesis_present": bool(grid_features["grid_hypothesis_present"]),
            "dominant_fx": float(grid_features["dominant_fx"]),
            "dominant_fy": float(grid_features["dominant_fy"]),
            "dominant_wavelength_x": grid_features["dominant_wavelength_x"],
            "dominant_wavelength_y": grid_features["dominant_wavelength_y"],
            "dominant_angle_deg": grid_features["dominant_angle_deg"],
            "grid_hypothesis_strength": float(grid_features["grid_hypothesis_strength"]),
            "grid_response_score": float(grid_features["grid_response_score"]),
            "paired_peak_count": int(grid_features["paired_peak_count"]),          
            "multi_grid_hypothesis_present": bool(multi_grid_features["multi_grid_hypothesis_present"]),
            "multi_grid_count": int(multi_grid_features["multi_grid_count"]),
            "multi_grid_response_score": float(multi_grid_features["multi_grid_response_score"]),
            "multi_grid_combined_strength": float(multi_grid_features["multi_grid_combined_strength"]),            
            "artifacts": {
                "fft_spectrum_image": str(spectrum_path),
                "fft_radial_profile_image": str(radial_plot_path),
                "fft_peakmap_image": str(peakmap_path),
                "fft_grid_overlay_path": str(fft_grid_overlay_path) if fft_grid_overlay_path is not None else None,
                "fft_grid_response_path": str(fft_grid_response_path) if fft_grid_response_path is not None else None,  
                "fft_multi_grid_response_path": str(fft_multi_grid_response_path) if fft_multi_grid_response_path is not None else None,
                "fft_multi_grid_overlay_path": str(fft_multi_grid_overlay_path) if fft_multi_grid_overlay_path is not None else None,                              
            },
            "peaks": [
                {
                    "x": int(p.x),
                    "y": int(p.y),
                    "value": round(float(p.value), 4),
                    "radius": round(float(p.radius), 4),
                    "angle_deg": round(float(p.angle_deg), 2),
                }
                for p in peaks[:100]
            ],
        }
    }
    save_json(result, json_path)
    return result

# ============================================================
# image loading and preprocessing
# ============================================================

def load_grayscale_image(image_path: str | Path, max_dim: int = DEFAULT_MAX_DIM) -> np.ndarray:
    """
    Load image, convert to grayscale float32 [0,1], resize conservatively if needed.
    """
    with Image.open(image_path) as im:
        im = im.convert("L")

        w, h = im.size
        scale = min(1.0, max_dim / max(w, h))
        if scale < 1.0:
            new_size = (max(1, int(round(w * scale))), max(1, int(round(h * scale))))
            im = im.resize(new_size, Image.Resampling.LANCZOS)

        arr = np.asarray(im, dtype=np.float32) / 255.0
        return arr


def apply_hann_window(image_gray: np.ndarray) -> np.ndarray:
    """
    Apply a separable Hann window to reduce border-induced FFT artifacts.
    """
    h, w = image_gray.shape
    wy = np.hanning(h).astype(np.float32)
    wx = np.hanning(w).astype(np.float32)
    window = np.outer(wy, wx)
    return image_gray * window


# ============================================================
# FFT computation
# ============================================================

def compute_fft_log_magnitude(image_gray: np.ndarray) -> np.ndarray:
    """
    Compute centered log-magnitude FFT spectrum.
    """
    fft2 = np.fft.fft2(image_gray)
    fft_shifted = np.fft.fftshift(fft2)
    magnitude = np.abs(fft_shifted)
    log_magnitude = np.log1p(magnitude)
    return log_magnitude.astype(np.float32)


def normalize_to_u8(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype(np.float32)
    lo = float(arr.min())
    hi = float(arr.max())
    if hi <= lo:
        return np.zeros_like(arr, dtype=np.uint8)
    out = (arr - lo) / (hi - lo)
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    return out


# ============================================================
# radial profile
# ============================================================

def compute_radial_profile(spectrum: np.ndarray) -> np.ndarray:
    """
    Mean energy as a function of radius from the spectrum center.
    """
    h, w = spectrum.shape
    cy = (h - 1) / 2.0
    cx = (w - 1) / 2.0

    y, x = np.indices((h, w))
    r = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
    r_int = np.floor(r).astype(np.int32)

    max_r = int(r_int.max())
    sums = np.bincount(r_int.ravel(), weights=spectrum.ravel(), minlength=max_r + 1)
    counts = np.bincount(r_int.ravel(), minlength=max_r + 1)

    with np.errstate(divide="ignore", invalid="ignore"):
        profile = sums / np.maximum(counts, 1)

    return profile.astype(np.float32)


def moving_average_1d(x: np.ndarray, window: int = 9) -> np.ndarray:
    if window <= 1:
        return x.copy()
    window = min(window, len(x))
    kernel = np.ones(window, dtype=np.float32) / float(window)
    padded = np.pad(x, (window // 2, window - 1 - window // 2), mode="edge")
    smooth = np.convolve(padded, kernel, mode="valid")
    return smooth.astype(np.float32)


def compute_radial_features(profile: np.ndarray) -> Dict[str, float]:
    """
    Conservative interpretable radial-profile features.
    """
    if len(profile) < 16:
        return {
            "radial_profile_score": 0.0,
            "midband_excess_score": 0.0,
            "ring_irregularity_score": 0.0,
        }

    n = len(profile)
    # ignore the first few bins because DC/near-DC dominates strongly
    start = max(2, int(0.02 * n))
    end = max(start + 1, int(0.95 * n))
    p = profile[start:end]

    if len(p) < 8:
        return {
            "radial_profile_score": 0.0,
            "midband_excess_score": 0.0,
            "ring_irregularity_score": 0.0,
        }

    smooth = moving_average_1d(p, window=max(5, int(0.03 * len(p)) | 1))
    residual = p - smooth

    ring_irregularity = robust_ratio(np.std(residual), np.mean(smooth))
    ring_irregularity_score = clamp01(ring_irregularity / 0.12)

    # compare midband with neighboring bands
    third = len(p) // 3
    if third < 2:
        midband_excess = 0.0
    else:
        low_band = float(np.mean(p[:third]))
        mid_band = float(np.mean(p[third:2 * third]))
        high_band = float(np.mean(p[2 * third:])) if len(p[2 * third:]) > 0 else mid_band
        neighbor_mean = (low_band + high_band) / 2.0 if (low_band + high_band) > 0 else 0.0
        midband_excess = max(0.0, (mid_band - neighbor_mean) / (neighbor_mean + 1e-8))

    midband_excess_score = clamp01(midband_excess / 0.25)

    # overall irregularity of the radial decay
    radial_profile_score = clamp01(
        0.55 * ring_irregularity_score +
        0.45 * midband_excess_score
    )

    return {
        "radial_profile_score": float(radial_profile_score),
        "midband_excess_score": float(midband_excess_score),
        "ring_irregularity_score": float(ring_irregularity_score),
    }


# ============================================================
# peak detection
# ============================================================

def detect_offcenter_peaks(
    spectrum: np.ndarray,
    peak_percentile: float = DEFAULT_PEAK_PERCENTILE,
    center_exclusion_ratio: float = DEFAULT_CENTER_EXCLUSION_RATIO,
    edge_exclusion_ratio: float = DEFAULT_EDGE_EXCLUSION_RATIO,
) -> Tuple[List[PeakPoint], np.ndarray]:
    """
    Detect bright off-center spectral peaks.
    Conservative implementation: percentile threshold + local maximum check.
    """
    h, w = spectrum.shape
    cy = (h - 1) / 2.0
    cx = (w - 1) / 2.0
    min_dim = min(h, w)

    y, x = np.indices((h, w))
    dy = y - cy
    dx = x - cx
    r = np.sqrt(dx**2 + dy**2)

    center_excl = center_exclusion_ratio * min_dim
    edge_margin = edge_exclusion_ratio * min_dim

    valid_mask = np.ones_like(spectrum, dtype=bool)
    valid_mask &= r >= center_excl
    valid_mask &= x >= edge_margin
    valid_mask &= x < (w - edge_margin)
    valid_mask &= y >= edge_margin
    valid_mask &= y < (h - edge_margin)

    vals = spectrum[valid_mask]
    if vals.size == 0:
        return [], np.zeros_like(spectrum, dtype=np.uint8)

    threshold = np.percentile(vals, peak_percentile)

    peaks: List[PeakPoint] = []
    peak_mask = np.zeros_like(spectrum, dtype=np.uint8)

    # local-max test on 3x3 neighborhood
    for yy in range(1, h - 1):
        for xx in range(1, w - 1):
            if not valid_mask[yy, xx]:
                continue

            v = spectrum[yy, xx]
            if v < threshold:
                continue

            neighborhood = spectrum[yy - 1:yy + 2, xx - 1:xx + 2]
            if v < np.max(neighborhood):
                continue

            radius = math.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
            angle_deg = math.degrees(math.atan2(yy - cy, xx - cx))

            peaks.append(
                PeakPoint(
                    y=int(yy),
                    x=int(xx),
                    value=float(v),
                    radius=float(radius),
                    angle_deg=float(angle_deg),
                )
            )
            peak_mask[yy, xx] = 255

    peaks.sort(key=lambda p: p.value, reverse=True)

    # cap very large lists to keep behavior stable
    peaks = peaks[:200]
    return peaks, peak_mask


def compute_peak_features(peaks: List[PeakPoint], shape: Tuple[int, int]) -> Dict[str, float]:
    """
    Interpret periodic-peak structure conservatively.
    """
    h, w = shape
    cy = (h - 1) / 2.0
    cx = (w - 1) / 2.0
    min_dim = min(h, w)

    peak_count = len(peaks)
    if peak_count == 0:
        return {
            "peak_periodicity_score": 0.0,
            "peak_symmetry_score": 0.0,
            "peak_count": 0,
        }

    peak_count_score = clamp01(peak_count / 14.0)

    # symmetry: for each peak, look for an opposite point around center
    coords = np.array([(p.y, p.x) for p in peaks], dtype=np.float32)
    symmetry_hits = 0
    tolerance = max(3.0, min_dim * 0.01)

    for p in peaks:
        sy = 2.0 * cy - p.y
        sx = 2.0 * cx - p.x

        if coords.size == 0:
            continue

        d = np.sqrt((coords[:, 0] - sy) ** 2 + (coords[:, 1] - sx) ** 2)
        if np.min(d) <= tolerance:
            symmetry_hits += 1

    peak_symmetry_ratio = symmetry_hits / max(peak_count, 1)
    peak_symmetry_score = clamp01(peak_symmetry_ratio)

    peak_periodicity_score = clamp01(
        0.55 * peak_count_score +
        0.45 * peak_symmetry_score
    )

    return {
        "peak_periodicity_score": float(peak_periodicity_score),
        "peak_symmetry_score": float(peak_symmetry_score),
        "peak_count": int(peak_count),
    }


# ============================================================
# anisotropy
# ============================================================

def compute_anisotropy_features(spectrum: np.ndarray) -> Dict[str, float]:
    """
    Measure whether energy is unusually concentrated along axes or diagonals.
    """
    h, w = spectrum.shape
    cy = (h - 1) / 2.0
    cx = (w - 1) / 2.0
    min_dim = min(h, w)

    y, x = np.indices((h, w))
    dy = y - cy
    dx = x - cx
    r = np.sqrt(dx**2 + dy**2)

    # exclude very center because it dominates
    center_excl = 0.08 * min_dim
    valid = r >= center_excl

    # angular bands
    angle = np.degrees(np.arctan2(dy, dx))
    angle = np.abs(((angle + 180.0) % 180.0) - 90.0)  # folded

    # horizontal / vertical axes
    axis_band_deg = 7.5
    axis_mask = valid & ((np.abs(dy) <= np.tan(np.radians(axis_band_deg)) * np.abs(dx)) |
                         (np.abs(dx) <= np.tan(np.radians(axis_band_deg)) * np.abs(dy)))

    # diagonals around ±45°
    diag_angle = np.degrees(np.abs(np.arctan2(np.abs(dy), np.abs(dx) + 1e-8)))
    diag_mask = valid & (np.abs(diag_angle - 45.0) <= axis_band_deg)

    base_mean = float(np.mean(spectrum[valid])) if np.any(valid) else 0.0
    axis_mean = float(np.mean(spectrum[axis_mask])) if np.any(axis_mask) else base_mean
    diag_mean = float(np.mean(spectrum[diag_mask])) if np.any(diag_mask) else base_mean

    axis_bias = max(0.0, (axis_mean - base_mean) / (base_mean + 1e-8))
    diagonal_bias = max(0.0, (diag_mean - base_mean) / (base_mean + 1e-8))

    axis_bias_score = clamp01(axis_bias / 0.18)
    diagonal_bias_score = clamp01(diagonal_bias / 0.18)
    anisotropy_score = clamp01(max(axis_bias_score, diagonal_bias_score))

    return {
        "anisotropy_score": float(anisotropy_score),
        "axis_bias_score": float(axis_bias_score),
        "diagonal_bias_score": float(diagonal_bias_score),
    }


# ============================================================
# scoring and interpretation
# ============================================================

def combine_fft_scores(
    radial_features: Dict[str, float],
    peak_features: Dict[str, float],
    anisotropy_features: Dict[str, float],
) -> float:
    """
    Weighted conservative combination.
    """
    score = (
        0.35 * radial_features["radial_profile_score"] +
        0.40 * peak_features["peak_periodicity_score"] +
        0.25 * anisotropy_features["anisotropy_score"]
    )
    return clamp01(score)

def interpret_fft_pattern(
    fft_anomaly_score: float,
    radial_features: Dict[str, float],
    peak_features: Dict[str, float],
    anisotropy_features: Dict[str, float],
    grid_response_score: float = 0.0,
) -> Tuple[str, str]:
    peak_score = peak_features["peak_periodicity_score"]
    peak_count = peak_features["peak_count"]
    symmetry = peak_features["peak_symmetry_score"]
    radial_score = radial_features["radial_profile_score"]
    ring_score = radial_features["ring_irregularity_score"]
    anisotropy = anisotropy_features["anisotropy_score"]
    axis_bias = anisotropy_features["axis_bias_score"]

    if fft_anomaly_score < 0.20:
        return (
            "frequency_inconclusive",
            "Frequency-domain analysis did not reveal a strong structured spectral anomaly beyond what can arise from normal scene content, compression, resizing, or routine processing."
        )

    if peak_score >= 0.82 and symmetry >= 0.62 and peak_count >= 6 and axis_bias >= 0.62 and grid_response_score >= 0.20:   
        return (
            "possible_decoder_grid_signature",
            "Frequency-domain analysis reveals repeated off-center spectral peaks with partial symmetry and axis-aligned structure, and a reconstructable spatial grid response. This indicates structured periodicity, but such patterns can also arise from genuine repeated scene content, camera pipeline effects, or regular image geometry."
            )
    if peak_score >= 0.65 and symmetry >= 0.55 and peak_count >= 6 and axis_bias >= 0.50:          
        return (
            "structured_frequency_anomaly",
            "Frequency-domain analysis reveals repeated off-center spectral peaks and structured spectral organization, consistent with artificial raster regularity or generative/decoder-related frequency artifacts."
        )

    if radial_score >= 0.50 and ring_score >= 0.45:
        return (
            "mild_structured_periodicity",
            "Frequency-domain analysis reveals an irregular radial energy distribution with ring-like midband structure, consistent with mild structured periodicity or non-photographic processing artifacts, though not strongly diagnostic on its own."
        )

    if anisotropy >= 0.55:
        return (
            "directional_frequency_bias",
            "Frequency-domain analysis reveals elevated directional energy concentration relative to the surrounding spectrum, suggesting structured processing bias or raster organization, though the result remains only moderately specific."
        )

    return (
        "frequency_inconclusive",
        "Frequency-domain analysis reveals only mild or ambiguous spectral structure and does not by itself support a strong frequency-domain conclusion."
    )


# ============================================================
# artifact rendering
# ============================================================

def save_spectrum_image(spectrum_u8: np.ndarray, out_path: str | Path) -> None:
    Image.fromarray(spectrum_u8, mode="L").save(out_path)


def save_peakmap_image(
    base_spectrum_u8: np.ndarray,
    peaks: List[PeakPoint],
    out_path: str | Path,
) -> None:
    rgb = Image.fromarray(base_spectrum_u8, mode="L").convert("RGB")
    draw = ImageDraw.Draw(rgb)

    for p in peaks:
        r = 4
        draw.ellipse((p.x - r, p.y - r, p.x + r, p.y + r), outline=(255, 64, 64), width = 2 if presentation_mode else 1)

    # mark center
    h, w = base_spectrum_u8.shape
    cx = w // 2
    cy = h // 2
    draw.line((cx - 6, cy, cx + 6, cy), fill=(64, 255, 64), width = 2 if presentation_mode else 1)
    draw.line((cx, cy - 6, cx, cy + 6), fill=(64, 255, 64), width = 2 if presentation_mode else 1)

    rgb.save(out_path)


def save_radial_profile_plot(
    radial_profile: np.ndarray,
    radial_features: Dict[str, float],
    out_path: str | Path,
) -> None:
    x = np.arange(len(radial_profile))
    smooth = moving_average_1d(radial_profile, window=max(5, int(0.03 * len(radial_profile)) | 1))

    # Create a stateless Figure (bypasses pyplot's global state)
    fig = Figure(figsize=(8, 4.5), dpi=140)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)

    ax.plot(x, radial_profile, linewidth=1.2, label="Radial energy")
    ax.plot(x, smooth, linewidth=1.2, label="Smoothed profile")
    
    ax.set_title(
        "FFT Radial Energy Profile\n"
        f"radial={radial_features['radial_profile_score']:.2f}, "
        f"midband={radial_features['midband_excess_score']:.2f}, "
        f"ring={radial_features['ring_irregularity_score']:.2f}"
    )
    ax.set_xlabel("Radius bin")
    ax.set_ylabel("Mean log-magnitude")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    # Save directly via the canvas. No plt.close() needed!
    canvas.print_figure(out_path)
    
# ============================================================
# helpers
# ============================================================

def clamp01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def robust_ratio(a: float, b: float) -> float:
    return float(a / (b + 1e-8))


def save_json(data: Dict[str, Any], out_path: str | Path) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================
# CLI test
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SignalLens FFT / Frequency Domain Analysis")
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("--out-dir", required=True, help="Output folder")
    parser.add_argument("--max-dim", type=int, default=DEFAULT_MAX_DIM)
    parser.add_argument("--no-window", action="store_true", help="Disable Hann windowing")
    parser.add_argument("--peak-percentile", type=float, default=DEFAULT_PEAK_PERCENTILE)

    args = parser.parse_args()

    result = run_fft_analysis(
        image_path=args.image_path,
        out_dir=args.out_dir,
        max_dim=args.max_dim,
        apply_window=not args.no_window,
        peak_percentile=args.peak_percentile,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))