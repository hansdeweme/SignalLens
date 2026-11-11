# Codex Task E — Corroboration Gate Transparency & Consistency

**Repository:** `D:\Coding\SignalLens`  
**Target release:** `0.1.0-beta.1`  
**Task type:** Focused investigation and bounded implementation  
**Priority:** High  
**Scope:** Corroboration gate evaluation, eligibility semantics and reasoning-trace diagnostics  
**Git:** Do not stage, commit, push, tag or publish.

## 1. Mission

Resolve an apparent inconsistency in SignalLens's production reasoning trace: a compound corroboration gate reports failure while its explanation states that the required number of supporting indicators was satisfied.

Determine whether this reflects:

1. A correct gate outcome with incomplete diagnostic reporting.
2. Inconsistent eligibility or strength evaluation.
3. A remaining logical defect introduced or exposed by Task D.

Implement the smallest justified correction.

**The objective is to make corroboration decisions accurate, transparent and auditable—not to change the Midjourney verdict.**

## 2. Mandatory preparation

Read:

- `AGENTS.md`
- `doc/test_quality/TEST_DISCIPLINE.md`
- `doc/reasoning_audit/origin_processing/root_cause_report.md`
- `doc/reasoning_audit/origin_processing/boundary_reliability_audit.md`
- `doc/reasoning_audit/origin_processing/origin_processing_architecture.md`
- `doc/reasoning_audit/origin_processing/task_d_implementation.md`

Inspect relevant production code and existing tests for:

- Production corroboration evaluation.
- Indicator eligibility.
- Compound-support requirements.
- Strength and reliability conditions.
- Evidence lineage and ancestry.
- Confidence-policy consumption of corroboration results.
- Reasoning-trace serialization and presentation.

Inspect Git status before making changes. Preserve all inherited modifications.

## 3. Reference defect

The latest Midjourney reasoning trace reports:

```text
Production Corroboration Audit
Version: 2b3

boundary.compound_support:
  passed=False

  2 observed supporting indicator(s) satisfy
  the 2-indicator compound_interpretations condition

  Eligible Evidence:
    evidence:boundary
    evidence:subject_boundary
```

The same trace reports:

```text
confidence.strong_source_diversity:
  passed=False

  1 measurement-disjoint supporting indicator
  does not satisfy the existing
  2-source diversity requirement
```

The overall confidence policy now produces:

```text
Primary Hypothesis: synthetic_origin
Confidence: Medium

localized_editing:
  Low / localized.camera_moderated_uncertainty

separate_edit_status:
  not_established_from_regional_anomalies
```

This primary conclusion is not the defect being investigated.

The concern is that the corroboration audit does not explain why `boundary.compound_support` failed despite apparently satisfying its stated indicator-count requirement.

Task C previously found that inconclusive Boundary Focus could influence compound strength while being excluded from supporting evidence.

Task D reportedly corrected that defect by requiring eligible supporting evidence for strength evaluation.

Task E must establish whether the current failed outcome is correct and whether its explanation reflects the actual implementation.

## 4. Investigation A — Reconstruct the gate decision

Trace the exact production code responsible for `boundary.compound_support`.

Identify every condition contributing to the final boolean outcome, including:

- Indicator-count requirements.
- Evidence eligibility.
- Observation status and polarity.
- Strength requirements.
- Reliability requirements.
- Compound-specific safeguards.
- Supporting evidence ancestry.
- Any additional veto or moderating condition.

For each condition, document:

| Condition | Required value | Observed value | Pass/fail |
|---|---|---|---|
| Indicator count | | | |
| Supporting strength | | | |
| Evidence eligibility | | | |
| Other applicable safeguards | | | |

Use actual values from the reference case wherever accessible.

Do not invent missing thresholds or infer implementation details from the trace alone.

**Required answer:** Which exact condition makes `boundary.compound_support` fail?

If the observed result is correct, preserve it.

If the implementation is incorrect, identify the smallest defensible fix.

## 5. Investigation B — Audit diagnostic consistency

Inspect how the production corroboration audit constructs its text.

Determine whether the message currently describes only the indicator-count component instead of the complete gate evaluation.

The audit should distinguish:

- Eligibility.
- Supporting-indicator count.
- Compound strength.
- Measurement ancestry.
- Overall gate outcome.
- Reason for failure.

For example, a failed gate should explain the distinction in a structure similar to:

```text
boundary.compound_support

Overall: FAILED

Indicator count:
  PASS — 2 of 2 required indicators observed

Eligible supporting evidence:
  evidence:boundary
  evidence:subject_boundary

Strength condition:
  FAIL — [actual measured value and requirement]

Overall failure reason:
  [specific unmet condition]
```

This is an illustrative format, not a prescribed data contract.

Use existing reporting conventions where possible.

A reader must never have to reverse-engineer a failed condition from unrelated trace sections.

## 6. Investigation C — Eligibility and strength consistency

Verify that the Task D correction is implemented consistently.

Specifically:

1. Can an ineligible observation contribute to compound strength?
2. Can an inconclusive observation influence strength without supporting the gate?
3. Are eligibility and strength assessed over the same evidence set where required?
4. Are there legitimate reasons for a measurement to qualify for one gate component but not another?
5. Are such differences explicit and auditable?
6. Does the consumer confidence policy use the same outcome reported in the trace?
7. Can the trace report success when the confidence policy treats the condition as failed, or vice versa?

Do not impose identical eligibility rules across unrelated gates when different semantics are intentional.

The requirement is internal consistency within each gate, not universal uniformity.

## 7. Investigation D — Audit related compound gates

Inspect the existing implementations for:

```text
boundary.compound_support
confidence.strong_source_diversity
synthetic.additional_support_flag
synthetic.fft_patch_compound
synthetic.material_asymmetry_compound
```

Determine whether the same diagnostic limitation exists elsewhere.

Keep this a narrowly scoped consistency check.

Do not redesign the entire corroboration framework.

Do not change corroboration thresholds, scoring weights or confidence policies unless a concrete implementation error is proven and the correction is strictly necessary.

## 8. Implementation authorization

After establishing the root cause, implement the smallest correction required.

Permitted changes:

- Correcting a demonstrated gate-evaluation defect.
- Making individual gate-condition outcomes explicit.
- Improving audit explanations for failed or successful gates.
- Aligning serialized diagnostic information with actual production decisions.
- Updating directly affected existing tests.

Not authorized:

- Changing detector thresholds.
- Retuning numerical evidence weights.
- Changing the primary-hypothesis precedence policy.
- Reclassifying image-generation metadata.
- Modifying OSINT logic.
- Refactoring unrelated reasoning modules.
- Redesigning GUI workspaces.
- Changing reporting-directory layout.
- Modifying the investigation revision lifecycle.

Task F and Task G will handle signal semantics and storage layout separately.

## 9. Preserve the reference-case interpretation

The current Midjourney outcome is:

| Dimension | Current result |
|---|---|
| Primary hypothesis | Synthetic origin |
| Confidence | Medium |
| Localized editing | Low |
| Separate editing | Not established |
| Declared process | `unspecified_generation_process` |
| Metadata authenticity | Unverified |
| Suspicious score | 18.04075 |
| Benign score | 1.50 |

This result is a regression reference, not a target that overrides the evidence.

A diagnostic-only correction should leave the result unchanged.

If a genuine calculation defect requires a result change, report the precise causal path and numerical impact rather than preserving the old result artificially.

Do not change any rule merely to make this example classify as synthetic.

## 10. Test discipline

**Maximum: one additional collected test case. Zero preferred if existing coverage is sufficient.**

Follow `doc/test_quality/TEST_DISCIPLINE.md`.

Before adding tests:

1. Inspect the existing corroboration and reasoning-policy tests.
2. Identify whether the missing behavior is already covered.
3. Prefer modifying or extending an existing test.
4. Avoid duplicating the same condition across unit, integration and GUI tests.

The essential regression behavior is:

> A failed compound gate must report the actual unmet condition, even when its indicator-count requirement passes.

If this can be verified through an existing test, add no new test.

Do not introduce an additional test module for this task.

Run focused relevant tests.

The full suite can be deferred to the final combined release-validation gate, unless changes affect a shared production contract that warrants earlier validation.

Report baseline collected test count, added cases and net change.

## 11. Required validation

### Midjourney reference

Verify:

- `boundary.compound_support` returns the correct boolean.
- Every applicable gate condition is represented accurately.
- The reported failure reason matches production behavior.
- The confidence policy consumes the reported outcome.
- No unexpected changes occur in the numerical measurements or final conclusion.

### ComfyUI reference

Where existing fixtures permit, confirm that:

- The graph-based generation declaration remains recognized.
- No false enhancement declaration reappears.
- Corroboration reporting remains internally consistent.
- No unrelated hypothesis-selection changes occur.

### General consistency

For the inspected compound gates, verify:

```text
reported overall outcome
=
actual production gate outcome
=
outcome consumed by confidence policy
```

Any intentional difference in semantics must be clearly documented.

## 12. Deliverable

Create or update a concise report at:

`doc/reasoning_audit/origin_processing/task_e_corroboration_gate.md`

Include:

1. Exact root cause with source-file and function references.
2. All relevant gate conditions and observed outcomes.
3. Whether the defect was diagnostic-only or computational.
4. Files changed and why.
5. Before/after reasoning-trace excerpt.
6. Reference-case validation results.
7. Test-count accounting.
8. Git status.
9. Remaining limitations, if any.

Do not create additional audit documents unless essential.

## 13. Acceptance criteria

Task E is complete when:

- The failed boundary compound condition is fully explained.
- The supporting-indicator count is distinguished from the overall outcome.
- Eligible evidence and compound-strength evaluation are consistent.
- The confidence policy and diagnostic trace agree.
- Related compound gates have been checked for the same reporting defect.
- No arbitrary threshold or score tuning has occurred.
- The Midjourney and ComfyUI conclusions remain stable unless an independently demonstrated calculation correction requires otherwise.
- Regression coverage is minimal and nonredundant.
- Unrelated working-tree changes remain untouched.
- Nothing is staged, committed, pushed, tagged or published.

## 14. Final Codex response

Return:

**Root cause:** Exact reason the gate fails.

**Fix:** Diagnostic-only or computational correction, with justification.

**Before/after:** Show the changed gate explanation.

**Behavior:** Confirm whether hypothesis selection and scores changed.

**Validation:** Focused test results and test-count impact.

**Git:** Modified files and confirmation of no commits.

**Status:** Complete / Conditional / Blocked.

**Guiding principle: A forensic audit trail must disclose not only which evidence was observed, but exactly why the evidence did or did not satisfy the decision rule.**