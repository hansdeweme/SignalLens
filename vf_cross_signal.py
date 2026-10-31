#vf_cross_signal.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#

#---------------------
# Signal Overlap Analysis and Classification
# These functions analyze the spatial overlap between ELA and noise analysis hotspots to identify potential cross-signal convergence patterns that may indicate localized editing or compositing.
#---------------------
from  collections import deque
import numpy as np

# Expects overlap metrics produced by compute_spatial_overlap(), not the legacy strict-intersection overlap schema.
# removed compute_block_overlap() since it's not needed for the new spatial proximity-based overlap approach.
# hotspot_mask = ELA_hotspots ∩ Residual_hotspots

def classify_cross_signal_overlap(overlap: dict) -> dict:
    matched_count = overlap.get("matched_ela_count", 0)
    overlap_ratio_ela = overlap.get("spatial_overlap_ratio_ela", 0.0)
    overlap_ratio_noise = overlap.get("spatial_overlap_ratio_noise", 0.0)
    spatial_jaccard_like = overlap.get("spatial_jaccard_like", 0.0)

    if matched_count >= 4 and spatial_jaccard_like >= 0.25:
        return {
            "cross_signal_pattern": "strong_hotspot_convergence",
            "cross_signal_strength": "medium",
            "cross_signal_note": (
                "ELA and residual analysis converge on the same localized regions, "
                "increasing confidence that these areas underwent distinct processing."
            ),
        }

    if matched_count >= 2 and (overlap_ratio_ela >= 0.20 or overlap_ratio_noise >= 0.20):
        return {
            "cross_signal_pattern": "partial_hotspot_convergence",
            "cross_signal_strength": "low",
            "cross_signal_note": (
                "ELA and residual analysis show partial spatial agreement in localized regions."
            ),
        }

    return {
        "cross_signal_pattern": "no_meaningful_convergence",
        "cross_signal_strength": "low",
        "cross_signal_note": (
            "ELA and residual analysis do not show meaningful hotspot agreement."
        ),
    }

def merge_block_lists(*block_lists):
    coords = set()
    merged = []
    for block_list in block_lists:
        for b in block_list:
            key = (b["row"], b["col"])
            if key not in coords:
                coords.add(key)
                merged.append({"row": b["row"], "col": b["col"]})
    return merged

def classify_boundary_convergence(
    overlap: dict,
    ela_pattern: dict,
    noise_pattern: dict,
) -> dict:
    ela_supportive = ela_pattern.get("ela_pattern") in {
        "localized_compression_anomaly",
        "ela_inconclusive",
    }
    noise_supportive = noise_pattern.get("noise_pattern") in {
        "localized_residual_anomaly",
        "noise_inconclusive",
    }

    shared_blocks = merge_block_lists(
        overlap.get("matched_ela_blocks", []),
        overlap.get("matched_noise_blocks", []),
    )

    clusters = find_connected_clusters(shared_blocks, connectivity=8)
    largest_cluster = clusters[0] if clusters else []
    contour = score_contour_shape(largest_cluster)

    matched_count = overlap.get("matched_ela_count", 0)
    spatial_overlap_ratio_ela = overlap.get("spatial_overlap_ratio_ela", 0.0)
    spatial_overlap_ratio_noise = overlap.get("spatial_overlap_ratio_noise", 0.0)

    strong_spatial_support = (
        matched_count >= 4
        and (spatial_overlap_ratio_ela >= 0.25 or spatial_overlap_ratio_noise >= 0.25)
    )
    # Strongest case: supportive component signals + good contour cluster
    if (
        ela_supportive
        and noise_supportive
        and strong_spatial_support
        and contour["is_contour_like"]
    ):
        return {
            "boundary_pattern": "possible_foreground_background_processing_mismatch",
            "boundary_strength": "medium",
            "boundary_note": (
                "ELA and residual hotspots converge in a connected, contour-like region. "
                "This is consistent with differential foreground/background processing, "
                "localized compositing, masking, or subject-specific retouching."
            ),
            "largest_shared_cluster": {
                "blocks": [{"row": r, "col": c} for r, c in largest_cluster],
                **contour,
            },
        }
    # Fallback case: strong spatial support even if contour clustering is fragmented
    if ela_supportive and noise_supportive and strong_spatial_support:
        return {
            "boundary_pattern": "possible_boundary_fragment_convergence",
            "boundary_strength": "low",
            "boundary_note": (
                "ELA and residual hotspots show strong spatial convergence, but the shared region "
                "is fragmented rather than forming a single strong contour-like cluster. "
                "This may still be consistent with foreground/background separation or localized retouching."
            ),
            "largest_shared_cluster": {
                "blocks": [{"row": r, "col": c} for r, c in largest_cluster],
                **contour,
            },
        }
    if matched_count >= 3 and (spatial_overlap_ratio_ela >= 0.20 or spatial_overlap_ratio_noise >= 0.20):
        return {
            "boundary_pattern": "partial_boundary_convergence",
            "boundary_strength": "low",
            "boundary_note": (
                "ELA and residual hotspots show partial spatial convergence, but the shared region "
                "is not strong enough or contour-like enough for a confident foreground/background interpretation."
            ),
            "largest_shared_cluster": {
                "blocks": [{"row": r, "col": c} for r, c in largest_cluster],
                **contour,
            },
        }
    return {
        "boundary_pattern": "boundary_inconclusive",
        "boundary_strength": "low",
        "boundary_note": (
            "Cross-signal hotspot overlap is not strong enough for a foreground/background boundary interpretation."
        ),
        "largest_shared_cluster": {
            "blocks": [{"row": r, "col": c} for r, c in largest_cluster],
            **contour,
        },
    }

def compute_cross_signal_payload(
    ela_blocks: list[dict],
    noise_blocks: list[dict],
    ela_pattern: str,
    noise_pattern: str,
    image_shape: tuple[int, int],
    block_size: int,
):
    # --- 1. spatial overlap ---
    overlap = compute_spatial_overlap(
        ela_blocks,
        noise_blocks,
        neighbor_distance=1,
    )
    # --- 2. classification ---
    cross_signal = classify_cross_signal_overlap(overlap)
    boundary_signal = classify_boundary_convergence(
        overlap,
        ela_pattern,
        noise_pattern,
    )
    if isinstance(cross_signal, str):
        cross_signal = {
            "cross_signal_pattern": cross_signal,
            "cross_signal_note": "",
        }
    if isinstance(boundary_signal, str):
        boundary_signal = {
            "boundary_pattern": boundary_signal,
            "boundary_note": "",
        }
    # --- 3. structural clustering ---
    shared_blocks = merge_block_lists(
        overlap.get("matched_ela_blocks", []),
        overlap.get("matched_noise_blocks", []),
    )
    clusters = find_connected_clusters(shared_blocks, connectivity=8)
    # --- 4. filter meaningful clusters ---
    filtered_blocks = []
    for cluster in clusters:
        shape = score_contour_shape(cluster)
        if shape["is_contour_like"] or shape["cluster_size"] >= 6:
            for r, c in cluster:
                filtered_blocks.append({"row": r, "col": c})
    # --- 5. build hotspot mask ---
    hotspot_mask = blocks_to_mask(
        filtered_blocks,
        image_shape=image_shape,
        block_size=block_size,
    )
    return {
        "overlap": overlap,
        "cross_signal": cross_signal,
        "boundary_signal": boundary_signal,
        "hotspot_mask": hotspot_mask,
    }

def blocks_to_mask(blocks: list[dict], image_shape: tuple[int, int], block_size: int,) -> np.ndarray:
    #  Convert block coordinates into a pixel-level binary mask.
    h, w = image_shape
    mask = np.zeros((h, w), dtype=np.uint8)
    for b in blocks:
        row = int(b["row"])
        col = int(b["col"])
        y0 = row * block_size
        x0 = col * block_size
        y1 = min(y0 + block_size, h)
        x1 = min(x0 + block_size, w)
        mask[y0:y1, x0:x1] = 1
    return mask

def compute_spatial_overlap(ela_blocks: list[dict], noise_blocks: list[dict], neighbor_distance: int = 1, ) -> dict:
    """
    Count ELA blocks as overlapping if a noise block lies within
    Chebyshev distance <= neighbor_distance.
    This is much better than strict coordinate intersection for
    contour-like hotspot regions.
    """
    ela_set = {(b["row"], b["col"]) for b in ela_blocks}
    noise_set = {(b["row"], b["col"]) for b in noise_blocks}
    matched_ela = set()
    matched_noise = set()
    shared_pairs = []
    for er, ec in ela_set:
        for nr, nc in noise_set:
            if abs(er - nr) <= neighbor_distance and abs(ec - nc) <= neighbor_distance:
                matched_ela.add((er, ec))
                matched_noise.add((nr, nc))
                shared_pairs.append({"ela": (er, ec), "noise": (nr, nc)})
                break
    union_size = len(ela_set | noise_set)
    return {
        "ela_block_count": len(ela_set),
        "noise_block_count": len(noise_set),
        "matched_ela_count": len(matched_ela),
        "matched_noise_count": len(matched_noise),
        "spatial_overlap_ratio_ela": len(matched_ela) / len(ela_set) if ela_set else 0.0,
        "spatial_overlap_ratio_noise": len(matched_noise) / len(noise_set) if noise_set else 0.0,
        "spatial_jaccard_like": (
            (len(matched_ela) + len(matched_noise)) / 2 / union_size
            if union_size else 0.0
        ),
        "matched_ela_blocks": [{"row": r, "col": c} for r, c in sorted(matched_ela)],
        "matched_noise_blocks": [{"row": r, "col": c} for r, c in sorted(matched_noise)],
        "shared_pairs": [
            {
                "ela_row": p["ela"][0],
                "ela_col": p["ela"][1],
                "noise_row": p["noise"][0],
                "noise_col": p["noise"][1],
            }
            for p in shared_pairs
        ],
    }

def find_connected_clusters(blocks: list[dict], connectivity: int = 8) -> list[list[tuple[int, int]]]:
    """
    Find connected components among blocks.
    connectivity=8 means diagonal touching counts as connected.
    """
    coords = {(b["row"], b["col"]) for b in blocks}
    visited = set()
    clusters = []
    if connectivity == 8:
        neighbors = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1),
                     (1, -1),  (1, 0),  (1, 1)]
    else:
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for start in coords:
        if start in visited:
            continue
        cluster = []
        queue = deque([start])
        visited.add(start)
        while queue:
            r, c = queue.popleft()
            cluster.append((r, c))
            for dr, dc in neighbors:
                nxt = (r + dr, c + dc)
                if nxt in coords and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        clusters.append(cluster)
    clusters.sort(key=len, reverse=True)
    return clusters

def score_contour_shape(cluster: list[tuple[int, int]]) -> dict:
    if not cluster:
        return {
            "cluster_size": 0,
            "bbox_height": 0,
            "bbox_width": 0,
            "elongation_ratio": 0.0,
            "bbox_fill_ratio": 0.0,
            "contour_like_score": 0.0,
            "is_contour_like": False,
        }
    rows = [r for r, _ in cluster]
    cols = [c for _, c in cluster]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)
    bbox_h = max_r - min_r + 1
    bbox_w = max_c - min_c + 1
    bbox_area = bbox_h * bbox_w
    cluster_size = len(cluster)
    elongation_ratio = max(bbox_h, bbox_w) / max(1, min(bbox_h, bbox_w))
    bbox_fill_ratio = cluster_size / bbox_area if bbox_area else 0
    score = 0.0
    if cluster_size >= 4:
        score += 0.3
    if elongation_ratio >= 1.4:      # relaxed
        score += 0.35
    if 0.1 <= bbox_fill_ratio <= 0.85:  # relaxed
        score += 0.35
    return {
        "cluster_size": cluster_size,
        "bbox_height": bbox_h,
        "bbox_width": bbox_w,
        "elongation_ratio": elongation_ratio,
        "bbox_fill_ratio": bbox_fill_ratio,
        "contour_like_score": score,
        "is_contour_like": score >= 0.55,  # relaxed
    }
