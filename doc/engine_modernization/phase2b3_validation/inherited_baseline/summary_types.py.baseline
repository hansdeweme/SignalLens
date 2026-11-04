#summary_types.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
# local imports to avoid circular dependencies
from gui_semantics import ModuleSummary
from signallens_version import APP_NAME, APP_VERSION, APP_STAGE, APP_GENERATOR_TEXT

@dataclass
class SummaryResult:
    overall_confidence: str = ""
    overall_pattern: Optional[str] = None
    overall_text: str = ""
    overall_polarity: str = "neutral"
    sections: dict[str, ModuleSummary] = field(default_factory=dict)
    overlay_paths: dict[str, str] = field(default_factory=dict)
    module_scores: dict[str, Optional[float]] = field(default_factory=dict)
    context_info: str = ""
    full_text: str = ""
    full_html: str = ""
    analysis_mode: str | None = None
    reasoning_trace: dict | None = None
    generator: str = APP_GENERATOR_TEXT
    app_metadata: dict = field(default_factory=lambda: {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "app_stage": APP_STAGE,
        "generator": APP_GENERATOR_TEXT,
    })