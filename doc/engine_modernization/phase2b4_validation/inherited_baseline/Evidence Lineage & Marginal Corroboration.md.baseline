# CODEX TASK — SignalLens Phase 2B.2: Evidence Lineage & Marginal Corroboration

## Mission

You are the principal Python engineer, forensic reasoning architect and statistical evidence specialist for SignalLens.

Your task is to implement **correction #6 of the original ten-point reasoning-engine roadmap: prevent double-counting of correlated forensic signals**.

Phase 2B.1 established that several SignalLens detectors share underlying measurements and that derived evidence can receive additional scoring weight despite originating from the same observations.

The objective is to make evidence dependencies explicit and introduce a deterministic, auditable mechanism for controlling redundant contributions.

**Do not assume that correlated evidence is worthless.** A derived detector may add legitimate information through localization, geometric interpretation or cross-measurement corroboration.

The correction must preserve that information while preventing the same observation from being counted repeatedly as independent proof.

This phase must not change the forensic detector algorithms or introduce an unvalidated scoring calibration.

---

## 1. Current baseline and audit findings

Previous development phases established:

- Phase 1: Hypothesis-aware routing and metadata reasoning.
- Phase 1.1: Hypothesis-scoped support, contradiction and moderation.
- Phase 1.2: Failure-tolerant segmentation and analysis scheduling.
- Phase 2A: Mathematically consistent scorecard calculations.
- Phase 2B.1: Complete evidence-dependency audit.

The latest reported baseline:

- Git branch: `fix/scorecard-integrity-phase2a`
- Committed baseline: `f64f226`
- Phase 2A changes were still uncommitted at the end of the audit.
- 184 automated tests passed.
- Both reference images completed without pipeline failures.

### Reference scores

| Reference | Current suspicious score | Overall finding |
|---|---:|---|
| Instagram | 20.47705 | High; localized editing |
| Midjourney | 6.0375 | Medium; unverified synthetic-generation declaration |

### Phase 2B.1 diagnostic ablation

| Calculation | Instagram | Midjourney |
|---|---:|---:|
| Production baseline | 20.47705 | 6.0375 |
| Excluding downstream-composite base weights | 13.46455 | 3.9125 |

These alternative scores are exploratory and **not calibrated**.

They must not be adopted directly as replacement scores or compared against unchanged confidence thresholds to justify new conclusions.

### Audit documents

Read these existing reports before implementing anything:

- `doc/phase2b_evidence_dependency/evidence_dependency_audit.md`
- `doc/phase2b_evidence_dependency/signal_inventory.csv`
- `doc/phase2b_evidence_dependency/evidence_dependency_graph.md`
- `doc/phase2b_evidence_dependency/contribution_lineage.csv`
- `doc/phase2b_evidence_dependency/reference_case_analysis.md`
- `doc/phase2b_evidence_dependency/phase2b2_implementation_proposal.md`
- `doc/phase2b_evidence_dependency/audit_dependency.py`

**Use the actual audit findings and proposal as the implementation basis.** If they conflict with this task's assumptions, document the discrepancy before proceeding. Do not invent new dependencies or scoring formulas to fill gaps.

---

## 2. Git and baseline protection

Before editing:

1. Inspect the branch, HEAD and working-tree status.
2. Confirm the Phase 2A implementation is present.
3. Run the existing test suite.
4. Review inherited uncommitted files.
5. Confirm the Phase 2B.1 audit artifacts exist.

If Phase 2A is still uncommitted, do not silently fold it into Phase 2B.2.

Provide a clear baseline report and preserve the inherited work. You may proceed with strictly isolated, reviewable changes only if they can be distinguished reliably from previous phases.

Do not stage, commit, push, merge, tag, stash, reset or discard changes.

Keep `test_images/` excluded from Git. Local test images may be analyzed read-only.

---

## 3. Implement an explicit evidence-lineage model

### Problem

The current reasoning engine represents multiple forensic indicators as distinct evidence domains, but those domains do not reliably describe their shared measurement ancestry.

Examples include:

- ELA → cross-signal convergence → boundary findings.
- Residual analysis → cross-signal convergence → boundary findings.
- Patch similarity → patch spatial localization.
- Subject texture → material regularization → subject-process asymmetry.
- Global frequency features → regional frequency interpretations.

These are examples to verify against the actual dependency audit, not assumptions that every relationship is always present.

### Required implementation

Introduce a lightweight evidence-lineage representation.

Prefer explicit dataclasses, enums or validated immutable structures.

At minimum, every score-contributing evidence record should be able to describe:

- Unique evidence identifier.
- Source detector.
- Evidence family.
- Original measurement ancestry.
- Direct upstream dependencies.
- Relevant forensic hypotheses.
- Evidence status and availability.
- Whether the evidence is primary, derived or composite.
- Whether it adds a new observation, localization or interpretation.
- Raw scoring contribution.
- Adjusted contribution, when applicable.

Design lineage records to reference existing evidence identifiers rather than duplicating raw detector payloads.

### Requirements

- Deterministic output.
- Stable identifiers.
- No circular dependency relationships.
- No dependence on dictionary insertion order.
- No serialization of raw pixel arrays or large masks.
- Backward compatibility with existing `EvidenceSnapshot` and `ScoreCard` consumers.
- Explicit handling of missing or unavailable upstream evidence.

The model must distinguish **measurement ancestry** from **statistical independence**.

Do not claim statistical independence merely because two detectors have different source modules.

---

## 4. Define evidence families from the audit

Use the Phase 2B.1 signal inventory and dependency graph to establish an explicit evidence-family registry.

Potential families include:

- Metadata and provenance declarations
- ELA/residual processing anomalies
- Boundary and localized processing
- Frequency-domain periodicity
- Patch recurrence and spatial localization
- Subject texture and material characteristics
- Sensor and camera-pipeline characteristics
- Compression history

These are illustrative groupings. Use the source-code audit to determine the final registry.

### Important distinction

An evidence family is not necessarily the same as a scorecard `domain`.

Different domains may share one measurement ancestry, while a single domain may contain several distinct measurements.

Document the rationale for every family assignment.

### Acceptance criteria

- Every active score-contributing indicator has a defined lineage.
- Composite indicators identify their direct dependencies.
- The registry has no unexplained orphan scoring signals.
- Unknown future signals are handled conservatively and explicitly.
- No arbitrary suppression occurs merely because two signals share a broad category name.

---

## 5. Introduce marginal corroboration

### Objective

Prevent downstream evidence from receiving an additional full independent contribution when it simply restates an already-counted observation.

However, preserve legitimate incremental information.

Examples of incremental information may include:

- Localization of an otherwise global anomaly.
- Agreement between genuinely distinct measurement families.
- New spatial relationships between detected structures.
- A mechanism-specific interpretation supported by additional measurements.

### Required approach

Create a pure, deterministic contribution-adjustment layer that operates on:

1. Existing raw contributions.
2. Explicit evidence ancestry.
3. Declared incremental evidence relationships.
4. Existing reliability information.

It should produce an auditable marginal contribution for each indicator.

### Core rules

**Rule A — Primary observations**

Primary evidence retains its existing contribution in the initial shadow implementation.

**Rule B — Pure descendants**

A downstream indicator derived entirely from previously counted evidence, with no separately established incremental observation, must not automatically receive another full independent evidence credit.

**Rule C — Incremental corroboration**

When a derived indicator adds demonstrably new information, represent that incremental support separately.

Do not infer a numerical marginal contribution merely from the existence of a new module or pattern.

**Rule D — Shared ancestry**

Where several indicators reuse the same underlying measurement, their shared ancestry must be visible in the adjustment trace.

**Rule E — Missing evidence**

Missing or unavailable upstream evidence must not create positive marginal corroboration.

**Rule F — Contradictory evidence**

Do not suppress legitimate contradictory evidence merely because it shares an upstream measurement with supporting evidence.

Its interpretation must remain hypothesis-specific.

### Numerical policy

Do not invent new coefficients or family-budget limits.

If the audit establishes a deterministic structural rule that can prevent a mathematically duplicated contribution without requiring calibration, implement that rule in shadow mode.

If an adjustment requires choosing a new coefficient, cap or relative weight without empirical justification, expose it as an explicit experimental parameter and keep it out of production behavior.

The default must not silently introduce new scoring assumptions.

---

## 6. Implement shadow scoring

### Purpose

We need to observe the effect of lineage-aware contribution handling before changing production decisions.

Implement an optional shadow scorecard that runs alongside the current scorecard.

The production scorecard must remain authoritative.

### Requirements

The existing scorecard continues to determine:

- Current suspicious score.
- Current benign score.
- Hypothesis assessments.
- Route selection.
- Overall pattern.
- Confidence tier.
- GUI summary.

The shadow mechanism calculates:

- Existing contribution.
- Lineage-adjusted diagnostic contribution.
- Difference between them.
- Evidence-family impact.
- Shared ancestry.
- Reason for each adjustment.
- Any adjustment requiring unvalidated assumptions.

### Suggested output

```json
{
  "evidence_dependency_analysis": {
    "mode": "shadow",
    "lineage_version": "2b2",
    "production_score_unchanged": true,
    "families": {},
    "contributions": [],
    "shadow_aggregates": {},
    "comparison": {},
    "limitations": []
  }
}
```

Adapt this to the actual application structure.

Do not overwrite Phase 2A's `scorecard_calculation` audit.

The Phase 2A calculation trace and the Phase 2B.2 dependency trace serve different purposes:

- Phase 2A explains mathematical aggregation.
- Phase 2B.2 explains shared evidence ancestry and hypothetical redundancy adjustments.

### Performance

Avoid rerunning expensive forensic detectors merely to calculate shadow contributions.

Reuse existing summaries and scorecard data.

Record the additional processing overhead, if measurable.

---

## 7. Investigate corroboration gates

The Phase 2B.1 audit identified a specific risk: corroboration gates may treat related descendant indicators as if they represent independent evidence.

Inspect code that checks:

- Number of suspicious domains.
- Number of strong signals.
- Cross-signal convergence.
- Synthetic support from other domains.
- Multiple corroborating mechanisms.
- Confidence rationale based on converging indicators.

### Required implementation

Create a lineage-aware diagnostic assessment of corroboration.

It should identify:

- Total supporting indicators.
- Distinct measurement ancestries.
- Shared or overlapping ancestry groups.
- Composite indicators derived from primary evidence.
- Whether a corroboration claim relies only on descendants of one observation family.

Do not change production gates in this task.

Record which existing gates would potentially behave differently under ancestry-aware interpretation.

### Acceptance criteria

A case with five derived indicators originating from one measurement family must not be described by the shadow analysis as having five independently corroborating observations.

At the same time, the shadow analysis must recognize genuinely additional measurements when the lineage graph supports them.

---

## 8. Audit confidence-rationale wording

Inspect current narrative and confidence-rationale functions for statements implying independence.

Examples:

- Independent forensic signals.
- Multiple independent domains.
- Independent corroboration.
- Converging evidence from distinct mechanisms.

Classify each statement as:

- Supported by distinguishable measurement ancestry.
- Corroborative but sharing ancestry.
- Unsupported by current evidence.
- Requiring empirical validation.

Generate recommended replacement wording that describes the evidence accurately.

For example:

Instead of:

"Multiple independent forensic signals confirm suspicious processing."

Prefer, where appropriate:

"Several forensic indicators show consistent anomalies, although some are derived from shared underlying measurements."

Do not modify production confidence rules or narratives unless fixing a strictly misleading independence claim can be done without changing classification behavior. Document any such wording-only change separately.

---

## 9. Regression tests

Preserve all existing 184 tests.

Add unit and integration tests covering:

| Scenario | Expected behavior |
|---|---|
| One primary observation | Full existing contribution retained |
| One primary and one pure descendant | Shared ancestry recognized |
| Two genuinely distinct primary measurements | Separate ancestry recognized |
| Two composites sharing the same parent | Redundant ancestry identified |
| Composite adding localization | Incremental information represented |
| Composite with missing upstream evidence | No fabricated marginal support |
| Contradictory evidence sharing ancestry | Contradiction remains visible |
| Multiple descendants of one measurement | Not reported as independent corroboration |
| Unknown evidence identifier | Conservative, explicit handling |
| Cyclic lineage registration | Rejected |
| Non-deterministic input ordering | Stable output |
| Repeated evaluation | Identical result |
| Serialization round trip | Lineage preserved |
| Missing detector result | Safe handling |
| Phase 2A score reconciliation | Unchanged |
| Production vs shadow scoring | Production output identical |
| Existing Midjourney case | No production classification regression |
| Existing Instagram case | No production classification regression |

Add integration tests that construct the full dependency lineage through the existing `EvidenceSnapshot` and scorecard interfaces.

Do not introduce new third-party dependencies solely for the tests.

---

## 10. Validate both reference images

Run the full headless pipeline against the two existing reference images if accessible.

Use `subject_based` analysis mode for both, consistent with Phase 2A validation.

### Instagram reference

Expected production baseline:

- Suspicious score: 20.47705.
- High-confidence localized-editing conclusion.
- No failed stages.

### Midjourney reference

Expected production baseline:

- Suspicious score: 6.0375.
- Medium-confidence unverified generation declaration.
- Person mask remains subject to the existing quality gate.
- No fabricated regional evidence.
- No failed stages.

### Required comparison

For each image, report:

| Metric | Production | Shadow |
|---|---|---|
| Suspicious aggregate | Existing value | Diagnostic value |
| Benign aggregate | Existing value | Diagnostic value |
| Number of scoring indicators | Existing count | Same observed indicators |
| Distinct measurement ancestries | Not previously tracked | Calculated |
| Suspected redundant contributions | Audit-derived | Identified |
| Hypothesis assessments | Existing | No shadow decision |
| Confidence tier | Existing | Not recalculated |

Do not assign a shadow confidence tier.

The current confidence thresholds are calibrated, if at all, for the current scoring model. They must not be applied mechanically to new diagnostic scores.

If observed production scores differ from the expected baseline, investigate whether the cause is a code regression, analysis-mode difference, configuration difference or an earlier unrecorded change.

Do not adjust weights to force numerical agreement.

---

## 11. Document proposed activation conditions

This task must not automatically activate dependency-adjusted scoring.

Instead, define the conditions that would justify activation.

At minimum, evaluate:

- Whether the lineage graph covers all active scoring indicators.
- Whether adjustments are mathematically reproducible.
- Whether primary evidence remains available.
- Whether the correction reduces duplicated contributions.
- Whether the correction preserves legitimate incremental corroboration.
- Whether the approach introduces arbitrary coefficients.
- Whether confidence and decision thresholds would need revision.
- Whether sufficient labeled examples exist to evaluate false-positive and false-negative consequences.

Separate:

**Structural correctness fixes**

Changes justified by direct evidence of duplicate accounting.

**Empirical weighting changes**

Changes requiring labeled data, calibration or statistical validation.

Do not present the latter as already validated.

---

## 12. Scope restrictions

Do not modify:

- Forensic detector algorithms.
- Existing detector thresholds.
- Production score coefficients.
- Production score aggregation.
- Decision-route ordering.
- Confidence calculations.
- Hypothesis selection.
- Provenance-verification logic.
- MediaPipe masking rules.
- GUI layout.
- Dependencies.
- PyInstaller packaging.
- GitHub workflows.

Do not perform unrelated refactoring.

Do not stage, commit, push, merge, tag or publish changes.

Protect all existing Phase 1–2A corrections.

---

## 13. Required deliverables

Create documentation under:

`doc/phase2b_evidence_dependency/`

### A. Implementation report

`phase2b2_shadow_implementation.md`

Describe:

- New lineage architecture.
- Evidence-family registry.
- Marginal corroboration rules.
- Shadow score calculation.
- Production compatibility.
- Known limitations.

### B. Lineage specification

`evidence_lineage_schema.md`

Define fields, identifiers, dependency rules and JSON representation.

### C. Reference-image comparison

`phase2b2_reference_comparison.md`

Include production and shadow contribution breakdowns for Instagram and Midjourney.

### D. Activation assessment

`phase2b2_activation_criteria.md`

Identify which changes are justified by code-level correctness and which require empirical validation.

### E. Tests

Add automated tests to the existing test suite.

Keep production modules focused and reusable.

Avoid implementing the entire evidence-lineage model inside a single large function.

---

## 14. Final report format

Provide:

**A. Baseline**

Branch, HEAD, Git status and existing tests.

**B. Implementation**

Changed files and added modules.

**C. Confirmed dependency corrections**

Which redundant evidence paths are now explicitly represented.

**D. Production invariance**

Demonstrate that existing scores, hypotheses and confidence tiers remain unchanged.

**E. Shadow analysis**

Show the numerical effect on both reference images, including family-level contributions and limitations.

**F. Corroboration analysis**

Identify any production corroboration gates that could overstate independent evidence.

**G. Test report**

Exact passed, failed and skipped counts.

**H. Activation recommendation**

State whether lineage-aware scoring can safely replace production scoring, or what validation remains necessary.

**I. Git status**

Confirm that nothing was staged, committed or pushed.

---

## Definition of Done

Phase 2B.2 is complete when:

1. Every active score-contributing signal has explicit measurement ancestry.
2. Direct, derived and composite evidence are distinguished.
3. Shared ancestry is visible and machine-readable.
4. Marginal corroboration is calculated deterministically in shadow mode.
5. Production scores and decisions remain unchanged.
6. Composite indicators are not automatically described as independent observations.
7. Unavailable upstream evidence does not create artificial corroboration.
8. Both reference images have production-versus-shadow comparisons.
9. All existing and newly added tests pass.
10. Activation requirements and limitations are explicitly documented.

**Core principle: Repeated indicators derived from the same observation must not be mistaken for independent corroboration. Genuine incremental forensic information must remain identifiable and explainable.**

Implement the lineage and shadow-scoring mechanisms, execute the tests and produce the requested reports. Do not activate dependency-adjusted scoring or commit changes.
