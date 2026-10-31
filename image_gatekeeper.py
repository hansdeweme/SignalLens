# image_gatekeeper.py
from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

DEFAULT_RESOLUTION_POLICY = {
    "global": {"max_dim": 1024, "resample": Image.Resampling.LANCZOS},
    "patch": {"max_dim": 1400, "resample": Image.Resampling.LANCZOS},
    "subject": {"max_dim": 1024, "resample": Image.Resampling.LANCZOS},
    "ela": {"max_dim": None, "resample": Image.Resampling.LANCZOS},  # preserve original workflow
}

@dataclass
class PreparedImageInfo:
    role: str
    path: str
    width: int
    height: int
    scale: float
    resized: bool
    max_dim: int | None

def _fit_size(width: int, height: int, max_dim: int | None) -> tuple[int, int, float]:
    if max_dim is None:
        return width, height, 1.0
    longest = max(width, height)
    if longest <= max_dim:
        return width, height, 1.0
    scale = max_dim / float(longest)
    return max(1, round(width * scale)), max(1, round(height * scale)), scale

def _save_prepared_variant(
    src_path: Path,
    out_path: Path,
    max_dim: int | None,
    resample,
) -> PreparedImageInfo:
    with Image.open(src_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        new_w, new_h, scale = _fit_size(width, height, max_dim)
        resized = (new_w, new_h) != (width, height)
        if resized:
            rgb = rgb.resize((new_w, new_h), resample=resample)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rgb.save(out_path)
        return PreparedImageInfo(
            role=out_path.stem,
            path=str(out_path),
            width=new_w,
            height=new_h,
            scale=scale,
            resized=resized,
            max_dim=max_dim,
        )

def prepare_analysis_images(
    image_path: Path,
    output_dir: Path,
    resolution_policy: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    policy = resolution_policy or DEFAULT_RESOLUTION_POLICY
    prep_dir = output_dir / "prepared_images"
    prep_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as img:
        orig_w, orig_h = img.size
    prepared: dict[str, PreparedImageInfo] = {}
    for role, cfg in policy.items():
        suffix = f"{image_path.stem}_{role}.png"
        out_path = prep_dir / suffix
        prepared[role] = _save_prepared_variant(
            src_path=image_path,
            out_path=out_path,
            max_dim=cfg.get("max_dim"),
            resample=cfg.get("resample", Image.Resampling.LANCZOS),
        )
    return {
        "original": {
            "path": str(image_path),
            "width": orig_w,
            "height": orig_h,
        },
        "prepared": {k: asdict(v) for k, v in prepared.items()},
        "policy": {
            k: {"max_dim": v.get("max_dim")}
            for k, v in policy.items()
        },
    }