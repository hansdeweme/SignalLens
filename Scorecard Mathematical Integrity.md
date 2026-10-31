# CODEX TASK — SignalLens Phase 2A: Scorecard Mathematical Integrity

## Mission

You are the principal Python engineer and forensic reasoning architect for SignalLens.

Phases 1, 1.1 and 1.2 corrected hypothesis-aware reasoning, evidence attribution, metadata extraction and failure-tolerant image segmentation.

The latest validation reports:

- **121 automated tests passed**, zero failed.
- Both reference images completed the full headless pipeline without stage failures.
- Instagram retained its High-confidence localized-editing conclusion.
- Midjourney retained its Medium-confidence unverified synthetic-generation declaration.
- Unreliable segmentation is now handled without fabricating evidence.

Your next task is **Phase 2A: audit and correct the mathematical integrity of the forensic scorecard**.

This is a narrowly scoped correctness task. Do not introduce new detection methods, recalibrate confidence, or redesign evidence weighting.

**Primary objective:** Every reported score must reconcile mathematically with its components, reliability adjustments must be applied exactly once and in the correct order, and unavailable evidence must never be mistaken for negative or positive evidence.

---

## 1. Repository and baseline protection

Before making modifications:

1. Inspect `git status`, branch and accumulated changes from Phases 1–1.2.
2. Review the current test suite and confirm its baseline.
3. Preserve all previous reasoning-engine and masking corrections.
4. Identify the current scorecard API and every consumer of its values.

The previous work was performed on:

`fix/reasoning-correctness-phase1`

### Important Git instructions

If Phases 1–1.2 remain uncommitted, **do not begin Phase 2A on top of an unreviewed working tree**.

Instead:

- Report the outstanding changes.
- Review their diff for unexpected files, generated artifacts and accidental modifications.
- Run the existing tests.
- Provide a concise readiness report.
- Stop before implementing Phase 2A.

Do not autonomously commit, stash, discard or move inherited work.

If the working tree is clean and the Phase 1 baseline is committed, create:

`fix/scorecard-integrity-phase2a`

Do not stage, commit, push, merge, tag or publish any changes.

Never modify or commit anything under `test_images/`.

---

## 2. Inspect the complete scorecard calculation

Start with `hypothesis_engine.py`, particularly:

- `compute_base_scores()`
- `compute_scorecard()`
- `derive_signals()`
- `ScoreCard` and related dataclasses

Also inspect:

- `decision_logic.py`
- `reasoning_persistence.py`
- Hypothesis assessment construction
- Existing scorecard serialization
- Narrative and confidence-rationale consumers
- Any other functions that recalculate, transform or interpret scorecard values

Document the calculation pipeline before editing.

For each scorecard field, determine:

- Its mathematical definition
- Its contributing inputs
- Its expected range, if any
- Whether it is an intermediate or final quantity
- Whether it includes reliability adjustments
- Whether it is consumed by decision routing
- Whether it is exposed in the reasoning trace

Pay particular attention to:

- `suspicious_score`
- `benign_score`
- `local_edit_support_score`
- `clone_support_score`
- `synthetic_boost`
- `edit_boost`
- `provenance_boost`
- `sensor_boost`
- `compression_boost`
- `caution_penalty`
- `camera_counter_support`
- `suspicious_domains`
- `benign_domains`

Do not assume these fields are directly additive without inspecting their actual definitions.

---

## 3. Correction A — Fix calculation ordering

### Known concern

The existing implementation has previously calculated the final suspicious score before applying certain reliability adjustments.

For example, logic resembling:

```python
card.suspicious_score = (
    base_suspicious
    + card.synthetic_boost
    + card.edit_boost
    + card.provenance_boost
    + card.sensor_boost
    + card.compression_boost
    - card.caution_penalty
)

if ds.boundary_reliability_score < 1.0:
    card.local_edit_support_score *= ds.boundary_reliability_score
    card.edit_boost *= ds.boundary_reliability_score
    card.caution_penalty += (
        1.0 - ds.boundary_reliability_score
    )
```

This is illustrative. Inspect the current implementation rather than assuming this exact sequence remains unchanged.

If final scores are calculated before all applicable adjustments, the scorecard becomes mathematically inconsistent.

### Required behavior

Implement a clear calculation sequence:

1. Calculate base evidence contributions.
2. Calculate raw mechanism-specific contributions.
3. Apply applicable reliability adjustments.
4. Apply penalties and caps in their intended order.
5. Calculate final aggregate scores.
6. Serialize the resulting components and aggregates.

**Final aggregates must be calculated from final adjusted components, not stale intermediate values.**

Preserve the existing formulas and intended weighting policy wherever possible.

Do not change numerical coefficients merely because the resulting classification appears undesirable.

### Acceptance criteria

- Final scores reconcile with their defined components.
- Reliability adjustments are applied exactly once.
- Repeated evaluation does not compound penalties.
- Intermediate fields are not mistakenly presented as final values.
- Existing scorecard consumers receive consistent data.

---

## 4. Correction B — Eliminate accidental double application of adjustments

Inspect the entire scorecard computation for:

- Reliability multipliers applied more than once
- Penalties added at multiple stages
- Contributions included both in a base score and a boost unintentionally
- Caps applied inconsistently
- Fields mutated after aggregate calculation
- Reused `ScoreCard` objects carrying state between evaluations
- Order-dependent mutations

Differentiate intentional evidence aggregation from accidental arithmetic duplication.

Do not attempt to solve correlated forensic evidence in this phase.

For example, ELA and boundary evidence may be intentionally represented as separate signals under the existing scoring model. Changing their statistical dependence belongs to Phase 2B.

This task should correct only demonstrable implementation errors or formula inconsistencies.

### Acceptance criteria

- Identical input evidence always produces identical scorecard output.
- Repeated calls do not accumulate state.
- Every adjustment has a single documented application point.
- All intentional nonlinear transformations and caps are preserved and documented.

---

## 5. Correction C — Handle unavailable evidence consistently

Phase 1.2 introduced controlled unavailability for segmentation-dependent stages.

A Low-quality person mask can now cause regional forensic evidence to remain unavailable while global analyses continue.

The scorecard must correctly handle:

- `not_run`
- `unavailable`
- `skipped`
- `inconclusive`
- `weak`
- Missing or null evidence objects
- Non-finite numeric values, if encountered

### Required behavior

Distinguish three concepts:

**Unavailable evidence**

The detector did not provide a usable observation.

This must not automatically count as suspicious or benign.

**Inconclusive evidence**

The detector ran but could not support a sufficiently specific conclusion.

Apply the existing neutral/inconclusive policy.

**Weak evidence**

The detector produced an observation classified as weak.

Preserve existing scoring rules where justified, but verify that the polarity and status are interpreted consistently.

Do not automatically convert unavailable evidence to weak evidence.

Do not manufacture zero-valued evidence objects if that changes how the scoring engine interprets the result.

### Acceptance criteria

- Missing regional evidence does not create positive synthetic-origin support.
- Missing regional evidence does not create positive photographic-authenticity support.
- Missing evidence is not counted as a suspicious or benign domain.
- No score calculations crash on absent optional evidence.
- Legitimate zero-valued measurements are distinguishable from missing measurements.
- Non-finite values are handled safely and explicitly.

---

## 6. Correction D — Make arithmetic auditable

Introduce a concise calculation breakdown in the reasoning trace.

Use the existing persistence mechanism and maintain backward compatibility.

The breakdown should make it possible to reconstruct the final score.

Suggested structure:

```json
{
  "scorecard_calculation": {
    "base_suspicious": 0.0,
    "base_benign": 0.0,
    "raw_contributions": {},
    "reliability_adjustments": {},
    "final_contributions": {},
    "penalties": {},
    "aggregate_scores": {},
    "calculation_version": "2a"
  }
}
```

Adapt the structure to the actual formula.

Do not introduce redundant fields without a clear reconciliation purpose.

### Requirements

- Every aggregate must be reconstructable from the recorded component values and documented operations.
- Include applied multipliers and penalties.
- Record caps or nonlinear transformations when relevant.
- Distinguish raw contributions from adjusted contributions.
- Use machine-readable finite numeric values.
- Preserve existing scorecard fields and JSON consumers.
- Avoid recording large raw image arrays or unnecessary intermediate detector data.

If a score is derived through nonlinear logic, document the operation rather than presenting it as a simple sum.

### Acceptance criteria

A test must be able to reconstruct the final score from the serialized breakdown within a defined floating-point tolerance.

---

## 7. Correction E — Scorecard consistency checks

Introduce internal validation of scorecard integrity.

Prefer a pure helper or validation method.

It should verify:

- Required aggregate values are finite.
- Defined component relationships reconcile.
- Reliability multipliers are within valid ranges.
- Score domains and status categories satisfy the documented contract.
- No unexpected negative values occur in fields defined as nonnegative.
- Missing evidence does not create artificial contributions.

Do not assume every score is bounded between zero and one. Several aggregate scores intentionally exceed one.

### Failure policy

During development and automated testing, mathematical inconsistencies should fail clearly.

In production, avoid allowing a validation exception to crash the entire forensic analysis pipeline.

Choose a conservative handling policy consistent with the existing pipeline architecture.

Do not silently repair invalid scores by arbitrary clipping.

An invalid scorecard must not produce a confident forensic conclusion.

---

## 8. Automated regression testing

Preserve all 121 existing tests.

Add targeted mathematical tests using synthetic evidence fixtures.

### Required scenarios

| Test | Expected behavior |
|---|---|
| No evidence | Neutral aggregate behavior |
| One suspicious signal | Correct contribution |
| One benign signal | Correct contribution |
| Suspicious and benign evidence | Correct separate accounting |
| Full boundary reliability | No unintended penalty |
| Reduced boundary reliability | Adjustments applied before final aggregation |
| Zero boundary reliability | No unsupported boundary contribution |
| Missing region masks | No invented regional contribution |
| Missing metadata | Neutral provenance contribution |
| Inconclusive detector | Existing inconclusive policy respected |
| Repeated scorecard evaluation | Identical results |
| Repeated evaluation using shared inputs | No accumulating mutation |
| Different evidence insertion orders | Identical aggregate result within tolerance |
| Null optional scores | Safe deterministic handling |
| NaN and infinity | Explicit rejection or controlled invalid state |
| Score cap boundaries | Existing caps preserved |
| Multiple adjustments | No accidental double application |
| Serialization round trip | Numerical consistency preserved |
| Audit breakdown reconstruction | Exact reconciliation within tolerance |
| Existing Midjourney fixture | Reasoning remains valid |
| Existing Instagram fixture | Reasoning remains valid |

Include property-based tests if a suitable library is already installed. Do not add a dependency merely for this purpose.

Use `math.isclose()` with justified tolerances for floating-point comparisons.

Avoid brittle assertions that depend on incidental dictionary ordering.

---

## 9. Real-image validation

After automated testing, run both existing reference images through the full headless pipeline if available.

Use `subject_based` mode for both, matching the Phase 1.2 validation.

### Instagram

Expected:

- Reliable person segmentation
- All expected stages available
- High localized-editing conclusion remains possible
- Scorecard components reconcile
- No regression in regional analysis execution

### Midjourney

Expected:

- Existing 91.82% person-mask coverage remains subject to the unchanged 90% limit
- Unreliable mask remains rejected
- No fabricated regional measurements
- Cross-signal executes independently
- Synthetic-generation declaration remains available
- Scorecard components reconcile
- No missing-evidence contribution is invented

Do not enforce identical final scores if correcting the calculation order legitimately changes them.

Instead, explain every observed numerical difference using the newly auditable contribution breakdown.

Do not tune the implementation to preserve a particular confidence tier.

The expected behavior is mathematical correctness, not numerical backward compatibility with a defective calculation.

---

## 10. Compatibility and scope restrictions

Maintain:

- The existing five-element `synthesize_overall()` return API
- Existing scorecard field names where practical
- Existing reasoning-trace JSON fields
- Current hypothesis assessment structure
- Current GUI/controller integration
- Existing detector algorithms
- Existing detector thresholds
- Current provenance categories
- Current mask-reliability policy

Do not change:

- Detection algorithms
- Score weights or coefficients
- Decision-route ordering
- Confidence thresholds
- Hypothesis selection rules
- Correlated-evidence weighting
- Dependency versions
- GUI layout
- PyInstaller packaging
- GitHub workflows

If a genuine mathematical fix necessarily changes a final score or decision, document it and add a regression test.

If a proposed fix requires changing the underlying scoring policy rather than correcting its implementation, leave it as a recommendation for Phase 2B.

---

## 11. Required final report

### A. Baseline

Report:

- Branch and Git state
- Existing test count
- Current scorecard calculation sequence
- Confirmed mathematical inconsistencies

### B. Implementation

List changed files and explain each correction.

### C. Before/after calculations

For each identified defect, show:

- Previous calculation
- Corrected calculation
- Numerical example
- Why the correction is mathematically necessary

### D. Reference-image results

Provide:

| Metric | Instagram before | Instagram after | Midjourney before | Midjourney after |
|---|---|---|---|---|
| Suspicious score | | | | |
| Benign score | | | | |
| Edit boost | | | | |
| Caution penalty | | | | |
| Final pattern | | | | |
| Confidence tier | | | | |
| Completed stages | | | | |
| Failed stages | | | | |

Explain changes rather than hiding them.

### E. Test results

Report exact passed, failed and skipped counts, plus new test coverage.

### F. Auditability

Demonstrate that a serialized scorecard can be independently reconstructed from its calculation breakdown.

### G. Remaining issues

Document unresolved questions about:

- Correlated evidence
- Score calibration
- Confidence calibration
- Provenance verification
- Segmentation reliability

Do not implement Phase 2B changes.

### H. Git status

Report modified and untracked files.

Do not stage, commit or push.

---

## Definition of Done

Phase 2A is complete when:

1. All scorecard calculations follow a documented order.
2. Every final aggregate reconciles with its reported components.
3. Reliability adjustments are applied exactly once.
4. Missing evidence does not contribute fabricated suspicious or benign support.
5. Repeated evaluation is deterministic.
6. Invalid numerical states cannot silently produce confident conclusions.
7. The reasoning trace contains a reconstructable mathematical audit.
8. Existing tests pass.
9. Both reference images complete without pipeline regressions.
10. Every changed forensic conclusion can be explained by a specific arithmetic correction.

**Core principle: A forensic reasoning system must be able to account for every numerical contribution to its conclusions. Mathematical integrity comes before statistical calibration.**

Implement the corrections, validate them, and deliver the report. Do not commit or push.
