# UI-3 implementation report

## A. Baseline

Branch `main`, HEAD `05fd6dc685a7c704aadf482d512f8f6026fd089b`. Entry regression: **406 passed in 5.83s**, no failures/skips. The task markdown was untracked. Contrary to the reported clean state, Git could not read inherited audit pytest directories and displayed their tracked files as deleted. No ACL, restoration or deletion operation was performed on those assets.

Reviewed the UI-0 concept/visibility/wireframe material, UI-1 session/presentation/report contracts and UI-2 shell/design/visual documentation alongside actual implementation. No AGENTS.md was found in the workspace search.

## B. Overview implementation

New `overview_workspace.py` implements the image/finding splitter, source/lifecycle header, existing-destination actions, three hypothesis cards, ordered evidence summaries, limitation disclosure and retained narrative dialog. It uses UI-2 Panel/label/ConfidenceIndicator/StatusMessage/theme components. One scroll surface serves the dashboard; command bar and navigation stay visible. The persisted Overview splitter now controls source/finding widths rather than the old context/narrative heights. Existing validated two-size preferences remain safe proportions; persistence stores no investigation content.

## C. Source-image viewer

New `source_image_viewer.py` provides a bounded, aspect-preserving, auto-oriented QGraphicsView preview, fit/zoom/reset/pan, encoded dimensions, streamed identity verification and two-thread photo loading. Request identity rejects stale completion. Fingerprint checks reject mid-load or post-load file changes. Full-resolution forensic comparison is intentionally outside UI-3. See source_image_viewer.md for decoder memory/shutdown limits.

## D. Reasoning presentation

Every primary/pattern/tier/explanation/limitation is copied from the immutable presentation contract. Three hypothesis components remain distinct even when missing. Exact confidence tiers use neutral UI-2 styling. Key evidence is first-two-per-role in existing order, with full recorded observation details and no new ranking. Provenance verification, stage coverage and missing measurements remain separately named. Existing Reasoning text also includes full recorded limitations/policy names to support Overview's detail links.

## E. Session integration

The shell's complete session/invocation/result/revision/lifecycle guard remains before all binding. New frozen `SourceIdentityView` is an optional snapshot extension; presenter imports no engine. Reanalysis/selection clears findings; obsolete analysis and image completions cannot populate the active view. OSINT edits retain frozen forensic JSON and current reports use UI-1's revisioned publication. No session/worker/controller/report implementation was changed.

## F. Legacy compatibility

One original summary QTextEdit moved to the owned Full investigation narrative dialog. Existing synthesis/update/export paths still own its content. Commands, settings, OSINT, execution log, trace, artifact directory, reports and stored-summary loading retain their established workflows. No unrelated workspace redesign or dependency addition occurred.

## G. Validation

Final full regression: **432 passing, 0 failing, 0 skipped**. All 406 existing cases pass unchanged; 26 new parameterized Overview/viewer cases cover sources, zoom, asynchronous delivery, identity, missing fields, exact tiers, evidence ordering, lifecycle, navigation, annotations, imported reports and layout. The initial panorama test required a mathematically correct one-pixel rounding tolerance for integer downsampling; production aspect-fit logic was unchanged by that correction.

## H. Reference images

Both actual GUI pipelines used captured `normal` profile, unchanged source SHA-256, empty optional scene context and a copied settings snapshot with isolated output root. Instagram remains suspicious **21.32705**, benign **2.25**, High localized editing. Midjourney remains suspicious **6.675**, benign **1.5**, Medium provenance-supported synthetic context with unverified metadata. Full hypothesis/evidence/limitation structures, confidence, coverage counts and hashes equal UI-2. Both report generations were current. Complete settings/hashes/results are in reference_verification.json.

## I. Visual inspection

Actual offscreen widget renders cover all requested lifecycle/result fixtures plus long text, lower evidence/scope and narrative. Native Windows checks cover empty/selected/running/completed analysis and final minimum/maximized layouts. Source metadata duplication and inflated wrapped-text size hints were corrected during inspection. See visual_validation.md for capture inventory, exact dimensions and DPI limits.

## J. Git status

Production edits: `gui_workspace.py`, `investigation_presenters.py`, `presentation_models.py`; `.gitignore` adds only UI-3 generated-run exclusions. New production modules: `overview_workspace.py`, `source_image_viewer.py`. New tests: `tests/test_overview_workspace.py`. New documentation, validation scripts/records and screenshots are under this directory. The task markdown remains user-supplied/untracked. Inherited audit permission-related apparent deletions remain untouched. Nothing was staged, committed, pushed, merged, tagged, reset or stashed.

## K. UI-4 readiness

No blocker identified to starting UI-4. It must define full-resolution artifact identity, coordinate spaces, orientation/registration and unavailable-artifact semantics explicitly; the bounded source preview does not establish alignment. Preserve UI-1 guards and exact evidence/policy values. Non-primary DPI, screen readers and arbitrary decoder stress behavior remain validation gaps. UI-4 was not started.
