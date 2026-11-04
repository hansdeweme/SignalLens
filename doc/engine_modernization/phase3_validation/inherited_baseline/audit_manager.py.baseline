#audit_manager.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta

@dataclass
class AuditRunInfo:
    name: str
    path: str
    size_bytes: int
    size_mb: float
    modified_at: str
    file_count: int
    folder_count: int

class AuditManager:
    def __init__(self, analyzed_dir: str | Path = "analyzed"):
        self.analyzed_dir = Path(analyzed_dir)

    def _folder_size_and_counts(self, folder: Path) -> tuple[int, int, int]:
        size = 0
        files = 0
        folders = 0
        for p in folder.rglob("*"):
            try:
                if p.is_file():
                    size += p.stat().st_size
                    files += 1
                elif p.is_dir():
                    folders += 1
            except OSError:
                continue
        return size, files, folders

    def list_runs(self) -> list[AuditRunInfo]:
        if not self.analyzed_dir.exists():
            return []
        runs: list[AuditRunInfo] = []
        for folder in self.analyzed_dir.iterdir():
            if not folder.is_dir():
                continue
            size, file_count, folder_count = self._folder_size_and_counts(folder)
            try:
                modified = datetime.fromtimestamp(folder.stat().st_mtime)
            except OSError:
                modified = datetime.min
            runs.append(
                AuditRunInfo(
                    name=folder.name,
                    path=str(folder),
                    size_bytes=size,
                    size_mb=round(size / (1024 * 1024), 2),
                    modified_at=modified.strftime("%Y-%m-%d %H:%M:%S"),
                    file_count=file_count,
                    folder_count=folder_count,
                )
            )
        runs.sort(key=lambda r: r.modified_at, reverse=True)
        return runs

    def get_archive_stats(self) -> dict:
        runs = self.list_runs()
        total_bytes = sum(r.size_bytes for r in runs)
        return {
            "analyzed_dir": str(self.analyzed_dir),
            "run_count": len(runs),
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "total_gb": round(total_bytes / (1024 * 1024 * 1024), 2),
            "average_mb": round((total_bytes / max(len(runs), 1)) / (1024 * 1024), 2),
            "largest_run": max((asdict(r) for r in runs), key=lambda x: x["size_bytes"], default=None),
            "oldest_run": min((asdict(r) for r in runs), key=lambda x: x["modified_at"], default=None),
            "newest_run": max((asdict(r) for r in runs), key=lambda x: x["modified_at"], default=None),
        }

    def delete_all_runs(self) -> int:
        runs = self.list_runs()
        deleted = 0
        for run in runs:
            path = Path(run.path)
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
                deleted += 1
        return deleted

    def delete_runs_older_than(self, days: int) -> int:
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        for run in self.list_runs():
            path = Path(run.path)
            try:
                modified = datetime.fromtimestamp(path.stat().st_mtime)
            except OSError:
                continue
            if modified < cutoff and path.exists() and path.is_dir():
                shutil.rmtree(path)
                deleted += 1
        return deleted

    def delete_runs_older_than_days(self, days: int = 30) -> int:
        return self.delete_runs_older_than(days)

    def remove_visual_artifacts_only(self) -> dict:
        visual_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
        deleted_files = 0
        deleted_bytes = 0
        for run in self.list_runs():
            folder = Path(run.path)
            for p in folder.rglob("*"):
                if not p.is_file():
                    continue
                if p.suffix.lower() not in visual_exts:
                    continue
                try:
                    size = p.stat().st_size
                    p.unlink()
                    deleted_files += 1
                    deleted_bytes += size
                except OSError:
                    continue
        return {
            "deleted_files": deleted_files,
            "deleted_bytes": deleted_bytes,
            "deleted_mb": round(deleted_bytes / (1024 * 1024), 2),
        }