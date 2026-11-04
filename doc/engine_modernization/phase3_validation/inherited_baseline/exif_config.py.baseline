#exif_config.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages

from pathlib import Path
import json

CONFIG_DIR = Path(__file__).parent
RULE_FILE = CONFIG_DIR / "exif_rules.json"

def load_exif_rules():
    with RULE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

# Load once at import
RULES = load_exif_rules()
WATCH_TAGS = set(tag.lower() for tag in RULES["watch_tags"])
TOOL_RULES = RULES["tool_rules"]
DECLARATIVE_GENERATION_TERMS = RULES["declarative_generation_terms"]
DECLARATIVE_ENHANCEMENT_TERMS = RULES["declarative_enhancement_terms"]

GENERATION_PROMPT_TAGS = {
    "prompt",
    "parameters",
    "workflow",
    "generationdata",
    "sd-metadata",
}

# Text-like tags that are worth scanning more broadly even if not in WATCH_TAGS.
TEXT_LIKE_TAG_HINTS = (
    "comment",
    "description",
    "caption",
    "keywords",
    "subject",
    "source",
    "software",
    "tool",
    "agent",
    "history",
    "prompt",
    "parameter",
    "generator",
    "manifest",
    "c2pa",
    "jumbf",
    "xml",
    "xmp",
    "warning",
)