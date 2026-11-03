# UI-2 visual validation

## Actual application inspection

The modified application was launched using `py -3.13 -B signallens_gui.py` and inspected with Windows computer-use screenshots. Native validation covered empty Overview in maximized and restored modes, the real Settings dialog, and Ctrl+6 navigation to Reports with a visible focus state. Settings was closed without saving; no OSINT search, upload, feedback or archive deletion was performed. The validation window was closed normally.

Native captures include OS window frames: maximized 1920×1152; restored approximately 1282×932 for 1280×900 content; Settings approximately 822×752 for 820×720 content. A native Qt display query reported primary display 1920×1200, available 1920×1152, DPR 1.0 and 96 logical DPI. The secondary screen reports DPR 1.5, but the application was not moved there or inspected at that scale. Windows DPI settings were not changed. Do not interpret the secondary monitor's existence as 150% GUI verification.

## Screenshot inventory

All paths are under `doc/gui_modernization/ui2/screenshots/`. PNGs are actual **offscreen Qt widget renders**, not mockups. JPGs are actual **native Windows captures**. offscreen_capture_manifest.json records requested/actual dimensions, platform and DPR; screenshot_manifest.json records file dimensions and capture category.

|File|State and inspection|
|---|---|
|01_empty_overview_offscreen.png|Empty shell, navigation, unavailable confidence, disabled Run|
|02_image_selected_offscreen.png|Real reference image selected; bounded source thumbnail, no conclusion|
|03_analysis_running_offscreen.png|Real controller/worker run; analyzing state, indeterminate processing and actual stage status|
|04_completed_overview_offscreen.png|Real completed reference; recorded High local-editing interpretation and neutral tier|
|05_image_forensics_offscreen.png|Existing artifact access and recorded stage status list|
|06_evidence_offscreen.png|Recorded hypothesis-specific roles, explanations and stable IDs|
|07_reasoning_offscreen.png|Recorded hypothesis/policy rationale and existing Decision Trace action|
|08_provenance_offscreen.png|Metadata declaration/verification and single retained OSINT group|
|09_reports_offscreen.png|Current report validity/revision and inherited export/load actions|
|10_settings_offscreen.png|Existing themed Settings dialog; General tab|
|11_osint_dialog_offscreen.png|Existing themed OSINTFindingDialog; unsaved empty form|
|12_minimum_overview_offscreen.png|Supported minimum 1040×720; commands/navigation/narrative remain reachable|
|13_large_overview_offscreen.png|Large 1600×1000 content window; not a native maximization claim|
|14_native_empty_maximized.jpg|Native maximized empty Overview|
|15_native_empty_restored.jpg|Native restored empty Overview|
|16_native_settings_owned_window.jpg|Native Settings over its owning main window|
|17_native_settings_dialog.jpg|Native bounded Settings dialog capture|
|18_native_reports_keyboard_navigation.jpg|Native Ctrl+6 Reports selection and focus outline|

capture_validation.py uses a real reference analysis with an isolated output root; it does not replay a fabricated finding. Current normal-profile Instagram result is 21.32705 / 2.25, High localized editing, matching UI-1. Offscreen widget capture retains real content and scrolling behavior but does not certify OS/window-manager/DPI behavior.

## Issues found and corrected

- Scroll-area child surfaces initially used a light default palette. Named scroll content/viewports and group surfaces now use the centralized dark palette; white gutters/unreadable OSINT captions were corrected.
- A wrapping status QLabel caused the footer to consume excessive vertical space. StatusMessage now provides a fixed-height line, explicit ellipsis and full tooltip/accessibility text. UI-1 exact status strings are preserved.
- Disabled primary Run initially looked enabled because of selector specificity. A centralized disabled primary rule now makes its disabled state evident.
- Offscreen font fallback produced misleading width measurements and monospace/tofu renders. The renderer/tests explicitly register installed Windows fonts; native Windows typography was checked separately.
- Tall Settings profile forms now have scroll containers. Existing controls/save semantics remain unchanged.
- Compact OSINT actions are arranged in three columns instead of an overflowing seven-button row.
- Confidence in the new shell is always a neutral text tier. Legacy summary display colors are made readable without modifying report data or introducing percentages.

## Acceptance limits

At 1040×720, the Overview upper context/limitations region may require scrolling and can be resized with the splitter; long narrative has its retained independent text scroll. This is a deliberate transitional layout, not an all-content-above-fold dashboard. Navigation and analysis actions remain visible, and all six destinations can be opened at the minimum size.

Native empty/restored/maximized/Settings/navigation states were inspected. Completed/running/all-workspace/OSINT/minimum states were inspected offscreen. Other DPI scales, cross-monitor movement, screen-reader operation, packaged executable rendering and a user-selectable light mode remain unverified. Standard Qt icons and white native title bars remain OS-managed. No pixel-perfect cross-platform screenshot assertions are used.
