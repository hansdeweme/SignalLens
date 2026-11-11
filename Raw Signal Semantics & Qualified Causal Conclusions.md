# Codex Task F — SignalLens: Raw Signal Semantics & Qualified Causal Conclusions

**Repository:** `D:\Coding\SignalLens`  
**Target release:** `0.1.0-beta.1`  
**Priority:** Medium–High  
**Task type:** Focused investigation and bounded implementation  
**Scope:** Raw signal semantics, derived flags, causal qualification, trace and report consistency  
**Git:** Do not stage, commit, push, tag or publish.

## 1. Mission

Resolve the remaining interpretability issue identified after Tasks D and E.

The current Midjourney reasoning trace contains:

```text
strong_local_edit = true
strong_cross = true
```

Yet the qualified forensic conclusion states:

```text
Primary Hypothesis: synthetic_origin
Confidence: Medium

localized_editing:
  Confidence: Low
  Polarity: neutral

separate_edit_status:
  not_established_from_regional_anomalies
```

These results may be logically compatible if `strong_local_edit` represents an intermediate regional-anomaly trigger rather than a supported conclusion about editing history.

However, the current name implies stronger causal evidence than the final assessment supports.

**Investigate the precise semantics of these fields and ensure no consumer interprets an intermediate signal as an established editing operation.**

The task must correct misleading semantics or unsafe data flow without retuning the forensic detection system.

## 2. Mandatory preparation

Read:

- `AGENTS.md`
- `doc/test_quality/TEST_DISCIPLINE.md`
- `doc/reasoning_audit/origin_processing/root_cause_report.md`
- `doc/reasoning_audit/origin_processing/origin_processing_architecture.md`
- `doc/reasoning_audit/origin_processing/task_d_implementation.md`
- `doc/reasoning_audit/origin_processing/task_e_corroboration_gate.md`
- Relevant Task B causal-provenance implementation documentation

Inspect the current Git working tree and preserve all inherited modifications.

Study the existing source contracts before introducing any new fields or renaming existing ones.

## 3. Reference-case invariants

The current Midjourney reference result is:

| Dimension | Current result |
|---|---|
| Primary hypothesis | `synthetic_origin` |
| Synthetic confidence | Medium |
| Localized editing confidence | Low |
| Localized polarity | Neutral |
| Separate editing | Not established |
| Declared process | `unspecified_generation_process` |
| Technical provenance authenticity | Unverified |
| Suspicious score | 18.04075 |
| Benign score | 1.50 |

Task E established that the boundary compound gate correctly fails:

```text
Structural indicator count: PASS

Strength condition: FAIL
subject_boundary = 0.393316
required minimum = 0.45

Overall: FAIL
```

Do not reopen or retune this gate unless a separate, demonstrable defect is discovered.

The reference conclusion is a regression invariant, not an instruction to force a particular classification.

## 4. Investigation A — Establish the meaning of raw derived flags

Trace the production origins of:

```text
strong_local_edit
strong_cross
fragmented_local_edit
boundary_stack_medium
subject_boundary_medium
region_geometry_unreliable
person_mask_reliable
```

Also inspect other similarly named `*_edit`, `*_clone`, `*_synthetic` and `*_support` flags where they participate directly in causal interpretation.

For each relevant flag, determine:

1. Which measured observations create it.
2. Whether it represents a detector result, composite heuristic, confidence condition or causal conclusion.
3. Whether its value is established before or after corroboration checks.
4. Whether it incorporates contradictory or moderating evidence.
5. Whether the name accurately describes its meaning.
6. Whether the value is stored in saved results or only constructed transiently.
7. Which downstream components consume it.

Produce a compact semantic inventory.

Do not assume that a `true` value is incorrect simply because the final hypothesis has Low confidence.

The essential distinction is between an intermediate trigger and a qualified conclusion.

## 5. Investigation B — Audit downstream consumers

Trace the use of `strong_local_edit` and related flags through:

- Evidence aggregation.
- Scorecard contribution calculation.
- Production corroboration.
- Confidence policies.
- Route selection.
- Hypothesis construction.
- Investigation synthesis.
- GUI workspaces.
- Exported reports.
- Saved JSON contracts.
- Reasoning traces.

Specifically determine whether any consumer:

- Treats a raw trigger as proof of an editing operation.
- Uses a preliminary flag after a qualifying corroboration gate has failed.
- Gives the same observation causal credit more than once.
- Displays an unqualified flag without its scope.
- Infers separate editing from regional processing alone.
- Bypasses the Task D multidimensional synthesis.
- Misrepresents detector strength as hypothesis confidence.

Distinguish an actual semantic or decision defect from merely unfortunate naming.

**Do not alter valid numerical contributions solely because a flag name sounds misleading.**

## 6. Investigation C — Define explicit semantic layers

Use the existing architecture where possible, but establish a clear conceptual separation between:

### Layer 1 — Measurement

Direct or computed forensic observations.

Examples:

```text
boundary transition measurement
ELA/residual convergence
regional FFT difference
patch similarity
```

### Layer 2 — Raw or derived signal

A heuristic trigger indicating that a particular pattern of observations is present.

Example:

```text
regional processing anomaly trigger = true
```

This is not necessarily evidence of a specific editing operation.

### Layer 3 — Qualified support

An assessment of how strongly the measurements support a defined interpretation after eligibility, corroboration, reliability and moderating conditions are considered.

Example:

```text
localized editing support = Low
```

### Layer 4 — Causal conclusion

A defensible interpretation of image creation or modification history.

Example:

```text
separate editing operation = not established
```

Investigate whether these layers are already represented in existing data structures.

**Prefer clarifying or reusing existing fields rather than introducing a new parallel signal framework.**

## 7. Implementation strategy

Choose the least disruptive solution supported by the investigation.

Possible approaches include:

### Option A — Clarify diagnostic presentation

Retain the existing field names in internal contracts, but display their semantic scope explicitly.

For example:

```text
Raw derived trigger:
  strong_local_edit = true

Interpretation:
  Regional anomaly trigger observed.
  Does not establish a separate editing operation.

Qualified hypothesis:
  localized_editing = Low

Causal assessment:
  separate_edit_status = not_established
```

### Option B — Introduce a more precise internal alias

Where necessary, introduce an internally clearer name such as:

```text
strong_regional_processing_trigger
```

Keep the legacy field as a compatibility alias if it is persisted or used by external consumers.

Avoid duplicating independently mutable state.

### Option C — Correct an unsafe consumer

If a downstream component improperly treats a raw flag as an established mechanism, fix that specific consumer to use the qualified assessment instead.

Document any changes to decision behavior.

### Selection criteria

Prefer Option A if the problem is limited to interpretation and presentation.

Use Option B only when the existing name creates a genuine maintenance or contract risk.

Use Option C only where source inspection demonstrates an incorrect data dependency.

A combination is permitted if necessary, but avoid broad refactoring.

## 8. Data-contract and compatibility requirements

Before renaming or replacing anything, determine whether the affected fields appear in:

- `analysis_run.json`
- `current_report.json`
- `ui_artifacts_v1.json`
- `reasoning_trace.json`
- `final_summary.json`
- Existing saved investigation revisions
- Existing report loaders
- External or documented APIs

If fields are persisted:

- Preserve backward compatibility.
- Do not silently change historical meanings.
- Do not invalidate previously saved investigations.
- Do not rewrite historical reports.
- Use schema/version changes only where truly required.

A compatibility alias is preferable to a breaking rename when the old field remains part of a supported contract.

## 9. Reasoning-trace improvements

A technical reader should be able to distinguish raw signals from qualified findings without consulting the source code.

Consider an explicit separation similar to:

```text
Derived Measurement Signals
---------------------------
strong_local_edit: true
  Scope: raw regional-processing trigger
  Causal significance: not established

Qualified Hypothesis
--------------------
localized_editing: Low / neutral
  Corroboration: insufficient

Causal Assessment
-----------------
separate_edit_status:
  not_established_from_regional_anomalies
```

This is an illustrative presentation, not a mandatory serialization structure.

Retain the original raw diagnostic values so future investigations remain auditable.

Ensure the trace does not imply that `strong_local_edit=true` overrides failed corroboration.

Keep explanations concise and avoid repeating the same disclaimer throughout the report.

## 10. GUI and report consistency

Inspect the six workspaces:

- Overview
- Image Forensics
- Evidence
- Reasoning
- Provenance
- Reports

Focus on displays that consume raw signal flags or describe localized editing.

Requirements:

- Overview should lead with the qualified investigation synthesis.
- Image Forensics may expose raw triggers, clearly labeled.
- Evidence should distinguish measurements from interpretations.
- Reasoning should show raw triggers, corroboration and final outcomes separately.
- Provenance must not infer editing history from unrelated raw signals.
- Reports must preserve the same semantic distinctions as the GUI.

Do not redesign the workspaces.

Do not add decorative UI elements, new navigation structures or additional panels unless necessary.

## 11. Numerical and policy invariants

Do not change:

- Detector algorithms.
- Detection thresholds.
- Evidence weights.
- Scorecard aggregation.
- Hypothesis precedence.
- Confidence tiers.
- Causal-provenance policy.
- OSINT behavior.
- Investigation revision semantics.

Exceptions require a demonstrated consumer defect directly within this task's scope.

If such a defect is found:

1. Document the incorrect dependency.
2. Explain the expected causal behavior.
3. Implement the smallest correction.
4. Disclose any effect on scores or decisions.
5. Do not tune values to preserve or achieve a preferred verdict.

The intended outcome is improved interpretability and correctness, not improved apparent detection performance.

## 12. Test discipline

Follow `doc/test_quality/TEST_DISCIPLINE.md`.

**Maximum: one additional collected test case. Zero preferred.**

Inspect existing tests before writing anything.

Prefer extending an existing test that already exercises reasoning-trace serialization or qualified hypothesis presentation.

The essential behavior to validate is:

> A raw regional-processing trigger can be true while localized editing support is Low and a separate editing operation remains unestablished, without contradictory reporting or incorrect downstream causal inference.

Avoid:

- New test modules.
- Duplicated unit and GUI assertions.
- Large parameterized expansions.
- New image fixtures.
- Broad golden-output regeneration.
- Redundant snapshot tests.

Run focused tests relevant to changed behavior.

A full-suite run may be performed once at the final validation gate.

Report the baseline of **525 collected tests**, additions, removals and net change.

## 13. Reference validation

### Midjourney image

Verify that the result continues to distinguish:

```text
Synthetic origin: Medium
Localized editing: Low
Separate edit: Not established
Metadata authenticity: Unverified
```

Confirm that `strong_local_edit=true`, if retained, is described as a raw or derived trigger rather than a final causal conclusion.

### ComfyUI/FLUX.2 image

Verify that:

- Full-generation context remains recognized.
- Regional anomalies do not imply subsequent localized editing.
- The previous `denoised_output` false-positive correction remains intact.
- Raw signals and qualified conclusions are consistently distinguished.

### Conventional photograph

Use an existing photograph fixture where practical.

Verify that a raw anomaly trigger alone cannot be presented as proof of AI generation, compositing or subsequent editing.

Do not add a new image fixture unless demonstrably necessary.

## 14. Deliverables

Create or update:

`doc/reasoning_audit/origin_processing/task_f_signal_semantics.md`

Include:

1. Root-cause determination.
2. Semantic inventory of affected flags.
3. Downstream consumer audit.
4. Selected implementation option and justification.
5. Files changed.
6. Before/after trace excerpts.
7. Data-contract compatibility assessment.
8. Midjourney and ComfyUI validation.
9. Test-count accounting.
10. Git status and remaining limitations.

Do not create unnecessary additional documentation.

## 15. Acceptance criteria

Task F is complete when:

- The precise meaning of `strong_local_edit` is established.
- Intermediate signals and qualified conclusions are distinguishable.
- No downstream component incorrectly promotes a raw trigger to an established editing operation.
- The reasoning trace communicates the distinction explicitly.
- GUI and reports use consistent terminology.
- Existing saved investigations remain readable.
- The Midjourney conclusion is preserved unless a concrete causal defect justifies change.
- The ComfyUI correction remains intact.
- Numerical detector measurements are unchanged unless a proven defect requires otherwise.
- No arbitrary threshold or weight tuning occurs.
- Test-count growth remains minimal.
- Unrelated working-tree changes are preserved.
- Nothing is staged, committed, pushed, tagged or published.

## 16. Final Codex response

Return:

**1. Root cause:** Why the raw flag and final conclusion appear inconsistent.

**2. Semantic distinction:** What the flag measures versus what the qualified hypothesis establishes.

**3. Consumer audit:** Any unsafe dependencies identified and corrected.

**4. Implementation:** Files changed and compatibility considerations.

**5. Before/after:** Representative reasoning-trace excerpts.

**6. Reference cases:** Midjourney and ComfyUI results.

**7. Validation:** Focused tests, full-suite results if executed, and test-count delta.

**8. Git:** Working-tree changes; no staging or commits.

**9. Status:** Complete / Conditional / Blocked.

**Guiding principle: A detector can strongly observe an anomaly without establishing the causal process that produced it. SignalLens must preserve that distinction from measurement through final report.**