# CODEX TASK — SignalLens GUI Modernization, Phase UI-0: Architecture & Design Audit

## Mission

You are the principal desktop application architect, senior PyQt6 engineer, forensic-software UX specialist and product design lead for SignalLens.

SignalLens recently completed a major modernization of its forensic reasoning engine, correcting ten previously identified deficiencies in hypothesis assessment, provenance interpretation, evidence aggregation, numerical consistency and confidence assignment.

The resulting application now has a more sophisticated forensic reasoning architecture than the original graphical interface was designed to present.

**Your task is to audit the current GUI and design a practical modernization strategy for a professional forensic investigation workspace.**

The desired direction is a modern interpretation of the traditional analytical dashboard, retaining the depth of a specialist Windows desktop application while improving visual clarity, navigation, information hierarchy and investigative usability.

This is an **inspection and design phase only**.

Do not implement the redesign.

---

## 1. Repository and baseline

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Windows desktop application
- Existing forensic analysis pipeline
- Existing hypothesis-aware reasoning engine
- Structured scorecard and reasoning traces

Reported Git baseline:

- Branch: `main`
- Reasoning-engine commit: `564c0ee`
- Documentation commit: `24705fe`
- 334 passing regression tests
- Clean working tree
- Changes committed locally, not necessarily pushed

Verify the actual repository state before starting.

The application already includes extensive forensic analysis capabilities. The modernization must preserve their availability and functionality.

### Strict repository protection

Do not:

- Modify production code.
- Modify existing tests.
- Refactor UI modules.
- Change dependencies.
- Stage or commit files.
- Push to GitHub.
- Merge branches.
- Reset or stash changes.
- Delete or reorganize existing assets.
- Modify the reasoning engine.

You may create documentation, audit scripts and screenshots in the designated audit-output directory.

All other work is read-only.

---

# Part A — Current GUI inventory

## 2. Map the complete interface architecture

Inspect all GUI-related Python modules, layouts, stylesheets, resources and application controllers.

Identify:

- Main window and application initialization.
- Navigation structure.
- Tabs and sub-tabs.
- Dockable or resizable panels.
- Analysis configuration controls.
- Source-image display.
- Detector-specific visualizations.
- Results and summary panels.
- Reasoning and confidence presentation.
- Metadata and provenance views.
- Progress indicators.
- Error and unavailable-result states.
- Report and export functionality.
- Settings and preferences.
- Keyboard shortcuts.
- Persistent GUI state.

Produce a comprehensive component inventory.

For every substantial GUI component, record:

| Field | Description |
|---|---|
| Component | Class or widget name |
| Source | Python file |
| Parent | Containing window or widget |
| Responsibility | Primary user-facing function |
| Data source | Controller, model or analysis result |
| Dependencies | Other GUI or backend modules |
| State handling | Local, shared or persisted |
| Visual issues | Layout, density, styling |
| Architectural issues | Coupling, duplication, ownership |
| Recommended action | Retain, refine, redesign or replace |

Do not assume conventional Qt class names. Inspect the actual implementation.

---

## 3. Document the current user journey

Reconstruct the real workflow from application launch to completed forensic report.

At minimum, examine:

1. Starting the application.
2. Loading or selecting an image.
3. Selecting analysis settings.
4. Initiating analysis.
5. Monitoring processing progress.
6. Reviewing the primary conclusion.
7. Inspecting individual forensic detectors.
8. Comparing source and analysis images.
9. Understanding supporting and contradicting evidence.
10. Inspecting metadata and provenance.
11. Reviewing uncertainty and limitations.
12. Accessing technical reasoning details.
13. Exporting or saving results.
14. Starting another investigation.

For each step, assess:

- Number of interactions.
- Navigation complexity.
- Information discoverability.
- Cognitive load.
- Feedback quality.
- Consistency with other screens.
- Whether the user must remember information from another view.
- Whether important information is hidden.
- Whether too much technical information is displayed prematurely.

Distinguish observations directly supported by GUI inspection from inferred usability risks.

Do not invent functionality or user interactions that are not implemented.

---

# Part B — Visual inspection

## 4. Run and inspect the actual application

Where the execution environment supports it:

1. Launch SignalLens using its documented local workflow.
2. Inspect the interface at its normal initial size.
3. Inspect it maximized.
4. Review different analysis-result screens.
5. Inspect the current dark/light theme behavior, if applicable.
6. Inspect scrolling, resizing and splitter behavior.
7. Observe image scaling and visualization quality.
8. Inspect long text and large evidence tables.
9. Inspect empty, loading and error states.

Use existing sample data or stored analysis results where possible.

If real-image analysis is required, use existing fixtures read-only.

**Do not modify test images or generated forensic results.**

### Screenshots

Capture screenshots of the current interface where technically possible.

Include:

- Main window.
- Initial/empty state.
- Image loaded.
- Analysis configuration.
- Analysis progress.
- Completed summary.
- Individual detector views.
- Reasoning details.
- Metadata/provenance.
- Export or reporting interface.

Save screenshots under:

`doc/gui_modernization/audit/screenshots/`

Use descriptive filenames.

If GUI execution or screenshot capture is unavailable, document the limitation. Do not fabricate screenshots or claim visual inspection occurred.

---

## 5. Evaluate the visual design

Assess the current interface against professional desktop-software standards.

### Layout

- Alignment and spacing.
- Panel proportions.
- Resizing behavior.
- Consistency of margins.
- Content density.
- Scroll behavior.
- Image viewing area.
- Navigation placement.

### Typography

- Font hierarchy.
- Headings.
- Label readability.
- Technical identifiers.
- Numerical alignment.
- Long-form explanatory text.
- Consistency across controls.

### Color

- Surface/background hierarchy.
- Semantic color usage.
- Contrast.
- Status visibility.
- Consistency.
- Accessibility.

### Components

- Buttons.
- Tabs.
- Tables.
- Cards.
- Tooltips.
- Progress indicators.
- Expandable panels.
- Dialogs.
- Charts.
- Image viewers.
- Evidence indicators.

### Desktop ergonomics

- High-DPI scaling.
- Small and large window behavior.
- Keyboard navigation.
- Focus indicators.
- Selection behavior.
- Copyability of forensic results.
- Resizable panels.
- Context preservation during navigation.

Give each category a score from 1 to 5.

Define the scoring criteria and provide concrete evidence for each score.

Do not assign scores merely from subjective impressions.

---

# Part C — Information architecture and forensic reasoning

## 6. Evaluate how the modernized reasoning engine is presented

This is the most important part of the audit.

SignalLens now distinguishes:

- Synthetic origin.
- Localized editing.
- Camera-acquisition compatibility.
- Supporting evidence.
- Contradictory evidence.
- Moderating evidence.
- Evidence reliability.
- Evidence coverage.
- Provenance declarations.
- Corroboration.
- Numerical scores.
- Confidence-policy rules.
- Evidence lineage.
- Unavailable detector results.

Inspect how much of this information is actually visible in the GUI.

For each concept, determine whether it is:

- Clearly represented.
- Present but difficult to access.
- Present with confusing terminology.
- Only available in raw traces.
- Not exposed in the GUI.

Produce a **reasoning visibility matrix**.

| Reasoning capability | Available in backend | Visible in GUI | Current location | Problem | Recommended presentation |
|---|---|---|---|---|---|

Important: establish the actual backend and GUI capabilities from the source code rather than relying solely on the modernization history.

---

## 7. Audit the primary forensic conclusion

Examine how the interface communicates the overall result.

Determine whether a user can immediately understand:

1. What SignalLens found.
2. Which forensic hypothesis is primarily supported.
3. The assigned confidence tier.
4. Why the finding received that confidence.
5. Which evidence supports the conclusion.
6. Which evidence contradicts or limits it.
7. Whether provenance is authenticated or merely declared.
8. Whether important detectors were unavailable.
9. What the conclusion does **not** establish.

### Critical design principle

Do not design a simple AI-versus-real classifier interface.

SignalLens does not produce a universally calibrated probability of image authenticity.

Avoid proposals such as:

- "98% AI-generated" gauges.
- Authenticity percentages without validated semantics.
- Red/green binary truth indicators.
- Presentation of heuristic suspicious scores as probabilities.
- Implying that camera-like evidence proves authenticity.
- Implying that editing evidence proves generative AI.

The interface must communicate forensic interpretation rather than unsupported certainty.

---

## 8. Evaluate evidence visualization

Review all existing visual forensic output components.

Examples may include:

- ELA.
- Residual/noise analysis.
- Boundary maps.
- Global FFT.
- Regional FFT.
- Patch similarity.
- Spatial patch analysis.
- Person segmentation.
- Texture and material analysis.
- Compression analysis.
- Camera/sensor evidence.

For each detector, determine:

- What output is produced.
- How it is displayed.
- Whether it is visual, numerical or textual.
- Whether the visualization can be enlarged.
- Whether the source image remains accessible.
- Whether original and processed images can be compared.
- Whether the visualization is correctly labeled.
- Whether unavailable results are distinguishable from negative findings.
- Whether visual regions connect to relevant evidence explanations.

Identify opportunities for:

- Synchronized image viewers.
- Before/after comparisons.
- Overlay controls.
- Zoom and pan.
- Region selection.
- Consistent visualization legends.
- Evidence-linked highlighting.

Do not propose unsupported heatmaps or overlays that would require inventing detector output.

Clearly distinguish features achievable from existing result data from features requiring backend changes.

---

# Part D — Architecture and implementation feasibility

## 9. Inspect GUI/backend coupling

Determine how the GUI obtains forensic results.

Inspect:

- Controllers.
- Workers.
- Signals and slots.
- Shared state.
- Models.
- Analysis-result objects.
- Background processing.
- Progress updates.
- Result persistence.
- Serialization.
- Exception handling.

Identify areas where presentation logic is mixed with:

- Forensic analysis.
- Evidence aggregation.
- Scoring.
- Hypothesis selection.
- Confidence computation.
- Provenance interpretation.

### Required principle

The redesigned GUI must consume the existing reasoning results.

It must not:

- Recalculate scores.
- Reassign confidence tiers.
- Reinterpret hypotheses independently.
- Create a second evidence model with conflicting semantics.
- Modify forensic detector thresholds.

Recommend an appropriate presentation-layer architecture using existing Qt capabilities and repository conventions.

Avoid unnecessary framework replacement.

---

## 10. Evaluate PyQt6 modernization options

Assess which Qt components are best suited to the existing application.

Consider where appropriate:

- `QMainWindow`.
- `QStackedWidget`.
- `QSplitter`.
- `QDockWidget`.
- `QAbstractItemModel`.
- `QTreeView`.
- `QTableView`.
- Custom `QWidget` components.
- `QGraphicsView` or an equivalent image-viewing architecture.
- Qt stylesheet/theme tokens.
- Persistent window and panel state.
- Existing third-party plotting components.

Do not introduce dependencies merely because they are popular.

Evaluate implementation complexity and compatibility with the current codebase.

Compare:

**Option A — Incremental GUI refinement**

Retain the main layout and improve styling, hierarchy and components.

**Option B — Workspace modernization**

Preserve backend/controller integration but reorganize the results into a modern forensic workspace with reusable panels.

**Option C — Full GUI rebuild**

Replace most interface components while retaining forensic analysis logic.

For each option, assess:

- Expected UX improvement.
- Implementation complexity.
- Regression risk.
- Architectural benefits.
- Expected maintenance burden.
- Migration challenges.
- Compatibility with existing tools.

Recommend one option and justify it.

---

# Part E — Proposed future design

## 11. Develop a professional SignalLens design concept

Based on the audit, propose a cohesive visual and interaction architecture.

Working design direction:

**SignalLens Forensic Workbench**

A modern, image-centered investigative dashboard combining professional desktop usability with structured forensic evidence.

The concept should prioritize:

1. Image visibility.
2. Primary forensic interpretation.
3. Separate hypothesis assessments.
4. Clear evidence attribution.
5. Confidence and limitations.
6. Direct access to detector visualizations.
7. Progressive disclosure of advanced reasoning details.

Possible workspace areas:

- Overview.
- Image Forensics.
- Evidence Explorer.
- Reasoning.
- Provenance.
- Reports.

Treat these as candidate sections, not mandatory implementation requirements.

Revise them when the existing application suggests a better structure.

### Suggested interface qualities

- Professional rather than decorative.
- Modern but restrained.
- High information density without visual clutter.
- Consistent typography.
- Clear status semantics.
- Comfortable image comparison.
- Efficient navigation.
- Scalable to future detectors.
- Appropriate for expert forensic users and technically curious nonexperts.

Avoid generic business-dashboard design.

Avoid unnecessary decorative charts.

---

## 12. Create wireframes

Produce low-fidelity wireframes for at least:

**A. Application entry / empty state**

How a new investigation begins.

**B. Investigation overview**

How the source image, primary conclusion, confidence and key evidence are displayed.

**C. Forensic image inspection**

How users explore and compare detector visualizations.

**D. Evidence Explorer**

How supporting, contradicting and moderating evidence is organized.

**E. Reasoning inspection**

How candidate findings, evidence lineage and confidence-policy decisions are exposed.

**F. Provenance and metadata**

How verified, unverified, missing and ambiguous information is displayed.

Wireframes may be produced using Markdown, Mermaid, SVG, HTML or another lightweight format supported by the existing environment.

Prefer artifacts that can be reviewed without installing additional dependencies.

Where feasible, create a static HTML concept using representative labels and sample data.

**Do not present the concept as a functioning replacement application.**

Do not build an interactive mock application unless it is clearly separated from production code.

---

## 13. Propose a visual design system

Specify an initial design system with:

### Typography

- Font family recommendations.
- Hierarchy.
- Size scale.
- Numerical text.
- Technical labels.

### Color

- Primary surfaces.
- Secondary surfaces.
- Borders.
- Accent colors.
- Text hierarchy.
- Semantic status colors.

### Spacing

- Base spacing units.
- Panel padding.
- Component gaps.
- Layout rhythm.

### Components

- Navigation.
- Cards.
- Evidence rows.
- Confidence indicators.
- Hypothesis summaries.
- Detector panels.
- Data tables.
- Expandable technical sections.
- Progress states.
- Error and unavailable states.

### Accessibility

- Contrast.
- Keyboard focus.
- High-DPI behavior.
- Status indicators that do not depend on color alone.

Recommend a dark-first or light-first strategy based on actual application usage and current UI conventions.

---

# Part F — Prioritized modernization roadmap

## 14. Build an implementation roadmap

Create a practical modernization plan with bounded phases.

Potential structure:

### UI-1 — Foundation

Theme tokens, typography, spacing, reusable components and navigation scaffolding.

### UI-2 — Investigation Overview

Primary finding, source image, hypothesis summaries and limitations.

### UI-3 — Image Forensics

Improved image viewing, detector panels and comparison tools.

### UI-4 — Evidence Explorer

Structured evidence tables, explanations, reliability and lineage.

### UI-5 — Reasoning and Provenance

Confidence-policy trace, candidate findings and provenance details.

### UI-6 — Reporting and Polish

Export presentation, accessibility, performance and final regression testing.

Adjust these stages based on the actual audit.

For each phase provide:

- Objective.
- Modules affected.
- New components.
- Existing components reused.
- Dependencies on other phases.
- Estimated complexity: Low / Medium / High.
- Major risks.
- Acceptance criteria.
- Relevant regression tests.

Do not provide arbitrary time estimates without a justified basis.

---

## 15. Identify quick wins

Separate genuine low-risk visual improvements from structural changes.

Examples to examine:

- Inconsistent padding.
- Weak typography hierarchy.
- Overly dense technical labels.
- Unclear navigation.
- Poorly presented confidence tiers.
- Excessive scrolling.
- Inconsistent empty states.
- Small image previews.
- Unstructured evidence descriptions.

Produce a ranked quick-win list based on:

**User impact × Implementation feasibility × Regression safety.**

Do not implement the quick wins during this audit.

---

# Part G — Deliverables

## 16. Required files

Create:

`doc/gui_modernization/audit/`

With the following artifacts:

### 1. `gui_architecture_inventory.md`

Complete current component/module map and GUI/backend relationships.

### 2. `current_user_journey.md`

Current navigation flow, pain points and usability risks.

### 3. `visual_design_audit.md`

Visual scores, evidence, screenshots and accessibility issues.

### 4. `reasoning_visibility_matrix.md`

Mapping from the modernized reasoning engine to current GUI presentation.

### 5. `gui_architecture_recommendation.md`

Comparison of incremental refinement, workspace modernization and full rebuild.

### 6. `signal_lens_design_concept.md`

Proposed information architecture, layout, interaction patterns and visual system.

### 7. `modernization_roadmap.md`

Prioritized implementation phases, dependencies, risks and acceptance criteria.

### 8. `executive_summary.md`

A concise management-level summary of the audit.

### 9. `screenshots/`

Actual screenshots if GUI execution is available.

### 10. `wireframes/`

Static wireframes or concept mockups for the main proposed screens.

---

# Part H — Validation and final report

## 17. Validate the audit artifacts

Before completion:

- Verify source-file references.
- Verify GUI component names.
- Verify current workflow descriptions.
- Verify backend-to-GUI data mappings.
- Ensure screenshots correspond to the real application.
- Ensure mockups are labeled as proposed concepts.
- Ensure the recommendation is implementable in PyQt6.
- Ensure no production code or tests were modified.

Run the existing regression suite only if useful for confirming baseline stability; do not modify tests.

---

## 18. Final Codex response

Return:

**A. Baseline**

Current branch, HEAD, Git status and relevant GUI modules.

**B. Current GUI assessment**

Overall visual/architectural maturity and the five most significant issues.

**C. Reasoning integration**

Which of the modernized reasoning capabilities are not yet meaningfully exposed in the current GUI.

**D. Recommended redesign strategy**

Choose incremental refinement, workspace modernization or full rebuild.

**E. Proposed workspace**

Main navigation, layout and component architecture.

**F. Visual direction**

Theme, typography, density and design language.

**G. Quick wins**

Top five high-value, low-risk improvements.

**H. Modernization phases**

Ordered implementation roadmap with dependencies.

**I. Audit artifacts**

Exact paths to all documentation, wireframes and screenshots.

**J. Git preservation**

Confirm that only authorized audit artifacts were created.

---

## Definition of Done

The GUI audit is complete when:

1. The entire current GUI architecture is inventoried.
2. The current investigation workflow is documented.
3. The actual visual design has been assessed where execution permits.
4. The reasoning engine's GUI exposure has been mapped.
5. The major usability and architectural weaknesses are identified.
6. A justified modernization strategy is selected.
7. A coherent future workspace has been described.
8. Reviewable wireframes have been produced.
9. A phased PyQt6 implementation roadmap is available.
10. Production code and tests remain unchanged.

**Core principle: Modernize the forensic investigation experience without weakening the rigor, transparency or reliability of the underlying reasoning engine.**

Perform the audit, produce the requested artifacts and report your findings. Do not begin implementation.
