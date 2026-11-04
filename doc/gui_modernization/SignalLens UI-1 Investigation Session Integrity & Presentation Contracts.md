# CODEX TASK — SignalLens UI-1: Investigation Session Integrity & Presentation Contracts

## Mission

You are the principal Python engineer, PyQt6 desktop architect, software quality engineer and forensic application specialist for SignalLens.

Your task is to implement **UI-1 — Investigation Session Integrity & Presentation Contracts**, the first implementation phase of SignalLens's GUI modernization.

SignalLens recently completed its ten-point forensic reasoning-engine modernization. The application now has a structured, hypothesis-aware reasoning system with auditable scores, evidence lineage, corroboration controls and centralized confidence assignment.

A subsequent GUI architecture and usability audit recommended **Option B: Workspace Modernization**, retaining PyQt6, the existing controllers and the forensic analysis engine.

However, the audit identified correctness risks that must be addressed before building the new interface:

1. Image reselection and worker lifecycle handling can create stale-result risks.
2. OSINT edits can cause displayed conclusions and saved reports to diverge.
3. GUI components do not consistently consume structured reasoning data.
4. Investigation state is not sufficiently separated from widget state.
5. Future workspace components need stable, typed presentation contracts.

**Primary objective:** Establish a reliable investigation lifecycle and authoritative presentation layer without changing forensic analysis, scoring, hypothesis selection or confidence assignment.

This phase is about correctness and architecture, not appearance.

---

# Part A — Baseline and repository protection

## 1. Inspect the current repository

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Windows desktop
- Existing worker/controller architecture
- Structured reasoning and scorecard persistence

Latest reported baseline:

- Branch: `main`
- HEAD: `00c5eb2`
- 334 existing regression tests passing
- UI-0 audit completed
- Existing documentation modifications preserved
- No UI modernization implementation yet

Verify actual Git state rather than assuming these values remain current.

Before editing:

1. Record branch, HEAD and working-tree status.
2. Identify existing tracked modifications.
3. Identify untracked files.
4. Distinguish prior work from this task.
5. Run the baseline regression suite.
6. Review the UI-0 audit documentation.

Do not stage, commit, push, merge, tag, reset, stash or discard existing changes.

Do not overwrite inherited modifications.

Keep `test_images/` and generated forensic outputs excluded from Git.

---

## 2. Read the UI-0 audit

Study all documents under:

`doc/gui_modernization/audit/`

Prioritize:

- `executive_summary.md`
- `gui_architecture_inventory.md`
- `current_user_journey.md`
- `reasoning_visibility_matrix.md`
- `gui_architecture_recommendation.md`
- `signal_lens_design_concept.md`
- `modernization_roadmap.md`

Inspect the actual implementation rather than relying solely on the audit.

Relevant source areas include:

- `signallens_gui.py`
- `settings_dialog.py`
- `osint_dialogs.py`
- Worker/controller modules
- Summary and reporting modules
- Reasoning persistence
- Analysis-result serialization

Determine the exact current data flow before designing new abstractions.

---

# Part B — Establish an authoritative investigation session

## 3. Define investigation identity

Introduce a lightweight, typed investigation-session model.

Each investigation must have a stable identity that distinguishes it from previous and subsequent analyses.

The model should track:

- Session identifier.
- Selected image path or source reference.
- Optional canonical file identity.
- Analysis invocation identifier.
- Current lifecycle state.
- Analysis profile/configuration snapshot.
- Result identity/version.
- Current forensic result reference.
- OSINT annotation state/version.
- Report validity or synchronization state.
- Relevant timestamps where useful.

Do not duplicate large image arrays or detector payloads in the session model.

Use immutable snapshots or clearly controlled state transitions where appropriate.

### Example conceptual structure

```python
@dataclass(frozen=True)
class InvestigationIdentity:
    session_id: str
    image_path: str
    analysis_id: str | None
```

```python
@dataclass
class InvestigationSession:
    identity: InvestigationIdentity
    state: InvestigationState
    analysis_result: object | None
    analysis_revision: int
    annotation_revision: int
```

These examples are illustrative, not mandatory.

Adapt to the existing architecture.

### Requirements

- Session IDs must be unique for distinct investigations.
- Reopening the same image may create a new investigation.
- Analysis IDs must distinguish separate runs within one investigation.
- Results must be associated with the invocation that produced them.
- Old worker callbacks must not mutate the active investigation.
- A selected filename alone must not serve as sufficient result identity.

---

## 4. Define an explicit lifecycle state machine

Establish a finite set of investigation states.

Suggested states:

- `EMPTY`
- `IMAGE_SELECTED`
- `ANALYZING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

Additional states may be justified by the existing architecture.

Define valid transitions.

Example:

```text
EMPTY
  → IMAGE_SELECTED
  → ANALYZING
  → COMPLETED

ANALYZING
  → FAILED

ANALYZING
  → CANCELLED

COMPLETED
  → ANALYZING
```

The exact transition model must account for the current application's real behavior.

### Critical cases

- User selects a new image while analysis is running.
- User selects the same image again.
- User begins a second analysis with different settings.
- Worker completion arrives after selection changes.
- Worker failure arrives after a new session begins.
- An old progress signal arrives after a newer invocation starts.
- Cancellation is requested but the worker has not stopped.
- Application closes during analysis.
- Analysis completes while a dialog is open.
- A stored result is loaded without running an analysis.

### Invariants

**Only callbacks belonging to the active analysis invocation may update active analysis state.**

A callback from an obsolete invocation must not overwrite:

- Selected image.
- Active results.
- Status.
- Progress.
- Summary.
- Detector panels.
- Reasoning presentation.
- Report state.

Design deterministic handling for obsolete callbacks.

---

# Part C — Worker lifecycle integrity

## 5. Audit current worker/controller ownership

Inspect how the current GUI launches, owns, replaces and cleans up analysis workers.

Document:

- Worker creation.
- Thread creation.
- Signal connections.
- Completion handling.
- Error handling.
- Progress handling.
- Cancellation support, if any.
- Thread shutdown.
- Resource ownership.
- Widget destruction and application exit.

Identify whether current code can:

- Start overlapping analyses.
- Replace a worker reference while a previous worker is active.
- Disconnect or delete a live worker prematurely.
- Retain obsolete signal connections.
- Update destroyed widgets.
- Leave threads running during application shutdown.

### Required implementation

Introduce a reliable ownership and callback-validation strategy.

Prefer existing Qt threading conventions and project patterns.

Do not invent cancellation support that the backend cannot safely provide.

If the worker is not cooperatively cancellable, distinguish:

**Logical cancellation**

The invocation is no longer active and its results cannot be published.

**Physical cancellation**

The worker is actually stopped through a supported, safe cancellation mechanism.

A logically cancelled worker may continue executing until completion, but must remain safely owned and cleaned up.

Do not use unsafe thread termination.

Do not block the GUI thread while waiting for lengthy forensic processing.

### Thread-safety requirement

All GUI state and widgets must be modified only on the GUI thread.

Worker threads should emit results or progress through Qt-safe mechanisms.

---

## 6. Guard all asynchronous callbacks

Introduce explicit active-invocation validation for:

- Progress.
- Status updates.
- Successful completion.
- Errors.
- Cancellation acknowledgment.
- Result persistence notifications, where applicable.

Validation must use immutable invocation identity captured when the worker is launched.

Do not identify the invocation by consulting a mutable `self.worker` reference at callback execution time.

### Acceptance scenarios

**Scenario A — Late completion**

1. Analyze image A.
2. Select image B.
3. Image A completes.
4. Image A's result must not appear as image B's result.

**Scenario B — Late progress**

1. Start analysis A.
2. Start or select investigation B.
3. A emits progress.
4. B's progress and status must remain unchanged.

**Scenario C — Reanalysis**

1. Analyze image A using profile X.
2. Reanalyze image A using profile Y.
3. The earlier invocation completes last.
4. The newer invocation must remain authoritative.

**Scenario D — Late error**

An obsolete worker failure must not replace the status of a newer successful investigation.

**Scenario E — Application closure**

Active workers must be managed safely during shutdown without accessing destroyed widgets or leaving orphaned Qt threads.

Implement deterministic tests for these cases.

Avoid timing-sensitive sleeps where signal-driven synchronization can be used.

---

# Part D — Result ownership and revision consistency

## 7. Separate raw analysis results from presentation state

The existing forensic results must remain authoritative.

Do not let individual GUI widgets become independent stores of forensic truth.

Establish a clear distinction between:

### Raw forensic result

The output produced by the analysis engine.

### Investigation state

Which image and analysis invocation are active.

### Annotations

User-supplied context or OSINT information associated with the investigation.

### Presentation model

A structured, read-only representation of relevant forensic findings for display.

### Report snapshot

The exact combination of forensic result and contextual annotations used for export.

### Required behavior

The same investigation identity and revision information must be available to:

- Current summary.
- Future Overview workspace.
- Detector views.
- Evidence Explorer.
- Reasoning Explorer.
- Provenance view.
- Report generator.

Do not introduce a second forensic decision engine in the presentation layer.

---

## 8. Prevent OSINT synchronization defects

The UI-0 audit found that OSINT changes could leave the displayed conclusion and saved report inconsistent.

Inspect the actual current OSINT workflow.

Identify:

- Which fields are editable.
- Where annotations are stored.
- Whether edits affect the forensic analysis result.
- Whether the summary is regenerated.
- Whether existing report data is cached.
- Whether saved reports include annotations.
- Whether stale views are detectable.

### Required solution

Establish explicit annotation revisions.

When an annotation changes:

1. The annotation revision must advance.
2. The current investigation must recognize the change.
3. Any presentation model depending on annotations must be refreshed or marked stale.
4. Any report snapshot depending on annotations must be invalidated or regenerated.
5. A newly exported report must use the intended current revision.

### Critical distinction

**OSINT annotations must not silently change detector outputs, numerical scores or forensic confidence.**

If the existing system deliberately uses OSINT in a separate contextual narrative, preserve that distinction and document it.

Do not allow post-analysis annotation editing to silently recalculate forensic conclusions.

If annotations materially influence some existing displayed contextual assessment, make that relationship explicit and ensure all dependent views update consistently.

### Required tests

- Editing annotations after analysis.
- Editing annotations before report export.
- Repeated OSINT edits.
- Cancelling an OSINT dialog without saving.
- Switching investigations with unsaved dialog content.
- Exporting after a revision change.
- Loading a stored investigation containing annotations.
- Detecting and avoiding stale report snapshots.

---

# Part E — Presentation contracts

## 9. Introduce typed, read-only presentation models

The new workspace should not parse arbitrary narrative strings to extract forensic meaning.

Create a small set of typed presentation contracts, derived from existing structured results.

Use frozen dataclasses or another lightweight existing project convention.

Suggested modules:

- `investigation_session.py`
- `investigation_presenters.py`
- `presentation_models.py`

These names are illustrative.

Avoid unnecessary package restructuring.

### A. Investigation summary

```python
@dataclass(frozen=True)
class InvestigationSummaryView:
    session_id: str
    image_name: str
    primary_hypothesis: str | None
    primary_finding: str | None
    confidence_tier: str | None
    status: str
    limitations: tuple[str, ...]
```

### B. Hypothesis assessment

```python
@dataclass(frozen=True)
class HypothesisView:
    hypothesis_id: str
    finding: str
    confidence_tier: str
    supporting_evidence: tuple[str, ...]
    contradicting_evidence: tuple[str, ...]
    moderating_evidence: tuple[str, ...]
```

### C. Evidence item

```python
@dataclass(frozen=True)
class EvidenceView:
    evidence_id: str
    label: str
    role: str
    reliability: str | None
    source_detector: str | None
    lineage_reference: str | None
```

### D. Provenance information

```python
@dataclass(frozen=True)
class ProvenanceView:
    declaration_status: str
    verification_status: str
    description: str
    limitations: tuple[str, ...]
```

### E. Investigation snapshot

```python
@dataclass(frozen=True)
class InvestigationViewSnapshot:
    session_id: str
    analysis_id: str
    analysis_revision: int
    annotation_revision: int
    summary: InvestigationSummaryView
    hypotheses: tuple[HypothesisView, ...]
    evidence: tuple[EvidenceView, ...]
    provenance: ProvenanceView
```

Adapt fields to existing production schemas.

Do not invent unavailable forensic data.

### Requirements

- Fields are derived from authoritative structured results.
- Unknown or unavailable values remain explicit.
- Heuristic numerical scores are not converted into probabilities.
- Confidence labels are consumed, never recomputed.
- Hypothesis selection is consumed, never repeated.
- Evidence roles retain their original semantics.
- Provenance verification status is not inferred from metadata presence.
- Existing result serialization remains compatible.
- Presentation models can be built without constructing GUI widgets.

---

## 10. Build a presentation adapter

Implement a narrow adapter that transforms current analysis and reasoning results into the presentation contracts.

The adapter should:

- Accept existing result objects or persisted structures.
- Read current hypothesis assessments.
- Read the authoritative confidence-policy output.
- Preserve supporting, contradicting and moderating evidence.
- Expose reliability and coverage limitations.
- Preserve source identifiers and lineage references.
- Expose provenance status.
- Provide stable identifiers suitable for future Qt models.
- Handle missing optional fields safely.

### Explicit prohibitions

The adapter must not:

- Run detectors.
- Calculate suspicious scores.
- Apply confidence thresholds.
- Reorder decision routes.
- Select a different primary hypothesis.
- Reclassify generation metadata.
- Invent reliability values.
- Present missing evidence as negative evidence.

If structured fields are unavailable, expose an explicit unknown or unavailable state instead of extracting speculative meanings from prose.

---

## 11. Design contracts for future Qt views

Specify how future GUI components will consume presentation snapshots.

Recommended principles:

- One active investigation session.
- Immutable or versioned result snapshots.
- Qt signals for lifecycle and snapshot changes.
- Read-only presentation models.
- No direct mutation of forensic results by UI widgets.
- Explicit session identity on all result-related updates.
- Shared structured data across tabs.
- Stable evidence IDs for cross-navigation.

A future Evidence Explorer should be able to select an evidence item and open a related detector view using a stable ID.

However, do not implement the Evidence Explorer in UI-1.

Only establish the data contracts required for it.

---

# Part F — Minimal current-GUI integration

## 12. Integrate session ownership into the existing GUI

Modify the current application only as necessary to use authoritative session state.

The existing GUI must remain recognizable and functional.

### Required changes

- Image selection creates or updates the correct investigation identity.
- Analysis launch creates a new invocation identity.
- Worker callbacks validate invocation ownership.
- Completed analysis results belong to the correct investigation.
- Summary refreshes use the active result.
- OSINT changes advance annotation revisions.
- Report exports use a consistent result/annotation snapshot.
- Reanalysis invalidates outdated derived presentation state.
- Loading stored results establishes a coherent investigation session.

### Do not implement yet

- New sidebar navigation.
- Modern dashboard.
- New theme.
- Image comparison workspace.
- Evidence Explorer.
- Reasoning visualization.
- Redesigned provenance panel.
- New report layout.

These belong to later phases.

### UI feedback

Minimal status improvements are permitted where required for correctness.

For example:

- Analysis running.
- Previous result superseded.
- No active result.
- Report snapshot refreshed.
- Analysis failed.

Do not begin general visual restyling.

---

# Part G — Failure handling and persistence

## 13. Define failure behavior

Review and implement explicit handling for:

- Invalid image selection.
- Unsupported image.
- Missing source file.
- Analysis failure.
- Worker shutdown failure.
- Corrupted stored result.
- Missing reasoning fields.
- Annotation persistence failure.
- Report-generation failure.
- Export while analysis is running.

Ensure that failures do not leave the GUI presenting results from the wrong investigation.

Where appropriate, preserve an earlier completed result as historical data without presenting it as the current result.

Do not silently replace failures with fabricated forensic findings.

---

## 14. Preserve existing storage compatibility

Inspect current saved-result and report formats.

New investigation identifiers and revision metadata should be introduced compatibly.

If legacy stored investigations lack session identifiers:

- Define a deterministic or explicit migration-on-load strategy.
- Preserve their forensic contents.
- Avoid destructive file migration.
- Do not pretend historical revision metadata existed.

If existing report generators accept mutable result dictionaries, introduce safe snapshots or explicit revision checking without a broad reporting rewrite.

Document compatibility and migration behavior.

---

# Part H — Regression testing

## 15. Preserve all existing tests

The latest reported baseline contains **334 passing tests**.

Run the full suite before and after implementation.

Add dedicated tests for the new lifecycle and presentation contracts.

### Session tests

- Unique session IDs.
- Multiple analyses of one image.
- Separate investigations of one file.
- Correct initial state.
- Valid lifecycle transitions.
- Invalid transition handling.
- Failure recovery.
- Reanalysis state reset.
- Stored-result loading.

### Worker tests

- Late completion ignored.
- Late progress ignored.
- Late error ignored.
- Old invocation cannot replace new result.
- Obsolete callbacks cannot update widgets.
- Correct worker cleanup.
- Safe application shutdown.
- No GUI-thread violations.

### OSINT consistency tests

- Annotation revision increments.
- Cancelled edits do not increment revision.
- Presentation refresh after committed edits.
- Report export uses current annotations.
- Stale cached reports are invalidated.
- Switching investigations does not transfer annotations.
- Stored annotations load correctly.

### Presentation-contract tests

- Complete structured result.
- Missing optional reasoning fields.
- Low-confidence/inconclusive outcome.
- Separate hypothesis assessments.
- Evidence role preservation.
- Confidence-tier preservation.
- Provenance verified/unverified/unknown distinction.
- Unavailable detector coverage.
- Lineage-reference preservation.
- Deterministic snapshot construction.
- No alteration of original results.

### Integration tests

- Existing summary remains usable.
- Existing report export remains usable.
- Existing controller signals remain compatible.
- GUI can display current and loaded results.
- Existing reasoning conclusions remain unchanged.

Prefer deterministic Qt signal tests rather than arbitrary time delays.

Avoid adding new dependencies where existing Qt and Python testing facilities are sufficient.

---

# Part I — Real-image verification

## 16. Run the reference images

Use the established headless pipeline where available.

### Instagram reference

`test_images/insta_fake/Curvy Leggings Outfit.jpg`

Expected existing baseline:

- Suspicious score: 20.47705
- Benign score: 2.25
- High-confidence localized-editing finding

### Midjourney reference

`test_images/midjourney/theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png`

Expected existing baseline:

- Suspicious score: 5.4
- Benign score: 1.5
- Medium-confidence unverified synthetic-generation declaration

The purpose of these tests is to establish that GUI/session changes do not modify forensic outcomes.

Additionally:

1. Build presentation snapshots from each result.
2. Validate consistency between the source hypothesis assessments and the presentation contracts.
3. Confirm confidence and evidence roles are unchanged.
4. Confirm unavailable detectors remain explicitly unavailable.
5. Confirm report snapshots refer to the intended image and result.

Do not modify test images.

Do not change forensic scoring to match expected outcomes.

---

# Part J — Documentation and deliverables

## 17. Required documentation

Create:

`doc/gui_modernization/ui1/`

With the following files.

### A. `session_lifecycle_specification.md`

Document:

- Session identity.
- Analysis invocation identity.
- State transitions.
- Cancellation semantics.
- Worker ownership.
- Stale callback handling.
- Shutdown behavior.

Include a state-transition diagram.

### B. `presentation_contracts.md`

Document:

- Data classes or types.
- Field provenance.
- Required and optional fields.
- Unknown/unavailable handling.
- Revision semantics.
- Future GUI consumption patterns.

### C. `osint_report_consistency.md`

Explain:

- Current OSINT workflow.
- Original inconsistency.
- Revision tracking.
- Refresh/invalidation behavior.
- Export snapshot guarantees.

### D. `implementation_report.md`

List:

- Source files changed.
- New classes/functions.
- Architectural decisions.
- Compatibility.
- Deviations from the proposed design.
- Remaining limitations.

### E. `regression_results.md`

Include:

- Baseline tests.
- Final tests.
- New tests.
- GUI lifecycle test results.
- Reference-image comparisons.
- Known unsupported cases.

---

# Part K — Final validation and reporting

## 18. Acceptance criteria

UI-1 is complete only when:

1. Every active investigation has an explicit identity.
2. Each analysis invocation has a separate identity.
3. Obsolete worker callbacks cannot overwrite active state.
4. Worker ownership and shutdown are safe.
5. Image reselection has deterministic behavior.
6. Reanalysis cannot publish results from the wrong invocation.
7. OSINT edits cannot silently desynchronize displayed and exported investigation content.
8. Report exports use a consistent investigation revision.
9. Structured presentation models expose existing reasoning evidence without reinterpreting it.
10. Future workspace components can consume these models without direct access to detector/scoring internals.
11. Existing forensic reasoning behavior remains unchanged.
12. Existing GUI functionality remains operational.
13. All regression tests pass.
14. Both reference images retain their established forensic conclusions.
15. Existing Git changes remain preserved.

---

## 19. Final Codex response

Return:

**A. Baseline**

Current branch, HEAD and inherited changes.

**B. Session architecture**

New identity and lifecycle model.

**C. Worker safety**

How stale results, progress and errors are prevented.

**D. OSINT/report consistency**

How revisions and report snapshots remain synchronized.

**E. Presentation contracts**

New structured models and their data sources.

**F. GUI integration**

Current widgets/controllers changed and their behavior.

**G. Testing**

Baseline and final test counts, failures and skips.

**H. Reference images**

Confirmation of unchanged forensic outcomes.

**I. Limitations**

Any remaining known lifecycle, persistence or UI integration risks.

**J. Git status**

Changed files and confirmation that no staging, commits or pushes occurred.

---

## Final instructions

Implement the smallest reliable architecture that satisfies the requirements.

Avoid introducing unnecessary abstractions.

Prefer existing Python and PyQt6 facilities.

Do not replace the current GUI.

Do not redesign the visual theme.

Do not modify the forensic reasoning engine.

Do not recalculate confidence or scores in UI code.

Do not stage, commit, push or publish.

**Core principle: Every displayed finding, detector visualization, annotation and exported report must belong to the correct investigation and derive from the same authoritative analysis state.**

Complete UI-1, validate the result and report the implementation. Do not begin UI-2.
