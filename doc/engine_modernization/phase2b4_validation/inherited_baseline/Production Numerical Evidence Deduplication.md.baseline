# CODEX TASK — SignalLens Phase 2B.4: Production Numerical Evidence Deduplication

## Mission

You are the principal Python engineer, forensic reasoning architect and statistical evidence specialist for SignalLens.

Your task is to resolve the **single remaining blocker in SignalLens's original ten-point reasoning-engine correction roadmap**:

**Correction #6 — Prevent double-counting of correlated forensic signals.**

The final independent acceptance audit returned:

**FAIL for roadmap closure — 9 corrections accepted, 1 partially accepted, 0 failed.**

The outstanding issue is that the production scorecard still permits overlapping numerical credit for evidence derived from shared underlying measurements.

Previous phases introduced evidence lineage, marginal-credit diagnostics and lineage-aware corroboration gates. These improvements prevent certain false independence claims, but numerical contributions in production still retain potentially redundant credit.

Your task is to correct demonstrable numerical double-counting while preserving legitimate incremental evidence.

**Primary objective:** Ensure that the same underlying forensic observation does not receive repeated numerical credit merely because it is interpreted by multiple downstream detectors.

This is a targeted correctness correction, not a general scoring redesign.

---

## 1. Current baseline

The latest acceptance audit reported:

- Git branch: `fix/scorecard-integrity-phase2a`
- Last reported committed baseline: `f64f226`
- Accumulated Phase 2A–3 changes remain uncommitted.
- **297 automated tests passed**, zero failed or skipped.
- Nine original corrections accepted.
- Correction #6 partially accepted.
- Both reference images completed without pipeline failures.

### Reference-image results

| Reference | Suspicious | Benign | Confidence |
|---|---:|---:|---|
| Instagram | 20.47705 | 2.25 | High — localized editing |
| Midjourney | 6.0375 | 1.5 | Medium — unverified generation declaration |

These are comparison baselines, not values that must be preserved if a genuine arithmetic correction changes them.

### Existing diagnostic experiment

| Calculation | Instagram | Midjourney |
|---|---:|---:|
| Current production | 20.47705 | 6.0375 |
| Remove downstream-composite base weights | 13.46455 | 3.9125 |

The alternative values are uncalibrated diagnostic ablations.

**Do not directly adopt them as production scores.**

The audit demonstrated sensitivity to overlapping evidence, not that every composite contribution should be removed.

---

## 2. Mandatory source review

Read the current implementation and the following documents before editing:

- `doc/final_reasoning_engine_acceptance_audit.md`
- `doc/phase2b_evidence_dependency/evidence_dependency_audit.md`
- `doc/phase2b_evidence_dependency/signal_inventory.csv`
- `doc/phase2b_evidence_dependency/contribution_lineage.csv`
- `doc/phase2b_evidence_dependency/evidence_dependency_graph.md`
- `doc/phase2b_evidence_dependency/phase2b2_shadow_implementation.md`
- `doc/phase2b_evidence_dependency/evidence_lineage_schema.md`
- `doc/phase2b_evidence_dependency/phase2b2_activation_criteria.md`
- `doc/phase2b_evidence_dependency/phase2b3_corroboration_gate_audit.md`
- `doc/phase2b_evidence_dependency/phase2b3_remaining_limitations.md`

Inspect relevant production modules, especially:

- `hypothesis_engine.py`
- Evidence-lineage registry and helpers
- Shadow marginal-credit implementation
- Production scorecard aggregation
- Corroboration-gate implementation
- `decision_logic.py`
- Centralized confidence-policy module
- `reasoning_persistence.py`

Use the current source code and acceptance audit as authoritative evidence.

Do not assume every reported dependency represents numerical double-counting.

---

## 3. Git baseline protection

Before modifying anything:

1. Inspect current branch and HEAD.
2. Inspect tracked and untracked changes.
3. Identify which changes belong to earlier phases.
4. Run the existing tests.
5. Verify the current acceptance-audit findings.
6. Confirm that the lineage registry and shadow diagnostics are available.

### Important

The repository contains accumulated uncommitted work.

**Do not silently build Phase 2B.4 on an ambiguous baseline.**

If earlier phases remain uncommitted:

- Preserve the current working tree.
- Identify the exact existing changes.
- Produce a concise baseline-readiness report.
- Do not create commits without authorization.
- Proceed only if your Phase 2B.4 changes can be isolated and reviewed independently.

If the changes cannot be safely isolated, stop implementation and report the blocker.

Do not stage, commit, push, merge, tag, reset, stash or discard any work.

Keep `test_images/` excluded from Git. Reference images may be analyzed read-only.

---

## 4. Classify numerical contribution relationships

Before writing code, review every confirmed shared-ancestry relationship identified in Phase 2B.1.

Classify each relevant contribution relationship into exactly one category.

### Category A — Exact duplicate numerical credit

The same observation or derived score is directly included more than once in an aggregate, without any additional measurement or meaningful transformation.

This is a mathematical correctness defect.

**Action:** Correct the duplicate contribution.

### Category B — Derived interpretation without additional information

A downstream signal restates, categorizes or summarizes previously counted observations without adding a separate measurable feature.

This can produce redundant numerical credit.

**Action:** Prevent it from receiving an additional independent contribution unless the existing scoring specification explicitly establishes a justified incremental interpretation.

### Category C — Genuine incremental measurement

A downstream detector adds information not contained in the original contribution.

Examples may include:

- New spatial localization.
- A separately measured transition property.
- Geometric consistency across regions.
- A new physical or processing characteristic.

**Action:** Preserve the incremental contribution, subject to the existing reliability policy.

Do not assume that every downstream detector adds such information.

### Category D — Related but not demonstrably redundant evidence

Two measurements share inputs or likely correlate but their incremental evidentiary value has not been established.

**Action:** Preserve existing scoring behavior provisionally, explicitly identify the unresolved relationship, and do not claim statistical independence.

Do not invent a suppression factor.

### Required output

Create a classification table:

| Contribution | Shared source | Relationship | Evidence of redundancy | Proposed action |
|---|---|---|---|---|

Every proposed numerical change must be supported by a documented Category A or B finding.

Do not use suspected statistical correlation alone to justify a production coefficient change.

---

## 5. Implement deterministic numerical deduplication

Reuse the existing evidence-lineage infrastructure.

Do not introduce a second competing lineage system.

Implement a deterministic production contribution-allocation mechanism that distinguishes:

- Raw detector contribution.
- Previously credited measurement ancestry.
- Additional measurable information.
- Eligible marginal contribution.
- Suppressed duplicate contribution.
- Final adjusted contribution.
- Adjustment reason.

### Core invariants

**Invariant 1 — A primary observation is credited once**

An identical observation cannot receive repeated independent numerical credit through multiple downstream representations.

**Invariant 2 — New information is preserved**

A derived detector may receive additional credit when it contributes a distinct measurable feature under the existing scoring rules.

**Invariant 3 — No arbitrary reweighting**

Do not create new numerical coefficients, caps or suppression percentages merely to make aggregate scores smaller.

**Invariant 4 — Hypothesis-specific interpretation**

Evidence supporting localized editing must not automatically become additional synthetic-origin credit.

**Invariant 5 — Missing evidence receives no credit**

Unavailable, rejected or missing measurements cannot generate marginal corroboration.

**Invariant 6 — Repeated evaluation is stable**

The same evidence must produce the same numerical result regardless of dictionary insertion order or repeated evaluation.

### Important design limitation

Do not assume that a shared ancestry record alone mathematically proves zero marginal information.

If the current data cannot establish whether the downstream indicator adds independent quantitative information, retain the contribution provisionally and flag it as unresolved.

Do not replace one unsupported scoring assumption with another.

---

## 6. Integrate with the production scorecard

Inspect how `compute_base_scores()` and `compute_scorecard()` currently aggregate evidence.

Apply justified deduplication at the earliest appropriate contribution-allocation stage.

Avoid correcting duplicate contributions only after the final aggregate is calculated.

The production calculation sequence should remain:

1. Collect usable evidence.
2. Determine raw contributions.
3. Resolve confirmed duplicate numerical credit.
4. Apply existing reliability adjustments.
5. Apply existing penalties and caps.
6. Calculate final aggregate scores.
7. Validate mathematical integrity.
8. Persist the calculation audit.
9. Pass the scorecard into hypothesis and confidence evaluation.

Adapt the sequence where existing formulas require a different order, but preserve mathematical reconciliation.

### Requirements

- Keep current detector outputs unchanged.
- Keep existing coefficients unchanged.
- Keep the centralized confidence policy authoritative.
- Keep lineage-aware corroboration gates operational.
- Keep shadow diagnostics available for comparison.
- Do not allow shadow scores to overwrite production scores.
- Keep the five-element synthesis API compatible.

If production scores change, they must change only because previously duplicated contribution credit was demonstrably corrected.

---

## 7. Update numerical auditability

Extend Phase 2A's reconstructable scorecard ledger.

Every affected contribution should expose:

- Evidence identifier.
- Existing raw contribution.
- Measurement ancestry.
- Deduplication classification.
- Eligible final contribution.
- Suppressed contribution, if any.
- Reliability multiplier.
- Final adjusted contribution.
- Explicit adjustment reason.

Suggested structure:

```json
{
  "numerical_deduplication": {
    "version": "2b4",
    "contributions": [
      {
        "evidence_id": "example",
        "raw_contribution": 1.0,
        "classification": "exact_duplicate",
        "credited_contribution": 0.0,
        "suppressed_contribution": 1.0,
        "reason": "same_measurement_already_credited"
      }
    ],
    "aggregate_reconciliation": {},
    "unresolved_relationships": []
  }
}
```

Adapt this to the existing schema.

Do not duplicate large detector payloads.

Ensure that the final production score remains reconstructable from the recorded ledger.

---

## 8. Validate interaction with confidence and routing

A corrected suspicious score may cross an existing routing threshold.

Do not automatically preserve historical conclusions.

For every changed reference result:

1. Identify the contribution correction.
2. Reconstruct the numerical effect.
3. Identify any decision gate that changed state.
4. Identify the resulting primary hypothesis.
5. Identify the centralized confidence-policy rule.
6. Determine whether the new conclusion is logically consistent.

Do not lower confidence merely because the score decreased.

Do not increase confidence to compensate for a reduced score.

Do not retune decision thresholds in this task.

If the existing confidence policy cannot interpret corrected contributions without further calibration, document the limitation rather than inventing new thresholds.

---

## 9. Regression tests

Preserve all 297 existing tests.

Add focused tests covering:

| Scenario | Required behavior |
|---|---|
| One primary observation | Existing contribution retained |
| Same observation recorded twice | Numerical credit applied once |
| Primary observation plus pure derived restatement | No duplicate independent contribution |
| Derived detector with distinct additional measurement | Incremental contribution retained |
| Two distinct measurement sources | Both contributions retained |
| Shared ancestry but uncertain redundancy | Contribution preserved and limitation recorded |
| Multiple descendants of one source | No artificial repeated credit |
| Related contradictory evidence | Hypothesis-specific treatment preserved |
| Missing upstream evidence | No marginal credit created |
| Rejected region mask | No fabricated region contribution |
| Generic composite evidence | No indiscriminate suppression |
| Mixed provenance and visual evidence | Distinct evidence families retained |
| Different evidence insertion order | Deterministic output |
| Repeated scorecard evaluation | Identical result |
| Invalid numerical contribution | Controlled invalid result |
| Phase 2A ledger reconstruction | Exact reconciliation |
| Phase 2B.2 shadow diagnostics | Still operational |
| Phase 2B.3 corroboration gates | Behavior preserved |
| Phase 3 confidence policy | Correctly receives adjusted score |
| JSON serialization | Backward compatible |
| Instagram reference | Explain any numerical change |
| Midjourney reference | Explain any numerical change |

Include tests that exercise production integration, not only isolated deduplication helpers.

Use synthetic evidence fixtures wherever possible.

Do not introduce new dependencies.

---

## 10. Reference-image validation

Run both original reference images through the complete headless pipeline using `subject_based` mode.

### Instagram

Reference baseline:

- Suspicious: 20.47705
- Benign: 2.25
- Confidence: High
- Primary hypothesis: localized editing

### Midjourney

Reference baseline:

- Suspicious: 6.0375
- Benign: 1.5
- Confidence: Medium
- Primary hypothesis: unverified synthetic-generation declaration

### Required before/after comparison

| Metric | Instagram before | Instagram after | Midjourney before | Midjourney after |
|---|---|---|---|---|
| Suspicious score | | | | |
| Benign score | | | | |
| Deduplicated contributions | | | | |
| Remaining unresolved overlaps | | | | |
| Primary hypothesis | | | | |
| Confidence tier | | | | |
| Completed stages | | | | |
| Failed stages | | | | |

Also report:

- Which contribution families were affected.
- Which exact contribution paths were corrected.
- Which indicators retained full credit.
- Whether route or confidence decisions changed.
- Whether any new safeguards were triggered.

Do not force production scores to match experimental ablation values.

---

## 11. Re-evaluate correction #6 acceptance

After implementation, independently reassess the original requirement:

**Prevent double-counting correlated signals.**

Determine whether:

1. Confirmed duplicate numerical contributions have been eliminated.
2. Confirmed derived restatements no longer receive unjustified repeated credit.
3. Genuinely incremental information remains represented.
4. Production corroboration gates remain lineage-aware.
5. Reasoning narratives avoid unsupported independence claims.
6. Mathematical scorecard integrity remains intact.
7. Unresolved statistical dependencies are clearly documented.

### Strict acceptance rule

Do not claim full completion merely because a deduplication module exists or because scores have decreased.

Correction #6 may be marked **ACCEPTED** only if the confirmed numerical double-counting defects identified in the previous acceptance audit have been resolved and the remaining limitations are genuinely empirical rather than known implementation defects.

If some original confirmed numerical duplication remains unresolved, report **PARTIALLY ACCEPTED**.

Do not broaden the task into general machine-learning calibration.

---

## 12. Scope restrictions

Do not modify:

- Forensic detector algorithms.
- Detection thresholds.
- Existing contribution coefficients.
- Provenance-verification semantics.
- Mask-reliability thresholds.
- General hypothesis-selection architecture.
- Centralized confidence-policy definitions.
- GUI layout.
- Dependencies.
- PyInstaller packaging.
- GitHub workflows.

Do not activate arbitrary experimental family caps.

Do not apply the diagnostic audit-A ablation directly.

Do not perform unrelated refactoring.

Do not stage, commit, push, merge, tag, stash, reset or discard work.

---

## 13. Required deliverables

Create the following documentation under:

`doc/phase2b_evidence_dependency/`

### A. Numerical contribution classification

`phase2b4_contribution_classification.md`

For every confirmed overlapping contribution path, record:

- Evidence ancestry.
- Classification A–D.
- Whether numerical credit was changed.
- Justification.
- Remaining uncertainty.

### B. Implementation report

`phase2b4_numerical_deduplication.md`

Describe the implementation, affected functions, compatibility, mathematical invariants and production behavior.

### C. Reference-image comparison

`phase2b4_reference_comparison.md`

Include before/after contribution breakdowns for Instagram and Midjourney.

### D. Acceptance reassessment

`phase2b4_correction6_acceptance.md`

Give an explicit ACCEPTED or PARTIALLY ACCEPTED disposition for correction #6, with source-code and test evidence.

### E. Regression tests

Add focused unit and integration tests.

---

## 14. Final Codex report

Provide:

**A. Baseline:** branch, HEAD, Git status and initial test count.

**B. Confirmed duplicates:** exact numerical contribution paths corrected.

**C. Preserved contributions:** derived findings whose incremental information justifies retaining credit.

**D. Remaining uncertainties:** relationships requiring empirical calibration.

**E. Before/after scores:** Instagram and Midjourney.

**F. Decision impact:** changes to hypotheses, routing or confidence, if any.

**G. Test results:** passed, failed and skipped counts.

**H. Mathematical integrity:** confirmation that the production score remains reconstructable.

**I. Correction #6 verdict:** ACCEPTED or PARTIALLY ACCEPTED, with explicit justification.

**J. Git status:** changed/untracked files and confirmation that nothing was staged or pushed.

---

## Definition of Done

Phase 2B.4 is complete when:

1. All confirmed numerical duplicate-credit paths are identified.
2. Demonstrable duplicate credit is removed from production aggregation.
3. Genuinely incremental evidence remains represented.
4. Ambiguous statistical relationships are not arbitrarily reweighted.
5. Scores remain mathematically reconstructable.
6. Evidence-lineage and corroboration safeguards remain operational.
7. Centralized confidence assignment remains authoritative.
8. Existing regression tests pass.
9. Both reference-image pipelines complete without failure.
10. Correction #6 receives a justified, independently verifiable acceptance disposition.

**Core principle: The same forensic observation must not receive repeated numerical credit merely because multiple modules interpret it. At the same time, legitimate additional measurements must not be discarded simply because they share an upstream source.**

Implement the minimal justified correction, validate it against the source code and reference cases, and report whether correction #6 can finally be accepted.

Do not commit or push.
