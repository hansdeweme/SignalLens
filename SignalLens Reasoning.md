# CODEX TASK — SignalLens Reasoning Engine Correctness Fixes (Phase 1)

## Mission

You are the principal Python engineer and forensic reasoning architect for SignalLens, a Windows desktop application for evaluating forensic evidence of AI-generated and AI-enhanced photographs.

Your task is to implement five identified correctness corrections in the existing reasoning engine.

**Primary objective:** Ensure that a weak or inconclusive result for one forensic hypothesis cannot suppress stronger evidence supporting a different hypothesis.

The current implementation has demonstrated this defect in two real analysis traces:

- **Midjourney image:** suspicious score 22.193, explicit synthetic metadata, final Confidence Tier Low, neutral polarity.
- **Instagram image:** suspicious score 25.4776, sparse metadata, final Confidence Tier High, suspicious polarity.

Both results were selected by `route_strong_local_edit()`. The Midjourney result was terminated by an inconclusive localized-processing branch before synthetic-origin or provenance evidence could be evaluated.

The intention is not to increase AI-detection sensitivity artificially. It is to make conclusions logically consistent, conservative, auditable and properly scoped to their evidence.

## Scope

Implement these five corrections:

1. Prevent premature decision-route termination.
2. Separate synthetic-origin and localized-editing hypotheses.
3. Correct embedded generation-prompt propagation.
4. Correct provenance weighting and interpretation.
5. Remove suspicious scoring caused solely by missing metadata.

Relevant modules include:

- `decision_logic.py`
- `hypothesis_engine.py`
- The module defining `build_metadata_section()`
- `exiftool_backend.py`, only where necessary
- Existing summary/report adapters, only where necessary
- New or existing tests

Inspect the actual repository structure, imports and call sites before modifying anything.

## Non-negotiable constraints

- Preserve all existing forensic detectors and their measurement algorithms.
- Do not retune FFT, ELA, residual, sensor, CFA, compression, patch-similarity or segmentation thresholds.
- Do not upgrade dependencies.
- Do not introduce an ML classifier or LLM-based reasoning.
- Do not interpret internal heuristic scores as probabilities.
- Preserve the current Windows GUI, controller entry points and analysis modes.
- Maintain backward compatibility with existing reasoning-trace consumers where practical.
- Do not access, modify, delete or commit anything under `test_images/`.
- Do not modify PyInstaller scripts or packaging.
- Do not stage, commit, push, tag or publish changes.
- Keep the changes narrowly scoped and avoid unrelated refactoring.


---

## Correction 1 — Prevent premature decision-route termination

### Problem

In `decision_logic.py`, `synthesize_overall()` iterates over ordered decision routes and returns immediately after the first match.

An inconclusive localized-editing outcome can therefore prevent later evaluation of synthetic-generation and provenance evidence.

### Required implementation

Refactor route evaluation so that:

- A matched route records a candidate finding.
- An inconclusive route does not automatically terminate assessment of unrelated hypotheses.
- Provenance and synthetic-origin evidence can be evaluated even when a localized-editing route matches.
- The final decision is selected through explicit, deterministic rules.
- Route order alone cannot cause strong evidence from an independent hypothesis to disappear.

Do not implement a simplistic rule that always prioritizes provenance, always prioritizes the highest score, or always selects the highest confidence label.

A specialized inconclusive route may still limit confidence in its own hypothesis. It must not automatically limit confidence in every other hypothesis.

Preserve existing early safety checks and evidence-reliability safeguards where applicable.

### Acceptance criteria

- A localized-editing result of Low/neutral cannot suppress a separate, supported synthetic-origin finding.
- Strong localized-editing evidence is not overwritten by weak or ambiguous provenance metadata.
- Existing benign and inconclusive cases remain possible.
- The engine produces a deterministic result independent of irrelevant route reordering.
- The trace records which candidates were evaluated and why the overall result was chosen.

---

## Correction 2 — Separate synthetic-origin and localized-editing hypotheses

### Problem

The current decision engine effectively merges multiple forensic questions into one dominant decision.

However, evidence of synthetic generation and evidence of localized compositing answer different questions.

For example:

- An entirely AI-generated image may have no compositing boundary.
- A genuine photograph may contain a synthetically inserted subject.
- A genuine photograph may contain ordinary non-AI retouching.
- A synthetic image may exhibit camera-like processing artifacts.

### Required implementation

Introduce a lightweight structured hypothesis assessment, preferably using dataclasses.

At minimum, support:

**Synthetic-origin hypothesis**

Evaluates evidence for synthetic image generation or AI-mediated creation.

**Localized-editing hypothesis**

Evaluates evidence for compositing, copy-move reuse, subject replacement and region-specific processing.

**Camera-acquisition hypothesis**

Preserves camera-like acquisition evidence without interpreting it as categorical proof of authenticity.

Each hypothesis assessment should contain:

- Hypothesis identifier
- Assessment polarity
- Support level or confidence tier
- Supporting evidence identifiers
- Contradicting or moderating evidence identifiers
- Evidence limitations
- Selected decision branch or explanation

Reuse existing `DecisionResult`, `DecisionEnv`, `EvidenceSnapshot` and `ScoreCard` structures where practical.

Do not build an unnecessarily complex new framework.

### Overall synthesis

The existing GUI expects an overall pattern, narrative, confidence and polarity.

Preserve that interface while deriving its result from the hypothesis assessments.

The narrative must distinguish between:

- Confidence in synthetic-origin evidence.
- Confidence in a specific localized-editing mechanism.
- Camera-acquisition compatibility evidence.

A Low-confidence localized-editing conclusion must not imply Low confidence in synthetic origin.

A High-confidence localized-editing conclusion must not automatically imply High confidence that AI generation occurred.

### Acceptance criteria

- Separate hypothesis assessments appear in the reasoning trace.
- The GUI still displays a coherent overall conclusion.
- Existing JSON fields remain usable by current consumers.
- Camera-like and synthetic-origin evidence may coexist without being treated as logically impossible.
- The final conclusion identifies its primary supporting hypothesis.

---

## Correction 3 — Repair embedded generation-prompt propagation

### Problem

The metadata summary builder recognizes `EMBEDDED_GENERATION_PROMPT` and assigns the pattern:

`embedded_generation_prompt_detected`

However, `hypothesis_engine.py` currently recognizes only:

- `declared_synthetic_candidate`
- `declared_enhancement_candidate`

when deriving `metadata_synthetic`.

This can cause explicit generation-prompt evidence to be lost during hypothesis construction.

A separate defect exists in the metadata-missing calculation:

`ev.metadata == "sparse_or_stripped"`

This compares an object with a string instead of comparing its pattern.

### Required implementation

1. Ensure `embedded_generation_prompt_detected` is recognized by the hypothesis engine.
2. Correct metadata-missing detection to inspect the metadata pattern.
3. Avoid duplicating metadata classification definitions across multiple modules.
4. Preserve the distinction between generation and enhancement declarations.
5. Ensure explicit metadata signals survive into the final evidence snapshot and reasoning trace.

Review the exact source logic that creates `EMBEDDED_GENERATION_PROMPT`.

Currently, generic fields such as `prompt`, `parameters` and `workflow` may be treated as strong generation evidence simply because they are populated.

Do not automatically assume all such fields prove AI generation.

Where possible, distinguish explicit generation-workflow evidence from ambiguous workflow metadata.

### Acceptance criteria

- An explicit embedded generation declaration activates the correct derived signal.
- The declaration survives hypothesis assessment.
- Sparse-metadata detection works correctly.
- Generic workflow metadata does not automatically receive the strongest generation classification.
- Metadata classification and derived signals remain internally consistent.

---

## Correction 4 — Correct provenance interpretation and routing

### Problem

The existing provenance route requires:

`provenance_boost >= 1.0`

However, a single synthetic metadata declaration contributes only `0.75`.

Consequently, a declared generation context may never qualify for the provenance route without additional evidence.

More importantly, a numeric threshold is currently standing in for several distinct types of evidence.

### Required implementation

Introduce explicit provenance-evidence states.

At minimum:

- `verified_generation_assertion`
- `unverified_generation_declaration`
- `unverified_enhancement_declaration`
- `ambiguous_tool_or_workflow_metadata`
- `provenance_present_unverified`
- `no_substantive_provenance_evidence`

These can be implemented as an enum or equivalent typed representation.

**Important:** Do not label an assertion cryptographically verified unless an actual validator has performed successful verification.

The existing ExifTool backend identifies possible C2PA presence but does not cryptographically verify it.

C2PA presence must not be promoted to verified provenance.

### Required routing behavior

- Explicit unverified generation declarations contribute to the synthetic-origin hypothesis.
- Weak tool-name matches do not automatically dominate the overall conclusion.
- Verified assertions, when genuinely available, can be distinguished from unverified declarations.
- Metadata absence does not imply either synthetic or photographic origin.
- Contradictory camera-like evidence is discussed in context rather than universally cancelling provenance.
- The provenance route no longer relies exclusively on the `>= 1.0` boost threshold.

Preserve existing numerical score fields for compatibility where possible, but make provenance decisions depend on structured evidence categories.

### Acceptance criteria

- A single credible unverified generation declaration can produce a provenance-related hypothesis finding without requiring OSINT corroboration.
- Its result explicitly states that metadata authenticity is unverified.
- Generic editing metadata does not imply AI generation.
- No unverified C2PA presence receives a verified label.
- Strong visual evidence can coexist with conflicting provenance evidence.
- The system does not mechanically assign High confidence to every embedded prompt.

---

## Correction 5 — Remove suspicious scoring caused solely by missing metadata

### Problem

The metadata summary currently treats `sparse_or_stripped` as suspicious, even with a numerical score of `0.0`.

`compute_base_scores()` uses polarity and status weights, so this contributes to the suspicious score.

That is not a defensible inference.

Metadata may be missing because of:

- Social-media processing
- Export or recompression
- Screenshots
- Privacy-related metadata removal
- File conversion
- Intentional stripping

Its absence does not establish AI generation.

### Required implementation

Change sparse or stripped metadata to neutral evidence.

Preserve its informational value as a limitation on provenance assessment.

Ensure that sparse metadata:

- Does not contribute a positive suspicious score.
- Does not independently activate synthetic-origin evidence.
- Does not count as an independent suspicious domain.
- Can still be described in the narrative as missing provenance coverage.

Check any other logic that treats missing metadata as positive evidence of synthetic origin.

### Acceptance criteria

- A metadata section with `pattern="sparse_or_stripped"` and `score=0.0` contributes zero positive suspicious evidence.
- An authentic image with stripped EXIF is not penalized solely for metadata absence.
- Existing metadata-declaration detections remain functional.
- The reasoning trace identifies missing provenance evidence without misclassifying its polarity.

---

## Regression testing requirements

Create focused automated tests using pytest or the repository's established testing framework.

Do not access or include the private `test_images/` directory.

Use synthetic `ModuleSummary` objects, mocked ExifTool payloads and existing non-image reasoning traces where appropriate.

### Required test cases

**Test 1 — Midjourney reasoning-trace regression**

Reconstruct the supplied Midjourney case where practical:

- `metadata_synthetic = true`
- `provenance_boost = 0.75` in the legacy scorecard
- `suspicious_score ≈ 22.193`
- `local_edit_support_score ≈ 4.50`
- `boundary_reliability_score = 0.75`
- `camera_counter_support = 1.25`
- Localized-editing corroboration is inconclusive

Expected:

- Localized-editing uncertainty remains visible.
- Synthetic-origin declaration remains visible.
- The overall conclusion does not incorrectly treat localized-editing uncertainty as a rejection of synthetic-origin evidence.
- No unsupported claim of verified provenance.

**Test 2 — Instagram reasoning-trace regression**

Reconstruct the supplied Instagram case where practical:

- Sparse metadata
- `suspicious_score ≈ 25.478` in the legacy scorecard
- `local_edit_support_score ≈ 6.70`
- Strong boundary-focused corroboration
- Strong subject-boundary evidence
- High boundary reliability

Expected:

- Strong localized-processing evidence remains recognizable.
- Missing metadata provides no positive synthetic evidence.
- The overall conclusion does not automatically equate compositing with AI generation.

**Test 3 — Metadata-only generation declaration**

Explicit unverified generation metadata, with otherwise inconclusive visual evidence.

Expected: a synthetic-origin provenance finding qualified as unverified, not automatically High confidence.

**Test 4 — Embedded prompt**

A clearly identified generation prompt/workflow.

Expected: correct propagation into `DerivedSignals` and hypothesis assessments.

**Test 5 — Generic workflow field**

An ordinary non-generative workflow entry.

Expected: no automatic strong AI-generation assertion.

**Test 6 — Authentic-looking image with stripped metadata**

No meaningful synthetic evidence.

Expected: neutral metadata finding, zero suspicious-score contribution from missing metadata.

**Test 7 — Camera-like evidence plus synthetic declaration**

Expected: both evidence families remain visible; neither is categorically discarded.

**Test 8 — Existing benign and inconclusive routing**

Expected: benign and inconclusive outcomes remain available and are not systematically promoted to suspicious.

**Test 9 — Route ordering**

Reorder unrelated decision routes in a test.

Expected: the hypothesis assessments and final result remain logically equivalent.

**Test 10 — JSON compatibility**

Expected: current required top-level reasoning-trace fields remain available, with new hypothesis fields added compatibly.

Do not assert that all historical final confidence labels must remain unchanged. Changes that correct a demonstrated defect are expected. Document every intentional difference.

---

## Implementation procedure

### Step 1 — Inspect

Read the relevant source files and identify:

- The complete metadata-classification path.
- The hypothesis engine's derived signal rules.
- Scorecard provenance calculations.
- The complete decision-route registry.
- Call sites consuming the five-element return value of `synthesize_overall()`.
- GUI and report dependencies on `reasoning_trace`.

Before editing, produce a brief implementation plan identifying files, interfaces and risks.

### Step 2 — Establish baseline

Run all existing tests, if available.

Record the baseline results and any pre-existing failures.

Do not repair unrelated failures.

### Step 3 — Implement

Apply the five corrections as small, reviewable changes.

Prefer reusable, typed helpers over more scattered conditional statements.

Do not broadly rewrite the detector or reporting architecture.

### Step 4 — Test

Run the focused regression suite, existing tests, import checks and syntax checks.

Perform a static compatibility review of the controller and GUI integration.

Do not claim end-to-end Windows testing unless it has actually been performed.

### Step 5 — Review

Inspect the resulting diff for accidental changes to forensic thresholds, unrelated modules or project configuration.

Ensure no test images, binary artifacts or generated analysis outputs are staged.

---

## Deliverables

1. Corrected reasoning-engine implementation.
2. Automated tests for all ten required scenarios.
3. Backward-compatible reasoning-trace schema with hypothesis-level assessments.
4. Brief technical document explaining the corrected reasoning behavior.
5. Before/after comparison of the Midjourney and Instagram cases.
6. Final test summary and changed-file inventory.

## Required final report

Provide:

**A. Implementation summary**

Which corrections were implemented and which files changed.

**B. Behavioral comparison**

For both reference cases, show:

- Original dominant pattern
- New dominant pattern
- Original confidence tier
- New confidence tier
- Synthetic-origin assessment
- Localized-editing assessment
- Explanation of any changes

If the complete trace cannot be replayed directly, clearly distinguish fixture-based simulation from an actual pipeline execution.

**C. Tests**

Number passed, failed and skipped, including pre-existing failures.

**D. Compatibility**

Any changes to APIs, JSON fields, GUI behavior or existing decision routes.

**E. Remaining concerns**

Issues discovered but deliberately left outside scope, especially correlated evidence weighting, scorecard recalculation and broader confidence calibration.

**F. Git status**

Current branch, modified files and untracked files.

Do not commit, push, tag or publish.

## Success criterion

SignalLens must no longer confuse uncertainty about one forensic mechanism with uncertainty about an entirely different hypothesis.

The final reasoning must preserve relevant evidence, explain contradictions and remain appropriately cautious about unverified metadata.

**Correctness, defensibility and auditability take precedence over higher confidence scores or increased suspicious classifications.**

