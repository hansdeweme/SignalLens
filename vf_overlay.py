#vf_overlay.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages#
#

from __future__ import annotations
from investigation_storage import artifact_stem
from pathlib import Path
from typing import Any, Iterable
from PIL import Image, ImageDraw, ImageColor

#------------------------------------------------
# This module provides functionality to create visual overlays on images, highlighting areas of interest such as hotspots identified in ELA or noise analysis.
#------------------------------------------------

def create_shared_boundary_overlays(output_dir: Path, selected_file: Path, cross_signal_payload: dict, ela_payload: dict | None, noise_payload: dict | None) -> dict[str, str] | None:
    if selected_file is None:
        return None
    cross_payload = cross_signal_payload
    if not cross_payload:
        return None
    boundary_signal = cross_payload.get("boundary_signal", {})
    largest_cluster = boundary_signal.get("largest_shared_cluster", {})
    boundary_blocks = largest_cluster.get("blocks", [])
    if not boundary_blocks:
        return None
    block_size = 64
    if ela_payload is not None:
        block_size = (
            ela_payload.get("ela", {})
            .get("blockwise", {})
            .get("block_size", 64)
        )
    paths = {}
    # 1. Original image overlay
    original_overlay_path = output_dir / f"{artifact_stem(selected_file)}_shared_boundary_overlay_original.png"
    draw_cluster_overlay(
        base_image_path=selected_file,
        output_path=original_overlay_path,
        cluster_blocks=boundary_blocks,
        block_size=block_size,
        outline_color="cyan",
        outline_width=4,
        fill_color="cyan",
        fill_alpha=45,
    )
    paths["original"] = str(original_overlay_path)
    # 2. ELA differential overlay
    if ela_payload is not None:
        ela_diff_path = Path(ela_payload["ela"]["ela_image_path"])
        ela_overlay_path = output_dir / f"{artifact_stem(selected_file)}_shared_boundary_overlay_ela.png"
        draw_cluster_overlay(
            base_image_path=ela_diff_path,
            output_path=ela_overlay_path,
            cluster_blocks=boundary_blocks,
            block_size=block_size,
            outline_color="cyan",
            outline_width=3,
            fill_color="cyan",
            fill_alpha=35,
        )
        paths["ela"] = str(ela_overlay_path)
    # 3. Residual overlay
    if noise_payload is not None:
        noise_diff_path = Path(noise_payload["noise"]["residual_image_path"])
        noise_overlay_path = output_dir / f"{artifact_stem(selected_file)}_shared_boundary_overlay_noise.png"
        draw_cluster_overlay(
            base_image_path=noise_diff_path,
            output_path=noise_overlay_path,
            cluster_blocks=boundary_blocks,
            block_size=block_size,
            outline_color="cyan",
            outline_width=3,
            fill_color="cyan",
            fill_alpha=35,
        )
        paths["noise"] = str(noise_overlay_path)
    return paths
# ------------------------------------------------
# Normalize block coordinates
#------------------------------------------------
def _normalize_block_coords(blocks: Iterable[Any]) -> list[tuple[int, int]]:
    coords = []
    seen = set()
    for block in blocks:
        if isinstance(block, dict):
            row = int(block["row"])
            col = int(block["col"])
        else:
            row, col = block
        key = (row, col)
        if key not in seen:
            seen.add(key)
            coords.append(key)
    return coords

# ------------------------------------------------
# Ranked hotspot overlay (used for ELA / residual top blocks)
#------------------------------------------------
def create_hotspot_overlay(
    base_image_path: str | Path,
    output_path: str | Path,
    top_blocks: list[dict],
    block_size: int = 64,
    max_blocks: int = 10,
    outline_color: str = "red",
    outline_width: int = 3,
    show_labels: bool = True,
) -> Path:
    base_image_path = Path(base_image_path)
    output_path = Path(output_path)
    img = Image.open(base_image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    for i, block in enumerate(top_blocks[:max_blocks], start=1):
        row = int(block["row"])
        col = int(block["col"])
        x1 = col * block_size
        y1 = row * block_size
        x2 = min(x1 + block_size, img.width)
        y2 = min(y1 + block_size, img.height)
        draw.rectangle(
            [x1, y1, x2, y2],
            outline=outline_color,
            width=outline_width,
        )
        if show_labels:
            draw.text((x1 + 3, y1 + 3), str(i), fill=outline_color)
    img.save(output_path)
    return output_path

# ------------------------------------------------
# Cluster overlay with outer contour (used for boundary signals)
#---------------------
def draw_cluster_overlay(
    base_image_path: str | Path,
    output_path: str | Path,
    cluster_blocks: list[dict] | list[tuple[int, int]],
    block_size: int = 64,
    outline_color: str = "cyan",
    outline_width: int = 4,
    fill_color: str | None = None,
    fill_alpha: int = 40,
) -> Path:
    base_image_path = Path(base_image_path)
    output_path = Path(output_path)
    coords = _normalize_block_coords(cluster_blocks)
    coord_set = set(coords)
    img = Image.open(base_image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # translucent fill
    if fill_color is not None:
        fill_rgb = ImageColor.getrgb(fill_color)
        fill_rgba = (fill_rgb[0], fill_rgb[1], fill_rgb[2], fill_alpha)
        for row, col in coords:
            x0 = col * block_size
            y0 = row * block_size
            x1 = min(x0 + block_size, img.width)
            y1 = min(y0 + block_size, img.height)

            draw.rectangle([x0, y0, x1, y1], fill=fill_rgba)
    # draw only exposed edges -> continuous contour
    offset = outline_width / 2
    for row, col in coords:
        x0 = col * block_size
        y0 = row * block_size
        x1 = min(x0 + block_size, img.width)
        y1 = min(y0 + block_size, img.height)
        # top edge
        if (row - 1, col) not in coord_set:
            draw.line(
                [(x0 - offset, y0 - offset), (x1 + offset, y0 - offset)],
                fill=outline_color,
                width=outline_width,
                joint="curve",
            )
        # bottom edge
        if (row + 1, col) not in coord_set:
            draw.line(
                [(x0 - offset, y1 + offset), (x1 + offset, y1 + offset)],
                fill=outline_color,
                width=outline_width,
                joint="curve",
            )
        # left edge
        if (row, col - 1) not in coord_set:
            draw.line(
                [(x0 - offset, y0 - offset), (x0 - offset, y1 + offset)],
                fill=outline_color,
                width=outline_width,
                joint="curve",
            )
        # right edge
        if (row, col + 1) not in coord_set:
            draw.line(
                [(x1 + offset, y0 - offset), (x1 + offset, y1 + offset)],
                fill=outline_color,
                width=outline_width,
                joint="curve",
            )
    combined = Image.alpha_composite(img, overlay).convert("RGB")
    combined.save(output_path)
    return output_path