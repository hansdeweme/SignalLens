# UI-3 visual validation

19 actual PyQt6 widget renders and native Windows screenshots are in [screenshots](screenshots/). No generated illustration or mockup substitutes for app captures. `capture_validation.py` drives both real GUI reference analyses and labeled exceptional-state fixtures. `native_validation.py` launches the actual Windows platform with isolated preferences/output.

## Capture inventory

| Files | State / dimensions | Method |
|---|---|---|
| 01_empty_offscreen | Empty, 1280×900 | Actual offscreen Qt widget |
| 02_selected_offscreen | Selected Instagram source, 1280×900 | Actual offscreen Qt widget |
| 03_analyzing_offscreen | Live guarded worker progress, 1280×900 | Actual offscreen GUI pipeline |
| 04_instagram_complete_offscreen | Completed High localized editing, 1280×900 | Actual GUI pipeline |
| 05_midjourney_complete_offscreen | Completed Medium unverified synthetic context, 1280×900 | Actual GUI pipeline |
| 06_inconclusive_offscreen | Inconclusive, 1280×900 | Explicit presentation fixture, not a measured new result |
| 07_missing_source_offscreen | Missing source with historical finding, 1280×900 | Explicit fixture |
| 08_failed_offscreen | Failed invocation with no finding, 1280×900 | Explicit fixture |
| 09_minimum_offscreen | 1040×720 | Actual widgets, minimum size |
| 10_large_offscreen | 1600×1000 | Large widget render, **not native maximization** |
| 11_long_content_offscreen | Long filename/structured text, 1280×900 | Explicit fixture |
| 12_evidence_scope_offscreen | Lower dashboard, 1280×900 | Actual completed Midjourney data |
| 13_narrative_offscreen | Retained narrative dialog, 900×700 | Actual completed narrative |
| 14_empty_native | 1282×932 captured outer window | Native Windows; 1280×900 client |
| 15_selected_native | 1282×932 outer | Native picker selection and source preview |
| 16_analyzing_native | 1282×932 outer | Native Run Analysis interaction |
| 17_instagram_complete_native | 1282×932 outer | Native pipeline completion; captured during layout investigation before final preferred-height refinement |
| 18_minimum_native | 1042×752 outer | Final revised layout; 1040×720 client; stored validated Midjourney report |
| 19_maximized_native | 1920×1152 | Final revised layout; native maximization on primary monitor |

The final 04/05 offscreen captures reflect the preferred-height correction. Native 18/19 independently verify that correction in the Windows plugin. Native 14–16 show the same empty/selected/running layout, unaffected by the completed-text size-hint change.

## Native environment and interaction

Windows Qt platform, DELL U2412M primary monitor, device-pixel ratio 1.0, logical DPI 96; desktop 1920×1200 and available area 1920×1152. The actual native file picker accepted the Instagram path; Run Analysis reached the matching completed result. Final layout was inspected at minimum and maximized sizes. Native preview zoom and Fit / Reset were exercised, and the primary-finding action opened the existing Reasoning workspace with its full recorded limitations, alongside existing automated keyboard/navigation tests. Native rendering includes window borders/title bar; offscreen dimensions are client-widget dimensions.

A secondary display reports DPR 1.5 but the app was not validated there. No 125% or 150% native DPI certification is claimed, no OS display setting was changed, and offscreen captures are not treated as DPI evidence. Screen-reader behavior remains unverified.

## Comparison and corrections

Compared against UI-2's `screenshots/04_completed_overview_offscreen.png`: UI-2's small source preview and two independently scrolling panes put a large narrative region above compact structured coverage. UI-3 gives the source and primary finding the first row, separates the three hypotheses, and moves the full narrative to explicit disclosure. Evidence and limitations now have dedicated, readable blocks without replacing their complete historical content.

Inspection corrected three objective issues: duplicated selected filename/hash controls consumed excessive vertical space; long filenames could enlarge the header; and QLabel's initial narrow preferred widths inflated the completed top row. Source identity moved to a copyable detail dialog with a short hash in the header, the filename now visually elides while retaining exact accessible text, and preferred height uses actual wrapped panel widths. Normal 1280×900 shows source, primary finding and all three hypothesis tiers; maximized shows complete hypothesis cards. At minimum size, lower controls/cards require vertical scrolling but remain reachable. Tests assert no horizontal scrolling and adequate action widths.

Evidence role columns preserve source order, explicitly name missing observations and provide details; they introduce no ranking. Long explanations use disclosed excerpts/tooltips plus full Reasoning access. Scope shows partial coverage, unverified provenance and regional limitations without treating missing stages as authenticity. Theme, neutral confidence and uncertainty wording remain consistent with UI-2.

Remaining limits: evidence/full limitations sit below the initial viewport; minimum size requires more scrolling; the preview is bounded rather than full resolution. Native non-primary DPI and assistive-technology testing remain future validation work.
