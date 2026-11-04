# CODEX TASK — SignalLens UI-4 Forensic Image Inspection & Comparison Workspace

## Mission

You are the principal PyQt6 desktop architect, senior Python engineer, digital-image forensics specialist and forensic visualization UX designer for SignalLens.

Implement **UI-4 — Forensic Image Inspection & Comparison Workspace**, the fourth phase of the SignalLens GUI modernization.

The previous phases established:

- **UI-0:** Architecture and usability audit, recommending workspace modernization.
- **UI-1:** Investigation-session integrity, invocation guards, annotation revisions and immutable presentation contracts.
- **UI-2:** Dark-first design system, six-destination workspace shell, keyboard navigation and persistent layout preferences.
- **UI-3:** Image-centered investigation Overview, asynchronous source-image viewer, hypothesis cards, evidence summaries and limitations.

UI-4 must transform the existing **Image Forensics** destination into a professional workspace for inspecting and comparing the source image with forensic detector outputs.

The objective is not to create visually impressive but misleading heatmaps.

**Primary objective: Allow investigators to inspect the actual forensic observations supporting SignalLens's findings, while preserving artifact identity, spatial integrity, reliability information and investigation-session consistency.**

Use existing analysis outputs.

Do not change detector algorithms, scoring, hypothesis selection or confidence assignment.

---

# Part A — Baseline and preparation

## 1. Verify repository state

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Windows desktop application

Latest reported state:

- UI-3 completed, committed and pushed.
- Working tree reportedly clean.
- Previous regression suite: 432 tests passed.
- No UI-4 implementation yet.

Verify:

1. Current branch.
2. HEAD commit.
3. Working-tree status.
4. Remote-tracking status.
5. Existing test count.
6. Presence of UI-1, UI-2 and UI-3 implementations.

Do not assume the repository remains clean.

Record the baseline before changing anything.

### Repository restrictions

Do not:

- Stage or commit files.
- Push changes.
- Merge branches.
- Create tags.
- Reset or stash changes.
- Delete generated forensic artifacts.
- Modify existing test images.
- Discard inherited modifications.

Keep `test_images/` excluded from Git.

Keep UI-4 changes separately reviewable.

---

## 2. Review existing architecture

Read:

`doc/gui_modernization/audit/`

`doc/gui_modernization/ui1/`

`doc/gui_modernization/ui2/`

`doc/gui_modernization/ui3/`

Prioritize:

- GUI architecture inventory.
- Current user journey.
- Reasoning visibility matrix.
- Workspace architecture.
- Design-system specification.
- Presentation contracts.
- Session-lifecycle specification.
- UI-3 source-image viewer documentation.
- UI-3 implementation report.
- UI-3 visual validation.

Inspect actual source files and implementation details.

Especially investigate:

- Current Image Forensics destination.
- Existing detector output access.
- Source-image viewer.
- Worker/controller integration.
- Artifact persistence.
- Detector result structures.
- Analysis output directories.
- Reasoning and evidence identifiers.
- UI-1 investigation identity.
- UI-3 asynchronous image-loading safeguards.

Do not design a second independent image-loading or session-management system if the existing implementation can be extended.

---

# Part B — Forensic artifact inventory

## 3. Audit existing detector outputs

**Complete this inspection before implementing the new workspace.**

Identify every detector or analysis stage producing a user-inspectable artifact.

Possible categories include:

- Error Level Analysis.
- Residual/noise analysis.
- Global FFT.
- Regional FFT.
- Compression analysis.
- Boundary analysis.
- Person segmentation.
- Subject/background comparison.
- Subject texture.
- Subject material.
- Process asymmetry.
- Patch similarity.
- Spatial patch recurrence.
- Sensor/CFA analysis.
- Cross-signal summaries.

This is a discovery list, not an assertion that every detector produces an image.

Inspect the actual code and recorded results.

### Required artifact inventory

For each detector, document:

| Field | Description |
|---|---|
| Detector ID | Stable internal identifier |
| Detector name | Human-readable label |
| Output type | Image, mask, chart, table, text, JSON or other |
| Artifact path | How output is located |
| Dimensions | Native width and height, if applicable |
| Color space | RGB, grayscale, heatmap, categorical mask, etc. |
| Coordinate system | Source pixels, cropped region, normalized coordinates or independent |
| Source transform | Resize, crop, rotation, padding or alignment |
| Spatial registration | Verified, conditional, unsupported or unknown |
| Reliability | Available quality/reliability metadata |
| Evidence association | Related signal or hypothesis IDs |
| Persistence | Whether output survives session reload |
| Recommended viewer | Suitable display mode |

**Do not assume a visualization is registered simply because it has the same width and height as the source image.**

A spatial relationship must be supported by the detector's actual processing path.

---

## 4. Classify artifact types

Create an explicit artifact taxonomy.

### Type A — Source-aligned spatial artifact

A visualization whose pixels correspond to known coordinates in the original image.

Examples may include a full-image residual map or a mask derived through a documented reversible resizing transform.

Allowed functionality:

- Side-by-side comparison.
- Synchronized zoom/pan.
- Overlay, if registration and rendering semantics are verified.

### Type B — Transformable spatial artifact

A cropped, resized or otherwise transformed visualization with documented geometry sufficient to register it to the original.

Allowed functionality:

- Side-by-side display.
- Registration-aware synchronization.
- Overlay only after the transform is correctly applied and validated.

### Type C — Non-spatial diagnostic visualization

A visualization representing frequency distributions, histograms, spectra or other information without direct source-pixel correspondence.

Allowed functionality:

- Side-by-side inspection.
- Independent zoom.
- Independent cursor behavior.

Do not allow source-coordinate overlays.

### Type D — Structured non-image evidence

Tables, scalar results, summaries and other detector outputs without image artifacts.

Allowed functionality:

- Structured presentation.
- Links to relevant reasoning.
- Clear indication that no image visualization is available.

### Type E — Missing or unusable artifact

An expected artifact is unavailable, corrupt, rejected or inaccessible.

Allowed functionality:

- Explicit unavailable state.
- Reason for unavailability.
- Relevant limitations.

Do not silently substitute unrelated output.

---

# Part C — Artifact identity and registration contracts

## 5. Introduce typed artifact presentation contracts

Extend UI-1's immutable presentation-model architecture.

Implement a small typed contract for forensic visualization artifacts.

Suggested conceptual structure:

```python
@dataclass(frozen=True)
class ForensicArtifact:
    artifact_id: str
    session_id: str
    analysis_id: str
    detector_id: str
    label: str
    artifact_type: str
    path: str | None
    width: int | None
    height: int | None
    registration_status: str
    reliability_status: str | None
    evidence_ids: tuple[str, ...]
```

Adapt the design to actual result structures and project conventions.

Include additional fields where needed for:

- Analysis-result revision.
- Source-file hash.
- Image orientation.
- Pixel-coordinate transform.
- Crop bounds.
- Resampling.
- Color interpretation.
- Artifact version or content identity.
- Availability and failure reason.

Avoid speculative fields that cannot be populated.

### Identity requirements

An artifact must be bound to:

- The correct investigation.
- The correct analysis invocation.
- The correct source image.
- The correct result revision.
- The actual detector that produced it.

An artifact path alone is insufficient identity.

Prevent an artifact from an older analysis from appearing in a newer investigation.

---

## 6. Define spatial registration explicitly

Implement a registration contract that distinguishes:

- `REGISTERED`
- `TRANSFORMABLE`
- `UNREGISTERED`
- `UNKNOWN`
- `NOT_APPLICABLE`

Use equivalent enums if better aligned with existing project conventions.

### Registration metadata

Where supported, capture:

- Source dimensions.
- Artifact dimensions.
- Crop origin.
- Crop size.
- Scaling.
- Rotation/orientation.
- Padding.
- Coordinate transform.
- Valid spatial extent.

Do not infer registration solely from matching image sizes.

### Coordinate mapping

Document transformations between:

- Source-image pixels.
- Artifact-image pixels.
- Viewer/display pixels.

Use consistent conventions.

### Critical invariant

**Never present a detector visualization as spatially aligned with the source unless its registration can be demonstrated from the production artifact pipeline.**

If registration information is missing, classify the artifact as unknown or unregistered.

Do not invent coordinates to enable an overlay.

---

# Part D — Image Forensics workspace

## 7. Build the main inspection layout

Replace the current Image Forensics placeholder or transitional view with a fully functional forensic inspection workspace.

Suggested desktop layout:

```text
┌───────────────────────────────────────────────────────────────┐
│ IMAGE FORENSICS                                                │
│ Source image · Detector artifact · Reliability · Registration  │
├────────────────┬──────────────────────┬───────────────────────┤
│ DETECTORS      │ SOURCE IMAGE         │ FORENSIC ARTIFACT     │
│                │                      │                       │
│ ELA            │                      │                       │
│ Residual       │                      │                       │
│ FFT            │                      │                       │
│ Boundaries     │                      │                       │
│ Segmentation   │                      │                       │
│ Patch analysis │                      │                       │
│ ...            │                      │                       │
│                │                      │                       │
├────────────────┴──────────────────────┴───────────────────────┤
│ ARTIFACT DETAILS                                               │
│ Detector · Meaning · Reliability · Registration · Limitations  │
├───────────────────────────────────────────────────────────────┤
│ View Evidence · View Reasoning · View Provenance               │
└───────────────────────────────────────────────────────────────┘
```

Adapt the layout to actual results and current UI-2 design conventions.

### Requirements

- Resizable panels.
- Source and artifact viewers visible simultaneously.
- Detector/artifact navigation.
- Clear selected-artifact state.
- Appropriate empty/loading/error states.
- Preserved session context.
- Consistent dark-first styling.
- No unnecessary fixed-size panels.

The source image should remain identifiable at all times.

---

## 8. Implement artifact navigation

Allow users to select available forensic artifacts.

Group outputs by detector or forensic analysis category where appropriate.

Each entry should indicate:

- Detector name.
- Artifact label.
- Output type.
- Availability.
- Reliability, if known.
- Registration capability.
- Selection state.

### Requirements

- Do not list nonexistent artifacts as if they were available.
- Do not duplicate artifacts because several reasoning signals reference them.
- Preserve stable artifact IDs.
- Support keyboard selection.
- Support long detector names.
- Display unavailable outputs without falsely implying negative forensic evidence.

Where a detector produces multiple artifacts, allow selection of each.

Do not create a new detector-classification algorithm in the GUI.

---

# Part E — Image viewers and comparison modes

## 9. Reuse and extend the UI-3 source-image viewer

Inspect the existing asynchronous viewer.

Reuse its:

- Bounded image loading.
- Fit-to-view behavior.
- Zoom controls.
- Source-hash checks.
- Session/revision guards.
- Error handling.

Refactor carefully if a reusable base viewer is necessary.

Do not introduce parallel image-loading logic with different correctness guarantees.

### Required controls

Both image panels should support:

- Fit to view.
- Zoom in.
- Zoom out.
- Reset.
- Pan.
- Clear scale indication.
- Loading indicator.
- Unavailable/error state.

Preserve aspect ratio.

Avoid excessive full-resolution decoding.

Keep the GUI responsive.

---

## 10. Implement comparison modes

### Mode A — Side-by-side comparison

Default mode.

Source image on one side, selected detector artifact on the other.

Supports:

- Independent zoom.
- Independent pan.
- Clear image labels.
- Artifact metadata.
- Reliability information.

This mode must work for all valid image artifacts.

### Mode B — Synchronized comparison

Available only when registration is verified.

Supports:

- Linked zoom.
- Linked pan.
- Corresponding source and artifact coordinates.
- Correct handling of crop and resize transforms.

Do not enable synchronization for non-spatial diagnostics.

### Mode C — Overlay comparison

Implement only for artifacts with validated spatial registration and suitable compositing semantics.

Supports:

- Adjustable opacity.
- Source/artifact overlay.
- Clear legend.
- Visual indication of registered spatial extent.

Do not overlay FFT spectra, histograms or other non-spatial diagnostics.

If reliable overlay cannot be implemented for any current artifact, keep overlay unavailable and document why.

Do not force implementation using speculative registration.

---

## 11. Implement robust zoom and pan synchronization

For registered artifacts:

- Link views through image-coordinate transforms, not raw scrollbar positions.
- Account for scaling and cropping.
- Prevent recursive signal loops.
- Handle zoom changes near image boundaries.
- Preserve stable focus points when zooming.
- Handle differing aspect ratios.

### Acceptance invariant

A selected source-image point must map to the correct corresponding artifact location within documented coordinate tolerance.

Create deterministic synthetic fixtures to test this.

Do not rely solely on visual inspection.

---

# Part F — Evidence context and interpretation

## 12. Provide detector context

Selecting an artifact should display a concise technical context panel.

Include where available:

- Detector name.
- Detector purpose.
- Artifact type.
- What the visualization represents.
- Relevant evidence identifiers.
- Reliability status.
- Registration status.
- Known limitations.
- Whether the detector ran successfully.
- Related forensic hypothesis.

### Critical distinction

A visualization is an observation, not necessarily a conclusion.

For example:

An ELA map may show compression inconsistencies, but that alone does not establish AI generation.

Do not present suspicious colors as automatically proving manipulation.

Use cautious, technically accurate language.

---

## 13. Connect artifacts to existing reasoning

Use current evidence IDs and presentation contracts.

Where the backend provides a relationship:

- Show related evidence.
- Link to the Evidence workspace.
- Link to the Reasoning workspace.
- Preserve the active investigation.

Where no relationship exists:

- Say that no structured evidence linkage is available.
- Do not invent a forensic association based on detector names alone.

Do not modify evidence scoring or hypothesis selection.

---

# Part G — Artifact discovery and persistence

## 14. Establish safe artifact discovery

Inspect existing result persistence and output-directory conventions.

Prefer explicit artifact manifests where already available.

If no complete manifest exists, implement a narrow adapter using known detector output contracts.

### Requirements

- No arbitrary filesystem crawling outside the investigation output area.
- No reliance on filename coincidence alone where stronger identity is available.
- No unsafe path traversal through stored metadata.
- No accidental selection of outputs from another analysis.
- No mutation of forensic artifacts.
- No duplicate artifact entries.
- Deterministic ordering.

### Stored investigations

Support reopening previously saved results.

If artifacts no longer exist:

- Preserve metadata where available.
- Mark the visualization unavailable.
- Do not silently show artifacts from another run.

Where older stored results lack new registration metadata, treat the registration status conservatively.

---

## 15. Handle artifact integrity

Verify applicable artifact properties before display.

Examples:

- File exists.
- File is readable.
- Image decodes successfully.
- Dimensions match expected metadata where specified.
- Source identity is compatible.
- Artifact identity matches the active result.
- Registration contract is valid.

Do not modify original files.

Avoid repeated expensive hashing where an existing verified identity can be reused safely.

Cache decoded previews only under keys that include sufficient artifact identity.

---

# Part H — Session and asynchronous safety

## 16. Preserve UI-1 lifecycle guarantees

Artifact loading must be session-aware.

### Required cases

- Image A's artifact finishes loading after image B is selected.
- The user selects artifact A, then artifact B before A loads.
- Reanalysis produces a newer artifact with the same filename.
- Stored analysis is loaded during an asynchronous preview.
- The source image changes on disk.
- The artifact disappears while being loaded.
- The selected analysis becomes obsolete.
- An analysis fails after previous artifacts were displayed.

### Invariant

**No image or detector artifact from an obsolete session, invocation or result revision may replace the active display.**

Use immutable request identities or equivalent safeguards.

Keep GUI updates on the main Qt thread.

Do not introduce unsafe thread cancellation.

---

# Part I — Desktop usability and accessibility

## 17. Professional interaction requirements

Support:

- Keyboard detector selection.
- Keyboard navigation.
- Visible focus state.
- Tooltips for technical controls.
- Clear fit/zoom controls.
- Copyable artifact identifiers or metadata.
- Adjustable panel proportions.
- Readable long labels.
- Persistent useful layout preferences.
- High-DPI-compatible controls.

Use UI-2's existing design tokens.

Do not create a new visual theme.

### Layout validation

Inspect:

- Normal window size.
- Maximized size.
- Minimum supported size.
- Narrow content panels.
- Tall and wide images.
- Long detector lists.
- Missing artifacts.
- Large technical descriptions.

Test native Windows behavior where possible.

Document any unverified DPI scales.

---

# Part J — Tests and validation

## 18. Preserve the existing regression suite

Latest reported baseline:

**432 tests passed, zero failed, zero skipped.**

Run the baseline suite first.

Add focused tests for UI-4.

### Artifact inventory tests

- Correct detector enumeration.
- Multiple artifacts per detector.
- Non-image artifacts.
- Missing artifact.
- Duplicate filenames.
- Stable IDs.
- Stored investigation compatibility.

### Registration tests

- Full-image registered artifact.
- Uniformly resized artifact.
- Cropped artifact.
- Rotated artifact.
- Padded artifact.
- Non-spatial FFT visualization.
- Unknown registration.
- Invalid transform.
- Mismatched dimensions.
- Coordinate round-trip accuracy.

### Viewer tests

- Fit.
- Zoom.
- Pan.
- Aspect ratio.
- Large images.
- Corrupt images.
- Async loading.
- Stale load rejection.

### Comparison tests

- Side-by-side viewing.
- Independent zoom.
- Registered synchronization.
- Unregistered sync disabled.
- Overlay eligibility.
- Overlay opacity.
- Overlay alignment.
- Recursive update prevention.

### Session tests

- New image selection.
- Reanalysis.
- Artifact selection during loading.
- Old worker completion.
- Stored-summary loading.
- Source changed on disk.
- Missing artifact after reload.
- Analysis failure.
- Session closure.

### Evidence integration tests

- Correct evidence IDs.
- Correct reliability status.
- Correct hypothesis associations.
- No invented evidence links.
- Correct unavailable states.
- Navigation to Evidence and Reasoning.

### Compatibility tests

- Overview remains functional.
- Existing analysis workflow remains functional.
- Report generation remains functional.
- OSINT state remains consistent.
- Existing confidence tiers unchanged.
- Existing scorecards unchanged.

Use deterministic tests.

Avoid fragile pixel-perfect rendering assertions.

---

# Part K — Reference-image validation

## 19. Validate Instagram and Midjourney

Use the established `normal` analysis profile.

Latest measured baseline:

| Reference | Suspicious | Benign | Primary finding |
|---|---:|---:|---|
| Instagram | 21.32705 | 2.25 | High localized editing |
| Midjourney | 6.675 | 1.5 | Medium unverified synthetic context |

For each image:

1. Run or load the existing full analysis.
2. Record source hash and analysis identity.
3. Enumerate available artifacts.
4. Classify artifact types.
5. Determine registration status from actual production transformations.
6. Open representative spatial and non-spatial artifacts.
7. Validate side-by-side comparison.
8. Validate sync/overlay only for eligible artifacts.
9. Verify evidence links where structured associations exist.
10. Confirm forensic scores and confidence remain unchanged.

If outputs differ because of environment or configuration, report the difference rather than modifying scoring.

### Important

Do not assume that the two reference images cover every artifact type.

Use synthetic fixtures for transform geometry and registration validation.

---

# Part L — Visual validation

## 20. Capture the implemented workspace

Run the actual GUI where supported.

Capture:

1. Empty Image Forensics workspace.
2. Completed Instagram investigation.
3. Completed Midjourney investigation.
4. Registered spatial artifact.
5. Non-spatial diagnostic artifact.
6. Unavailable artifact.
7. Independent side-by-side comparison.
8. Synchronized comparison.
9. Overlay mode, if supported.
10. Minimum window.
11. Maximized window.
12. Long detector list.

Save captures under:

`doc/gui_modernization/ui4/screenshots/`

Provide native Windows screenshots where possible.

Do not claim native DPI validation unless tested.

### Visual acceptance

- Source image remains prominent.
- Artifact labeling is unambiguous.
- Detector selection is understandable.
- Reliability and registration are clearly indicated.
- No clipping or overlapping text.
- Correct aspect-ratio behavior.
- No misleading overlay.
- Smooth pan/zoom behavior.
- Consistent design-system application.

---

# Part M — Documentation

## 21. Required deliverables

Create:

`doc/gui_modernization/ui4/`

### A. `artifact_inventory.md`

Complete detector-output inventory.

Include output types, persistence, registration, reliability and evidence associations.

### B. `artifact_contracts.md`

Document artifact identity, metadata, transforms, availability, versioning and compatibility.

### C. `spatial_registration.md`

Document coordinate systems, transformations, registration rules, mapping calculations and acceptance tolerances.

### D. `comparison_workspace_design.md`

Describe layout, navigation, viewer behavior, comparison modes, overlays and interaction rules.

### E. `artifact_evidence_mapping.md`

Map detector artifacts to structured evidence IDs and reasoning links.

Explicitly identify unsupported relationships.

### F. `session_and_async_integrity.md`

Describe artifact-loading request identity, stale-result guards, source verification and caching.

### G. `legacy_artifact_compatibility.md`

Explain how existing and stored results are loaded without destructive migration.

### H. `implementation_report.md`

Summarize changed modules, architecture, functionality, limitations and future migration considerations.

### I. `visual_validation.md`

Report screenshots, native rendering checks, window dimensions and DPI limitations.

### J. `regression_results.md`

Include test counts, reference-image results and mathematical/coordinate validation.

---

# Part N — Final acceptance criteria

## 22. UI-4 Definition of Done

UI-4 is complete when:

1. Existing forensic artifacts are inventoried and classified.
2. Every displayed artifact has a stable investigation-bound identity.
3. Registration is explicitly verified, transformable, unknown or unsupported.
4. The Image Forensics destination provides a functional comparison workspace.
5. Source and artifact images can be inspected side by side.
6. Independent zoom and pan work reliably.
7. Synchronized comparison is enabled only for eligible spatial artifacts.
8. Overlay comparison is enabled only when spatial registration and compositing semantics are valid.
9. Non-spatial diagnostic visualizations cannot be misleadingly overlaid.
10. Evidence context and reliability are available where supported.
11. Missing, corrupt and rejected outputs are handled explicitly.
12. Stored investigations remain accessible.
13. Obsolete asynchronous loads cannot overwrite active content.
14. Existing investigation and report workflows remain operational.
15. Forensic scores, hypotheses and confidence remain unchanged.
16. All existing and new regression tests pass.
17. Visual validation and documentation are completed.
18. No unrelated development phase has begun.

---

## 23. Final Codex response

Return:

**A. Baseline**

Branch, HEAD, working-tree state and starting tests.

**B. Artifact inventory**

Number of detectors inspected and artifacts classified by type.

**C. Registration**

Which artifact families support synchronization or overlay, and which do not.

**D. Workspace implementation**

New viewer, navigation, panels and comparison functionality.

**E. Evidence integration**

Supported evidence mappings and remaining gaps.

**F. Session integrity**

How stale artifact/image loads are prevented.

**G. Reference validation**

Instagram and Midjourney results and artifact coverage.

**H. Tests**

Exact pass, fail and skip counts.

**I. Visual validation**

Screenshots, platform behavior and DPI coverage.

**J. Limitations**

Unknown registrations, unavailable outputs and deferred functionality.

**K. Git status**

Changed and untracked files; confirmation that nothing was staged, committed or pushed.

**L. UI-5 readiness**

Any blockers to the structured Evidence Explorer.

---

## Strict constraints

- Do not change detector algorithms.
- Do not change numerical scoring.
- Do not change hypothesis selection.
- Do not change confidence-policy rules.
- Do not alter evidence-lineage logic.
- Do not reclassify provenance.
- Do not weaken UI-1 session safeguards.
- Do not replace UI-2's design system.
- Do not redesign the UI-3 Overview.
- Do not implement the full Evidence Explorer.
- Do not redesign Reports.
- Do not introduce unnecessary dependencies.
- Do not stage, commit, push, merge, tag, reset or stash.
- Preserve existing Git changes and excluded test assets.

**Core principle: A forensic visualization is meaningful only when its origin, geometry, reliability and relationship to the underlying evidence are understood. A visually convincing comparison must never substitute for a technically valid one.**

Implement UI-4, validate the workspace against actual detector artifacts, and deliver the requested documentation. Do not begin UI-5.
