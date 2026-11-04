# CODEX TASK — SignalLens UI-6: Provenance, OSINT & Reporting Modernization

## Mission

You are the principal Python engineer, senior PyQt6 desktop architect, digital-forensics specialist, forensic reporting architect and software quality engineer for SignalLens.

Implement **UI-6 — Provenance, OSINT & Reporting Modernization**, the sixth phase of SignalLens's GUI modernization.

The application now provides:

- **UI-1:** Investigation-session integrity, guarded worker callbacks, annotation revisions and consistent report snapshots.
- **UI-2:** Dark-first design system, reusable components and six-destination navigation.
- **UI-3:** Image-centered investigation Overview.
- **UI-4:** Image Forensics workspace with detector artifacts, registered synchronization and guarded overlays.
- **UI-5:** Evidence and Reasoning explorers, including lineage, corroboration, scorecard calculations and confidence-policy explanations.

UI-6 must complete the remaining two workspace destinations:

1. **Provenance** — metadata, declarations, verification status and contextual OSINT.
2. **Reports** — review, consistency checks and export of the current investigation.

The implementation must preserve the distinction between forensic measurements, provenance claims, contextual research and conclusions.

**Primary objective: Deliver professional provenance and reporting workflows in which every displayed or exported statement is traceable to the correct investigation, authoritative data and evidence limitations.**

Do not change forensic detector algorithms, scoring or confidence assignment.

Do not introduce new provenance-verification technologies during UI-6.

---

# Part A — Baseline, test discipline and repository protection

## 1. Verify repository state

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Windows desktop application

Latest reported baseline:

- Branch: `main`
- Last reported HEAD: `656df83`
- UI-5 implemented.
- Test rationalization completed.
- Final reported suite: **504 passing tests**.
- Zero failures, skips or warnings.
- Test-discipline policy introduced through `AGENTS.md`.

Verify actual branch, HEAD, working-tree state and test count.

Do not assume the latest changes are committed.

### Read mandatory instructions first

Read:

`AGENTS.md`

`doc/test_quality/TEST_DISCIPLINE.md`

`doc/test_quality/behavioral_coverage_matrix.md`

`doc/test_quality/rationalization_report.md`

These govern test development throughout UI-6.

### Mandatory testing discipline

Before creating any tests:

1. Search for existing tests covering the relevant behavior.
2. Identify authoritative test owners.
3. Reuse or extend existing coverage.
4. Add tests only for genuinely new behavior or demonstrated gaps.
5. Prefer shared fixtures and parameterization.
6. Avoid duplicating UI-1 session and worker tests.
7. Avoid recreating complete reference-image tests.
8. Report every added, removed or consolidated test group.

A net increase exceeding **10 collected tests** requires explicit justification.

This is a review threshold, not a hard cap.

Do not combine unrelated assertions into oversized tests to evade the threshold.

Run targeted tests during development and the complete suite at final validation.

### Repository protection

Preserve inherited changes.

Do not stage, commit, push, merge, tag, reset, stash or discard existing work.

Do not modify `test_images/` or generated forensic artifacts.

Do not introduce unnecessary dependencies.

---

## 2. Review existing architecture

Read:

`doc/gui_modernization/audit/`

`doc/gui_modernization/ui1/`

`doc/gui_modernization/ui2/`

`doc/gui_modernization/ui3/`

`doc/gui_modernization/ui4/`

`doc/gui_modernization/ui5/`

Prioritize:

- Investigation-session specification.
- Presentation contracts.
- OSINT/report consistency documentation.
- Workspace architecture.
- Design-system specification.
- Overview data mapping.
- Evidence and Reasoning presentation contracts.
- Cross-workspace navigation.
- Existing report and persistence behavior.

Inspect the actual production implementation, especially:

- `signallens_gui.py`
- `osint_dialogs.py`
- Settings integration
- Metadata summary modules
- ExifTool extraction
- Provenance presentation adapters
- Investigation-session modules
- Annotation revision handling
- Report generation and persistence
- Existing export interfaces

Use source code as the authority when documentation and implementation differ.

---

# Part B — Provenance architecture audit

## 3. Inventory current provenance information

Before implementing the workspace, identify all provenance-related data currently available.

Inspect:

- EXIF metadata.
- IPTC fields.
- XMP metadata.
- Software and processing declarations.
- Embedded generation prompts.
- AI-generation declarations.
- AI-enhancement declarations.
- C2PA-related metadata.
- Source-file properties.
- Metadata availability.
- Metadata extraction errors.
- Unknown or ambiguous provenance states.

Create a source mapping for each field.

| Field | Backend source | Recorded value | Trust status | Current UI location | Proposed presentation |
|---|---|---|---|---|---|

### Critical distinction

SignalLens may detect provenance-related metadata without verifying its authenticity.

Do not equate:

- Metadata presence.
- Metadata declaration.
- Detected C2PA-related fields.
- Cryptographically verified provenance.

These are different evidentiary states.

Do not infer verification from the existence of a metadata field.

---

## 4. Define provenance presentation semantics

Use explicit terminology for:

**Verified provenance**

Only when genuine verification has occurred and the current backend records that result.

**Unverified declaration**

A metadata assertion concerning generation, enhancement or processing that has not been authenticated.

**Ambiguous provenance**

Metadata that could reflect multiple processing histories.

**Missing provenance**

No meaningful provenance information is available.

**Unavailable extraction**

Metadata could not be read or evaluated.

**Unsupported verification**

A provenance mechanism is recognized but verification is not implemented or available.

### Important

Do not display "Verified" merely because C2PA-related data exists.

If SignalLens currently performs no cryptographic validation, the interface must explicitly communicate that limitation.

Missing provenance is not proof of authenticity or AI generation.

---

# Part C — Provenance workspace

## 5. Implement the Provenance destination

Replace the current transitional Provenance view with a structured workspace.

Suggested organization:

```text
┌────────────────────────────────────────────────────────────────┐
│ PROVENANCE                                                     │
│ Investigation identity · Source · Extraction status           │
├────────────────────────────────────────────────────────────────┤
│ PROVENANCE SUMMARY                                             │
│ Declaration · Verification · Availability · Limitations        │
├──────────────────────────────┬─────────────────────────────────┤
│ METADATA EXPLORER            │ SELECTED FIELD                  │
│                              │                                 │
│ EXIF                         │ Field name                      │
│ IPTC                         │ Recorded value                  │
│ XMP                          │ Source                          │
│ Software                     │ Interpretation                  │
│ Generation declarations      │ Trust status                    │
│ C2PA-related information     │ Limitations                     │
├──────────────────────────────┴─────────────────────────────────┤
│ CONTEXTUAL RESEARCH / OSINT                                    │
│ Notes · Sources · Annotations · Revision status                │
└────────────────────────────────────────────────────────────────┘
```

Adapt the layout to the current design system.

### Required capabilities

- Provenance summary.
- Structured metadata browsing.
- Field search/filter.
- Technical field detail.
- Recorded declaration status.
- Explicit verification status.
- Extraction limitations.
- Copyable technical values.
- Access to contextual OSINT.
- Navigation to related reasoning.

Do not build an entirely new metadata extraction engine.

---

## 6. Metadata Explorer

Implement a structured metadata table or tree.

Prefer Qt model/view components for potentially large metadata collections.

### Features

- Group by metadata namespace/source.
- Search field names and values.
- Select a field.
- Display its recorded source.
- Display its interpretation where available.
- Copy field names and values.
- Preserve original technical values.
- Display extraction failures appropriately.

### Data integrity

Do not silently normalize away meaningful metadata.

For example, retain technical identifiers and original declaration values where useful.

Human-readable labels may supplement technical values but must not replace them.

Avoid interpreting arbitrary software names as proof of AI generation.

### Performance

Metadata may contain large text values, binary payload descriptions or nested structures.

Avoid constructing thousands of widgets unnecessarily.

Use bounded previews and expandable detail views.

Do not display raw binary payloads as ordinary text.

---

# Part D — OSINT modernization

## 7. Audit the current OSINT workflow

Inspect all existing contextual research and annotation capabilities.

Identify:

- Editable fields.
- Source URLs.
- Research notes.
- User-entered classifications.
- Timestamp information.
- Existing dialog behavior.
- Persistence.
- Current report integration.
- Annotation revision semantics.

Determine which fields represent:

- User observations.
- External source claims.
- Research notes.
- Forensic analysis results.

Do not conflate these categories.

---

## 8. Integrate OSINT into the workspace

Provide a professional contextual research section in the Provenance destination.

Reuse existing OSINT functionality wherever practical.

### Required features

- View current annotations.
- Edit supported fields.
- Add or modify notes through existing contracts.
- Display annotation revision.
- Show whether changes are saved.
- Preserve source references where available.
- Maintain context when navigating between workspaces.

### Source attribution

Where external claims are recorded, preserve:

- Source reference.
- Original claim or note.
- User-entered context.
- Relevant timestamp, if recorded.

Do not invent missing source information.

### Critical separation

**OSINT information is contextual evidence, not an automatic forensic detector output.**

Changing OSINT notes must not silently:

- Change suspicious scores.
- Change benign scores.
- Reclassify hypotheses.
- Upgrade confidence.
- Rewrite detector observations.

If the existing application produces a separate contextual interpretation, label it as such.

---

## 9. Preserve annotation revision integrity

Reuse UI-1's annotation-revision system.

### Required scenarios

- User edits annotations after analysis.
- User cancels an edit.
- User switches investigations during editing.
- Stored annotations are loaded.
- A report is exported after OSINT changes.
- A previous report snapshot exists.
- Annotation persistence fails.

### Invariants

- Cancelled edits do not increment revisions.
- Committed edits advance the correct revision.
- No annotation leaks across investigations.
- Current display uses the intended revision.
- Export uses an internally consistent snapshot.
- Failed saves do not falsely appear successful.

Do not create another parallel annotation store.

---

# Part E — Reporting architecture audit

## 10. Inspect existing reporting formats

Inventory all currently supported outputs.

Determine:

- Export formats.
- Generated report content.
- File naming.
- Template handling.
- Image inclusion.
- Detector-artifact references.
- Summary narrative.
- Scorecard details.
- Provenance statements.
- OSINT appendix.
- Reasoning trace inclusion.
- Error handling.

Document current report fields and their sources.

| Report section | Current source | Investigation revision | Known limitation | UI-6 action |
|---|---|---|---|---|

Do not assume PDF, HTML, JSON or other formats are supported unless verified in source code.

Preserve existing export formats.

Do not introduce a large reporting framework.

---

# Part F — Reports workspace

## 11. Implement the Reports destination

Replace the current transitional Reports view with a structured reporting workspace.

Suggested organization:

```text
┌────────────────────────────────────────────────────────────────┐
│ REPORTS                                                        │
│ Investigation · Analysis revision · Annotation revision        │
├───────────────────┬────────────────────────────────────────────┤
│ REPORT OPTIONS    │ REPORT PREVIEW                             │
│                   │                                            │
│ Sections          │ Investigation summary                      │
│                   │                                            │
│ Existing formats  │ Primary forensic finding                   │
│                   │                                            │
│ Export location   │ Hypotheses and confidence                  │
│                   │                                            │
│ Export action     │ Evidence and limitations                   │
│                   │                                            │
│                   │ Provenance / OSINT                          │
├───────────────────┴────────────────────────────────────────────┤
│ Snapshot validity · Export status · Errors                     │
└────────────────────────────────────────────────────────────────┘
```

Use the existing design system.

The workspace should make the current report state understandable without changing established forensic content.

---

## 12. Implement report preview

Provide an inspectable preview of the current report content.

### Required behavior

- Show the current investigation identity.
- Show the relevant analysis revision.
- Show the annotation revision.
- Present the report sections actually supported by the exporter.
- Preserve recorded forensic conclusions.
- Preserve confidence and uncertainty.
- Distinguish OSINT notes from forensic findings.
- Display export readiness.
- Clearly communicate missing optional data.

### Critical requirement

**The preview and exported report must derive from the same authoritative snapshot.**

Do not create one report representation for the GUI and another unrelated representation for export.

Where different formatting is necessary, both must use the same report data contract.

### Scope limitation

Do not redesign every existing report template.

UI-6 may improve section presentation and consistency, but must not silently change the forensic meaning of report content.

---

## 13. Introduce a report presentation contract

Extend existing UI-1 report snapshot structures where necessary.

Suggested conceptual fields:

```python
@dataclass(frozen=True)
class ReportPresentation:
    session_id: str
    analysis_id: str
    analysis_revision: int
    annotation_revision: int
    report_sections: tuple
    export_formats: tuple[str, ...]
    ready: bool
    limitations: tuple[str, ...]
```

Adapt to current project conventions.

### Requirements

- Stable investigation identity.
- Explicit revision identity.
- Immutable or snapshot-based data.
- No recalculation of forensic scores.
- No new hypothesis selection.
- No reinterpretation of provenance claims.
- No hidden mutation of OSINT annotations.

Avoid unnecessary duplication of existing report models.

---

## 14. Report snapshot consistency

Implement or reuse revision-aware export handling.

### Required scenarios

**Scenario A — Annotation updated**

1. Analysis completes.
2. Report preview is generated.
3. OSINT annotation changes.
4. Previous preview becomes stale or refreshes.
5. Export uses the current intended snapshot.

**Scenario B — Reanalysis**

1. An investigation has completed results.
2. Reanalysis begins.
3. Old report data remains historical rather than current.
4. The new result becomes authoritative after completion.

**Scenario C — Investigation switch**

A report export started for image A must not silently become an export of image B.

**Scenario D — Export failure**

An export failure must not mark the report successfully saved.

**Scenario E — Stored investigation**

A stored result must export using its actual available fields without fabricating newer structured records.

### Source integrity

Report identity should be bound to the correct image and analysis result.

Where source hashes are available, preserve or reference them consistently.

---

# Part G — Reporting language and forensic safeguards

## 15. Preserve forensic interpretation

Audit report wording for misleading claims.

Specifically verify:

- High confidence is not described as a calibrated probability.
- Suspicious scores are not presented as AI-generation percentages.
- Localized editing is not equated with full synthetic generation.
- Camera compatibility is not described as proof of authenticity.
- Unverified generation declarations remain qualified.
- Missing metadata remains neutral.
- Unavailable detectors are not interpreted as negative evidence.
- OSINT claims are distinguished from measured observations.
- Contradictory and moderating evidence retain their proper roles.

### Important

UI-6 should not rewrite the reasoning engine's narratives.

Only correct presentation inconsistencies introduced by GUI or report adapters.

If source narratives contain substantive forensic errors, document them separately rather than silently changing the reasoning engine.

---

## 16. Report traceability

Where data is available, allow reports to reference:

- Investigation identity.
- Source image.
- Analysis profile.
- Primary finding.
- Hypothesis assessments.
- Evidence identifiers.
- Relevant detector artifacts.
- Provenance declarations.
- Confidence-policy rationale.
- Coverage limitations.
- Annotation revision.

Do not require every report to include the complete numerical ledger.

The report should provide appropriate summary information while preserving access to detailed forensic records through existing formats or references.

Avoid excessive technical output in the default human-readable report.

---

# Part H — Cross-workspace integration

## 17. Connect Provenance and Reports

Use existing UI-2 navigation and UI-5 cross-workspace contracts.

### From Overview

- Open provenance summary.
- Open report preview/export.

### From Evidence

- Open relevant provenance fields where authoritative associations exist.
- Preserve evidence selection when returning.

### From Reasoning

- Open supporting provenance declarations.
- Inspect report-relevant confidence explanations.

### From Provenance

- Open related reasoning.
- Open contextual OSINT editing.
- Open Reports.

### From Reports

- Return to Overview.
- Inspect relevant evidence.
- Inspect provenance.
- Review contextual annotations.

### Safeguards

- Preserve investigation identity.
- Preserve analysis revision.
- Preserve annotation revision.
- Reject stale navigation targets.
- Do not fabricate evidence relationships.
- Do not rerun forensic analysis.

---

# Part I — Legacy result compatibility

## 18. Support historical investigations

Some stored results may lack:

- New provenance presentation fields.
- Explicit verification status.
- Complete evidence lineage.
- Confidence-policy details.
- Annotation revisions.
- Source hashes.

### Required behavior

- Display available historical information.
- Mark unavailable fields explicitly.
- Preserve legacy narrative access.
- Preserve existing export compatibility.
- Avoid destructive migrations.
- Do not infer that missing verification fields imply successful verification.

If legacy content cannot be previewed reliably in a new structured form, provide an explicit fallback to the existing representation.

Document the limitation.

---

# Part J — Performance and accessibility

## 19. Desktop usability

Use UI-2's established design system.

Requirements:

- Resizable panels.
- Readable metadata tables.
- Copyable values.
- Searchable metadata.
- Clear editing state.
- Visible keyboard focus.
- Accessible status indicators.
- Consistent section headings.
- Long text handling.
- Progress and error feedback.
- No unnecessary modal dialogs.
- No misleading decorative analytics.

### Performance

- Avoid rebuilding large metadata trees after every small annotation change.
- Avoid repeated parsing of unchanged forensic result structures.
- Avoid expensive report generation on every navigation event.
- Avoid blocking the GUI during large exports.
- Use existing worker patterns where appropriate.

Preserve Qt thread-safety.

---

# Part K — Testing and validation

## 20. Mandatory test-coverage audit

Before writing new tests, consult:

`doc/test_quality/behavioral_coverage_matrix.md`

Identify existing authoritative coverage for:

- Session identity.
- Worker lifecycle.
- Annotation revisions.
- Report snapshot consistency.
- Metadata extraction.
- Provenance interpretation.
- Stored-result compatibility.
- Cross-workspace navigation.

Do not duplicate those tests.

Focus new coverage on UI-6-specific behavior.

### Suggested new test groups

**Provenance presentation**

- Verification versus declaration labeling.
- Metadata filtering.
- Missing/unavailable metadata.
- Source-field preservation.

**OSINT integration**

- Existing annotation contract connected to new workspace.
- Current revision visible after a committed edit.
- Cancelled edit leaves presentation unchanged.

**Report workspace**

- Preview and export consume the same snapshot.
- Annotation change invalidates preview.
- Investigation switch prevents wrong report export.
- Legacy report fallback.

**Navigation**

- Provenance and Reports receive the correct investigation context.
- Stale navigation requests are rejected.

### Test discipline requirements

- Search first.
- Reuse existing fixtures.
- Avoid duplicated full-pipeline image runs.
- Consolidate overlapping cases.
- Add only necessary tests.
- Justify any net increase above ten collected tests.

The final report must include:

| Test metric | Count |
|---|---:|
| Baseline collected | |
| Added | |
| Consolidated | |
| Removed | |
| Final collected | |
| Net change | |

Do not use test count as a measure of feature quality.

---

## 21. Reference-investigation validation

Use existing saved Instagram and Midjourney results where possible.

Current `normal`-profile reference values:

| Reference | Suspicious | Benign | Finding |
|---|---:|---:|---|
| Instagram | 21.32705 | 2.25 | High localized editing |
| Midjourney | 6.675 | 1.5 | Medium unverified synthetic context |

The purpose is to verify presentation and reporting consistency, not to rerun detector calibration.

For each case:

1. Load the recorded investigation.
2. Verify provenance presentation.
3. Verify confidence wording.
4. Verify missing/unverified status distinctions.
5. Apply a controlled OSINT annotation edit.
6. Confirm the annotation revision changes.
7. Confirm report preview updates.
8. Confirm export uses the correct snapshot.
9. Verify forensic scores and findings remain unchanged.

Do not modify original reference images or saved baseline artifacts.

---

# Part L — Native GUI and visual validation

## 22. Inspect the completed workspaces

Capture:

1. Empty Provenance view.
2. Populated metadata explorer.
3. Unverified generation declaration.
4. Missing metadata.
5. OSINT edit state.
6. Updated annotation revision.
7. Empty Reports view.
8. Populated report preview.
9. Export-ready state.
10. Stale preview after annotation change.
11. Export failure state.
12. Stored legacy investigation.

Save screenshots under:

`doc/gui_modernization/ui6/screenshots/`

Use native Windows rendering where available.

### Native DPI validation

Several previous phases documented unverified native Windows scaling.

Where possible, test:

- 100%.
- 125%.
- 150%.

Check:

- Main workspace.
- Metadata tables.
- Long text.
- Dialogs.
- Report preview.
- Splitter resizing.
- Focus/navigation.

Do not claim a DPI scale was verified without actually testing it.

If native testing is unavailable, document this as a release-validation requirement for UI-7.

---

# Part M — Documentation

## 23. Required deliverables

Create:

`doc/gui_modernization/ui6/`

### A. `provenance_data_inventory.md`

Authoritative field sources, trust categories and current capabilities.

### B. `provenance_workspace_design.md`

Layout, metadata browsing, verification terminology and limitations.

### C. `osint_workspace_integration.md`

Annotation editing, revisions, persistence and contextual separation.

### D. `report_contracts.md`

Report snapshot identity, revision semantics, preview/export relationships and supported formats.

### E. `report_consistency_validation.md`

Tests and scenarios proving preview/export synchronization.

### F. `legacy_compatibility.md`

Historical-result handling and fallback behavior.

### G. `cross_workspace_navigation.md`

Navigation contracts and session/revision safeguards.

### H. `implementation_report.md`

Architecture, changed files, components, compatibility and limitations.

### I. `visual_validation.md`

Screenshots, window sizes, DPI conditions and remaining issues.

### J. `regression_results.md`

Baseline, added/consolidated/removed tests, final totals and validation outcomes.

---

# Part N — Acceptance criteria

## 24. UI-6 Definition of Done

UI-6 is complete when:

1. Provenance has a functional structured workspace.
2. Recorded metadata fields are inspectable and searchable.
3. Provenance declaration and verification status are distinguished.
4. Missing and unavailable provenance are represented accurately.
5. OSINT annotations are accessible and editable through existing contracts.
6. Annotation revision integrity is preserved.
7. OSINT edits cannot silently change forensic findings.
8. Reports has a functional preview/export workspace.
9. Preview and export consume the same authoritative investigation snapshot.
10. Stale previews and obsolete export requests are handled safely.
11. Existing report formats remain compatible.
12. Legacy investigations remain accessible.
13. Cross-workspace navigation preserves investigation identity.
14. Existing forensic scores, hypotheses and confidence remain unchanged.
15. UI-1 session safeguards remain intact.
16. Existing regression coverage is preserved.
17. New tests comply with mandatory test discipline.
18. Visual and native-platform validation is documented.
19. Production functionality remains available.
20. No unrelated development phase has begun.

---

## 25. Final Codex response

Return:

**A. Baseline**

Branch, HEAD, working-tree state and starting test count.

**B. Provenance**

Structured metadata capabilities, declaration/verification semantics and limitations.

**C. OSINT**

Annotation editing, revision handling and separation from forensic findings.

**D. Reports**

Preview/export functionality, supported formats and snapshot guarantees.

**E. Legacy compatibility**

Handling of partial or historical results.

**F. Cross-navigation**

Supported routes and session consistency.

**G. Test discipline**

Existing coverage reused, new tests justified, added/consolidated/removed counts.

**H. Validation**

Final passed, failed and skipped tests.

**I. Visual inspection**

Screenshots, native Windows behavior and DPI coverage.

**J. Remaining limitations**

Unverified platform behavior, missing structured fields and deferred functionality.

**K. Git status**

Changed/untracked files and confirmation that nothing was staged, committed or pushed.

**L. UI-7 readiness**

Any blockers to final GUI validation and polish.

---

## Strict constraints

- Do not modify forensic detector algorithms.
- Do not change suspicious or benign scoring.
- Do not change hypothesis selection.
- Do not change confidence-policy rules.
- Do not alter evidence-lineage calculations.
- Do not implement C2PA cryptographic verification.
- Do not implement SynthID or new watermark detection.
- Do not change provenance classification semantics.
- Do not weaken UI-1 session safeguards.
- Do not replace UI-2's visual design system.
- Do not redesign UI-3, UI-4 or UI-5.
- Do not introduce unnecessary dependencies.
- Do not rewrite historical result files.
- Do not introduce unsupported export formats.
- Do not stage, commit, push, merge, tag, reset or stash.
- Preserve inherited work and excluded test assets.

**Core principle: Provenance claims, forensic measurements, contextual OSINT and final conclusions are different kinds of information. A professional forensic application must preserve those distinctions consistently across its interface and exported reports.**

Implement UI-6, validate the two completed workspaces, comply with mandatory test discipline and deliver the requested documentation. Do not begin UI-7.
