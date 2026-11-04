# CODEX TASK — SignalLens UI-2: Visual Design System & Workspace Shell

## Mission

You are the principal PyQt6 desktop architect, senior Python engineer, UI/UX design lead and software quality specialist for SignalLens.

Your task is to implement **UI-2 — Visual Design System & Workspace Shell**, the second implementation phase of SignalLens's GUI modernization.

The objective is to transform SignalLens from its traditional utility-style interface into the foundation of a professional forensic investigation workspace.

SignalLens now contains a substantially modernized reasoning engine with:

- Separate synthetic-origin, localized-editing and camera-acquisition hypotheses.
- Structured supporting, contradicting and moderating evidence.
- Auditable mathematical scorecards.
- Evidence lineage and corroboration controls.
- Centralized confidence assignment.
- Explicit provenance limitations.
- Reliable handling of unavailable forensic measurements.

UI-1 introduced:

- Investigation-session identity.
- Analysis-invocation identity.
- Guarded worker callbacks.
- Session lifecycle transitions.
- Frozen analysis configuration.
- Source-file identity checks.
- Annotation revisions.
- Consistent report snapshots.
- Immutable presentation contracts.

**UI-2 must create a modern visual framework around these capabilities without changing their forensic meaning or existing behavior.**

The desired result is a refined, professional desktop workspace combining the analytical density of established forensic tools with the clarity of contemporary data applications.

This is not a web application.

Retain Python 3.13 and PyQt6.

---

# Part A — Baseline and prerequisite verification

## 1. Inspect the repository

Project:

`D:\Coding\SignalLens`

Last reported state:

- Branch: `main`
- HEAD: `00c5eb2`
- UI-1 implemented but not committed.
- 378 regression tests passing.
- Existing modifications preserved.
- No UI-2 implementation yet.

Verify actual branch, HEAD, working-tree state and test count.

Do not assume earlier changes were committed.

### Read before editing

Study:

`doc/gui_modernization/audit/`

Especially:

- `executive_summary.md`
- `gui_architecture_inventory.md`
- `visual_design_audit.md`
- `reasoning_visibility_matrix.md`
- `gui_architecture_recommendation.md`
- `signal_lens_design_concept.md`
- `modernization_roadmap.md`
- `wireframes/index.html`

Also study:

`doc/gui_modernization/ui1/`

Especially:

- `session_lifecycle_specification.md`
- `presentation_contracts.md`
- `implementation_report.md`
- `osint_report_consistency.md`
- `regression_results.md`

Inspect the current implementation of:

- `signallens_gui.py`
- Settings and OSINT dialogs.
- Worker/controller integration.
- Investigation-session modules.
- Presentation-model modules.
- Existing stylesheets and assets.
- Current result-summary and detector visualization widgets.

Do not implement a design based solely on conceptual wireframes.

Use the actual application structure and current Qt behavior.

---

## 2. Verify the UI-1 foundation

Before making GUI changes, confirm:

- Session identity remains authoritative.
- Worker callbacks are invocation-guarded.
- Existing GUI components consume the active investigation state.
- OSINT edits maintain report consistency.
- Presentation contracts do not recalculate forensic findings.
- Stored-summary loading remains operational.

Run the existing tests.

Record the result.

If you discover a critical UI-1 defect that makes UI-2 unsafe, document it and stop the affected integration work rather than silently rewriting the architecture.

### Historical scoring discrepancy

The UI-1 report measured the following reference scores:

| Reference | Earlier reasoning baseline | UI-1 measured baseline |
|---|---:|---:|
| Instagram suspicious | 20.47705 | 21.32705 |
| Midjourney suspicious | 5.40000 | 6.67500 |

UI-1 reportedly produced identical before/after measurements.

Perform a **bounded read-only baseline comparison** of the discrepancy before UI-2 implementation.

Inspect:

- Repository revisions.
- Analysis configuration.
- Analysis profile.
- Source-file hashes.
- Input normalization.
- Detector availability.
- Scoring contribution ledgers.
- Relevant saved result traces.

Determine whether the differences are explained by configuration, source revision, execution environment or another identifiable factor.

Do not modify the reasoning engine or tune scores.

If the discrepancy cannot be resolved from available evidence, document it explicitly and preserve the current measured baseline.

Do not invent a root cause.

The comparison must not turn UI-2 into a forensic scoring project.

---

## 3. Preserve existing work

The repository may contain uncommitted UI-1 and UI-0 work.

Before editing:

1. Record the existing Git status.
2. Identify inherited modifications.
3. Record files already changed by earlier work.
4. Keep UI-2 edits separately reviewable.
5. Preserve existing documentation and artifacts.

Do not:

- Stage files.
- Commit.
- Push.
- Merge.
- Tag.
- Reset.
- Stash.
- Discard inherited changes.

Keep test images and generated forensic outputs outside Git.

Do not delete or reorganize existing research assets.

---

# Part B — Design objectives

## 4. Establish the SignalLens visual identity

Create a coherent design language suitable for a specialist forensic application.

The interface should communicate:

- Precision.
- Reliability.
- Technical sophistication.
- Transparency.
- Professional restraint.
- Investigative control.

Avoid generic consumer-app styling.

Avoid decorative analytics that imply statistical precision the system does not possess.

### Preferred direction

**Dark-first forensic workspace**

Use:

- Neutral charcoal or graphite surfaces.
- Subtle tonal differences between panels.
- Restrained blue/cyan accent colors.
- Clear, accessible text hierarchy.
- Fine but visible borders.
- Moderate corner radii.
- Consistent spacing.
- Limited animation.
- Clear selection and focus states.

The objective is not to imitate a cinematic hacking interface.

SignalLens should resemble a serious scientific or investigative desktop tool.

### Important

Implement the design system through centralized tokens.

Do not scatter arbitrary colors, fonts and margins through individual widgets.

---

# Part C — Visual design system

## 5. Implement centralized design tokens

Introduce a dedicated design-system module or similarly maintainable structure.

For example:

`gui/design_system.py`

Adapt filenames and package layout to existing conventions.

Define tokens for:

### Color

- Application background.
- Navigation background.
- Primary panel background.
- Secondary panel background.
- Elevated surface.
- Borders.
- Dividers.
- Primary text.
- Secondary text.
- Disabled text.
- Accent.
- Hover.
- Selected.
- Focus.
- Success.
- Warning.
- Error.
- Neutral/unknown.
- Unavailable.

### Typography

- Primary UI font.
- Monospace font.
- Display heading.
- Section heading.
- Card heading.
- Body text.
- Secondary text.
- Caption.
- Technical metadata.

### Spacing

Use a consistent spacing scale.

Suggested base:

- 4 px.
- 8 px.
- 12 px.
- 16 px.
- 24 px.
- 32 px.

Adapt where required for Windows high-DPI behavior.

### Geometry

- Corner radius.
- Standard control height.
- Navigation width.
- Panel padding.
- Icon size.
- Border width.
- Minimum content dimensions.

### Design constraints

- Avoid hardcoded styling in business-logic modules.
- Avoid repeated stylesheet fragments.
- Support future light-theme implementation without architectural changes.
- Keep colors semantic rather than bound to particular forensic outcomes.

---

## 6. Build reusable GUI components

Implement a small library of reusable PyQt6 widgets.

Prioritize components required by UI-2 and later phases.

Suggested components:

### A. Section header

Supports:

- Heading.
- Description.
- Optional actions.
- Optional status text.

### B. Panel/card container

Supports:

- Standard padding.
- Consistent background.
- Optional title.
- Optional toolbar.
- Clear content boundaries.

### C. Status indicator

Supports:

- Pending.
- Analyzing.
- Completed.
- Failed.
- Cancelled.
- Unavailable.
- Unknown.

Do not confuse lifecycle status with forensic confidence.

### D. Confidence indicator

Supports:

- High.
- Medium.
- Low.
- Inconclusive.
- Unavailable.

Must display the actual authoritative confidence tier.

Do not convert tiers to percentages.

Do not use red/green as a binary AI-authenticity classification.

### E. Empty-state component

Supports:

- No image loaded.
- No analysis result.
- Analysis in progress.
- No evidence available.
- Result unavailable.
- Error state.

### F. Navigation item

Supports:

- Icon.
- Label.
- Active state.
- Hover/focus state.
- Optional notification/status marker.

### G. Metadata label/value row

Supports readable technical values and copyable information.

### H. Collapsible technical section

Provides progressive disclosure for dense forensic details.

### Requirements

- Reuse existing Qt capabilities.
- Avoid introducing unnecessary dependencies.
- Use consistent interaction states.
- Support keyboard focus.
- Support high-DPI rendering.
- Preserve accessibility.
- Keep components independent from detector-specific code.

Do not build large speculative component frameworks.

Implement only what this phase or its immediate successors require.

---

# Part D — Application workspace shell

## 7. Introduce a modern main-window layout

Create a professional workspace shell around the existing application.

Suggested structure:

```text
┌──────────────────────────────────────────────────────────────┐
│ SignalLens                                    Status / Tools │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│  Overview     │                                              │
│               │                                              │
│  Image        │            Active Workspace                  │
│  Forensics    │                                              │
│               │                                              │
│  Evidence     │                                              │
│               │                                              │
│  Reasoning    │                                              │
│               │                                              │
│  Provenance   │                                              │
│               │                                              │
│  Reports      │                                              │
│               │                                              │
├───────────────┴──────────────────────────────────────────────┤
│ Session status · Image · Analysis state · Version            │
└──────────────────────────────────────────────────────────────┘
```

This is a conceptual layout, not an exact pixel specification.

Use the UI-0 design concept and wireframes as the primary design references.

### Preferred implementation

Use Qt-native components such as:

- `QMainWindow`
- `QWidget`
- `QStackedWidget`
- `QSplitter`
- `QScrollArea`
- `QVBoxLayout`
- `QHBoxLayout`

Choose components based on actual resizing and state requirements.

Do not use a web-rendering framework to build the main application shell.

---

## 8. Implement navigation

Introduce six main workspace destinations:

1. Overview
2. Image Forensics
3. Evidence
4. Reasoning
5. Provenance
6. Reports

### Requirements

- Clearly identifiable active destination.
- Consistent navigation across investigation states.
- Keyboard-accessible navigation.
- Stable layout when switching destinations.
- No duplicate investigation state.
- No independent forensic calculations.
- Navigation must not start analysis or mutate results.
- No stale-result leakage between sessions.
- Preserve current analysis configuration access.

### Scope control

Do not implement the complete content of these six workspaces yet.

Create their navigational structure and appropriate initial content.

Existing functionality should remain accessible through integration or temporary legacy panels.

Do not replace working functionality with empty placeholders that make it inaccessible.

---

## 9. Preserve the existing forensic workflow

The current application must remain usable throughout the modernization.

The following must continue to work:

- Selecting images.
- Configuring analysis.
- Starting analysis.
- Monitoring progress.
- Reviewing current summary.
- Accessing detector results.
- Viewing metadata.
- Editing OSINT information.
- Saving and exporting reports.
- Loading stored summaries.
- Handling failures.

### Transitional integration

Where the new workspace lacks a completed replacement view, provide access to the existing functional UI.

Possible approaches:

- Embed the existing widget within the relevant workspace.
- Provide a dedicated legacy-detail panel.
- Preserve an accessible dialog.
- Reuse current widgets inside new containers.

Do not duplicate the existing analysis engine or create parallel controllers.

Avoid constructing multiple live instances of stateful legacy widgets if they could diverge.

Document every temporarily retained legacy component and its intended migration phase.

---

# Part E — Layout and resizing

## 10. Implement professional desktop resizing behavior

The application should support:

- Normal window mode.
- Maximized mode.
- Reasonable minimum window dimensions.
- Resizable content panels.
- Persistent navigation visibility.
- Proper scrolling for lengthy results.
- Consistent margins.
- Adaptive content layouts where practical.

### Avoid

- Fixed-size main layouts.
- Clipped buttons.
- Overlapping labels.
- Unusable image previews.
- Excessive nested scrolling.
- Horizontally overflowing summary text.
- Dialogs that require unnecessarily large displays.

### Splitters

Use `QSplitter` where resizable panels materially improve usability.

Preserve splitter state when appropriate.

Do not overuse nested splitters.

### Window persistence

Where compatible with the existing settings architecture, persist:

- Window geometry.
- Maximized state.
- Navigation width.
- Relevant splitter sizes.
- Last selected workspace destination.

Do not persist sensitive forensic image contents in GUI settings.

Validate restored geometry against the available screen configuration to avoid reopening the application entirely off-screen.

---

# Part F — Investigation-session integration

## 11. Connect the workspace shell to UI-1

The shell must consume the authoritative session lifecycle.

At minimum, display:

- Current image name.
- Investigation state.
- Analysis progress where available.
- Active session identity or shortened identifier where useful.
- Current result availability.
- Clear indication when no completed result exists.

### Important

Do not create another independent session-state model.

Do not store duplicated forensic results inside navigation widgets.

Use the existing UI-1 session/presentation contracts.

When investigation state changes:

- The shell status updates.
- Relevant workspace views receive the active snapshot.
- Obsolete snapshots cannot appear as current results.
- Empty-state components update consistently.
- Navigation remains functional.

Do not loosen UI-1's stale-callback guards.

---

## 12. Represent forensic uncertainty correctly

The interface should distinguish:

### Investigation lifecycle

- Running.
- Completed.
- Failed.
- Cancelled.
- Unavailable.

### Forensic confidence

- High.
- Medium.
- Low.
- Inconclusive.

### Provenance verification

- Verified.
- Unverified.
- Not present.
- Unknown.

### Evidence availability

- Available.
- Unavailable.
- Rejected due to reliability.
- Not applicable.

Do not use one generic color or status badge to represent all these concepts.

A completed analysis may still produce an inconclusive finding.

A suspicious forensic score does not automatically establish AI generation.

A camera-compatible signal does not prove authenticity.

A missing watermark or absent metadata does not establish human origin.

Ensure these distinctions are maintained in reusable components.

---

# Part G — Initial workspace content

## 13. Overview shell

Implement only the structural foundation.

It should contain regions reserved for:

- Investigation header.
- Source-image preview.
- Primary forensic finding.
- Hypothesis summaries.
- Supporting evidence summary.
- Limitations.
- Analysis status.

Where possible, reuse current presentation data to display an accurate minimal summary.

Do not implement the complete UI-3 investigation dashboard.

Do not introduce new scoring visualizations.

---

## 14. Image Forensics shell

Provide:

- Workspace heading.
- Access to existing detector results.
- Appropriate content container.
- Empty state when no analysis exists.

Reserve space for later synchronized source/detector comparison.

Do not implement advanced zoom synchronization, overlays or region selection in UI-2.

---

## 15. Evidence shell

Provide:

- Workspace heading.
- Existing evidence content where available.
- Structured presentation-model access.
- Explicit empty/unavailable state.

Do not build the full Evidence Explorer yet.

Do not introduce new evidence classifications.

---

## 16. Reasoning shell

Provide:

- Workspace heading.
- Access to existing decision trace and reasoning summaries.
- Proper handling when structured reasoning is unavailable.

Do not implement the complete reasoning graph or evidence-lineage explorer.

---

## 17. Provenance shell

Provide:

- Workspace heading.
- Existing metadata/provenance access.
- Correct distinction between metadata declarations and verification.

Do not implement new C2PA or watermark verification capabilities.

---

## 18. Reports shell

Provide:

- Workspace heading.
- Access to existing report/export functionality.
- Current report validity state where available.

Use UI-1's report-snapshot guarantees.

Do not redesign report contents in this phase.

---

# Part H — Existing dialogs and compatibility

## 19. Apply the design system consistently

Where safe, apply the new typography, spacing and colors to:

- Main window.
- Settings dialog.
- OSINT dialogs.
- Progress indicators.
- Existing report interactions.
- Error dialogs.

Do not redesign the workflows within these dialogs.

If styling an existing dialog produces regressions, document the issue and retain the existing styling until a focused migration phase.

### Platform compatibility

Preserve:

- Windows native dialog behavior.
- File pickers.
- Modal-dialog semantics.
- Keyboard focus.
- Context menus.
- Copy/paste behavior.
- Existing shortcuts.

Avoid global Qt stylesheet rules that unexpectedly break child widgets.

---

# Part I — Testing

## 20. Preserve all current regression tests

The latest reported baseline contains 378 passing tests.

Run the existing suite before and after implementation.

Add targeted tests for:

### Design system

- Token availability.
- Theme application.
- Semantic status mapping.
- Confidence label mapping.
- Component creation.
- Disabled/hover/focus behavior where testable.

### Navigation

- All six destinations exist.
- Active destination updates.
- Navigation does not mutate investigation state.
- Switching destinations preserves the active result.
- Unavailable content has a meaningful empty state.

### Session integration

- New image selection clears outdated presentation.
- Analysis progress updates shell status.
- Completed results populate the correct session.
- Obsolete callbacks remain ineffective.
- Loading stored results updates the shell.
- Annotation revisions do not silently alter forensic findings.

### Layout

- Window can be resized.
- Content does not disappear at supported minimum size.
- Splitter state is preserved where implemented.
- Window geometry can be restored.
- Invalid/off-screen geometry falls back safely.

### Compatibility

- Existing analysis controls remain accessible.
- Settings dialog opens.
- OSINT dialog opens.
- Existing detector views remain accessible.
- Report export remains accessible.
- Current reasoning summaries remain visible.

Prefer deterministic Qt tests.

Do not introduce screenshot-based pixel-perfect assertions unless a stable and portable testing method already exists.

---

# Part J — Visual validation

## 21. Inspect the actual application

Run the modified GUI where the environment supports it.

Capture screenshots of:

1. Empty Overview.
2. Image selected.
3. Analysis running.
4. Completed Overview.
5. Image Forensics shell.
6. Evidence shell.
7. Reasoning shell.
8. Provenance shell.
9. Reports shell.
10. Settings or OSINT dialog.

Where possible, inspect:

- Normal window mode.
- Maximized mode.
- Minimum supported size.
- Windows native rendering.
- Different DPI scaling settings.

If only offscreen Qt testing is available, state that explicitly.

Do not claim native Windows/DPI verification without performing it.

### Visual acceptance checks

- Consistent spacing.
- Clear typography hierarchy.
- Legible labels.
- Adequate contrast.
- No clipped controls.
- No overlapping text.
- Proper empty states.
- Clearly selected navigation destination.
- Proper progress/status representation.
- No decorative percentages or misleading confidence visuals.

Save screenshots under:

`doc/gui_modernization/ui2/screenshots/`

Do not commit generated screenshots automatically.

---

# Part K — Documentation

## 22. Required deliverables

Create:

`doc/gui_modernization/ui2/`

### A. `design_system_specification.md`

Document:

- Color tokens.
- Typography.
- Spacing.
- Geometry.
- Component styles.
- Status semantics.
- Accessibility principles.
- Future light-theme considerations.

### B. `workspace_architecture.md`

Document:

- Main-window structure.
- Navigation.
- Workspace containers.
- Session binding.
- Reused legacy widgets.
- Future migration points.

Include a component diagram.

### C. `component_inventory.md`

List all new reusable UI components and their responsibilities.

### D. `legacy_migration_map.md`

For each existing GUI component:

- Current location.
- UI-2 location.
- Reuse strategy.
- Relevant future UI phase.
- Known compatibility concerns.

### E. `visual_validation.md`

Report:

- Screens inspected.
- Screenshot paths.
- Window sizes.
- DPI conditions.
- Visual issues discovered and corrected.
- Remaining unverified platform behavior.

### F. `implementation_report.md`

Summarize:

- New files.
- Modified files.
- Architectural choices.
- Behavior preserved.
- Known limitations.
- Deviations from original plan.

### G. `regression_results.md`

Include:

- Baseline tests.
- Final tests.
- New tests.
- GUI tests.
- Reference-image behavior.
- Any skipped validation.

### H. `score_baseline_diagnostic.md`

Document the bounded investigation into historical reference-score discrepancies.

Separate verified facts from hypotheses.

Do not alter scoring or reference configurations to force agreement.

---

# Part L — Final acceptance criteria

## 23. UI-2 Definition of Done

UI-2 is complete when:

1. A centralized SignalLens design system exists.
2. Main-window styling is consistent and professional.
3. Six workspace destinations are implemented.
4. Navigation is functional and keyboard accessible.
5. The application shell is resizable.
6. Supported window geometry and layout state can be restored.
7. The shell consumes the authoritative UI-1 investigation state.
8. Obsolete results cannot appear as current content.
9. Existing analysis controls remain accessible.
10. Existing detector results remain accessible.
11. Existing reasoning and metadata views remain accessible.
12. Existing OSINT and report workflows remain functional.
13. Confidence and forensic uncertainty are represented accurately.
14. Existing regression tests pass.
15. UI-specific regression tests pass.
16. Visual screenshots and validation notes are produced.
17. Production forensic behavior remains unchanged.
18. Existing repository changes remain preserved.

---

## 24. Final Codex report

Return the following.

**A. Baseline**

Branch, HEAD, inherited Git changes and starting tests.

**B. Score diagnostic**

Explanation of the reference-score discrepancy, or explicit unresolved status.

**C. Design system**

Implemented tokens, typography, colors and reusable components.

**D. Workspace architecture**

Main-window structure, navigation and session integration.

**E. Legacy compatibility**

Which existing functions remain accessible and how.

**F. Visual validation**

Screenshots, window sizes, platform and DPI conditions.

**G. Tests**

Exact before/after counts, failures and skips.

**H. Known limitations**

Unverified behaviors, styling issues, migration risks or platform-specific concerns.

**I. Git status**

Changed and untracked files; confirmation that nothing was staged, committed or pushed.

**J. Next phase readiness**

Whether UI-3 can safely begin, and any blocking issues.

---

## Strict constraints

- Do not change forensic detector algorithms.
- Do not change scoring coefficients.
- Do not change the reasoning engine.
- Do not change confidence rules.
- Do not modify evidence-lineage logic.
- Do not alter provenance interpretation.
- Do not weaken UI-1 session safeguards.
- Do not replace PyQt6.
- Do not introduce unnecessary dependencies.
- Do not build the complete UI-3 Overview.
- Do not build advanced image comparison yet.
- Do not build the full Evidence Explorer yet.
- Do not redesign report contents.
- Do not stage, commit, push, merge, tag, reset or stash.
- Preserve all inherited modifications.

**Core principle: Build a professional forensic investigation workspace that presents the existing reasoning engine clearly, without creating new sources of truth or disrupting established forensic functionality.**

Complete UI-2, validate the new application shell and report the results. Do not begin UI-3.
