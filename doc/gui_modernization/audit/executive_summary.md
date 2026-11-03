# SignalLens UI-0 executive summary

3 November 2026. **Recommend Option B: workspace modernization in PyQt6.** The forensic backend is substantially richer than its current single-form GUI. Preserve its reasoning and create structured, image-centered presentation around existing results. No redesign was implemented.

## Baseline and confidence in findings

`main`, HEAD `00c5eb2`; supplied earlier commits remain in history. Entry working tree was not clean: one modified reasoning-engine DOCX, the untracked UI-0 task and a Word lock file. Those changes were preserved. Core GUI: signallens_gui.py, settings_dialog.py, osint_dialogs.py; bridge/controller: analysis_worker.py and signallens_controller.py; presentation: summary_synthesizer.py, summary_sections.py, narrative_builder.py and gui_semantics.py.

Live empty-state inspection covered normal/maximized layout and Tools menu. A read-only harness displayed an existing stored summary in the actual GUI widget and inspected scrolling; no detector run or fixture modification occurred. Dialogs, progress/error behavior and detector output contracts were inspected in source where live coverage was unavailable. Screenshots and limitations are documented explicitly. All **334 existing regression tests passed** after a sandbox temporary-folder permission failure was resolved by an approved rerun. This confirms baseline logic tests, not full GUI correctness.

## Five most significant issues

1. No embedded source/detector viewer or comparison workspace: image investigation leaves the application.
2. Conclusions, per-hypothesis evidence and qualifications compete inside a 160–220px report pane; maximization mostly enlarges the OSINT region.
3. Decision Trace is a legacy partial projection: structured policy, coverage, corroboration and ancestry are not meaningfully navigable.
4. Session correctness needs attention: stale trace access on reselection, mutable run context and incomplete error-thread cleanup are source-confirmed risks.
5. Display/report revisions can diverge after OSINT edits; settings/output/archive ownership is inconsistent. A cosmetic reskin would preserve these weaknesses.

## Reasoning integration

Separate synthetic-origin, localized-editing and camera-acquisition assessments, supporting/contradicting/moderating/contextual evidence, confidence rationale and limitations already appear in long narrative text. They are hard to inspect, not wholly absent. Structured confidence policy, production corroboration, numerical allocation and pipeline coverage are richer in exported traces than in the dialog. Full dependency-shadow lineage is opt-in and must not be assumed available in ordinary GUI results. Metadata declarations remain unverified; this path has no cryptographic provenance validator.

## Proposed workbench and visual direction

Overview → Image Forensics → Evidence → Reasoning → Provenance → Reports. A QMainWindow/QStackedWidget shell with resizable splitters keeps source/run identity, finding, tier and limitations together. Reuse controller/worker, result objects, settings and OSINT forms and existing export formats. Use model-backed evidence/route tables and QGraphicsView image inspection; avoid framework replacement and new decorative dependencies.

Dark-first inspection workspace with full light-palette support; native Segoe UI hierarchy, compact 4-unit spacing rhythm, restrained panels, selectable technical IDs and visible keyboard focus. Confidence is a named tier attached to a hypothesis, never an authenticity probability or binary truth indicator. Qt supports a defined rich-text HTML subset, so current browser-style theme CSS should be replaced with native tokens/supported rendering ([Qt QTextEdit](https://doc.qt.io/qt-6/qtextedit.html)).

## Quick wins and phases

Quick wins: human-readable profile labels/tooltips, accessible semantic colors, consistent spacing/headings, useful empty states/action initialization, and a resizable summary/log region. None was implemented.

UI-1 foundation/session correctness → UI-2 overview → UI-3 image inspection → UI-4 evidence → UI-5 reasoning/provenance → UI-6 reports/accessibility/polish. Each phase has module boundaries, dependencies, complexity, risks and acceptance/regression gates in modernization_roadmap.md. No timing estimate is asserted without implementation evidence.

## Artifacts and preservation

All deliverables are under `doc/gui_modernization/audit/`:

- gui_architecture_inventory.md — component, dataflow and detector inventory.
- current_user_journey.md — implemented workflow and inferred usability costs.
- visual_design_audit.md — scored design review, observed states and limits.
- reasoning_visibility_matrix.md — exact backend/GUI mapping and conclusion assessment.
- gui_architecture_recommendation.md — options, ownership, Qt choices and feasibility boundaries.
- signal_lens_design_concept.md — proposed workspace, state rules, tokens and accessibility targets.
- modernization_roadmap.md — phased plan and ranked quick wins.
- executive_summary.md — this document.
- wireframes/index.html — six static proposed screens; individual A–F SVG and PNG files.
- screenshots/ — actual application captures; manifest in screenshots/README.md.
- source_index.json, protected_baseline.json, preservation_check.json, validation.json — source/reference and preservation evidence.
- inspect_sources.py, replay_gui.py, build_wireframes.py, validate_audit.py — isolated audit utilities; regression logs and temporary test files also remain within this directory.

No production/test/dependency edits, staging, commits, push, resets, stash or asset reorganization were performed. Final tracked-file hashes are compared to the audit-start baseline, including the user's pre-existing modified DOCX. Final status and exact validation outcomes are in validation.json. Proposed layouts are clearly separate from actual screenshots.
