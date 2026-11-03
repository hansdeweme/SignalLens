# Proposed concept: SignalLens Forensic Workbench

**UI-0 design proposal only. No replacement application has been implemented.** The wireframes use illustrative labels, not new forensic findings. Existing historical results inform content density, not design-example conclusions.

## Workspace and interaction

Use six stable destinations: Overview, Image Forensics, Evidence, Reasoning, Provenance, Reports. Keep analysis configuration beside entry/selected state and behind an explicit Configure action after results. Settings, archive maintenance and Help remain application-level commands. A persistent header identifies source file and run/revision; footer reports execution state and coverage. The investigation image stays available while changing evidence or reasoning selection.

|Area|Main content|Interaction and preservation|
|---|---|---|
|Entry / empty|Open/drop image, supported formats, short explanation, optional profile/context|Choose/drop uses existing supported-file workflow. No invented recent-case loader. Optional future recent runs require explicit persisted-case loading design. Configuration uses human labels with existing profile values.|
|Overview|Large source preview; primary finding and named hypothesis; confidence tier; parallel hypothesis summaries; key evidence and limitations|Tier and explanation are authoritative data. “View rationale” opens Reasoning with hypothesis selected. Source/run ID always visible. Partial coverage remains visible above fold.|
|Image Forensics|Detector/artifact list, source and derived view in resizable split; fit / 100% / zoom / pan; explanation below|Click detector selects existing payload/artifact. Link views only where geometry verified. Toggle source/derived or compare side by side; retain independent transforms when link is off. Baked overlay labeled as such.|
|Evidence|Hypothesis filter, role filter, observation table, detail inspector and source thumbnail|Rows show role, label, status, evidence ID and backend interpretation. Role is per hypothesis; do not globally color an observation as suspicious. Selection can link to an existing visualization when mapping is known.|
|Reasoning|Primary selection reason; hypothesis tree; candidate route evaluations; confidence policy; numerical ledger; ancestry details|Default to explanations, expandable technical identifiers. Policy result copied, never re-evaluated. Production ancestry and optional diagnostic shadow separated and explicitly labeled.|
|Provenance|Provenance state, raw metadata fields/signals, attribution, manual OSINT records|Today state says unverified or absent/ambiguous; verification capability unavailable. Analyst records include provider, URL/date/notes and attribution. Search opens external provider; does not imply automatic search or upload.|
|Reports|Current snapshot identity/revision, summary/trace/manifest artifact list, preview, reveal/copy paths|Reuse current HTML/TXT/JSON outputs. New report regeneration uses the same authoritative summary operation. PDF/print is future optional work, not an existing feature. Archive maintenance kept separate.|

Hypotheses: Synthetic origin; Localized editing; Camera-acquisition compatibility; Unresolved anomaly when actually returned. Do not force mutual exclusivity or add a fourth assessment when backend has not emitted it. The primary title describes a forensic interpretation. No authenticity meter, AI percentage, decorative trend chart or “verified camera photo” badge.

## State rules

Empty: source well and Open action, no fake placeholders that look like results. Selected: source identity/preview, configuration, Run; prior result access invalidated. Running: pinned run identity, current stage and detailed log; do not invent percent complete. Completed/partial: findings with stage coverage and exact missing reasons. Failed: plain error, retained diagnostic path where available, retry/open another image; prior results clearly attributed rather than silently substituted. Missing artifact file: keep its catalog entry, mark unavailable, leave evidence interpretation unchanged.

Run context must be a recorded input snapshot. Changing profile/context or OSINT after completion creates a revision or explicit “requires rerun/reinterpretation” state; never let a checkbox silently change the meaning of an already exported report. Preserve zoom/pan, selected evidence/hypothesis and scroll position across page navigation within a revision. Restore only safe workspace preferences across application launches.

## Visual system

Dark-first for the **inspection workspace**, with a fully supported light palette. This follows the current dark report convention and gives image surroundings a restrained surface; it is a design judgment, not evidence that users prefer dark mode. Current application has no consistent global theme, so dark-first requires deliberate palette coverage for all dialogs. Exports use light/print-friendly styling. Provide system/light/dark preference only when all states are verified.

|Token / role|Dark|Light|
|---|---|---|
|Canvas / image surround|#111827|#eef2f6|
|Main surface|#1f2937|#ffffff|
|Raised / selected surface|#293548|#e8eef6|
|Border|#526078|#66758a|
|Primary text|#f3f4f6|#172033|
|Secondary text|#c0cad8|#49566b|
|Action / focus|#93c5fd|#1d4ed8|
|Warning / limited|#fcd34d|#854d0e|
|Error / failed|#fca5a5|#991b1b|
|Completed execution|#86efac|#166534|

Semantic colors describe **execution and data availability**, not truth. Confidence badges use plain tier text and neutral border; evidence roles use labels + distinct icons, not red/green verdicts. Verify all final token/surface combinations against contrast targets; these are initial proposals, not certified components.

Typography: Segoe UI / system sans-serif, native Qt point sizes for DPI. Body 10–11pt; secondary labels 9–10pt; panel titles 12pt semibold; finding 16–18pt; application/page title 20pt only when needed. Consolas fallback monospace for IDs/paths; keep selectable and accessible. Tabular numerals where supported; right-align technical numerical columns and include units/scale semantics. Show missing values as — with a reason, not 0.

Spacing: 4 logical-pixel base; 8 control gaps, 12 compact panel padding, 16 standard panel padding, 24 section gaps. Evidence rows approximately 32–36 logical pixels at default font, expandable for long interpretations; do not truncate the only explanation. Input and navigation targets at least 32 logical pixels high, preferably 36; respect system font scaling and style metrics. At narrow widths, stack panels or collapse optional inspector; never hide the conclusion or limits. Initial target minimum 1024×700 logical pixels with a documented compact layout; validate against actual display constraints before choosing a hard minimum.

Components: left navigation with icon + text and active marker; flat bordered panels rather than decorative cards; hypothesis rows containing title/tier/explanation; evidence table with details beside it; detector panels with title, input role/dimensions and diagnostic caveat; disclosure rows for policy IDs, ledger and raw trace; stage list with text status; distinct failed/skipped/unavailable/inconclusive states; plain error panel with safe retry. Use native menus and context menus for copy/reveal actions.

Accessibility acceptance targets: normal text contrast ≥4.5:1; large text and non-text focus/control outlines ≥3:1; visible 2px focus ring; logical tab order and label buddies; all roles/statuses readable without color; accessible names for image views and zoom controls; keyboard fit/zoom/reset and table copy; 100/125/150/200% scaling with no clipped essential controls. Screen-reader behavior must be tested, not inferred from Qt inheritance.

## Review artifacts

Open `wireframes/index.html` for six static, labeled concepts (A–F). Each SVG is also standalone; PNGs are audit renders of those SVGs for convenient review. The Reports destination is specified above but is not a claimed current GUI screen. Wireframe placeholder images deliberately avoid fabricating detector outputs or heatmaps.
