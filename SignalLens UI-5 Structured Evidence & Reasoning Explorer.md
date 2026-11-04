# CODEX TASK — SignalLens UI-5 Structured Evidence & Reasoning Explorer

## Mission

You are the principal Python engineer, senior PyQt6 desktop architect, digital-image forensics specialist, explainable-AI architect and forensic software UX designer for SignalLens.

Implement **UI-5 — Structured Evidence & Reasoning Explorer**, the fifth phase of the SignalLens GUI modernization.

SignalLens now has:

- **UI-1:** Authoritative investigation sessions, invocation identity, worker lifecycle safeguards, annotation revisions and immutable presentation contracts.
- **UI-2:** A dark-first design system, six-destination workspace navigation and reusable components.
- **UI-3:** An image-centered investigation Overview with primary findings, hypothesis summaries, evidence and limitations.
- **UI-4:** A forensic image-inspection workspace with artifact navigation, independent comparison, registered synchronization, guarded overlays and evidence links.

The underlying reasoning engine has also completed its original ten-point modernization, including:

- Candidate-based decision routing.
- Separate forensic hypothesis assessments.
- Structured provenance interpretation.
- Hypothesis-specific supporting, contradicting and moderating evidence.
- Reliable treatment of unavailable measurements.
- Mathematically reconstructable scorecards.
- Evidence lineage and numerical deduplication.
- Lineage-aware corroboration.
- Centralized confidence assignment.
- Detailed reasoning traces.

**UI-5 must expose these capabilities through a professional, navigable forensic investigation interface.**

The objective is not to display raw JSON in a more attractive format.

The objective is to make the relationship between observations, evidence, hypotheses, numerical contributions, confidence and final findings understandable and auditable.

Do not modify the forensic reasoning engine.

---

# Part A — Baseline and architecture review

## 1. Verify the repository

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Windows desktop application

Latest reported baseline:

- UI-4 implemented.
- 468 automated tests passed.
- Zero failed or skipped.
- UI-4 changes had not yet been committed at the time of the previous report.
- Native Windows DPI review remains outstanding.

Verify the actual:

1. Branch.
2. HEAD commit.
3. Working-tree state.
4. Tracked and untracked modifications.
5. Existing regression-test count.
6. Presence of UI-1 through UI-4 implementations.

Do not assume UI-4 is committed.

Record all inherited modifications.

### Repository protection

Do not:

- Stage files.
- Commit.
- Push.
- Merge.
- Tag.
- Reset.
- Stash.
- Delete generated forensic artifacts.
- Modify reference images.
- Discard inherited changes.

Keep `test_images/` and generated forensic outputs excluded from Git.

Make UI-5 changes independently reviewable where practical.

---

## 2. Read existing architecture documentation

Review:

`doc/gui_modernization/audit/`

`doc/gui_modernization/ui1/`

`doc/gui_modernization/ui2/`

`doc/gui_modernization/ui3/`

`doc/gui_modernization/ui4/`

Prioritize:

- `reasoning_visibility_matrix.md`
- `presentation_contracts.md`
- `session_lifecycle_specification.md`
- `workspace_architecture.md`
- `design_system_specification.md`
- `overview_data_mapping.md`
- `artifact_contracts.md`
- `artifact_evidence_mapping.md`
- `session_and_async_integrity.md`
- UI-4 implementation and regression reports.

Also inspect the original reasoning-engine modernization reports, especially:

- The final ten-point acceptance audit.
- Phase 2A scorecard documentation.
- Phase 2B evidence dependency, lineage and deduplication reports.
- Phase 3 confidence-policy documentation.

Treat the current production implementation as authoritative.

Do not assume the documentation reflects every subsequent source change.

---

# Part B — Structured reasoning inventory

## 3. Audit current reasoning outputs

Before implementing the explorers, inspect all relevant current result objects and persisted data structures.

Identify the authoritative sources for:

### Hypothesis assessments

- Synthetic origin.
- Localized editing.
- Camera-acquisition compatibility.
- Primary hypothesis.
- Secondary hypotheses.
- Finding specificity.
- Confidence tiers.

### Evidence

- Evidence identifiers.
- Detector identifiers.
- Supporting evidence.
- Contradicting evidence.
- Moderating evidence.
- Evidence reliability.
- Evidence availability.
- Evidence specificity.
- Evidence lineage.
- Related artifact identifiers.

### Scorecard

- Raw numerical contributions.
- Base scores.
- Reliability adjustments.
- Numerical deduplication.
- Domain bonuses.
- Mechanism terms.
- Penalties and caps.
- Suspicious and benign totals.
- Calculation reconciliation.

### Corroboration

- Source-diversity requirements.
- Shared-ancestry checks.
- Compound-mechanism gates.
- Accepted corroboration.
- Rejected corroboration.
- Reasons for gate outcomes.

### Confidence

- Authoritative confidence tier.
- Confidence-policy rule.
- Supporting evidence.
- Contradicting evidence.
- Moderating evidence.
- Reliability restrictions.
- Coverage limitations.

### Decision trace

- Candidate findings.
- Route evaluations.
- Selected primary finding.
- Secondary findings.
- Rejected or superseded candidates.
- Selection rationale.

### Provenance and coverage

- Declared generation information.
- Verification status.
- Missing metadata.
- Unavailable or rejected detectors.
- Relevant quality limitations.

### Required output

Create a structured source inventory:

| Data category | Backend source | Persistence path | Current UI contract | Missing fields | Recommended presentation |
|---|---|---|---|---|---|

Identify which data already exists in UI-1's presentation contracts and which requires compatible contract extensions.

Do not implement duplicate reasoning logic to fill missing fields.

---

# Part C — Design objectives

## 4. Define the investigative workflow

UI-5 must support two distinct but connected questions.

### Evidence Explorer

**What was observed, where did the observation originate, and how should it be interpreted?**

### Reasoning Explorer

**How did SignalLens combine the observations to arrive at its findings and confidence assessments?**

The interface must allow investigators to progress from a high-level conclusion toward increasingly detailed technical explanations.

Use progressive disclosure.

Avoid displaying the full reasoning trace as an unstructured wall of text.

### Required investigative path

An investigator should be able to move through:

1. Primary finding.
2. Relevant hypothesis.
3. Supporting or contradicting evidence.
4. Original detector observation.
5. Related visualization, if available.
6. Evidence reliability and limitations.
7. Corroboration and lineage.
8. Numerical contribution.
9. Confidence-policy rule.
10. Final synthesis.

This path must preserve the active investigation and avoid changing forensic results.

---

# Part D — Evidence Explorer

## 5. Implement the Evidence workspace

Replace the existing Evidence placeholder or transitional content with a structured explorer.

Suggested layout:

```text
┌────────────────────────────────────────────────────────────────┐
│ EVIDENCE EXPLORER                                              │
│ Investigation · Active hypothesis · Coverage                   │
├───────────────────┬────────────────────────────────────────────┤
│ FILTERS           │ EVIDENCE LIST                              │
│                   │                                            │
│ Hypothesis        │ Evidence item 01                           │
│  Synthetic        │   Supporting · Reliable                    │
│  Editing          │                                            │
│  Camera           │ Evidence item 02                           │
│                   │   Moderating · Limited                     │
│ Role              │                                            │
│  Supporting       │ Evidence item 03                           │
│  Contradicting    │   Contradicting · Reliable                  │
│  Moderating       │                                            │
│                   │                                            │
│ Detector          │                                            │
│ Availability      │                                            │
├───────────────────┴────────────────────────────────────────────┤
│ SELECTED EVIDENCE DETAIL                                       │
│ Source · Observation · Reliability · Lineage · Related artifact│
└────────────────────────────────────────────────────────────────┘
```

Adapt the design to the actual UI-2 workspace shell and available screen space.

### Required capabilities

- Display structured evidence items.
- Filter by hypothesis.
- Filter by evidence role.
- Filter by detector or evidence family.
- Filter by availability or reliability where supported.
- Select an evidence item.
- Inspect its structured details.
- Open associated forensic artifacts.
- Open related reasoning information.
- Preserve stable selection when possible.

Use actual backend evidence IDs.

Do not invent evidence categories based on presentation wording.

---

## 6. Preserve hypothesis-specific evidence roles

Evidence roles must remain relative to a hypothesis.

A single observation may:

- Support one hypothesis.
- Moderate another.
- Be irrelevant to a third.

The Evidence Explorer must not present every observation as universally supporting or contradicting AI generation.

### Required behavior

When the active hypothesis changes:

- Evidence roles update from authoritative assessments.
- Supporting and contradicting evidence remain correctly scoped.
- Irrelevant observations do not become fabricated contradictions.
- Evidence details preserve their original detector source.
- Reliability information is retained.

### Important

Do not reclassify evidence in the GUI.

If the backend does not establish a relationship, display the association as unavailable rather than inferring one.

---

## 7. Evidence detail panel

Each evidence item should expose relevant structured information.

Where available:

- Evidence identifier.
- Human-readable label.
- Technical description.
- Detector or analysis stage.
- Hypothesis association.
- Evidence role.
- Original observation.
- Reliability status.
- Availability status.
- Limitations.
- Lineage references.
- Numerical contribution references.
- Related forensic artifacts.

### Interpretation

Clearly distinguish:

**Measured observation**

What the detector actually recorded.

**Derived inference**

How SignalLens interprets that observation.

**Hypothesis relevance**

Which forensic explanation the inference supports or limits.

Do not collapse these into one unexplained statement.

---

# Part E — Evidence lineage

## 8. Implement lineage inspection

Use the existing evidence-lineage registry and persisted lineage records.

The purpose is to show how derived signals relate to their underlying observations.

### Required functionality

For a selected evidence item, display:

- Direct parents.
- Direct descendants where available.
- Evidence family.
- Shared measurement ancestry.
- Composite-signal status.
- Relevant source-diversity limitations.

Use stable IDs and structured relationships.

### Preferred initial visualization

A hierarchical tree or dependency table is acceptable.

Do not build a complex graph-rendering framework unless the current data and Qt implementation justify it.

The priority is correctness and readability.

### Critical distinction

**Shared computational ancestry does not automatically prove complete statistical redundancy.**

The UI must distinguish:

- Confirmed duplicate numerical credit.
- Shared computational dependency.
- Potential statistical correlation.
- Distinct incremental measurements.

Only display classifications that the existing backend or documented audit actually supports.

Do not invent independence scores or correlation coefficients.

---

## 9. Lineage navigation

Where supported:

- Select a parent signal.
- Select a descendant signal.
- Navigate to related evidence.
- Open the corresponding detector artifact.
- Return to the original evidence selection.

Maintain deterministic navigation history where practical.

### Required safeguard

Do not assume every lineage node corresponds to a user-visible evidence item.

Some nodes may represent intermediate calculations or unavailable measurements.

Display such nodes appropriately without creating fictional evidence.

---

# Part F — Reasoning Explorer

## 10. Implement the Reasoning workspace

Replace the existing reasoning placeholder or transitional view with a structured inspection interface.

Suggested sections:

1. Hypothesis assessments.
2. Candidate findings and route decisions.
3. Corroboration.
4. Confidence-policy explanation.
5. Numerical scorecard.
6. Raw trace access.

Use tabs, collapsible panels or another suitable progressive-disclosure structure.

Avoid excessive nesting.

Keep the primary finding and active hypothesis visible while inspecting detailed calculations.

---

## 11. Hypothesis assessment panel

Display the authoritative structured assessment for each forensic hypothesis.

Include:

- Hypothesis.
- Finding.
- Confidence.
- Supporting evidence.
- Contradicting evidence.
- Moderating evidence.
- Reliability limitations.
- Relevant rationale.

The interface must preserve the possibility that several hypotheses are simultaneously supported.

Do not turn the three hypothesis families into an exclusive probability distribution.

Do not create percentage charts.

The primary hypothesis must be clearly distinguished from secondary findings.

---

## 12. Candidate findings and decision routes

Expose the actual decision trace.

Where recorded, show:

- Route identifier.
- Candidate finding.
- Eligibility or match state.
- Relevant conditions.
- Selection status.
- Selection rationale.
- Reason for non-selection.

### Critical distinction

A candidate that was evaluated but not selected is not necessarily forensically disproven.

Use terminology such as:

- Selected.
- Not selected.
- Inconclusive.
- Ineligible.
- Superseded.

Only when supported by the actual trace.

Do not fabricate route outcomes.

### Determinism

Preserve the recorded route order or explicit ordering metadata.

Do not reorder findings based on arbitrary UI preferences when that changes the meaning of the trace.

---

# Part G — Numerical scorecard audit

## 13. Expose score calculations

Create a structured, inspectable scorecard view.

The purpose is to make existing calculations independently understandable.

### Display

- Suspicious total.
- Benign total.
- Contributing evidence.
- Base weights.
- Reliability adjustments.
- Deduplication adjustments.
- Domain bonuses.
- Mechanism terms.
- Penalties.
- Final contributions.
- Reconciliation status.

Use existing Phase 2A and Phase 2B.4 calculation records.

### Suggested structure

```text
SCORECARD AUDIT

Suspicious total: [recorded value]
Benign total:     [recorded value]

Contribution ledger
─────────────────────────────────────────────────────
Evidence     Raw    Dedup.    Reliability    Final
Signal A     ...    ...       ...            ...
Signal B     ...    ...       ...            ...

Domain bonuses
Mechanism terms
Penalties and caps
Final reconciliation
```

Do not assume every historical result contains every ledger field.

### Mathematical integrity

The interface should display recorded calculations and their existing audit status.

If sufficient inputs exist, it may independently check arithmetic reconciliation using the existing documented scorecard formula, but this must be a pure validation function and must never replace the authoritative score.

Do not implement a competing scoring engine.

Do not change any stored contribution.

### Numerical accuracy

- Preserve adequate decimal precision.
- Avoid misleading rounding.
- Support copyable exact values.
- Clearly distinguish raw and adjusted contributions.
- Explain suppressed duplicate contributions.
- Mark incomplete historical ledgers.

### Important

A suspicious score of 6.675 is not a 66.75% probability.

Never display heuristic scores as calibrated probabilities.

---

# Part H — Corroboration and confidence

## 14. Corroboration audit panel

Display existing corroboration decisions.

Include where available:

- Gate identifier.
- Applicable hypothesis or mechanism.
- Required supporting conditions.
- Evidence sources.
- Shared ancestry.
- Independence requirement.
- Gate result.
- Reasoning explanation.

Distinguish:

- True independent-source requirements.
- General evidence accumulation.
- Legitimate compound mechanisms.

Do not treat all multi-signal gates as source-independence tests.

If independence was not assessed, do not imply that it was verified.

---

## 15. Confidence-policy explanation

Expose the centralized confidence policy introduced in Phase 3.

For the selected hypothesis, show:

- Final confidence tier.
- Applied policy rule.
- Relevant supporting evidence.
- Contradicting evidence.
- Moderating evidence.
- Reliability constraints.
- Coverage constraints.
- Applicable confidence caps.
- Explanation of the final tier.

### Required invariant

**The GUI consumes the final confidence-policy result. It does not calculate confidence.**

Do not reapply thresholds.

Do not upgrade confidence based on how many evidence items are visible.

Do not downgrade confidence because a visualization is unavailable after analysis.

### Terminology

Use:

- High confidence.
- Medium confidence.
- Low confidence.
- Inconclusive.
- Unavailable.

These describe qualitative support for a forensic interpretation, not statistically calibrated probabilities.

---

# Part I — Cross-workspace navigation

## 16. Integrate UI-3 and UI-4

UI-5 must connect the existing investigation workflow.

### From Overview

Users can open:

- Full evidence supporting the primary finding.
- Hypothesis-specific details.
- Limitations and coverage.
- Confidence explanation.

### From Image Forensics

Users can open:

- Evidence associated with the selected artifact.
- Its detector observation.
- Relevant hypothesis assessment.
- Related reasoning record.

### From Evidence Explorer

Users can open:

- Related detector artifacts.
- Parent or descendant evidence.
- Numerical contributions.
- Confidence reasoning.

### From Reasoning Explorer

Users can open:

- Supporting evidence.
- Contradicting evidence.
- Related visualization artifacts.
- Provenance information where applicable.

### Navigation requirements

- Use stable IDs.
- Preserve session identity.
- Preserve the current analysis revision.
- Preserve relevant selection context.
- Reject stale navigation requests.
- Do not rerun analysis.
- Do not mutate forensic results.

If a requested artifact or evidence record is unavailable, show an explicit unavailable state.

Do not silently navigate to unrelated content.

---

# Part J — Presentation architecture

## 17. Extend UI-1 presentation contracts

Create compatible typed presentation structures for the new explorers.

Suggested conceptual contracts:

```python
@dataclass(frozen=True)
class EvidenceDetailView:
    evidence_id: str
    hypothesis_id: str
    role: str
    detector_id: str | None
    reliability: str | None
    parent_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
```

```python
@dataclass(frozen=True)
class ScoreContributionView:
    evidence_id: str
    raw_contribution: float | None
    deduplicated_contribution: float | None
    reliability_adjusted_contribution: float | None
    final_contribution: float | None
```

```python
@dataclass(frozen=True)
class ConfidenceExplanationView:
    hypothesis_id: str
    tier: str
    policy_rule: str | None
    rationale: tuple[str, ...]
```

Adapt these to the existing schemas.

Do not duplicate fields unnecessarily.

### Contract requirements

- Immutable or controlled read-only structures.
- Stable identifiers.
- Explicit unavailable values.
- Session and result-revision binding.
- Deterministic construction.
- No reliance on GUI widget state for forensic truth.
- Compatibility with existing persisted results.

Avoid exposing raw mutable backend objects directly to the GUI.

---

## 18. Handle legacy and partial results

Some stored investigations may lack:

- Complete lineage records.
- Numerical deduplication audit fields.
- Full confidence-policy traces.
- Structured corroboration records.
- Complete hypothesis assessments.

The explorers must support partial availability.

### Required behavior

- Display available information.
- Clearly mark missing structured records.
- Preserve access to legacy narrative and raw trace.
- Never fabricate missing fields.
- Avoid crashes from incomplete dictionaries.
- Distinguish unsupported schema from corrupted records.

Do not rewrite historical investigations merely to populate new UI fields.

---

# Part K — Session integrity and performance

## 19. Preserve UI-1 safeguards

All explorer content must belong to the active session and result revision.

Test:

- Image reselection.
- Reanalysis.
- Stored-summary loading.
- Late worker completion.
- Late artifact loading.
- Evidence selection during session switch.
- Annotation revision changes.
- Missing source artifacts.
- Failed analysis.

Do not allow obsolete evidence details or confidence explanations to remain visible as current results.

### Performance

Reasoning traces may contain many nested records.

Avoid constructing an enormous visible widget tree for every trace field.

Prefer:

- Lazy detail expansion.
- Qt model/view structures.
- Bounded lists.
- Incremental rendering.
- Efficient filtering.

Do not load large forensic image arrays into the Evidence Explorer.

Reuse UI-4 artifact viewing when images are needed.

---

# Part L — Testing

## 20. Preserve the complete regression suite

Latest reported baseline:

**468 tests passed, zero failed, zero skipped.**

Run this baseline before implementation.

Add targeted UI-5 tests.

### Evidence Explorer

- Three hypothesis families.
- Supporting/contradicting/moderating roles.
- Detector filtering.
- Reliability filtering.
- Missing evidence.
- Duplicate evidence references.
- Stable evidence IDs.
- Evidence detail selection.

### Lineage

- Parent-child relationships.
- Multiple parents.
- Shared ancestry.
- Intermediate nodes.
- Missing lineage records.
- Cyclic or malformed data handled safely.
- Unknown statistical independence.
- No invented evidence relationships.

### Reasoning

- Primary and secondary hypotheses.
- Candidate route outcomes.
- Inconclusive routes.
- Superseded findings.
- Missing route details.
- Confidence-policy rule display.
- Reliability caps.
- Coverage limitations.

### Scorecard

- Raw contributions.
- Reliability adjustments.
- Numerical deduplication.
- Domain bonuses.
- Penalties.
- Reconciliation.
- Invalid or unavailable values.
- Historical incomplete ledgers.
- Exact value copying.

### Navigation

- Overview → Evidence.
- Overview → Reasoning.
- Image Forensics → Evidence.
- Evidence → Image Forensics.
- Evidence → Reasoning.
- Reasoning → Evidence.
- Stale navigation rejection.

### Compatibility

- Existing analysis workflow.
- UI-3 Overview.
- UI-4 comparison workspace.
- Metadata and provenance.
- OSINT revisions.
- Report exports.
- Stored-summary loading.

Prefer deterministic Qt tests.

Do not introduce unnecessary dependencies.

---

# Part M — Reference-image validation

## 21. Validate real investigations

Use the current `normal` profile unless repository documentation establishes a different active baseline.

Latest measured values:

| Reference | Suspicious | Benign | Primary finding |
|---|---:|---:|---|
| Instagram | 21.32705 | 2.25 | High localized editing |
| Midjourney | 6.675 | 1.5 | Medium unverified synthetic context |

For each reference:

1. Confirm source hash and analysis profile.
2. Load or run the complete analysis.
3. Build Evidence Explorer presentation structures.
4. Verify hypothesis-specific evidence roles.
5. Inspect lineage records.
6. Inspect scorecard contributions.
7. Inspect corroboration audit.
8. Inspect confidence-policy explanation.
9. Navigate to related UI-4 artifacts where supported.
10. Confirm scores, findings and confidence remain unchanged.

If scores differ, report the cause where demonstrable.

Do not modify scoring to force historical values.

Do not assume the two reference images represent a complete forensic validation dataset.

---

# Part N — Visual validation

## 22. Inspect the implemented explorers

Capture:

1. Empty Evidence workspace.
2. Instagram evidence grouped by hypothesis.
3. Midjourney evidence grouped by hypothesis.
4. Supporting evidence detail.
5. Contradicting evidence detail.
6. Moderating evidence detail.
7. Shared-lineage example.
8. Missing-lineage example.
9. Reasoning hypothesis summary.
10. Candidate decision trace.
11. Scorecard contribution ledger.
12. Numerical deduplication example.
13. Corroboration audit.
14. Confidence explanation.
15. Stored legacy result.
16. Minimum-size window.
17. Maximized window.

Save under:

`doc/gui_modernization/ui5/screenshots/`

Use native Windows screenshots where possible.

Document any unverified DPI scales.

### Visual acceptance

- Correct evidence semantics.
- Clear hierarchy.
- Readable tables.
- No clipping.
- Usable filters.
- Responsive selection.
- No unexplained numerical percentages.
- Clear missing-data states.
- Stable navigation.
- Consistent UI-2 design system.

Do not use decorative graphs that imply unsupported statistical relationships.

---

# Part O — Documentation

## 23. Required deliverables

Create:

`doc/gui_modernization/ui5/`

### A. `reasoning_data_inventory.md`

Map authoritative backend fields to UI-5 presentation requirements.

### B. `evidence_explorer_design.md`

Describe filters, evidence roles, details, interaction and navigation.

### C. `lineage_presentation.md`

Document parent/descendant handling, shared ancestry and limitations.

### D. `reasoning_explorer_design.md`

Document candidate findings, hypothesis assessments, corroboration and confidence explanations.

### E. `scorecard_audit_presentation.md`

Describe ledger fields, numerical precision, reconciliation and deduplication display.

### F. `presentation_contract_extensions.md`

Document new typed contracts and their source mappings.

### G. `cross_workspace_navigation.md`

Describe stable identifiers, routing, session checks and unavailable targets.

### H. `legacy_result_compatibility.md`

Explain partial historical records and fallback behavior.

### I. `implementation_report.md`

Summarize architecture, changed files, design decisions and limitations.

### J. `visual_validation.md`

Document screenshots, layout checks and remaining platform limitations.

### K. `regression_results.md`

Include baseline/final test counts and reference-image outcomes.

---

# Part P — Final acceptance criteria

## 24. UI-5 Definition of Done

UI-5 is complete when:

1. The Evidence destination provides a functional structured explorer.
2. Evidence can be filtered by hypothesis and role.
3. Supporting, contradicting and moderating semantics remain correct.
4. Evidence details expose available source, reliability and limitations.
5. Lineage relationships are inspectable.
6. Shared ancestry is not misrepresented as statistical dependence.
7. The Reasoning destination provides structured hypothesis assessments.
8. Candidate route decisions are inspectable.
9. Corroboration decisions are visible where available.
10. Confidence-policy explanations are accessible.
11. Numerical scorecard contributions are inspectable and reconstructable where supported.
12. Numerical deduplication remains visible and correctly attributed.
13. Cross-navigation to UI-4 artifacts works where authoritative links exist.
14. Missing structured data is represented explicitly.
15. Legacy results remain accessible.
16. Active session and revision integrity are preserved.
17. Existing forensic outcomes remain unchanged.
18. All existing and new tests pass.
19. Visual validation and documentation are completed.
20. No unrelated GUI phase is implemented.

---

## 25. Final Codex response

Return:

**A. Baseline**

Branch, HEAD, Git state and starting tests.

**B. Evidence Explorer**

Implemented filters, detail views and data sources.

**C. Lineage**

Supported dependency relationships and limitations.

**D. Reasoning Explorer**

Hypotheses, candidate findings, corroboration and confidence presentation.

**E. Scorecard audit**

Contribution display, numerical integrity and deduplication records.

**F. Cross-navigation**

Supported connections between Overview, Image Forensics, Evidence and Reasoning.

**G. Session integrity**

How stale selections and obsolete results are prevented.

**H. Reference cases**

Instagram and Midjourney outcomes.

**I. Tests**

Exact passed, failed and skipped counts.

**J. Visual validation**

Screenshots, native checks and remaining DPI limitations.

**K. Git status**

Modified/untracked files and confirmation that nothing was staged, committed or pushed.

**L. UI-6 readiness**

Any blockers to provenance, OSINT and report-workspace modernization.

---

## Strict constraints

- Do not modify detector algorithms.
- Do not change numerical scoring.
- Do not change hypothesis selection.
- Do not change confidence-policy rules.
- Do not alter evidence-lineage calculations.
- Do not change provenance semantics.
- Do not weaken UI-1 session safeguards.
- Do not replace UI-2's design system.
- Do not redesign UI-3's Overview.
- Do not redesign UI-4's image-comparison workspace.
- Do not implement new provenance verification.
- Do not redesign report contents.
- Do not introduce unnecessary dependencies.
- Do not stage, commit, push, merge, tag, reset or stash.
- Preserve all inherited modifications.

**Core principle: Every forensic conclusion should be traceable through its supporting observations, evidence relationships, numerical contributions, corroboration conditions and confidence rules—without hiding uncertainty or inventing information.**

Implement UI-5, validate it against the existing reasoning engine and reference investigations, and deliver the requested documentation. Do not begin UI-6.
