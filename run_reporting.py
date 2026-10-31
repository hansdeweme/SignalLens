#run_reporting.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#


from __future__ import annotations
import json
from   dataclasses import dataclass, field
from   datetime import datetime, timezone
from   pathlib import Path
from   typing import Any, Dict, List, Optional
from   uuid import uuid4
# local imports
from signallens_version import APP_VERSION

def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()

def _safe_jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)

@dataclass
class RunRecorder:
    output_dir: Path
    selected_file: Path
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8])
    started_at: str = field(default_factory=_now_iso)
    finished_at: Optional[str] = None
    status: str = "running"

    stages: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir)
        self.selected_file = Path(self.selected_file)
        self.logs_dir = self.output_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "analysis_run.json"
        self.log_path = self.logs_dir / "run.log"
        self.flush_manifest()

    def log(self, message: str, level: str = "info") -> None:
        line = f"{_now_iso()} [{level.upper()}] {message}\n"
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line)

    def record_stage_start(self, stage_name: str) -> None:
        self.stages.append({
            "name": stage_name,
            "started_at": _now_iso(),
            "finished_at": None,
            "status": "running",
            "elapsed_seconds": None,
            "error": None,
        })
        self.flush_manifest()

    def record_stage_finish(self, stage_name: str, elapsed_seconds: float, status: str = "success", error: str | None = None) -> None:
        for stage in reversed(self.stages):
            if stage["name"] == stage_name and stage["finished_at"] is None:
                stage["finished_at"] = _now_iso()
                stage["status"] = status
                stage["elapsed_seconds"] = round(float(elapsed_seconds), 4)
                stage["error"] = error
                break
        self.flush_manifest()

    def record_error(self, where: str, message: str) -> None:
        self.errors.append({
            "where": where,
            "message": message,
            "at": _now_iso(),
        })
        self.flush_manifest()

    def add_artifact(self, key: str, value: Any) -> None:
        self.artifacts[key] = _safe_jsonable(value)
        self.flush_manifest()

    def finalize(self, status: str = "completed") -> None:
        self.status = status
        self.finished_at = _now_iso()
        self.flush_manifest()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "app": "SignalLens",
            "version": APP_VERSION,            
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "input": {
                "selected_file": str(self.selected_file),
                "input_name": self.selected_file.name,
            },
            "stages": self.stages,
            "artifacts": self.artifacts,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def flush_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.as_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

