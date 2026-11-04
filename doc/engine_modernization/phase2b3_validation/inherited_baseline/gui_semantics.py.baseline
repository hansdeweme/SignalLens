#sgui_semantics.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#
# Signal kinds / strengths how this translates into colours

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any

class LogLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARN = "warn"
    ERROR = "error"
    FINDING = "finding"

class SignalPolarity(str, Enum):
    NEUTRAL = "neutral"
    SUSPICIOUS = "suspicious"
    BENIGN = "benign"

class SignalStrength(str, Enum):
    NOT_RUN = "not_run"
    INCONCLUSIVE = "inconclusive"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    
SEMANTIC_COLORS = {
    "text_primary": "#d1d5db",
    "text_muted": "#9ca3af",
    "border_subtle": "#374151",
    "bg_subtle": "#1f2937",
    # log / event semantics
    "info": "#6b7280",
    "success": "#4b7f52",
    "warn": "#b08900",
    "error": "#b91c1c",
    "finding": "#6d28d9",
    # suspicious signal strengths
    "suspicious_weak": "#a16207",
    "suspicious_medium": "#b45309",
    "suspicious_strong": "#b91c1c",
    # benign signal strengths
    "benign_weak": "#bbf7d0",
    "benign_medium": "#4ade80",
    "benign_strong": "#15803d",
    # neutral / inconclusive
    "neutral_not_run": "#9ca3af",
    "neutral_inconclusive": "#6b7280",
}    

# helper functions
def color_for_log_level(level: str) -> str:
    level = (level or "info").lower()
    return {
        "info": SEMANTIC_COLORS["info"],
        "success": SEMANTIC_COLORS["success"],
        "warn": SEMANTIC_COLORS["warn"],
        "error": SEMANTIC_COLORS["error"],
        "finding": SEMANTIC_COLORS["finding"],
    }.get(level, SEMANTIC_COLORS["info"])
    
def color_for_signal(polarity: str, strength: str) -> str:
    polarity = (polarity or "neutral").lower()
    strength = (strength or "inconclusive").lower()
    if polarity == "suspicious":
        return {
            "weak": SEMANTIC_COLORS["suspicious_weak"],
            "medium": SEMANTIC_COLORS["suspicious_medium"],
            "strong": SEMANTIC_COLORS["suspicious_strong"],
        }.get(strength, SEMANTIC_COLORS["neutral_inconclusive"])
    if polarity == "benign":
        return {
            "weak": SEMANTIC_COLORS["benign_weak"],
            "medium": SEMANTIC_COLORS["benign_medium"],
            "strong": SEMANTIC_COLORS["benign_strong"],
        }.get(strength, SEMANTIC_COLORS["neutral_inconclusive"])
    return {
        "not_run": SEMANTIC_COLORS["neutral_not_run"],
        "inconclusive": SEMANTIC_COLORS["neutral_inconclusive"],
        "weak": SEMANTIC_COLORS["neutral_inconclusive"],
        "medium": SEMANTIC_COLORS["neutral_inconclusive"],
        "strong": SEMANTIC_COLORS["neutral_inconclusive"],
    }.get(strength, SEMANTIC_COLORS["neutral_inconclusive"])
    
def color_for_confidence(confidence: str, polarity: str = "neutral") -> str:
    confidence = (confidence or "Low").capitalize()
    polarity = (polarity or "neutral").lower()
    if polarity == "suspicious":
        return {
            "High": SEMANTIC_COLORS["suspicious_strong"],
            "Medium": SEMANTIC_COLORS["suspicious_medium"],
            "Low": SEMANTIC_COLORS["neutral_inconclusive"],
        }.get(confidence, SEMANTIC_COLORS["neutral_inconclusive"])
    if polarity == "benign":
        return {
            "High": SEMANTIC_COLORS["benign_strong"],
            "Medium": SEMANTIC_COLORS["benign_medium"],
            "Low": SEMANTIC_COLORS["neutral_inconclusive"],
        }.get(confidence, SEMANTIC_COLORS["neutral_inconclusive"])
    return {
        "High": SEMANTIC_COLORS["warn"],
        "Medium": SEMANTIC_COLORS["warn"],
        "Low": SEMANTIC_COLORS["neutral_inconclusive"],
    }.get(confidence, SEMANTIC_COLORS["neutral_inconclusive"])
    
@dataclass
class ModuleSummary:
    name: str
    status: str = "not_run"
    polarity: str = "neutral"
    domain: str = "unknown"
    pattern: Optional[str] = None
    score: Optional[float] = None
    confidence: Optional[str] = None
    note: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    