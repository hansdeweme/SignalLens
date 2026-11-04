#app_paths.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
import sys
from pathlib import Path

def app_dir() -> Path:
    """
    Folder containing the EXE in frozen mode,
    or the source folder in normal Python mode.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def resource_path(relative_path: str | Path) -> Path:
    """
    Resolve bundled read-only resources.
    In PyInstaller mode, --add-data files are placed under sys._MEIPASS.
    In source mode, resources are resolved relative to the source folder.
    """
    relative_path = Path(relative_path)
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return app_dir() / relative_path