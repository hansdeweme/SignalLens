# mask_contract.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
"""Mask availability and geometry contracts; no forensic scoring or calibration."""

from enum import Enum
from pathlib import Path
import math
import cv2
import numpy as np


class MaskStatus(str, Enum):
    RELIABLE = "reliable"
    LIMITED = "limited"
    UNRELIABLE = "unreliable"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    APPROXIMATE = "approximate"

class StageUnavailable(Exception):
    """An expected lack of usable evidence, not an execution error."""

class InvalidMaskPayload(ValueError):
    """A producer returned an incomplete or inconsistent mask contract."""

PERSON_MASK_STATUSES = {MaskStatus.RELIABLE.value, MaskStatus.LIMITED.value}
MASK_PATHS = ("subject_mask_path", "boundary_band_path", "background_mask_path")

def person_mask_diagnostics(payload: dict | None, execution_error: str | None = None) -> dict:
    block = (payload or {}).get("person_subject_mask", {})
    quality = block.get("quality", {})
    backend = block.get("backend", "none")
    reliability = quality.get("mask_reliability", "low")
    errors = block.get("backend_errors", [])
    if quality.get("backend_error") and not errors:
        errors = [{"backend": "mediapipe_tasks_image_segmenter", "error": quality["backend_error"]}]
    reasons = list(quality.get("quality_reasons", []))
    person_specific = backend == "mediapipe_tasks_image_segmenter"
    if not block:
        status = MaskStatus.ERROR if execution_error else MaskStatus.UNAVAILABLE
        reasons.append(execution_error or "Segmentation produced no person-mask payload.")
    elif person_specific and reliability in {"high", "medium"}:
        status = MaskStatus.RELIABLE if reliability == "high" else MaskStatus.LIMITED
    elif backend == "opencv_hog":
        status = MaskStatus.APPROXIMATE
        reasons.append("HOG supplies a bounding box, not a validated person contour.")
    elif errors and not quality.get("person_detected"):
        status = MaskStatus.ERROR
        reasons.append("Segmentation backend execution failed and no usable person mask was produced.")
    elif not quality.get("person_detected"):
        status = MaskStatus.UNAVAILABLE
        reasons.append("No person was detected; a center-box diagnostic is not a person mask.")
    else:
        status = MaskStatus.UNRELIABLE
        if not reasons:
            reasons.append(f"Person-mask geometry rejected by existing quality policy ({reliability}).")
    usable = person_specific and status.value in PERSON_MASK_STATUSES
    return {
        "mask_status": status.value,
        "mask_source": backend,
        "mask_reliability": reliability if usable else "low",
        "person_specific": person_specific,
        "person_mask_reliability": reliability if usable else "low",
        "person_mask_reliable": usable,
        "fallback_used": backend in {"opencv_hog", "fallback_center_subject"},
        "fallback_reason": block.get("fallback_reason"),
        "rejection_reasons": reasons,
        "backend": backend,
        "backend_version": block.get("backend_version"),
        "model_name": block.get("model_name"),
        "model_version": block.get("model_version"),
        "confidence_kind": block.get("confidence_kind", "backend-specific proxy, not a calibrated probability"),
        "detection_confidence": quality.get("detector_confidence"),
        "foreground_area_ratio": quality.get("subject_area_ratio"),
        "mask_coverage": quality.get("subject_area_ratio"),
        "quality": quality,
        "mask_dimensions": block.get("image_geometry"),
        "backend_errors": errors,
        "disabled_stages": [],
    }

def normalize_region_masks(
    payload: dict, *, mask_source: str, mask_reliability: str,
    mask_status: str, person_specific: bool, fallback_used: bool = False,
    fallback_reason: str | None = None, background_excludes_boundary: bool = False,
) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("region_masks"), dict):
        raise InvalidMaskPayload("Missing region_masks object.")
    masks = dict(payload["region_masks"])
    shape = masks.get("shape")
    if not isinstance(shape, (list, tuple)) or len(shape) != 2 or any(type(n) is not int or n <= 0 for n in shape):
        raise InvalidMaskPayload("Mask shape must be two positive integer dimensions.")
    legacy_ratios = masks.get("ratios", {})
    for name in ("subject", "boundary", "background"):
        value = masks.get(f"{name}_ratio", legacy_ratios.get(name))
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise InvalidMaskPayload(f"Invalid {name} area ratio.")
        masks[f"{name}_ratio"] = float(value)
    masks.update({
        "shape": list(shape), "height": shape[0], "width": shape[1],
        "ratios": {name: masks[f"{name}_ratio"] for name in ("subject", "boundary", "background")},
        "source": "person_subject_mask" if person_specific else mask_source,
        "mask_source": mask_source, "mask_status": MaskStatus(mask_status).value,
        "mask_reliability": mask_reliability, "person_specific": bool(person_specific),
        "person_mask_reliability": mask_reliability if person_specific else "low",
        "fallback_used": bool(fallback_used), "fallback_reason": fallback_reason,
        "background_excludes_boundary": bool(background_excludes_boundary),
    })
    result = {**payload, "region_masks": masks}
    validate_region_masks(result, inspect_files=False)
    return result

def validate_region_masks(payload: dict, *, inspect_files: bool = True) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("region_masks"), dict):
        raise InvalidMaskPayload("Missing region_masks object.")
    masks = payload["region_masks"]
    shape = masks.get("shape")
    if not isinstance(shape, (list, tuple)) or len(shape) != 2 or any(type(n) is not int or n <= 0 for n in shape):
        raise InvalidMaskPayload("Invalid mask dimensions.")
    for key in ("mask_source", "mask_reliability", "mask_status", "person_specific", "fallback_used", "fallback_reason"):
        if key not in masks:
            raise InvalidMaskPayload(f"Missing canonical mask metadata: {key}.")
    if masks["mask_status"] not in {s.value for s in MaskStatus}:
        raise InvalidMaskPayload("Unknown mask status.")
    if any(type(masks[key]) is not bool for key in ("person_specific", "fallback_used")):
        raise InvalidMaskPayload("Mask availability flags must be booleans.")
    if masks["mask_reliability"] not in {"high", "medium", "low"} or not isinstance(masks["mask_source"], str) or not masks["mask_source"]:
        raise InvalidMaskPayload("Unknown mask reliability or source.")
    if masks.get("height") != shape[0] or masks.get("width") != shape[1]:
        raise InvalidMaskPayload("Mask dimensions disagree with shape.")
    if masks["mask_status"] in PERSON_MASK_STATUSES and (
        not masks["person_specific"] or masks["mask_reliability"] not in {"high", "medium"}
        or masks["mask_source"] != "mediapipe_tasks_image_segmenter"
    ):
        raise InvalidMaskPayload("Reliable person geometry requires a supported person-segmentation source.")
    for name, key in zip(("subject", "boundary", "background"), MASK_PATHS):
        if not isinstance(masks.get(key), (str, Path)) or not str(masks[key]):
            raise InvalidMaskPayload(f"Missing mask path: {key}.")
        ratio = masks.get(f"{name}_ratio")
        if not isinstance(ratio, (int, float)) or not math.isfinite(ratio) or not 0 <= ratio <= 1:
            raise InvalidMaskPayload(f"Invalid {name} ratio.")
        if inspect_files:
            image = cv2.imread(str(masks[key]), cv2.IMREAD_GRAYSCALE)
            if image is None or image.shape != tuple(shape):
                raise InvalidMaskPayload(f"Unreadable mask or shape mismatch: {key}.")
            if not np.isin(image, (0, 1, 255)).all():
                raise InvalidMaskPayload(f"Non-binary mask data: {key}.")
            actual = float(np.count_nonzero(image) / image.size)
            if abs(actual - ratio) > 1.0 / image.size + 1e-9:
                raise InvalidMaskPayload(f"Stored {name} ratio disagrees with mask coverage.")
    if masks["subject_ratio"] <= 0 or masks["background_ratio"] <= 0 or masks["boundary_ratio"] <= 0:
        raise InvalidMaskPayload("Region masks require nonempty foreground, background and boundary.")
    return masks

def require_person_geometry(payload: dict | None) -> dict:
    if payload is None:
        raise StageUnavailable("No usable subject/background region masks are available.")
    masks = validate_region_masks(payload, inspect_files=False)
    if not masks["person_specific"] or masks["mask_status"] not in PERSON_MASK_STATUSES:
        raise StageUnavailable("Approximate or rejected masks cannot support person-specific regional analysis.")
    return masks
