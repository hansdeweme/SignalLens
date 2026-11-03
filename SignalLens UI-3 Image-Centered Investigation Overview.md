# CODEX TASK — SignalLens UI-3 Image-Centered Investigation Overview

## Mission

You are the principal PyQt6 desktop architect, senior Python engineer, forensic-software UX specialist and product design lead for SignalLens.

Implement **UI-3 — Image-Centered Investigation Overview**, the third phase of SignalLens's GUI modernization.

The previous phases established:

- **UI-0:** GUI architecture and usability audit.
- **UI-1:** Investigation-session integrity, guarded worker callbacks, annotation revisions and immutable presentation contracts.
- **UI-2:** Dark-first design system, reusable Qt components, six-destination workspace shell, keyboard navigation and persistent layout preferences.

UI-3 must turn the Overview destination into a fully functional, professional forensic investigation dashboard.

The Overview should allow a user to understand an investigation's principal result within seconds while retaining access to the underlying evidence and uncertainty.

**Primary objective: Make SignalLens's improved reasoning engine understandable through a clear, image-centered interface without altering forensic analysis or introducing unsupported certainty.**

This is a production GUI implementation task, not another design audit.

---

# Part A — Baseline and preparation

## 1. Verify the repository

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Windows desktop application

Latest reported state:

- Branch: `main`
- Working tree: clean
- UI-1 and UI-2 committed
- Latest regression suite: 406 passing tests
- No known failures or skipped tests

Verify the actual branch, HEAD, working tree and test count.

Do not assume the earlier commit identifiers are still current.

Run the existing regression suite before making changes.

### Read the existing documentation

Review:

`doc/gui_modernization/audit/`

`doc/gui_modernization/ui1/`

`doc/gui_modernization/ui2/`

Pay particular attention to:

- `signal_lens_design_concept.md`
- `reasoning_visibility_matrix.md`
- `workspace_architecture.md`
- `design_system_specification.md`
- `presentation_contracts.md`
- `implementation_report.md`
- `visual_validation.md`
- The six UI-0 wireframes

Inspect the actual GUI implementation before editing.

Do not rely on conceptual documentation where the implemented code differs.

### Repository protection

Do not stage, commit, push, merge, tag, reset or stash.

Do not alter forensic detectors, scoring logic, confidence policies or analysis thresholds.

Preserve existing files and generated forensic artifacts.

Keep `test_images/` excluded from Git.

---

# Part B — Product objective and information hierarchy

## 2. Define the Overview's purpose

The Overview should answer the following questions in order:

1. Which image am I investigating?
2. Has the analysis completed successfully?
3. What is the primary forensic finding?
4. How confident is SignalLens in that specific finding?
5. What do the other hypotheses indicate?
6. Which observations support the conclusion?
7. What contradicts or limits the conclusion?
8. Were important measurements unavailable?
9. Where can I inspect the underlying evidence?
10. What can—and cannot—be concluded?

A user should not have to read the complete legacy narrative or decision trace to understand these points.

The design must support both:

**Rapid review:** A concise, understandable forensic summary.

**Expert investigation:** Direct access to additional evidence and reasoning detail.

Use progressive disclosure rather than showing every technical field at once.

---

## 3. Establish the Overview hierarchy

Implement these primary sections:

### A. Investigation header

- Current image filename.
- Current investigation lifecycle status.
- Analysis profile.
- Relevant image properties.
- Source identity where useful.
- Active-result availability.

### B. Source-image viewer

- Large source-image preview.
- Correct aspect ratio.
- Clear identification of the original image.
- Basic zoom and fit controls.
- Image metadata such as dimensions where available.

### C. Primary forensic finding

- Main hypothesis or finding.
- Authoritative confidence tier.
- Brief explanation.
- Important qualifiers.
- Clear distinction between evidence and proof.

### D. Hypothesis assessments

Separate assessment summaries for:

- Synthetic origin.
- Localized editing.
- Camera-acquisition compatibility.

### E. Key evidence

A concise collection of important supporting and contradicting observations.

### F. Limitations and coverage

Important unavailable measurements, reliability restrictions, and provenance limitations.

### G. Investigation actions

Relevant actions to:

- Start or repeat analysis.
- Inspect forensic detector outputs.
- Open detailed evidence.
- Open reasoning.
- Inspect provenance.
- Access reporting.

Do not duplicate analysis controls unnecessarily.

Reuse existing controls where practical.

---

# Part C — Layout and visual design

## 4. Implement a responsive desktop dashboard

Use the UI-2 design system.

The intended layout is a modern forensic dashboard, not a collection of unrelated cards.

### Suggested arrangement

```text
┌────────────────────────────────────────────────────────────────┐
│ INVESTIGATION OVERVIEW                                         │
│ image_name.jpg             Completed · Profile: subject_based  │
├───────────────────────────────┬────────────────────────────────┤
│                               │ PRIMARY FORENSIC FINDING       │
│                               │                                │
│      SOURCE IMAGE             │ Localized processing           │
│                               │ inconsistency                  │
│                               │                                │
│                               │ HIGH CONFIDENCE                │
│                               │                                │
│                               │ Short explanation              │
│                               │                                │
│                               │ Important qualification        │
├───────────────────────────────┴────────────────────────────────┤
│ HYPOTHESIS ASSESSMENTS                                         │
│                                                                │
│ Synthetic origin  │ Localized editing │ Camera compatibility   │
├────────────────────────────────────────────────────────────────┤
│ KEY EVIDENCE                         │ LIMITATIONS             │
│                                      │                         │
│ Supporting evidence                  │ Unavailable detectors   │
│ Contradicting evidence               │ Reliability limits      │
│ Moderating evidence                  │ Provenance status       │
├──────────────────────────────────────┴─────────────────────────┤
│ View Image Forensics · Evidence · Reasoning · Report            │
└────────────────────────────────────────────────────────────────┘
```

Treat this as a design starting point.

Adapt the arrangement based on actual Qt behavior and available screen space.

### Layout requirements

- Source image remains prominent.
- Main finding remains visible without extensive scrolling at normal desktop sizes.
- Hypothesis summaries are visually distinct.
- Long evidence lists do not dominate the screen.
- The interface scrolls predictably when necessary.
- Panel sizes adapt to window resizing.
- No clipped text or overlapping controls.
- Existing navigation remains visible.

Use layouts and size policies rather than extensive fixed pixel positioning.

Do not create separate hardcoded layouts for each resolution.

---

# Part D — Source-image viewer

## 5. Implement a reusable source-image component

The original image is central to the investigation and must remain accessible.

Create or adapt a reusable Qt widget for displaying the selected source image.

### Required features

- Aspect-ratio-preserving rendering.
- Fit-to-view.
- Zoom in.
- Zoom out.
- Reset zoom.
- Optional mouse-wheel zoom where practical.
- Clear filename and dimension display.
- Appropriate loading and error states.

### Image handling

- Avoid unnecessarily loading full-resolution images multiple times.
- Respect memory constraints for large source images.
- Avoid blocking the GUI during expensive image decoding.
- Use existing Qt image facilities unless a justified alternative already exists.
- Handle unusual aspect ratios.
- Handle transparent images sensibly.
- Avoid distorting color interpretation through inappropriate overlays.

### Source integrity

Display the actual selected investigation image.

Do not substitute an analysis visualization or cached image from another session.

Respect UI-1 source identity and revision safeguards.

If the source file has changed or disappeared, show an explicit warning or unavailable state.

Do not silently display the wrong file.

### Important scope boundary

Advanced synchronized comparison, detector overlays and region-selection tools belong to UI-4.

Implement only the source-image viewing capabilities required for a professional Overview.

---

# Part E — Primary forensic finding

## 6. Design the main finding component

This is the most important interpretive component.

It should display:

- Primary forensic hypothesis.
- Primary finding or dominant pattern.
- Authoritative confidence tier.
- Concise evidence-based explanation.
- Important interpretive limitations.

Use the structured presentation contracts introduced in UI-1.

Do not reconstruct findings by parsing arbitrary paragraphs of the legacy narrative.

### Confidence semantics

The interface must distinguish:

- High.
- Medium.
- Low.
- Inconclusive.
- Unavailable.

Confidence describes the strength of evidence for a particular interpretation.

It is **not a calibrated probability of AI generation**.

Do not display:

- Arbitrary authenticity percentages.
- Probability gauges.
- "Definitely AI" claims.
- Unsupported binary real/fake verdicts.

### Visual treatment

The main finding should receive the strongest visual emphasis after the source image.

Use typography, spacing and modest semantic indicators.

Avoid oversized warning symbols, alarming red panels or decorative score rings.

### Example

**Localized processing inconsistency**

*High confidence*

"Multiple regional observations support a localized-processing interpretation. This does not independently establish whole-image synthetic generation."

This is illustrative wording only.

Actual content must derive from the current authoritative result.

---

# Part F — Hypothesis assessment cards

## 7. Present separate forensic hypotheses

Create three consistent hypothesis summary components:

### Synthetic origin

Assessment of evidence relevant to AI-generated image origin.

### Localized editing

Assessment of editing, compositing and region-specific processing.

### Camera-acquisition compatibility

Assessment of camera-like sensor and processing characteristics.

### Each component should expose

- Hypothesis name.
- Finding or assessment.
- Confidence tier.
- Concise supporting explanation.
- Relevant limitation.
- Navigation to detailed reasoning.

### Critical rules

Do not force every hypothesis into a binary yes/no state.

Do not assume that all hypotheses must have a confidence tier.

Do not treat camera-acquisition compatibility as proof of photographic authenticity.

Do not treat localized editing as proof of generative AI.

Do not transfer confidence between hypotheses.

Do not recalculate hypothesis assessments inside the GUI.

### Missing assessments

If a stored or legacy result lacks structured hypothesis data, show an explicit unavailable state.

Do not fabricate a hypothesis assessment from generic suspicious and benign scores.

Preserve access to the original narrative for legacy records.

---

# Part G — Evidence and limitations

## 8. Implement a concise evidence summary

The Overview should show only the most relevant evidence.

Use the existing structured evidence roles:

- Supporting.
- Contradicting.
- Moderating.

### Evidence display

Each item may show:

- Human-readable label.
- Evidence role.
- Source detector or family.
- Reliability where available.
- Short description.
- Link to detailed evidence.

### Ranking

Use existing authoritative ordering, relevance or priority information where provided.

Do not create a new forensic scoring or evidence-ranking algorithm.

If the backend does not provide an authoritative ranking, preserve stable source order and apply a simple documented display limit.

Do not imply that the first displayed item is statistically strongest unless the underlying data establishes that.

### Limitations panel

Present material limitations such as:

- Missing or unverified provenance.
- Rejected segmentation mask.
- Unavailable regional detectors.
- Insufficient image resolution.
- Low-reliability evidence.
- Missing optional metadata.
- Incomplete analysis.

Distinguish:

**Unavailable evidence** from **negative evidence**.

Do not convert the absence of data into a suspicious finding.

### Empty states

When no relevant evidence exists, explain that no structured evidence is available for display.

Do not present empty lists as proof of authenticity.

---

# Part H — Investigation lifecycle integration

## 9. Bind the Overview to UI-1 sessions

Use the authoritative investigation session and presentation snapshot.

The Overview must update correctly when:

1. No image is selected.
2. An image is selected.
3. Analysis begins.
4. Progress arrives.
5. Analysis completes.
6. Analysis fails.
7. A result becomes obsolete.
8. A new image replaces the previous selection.
9. The same image is reanalyzed.
10. A stored summary is loaded.
11. OSINT annotations are updated.
12. The source image becomes unavailable.

### Required invariant

**Every element of the Overview must belong to the same active investigation and result revision.**

Never display:

- Image A with the findings of image B.
- The previous investigation's confidence on a newly selected image.
- An outdated finding after reanalysis.
- Stale OSINT annotations on a current report.

Where asynchronous image loading is used, bind its completion to the same session identity.

Reuse UI-1's existing ownership and stale-update safeguards.

---

## 10. Define lifecycle-specific presentation

### Empty

Explain how to start an investigation.

### Image selected

Display the source preview and indicate that analysis has not yet been completed.

### Analyzing

Display progress and preserve an accurate current status.

Do not show old results as if they belong to the running analysis.

### Completed

Display the full Overview.

### Failed

Display an actionable error state.

Do not invent a forensic result.

### Cancelled or superseded

Clearly distinguish an abandoned analysis from a completed investigation.

### Stored result

Display available structured data and identify any unavailable legacy fields.

Do not assume the original source image is still available.

---

# Part I — Navigation and usability

## 11. Connect Overview actions to existing workspaces

Users should be able to open:

- Image Forensics.
- Evidence.
- Reasoning.
- Provenance.
- Reports.

Use the navigation infrastructure introduced in UI-2.

Do not create new independent navigation controllers.

### Requirements

- Clicking an action opens the correct workspace.
- Active investigation context is preserved.
- Navigation does not rerun forensic analysis.
- Navigation does not modify scoring or confidence.
- Keyboard shortcuts remain operational.
- Disabled actions communicate why they are unavailable.

Where later workspace implementations are incomplete, navigate to the existing functional content or an explicitly labeled transitional view.

Do not promise functionality that has not been implemented.

---

## 12. Improve readability and accessibility

Use UI-2 typography and design tokens.

### Requirements

- Readable body text.
- Clear heading hierarchy.
- Accessible contrast.
- Keyboard focus indicators.
- Tooltips for technical concepts where useful.
- Copyable technical information.
- Proper text wrapping.
- Resizable panels.
- Stable layout with long filenames.
- Reasonable behavior at minimum window size.

Test the Overview at normal and maximized window sizes.

Where practical, include 125% and 150% Windows display scaling checks.

Do not claim DPI validation if only offscreen testing was performed.

---

# Part J — Architecture and boundaries

## 13. Keep presentation separate from forensic logic

The Overview must consume existing structured results.

Suggested implementation structure:

- `overview_workspace.py`
- `source_image_viewer.py`
- Reusable hypothesis/finding/evidence components
- Narrow additions to existing presentation adapters only where required

Adapt filenames to current project conventions.

### Forbidden behavior

The Overview must not:

- Run detector algorithms.
- Calculate suspicious or benign scores.
- Assign confidence.
- Reclassify metadata.
- Select hypotheses.
- Apply corroboration thresholds.
- Recompute evidence lineage.
- Modify analysis results.

If a required display field is missing from the UI-1 presentation contract, extend that contract compatibly.

Trace every new display field to an authoritative backend source.

Avoid parallel data models containing contradictory forensic interpretations.

---

## 14. Preserve legacy workflows

All existing functionality must remain available.

In particular:

- Analysis configuration.
- Starting analysis.
- Progress monitoring.
- Detector-file access.
- Legacy narrative summary.
- Decision trace.
- Metadata.
- OSINT.
- Reporting.
- Stored-summary loading.

The Overview may replace the legacy scrolling summary as the primary landing view, but must not remove access to the full narrative.

Document where that narrative remains accessible.

Do not redesign other workspaces during UI-3.

---

# Part K — Testing

## 15. Preserve existing regression coverage

The latest reported baseline is:

**406 passing tests, zero failed or skipped.**

Run the existing suite before implementation.

Add targeted automated tests for the new Overview.

### Source-image tests

- Valid image loading.
- Missing image.
- Corrupted image.
- Unusual aspect ratio.
- Large image.
- Zoom and fit behavior.
- Image reselection.
- Source file changed.
- Old image-load completion after new selection.

### Finding tests

- High-confidence localized editing.
- Medium-confidence unverified synthetic origin.
- Inconclusive result.
- No primary finding.
- Missing confidence policy data.
- Long finding descriptions.

### Hypothesis tests

- Three complete assessments.
- Partially available assessments.
- Missing assessments in legacy results.
- Hypothesis-specific confidence preserved.
- Camera compatibility not presented as authenticity proof.

### Evidence tests

- Supporting evidence.
- Contradicting evidence.
- Moderating evidence.
- Missing evidence.
- Unavailable detectors.
- Rejected segmentation.
- Stable ordering.
- Correct source identifiers.

### Session tests

- New investigation.
- Reanalysis.
- Obsolete worker completion.
- Stored-summary loading.
- Failed analysis.
- OSINT revision update.
- Report snapshot consistency.

### Navigation tests

- Overview to Image Forensics.
- Overview to Evidence.
- Overview to Reasoning.
- Overview to Provenance.
- Overview to Reports.
- Keyboard navigation compatibility.

### Rendering tests

- Normal-sized window.
- Maximized window.
- Minimum supported size.
- Long filenames.
- Long narratives.
- Empty states.
- Text wrapping.
- No overlapping controls.

Avoid fragile pixel-perfect snapshot assertions.

Use deterministic Qt tests and actual structured fixtures.

---

# Part L — Reference-image validation

## 16. Validate the current forensic baseline

Use both existing reference images if accessible.

The current measured `normal`-profile baseline reported during UI-2 was:

| Reference | Suspicious | Benign | Finding |
|---|---:|---:|---|
| Instagram | 21.32705 | 2.25 | High localized editing |
| Midjourney | 6.675 | 1.5 | Medium unverified generation declaration |

These values differ from earlier `subject_based` runs.

Record the analysis profile, input file hash and relevant configuration alongside every comparison.

### Validation requirements

For each image:

1. Confirm forensic results remain unchanged.
2. Create the Overview presentation snapshot.
3. Verify primary finding and confidence.
4. Verify separate hypothesis assessments.
5. Verify supporting, contradicting and moderating evidence.
6. Verify limitations and coverage.
7. Verify source-image identity.
8. Confirm report compatibility.

Do not alter forensic scoring or thresholds to force baseline agreement.

---

# Part M — Visual validation

## 17. Inspect the actual redesigned Overview

Run SignalLens where the environment permits.

Capture:

1. Empty Overview.
2. Selected-image Overview.
3. Analyzing state.
4. Completed Instagram Overview.
5. Completed Midjourney Overview.
6. Inconclusive result.
7. Missing-image state.
8. Failed-analysis state.
9. Minimum supported window size.
10. Maximized window.

Save visual captures under:

`doc/gui_modernization/ui3/screenshots/`

Include native Windows screenshots where possible.

Compare the redesigned Overview against the existing UI-2 completed-Overview screenshot.

Evaluate:

- Visual hierarchy.
- Source-image prominence.
- Legibility.
- Information density.
- Hypothesis clarity.
- Evidence visibility.
- Limitation visibility.
- Scrolling behavior.
- Professional consistency.
- Uncertainty communication.

Report objective layout issues discovered and corrected.

Do not treat an offscreen rendering as a substitute for native DPI verification.

---

# Part N — Documentation

## 18. Required deliverables

Create:

`doc/gui_modernization/ui3/`

### A. `overview_design_specification.md`

Describe:

- Information hierarchy.
- Layout.
- Components.
- Typography.
- Interaction behavior.
- Empty/loading/completed/error states.
- Accessibility considerations.

### B. `overview_data_mapping.md`

Map each visible UI field to its authoritative source.

Include:

| Display field | Presentation contract | Backend source | Fallback behavior |
|---|---|---|---|

### C. `source_image_viewer.md`

Document:

- Image-loading strategy.
- Zoom behavior.
- Aspect-ratio preservation.
- Source identity checks.
- Memory considerations.
- Failure states.

### D. `overview_session_integration.md`

Explain how the Overview responds to session transitions and rejects stale updates.

### E. `legacy_summary_migration.md`

Document:

- What moved into the Overview.
- What remains in the legacy summary.
- Where users access complete narratives.
- What will be migrated in later phases.

### F. `visual_validation.md`

Document:

- Screenshots.
- Window dimensions.
- DPI conditions.
- Comparison against UI-2.
- Remaining visual issues.

### G. `implementation_report.md`

Summarize:

- New modules.
- Modified modules.
- Reused components.
- Architecture.
- Compatibility.
- Remaining limitations.

### H. `regression_results.md`

Include:

- Starting test count.
- Final test count.
- New tests.
- Reference-image outcomes.
- GUI integration results.
- Failures and skips.

---

# Part O — Final acceptance criteria

## 19. UI-3 Definition of Done

UI-3 is complete when:

1. The Overview is a functional, image-centered investigation dashboard.
2. The selected source image is displayed accurately.
3. The primary finding is prominent and understandable.
4. Confidence is displayed without implying statistical probability.
5. Synthetic origin, localized editing and camera compatibility are distinguishable.
6. Key evidence is presented with correct roles.
7. Important limitations and unavailable measurements are visible.
8. Source-image and forensic-result identities remain synchronized.
9. All lifecycle states are handled correctly.
10. Existing analysis and report workflows remain operational.
11. Navigation to deeper workspaces is functional.
12. The legacy narrative remains accessible.
13. No forensic calculations occur in presentation code.
14. Existing tests continue passing.
15. New Overview tests pass.
16. Both reference-image outcomes remain unchanged.
17. Visual screenshots and implementation documentation are produced.
18. No unrelated workspace redesign is introduced.

---

## 20. Final Codex response

Return:

**A. Baseline**

Branch, HEAD, Git status and starting tests.

**B. Overview implementation**

New components, layout and behaviors.

**C. Source-image viewer**

Loading, zoom, resizing and identity safeguards.

**D. Reasoning presentation**

How the primary finding, hypotheses, evidence and limitations are displayed.

**E. Session integration**

How stale images and results are prevented.

**F. Legacy compatibility**

Where existing narrative and analysis functionality remain available.

**G. Validation**

Exact passing, failing and skipped test counts.

**H. Reference images**

Outcomes, scores and configuration consistency.

**I. Visual inspection**

Screenshots, layout issues and DPI coverage.

**J. Git status**

Modified/untracked files and confirmation that nothing was staged, committed or pushed.

**K. UI-4 readiness**

Identify any blockers to advanced image-forensic comparison work.

---

## Strict constraints

- Do not change forensic detectors.
- Do not change numerical scoring.
- Do not change hypothesis selection.
- Do not change confidence-policy rules.
- Do not alter evidence lineage.
- Do not reclassify provenance.
- Do not weaken UI-1 session safeguards.
- Do not replace UI-2 navigation or design-system architecture.
- Do not build advanced image comparison yet.
- Do not implement the full Evidence Explorer.
- Do not redesign Reports.
- Do not introduce unnecessary dependencies.
- Do not stage, commit, push, merge, tag, reset or stash.
- Preserve existing Git changes and excluded test assets.

**Core principle: An investigator should understand what SignalLens found, why it matters and what remains uncertain without having to decipher a technical trace—while retaining immediate access to the evidence behind every conclusion.**

Implement UI-3, run the complete regression suite, validate the redesigned Overview and deliver the requested reports. Do not begin UI-4.
