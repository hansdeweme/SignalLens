# CODEX TASK — SignalLens Phase 2B.3: Production Corroboration Integrity

## Mission

You are the principal Python engineer, forensic reasoning architect and statistical evidence specialist for SignalLens.

Your task is to complete **correction #6 of the original ten-point reasoning-engine roadmap: prevent double-counting correlated forensic signals**.

Phases 2B.1 and 2B.2 established that multiple forensic signals can share the same underlying measurements. The system now has an evidence-lineage registry, immutable lineage records, marginal-credit allocation and optional shadow diagnostics.

However, production corroboration logic may still treat multiple descendant signals as independent evidence.

Your mission is to correct this specific logical problem in production.

**Primary objective:** A collection of related forensic indicators must not satisfy an independent-corroboration requirement merely because they originate from different modules or carry different evidence-domain identifiers.

Preserve genuinely distinct evidence and legitimate additional interpretations.

This task must not activate experimental numerical reweighting.

---

## 1. Baseline and project context

Previous development phases:

- **Phase 1:** Hypothesis-aware routing, metadata propagation and provenance interpretation.
- **Phase 1.1:** Hypothesis-specific evidence attribution.
- **Phase 1.2:** Failure-tolerant masking and regional analysis.
- **Phase 2A:** Mathematical scorecard integrity.
- **Phase 2B.1:** Evidence-dependency audit.
- **Phase 2B.2:** Evidence lineage and shadow marginal-corroboration diagnostics.

The latest reported validation:

- 232 automated tests passed.
- Zero failed or skipped.
- Both reference images completed without pipeline failures.
- Production scores and decisions remained unchanged.

### Reference baselines

| Reference | Suspicious score | Final conclusion |
|---|---:|---|
| Instagram | 20.47705 | High — localized editing |
| Midjourney | 6.0375 | Medium — unverified synthetic-generation declaration |

The Phase 2B.2 shadow analysis also reports:

| Reference | Default shadow | Audit-A experiment |
|---|---:|---:|
| Instagram | 20.47705 | 13.46455 |
| Midjourney | 6.0375 | 3.9125 |

The experimental values are uncalibrated. **Do not use them for production decisions.**

### Read before implementation

Inspect:

- `doc/phase2b_evidence_dependency/evidence_dependency_audit.md`
- `doc/phase2b_evidence_dependency/evidence_dependency_graph.md`
- `doc/phase2b_evidence_dependency/contribution_lineage.csv`
- `doc/phase2b_evidence_dependency/phase2b2_shadow_implementation.md`
- `doc/phase2b_evidence_dependency/evidence_lineage_schema.md`
- `doc/phase2b_evidence_dependency/phase2b2_reference_comparison.md`
- `doc/phase2b_evidence_dependency/phase2b2_activation_criteria.md`

Use the actual current code and lineage registry as the source of truth.

Do not assume illustrative dependency relationships are accurate without verification.

---

## 2. Repository protection

Before editing:

1. Inspect the current Git branch, HEAD and working-tree status.
2. Identify inherited uncommitted changes.
3. Run the existing tests.
4. Confirm the Phase 2B.2 implementation and lineage registry are present.
5. Confirm current production behavior.

Preserve all inherited changes.

Do not commit, stage, push, merge, tag, stash, reset or discard anything.

If existing uncommitted work cannot be safely distinguished from Phase 2B.3 changes, report the obstacle before modifying those files.

Do not alter anything under `test_images/`.

Local reference images may be analyzed read-only.

---

## 3. Audit production corroboration gates

Inspect `hypothesis_engine.py`, `decision_logic.py` and related modules for logic that infers corroboration from:

- Counts of suspicious domains.
- Counts of strong forensic signals.
- Multiple positive indicators.
- Cross-signal convergence.
- Synthetic support from other domains.
- Boundary and regional-processing agreement.
- Multiple supporting mechanisms.
- Evidence diversity.
- Confidence-rationale generation.

Identify every place where the implementation may implicitly interpret different domain identifiers or different detector outputs as independent evidence.

For each gate, document:

| Property | Required information |
|---|---|
| Gate identifier | Function and condition |
| Hypothesis | Which hypothesis it supports |
| Inputs | Exact evidence identifiers |
| Current condition | Existing implementation |
| Shared ancestry | Relevant upstream measurements |
| Independence assumption | Explicit or implicit |
| Risk | Potential duplicate corroboration |
| Correction | Minimal justified change |
| Expected impact | Potential routing or confidence differences |

Distinguish three types of conditions:

**A. Independent corroboration requirements**

The gate explicitly requires multiple independent observations or evidence families.

These must use lineage-aware uniqueness.

**B. General evidence accumulation**

The gate combines multiple supporting indicators without claiming statistical independence.

Do not automatically replace these with lineage counts.

**C. Mechanism-specific compound evidence**

The gate requires several related measurements to establish a specific forensic pattern.

Do not destroy legitimate compound conditions merely because their inputs share ancestry.

Only type A is automatically eligible for production correction.

Types B and C require explicit justification before any change.

---

## 4. Implement lineage-aware corroboration checks

Reuse the Phase 2B.2 lineage infrastructure.

Introduce a small, deterministic helper that evaluates whether a set of indicators satisfies a specified corroboration requirement.

The helper should support:

- Hypothesis-specific evidence selection.
- Available and valid observations only.
- Source-measurement ancestry.
- Direct and derived indicators.
- Shared upstream measurements.
- Distinct measurement families.
- Explicit incremental evidence.
- Conservative handling of unknown lineage.

### Important logic requirement

A shared ancestor does not automatically make two indicators identical.

Likewise, two indicators having different ancestry labels does not establish statistical independence.

Use the explicit lineage model and documented gate semantics.

For example:

- A primary ELA anomaly and a boundary conclusion derived only from that same ELA anomaly must not count as two independent observations.
- A boundary conclusion combining ELA and residual information can potentially represent meaningful compound support, but must not automatically be counted as a third independent source.
- A spatial localization finding can add interpretive value without necessarily adding another independent measurement.
- Distinct metadata declarations and pixel-based observations may represent separate evidence sources, although metadata trustworthiness remains a separate question.

Do not create a simplistic universal rule such as `number_of_domains >= 2`.

### Required result structure

The corroboration helper should provide a machine-readable result containing:

- Gate identifier.
- Hypothesis.
- Considered evidence identifiers.
- Eligible evidence identifiers.
- Distinct ancestry groups.
- Shared ancestry.
- Incremental support findings.
- Whether the requirement is satisfied.
- Explanation of the result.
- Unknown or provisional lineage limitations.

The result must be deterministic and serializable.

---

## 5. Correct production gates where justified

For every gate classified as requiring independent corroboration:

1. Establish its current behavior.
2. Define the required distinct observations.
3. Replace domain-count-based independence assumptions with lineage-aware checks.
4. Preserve the gate's existing intended evidentiary purpose.
5. Record which evidence satisfied or failed the condition.

### Critical constraints

Do not introduce arbitrary new weights, coefficients or family budgets.

Do not activate shadow marginal-credit scoring.

Do not replace current suspicious or benign aggregate scores.

Do not modify detector outputs.

Do not make every multi-signal gate stricter simply because signals share some ancestry.

If a gate cannot be corrected without selecting an empirically unsupported independence threshold, leave it unchanged, flag it as unresolved and explain the validation requirement.

### Acceptance criteria

- Multiple descendants of one primary observation cannot independently satisfy a true multi-source corroboration requirement.
- Legitimately distinct measurements can satisfy the requirement.
- Compound forensic mechanisms retain their intended behavior.
- Unknown lineage cannot silently be treated as independent confirmation.
- Gate failures do not erase the original underlying observations.
- Any classification changes are attributable to a specific corrected gate.

---

## 6. Correct unsupported independence claims

Inspect the human-readable outputs produced by:

- `build_confidence_rationale()`
- Hypothesis assessment narratives.
- Overall forensic summaries.
- Supporting and contradicting signal descriptions.
- Reasoning-trace selection explanations.

Replace wording that overstates the independence of related evidence.

Distinguish:

- Independent measurement sources, where supported.
- Multiple mutually consistent indicators sharing ancestry.
- Derived corroboration.
- Mechanism-specific compound evidence.
- Unverified or provisional evidence diversity.

Do not use the word *independent* unless its meaning is defined and supported by the available lineage information.

Where statistical independence has not been demonstrated, prefer descriptions of distinct measurement ancestry or multiple consistent indicators rather than definitive claims of independence.

Do not rewrite unrelated forensic descriptions.

---

## 7. Preserve mathematical scorecard integrity

Phase 2A established reconstructable and internally consistent score calculations.

Those guarantees must remain intact.

### Requirements

- Production numerical contributions remain unchanged.
- Existing scoring coefficients remain unchanged.
- Existing reliability multipliers remain unchanged.
- The final score still reconciles with its Phase 2A calculation trace.
- Evidence-lineage analysis does not mutate detector summaries.
- Shadow scoring remains diagnostic.
- Repeated evaluation is deterministic.

Correcting a corroboration gate may change which decision candidate qualifies.

That is acceptable if the change is justified by the original gate's independence requirement.

However, it must not silently change the underlying numerical score.

---

## 8. Add corroboration audit to the reasoning trace

Extend the current reasoning trace with a concise record of production corroboration decisions.

Suggested structure:

```json
{
  "corroboration_audit": {
    "version": "2b3",
    "evaluated_gates": [
      {
        "gate_id": "example",
        "hypothesis": "localized_editing",
        "considered_evidence": [],
        "distinct_ancestry_groups": [],
        "shared_ancestry": [],
        "requirement_satisfied": false,
        "explanation": ""
      }
    ],
    "limitations": []
  }
}
```

Adapt names to the existing schema.

Preserve current fields and consumers.

Do not duplicate the complete evidence-lineage graph in every gate result.

Record only the lineage information necessary to explain each corroboration decision.

---

## 9. Regression testing

Preserve all existing 232 tests.

Add focused tests covering:

| Scenario | Expected behavior |
|---|---|
| One primary observation | Counts as one source |
| One primary plus two descendants | Does not become three independent sources |
| Two distinct primary measurement sources | Can satisfy a two-source requirement |
| Cross-signal composite using two parents | Composite does not automatically become a third source |
| Genuine compound boundary mechanism | Remains evaluable |
| Patch similarity plus patch spatial descendant | No invented independent corroboration |
| Subject texture and shared derived features | Shared ancestry recognized |
| Metadata plus pixel-based observation | Separate source categories retained |
| Missing upstream evidence | No fabricated corroboration |
| Unknown lineage | Conservative, explicit outcome |
| Conflicting evidence | Contradictions retained by hypothesis |
| Evidence supplied in different orders | Deterministic results |
| Repeated evaluation | No mutable state accumulation |
| Corrected production gate | Expected routing behavior |
| Unsupported independence language | Not emitted |
| Phase 2A score reconciliation | Unchanged |
| Phase 2B.2 shadow scoring | Unchanged |
| JSON serialization | Backward compatible |

Add integration-level tests for `synthesize_overall()` and affected hypothesis assessments.

Do not only test the new helper in isolation.

Avoid introducing new dependencies.

---

## 10. Reference-image validation

Run both existing reference images through the full headless pipeline, if accessible.

Use `subject_based` mode for both.

### Instagram

Expected baseline:

- Suspicious score: 20.47705.
- High localized-editing confidence.
- No failed stages.

### Midjourney

Expected baseline:

- Suspicious score: 6.0375.
- Medium synthetic-origin confidence.
- No failed stages.
- Unreliable person mask remains rejected under existing policy.

### Validation requirements

For each reference report:

- Production suspicious score.
- Production benign score.
- Final dominant pattern.
- Confidence tier.
- Hypothesis assessments.
- Corroboration gates evaluated.
- Which gates passed or failed.
- Evidence ancestry supporting those results.
- Any decision changes relative to baseline.

Do not modify a gate merely to preserve a historical confidence tier.

Do not regard a changed tier as automatically an improvement.

If classification changes occur, show the exact corrected gate responsible and verify that the new behavior is supported by the underlying evidence.

---

## 11. Scope restrictions

Do not modify:

- Detector algorithms.
- Detector thresholds.
- Production scoring coefficients.
- Numerical score aggregation.
- Shadow marginal-credit policy.
- Confidence-tier definitions.
- General hypothesis-selection architecture.
- MediaPipe masking rules.
- Metadata-extraction behavior.
- Dependencies.
- GUI layout.
- PyInstaller packaging.
- GitHub workflows.

Do not attempt correction #9 in this task.

Do not introduce empirical calibration or probability estimates.

Do not perform unrelated refactoring.

Do not stage, commit, push, tag, merge, reset or discard changes.

---

## 12. Required deliverables

Create the following documentation under:

`doc/phase2b_evidence_dependency/`

### A. Gate audit

`phase2b3_corroboration_gate_audit.md`

Include every relevant production gate, its ancestry assumptions and whether correction was required.

### B. Implementation report

`phase2b3_implementation.md`

Document changed files, production behavior, mathematical invariants and backward compatibility.

### C. Reference comparison

`phase2b3_reference_comparison.md`

Show before/after results and the gate-level reasoning for both images.

### D. Remaining limitations

`phase2b3_remaining_limitations.md`

Identify any unresolved potential double-counting that requires empirical weighting or calibration.

### E. Tests

Add focused automated tests to the existing suite.

Keep the production implementation modular, deterministic and inspectable.

---

## 13. Required final report

Provide:

**A. Baseline:** branch, HEAD, Git status and existing tests.

**B. Gate inventory:** number of gates inspected, number corrected and number intentionally left unchanged.

**C. Corrected behavior:** which false independence assumptions were eliminated.

**D. Production invariance:** confirm that detector outputs and numerical scores remain unchanged.

**E. Reference results:** Instagram and Midjourney scores, conclusions and gate decisions.

**F. Testing:** exact passed, failed and skipped counts.

**G. Remaining correction #6 limitations:** distinguish fixed independent-corroboration defects from unresolved statistical weighting concerns.

**H. Compatibility:** API and JSON compatibility findings.

**I. Git status:** modified/untracked files and confirmation that nothing was staged or pushed.

---

## Definition of Done

Phase 2B.3 is complete when:

1. All production corroboration gates have been inspected.
2. Gates requiring independent sources use lineage-aware checks where justified.
3. Descendant indicators cannot artificially satisfy independent-evidence requirements.
4. Legitimate compound forensic mechanisms remain operational.
5. Unsupported independence claims are corrected.
6. Production scores and coefficients are unchanged.
7. Reasoning traces explain corroboration decisions.
8. The existing 232 tests and new regression tests pass.
9. Both reference images complete without pipeline failures.
10. Remaining empirical weighting limitations are documented separately.

**Core principle: Distinct indicators do not necessarily represent independent evidence. SignalLens must distinguish corroboration from repeated interpretation of the same measurement.**

Implement the targeted production corrections, validate them and deliver the reports. Do not activate experimental numerical reweighting or commit changes.
