#signallens_settings.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
from __future__ import annotations
from   pathlib import Path
from   functools import lru_cache
from   copy import deepcopy
import json

SETTINGS_FILE = Path("signallens_settings.json")

DEFAULT_SETTINGS = {
    "supported_extensions": [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".heic", ".heif",],
    "file_masks": "*.jpg *.jpeg *.png *.webp *.tif *.tiff *.bmp *.heic *.heif",
    "output_root": "./analyzed/",
    "patch_similarity_profiles": {
        "normal": {
            "patch_size": 24,
            "stride": 12,
            "descriptor_size": 8,
            "similarity_threshold": 0.965,
            "max_pairs_to_keep": 300,
            "max_pairs_for_overlay": 60,
        },
        "subject_based": {
            "patch_size": 16,
            "stride": 8,
            "descriptor_size": 8,
            "similarity_threshold": 0.945,
            "max_pairs_to_keep": 500,
            "max_pairs_for_overlay": 80,
        },
    },
    "subject_background_profiles": {
        "normal": {
            "subject": 96,
            "boundary": 64,
            "background": 128,
        },
        "subject_based": {
            "subject": 160,
            "boundary": 64,
            "background": 64,
        },
    },
}

def _merge_defaults(user: dict, default: dict) -> dict:
    result = deepcopy(default)
    for key, value in user.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_defaults(value, result[key])
        else:
            result[key] = value
    return result

@lru_cache(maxsize=1)
def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return deepcopy(DEFAULT_SETTINGS)
    with SETTINGS_FILE.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    return _merge_defaults(loaded, DEFAULT_SETTINGS)

def save_settings(settings: dict) -> None:
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
    load_settings.cache_clear()
    
def reload_settings() -> dict:
    load_settings.cache_clear()
    return load_settings()   

def reset_settings_to_defaults() -> dict:
    save_settings(DEFAULT_SETTINGS)
    return load_settings()

def get_patch_profile(profile_name: str) -> dict:
    settings = load_settings()
    profiles = settings.get("patch_similarity_profiles", {})
    if profile_name in profiles:
        return profiles[profile_name]
    return profiles.get("normal", {})

def get_subject_background_profile(profile_name: str) -> dict:
    settings = load_settings()
    profiles = settings.get("subject_background_profiles", {})
    if profile_name in profiles:
        return profiles[profile_name]
    return profiles.get("normal", {})
    
def get_output_root() -> str:
    return load_settings().get("output_root", "analyzed")

def get_supported_extensions() -> list[str]:
    return load_settings().get("supported_extensions", [".jpg", ".jpeg", ".png", ".webp"])

def get_file_masks() -> str:
    return load_settings().get(
        "file_masks",
        "*.jpg *.jpeg *.png *.webp",
    )