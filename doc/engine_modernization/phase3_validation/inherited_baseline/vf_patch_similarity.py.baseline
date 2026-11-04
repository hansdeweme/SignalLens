#vf_patch_similarity.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#
# This module will produce false positives on: brick walls, windows, tiles, fabrics, foliage, repetitive architecture, patterned wallpapers,
# and many other naturally occurring repeated structures. 
# that is normal, That is why: thresholds are strict, labels are cautious,  the interpretation references scene context
# especially in combination with fft analysis, detector interaction needs interpretation thresholds.
# This module behaves more like “strong repeated local structure detector” than “reliable clone-reuse detector”, thus is best treated as supporting evidence not standalone proof

from __future__ import annotations
import json
import math
import numpy as np
import cv2
from   dataclasses import dataclass
from   pathlib import Path
from   typing import Any, Dict, List, Tuple
from   PIL import Image, ImageDraw
from  sklearn.neighbors import NearestNeighbors

# ============================================================
# configuration
# ============================================================
DEFAULT_MAX_DIM = 768
DEFAULT_PATCH_SIZE = 24
DEFAULT_STRIDE = 12
DEFAULT_DESCRIPTOR_SIZE = 8
DEFAULT_SIMILARITY_THRESHOLD = 0.965
DEFAULT_MIN_SEPARATION_FACTOR = 1.5
DEFAULT_MAX_PAIRS_TO_KEEP = 300
DEFAULT_MAX_PAIRS_FOR_OVERLAY = 60

# ============================================================
# dataclasses
# ============================================================

@dataclass
class PatchDescriptor:
    x: int
    y: int
    vector: np.ndarray

@dataclass
class PatchPair:
    ax: int
    ay: int
    bx: int
    by: int
    similarity: float
    distance: float

# ============================================================
# public API
# ============================================================
def run_patch_similarity_analysis(
image_path: str | Path,
    output_dir: str | Path,
    max_dim: int = DEFAULT_MAX_DIM,
    patch_size: int = DEFAULT_PATCH_SIZE,
    stride: int = DEFAULT_STRIDE,
    descriptor_size: int = DEFAULT_DESCRIPTOR_SIZE,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    max_pairs_to_keep: int = DEFAULT_MAX_PAIRS_TO_KEEP,
    max_pairs_for_overlay: int = DEFAULT_MAX_PAIRS_FOR_OVERLAY,
) -> Dict[str, Any]:    
    """
    Patch similarity / repetition analysis.
    Detects strong repeated local structures and possible clone-like reuse.
    Writes:
      - patch_similarity_results.json
      - *_patch_similarity_overlay.png
      - *_patch_similarity_heatmap.png
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    gray, rgb_for_overlay, scale_info = load_images(
        image_path=image_path,
        max_dim=max_dim,
    )
    h, w = gray.shape
    if h < patch_size or w < patch_size:
        raise ValueError(
            f"Image too small for patch analysis: {w}x{h}, patch_size={patch_size}"
        )
    descriptors = extract_patch_descriptors(
        gray=gray,
        patch_size=patch_size,
        stride=stride,
        descriptor_size=descriptor_size,
    )
        
    # choose between old bruteforce comparison vs bucketed comparison vs accelerated ANN search
    # Convert Cosine Similarity threshold to Euclidean Distance threshold
    # Formula: dist = sqrt(2 * (1 - similarity))
    dist_threshold = math.sqrt(2 * (1.0 - similarity_threshold))
    pairs, nn_stats = find_similar_patches_accelerated(
            patch_descriptors=descriptors,
            patch_size=patch_size,
            threshold=dist_threshold,
            max_matches=max_pairs_to_keep,
        )
    recurrence_map = build_recurrence_map(
        shape=gray.shape,
        pairs=pairs,
        patch_size=patch_size,
    )
    features = compute_similarity_features(
        pairs=pairs,
        recurrence_map=recurrence_map,
        patch_size=patch_size,
        shape=gray.shape,
    )
    similarity_pattern, similarity_note = interpret_patch_similarity(features)
    stem = image_path.stem
    overlay_path = output_dir / f"{stem}_patch_similarity_overlay.png"
    heatmap_path = output_dir / f"{stem}_patch_similarity_heatmap.png"
    json_path = output_dir / "patch_similarity_results.json"
    save_patch_similarity_overlay(
            base_image=rgb_for_overlay,
            pairs=pairs[:max_pairs_for_overlay],
            out_path=overlay_path,
            patch_size=patch_size,
        )
    save_recurrence_heatmap(
        recurrence_map=recurrence_map,
        out_path=heatmap_path,
    )
    result = {
        "patch_similarity": {
            "input_image": str(image_path),
            "patch_count": int(nn_stats["patch_count"]),
            # We map the new stats to the old keys so the Controller doesn't break
            "bucket_count": int(nn_stats["patch_count"]),  # Total patches acting as 'nodes'
            "nontrivial_bucket_count": len(pairs),         # Actual matches found
            "candidate_comparisons": int(nn_stats["candidate_comparisons"]),
            "repetition_score": round(float(features["repetition_score"]), 4),
            "clone_suspicion_score": round(float(features["clone_suspicion_score"]), 4),
            "pair_count": int(features["pair_count"]),
            "coverage_ratio": round(float(features["coverage_ratio"]), 4),
            "similarity_pattern": similarity_pattern,
            "similarity_note": similarity_note,
            # expose matched-pair geometry for spatial analysis            
            "top_pairs": [
                {
                    "ax": int(p.ax),
                    "ay": int(p.ay),
                    "bx": int(p.bx),
                    "by": int(p.by),
                    "similarity": round(float(p.similarity), 6),
                    "distance": round(float(p.distance), 3),
                }
                for p in pairs[:200]
            ],
            "patch_size": int(patch_size),
            "scale_info": {
                "scale": float(scale_info["scale"]),
                "width": int(scale_info["width"]),
                "height": int(scale_info["height"]),
            },
            "artifacts": {
                "patch_similarity_overlay": str(overlay_path),
                "patch_similarity_heatmap": str(heatmap_path),
            }
        }
    }
    save_json(result, json_path)
    return result

# ============================================================
# loading
# ============================================================

def load_images(
    image_path: str | Path,
    max_dim: int = DEFAULT_MAX_DIM,
) -> Tuple[np.ndarray, Image.Image, Dict[str, float]]:
    """
    Return grayscale float32 [0,1], RGB PIL image for overlay, and scale metadata.
    """
    with Image.open(image_path) as im:
        rgb = im.convert("RGB")
        gray = im.convert("L")
        w, h = rgb.size
        scale = min(1.0, max_dim / max(w, h))
        if scale < 1.0:
            new_size = (max(1, int(round(w * scale))), max(1, int(round(h * scale))))
            rgb = rgb.resize(new_size, Image.Resampling.LANCZOS)
            gray = gray.resize(new_size, Image.Resampling.LANCZOS)
        gray_arr = np.asarray(gray, dtype=np.float32) / 255.0
        return gray_arr, rgb, {
            "scale": scale,
            "width": rgb.width,
            "height": rgb.height,
        }


# ============================================================
# descriptor extraction
# ============================================================

def extract_patch_descriptors(
    gray: np.ndarray,
    patch_size: int,
    stride: int,
    descriptor_size: int,
) -> List[PatchDescriptor]:
    """
    Extract simple normalized descriptors from overlapping grayscale patches.
    Each descriptor is created by:
      - cropping patch
      - resizing to descriptor_size x descriptor_size
      - z-normalizing
      - flattening
    """
    h, w = gray.shape
    descriptors: List[PatchDescriptor] = []
    for y in range(0, h - patch_size + 1, stride):
        for x in range(0, w - patch_size + 1, stride):
            patch = gray[y:y + patch_size, x:x + patch_size]
            desc = patch_to_descriptor(patch, descriptor_size=descriptor_size)
            descriptors.append(PatchDescriptor(x=x, y=y, vector=desc))
    return descriptors

def patch_to_descriptor(patch: np.ndarray, descriptor_size: int) -> np.ndarray:
    small = cv2.resize(
        patch.astype(np.float32),
        (descriptor_size, descriptor_size),
        interpolation=cv2.INTER_AREA,
    )
    mean = float(small.mean())
    std = float(small.std())
    if std < 1e-6:
        vec = small - mean
    else:
        vec = (small - mean) / std
    vec = vec.reshape(-1).astype(np.float32)
    norm = float(np.linalg.norm(vec))
    if norm > 1e-8:
        vec /= norm
    return vec

def descriptor_to_bucket_key(
    vec: np.ndarray,
    bucket_dims: int,
    bucket_quant: float,
) -> tuple[int, ...]:
    """
    Convert a normalized descriptor into a coarse quantized bucket key.
    """
    dims = min(bucket_dims, len(vec))
    coarse = np.round(vec[:dims] * bucket_quant).astype(np.int16)
    return tuple(int(x) for x in coarse)    
        
def build_descriptor_buckets(
    descriptors: List[PatchDescriptor],
    bucket_dims: int,
    bucket_quant: float,
) -> Dict[tuple[int, ...], List[PatchDescriptor]]:
    buckets: Dict[tuple[int, ...], List[PatchDescriptor]] = {}
    for desc in descriptors:
        key = descriptor_to_bucket_key(
            vec=desc.vector,
            bucket_dims=bucket_dims,
            bucket_quant=bucket_quant,
        )
        buckets.setdefault(key, []).append(desc)
    return buckets

# ============================================================
# pair search replaces bucketed comparison
# The KD-Tree reduces the search complexity from $O(N^2)$ to $O(N \log N)$
# ============================================================
def find_similar_patches_accelerated(
    patch_descriptors: List[PatchDescriptor],
    patch_size: int = 8,
    threshold: float = 0.26,
    max_matches: int = 500,
    k_neighbors: int = 8,
) -> Tuple[List[PatchPair], Dict[str, Any]]:
    pairs: List[PatchPair] = []
    n_patches = len(patch_descriptors)
    k = min(k_neighbors, n_patches)
    stats = {
        "patch_count": n_patches,
        "search_mode": "nearest_neighbors",
        "k_neighbors": int(k),
        "candidate_comparisons": int(n_patches * max(k - 1, 0)),
    }
    if n_patches < 2:
        return pairs, stats
    feature_matrix = np.array(
        [p.vector for p in patch_descriptors],
        dtype=np.float32,
    )
    nn = NearestNeighbors(
        n_neighbors=k,
        algorithm="auto",
        metric="euclidean",
    )
    nn.fit(feature_matrix)
    distances, indices = nn.kneighbors(feature_matrix)
    seen_pairs = set()
    min_separation = patch_size * 2
    for i, (dists, idxs) in enumerate(zip(distances, indices)):
        p1 = patch_descriptors[i]
        for dist, neighbor_idx in zip(dists[1:], idxs[1:]):
            dist = float(dist)
            neighbor_idx = int(neighbor_idx)
            if dist >= threshold:
                continue
            p2 = patch_descriptors[neighbor_idx]
            dxy = math.hypot(p1.x - p2.x, p1.y - p2.y)
            if dxy <= min_separation:
                continue
            pair_key = tuple(sorted((i, neighbor_idx)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            sim = 1.0 - (dist ** 2 / 2.0)
            pairs.append(
                PatchPair(
                    ax=p1.x,
                    ay=p1.y,
                    bx=p2.x,
                    by=p2.y,
                    similarity=float(sim),
                    distance=float(dxy),
                )
            )
            if len(pairs) >= max_matches:
                break
        if len(pairs) >= max_matches:
            break
    pairs.sort(key=lambda p: (p.similarity, p.distance), reverse=True)
    return pairs, stats
#------------------------------------------------------
# bucketed comparison
#------------------------------------------------------
def find_similar_patch_pairs_bucketed(
    descriptors: List[PatchDescriptor],
    patch_size: int,
    similarity_threshold: float,
    min_separation_factor: float,
    max_pairs_to_keep: int,
    bucket_dims: int,
    bucket_quant: float,
    max_bucket_size: int,
) -> Tuple[List[PatchPair], Dict[str, float]]:
    """
    Compare descriptors only within coarse feature buckets.
    This is a first-pass candidate-pruning strategy to avoid full O(N^2).
    """
    min_separation = patch_size * min_separation_factor
    pairs: List[PatchPair] = []
    buckets = build_descriptor_buckets(
        descriptors=descriptors,
        bucket_dims=bucket_dims,
        bucket_quant=bucket_quant,
    )
    candidate_comparisons = 0
    bucket_sizes = []
    for key, bucket in buckets.items():
        bucket_size = len(bucket)
        bucket_sizes.append(bucket_size)
        # ignore singleton buckets
        if bucket_size < 2:
            continue
        # optional cap to avoid pathological buckets
        if bucket_size > max_bucket_size:
            # keep most "energetic" / variable descriptors first
            # for now: deterministic truncation by position
            bucket = bucket[:max_bucket_size]
            bucket_size = len(bucket)
        for i in range(bucket_size):
            di = bucket[i]
            vi = di.vector
            for j in range(i + 1, bucket_size):
                dj = bucket[j]
                candidate_comparisons += 1
                dxy = math.hypot(dj.x - di.x, dj.y - di.y)
                if dxy < min_separation:
                    continue
                sim = cosine_similarity(vi, dj.vector)
                if sim < similarity_threshold:
                    continue
                pairs.append(
                    PatchPair(
                        ax=di.x,
                        ay=di.y,
                        bx=dj.x,
                        by=dj.y,
                        similarity=float(sim),
                        distance=float(dxy),
                    )
                )
    pairs.sort(key=lambda p: (p.similarity, p.distance), reverse=True)
    pairs = pairs[:max_pairs_to_keep]
    bucket_count = len(buckets)
    nontrivial_bucket_count = sum(1 for s in bucket_sizes if s >= 2)
    mean_bucket_size = float(np.mean(bucket_sizes)) if bucket_sizes else 0.0
    max_observed_bucket_size = int(max(bucket_sizes)) if bucket_sizes else 0
    nn_stats = {
        "bucket_count": bucket_count,
        "nontrivial_bucket_count": nontrivial_bucket_count,
        "mean_bucket_size": mean_bucket_size,
        "max_observed_bucket_size": max_observed_bucket_size,
        "candidate_comparisons": candidate_comparisons,
    }
    return pairs, nn_stats    

# ============================================================
# 'old' pair search
# ============================================================
def find_similar_patch_pairs_bruteforce(
    descriptors: List[PatchDescriptor],
    patch_size: int,
    similarity_threshold: float,
    min_separation_factor: float,
    max_pairs_to_keep: int,
) -> List[PatchPair]:
    """
    Compare patch descriptors and keep highly similar, spatially separated pairs.
    For V1, a direct O(N^2) pass is acceptable on resized images with moderate stride.
    If needed later, this can be accelerated with ANN / LSH / KD-tree strategies.
    """
    min_separation = patch_size * min_separation_factor
    pairs: List[PatchPair] = []
    n = len(descriptors)
    for i in range(n):
        di = descriptors[i]
        vi = di.vector
        for j in range(i + 1, n):
            dj = descriptors[j]
            # suppress trivial local neighbors / overlapping patches
            dxy = math.hypot(dj.x - di.x, dj.y - di.y)
            if dxy < min_separation:
                continue
            sim = cosine_similarity(vi, dj.vector)
            if sim < similarity_threshold:
                continue
            pairs.append(
                PatchPair(
                    ax=di.x,
                    ay=di.y,
                    bx=dj.x,
                    by=dj.y,
                    similarity=float(sim),
                    distance=float(dxy),
                )
            )
    pairs.sort(key=lambda p: (p.similarity, p.distance), reverse=True)
    return pairs[:max_pairs_to_keep]

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))

# ============================================================
# recurrence map and features
# ============================================================
def build_recurrence_map(
    shape: Tuple[int, int],
    pairs: List[PatchPair],
    patch_size: int,
) -> np.ndarray:
    """
    Build a heatmap where repeated-patch regions accumulate evidence.
    """
    h, w = shape
    heat = np.zeros((h, w), dtype=np.float32)
    for p in pairs:
        weight = max(0.0, p.similarity - 0.90) / 0.10  # similarity emphasis
        weight = float(np.clip(weight, 0.0, 1.5))
        heat[p.ay:p.ay + patch_size, p.ax:p.ax + patch_size] += weight
        heat[p.by:p.by + patch_size, p.bx:p.bx + patch_size] += weight
    return heat

def compute_similarity_features(
    pairs: List[PatchPair],
    recurrence_map: np.ndarray,
    patch_size: int,
    shape: Tuple[int, int],
) -> Dict[str, float]:
    """
    Derive conservative summary features from strong repeated pairs.
    """
    h, w = shape
    image_area = float(h * w)
    pair_count = len(pairs)
    if pair_count == 0:
        return {
            "repetition_score": 0.0,
            "clone_suspicion_score": 0.0,
            "pair_count": 0,
            "spatially_separated_pair_count": 0,
            "strong_pair_density_score": 0.0,
            "mean_similarity": 0.0,
            "max_similarity": 0.0,
            "coverage_ratio": 0.0,
        }
    sims = np.array([p.similarity for p in pairs], dtype=np.float32)
    dists = np.array([p.distance for p in pairs], dtype=np.float32)
    # stronger evidence if repeated pairs are not just barely above threshold
    mean_similarity = float(np.mean(sims))
    max_similarity = float(np.max(sims))
    # "spatially separated" means well beyond local texture continuity
    separated_threshold = patch_size * 3.0
    spatially_separated_pair_count = int(np.sum(dists >= separated_threshold))
    # how much of the image participates in repeated-patch evidence
    active_mask = recurrence_map > 0.0
    coverage_ratio = float(np.count_nonzero(active_mask) / max(image_area, 1.0))
    # recurrence concentration / density
    if np.count_nonzero(active_mask) > 0:
        mean_active = float(np.mean(recurrence_map[active_mask]))
        max_active = float(np.max(recurrence_map[active_mask]))
    else:
        mean_active = 0.0
        max_active = 0.0
    strong_pair_density_score = clamp01(
        0.60 * min(pair_count / 50.0, 1.0) +
        0.40 * min(spatially_separated_pair_count / 20.0, 1.0)
    )
    repetition_score = clamp01(
        0.40 * min(pair_count / 40.0, 1.0) +
        0.30 * min(spatially_separated_pair_count / 16.0, 1.0) +
        0.15 * clamp01((mean_similarity - 0.96) / 0.03) +
        0.15 * clamp01(coverage_ratio / 0.12)
    )
    # make clone suspicion less coverage-positive
    clone_suspicion_score = clamp01(
        0.45 * min(spatially_separated_pair_count / 12.0, 1.0) +
        0.30 * clamp01((max_similarity - 0.975) / 0.02) +
        0.15 * clamp01((mean_similarity - 0.965) / 0.03) +
        0.10 * clamp01(1.0 - abs(coverage_ratio - 0.10) / 0.10)
        # balanced peak function: peak at coverage = 0.10 and falls off both sides
        # 0.10 * clamp01(coverage_ratio / 0.10) this always rewards more coverage, this is backwards for clone detection
        # High coverage is often natural repetition, low/moderate coverage is more consistent with localized copy-move
    )
    return {
        "repetition_score": float(repetition_score),
        "clone_suspicion_score": float(clone_suspicion_score),
        "pair_count": int(pair_count),
        "spatially_separated_pair_count": int(spatially_separated_pair_count),
        "strong_pair_density_score": float(strong_pair_density_score),
        "mean_similarity": float(mean_similarity),
        "max_similarity": float(max_similarity),
        "coverage_ratio": float(coverage_ratio),
    }

# ============================================================
# interpretation
# ============================================================
def interpret_patch_similarity(features: Dict[str, float]) -> Tuple[str, str]:
    repetition_score = float(features["repetition_score"])
    clone_score = float(features["clone_suspicion_score"])
    pair_count = int(features["pair_count"])
    separated_count = int(features["spatially_separated_pair_count"])
    mean_similarity = float(features["mean_similarity"])
    max_similarity = float(features["max_similarity"])
    coverage_ratio = float(features["coverage_ratio"])
    if pair_count == 0 or repetition_score < 0.18:
        return (
            "patch_similarity_inconclusive",
            "Patch-similarity analysis did not reveal strong spatially separated repeated structures beyond what can occur naturally in textured, patterned, or repetitive scene content."
        )
    # tighten possible_clone_reuse by adding coverage_ratio <= 0.18
    if clone_score >= 0.82 and separated_count >= 10 and max_similarity >= 0.985 and mean_similarity >= 0.93 and coverage_ratio <= 0.18:
        return (
            "possible_clone_reuse",
            "Patch-similarity analysis reveals highly similar spatially separated local regions consistent with duplicated local content or copy-move style reuse."
        )
    if repetition_score >= 0.60 and separated_count >= 10 and mean_similarity >= 0.972:
        return (
            "possible_synthetic_texture_repetition",
            "Patch-similarity analysis reveals repeated high-similarity local motifs across spatially separated regions, consistent with structured texture reuse or synthetic patch recurrence."
        )
    if repetition_score >= 0.35 and separated_count >= 4:
        return (
            "structured_patch_recurrence",
            "Patch-similarity analysis reveals repeated local structures across spatially separated regions. The result is notable, though it may still reflect natural patterned content depending on scene context."
        )
    return (
        "localized_repetition_detected",
        "Patch-similarity analysis reveals some repeated local structures, though the result remains only moderately specific and may reflect natural scene repetition."
    )

# ============================================================
# artifacts
# ============================================================
def save_patch_similarity_overlay(
    base_image: Image.Image,
    pairs: List[PatchPair],
    out_path: str | Path,
    patch_size: int,
) -> None:
    """
    Draw top repeated-patch boxes and connecting lines.
    """
    im = base_image.copy().convert("RGBA")
    draw = ImageDraw.Draw(im)
    for idx, p in enumerate(pairs):
        # slight taper in alpha/importance by rank
        rank_scale = max(0.25, 1.0 - idx / max(len(pairs), 1))
        line_alpha = int(180 * rank_scale)
        box_alpha = int(130 * rank_scale)
        line_color = (255, 80, 80, line_alpha)
        box_a_color = (255, 220, 80, box_alpha)
        box_b_color = (80, 220, 255, box_alpha)
        # centers
        acx = p.ax + patch_size / 2
        acy = p.ay + patch_size / 2
        bcx = p.bx + patch_size / 2
        bcy = p.by + patch_size / 2
        draw.line((acx, acy, bcx, bcy), fill=line_color, width=2)
        draw.rectangle(
            (p.ax, p.ay, p.ax + patch_size, p.ay + patch_size),
            outline=box_a_color,
            width=2,
        )
        draw.rectangle(
            (p.bx, p.by, p.bx + patch_size, p.by + patch_size),
            outline=box_b_color,
            width=2,
        )
    im.save(out_path)

def save_recurrence_heatmap(
    recurrence_map: np.ndarray,
    out_path: str | Path,
) -> None:
    """
    Save recurrence heatmap as grayscale for now.
    """
    arr = recurrence_map.astype(np.float32)
    if np.max(arr) > 0:
        arr = arr / np.max(arr)
    arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
    Image.fromarray(arr, mode="L").save(out_path)

# ============================================================
# helpers
# ============================================================
def clamp01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))

def save_json(data: Dict[str, Any], out_path: str | Path) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================================
# CLI test
# ============================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SignalLens Patch Similarity / Clone / Repetition Analysis")
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("--output-dir", required=True, help="Output folder")
    parser.add_argument("--max-dim", type=int, default=DEFAULT_MAX_DIM)
    parser.add_argument("--patch-size", type=int, default=DEFAULT_PATCH_SIZE)
    parser.add_argument("--stride", type=int, default=DEFAULT_STRIDE)
    parser.add_argument("--descriptor-size", type=int, default=DEFAULT_DESCRIPTOR_SIZE)
    parser.add_argument("--similarity-threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD)
    args = parser.parse_args()
    result = run_patch_similarity_analysis(
        image_path=args.image_path,
        output_dir=args.output_dir,
        max_dim=args.max_dim,
        patch_size=args.patch_size,
        stride=args.stride,
        descriptor_size=args.descriptor_size,
        similarity_threshold=args.similarity_threshold,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))