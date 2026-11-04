#narrative_builder.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from html import escape
# local imports to avoid circular dependencies
from gui_semantics import color_for_confidence, color_for_signal
from summary_types import SummaryResult

ORDERED_SECTION_KEYS = [
    "osint",
    "metadata",
    "sensor_origin",
    "cfa_demosaic",
    "ela",
    "noise",
    "compression_history",
    "subject_boundary",
    "region_masks",
    "segmentation_alignment",
    "cross_signal",
    "boundary",
    "boundary_focus",
    "patch_similarity",
    "patch_spatial",
    "region_fft",
    "fft",
    "subject_texture_consistency",
    "subject_process_asymmetry",
    "subject_material_realism",
]

def render_summary_text(result: SummaryResult) -> str:
    if not result.sections:
        return ""
    lines = [
        "Overall Forensic Reading (OSINT · Metadata · ELA · Residual · Sensor Origin · CFA/Demosaicing · Compression History · Patch Similarity · Cross-Signal · Boundary Signal · Boundary Focus · Subject Boundary · Region FFT · FFT)"
        f"Confidence Tier: {result.overall_confidence}",
        result.overall_text,
        "",
        "--------------------------------------------------",
        "",
    ]
    if result.context_info:
        lines.insert(3, f"Context Information: {result.context_info}")
    for key in ORDERED_SECTION_KEYS:
        section = result.sections.get(key)
        if section is None:
            continue
        lines.append(section.name)
        lines.append(section.note)
        lines.append("")
    return "\n".join(lines).rstrip()

def format_overall_text_html(text: str) -> str:
    if not text:
        return ""
    # Escape first (important for safety)
    text = escape(text)
    lines = text.split("\n")
    html_parts = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        # --- Bullet handling ---
        if stripped.startswith("- "):
            if not in_list:
                html_parts.append("<ul style='margin:6px 0 6px 16px; padding:0;'>")
                in_list = True
            html_parts.append(f"<li>{stripped[2:]}</li>")
            continue
        # --- Close list if needed ---
        if in_list:
            html_parts.append("</ul>")
            in_list = False
        # --- Section headers ---
        if stripped in {
            "Supporting Signals:",
            "Contradicting Signals:",
            "Confidence Rationale:",
        }:
            html_parts.append(
                f"<div style='margin-top:10px; font-weight:600;'>{stripped}</div>"
            )
            continue
        # --- Empty line → spacing ---
        if not stripped:
            html_parts.append("<div style='height:6px;'></div>")
            continue
        # --- Normal text ---
        html_parts.append(f"<div>{stripped}</div>")
    if in_list:
        html_parts.append("</ul>")
    return "".join(html_parts)

def render_summary_html(result: SummaryResult) -> str:
    if not result.sections:
        return ""

    confidence_color = color_for_confidence(
        result.overall_confidence,
        result.overall_polarity,
    )

    def htmlize_multiline(text: str) -> str:
        if not text:
            return ""
        return escape(text).replace("\n", "<br>")

    theme_css = """
    <style>
      :root {
        --sl-bg: #ffffff;
        --sl-text: #111827;
        --sl-muted: #4b5563;
        --sl-context-bg: #f3f4f6;
        --sl-context-border: #9ca3af;

        --sl-benign-weak: #9ae6b4;
        --sl-benign-medium: #48bb78;
        --sl-benign-strong: #166534;
      }

      @media (prefers-color-scheme: dark) {
        :root {
          --sl-bg: #0f172a;
          --sl-text: #d1d5db;
          --sl-muted: #9ca3af;
          --sl-context-bg: #111827;
          --sl-context-border: #4b5563;

          --sl-benign-weak: #9ae6b4;
          --sl-benign-medium: #48bb78;
          --sl-benign-strong: #166534;
        }
      }

      .sl-report {
        font-family: Segoe UI, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.4;
        color: var(--sl-text);
        background-color: var(--sl-bg);
        padding: 12px;
      }

      .sl-overall-title {
        font-size: 11pt;
        font-weight: 600;
        margin-bottom: 4px;
      }

      .sl-context-box {
        margin-top: 8px;
        margin-bottom: 8px;
        padding: 6px 8px;
        border-left: 3px solid var(--sl-context-border);
        background-color: var(--sl-context-bg);
        color: var(--sl-muted);
        font-style: italic;
      }

      .sl-section {
        margin-top: 10px;
        margin-bottom: 8px;
      }

      .sl-section-note {
        line-height: 1.35;
      }
    </style>
    """

    parts = [
        theme_css,
        "<div class='sl-report'>",
        "<div style='margin-bottom:12px;'>",
        "<div class='sl-overall-title'>Overall Forensic Reading</div>",
    ]

    if result.overall_confidence:
        parts.append(
            "<div style='margin-bottom:2px;'>"
            f"<b>Confidence Tier:</b> "
            f"<span style='color:{confidence_color}; font-weight:600;'>{escape(result.overall_confidence)}</span>"
            "</div>"
        )

    if result.overall_pattern:
        parts.append(
            "<div style='margin-bottom:2px;'>"
            f"<b>Dominant Pattern:</b> {escape(str(result.overall_pattern))}"
            "</div>"
        )

    if result.context_info:
        parts.append(
            "<div class='sl-context-box'>"
            f"{htmlize_multiline(str(result.context_info))}"
            "</div>"
        )

    if result.overall_text:
        parts.append(
            "<div style='margin-top:6px; line-height:1.4;'>"
            f"{format_overall_text_html(result.overall_text)}"
            "</div>"
        )

    parts.append("</div>")

    for key in ORDERED_SECTION_KEYS:
        section = result.sections.get(key)
        if section is None:
            continue

        heading_color = color_for_signal(section.polarity, section.status)
        parts.append("<div class='sl-section'>")
        parts.append(
            f"<div style='color:{heading_color}; font-weight:600; margin-bottom:2px;'>"
            f"{escape(section.name)}</div>"
        )
        if section.note:
            parts.append(
                f"<div class='sl-section-note'>{htmlize_multiline(section.note)}</div>"
            )
        parts.append("</div>")

    parts.append("</div>")
    return "".join(parts)