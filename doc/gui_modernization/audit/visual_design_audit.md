# UI-0: visual design audit

## Method and limits

Live launch: `py -3.13 -B signallens_gui.py`, using the root source bootstrap and existing settings. Normal/restored window and maximized window were inspected on the current Windows desktop. Layout minimum overrides the requested 700×360 size; the normal bounded capture is 752×819, maximized 1920×1152. These are captured image dimensions, not a cross-DPI sizing specification. The summary is dark while the remaining native controls are light.

Completed rendering uses `replay_gui.py`: the real SignalLensGui and its actual QTextEdit receive unmodified stored full_html from `doc/final_acceptance_audit/instagram/summary/final_summary.json`. No result synthesis, detector run, new selection, settings save or persistence callback occurs. The harness status/log identify replay; no source image is loaded. The completed screenshot is evidence of rendering only, not an end-to-end pipeline test. Source references and backend interpretation were checked separately against current code.

Current Tools menu was viewed. Automation of a popup item failed because the native popup intercepted the parent-window target; retry/activation did not yield a verified dialog. Settings and Decision Trace were source-inspected, not visually certified. No fake dialog screenshots were generated. Existing test_images and analyzed folders contained no usable images/results; historical documentation validation artifacts supplied stored result data. No new real-image analysis was necessary.

## Scoring rubric

1 = essential task unsupported or severe obstruction; 2 = task possible with substantial friction/inconsistency; 3 = functional with clear limitations; 4 = coherent and efficient with minor gaps; 5 = mature, consistently verified across representative states/sizes/input methods. Scores combine observed rendering and explicitly identified code behavior; they are not averages or claims of user-study validity. Untested DPI/themes cannot qualify for 5.

|Category|Score / 5|Concrete evidence and implication|
|---|---:|---|
|Layout|2|V: initial form fits only after layout expansion; maximization stretches controls and OSINT list. S: summary max 220px, log fixed 100px; no splitter or outer scroll area. No embedded source-image area. Alignment within rows is regular, but proportions do not serve investigation.|
|Typography|2|R: confidence tier is bold and headings differentiate modules, but raw snake_case dominant pattern is very prominent; 10pt report body and 11pt title give modest hierarchy. Trace uses 13px; native control font left to platform. No aligned numerical table outside raw HTML.|
|Color|2|V/R: fixed dark summary within light form; red High tier has weak contrast. S: semantic colors are hardcoded; browser :root/var()/prefers-color-scheme CSS in QTextEdit is not a robust native theme mechanism. No app theme switch.|
|Components|2|V: familiar buttons/checks work as native controls, but seven OSINT actions stay prominent when empty. R: no detector viewer, artifact gallery or evidence table; HTML summary and modal route table carry complex reasoning. S: missing stages have note-level explanations, no stage panel.|
|Desktop ergonomics|2|V: line edit focus underline and readable controls; R: selectable report and internal scroll. S: no panel resize, zoom/pan, custom shortcuts or geometry persistence; no coordinated close/running-state guard. Multi-DPI keyboard/screen-reader behavior not fully exercised.|

Overall maturity: functional beta utility, with useful forensic narrative and reporting foundation; not yet a professional image-centered investigation workspace. No arithmetic overall score is warranted because absent image inspection and lifecycle risks outweigh cosmetic strengths.

## Contrast evidence

Calculated sRGB contrast against explicit summary background #1f2937: default body #d1d5db approximately 10:1 (good), suspicious High #b91c1c approximately 2.3:1 (poor for small text), benign medium #4ade80 approximately 8:1, neutral #6b7280 approximately 3:1 (poor for normal-size text). Use the exact recalculated values in validation.json if rounding differs. Log surface follows the native palette, so color testing must cover both palettes. Do not infer all rich-text browser CSS is applied; screenshot shows actual rendered result, and Qt supports only a defined rich-text HTML subset ([Qt QTextEdit](https://doc.qt.io/qt-6/qtextedit.html), [rich-text support](https://doc.qt.io/qt-6/richtext.html)).

## Screenshots and coverage

|File under screenshots/|What it actually demonstrates|
|---|---|
|01_initial_normal.jpg|Actual production GUI empty state at its initial layout-constrained size; configuration controls visible|
|02_empty_maximized.jpg|Settled maximized empty state; mixed surfaces, disproportionate OSINT allocation|
|04_completed_summary_replay.jpg|Actual summary widget with historical report header; replay clearly labeled|
|05_summary_evidence_scroll_replay.jpg|Long supporting-evidence prose after scrolling the same stored report|

Not captured: image-loaded state (no embedded image preview exists), analysis progress/error (no run performed), Settings modal, Decision Trace modal, detector/metadata/export screens (no dedicated detector/metadata/report workspace exists). Metadata and detector **notes** are rendered within the same report, not separate screens. Output artifacts themselves are diagnostic images, not screenshots of a viewer. Theme switching, long-table dialog resizing, secondary monitor and 125/150/200% DPI remain unverified. There is no implemented splitter to exercise.

## Prioritized visual and accessibility findings

1. Missing image inspection is the largest task gap. Preserve filename/run identity while adding source and actual detector views.
2. Pin finding scope, confidence rationale and limitations. A narrow scroll pane should not be the only place to discover qualifications.
3. Use native theme tokens and theme-specific semantic foregrounds; encode state with text/icons as well as color. “High” is confidence strength, not danger severity.
4. Move advanced context/profile details into a resizable configuration region; move logs into an expandable execution panel. Keep errors and coverage visible.
5. Provide focus order, label buddies, explicit commands, selected-row copy, keyboard zoom, and stable focus after page changes. Native Qt controls help but do not prove full assistive-technology support.

Source-confirmed risks requiring future verification: long profile settings may overflow without QScrollArea; route HTML columns can force horizontal scrolling; raw trace interpolation is not escaped; file reselection may expose stale trace. These were not reproduced by changing case data during this audit.
