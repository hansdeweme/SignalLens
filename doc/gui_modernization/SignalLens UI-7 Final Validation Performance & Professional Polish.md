# CODEX TASK — SignalLens UI-7 Final Validation, Performance & Professional Polish

## Mission

You are the principal Windows desktop software architect, senior Python/PyQt6 engineer, forensic-software quality specialist, performance engineer and release-validation lead for SignalLens.

Your task is to complete **UI-7 — Final Validation, Performance & Professional Polish**, the final phase of SignalLens's GUI modernization.

Over the preceding phases, SignalLens has evolved from a traditional forensic utility interface into a six-workspace investigation application.

The completed phases are:

| Phase | Implementation |
|---|---|
| UI-0 | GUI architecture and usability audit |
| UI-1 | Investigation-session integrity and presentation contracts |
| UI-2 | Dark-first design system and workspace shell |
| UI-3 | Image-centered Investigation Overview |
| UI-4 | Forensic Image Inspection and Comparison |
| UI-5 | Structured Evidence and Reasoning Explorers |
| UI-6 | Provenance, OSINT and Reports workspaces |

The underlying forensic reasoning engine has also completed its original ten-point correctness modernization.

**Your mission is to verify that the modernized application is reliable, performant, visually consistent and professionally usable as a native Windows forensic investigation tool.**

This phase must not become another feature-development project.

The priority is to identify and correct demonstrated defects, validate existing capabilities and establish a reliable release baseline.

---

# PART A — Baseline and mandatory engineering discipline

## 1. Verify the repository

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Windows desktop application
- Existing Windows packaging configuration, if present

Latest reported baseline:

- Branch: `main`
- UI-6 implemented.
- 514 regression tests passed.
- Zero failures, skips or warnings.
- UI-6 changes may remain uncommitted.
- Native Windows DPI testing remains incomplete.
- Large legacy automatic report saves remain synchronous.

Verify the actual repository state.

Record:

1. Current branch.
2. HEAD commit.
3. Working-tree status.
4. Tracked and untracked changes.
5. Existing test count.
6. Python and PyQt6 versions.
7. Current packaging configuration.
8. Existing GUI and application entry points.

Do not assume that UI-6 was committed.

Preserve inherited work.

Do not stage, commit, push, merge, reset, stash, tag or discard any changes.

Keep test images and generated forensic outputs outside Git.

---

## 2. Read mandatory project guidance

Before editing, read:

`AGENTS.md`

`doc/test_quality/TEST_DISCIPLINE.md`

`doc/test_quality/behavioral_coverage_matrix.md`

`doc/test_quality/rationalization_report.md`

Also review the GUI modernization documentation:

`doc/gui_modernization/audit/`

`doc/gui_modernization/ui1/`

`doc/gui_modernization/ui2/`

`doc/gui_modernization/ui3/`

`doc/gui_modernization/ui4/`

`doc/gui_modernization/ui5/`

`doc/gui_modernization/ui6/`

Read the latest implementation reports, regression results and known limitations.

### Mandatory test discipline

The current reported suite contains 514 collected tests.

Do not add another large collection of repetitive regression tests.

Before writing new tests:

1. Identify existing coverage.
2. Determine whether the behavior is already protected.
3. Reuse authoritative tests.
4. Extend existing tests when practical.
5. Add tests only for newly corrected defects or proven gaps.
6. Reuse existing fixtures.
7. Avoid repeating full forensic pipelines.
8. Consolidate redundant cases where justified.

A net increase exceeding **10 collected tests** requires explicit justification.

This is a review threshold, not a mandatory target.

Do not manipulate test grouping merely to stay below the threshold.

### Validation philosophy

UI-7 should emphasize:

- Native execution.
- Manual interaction.
- Measured performance.
- Visual inspection.
- End-to-end integration.
- Targeted regression testing.

Additional unit tests are not automatically the best validation method.

---

# PART B — Establish a validation matrix

## 3. Inventory the complete GUI

Inspect all six workspaces and the existing dialogs.

### Workspaces

1. Overview.
2. Image Forensics.
3. Evidence.
4. Reasoning.
5. Provenance.
6. Reports.

### Supporting interfaces

- Analysis configuration.
- Settings.
- OSINT editors.
- File selection.
- Analysis progress.
- Errors and warnings.
- Stored investigation loading.
- Export dialogs.
- Application shutdown.

Create a validation matrix containing:

| Area | Functional | Native Windows | DPI | Performance | Accessibility | Status |
|---|---|---|---|---|---|---|

Use:

- PASS
- FAIL
- NOT TESTED
- NOT APPLICABLE

Do not mark an item PASS based solely on prior implementation reports.

Distinguish actual native execution from offscreen Qt rendering.

---

# PART C — Native Windows validation

## 4. Run the application natively

Launch SignalLens through its documented Windows development workflow.

Do not substitute offscreen Qt tests for native-window inspection.

Verify:

- Application startup.
- Initial window geometry.
- Window maximization.
- Window restoration.
- Window resizing.
- Navigation.
- Dialog focus.
- Modal behavior.
- Mouse interaction.
- Keyboard interaction.
- Application shutdown.

Where possible, validate behavior on the actual Windows desktop.

### Critical limitation

If the execution environment cannot launch a visible native Windows desktop, explicitly report:

**NATIVE WINDOWS VALIDATION NOT PERFORMED**

Continue with supported offscreen and automated checks, but do not claim native release readiness.

Do not fabricate native screenshots.

Do not claim DPI conditions were validated merely by changing Qt scale variables.

---

## 5. High-DPI validation

Test supported Windows scaling configurations where technically possible:

- 100%.
- 125%.
- 150%.

If additional scaling levels are practical, include them.

### Inspect

- Sidebar navigation.
- Header.
- Status indicators.
- Font rendering.
- Card layouts.
- Tables.
- Splitters.
- Scrollbars.
- Tooltips.
- Dialogs.
- Icons.
- Image viewers.
- Report previews.

### Image-specific verification

Check:

- Fit-to-view.
- Zoom anchoring.
- Pan behavior.
- Registered comparison.
- Synchronized zoom and pan.
- Overlay alignment.
- EXIF-oriented images.
- Crop and scaling transforms.

### Coordinate integrity

Verify that source-image, artifact-image, Qt logical and physical display coordinates are handled consistently.

Use existing deterministic registration tests to complement visual verification.

Do not alter forensic registration contracts merely to compensate for a visual layout problem.

---

# PART D — End-to-end investigative workflow

## 6. Validate complete investigations

Perform representative end-to-end user journeys.

### Workflow A — New investigation

1. Launch SignalLens.
2. Select an image.
3. Configure analysis.
4. Start analysis.
5. Monitor progress.
6. Review Overview.
7. Inspect Image Forensics.
8. Inspect supporting evidence.
9. Inspect Reasoning.
10. Inspect Provenance.
11. Add an OSINT annotation.
12. Open Reports.
13. Preview the current report.
14. Export the report.
15. Verify output files.
16. Reopen the stored investigation.

### Workflow B — Investigation replacement

1. Analyze image A.
2. Select image B.
3. Verify obsolete content is cleared.
4. Analyze image B.
5. Confirm B's results remain authoritative.

### Workflow C — Reanalysis

1. Analyze an image using one profile.
2. Reanalyze with different settings.
3. Verify correct invocation identity.
4. Verify correct results and reports.
5. Ensure older asynchronous callbacks cannot replace the active result.

### Workflow D — Failure recovery

Exercise supported failure scenarios:

- Missing image.
- Corrupt image.
- Missing detector artifact.
- Failed analysis.
- Invalid stored summary.
- Export failure.
- Missing metadata.
- Unavailable reasoning details.

The application should remain stable and should not present stale findings as current.

### Required outcome

Every workspace must consistently refer to the intended investigation.

No test should silently modify source images or saved baseline artifacts.

---

# PART E — Performance and responsiveness

## 7. Establish measurable performance baselines

Measure actual application behavior rather than relying on subjective impressions.

Use representative workloads:

### Small investigation

A modest image and minimal recorded evidence.

### Typical investigation

A realistic image with the usual detector outputs.

### Large image

A high-resolution image approaching the application's practical supported limits.

### Large reasoning trace

A recorded investigation containing many evidence and lineage entries.

### Large metadata record

Numerous fields and substantial textual metadata.

### Large report

A report containing substantial forensic detail and contextual annotations.

Prefer existing safe fixtures and stored results.

Do not create or commit unnecessarily large binary test assets.

### Measure

Where practical:

- Application startup latency.
- Time to display source-image preview.
- Workspace-navigation latency.
- Artifact-switch latency.
- Metadata filtering.
- Evidence filtering.
- Reasoning expansion.
- Report-preview generation.
- Export duration.
- GUI responsiveness during export.
- Memory usage.
- Memory behavior after switching investigations.

Use a repeatable, documented method.

Do not make up benchmark figures.

---

## 8. Identify genuine performance problems

Prioritize defects such as:

- Main-thread blocking.
- Excessive image decoding.
- Large widget-tree construction.
- Repeated parsing of unchanged results.
- Rebuilding metadata models unnecessarily.
- Unbounded preview caches.
- Memory retention after investigation switching.
- Synchronous report generation affecting UI responsiveness.

### Important

Do not refactor code solely because it appears inefficient.

Fix measured performance problems.

Before modifying an implementation:

1. Record the observed problem.
2. Identify the cause.
3. Propose the smallest safe correction.
4. Implement the correction.
5. Remeasure.
6. Verify no forensic behavior changed.

Do not optimize detector algorithms in UI-7.

---

## 9. Investigate legacy automatic report saves

UI-6 introduced background explicit exports, but legacy automatic report saving may remain synchronous.

Determine:

- Which code path performs automatic saving.
- Whether it runs on the GUI thread.
- Which formats are generated.
- Whether large reports noticeably block interaction.
- Whether output consistency is preserved.
- Whether failures are handled correctly.

### Decision rule

If no meaningful responsiveness problem is demonstrated, document the behavior and retain it.

If a real problem is demonstrated, implement a narrowly scoped correction that preserves:

- Investigation identity.
- Analysis revision.
- Annotation revision.
- Report snapshot consistency.
- Existing output formats.
- Failure reporting.

Do not introduce a second reporting system.

Do not change report semantics.

---

# PART F — Visual consistency and professional polish

## 10. Audit the completed interface

Review all six workspaces together.

Assess:

### Visual hierarchy

- Main headings.
- Primary findings.
- Secondary information.
- Technical details.
- Status indicators.

### Typography

- Consistent font families.
- Heading sizes.
- Technical labels.
- Numeric alignment.
- Readable long-form descriptions.

### Layout

- Panel alignment.
- Padding.
- Spacing.
- Splitter behavior.
- Minimum dimensions.
- Scrolling.

### Components

- Buttons.
- Navigation.
- Search fields.
- Filters.
- Tables.
- Tooltips.
- Empty states.
- Loading states.
- Error states.
- Dialogs.

### Color

- Consistent design tokens.
- Adequate contrast.
- Semantic status colors.
- Accessible focus indicators.

### Interaction

- Consistent selection behavior.
- Predictable navigation.
- Accessible controls.
- Copyable technical values.
- Clear feedback.

### Correction scope

Fix:

- Clipped controls.
- Inconsistent spacing.
- Obvious contrast issues.
- Broken focus behavior.
- Misaligned components.
- Unreadable metadata.
- Incorrect scrolling.
- Confusing status labels.

Do not redesign entire workspaces.

Do not introduce new dashboard features.

Do not replace the established design system.

---

# PART G — Accessibility and keyboard navigation

## 11. Review keyboard accessibility

Verify:

- Ctrl+1–6 workspace navigation.
- Logical tab order.
- Visible keyboard focus.
- Keyboard detector selection.
- Evidence filtering.
- Metadata filtering.
- Table navigation.
- Dialog confirmation/cancellation.
- Report export interactions.
- Escape behavior where appropriate.

### Requirements

- Controls must have accessible names where applicable.
- Icon-only actions should provide tooltips or accessible labels.
- Status must not depend only on color.
- Disabled actions should communicate their limitations.
- Important information should remain available without mouse-only interaction.

Use Qt's native accessibility capabilities where practical.

Do not introduce a new accessibility framework.

---

## 12. Review uncertainty communication

Ensure consistent representation of:

- High/Medium/Low confidence.
- Inconclusive findings.
- Unverified provenance.
- Missing provenance.
- Unavailable evidence.
- Rejected detector results.
- Contextual OSINT.
- Historical/legacy data.

### Critical rules

- Suspicious scores are not AI probabilities.
- High confidence is not mathematical certainty.
- Camera-like evidence is not proof of photographic authenticity.
- Localized editing does not automatically imply synthetic origin.
- Metadata presence does not prove cryptographic verification.
- Missing evidence is not negative evidence.

UI-7 may correct misleading labels or presentation wording.

Do not rewrite authoritative forensic findings or confidence rules.

---

# PART H — Stability and lifecycle testing

## 13. Verify asynchronous behavior

Review the UI-1 through UI-6 lifecycle safeguards.

Validate:

- Worker completion after navigation.
- Image selection during processing.
- Artifact selection during asynchronous loading.
- Report export during investigation switching.
- OSINT editing during navigation.
- Stored-result loading during active investigation.
- Application shutdown with active workers.
- Missing files during asynchronous operations.

### Important

Existing logical cancellation does not guarantee termination of a stuck backend.

Document whether shutdown remains blocked by genuinely nonterminating workers.

Do not introduce unsafe thread termination.

If a serious shutdown issue is reproducible, implement the smallest safe correction that fits the existing threading model.

Do not redesign the worker architecture.

---

# PART I — Packaged Windows application

## 14. Inspect packaging configuration

Identify the existing packaging or distribution method.

Examples may include:

- PyInstaller.
- Existing build scripts.
- Application spec files.
- Windows resources.
- Bundled Qt plugins.
- Model assets.
- ExifTool dependencies.

Do not assume a particular build tool.

### Validate packaging where possible

If the existing build process is available:

1. Build an application artifact using the documented process.
2. Verify required resources are included.
3. Launch the packaged application.
4. Verify all six workspaces.
5. Open an image.
6. Verify analysis dependencies.
7. Inspect existing results.
8. Verify reporting.
9. Verify controlled shutdown.

### Important

Do not publish or distribute the build.

Do not add or upgrade dependencies.

Do not change package metadata or version numbers.

If packaging cannot be executed, document the blocker rather than modifying build scripts speculatively.

### Acceptance

A source-code test suite passing does not establish packaged-application correctness.

Report source execution and packaged execution separately.

---

# PART J — Regression testing and test discipline

## 15. Reuse existing coverage

The reported baseline contains 514 tests.

Before adding any new test, consult:

`doc/test_quality/behavioral_coverage_matrix.md`

### Prefer existing coverage for

- Forensic scores.
- Hypothesis selection.
- Confidence policy.
- Evidence lineage.
- Session identity.
- Worker callback guards.
- Annotation revisions.
- Report snapshots.
- Artifact registration.
- Cross-workspace navigation.

Do not duplicate these tests.

### Add a test only when

- A reproducible defect was corrected.
- A genuinely untested safety-critical behavior was discovered.
- A changed interface introduced new behavior requiring protection.
- Existing coverage demonstrably cannot detect the regression.

### Required accounting

| Test accounting | Count |
|---|---:|
| Baseline collected | |
| New tests | |
| Consolidated | |
| Removed | |
| Final collected | |
| Net change | |

A net increase exceeding ten collected cases requires explicit justification.

Avoid adding tests for purely visual adjustments unless those tests protect stable, meaningful behavior.

---

## 16. Full regression validation

After the final corrections:

1. Run targeted tests.
2. Run the full suite once for final acceptance.
3. Record collected, passed, failed and skipped counts.
4. Record warnings.
5. Record execution duration.
6. Confirm forensic calculations remain unchanged.
7. Confirm persistence and export compatibility.

Do not equate a green suite with successful native Windows validation.

Both are required for a full release-readiness claim.

---

# PART K — Reference investigations

## 17. Validate the two established reference cases

Use existing stored runs where possible.

Current `normal`-profile reference values:

| Reference | Suspicious | Benign | Primary finding |
|---|---:|---:|---|
| Instagram | 21.32705 | 2.25 | High localized editing |
| Midjourney | 6.675 | 1.5 | Medium unverified synthetic context |

For each reference:

- Confirm source hash.
- Confirm analysis profile.
- Confirm primary hypothesis.
- Confirm confidence.
- Confirm score values.
- Inspect Overview.
- Inspect Image Forensics.
- Inspect Evidence.
- Inspect Reasoning.
- Inspect Provenance.
- Preview and export a report.

### Important

These numerical values are specific to the recorded `normal`-profile runs.

Do not compare them against historical `subject_based` results without accounting for configuration differences.

Do not modify scoring to force equality.

Do not repeatedly run full detector pipelines when existing validated result fixtures suffice.

---

# PART L — Release-readiness audit

## 18. Define severity and acceptance rules

Classify identified issues:

### Critical

- Incorrect investigation identity.
- Stale result shown as current.
- Incorrect exported findings.
- Corrupted forensic result.
- Uncontrolled application crash.
- Unsafe or incorrect coordinate registration.

### High

- Major workspace unusable.
- Report export consistently fails.
- Analysis workflow blocked.
- Serious native DPI interaction failure.
- Significant main-thread freezes under supported workloads.

### Medium

- Important control clipping.
- Broken keyboard navigation.
- Persistent layout errors.
- Moderate performance degradation.
- Confusing but noncritical presentation.

### Low

- Minor spacing.
- Cosmetic inconsistency.
- Nonessential tooltip issue.

### Release rules

**PASS**

No unresolved Critical or High issues, and required validation has actually been performed.

**CONDITIONAL PASS**

No known Critical or High defects, but a material validation limitation remains.

**FAIL**

One or more Critical or High defects remain unresolved.

Do not issue full PASS if native Windows or packaged application validation was required but could not be performed.

Document limitations precisely.

---

# PART M — Documentation and deliverables

## 19. Required documentation

Create:

`doc/gui_modernization/ui7/`

With:

### A. `validation_matrix.md`

Complete workspace, native-platform, DPI, accessibility and performance coverage.

### B. `native_windows_validation.md`

Actual native Windows results, scaling configurations, screenshots and limitations.

### C. `end_to_end_workflows.md`

Recorded complete user journeys and their outcomes.

### D. `performance_baseline.md`

Measured timings, memory observations, methodology and reproducibility notes.

### E. `visual_polish_audit.md`

Visual defects identified, changes made and unresolved issues.

### F. `accessibility_review.md`

Keyboard, focus, labeling, contrast and navigation results.

### G. `packaging_validation.md`

Build configuration, build/launch results, included resources and limitations.

### H. `defect_register.md`

Each finding with:

- Identifier.
- Severity.
- Reproduction steps.
- Affected module.
- Root cause where established.
- Correction.
- Validation evidence.
- Current status.

### I. `implementation_report.md`

Changed modules, exact correction scope and compatibility.

### J. `regression_results.md`

Baseline/final tests, coverage reuse, net change and reference outcomes.

### K. `release_readiness.md`

Final verdict:

- PASS.
- CONDITIONAL PASS.
- FAIL.

Include blocking issues and remaining limitations.

---

## 20. Screenshots and diagnostic artifacts

Save screenshots under:

`doc/gui_modernization/ui7/screenshots/`

Capture:

- Main window.
- All six workspaces.
- Normal window.
- Maximized window.
- Minimum supported window.
- Representative dialogs.
- Large metadata.
- Large reasoning trace.
- Report preview.
- Image comparison.
- Error and unavailable states.

Include DPI-specific captures where actually tested.

Keep large generated artifacts and temporary benchmarks outside Git unless they are small, deliberate documentation fixtures.

Do not commit diagnostic outputs automatically.

---

# PART N — Final acceptance criteria

## 21. UI-7 Definition of Done

UI-7 is complete when:

1. All six workspaces have been reviewed as one application.
2. Critical user journeys have been exercised.
3. Native Windows behavior has been validated where technically available.
4. High-DPI rendering and interactions have been tested where technically possible.
5. Image registration and overlay behavior remain correct.
6. Keyboard navigation and focus behavior have been checked.
7. Large-investigation performance has been measured.
8. Report-preview and export consistency is preserved.
9. Existing session safeguards remain operational.
10. Major visual inconsistencies have been corrected.
11. Packaging has been validated where possible.
12. Existing forensic scores, hypotheses and confidence remain unchanged.
13. Existing regression coverage is preserved.
14. New tests comply with mandatory test discipline.
15. All observed defects have documented severity and disposition.
16. The final release-readiness verdict is evidence-based.
17. No unrelated feature development has occurred.
18. Inherited Git changes remain preserved.

---

## 22. Final Codex response

Return:

**A. Baseline**

Branch, HEAD, Git status, Python/PyQt6 versions and starting test count.

**B. Native Windows**

Actual native checks completed, including DPI scales.

**C. End-to-end workflows**

Completed scenarios and failures.

**D. Performance**

Measured timings, memory and main-thread responsiveness.

**E. Visual polish**

Corrections made and remaining issues.

**F. Accessibility**

Keyboard, focus and interaction findings.

**G. Packaging**

Build and packaged-launch status.

**H. Test discipline**

Added, consolidated, removed and final test counts.

**I. Reference cases**

Instagram/Midjourney scores, findings and confidence.

**J. Defects**

Critical/High/Medium/Low findings and current status.

**K. Git preservation**

Changed and untracked files; confirmation that no stage, commit, push or merge occurred.

**L. Release readiness**

PASS, CONDITIONAL PASS or FAIL, with precise justification.

---

## Strict constraints

- Do not modify forensic detector algorithms.
- Do not change scoring coefficients.
- Do not change hypothesis selection.
- Do not change confidence-policy rules.
- Do not alter evidence lineage.
- Do not modify provenance verification semantics.
- Do not add new forensic detectors.
- Do not implement new C2PA or watermark verification.
- Do not redesign existing workspaces.
- Do not introduce new GUI features.
- Do not upgrade dependencies.
- Do not alter supported report formats.
- Do not publish or distribute builds.
- Do not stage, commit, push, merge, tag, reset or stash.
- Preserve inherited modifications and excluded test assets.

**Core principle: SignalLens must not merely look professional. It must behave reliably, preserve forensic evidence integrity, remain responsive under realistic workloads and present uncertainty accurately throughout the investigation.**

Complete UI-7, correct demonstrated defects within scope, validate the application and deliver an evidence-based release-readiness verdict. Do not start another modernization phase.
