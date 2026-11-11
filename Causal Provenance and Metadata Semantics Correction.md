# Codex Task B — Causal Provenance and Metadata Semantics Correction

**Repository:** `D:\Coding\SignalLens`  
**Priority:** High — pre-release correctness  
**Authorization:** Bounded implementation and validation  
**Scope:** Metadata interpretation, provenance, reasoning, primary-finding selection and necessary presentation adapters

## 1. Read first

Read all five Task A documents under:

`doc/reasoning_audit/causal_provenance/`

Treat `root_cause_report.md` and `task_b_implementation_plan.md` as the starting point.

Read `AGENTS.md` and `doc/test_quality/TEST_DISCIPLINE.md`.

Inspect the actual source implementation before making changes. Where this task differs from Task A's source-grounded findings, document the discrepancy and select the smallest defensible implementation.

Preserve unrelated or inherited working-tree changes. Do not commit or push.

## 2. Objective

Correct two demonstrated issues:

**Issue A — Causal misprioritization**

The engine selects High-confidence localized editing despite embedded metadata describing a coherent full-image generation workflow.

The existing primary-selection policy gives decisive localized mechanisms priority over other explanations without adequately distinguishing regional processing anomalies from evidence of a separate editing operation.

**Issue B — Incorrect enhancement declaration**

A substring match against the unused ComfyUI output port `denoised_output` creates `metadata:DECLARED_ENHANCEMENT`.

The identifier is not evidence that an existing photograph was enhanced.

Implement generalizable corrections without special-casing the example image, FLUX.2 checkpoint or LoRA filename.

## 3. Workflow interpretation

Introduce a minimal structured workflow interpretation for recognized ComfyUI JSON metadata.

Where graph evidence permits, distinguish:

- Declared full-image generation.
- Declared image-to-image processing.
- Declared inpainting or masked editing.
- Declared enhancement/upscaling.
- Mixed or multi-stage workflows.
- Indeterminate or unsupported workflows.

For full-generation classification, inspect the active graph feeding the saved output, including latent initialization, image inputs, sampler connections, decoding and output paths.

Do not classify solely from keyword presence or model names.

Respect custom nodes, missing links, unsupported structures and ambiguous graphs. Return an indeterminate interpretation where necessary.

Keep two concepts explicitly separate:

- **Declared process:** What the embedded workflow describes.
- **Provenance authenticity:** Whether the workflow's relationship to the image is authenticated.

A coherent workflow does not imply verified provenance.

Maintain compatibility with existing metadata and evidence contracts wherever possible. Avoid building a general-purpose workflow execution framework.

## 4. Fix enhancement false positives

Replace inappropriate substring-based enhancement interpretation within structured workflow payloads.

The following must not independently trigger `DECLARED_ENHANCEMENT`:

- `denoised_output`
- A bare `denoise` parameter.
- Standard sampling or latent-decoding operations.
- LoRA or model identifiers containing incidental enhancement-related words.

An actual, explicit enhancement declaration or a structurally established enhancement workflow may still produce the finding.

Preserve legitimate unstructured metadata matching where appropriate.

Audit whether `PNG:Prompt` and `PNG:Workflow` describe the same underlying graph. Do not count duplicate representations as independent evidence.

Do not solve this problem by simply excluding the exact substring `denoised_output` while leaving the broader semantic defect intact.

## 5. Correct causal interpretation and primary selection

Retain the existing hypothesis-specific assessments and confidence architecture.

Introduce the smallest necessary compatibility or selection correction such that the system distinguishes:

1. Full-image generation declared by embedded metadata.
2. Regional processing anomalies found in pixels.
3. Specific evidence that a separate localized edit occurred.

Regional anomalies may coexist with synthetic creation without establishing an additional editing operation.

Do not discard them.

When a coherent full-generation workflow exists, the overall finding must explain its relevance, authenticity limitations and relationship to localized measurements.

A High localized confidence tier must not automatically establish that the image underwent a distinct subsequent edit.

Conversely, an unauthenticated generation graph must not automatically override strong, specific evidence of real localized manipulation.

Preserve competing hypotheses when appropriate, including an unresolved outcome where the evidence does not permit reliable selection.

The final decision must be deterministic, auditable and derived from explicit rules.

**Do not force a predetermined primary hypothesis for the reference image.** A more qualified overall finding is acceptable if it better represents the available evidence.

## 6. Investigate the synthetic-route weakness

Task A found:

`synthetic_boost = 0.4`, below the `1.0` threshold.

It also identified three omitted patch metrics.

Trace the omission and determine whether it is:

- An intended restriction.
- An evidence-contract mismatch.
- A missing adapter mapping.
- A genuine computation or routing defect.

Correct a proven data-flow defect if it falls within this task's scope.

Do not lower thresholds or raise scores merely to make `route_synthetic_multi_signal` match.

If the issue requires broader detector changes, document and defer it rather than expanding Task B.

## 7. Presentation and reporting

Ensure the GUI, reasoning trace, saved investigation and exported reports consistently distinguish:

- Declared creation process.
- Unverified provenance.
- Supporting and contradictory image-based evidence.
- Localized processing anomalies.
- Evidence of a separate editing operation, when established.

Preserve the existing immutable analysis/presentation contracts, session identity and report snapshot behavior.

Do not redesign the GUI or introduce new workspaces.

Avoid displaying raw ComfyUI JSON as the only explanation when a concise structured description can be provided.

## 8. Mandatory test discipline

**Excessive regression testing is expressly prohibited.**

Before adding any tests:

1. Audit relevant existing tests and fixtures.
2. Identify which new observable behaviors lack coverage.
3. Prefer extending existing parameterized tests.
4. Reuse the established metadata, reasoning and presentation fixtures.
5. Avoid duplicating tests for session identity, worker lifecycle, report consistency and unchanged forensic scoring.

Target **no more than five additional collected test cases** for this task. This is a ceiling, not a target.

Any proposed increase above five requires a specific explanation of an uncovered critical behavior and must be reported as an exception—not silently implemented.

Do not create one test module per scenario or repeat the same invariant across unit, integration and GUI tests.

Required behaviors should include, using existing coverage wherever possible:

- `denoised_output` does not declare enhancement.
- A coherent empty-latent graph is recognized as declared full generation.
- Image-input and masked workflows are not incorrectly classified as full generation.
- Unverified or misleading metadata cannot independently authenticate image origin.
- Primary-selection reasoning remains coherent when localized anomalies coexist with a generation declaration.

Keep the test cases independent of specific FLUX.2 or LoRA filenames.

Run focused tests during implementation and the complete existing suite once at the final validation gate.

Report existing count, additions, consolidations, removals and net change.

Do not interpret an increasing test count as evidence of higher quality.

## 9. Regression and release safeguards

Preserve existing detector outputs, numerical scorecards and reference-image behavior except where an intentional reasoning or metadata correction changes the interpretation.

For each affected reference image, report:

- Analysis profile.
- Source identity/hash.
- Relevant settings.
- Before-and-after primary hypothesis.
- Before-and-after confidence tiers.
- Exact reason for any changed conclusion.
- Whether numerical detector measurements changed.

Do not regenerate baselines to conceal failures.

The previous reference cases must continue to run successfully, but expected interpretations may only be updated where justified by the new causal rules.

Avoid introducing claims of calibrated probabilities or verified metadata authenticity.

## 10. Deliverables

Provide:

1. Source changes implementing the bounded correction.
2. A short implementation report explaining the new workflow semantics.
3. A before-and-after comparison for the original ComfyUI case.
4. The root cause and correction for `DECLARED_ENHANCEMENT`.
5. An explanation of any synthetic-route changes or remaining limitations.
6. Test coverage and full-suite results.
7. A concise change inventory and Git status.

Document changes under `doc/reasoning_audit/causal_provenance/` without generating unnecessary reports.

Do not stage, commit, tag or push.

## 11. Acceptance criteria

Task B succeeds when:

- A structured ComfyUI workflow is interpreted from its connected graph, not only keyword matches.
- The original `denoised_output` false positive is eliminated.
- Legitimate enhancement declarations remain detectable.
- Declared creation history is separated from provenance authenticity.
- Localized anomalies are no longer automatically treated as proof of a separate editing operation.
- Primary selection explains the relationship between synthetic creation and localized evidence.
- Existing numerical scorecards and detector behavior are preserved unless a clearly documented data-flow defect requires correction.
- Existing reports and GUI presentation remain consistent.
- No excessive regression tests are introduced.
- Full-suite validation passes.
- No unrelated changes are made or committed.

**The success criterion is better causal reasoning and more precise metadata interpretation—not simply a different label for one synthetic image.**