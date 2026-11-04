#vf_ela.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages#

from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import numpy as np
import math
from typing import Any, Dict, List
from PIL import Image, ImageChops, ImageEnhance
# local imports
from vf_overlay import create_hotspot_overlay

SUPPORTED_NATIVE_JPEG = {".jpg", ".jpeg"}

def estimate_jpeg_quality(img: Image.Image) -> int:
    """
    Estimate the JPEG quality (0-100) of a Pillow Image object using a Python port of ImageMagick's heuristic.    
    Returns -1 if the image is not a JPEG or has no quantization tables.
    """
    if not hasattr(img, 'quantization') or not img.quantization:
        return -1  # Not a JPEG or no qtables available    
    qdict = img.quantization
    qsum = sum(sum(qtable) for qtable in qdict.values())    
    if not qdict:
        return -1    
    # Start with luminance table (index 0)
    # but first test if we have a valid quantization table:
    q0 = qdict.get(0)
    if not q0 or len(q0) < 54:
        return -1    
    qvalue = q0[2] + q0[53]  # Specific coefficients used in the heuristic    
    q1 = qdict.get(1)
    if q1 and len(q1) >= 1:
        # Add chrominance info if present
        qvalue += q1[0] + q1[-1]
        hash_list = _HASH_2
        sums_list = _SUMS_2
    else:
        hash_list = _HASH_1
        sums_list = _SUMS_1    
    for i in range(100):
        if (qvalue < hash_list[i]) and (qsum < sums_list[i]):
            continue
        if ((qvalue <= hash_list[i]) and (qsum <= sums_list[i])) or (i >= 50):
            return i + 1    
    return -1

# Precomputed lookup tables (from the ImageMagick heuristic)
_HASH_1 = [510, 505, 422, 380, 355, 338, 326, 318, 311, 305,
           300, 297, 293, 291, 288, 286, 284, 283, 281, 280,
           279, 278, 277, 273, 262, 251, 243, 233, 225, 218,
           211, 205, 198, 193, 186, 181, 177, 172, 168, 164,
           158, 156, 152, 148, 145, 142, 139, 136, 133, 131,
           129, 126, 123, 120, 118, 115, 113, 110, 107, 105,
           102, 100, 97, 94, 92, 89, 87, 83, 81, 79,
           76, 74, 70, 68, 66, 63, 61, 57, 55, 52,
           50, 48, 44, 42, 39, 37, 34, 31, 29, 26,
           24, 21, 18, 16, 13, 11, 8, 6, 3, 2, 0]

_SUMS_1 = [16320, 16315, 15946, 15277, 14655, 14073, 13623, 13230, 12859,
           12560, 12240, 11861, 11456, 11081, 10714, 10360, 10027, 9679,
           9368, 9056, 8680, 8331, 7995, 7668, 7376, 7084, 6823,
           6562, 6345, 6125, 5939, 5756, 5571, 5421, 5240, 5086,
           4976, 4829, 4719, 4616, 4463, 4393, 4280, 4166, 4092,
           3980, 3909, 3835, 3755, 3688, 3621, 3541, 3467, 3396,
           3323, 3247, 3170, 3096, 3021, 2952, 2874, 2804, 2727,
           2657, 2583, 2509, 2437, 2362, 2290, 2211, 2136, 2068,
           1996, 1915, 1858, 1773, 1692, 1620, 1552, 1477, 1398,
           1326, 1251, 1179, 1109, 1031, 961, 884, 814, 736,
           667, 592, 518, 441, 369, 292, 221, 151, 86, 64, 0]

_HASH_2 = [1020, 1015, 932, 848, 780, 735, 702, 679, 660, 645,
           632, 623, 613, 607, 600, 594, 589, 585, 581, 571,
           555, 542, 529, 514, 494, 474, 457, 439, 424, 410,
           397, 386, 373, 364, 351, 341, 334, 324, 317, 309,
           299, 294, 287, 279, 274, 267, 262, 257, 251, 247,
           243, 237, 232, 227, 222, 217, 213, 207, 202, 198,
           192, 188, 183, 177, 173, 168, 163, 157, 153, 148,
           143, 139, 132, 128, 125, 119, 115, 108, 104, 99,
           94, 90, 84, 79, 74, 70, 64, 59, 55, 49,
           45, 40, 34, 30, 25, 20, 15, 11, 6, 4, 0]

_SUMS_2 = [32640, 32635, 32266, 31495, 30665, 29804, 29146, 28599, 28104,
           27670, 27225, 26725, 26210, 25716, 25240, 24789, 24373, 23946,
           23572, 22846, 21801, 20842, 19949, 19121, 18386, 17651, 16998,
           16349, 15800, 15247, 14783, 14321, 13859, 13535, 13081, 12702,
           12423, 12056, 11779, 11513, 11135, 10955, 10676, 10392, 10208,
           9928, 9747, 9564, 9369, 9193, 9017, 8822, 8639, 8458,
           8270, 8084, 7896, 7710, 7527, 7347, 7156, 6977, 6788,
           6607, 6422, 6236, 6054, 5867, 5684, 5495, 5305, 5128,
           4945, 4751, 4638, 4442, 4248, 4065, 3888, 3698, 3509,
           3326, 3139, 2957, 2775, 2586, 2405, 2216, 2037, 1846,
           1666, 1483, 1297, 1109, 927, 735, 554, 375, 201,
           128, 0]



@dataclass
class ElaMetrics:
    native_jpeg_ela: bool
    input_format: str
    recompression_quality: int
    mean_diff: float
    std_diff: float
    max_diff: int
    p95_diff: float
    high_diff_pixel_ratio: float
    ela_scale_factor: float
    status: str
    note: str

def load_rgb_image(path: Path) -> Image.Image:
    img = Image.open(path)
    return img.convert("RGB")

def compute_diff_array(original: Image.Image, recompressed: Image.Image) -> np.ndarray:
    diff = ImageChops.difference(original, recompressed)
    diff_arr = np.asarray(diff, dtype=np.uint8)
    return diff_arr

def compute_ela_scale_factor(diff_arr: np.ndarray, min_scale: float = 1.0, fallback_scale: float = 10.0) -> float:
    max_diff = int(diff_arr.max())
    if max_diff <= 0:
        return fallback_scale
    return max(min_scale, 255.0 / max_diff)

def create_ela_visual(diff_arr: np.ndarray, scale_factor: float) -> Image.Image:
    diff_img = Image.fromarray(diff_arr)
    enhancer = ImageEnhance.Brightness(diff_img)
    ela_img = enhancer.enhance(scale_factor)
    return ela_img

def compute_blockwise_ela_stats(
    diff_arr: np.ndarray,
    block_size: int = 64,
) -> Dict[str, Any]:
    """
    Compute blockwise ELA metrics from the raw diff array.
    Uses per-pixel max channel difference, then aggregates by block mean.
    """
    pixel_diff = diff_arr.max(axis=2).astype(np.float32)
    h, w = pixel_diff.shape
    grid_rows = math.ceil(h / block_size)
    grid_cols = math.ceil(w / block_size)
    blocks: List[Dict[str, Any]] = []
    block_means: List[float] = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            y0 = row * block_size
            y1 = min((row + 1) * block_size, h)
            x0 = col * block_size
            x1 = min((col + 1) * block_size, w)
            block = pixel_diff[y0:y1, x0:x1]
            block_mean = float(block.mean()) if block.size else 0.0
            block_max = float(block.max()) if block.size else 0.0
            block_p95 = float(np.percentile(block, 95)) if block.size else 0.0
            item = {
                "row": row,
                "col": col,
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "mean": block_mean,
                "max": block_max,
                "p95": block_p95,
            }
            blocks.append(item)
            block_means.append(block_mean)
    means = np.array(block_means, dtype=np.float32)
    median_block_mean = float(np.median(means)) if means.size else 0.0
    max_block_mean = float(np.max(means)) if means.size else 0.0
    p95_block_mean = float(np.percentile(means, 95)) if means.size else 0.0
    total_block_energy = float(np.sum(means)) if means.size else 0.0
    # Avoid divide-by-zero problems on very quiet images
    if median_block_mean <= 1e-8:
        max_block_to_median_ratio = float("inf") if max_block_mean > 0 else 1.0
    else:
        max_block_to_median_ratio = max_block_mean / median_block_mean
    # Hot blocks: relative threshold over block means
    # This is much more stable than a fixed raw-pixel threshold.
    hot_threshold = max(p95_block_mean, median_block_mean * 2.0)
    hot_mask = means >= hot_threshold if means.size else np.array([], dtype=bool)
    hot_block_ratio = float(hot_mask.mean()) if hot_mask.size else 0.0
    # Concentration: how much of the total block energy is in the top 5% blocks?
    if means.size:
        top_k = max(1, math.ceil(0.05 * len(means)))
        top_vals = np.sort(means)[-top_k:]
        top_5pct_block_energy_share = (
            float(np.sum(top_vals)) / total_block_energy
            if total_block_energy > 1e-8
            else 0.0
        )
    else:
        top_5pct_block_energy_share = 0.0
    # Top hotspot blocks for debugging / GUI display
    top_blocks = sorted(blocks, key=lambda b: b["mean"], reverse=True)[:10]       
    TOP_N = 10
    hottest_block = None
    if top_blocks:
        hottest_block = {
            "row": top_blocks[0]["row"],
            "col": top_blocks[0]["col"],
            "mean": top_blocks[0]["mean"],
        }    
    
    return {
        "block_size": block_size,
        "grid_rows": grid_rows,
        "grid_cols": grid_cols,
        "median_block_mean": median_block_mean,
        "max_block_mean": max_block_mean,
        "p95_block_mean": p95_block_mean,
        "max_block_to_median_ratio": max_block_to_median_ratio,
        "hot_block_ratio": hot_block_ratio,
        "top_5pct_block_energy_share": top_5pct_block_energy_share,
        "top_blocks": [
            {"row": b["row"], "col": b["col"], "mean": b["mean"]}
            for b in top_blocks[:TOP_N]
        ],
        "hottest_block": hottest_block
    }


#------------------------------
# classifier
#-----------------------------
def classify_ela_pattern(block_stats: Dict[str, Any]) -> Dict[str, Any]:
    ratio = block_stats["max_block_to_median_ratio"]
    hot_ratio = block_stats["hot_block_ratio"]
    concentration = block_stats["top_5pct_block_energy_share"]
    # Conservative first-pass heuristic rules
    if ratio >= 4.0 and hot_ratio <= 0.10 and concentration >= 0.30:
        return {
            "ela_pattern": "localized_compression_anomaly",
            "ela_signal_strength": "medium",
            "ela_note": (
                "ELA energy is concentrated in a limited number of blocks, "
                "which may indicate localized editing or compositing inconsistency."
            ),
        }
    if ratio < 2.0 and hot_ratio > 0.15 and concentration < 0.20:
        return {
            "ela_pattern": "uniform_recompression_pattern",
            "ela_signal_strength": "low",
            "ela_note": (
                "ELA activity appears relatively spread out, suggesting global recompression "
                "or naturally detailed image structure rather than a localized anomaly."
            ),
        }
    return {
        "ela_pattern": "ela_inconclusive",
        "ela_signal_strength": "low",
        "ela_note": (
            "ELA results do not clearly indicate either a localized anomaly or a uniform pattern."
        ),
    }

def compute_ela_metrics(
    diff_arr: np.ndarray,
    native_jpeg_ela: bool,
    input_format: str,
    recompression_quality: int,
    scale_factor: float,
) -> ElaMetrics:
    # Flatten across channels by taking per-pixel max channel difference
    pixel_diff = diff_arr.max(axis=2)

    mean_diff = float(pixel_diff.mean())
    std_diff = float(pixel_diff.std())
    max_diff = int(pixel_diff.max())
    p95_diff = float(np.percentile(pixel_diff, 95))

    # Threshold can be tuned later -> prioritize stable block-based statistics over this pixel-based count
    high_diff_threshold = 25
    high_diff_pixel_ratio = float((pixel_diff >= high_diff_threshold).mean())

    if not native_jpeg_ela:
        status = "exploratory_only"
        note = (
            "Input is not a native JPEG. ELA was computed after JPEG recompression and should "
            "be treated as exploratory, not as native JPEG compression evidence."
        )
    else:
        status = "ok"
        note = "Native JPEG ELA completed."

    return ElaMetrics(
        native_jpeg_ela=native_jpeg_ela,
        input_format=input_format,
        recompression_quality=recompression_quality,
        mean_diff=mean_diff,
        std_diff=std_diff,
        max_diff=max_diff,
        p95_diff=p95_diff,
        high_diff_pixel_ratio=high_diff_pixel_ratio,
        ela_scale_factor=scale_factor,
        status=status,
        note=note,
    )

def run_ela(
    image_path: Path,
    output_dir: Path,
    jpeg_quality: int = 90,
    save_intermediate_jpeg: bool = True,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    # estimate dynamically the original JPEG quality
    try:
        with Image.open(image_path) as img:
            org_quality_est = estimate_jpeg_quality(img)
    except Exception as e:
        # print(f"[Debug ELA] Error opening image for quality estimation: {e}")
        org_quality_est = -1        
    if org_quality_est == -1:
        recompress_quality = jpeg_quality
    else:
        recompress_quality = max(20, min(95, org_quality_est - 5))        
    # print(f"[Debug ELA] Estimated original JPEG quality of {image_path}: {org_quality_est}")
    # print(f"[Debug ELA] Effective recompression quality: {recompress_quality}")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    original = load_rgb_image(image_path)
    input_format = image_path.suffix.lower()
    native_jpeg_ela = input_format in SUPPORTED_NATIVE_JPEG
    temp_jpeg_path = output_dir / f"{image_path.stem}_ela_recompressed_q{recompress_quality}.jpg"
    # print(f"[Debug ELA] Recompressed JPEG quality of {temp_jpeg_path}: {recompress_quality}")  
    ela_image_path = output_dir / f"{image_path.stem}_ela.png"
    hotspot_overlay_original_path = output_dir / f"{image_path.stem}_ela_overlay_original.png"
    hotspot_overlay_diff_path = output_dir / f"{image_path.stem}_ela_overlay_diff.png"    
    ela_json_path = output_dir / f"{image_path.stem}_ela.json"
    # Recompress to JPEG
    original.save(temp_jpeg_path, "JPEG", quality=recompress_quality)
    recompressed = load_rgb_image(temp_jpeg_path)
    # Compute diff
    diff_arr = compute_diff_array(original, recompressed)
    # Scale for visibility
    scale_factor = compute_ela_scale_factor(diff_arr)
    ela_visual = create_ela_visual(diff_arr, scale_factor)
    ela_visual.save(ela_image_path)
    metrics = compute_ela_metrics(
        diff_arr=diff_arr,
        native_jpeg_ela=native_jpeg_ela,
        input_format=input_format,
        recompression_quality=recompress_quality,
        scale_factor=scale_factor,
    )
    block_stats = compute_blockwise_ela_stats(diff_arr=diff_arr, block_size=64)
    pattern = classify_ela_pattern(block_stats)
    #mark both original image and differezed image
    create_hotspot_overlay(
        base_image_path=image_path,
        output_path=hotspot_overlay_original_path,
        top_blocks=block_stats.get("top_blocks", []),
        block_size=block_stats["block_size"],
        max_blocks=10,
    )
    create_hotspot_overlay(
        base_image_path=ela_image_path,
        output_path=hotspot_overlay_diff_path,
        top_blocks=block_stats.get("top_blocks", []),
        block_size=block_stats["block_size"],
        max_blocks=10,
        outline_color="yellow",
    )    
    payload = {
        "file": {
            "input_path": str(image_path),
            "input_name": image_path.name,
        },
        "ela": {
            **asdict(metrics),
            "ela_image_path": str(ela_image_path),
            "ela_hotspot_overlay_original_path": str(hotspot_overlay_original_path),
            "ela_hotspot_overlay_diff_path": str(hotspot_overlay_diff_path),            
            "recompressed_jpeg_path": str(temp_jpeg_path) if save_intermediate_jpeg else None,
            "blockwise": block_stats,
            "pattern": pattern,
        },
    }
    ela_json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not save_intermediate_jpeg and temp_jpeg_path.exists():
        temp_jpeg_path.unlink(missing_ok=True)
    return payload
