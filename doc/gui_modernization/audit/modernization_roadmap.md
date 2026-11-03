# UI-0: bounded modernization roadmap

Recommended order: **UI-1 → UI-2 → UI-3 → UI-4 → UI-5 → UI-6**. Define the result adapter and stable IDs in UI-1 so image/evidence work does not create competing models. No arbitrary calendar estimates: complexity reflects ownership changes, cross-module integration and validation burden.

## UI-1 — Foundation and session correctness

- Objective: coherent native theme/typography, shell navigation scaffold, single session lifecycle and read-only result adapter.
- Modules: signallens_gui.py, analysis_worker.py, settings_dialog.py, signallens_settings.py, gui_semantics.py; adapter/session modules proposed, names to be chosen at implementation.
- New components: QMainWindow shell, navigation/stack, theme tokens, session coordinator and run ID. Reuse existing worker/controller, forms and report widget fallback.
- Dependency: current 334-test baseline and approved UI-0 direction. Complexity: **High** (lifecycle); theme-only subset Medium.
- Risks: stale callbacks, shutdown thread lifetime, cached settings, result folder identity. Keep pipeline scoring unchanged; cancellation excluded.
- Acceptance: old trace disabled on new selection; Clear/reselection/close cannot misattribute running work; error and success both clean up worker/thread; settings applied consistently; all old commands reachable; window/split preferences versioned separately from forensic settings; raw SummaryResult unchanged.
- Regression: all existing tests; add meaningful GUI lifecycle tests for failure, late completion and new-file invalidation. Test worker with mocked controller, no detector execution needed.

## UI-2 — Investigation Overview

- Objective: show source identity/image, primary hypothesis, exact tier, interpretation, parallel assessments and coverage limits together.
- Modules: signallens_gui.py, summary_types.py consumers, summary_synthesizer.py invocation boundary; narrative_builder.py retained as fallback/report renderer.
- New: source preview, FindingPanel, HypothesisList, CoveragePanel. Reuse SummaryResult/trace, evidence_presentation labels and existing narrative.
- Dependency: UI-1 adapter and session correctness. Complexity: **Medium**.
- Risks: mistaking a dominant pattern for a primary hypothesis; accidentally giving missing detector evidence a benign appearance; optional/legacy trace fields absent.
- Acceptance: displayed confidence exactly matches backend policy; missing hypotheses shown as not recorded; no invented percentages; limitations readable without scrolling the whole report; raw trace accessible; 1024×700 compact and maximized layouts verified.
- Regression: test_hypothesis_scoping.py, test_confidence_policy.py, test_reasoning.py, test_mask_pipeline.py; adapter checks for partial/invalid/legacy results and source/run identity.

## UI-3 — Image Forensics

- Objective: inspect actual output assets with fit/zoom/pan and safe comparisons.
- Modules: GUI adapter/viewers; image_gatekeeper.py and all vf payload schemas read, unchanged. summary_sections.py artifact adapters may need presentation metadata only.
- New: ArtifactCatalog, QGraphicsView viewer, comparison splitter, geometry-link controller. Reuse existing PNG/JPG outputs, prepared image metadata, patch pairs/masks, FFT plots.
- Dependency: UI-1 IDs and UI-2 source panel. Complexity: **High**.
- Risks: cross-resolution drift, regional crop offsets, spectrum vs spatial confusion, huge raster memory and missing files. Do not assume every baked overlay is a separable heatmap.
- Acceptance: every supported detector artifact reachable by name; source always reachable; independent zoom/pan works; aspect ratio preserved; synchronized link only for validated mapping; unavailable file explained; no original/artifact modification; memory bounded with lazy decode.
- Regression: test_mask_pipeline.py plus transform/patch-coordinate tests with different image sizes and crop offsets; manual large-image/high-DPI viewing. Existing reasoning suite must remain unchanged in output.

## UI-4 — Evidence Explorer

- Objective: query observations by hypothesis and role while preserving authoritative interpretation and lineage IDs.
- Modules: read-only SummaryResult/trace adapter; hypothesis_evidence.py and signal_language.py consumed unchanged.
- New: QAbstractTableModel/QSortFilterProxyModel, QTableView, evidence detail inspector and available-artifact link.
- Reuse: evidence_details, supporting/contradicting/moderating/contextual IDs and explanations, existing source viewer.
- Dependency: UI-1 contract, UI-2 hypothesis selection, UI-3 visual links. Complexity: **Medium–High**.
- Risks: roles differ across hypotheses; repeated observations are not independent sources; raw IDs can be absent from older traces.
- Acceptance: role switch changes only filtering; no re-scoring; missing vs empty role distinguished; same evidence retains stable ID across pages; copy includes hypothesis/role/source; sorting never changes findings; no speculative region highlight.
- Regression: test_hypothesis_scoping.py, test_evidence_lineage.py, test_numerical_evidence.py; model filtering/selection tests using multi-role and missing-details examples.

## UI-5 — Reasoning and Provenance

- Objective: expose actual policy/corroboration/numerical audit, metadata authenticity state and manual OSINT attribution.
- Modules: current Decision Trace method replaced by view; reasoning_persistence.py serializers retained; metadata_evidence.py, production_corroboration.py, confidence_policy.py and numerical_evidence.py consumed; OSINT dialogs reused.
- New: policy/route QTreeView, ledger table, ancestry inspector, metadata table and OSINT page.
- Dependency: UI-4 evidence IDs/details, UI-1 session revision. Complexity: **High**.
- Risks: opt-in shadow data confused with production; ancestry mistaken for statistical independence; present C2PA mistaken for validated C2PA; unsaved final report after OSINT edit.
- Acceptance: tier/rule/rationale identical to backend; compound and distinct-source gates labeled; diagnostic sidecars labeled and optional; missing graph says not recorded; no current path marked authenticated; OSINT edits visibly revise summary and report state; trace values HTML-escaped if rich text remains.
- Regression: test_production_corroboration.py, test_evidence_lineage.py, test_numerical_evidence.py, test_scorecard_integrity.py, test_confidence_policy.py, metadata cases in test_reasoning.py; GUI injection/escaping and revision parity tests.

## UI-6 — Reports, accessibility and polish

- Objective: reproducible report handoff, consistent workspace persistence, archive management and accessibility/performance verification.
- Modules: summary_persistence.py, reasoning_persistence.py, run_reporting.py, audit_manager.py, GUI report/archive/help views and settings.
- New: Reports artifact list/preview, copy/reveal commands, archive model view, final focus/shortcut map. Reuse existing JSON/TXT/HTML exports, logs and manifests; optional PDF needs separate scope.
- Dependency: all prior phases. Complexity: **Medium–High**.
- Risks: GUI/current-export mismatch; archive cleanup targeting wrong configured root; accidental evidence deletion; oversized artifact memory; preference migration.
- Acceptance: displayed run/revision matches exported content; report warnings and provenance qualifications survive export; configured archive path consistently honored; cleanup remains explicit/confirmed; all features keyboard reachable; contrast/DPI checklist passes; launch/resize/navigation responsive on representative results; original evidence hashes unchanged.
- Regression: all 334 existing tests plus report snapshot identity, Unicode/path, OSINT revision export, configured archive target and accessibility smoke tests. No new tests that merely restate CSS values.

## Ranked quick wins (not implemented)

Rank = User impact × feasibility × regression safety, each 1–5; 5 is highest/easiest/safest. These scores are prioritization judgments tied to concrete changes, not measurements.

|Rank|Improvement|I × F × S|Boundary|
|---|---|---|---|
|1|Replace raw profile display labels with “Standard” / “Subject focused”; tooltip explains scope while preserving item values|3×5×5=75|Low-risk presentation only|
|2|Fix summary/status foreground contrast for the current surfaces; retain text tier/role labels|4×4×4=64|Theme/render check needed; no polarity semantics changed|
|3|Use consistent 8/12/16 spacing and heading hierarchy in current form and supported rich text|3×4×5=60|Visual only; verify native minimum sizing|
|4|Improve empty-state guidance: identify Choose Image → configure → Run; explicitly initialize unavailable OSINT edit actions|3×4×4=48|Small state affordance; source unchanged until future phase|
|5|Make current summary vertically resizable by removing the low cap / introducing a simple splitter with log|4×3×4=48|Bounded layout change, verify normal/minimized sizing; no new result logic|

Structural changes are **not** cosmetic quick wins: new source viewer, lifecycle/worker fixes, report revision handling, evidence models, output-folder collision policy and cryptographic verification. Address correctness risks in UI-1 despite their higher complexity; ranking above is not a recommendation to postpone correctness for styling.
