# UI-3 Overview design specification

The Overview is a native Qt dashboard for the current investigation. It projects recorded results; it performs no forensic classification. UI-2's dark palette, Segoe UI typography, neutral confidence indicators, spacing, focus treatment and six-destination navigation remain authoritative.

## Information hierarchy

1. Filename (one visually elided line; full text in tooltip), lifecycle, captured profile, abbreviated recorded source hash and result availability.
2. Persistent links to Image Forensics, Evidence, Reasoning, Provenance and Reports. These route through the existing shell. They never launch analysis. Before completion, disabled links explain availability; the sidebar remains available, and Provenance enables after selection.
3. A horizontally resizable source/finding pair: aspect-fit image, encoded dimensions, bounded-preview label, keyboard-accessible zoom and reset; primary hypothesis, exact recorded confidence, dominant pattern, structured explanation and qualifiers.
4. Three distinct hypothesis cards: Synthetic origin, Localized editing and Camera-acquisition compatibility. Each has its own exact tier, explanation excerpt, limitation excerpt and reasoning action. Missing assessments remain unavailable. Camera compatibility explicitly does not establish authenticity or exclude editing/generation.
5. Supporting, contradicting and moderating evidence summaries, followed by limitations/coverage and full-narrative access.

The dashboard uses one vertical scroll surface. Navigation and analysis commands stay outside it. The first row calculates its preferred height from wrapped content at the actual panel widths rather than QLabel's initial narrow width. Source and primary finding are visible immediately; normal size also reveals all three hypothesis tiers. Evidence and comprehensive limitations require scrolling. At 1040×720, the first row remains reachable without horizontal scrolling; lower cards require more vertical scrolling. Maximization reveals more content rather than stretching the legacy narrative.

## Progressive disclosure

Structured excerpts are simple character caps, not narrative parsing or semantic summaries. Full explanations and limitations remain in existing Reasoning and the scope dialog; full source identity is copyable in Source identity. Observation details show exact hypothesis/role/ID/source/reliability/interpretation/lineage fields, marking missing values. Key evidence shows the first two observations per role in existing snapshot order, with no ranking, deduplication or new corroboration logic. Contextual observations and uncapped entries remain in Evidence and the decision trace.

The retained narrative opens in an owned, modeless dialog so it can continue receiving the existing guarded updates. There is still one summary widget and one result owner. All analysis commands remain in UI-2's command bar.

## Lifecycle and accessibility

Empty explains image selection; selected shows the source without findings; analyzing clears prior findings and uses existing guarded status/progress; completed reveals the recorded result; failed gives recovery instructions and the recorded error; cancelled/superseded displays no completed finding. Stored results identify their origin and unavailable fields. Missing/changed/corrupt images produce explicit viewer messages without erasing the historical forensic result.

Labels are plain text and wrap. Technical source text and detail views support copying. Buttons have native keyboard focus and accessible names; confidence is textual and never a percentage or verdict color. Long filenames retain their full accessible value/tooltip while visual elision bounds the header. No screen-reader audit or non-100% native DPI certification is claimed.
