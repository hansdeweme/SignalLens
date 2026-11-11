#vf_person_subject_mask.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
# Person-aware subject segmentation for region-aware forensic analysis.
# Preferred backend: MediaPipe Tasks ImageSegmenter using selfie_segmenter.tflite.
# Fallbacks: OpenCV HOG person detector, then conservative central-subject mask.
# 
# 
from __future__ import annotations
from investigation_storage import artifact_stem
from pathlib import Path
from typing import Any, Dict, Tuple
import cv2
import json
import numpy as np
import sys
import contextlib
import os
from importlib.metadata import version, PackageNotFoundError
# local imports
from app_paths import app_dir, resource_path
from mask_contract import normalize_region_masks, person_mask_diagnostics

@contextlib.contextmanager
def suppress_native_stderr():
    """
    Suppress native/C++ stderr output, including some MediaPipe/TFLite warnings.
    In PyInstaller --windowed mode, sys.stderr may be None. In that case,
    do nothing instead of failing before MediaPipe can run.
    """
    if sys.stderr is None or not hasattr(sys.stderr, "fileno"):
        yield
        return
    try:
        stderr_fd = sys.stderr.fileno()
    except Exception:
        yield
        return
    try:
        saved_stderr_fd = os.dup(stderr_fd)
    except OSError:
        yield
        return
    try:
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), stderr_fd)
            yield
    finally:
        try:
            os.dup2(saved_stderr_fd, stderr_fd)
        finally:
            os.close(saved_stderr_fd)

def _write_person_mask_debug(
    output_dir: Path,
    stem: str,
    payload: dict[str, Any],
) -> None:
    try:
        debug_path = output_dir / f"{stem}_person_mask_debug.json"
        debug_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        # Never let debugging break analysis.
        pass


def _detect_person_mask_mediapipe_tasks(
    image_bgr: np.ndarray,
    model_path: str | Path = "selfie_segmenter.tflite",
    threshold: float = 0.50,
) -> tuple[np.ndarray | None, float]:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    model_path = Path(model_path)
    if not model_path.is_absolute():
        model_path = resource_path(model_path)    
    if not model_path.exists():
        raise FileNotFoundError(
            f"MediaPipe segmenter model not found: {model_path}. "
        )
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    base_options = python.BaseOptions(model_asset_path=str(model_path))
    options = vision.ImageSegmenterOptions(
        base_options=base_options,
    )
    with vision.ImageSegmenter.create_from_options(options) as segmenter:
        result = segmenter.segment(mp_image)
    if getattr(result, "confidence_masks", None):
        mask = result.confidence_masks[0].numpy_view()
    elif getattr(result, "category_mask", None) is not None:
        mask = result.category_mask.numpy_view().astype(np.float32)
    else:
        return None, 0.0
    mask = _ensure_2d_mask(mask).astype(np.float32)
    binary = _refine_mediapipe_mask_from_confidence(
        conf_mask=mask,
        threshold=threshold,
        core_threshold=0.70,
    )    
    confidence = float(np.mean(mask))
    return binary, confidence

def _refine_mediapipe_mask_from_confidence(
    conf_mask: np.ndarray,
    threshold: float = 0.50,
    core_threshold: float = 0.70,
) -> np.ndarray:
    conf_mask = _ensure_2d_mask(conf_mask).astype(np.float32)
    base = (conf_mask > threshold).astype(np.uint8)
    core = (conf_mask > core_threshold).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        base,
        connectivity=8,
    )
    keep = np.zeros_like(base, dtype=np.uint8)
    core_labels = set(np.unique(labels[core > 0]).tolist())
    core_labels.discard(0)
    for label in core_labels:
        keep[labels == label] = 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    keep = cv2.morphologyEx(keep, cv2.MORPH_OPEN, kernel)
    return keep.astype(np.uint8)

def _ensure_2d_mask(mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask)
    if mask.ndim == 3:
        if mask.shape[2] == 1:
            mask = mask[:, :, 0]
        else:
            mask = mask[:, :, 0]
    if mask.ndim != 2:
        raise ValueError(f"Expected 2D mask, got shape {mask.shape}")
    return mask

# for non mediapipe masks
def _clean_mask(mask: np.ndarray) -> np.ndarray:
    mask_u8 = (mask > 0).astype(np.uint8)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask_u8 = cv2.morphologyEx(mask_u8, cv2.MORPH_CLOSE, kernel_close)
    mask_u8 = cv2.morphologyEx(mask_u8, cv2.MORPH_OPEN, kernel_open)
    largest, _, _ = _largest_component_stats(mask_u8)
    return largest.astype(np.uint8)

def _safe_area_ratio(mask: np.ndarray) -> float:
    return float(np.count_nonzero(mask)) / max(float(mask.size), 1.0)

def _largest_component_stats(mask: np.ndarray) -> tuple[np.ndarray, int, float]:
    mask_u8 = (mask > 0).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
    if num_labels <= 1:
        return mask_u8, 0, 0.0
    best_label = 1
    best_area = 0
    component_count = 0
    for label in range(1, num_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area <= 0:
            continue
        component_count += 1
        if area > best_area:
            best_area = area
            best_label = label
    largest = (labels == best_label).astype(np.uint8)
    total_area = max(int(np.count_nonzero(mask_u8)), 1)
    largest_component_ratio = float(best_area) / float(total_area)
    return largest, component_count, largest_component_ratio

def _make_bbox_mask(shape_hw: Tuple[int, int], bbox: Tuple[int, int, int, int]) -> np.ndarray:
    h, w = shape_hw
    x, y, bw, bh = bbox
    x0 = max(0, int(x))
    y0 = max(0, int(y))
    x1 = min(w, int(x + bw))
    y1 = min(h, int(y + bh))
    mask = np.zeros((h, w), dtype=np.uint8)
    if x1 > x0 and y1 > y0:
        mask[y0:y1, x0:x1] = 1
    return mask

def _detect_person_bbox_hog(image_bgr: np.ndarray) -> tuple[Tuple[int, int, int, int] | None, float]:
    """
    Lightweight first-pass person detector.
    This is deliberately conservative and replaceable. It returns the largest detected
    person-like bounding box plus a detector confidence proxy.
    """
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    rects, weights = hog.detectMultiScale(
        image_bgr,
        winStride=(8, 8),
        padding=(16, 16),
        scale=1.05,
    )
    if len(rects) == 0:
        return None, 0.0
    best_idx = int(np.argmax([w * h for x, y, w, h in rects]))
    bbox = tuple(int(v) for v in rects[best_idx])
    confidence = float(weights[best_idx]) if len(weights) > best_idx else 0.5
    return bbox, confidence

def _fallback_center_subject_mask(image_bgr: np.ndarray) -> np.ndarray:
    """
    Fallback mask used only when person detection fails.
    It deliberately returns a conservative central foreground region, not a final
    reliable person mask. QA should mark this as low reliability.
    """
    h, w = image_bgr.shape[:2]
    x0 = int(round(w * 0.20))
    x1 = int(round(w * 0.80))
    y0 = int(round(h * 0.08))
    y1 = int(round(h * 0.95))
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y0:y1, x0:x1] = 1
    return mask

def _quality_from_mask(
    mask: np.ndarray,
    person_detected: bool,
    detector_confidence: float,
) -> dict[str, Any]:
    area_ratio = _safe_area_ratio(mask)
    _, component_count, largest_component_ratio = _largest_component_stats(mask)
    if (
        person_detected
        and 0.08 <= area_ratio <= 0.85
        and largest_component_ratio >= 0.70
        and component_count <= 3
    ):
        reliability = "high"
        pattern = "person_subject_mask_generated"
    elif (
        person_detected
        and 0.03 <= area_ratio <= 0.90
        and largest_component_ratio >= 0.50
    ):
        reliability = "medium"
        pattern = "person_subject_mask_generated_low_confidence"
    else:
        reliability = "low"
        pattern = "person_subject_mask_unreliable"
    reasons = []
    if not person_detected:
        reasons.append("No detected person supports this mask.")
    if not 0.03 <= area_ratio <= 0.90:
        reasons.append(f"Foreground area ratio {area_ratio:.6f} is outside the existing usable range [0.03, 0.90].")
    if largest_component_ratio < 0.50:
        reasons.append(f"Largest-component coverage {largest_component_ratio:.6f} is below the existing 0.50 usable minimum.")
    if reliability == "medium":
        reasons.append("Usable with limitations: the existing high-quality area/component criteria were not all met.")
    return {
        "pattern": pattern,
        "person_detected": bool(person_detected),
        "detector_confidence": float(detector_confidence),
        "subject_area_ratio": float(area_ratio),
        "largest_component_ratio": float(largest_component_ratio),
        "component_count": int(component_count),
        "mask_reliability": reliability,
        "quality_reasons": reasons,
    }

def _save_mask(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), (mask > 0).astype(np.uint8) * 255)

def _save_overlay(image_bgr: np.ndarray, mask: np.ndarray, path: Path) -> None:
    mask = _ensure_2d_mask(mask).astype(np.uint8)
    if mask.shape != image_bgr.shape[:2]:
        mask = cv2.resize(
            mask,
            (image_bgr.shape[1], image_bgr.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )
    overlay = image_bgr.copy()
    color_layer = np.zeros_like(image_bgr)
    color_layer[:, :, 1] = 220
    blended = cv2.addWeighted(image_bgr, 0.55, color_layer, 0.45, 0.0)
    mask_3 = mask[:, :, None].astype(bool)
    overlay = np.where(mask_3, blended, overlay)
    contours, _ = cv2.findContours(
        mask.astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    cv2.drawContours(overlay, contours, -1, (80, 255, 120), 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), overlay)
    
def run_person_subject_mask_analysis(
    image_path: str | Path,
    output_dir: str | Path,
    backend: str = "mediapipe_tasks_image_segmenter",
    model_name: str = "selfie_segmenter.tflite",
    conf: float = 0.25,
    imgsz: int = 640,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError(f"Failed to load image: {image_path}")
    h, w = image_bgr.shape[:2]
    raw_mask: np.ndarray | None = None
    detector_confidence = 0.0
    person_count = 0
    person_detected = False
    detection_backend = "none"
    backend_error: str | None = None    
    backend_errors = []
# ------------------------------------------------------------
# Preferred backend: MediaPipe
# ------------------------------------------------------------
    try:
        with suppress_native_stderr():
            raw_mask, detector_confidence = _detect_person_mask_mediapipe_tasks(
                image_bgr=image_bgr,
                model_path=model_name,
                threshold=0.60,
            )
        if raw_mask is not None:
            person_detected = bool(np.any(raw_mask))
            person_count = int(person_detected)
            detection_backend = "mediapipe_tasks_image_segmenter"
    except Exception as e:
        backend_error = str(e)
        backend_errors.append({"backend": "mediapipe_tasks_image_segmenter", "error": str(e)})
        print(f"[PersonMask] MediaPipe Tasks failed, falling back to HOG: {e}")
    
    # ------------------------------------------------------------
    # Fallback backend: OpenCV HOG person detector
    # ------------------------------------------------------------
    if raw_mask is None:
        try:
            bbox, hog_confidence = _detect_person_bbox_hog(image_bgr)
        except Exception as exc:
            backend_errors.append({"backend": "opencv_hog", "error": str(exc)})
            bbox, hog_confidence = None, 0.0
        if bbox is not None:
            raw_mask = _make_bbox_mask((h, w), bbox)
            detector_confidence = float(hog_confidence)
            person_count = 1
            person_detected = True
            detection_backend = "opencv_hog"
    # ------------------------------------------------------------
    # Last-resort fallback: conservative central subject box
    # ------------------------------------------------------------
    if raw_mask is None:
        raw_mask = _fallback_center_subject_mask(image_bgr)
        detector_confidence = 0.0
        person_count = 0
        person_detected = False
        detection_backend = "fallback_center_subject"
    # ------------------------------------------------------------
    # Clean and validate mask
    # ------------------------------------------------------------
    if detection_backend.startswith("mediapipe"):
        mask = raw_mask.astype(np.uint8)
    else:
        mask = _clean_mask(raw_mask)
    quality = _quality_from_mask(
        mask=mask,
        person_detected=person_detected,
        detector_confidence=detector_confidence,
    )
    person_mask_reliability = quality["mask_reliability"]
    quality["person_instance_count"] = int(person_count)
    quality["backend_error"] = backend_error
    stem = artifact_stem(image_path)
    # debug 
    model_candidate = resource_path("selfie_segmenter.tflite")
    debug_info: dict[str, Any] = {
        "stage": "person_subject_mask",
        "image_path": str(image_path),
        "output_dir": str(output_dir),
        "frozen": bool(getattr(sys, "frozen", False)),
        "executable": str(sys.executable),
        "cwd": str(Path.cwd()),
        "app_dir": str(app_dir()),
        "_MEIPASS": str(getattr(sys, "_MEIPASS", "")),
        "selfie_segmenter_resource_path": str(model_candidate),
        "selfie_segmenter_resource_exists": bool(model_candidate.exists()),
    }
    
    mask_path = output_dir / f"{stem}_person_subject_mask.png"
    overlay_path = output_dir / f"{stem}_person_subject_mask_overlay.png"
    _save_mask(mask, mask_path)
    _save_overlay(image_bgr, mask, overlay_path)
    # write debug info
    debug_info.update({
        "detection_backend": detection_backend,
        "backend_error": backend_error,
        "person_detected": bool(person_detected),
        "person_count": int(person_count),
        "detector_confidence": float(detector_confidence),
        "mask_shape": list(mask.shape) if mask is not None else None,
        "mask_nonzero": int(np.count_nonzero(mask)) if mask is not None else 0,
        "mask_area_ratio": float(_safe_area_ratio(mask)) if mask is not None else 0.0,
        "quality": quality,
    })
    try:
        backend_version = version("mediapipe") if detection_backend == "mediapipe_tasks_image_segmenter" else cv2.__version__
    except PackageNotFoundError:
        backend_version = None
    payload = {
        "person_subject_mask": {
            "pattern": quality["pattern"],
            "status": (
                "ok"
                if quality["mask_reliability"] in {"high", "medium"}
                else "unreliable"
            ),
            "person_mask_reliability": person_mask_reliability,
            "backend": detection_backend,
            "requested_backend": backend,
            "backend_version": backend_version,
            "backend_errors": backend_errors,
            "confidence_kind": "mean foreground confidence, not a person-detection probability" if detection_backend == "mediapipe_tasks_image_segmenter" else "HOG score proxy or unavailable",
            "fallback_reason": backend_error or ("No MediaPipe person mask was produced." if detection_backend != "mediapipe_tasks_image_segmenter" else None),
            "model_name": model_name if detection_backend == "mediapipe_tasks_image_segmenter" else None,
            "mask_path": str(mask_path),
            "overlay_path": str(overlay_path),
            "quality": quality,
            "image_geometry": {
                "width": int(w),
                "height": int(h),
            },
        }
    }
    diagnostics = person_mask_diagnostics(payload)
    payload["person_subject_mask"].update({key: diagnostics[key] for key in (
        "mask_status", "mask_source", "mask_reliability", "person_specific", "fallback_used", "fallback_reason",
    )})
    payload["person_subject_mask"]["person_mask_reliability"] = diagnostics["person_mask_reliability"]
    if diagnostics["mask_status"] in {"approximate", "unavailable", "error"}:
        payload["person_subject_mask"]["status"] = diagnostics["mask_status"]
    debug_info.update(backend_version=backend_version, mask_status=diagnostics["mask_status"],
                      rejection_reasons=diagnostics["rejection_reasons"], backend_errors=backend_errors)
    _write_person_mask_debug(output_dir, stem, debug_info)
    return payload

def derive_region_masks_from_person_mask(person_mask_path: str | Path, image_path: str | Path, output_dir: str | Path, person_mask_reliability: str | None = None, mask_source: str = "mediapipe_tasks_image_segmenter", person_specific: bool = True,) -> dict:
    person_mask = cv2.imread(str(person_mask_path), cv2.IMREAD_GRAYSCALE)
    if person_mask is None:
        raise ValueError(f"Failed to load person mask: {person_mask_path}")
    subject = (person_mask > 0).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    dilated = cv2.dilate(subject, kernel, iterations=1)
    eroded = cv2.erode(subject, kernel, iterations=1)
    boundary = ((dilated > 0) & (eroded == 0)).astype(np.uint8)
    background = (subject == 0).astype(np.uint8)
    stem = artifact_stem(image_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    subject_path = out / f"{stem}_person_subject_region_mask.png"
    boundary_path = out / f"{stem}_person_boundary_band_mask.png"
    background_path = out / f"{stem}_person_background_mask.png"
    cv2.imwrite(str(subject_path), subject * 255)
    cv2.imwrite(str(boundary_path), boundary * 255)
    cv2.imwrite(str(background_path), background * 255)
    image_area = max(subject.size, 1)
    h, w = subject.shape
    payload = {
        "region_masks": {
            "shape": [int(h), int(w)],
            "height": int(h),
            "width": int(w),
            "source": "person_subject_mask",
            "person_mask_reliability": person_mask_reliability,
            "subject_mask_path": str(subject_path),
            "boundary_band_path": str(boundary_path),
            "background_mask_path": str(background_path),
            "subject_ratio": float(np.count_nonzero(subject) / image_area),
            "boundary_ratio": float(np.count_nonzero(boundary) / image_area),
            "background_ratio": float(np.count_nonzero(background) / image_area),
        }
    }
    return normalize_region_masks(
        payload, mask_source=mask_source, mask_reliability=person_mask_reliability or "low",
        mask_status=("reliable" if person_mask_reliability == "high" else "limited" if person_mask_reliability == "medium" else "unreliable") if person_specific else "approximate",
        person_specific=person_specific, fallback_used=not person_specific,
        fallback_reason="Bounding-box geometry is approximate." if not person_specific else None,
    )
