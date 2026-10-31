# CODEX TASK — SignalLens Phase 1.1: Hypothesis-Scoped Evidence and Validation

## Mission

You are the principal Python engineer and forensic reasoning architect for SignalLens.

Phase 1 introduced hypothesis-aware reasoning, separating:

1. Synthetic origin
2. Localized editing
3. Camera acquisition compatibility

The implementation now preserves synthetic-generation declarations even when localized-editing evidence is inconclusive.

However, one important defect remains: **the human-readable Supporting Signals and Contradicting Signals lists still combine evidence belonging to different hypotheses.**

Your mission is to correct that inconsistency, strengthen regression coverage and verify that the new reasoning architecture remains internally coherent.

This is a focused correctness task, not a redesign of the forensic engine.

## Current implementation status

The previous Codex task implemented:

- Candidate-based decision routing.
- Separate hypothesis assessments.
- Embedded generation-prompt propagation.
- Structured provenance-evidence categories.
- Neutral handling of sparse metadata.

The current automated test suite reports **61 passing tests**.

During manual retesting with the original Midjourney image, a metadata-extraction defect was discovered. Codex subsequently corrected recognition of the embedded prompt and IPTC `trainedAlgorithmicMedia` declaration and excluded folder names from metadata evidence.

The latest reported Midjourney assessment is:

| Hypothesis | Result |
|---|---|
| Overall | Medium / suspicious |
| Synthetic origin | Medium / suspicious; declaration unverified |
| Localized editing | Low / neutral |
| Camera compatibility | Medium / benign |

The Instagram reference image retains a High-confidence localized-editing conclusion.

These results must be preserved unless testing demonstrates a genuine correctness issue.

---

## 1. Correct hypothesis-scoped supporting evidence

### Problem

The current overall narrative is assembled using generic helpers such as:

- `extract_secondary_patterns()`
- `extract_contradicting_patterns()`
- `append_secondary_patterns()`
- `append_contradicting_patterns()`

These helpers historically relied primarily on signal polarity and strength.

That is insufficient after introducing multiple hypotheses.

For example:

- Copy-move evidence does not directly establish synthetic image generation.
- Boundary-processing consistency does not necessarily contradict whole-image generation.
- Camera-like sensor evidence does not automatically disprove AI enhancement or localized compositing.
- Explicit generation metadata does not establish a particular localized-editing mechanism.

### Required changes

Inspect the current implementation of `finish_decision()`, the hypothesis assessments and the narrative-generation helpers.

Ensure that supporting and contradicting evidence is selected according to the **hypothesis being evaluated**, not simply according to the overall polarity.

Each hypothesis must maintain its own:

- Supporting evidence
- Contradicting evidence
- Moderating or contextual evidence
- Evidence limitations

The overall narrative should present evidence directly relevant to its selected primary hypothesis.

Evidence belonging to other hypotheses must remain accessible through their separate assessments.

### Important constraints

Do not implement hypothesis scoping through simplistic substring matching of pattern names.

Prefer an explicit, maintainable mapping of evidence identifiers or evidence families to supported hypotheses.

A signal may legitimately inform more than one hypothesis, but its relevance and interpretation must be explicit.

Do not hide inconvenient contradicting evidence to make conclusions appear stronger.

### Acceptance criteria

For a synthetic-origin conclusion:

- Explicit generation declarations may appear as supporting evidence.
- Validated synthetic-structure indicators may contribute.
- Copy-move findings must not automatically appear as synthetic-origin support.
- Boundary-processing consistency must not automatically be presented as contradiction.
- Camera-like evidence may appear as contextual or moderating evidence where appropriate.

For a localized-editing conclusion:

- Boundary anomalies, compression inconsistencies and spatially supported duplication may contribute.
- Synthetic-generation declarations must not automatically establish compositing.
- Camera compatibility must not automatically negate localized editing.

For a camera-acquisition assessment:

- Sensor and CFA evidence must retain their limited, compatibility-oriented interpretation.
- Camera-like structure must not be described as proof that an image is authentic.

---

## 2. Ensure consistency between structured reasoning and human-readable reporting

### Problem

SignalLens now produces separate structured hypothesis assessments, but the overall narrative may still use legacy signal-selection logic.

This can result in a JSON explanation that differs conceptually from the GUI's prose.

### Required changes

Use the structured hypothesis assessments as the authoritative source for hypothesis-specific evidence presentation.

Where possible, avoid independently reconstructing supporting and contradicting evidence through separate narrative heuristics.

The following outputs should be consistent:

- Selected primary hypothesis
- Overall dominant pattern
- Overall polarity
- Overall confidence tier
- Supporting evidence
- Contradicting evidence
- Contextual limitations
- Hypothesis-specific explanations

Preserve the existing five-element return contract of `synthesize_overall()`.

Preserve existing reasoning-trace fields where practical. Add fields rather than removing or renaming them.

Existing GUI and report consumers must continue to work.

---

## 3. Strengthen metadata-extraction regression tests

### Background

The initial Phase 1 tests passed, but a manual real-image test revealed that the metadata extractor was not delivering the expected synthetic-generation declaration.

The defect involved embedded generation prompts and IPTC `trainedAlgorithmicMedia`.

This exposed a coverage gap between isolated reasoning tests and actual metadata extraction.

### Required tests

Add integration-oriented tests using controlled, synthetic metadata payloads.

Verify the complete processing path:

`ExifTool payload → metadata extraction → metadata summary → derived signals → hypothesis assessments → final reasoning`

Test at least:

1. Explicit embedded Midjourney generation prompt.
2. IPTC `trainedAlgorithmicMedia` indicating generative creation.
3. Generic workflow metadata without a generation declaration.
4. Creator or author metadata without AI-generation evidence.
5. AI-related text appearing only in a filename or folder path.
6. Sparse or stripped metadata.
7. C2PA-related metadata without cryptographic verification.
8. Conflicting camera metadata and explicit generation declarations.

For the IPTC case, respect the actual semantics of the metadata property and its controlled vocabulary rather than treating every populated `trainedAlgorithmicMedia` field as equivalent.

The tests must verify that the original evidence survives into the final hypothesis assessment.

Do not use or modify anything under `test_images/`.

---

## 4. Add hypothesis-specific regression scenarios

Create deterministic tests for the following cases.

### Scenario A — Midjourney declaration with inconclusive localized editing

Input characteristics:

- Explicit synthetic-generation declaration
- Weak boundary-specific corroboration
- Some suspicious structural signals
- Camera-compatible sensor evidence

Expected:

- Synthetic-origin declaration retained
- Provenance marked unverified
- Localized-editing uncertainty retained
- Camera compatibility retained
- Overall Supporting Signals scoped to synthetic origin
- No inappropriate copy-move or boundary-consistency explanations

### Scenario B — Instagram-like localized-processing finding

Input characteristics:

- Sparse metadata
- Strong boundary-focus anomaly
- Strong subject-boundary evidence
- Multiple localized-processing indicators

Expected:

- Strong localized-editing conclusion remains possible
- Sparse metadata provides no positive suspicious weight
- No unsupported claim of AI generation
- Supporting evidence relates to localized processing

### Scenario C — Multiple supported hypotheses

Input characteristics:

- Explicit generation declaration
- Strong localized-editing evidence
- Camera-like acquisition evidence

Expected:

- All three assessments remain independently visible
- Overall synthesis is deterministic
- Secondary hypotheses are not silently discarded
- No evidence is misrepresented as proving a different mechanism

### Scenario D — No meaningful evidence

Expected:

- Inconclusive result
- Empty or appropriately qualified supporting evidence
- No invented contradictions
- No misleading confidence justification

---

## 5. Audit the confidence rationale

Inspect `build_confidence_rationale()` and related narrative functions.

The current confidence rationale may make broad statements such as:

- Multiple independent forensic domains show converging evidence.
- Contradicting signals reduce confidence.
- Strong camera evidence counterbalances suspicious indicators.

Determine whether these statements remain justified for the selected hypothesis.

### Required correction

Make confidence explanations hypothesis-aware.

Do not claim evidence is independent merely because different modules produced it.

Do not change numerical scoring, confidence thresholds or the scorecard calculation in this task.

The objective is to correct explanations, not recalibrate confidence.

---

## 6. Validation and compatibility

### Automated validation

Run all existing tests plus the new tests.

Also run:

- Python syntax checks
- Relevant module imports
- Controller import smoke test
- GUI import smoke test
- JSON serialization tests
- Reasoning-trace schema compatibility checks

Where feasible, test rendering through the existing summary and narrative builders.

### End-to-end validation

If the necessary original images and Windows runtime are available locally, perform full image analyses.

If they are not available or executing the GUI is outside the environment's capabilities, do not claim end-to-end validation.

Instead, provide exact manual test instructions for the developer.

The manual validation should include:

- Restarting SignalLens to load the changes.
- Running the original Midjourney image.
- Running the Instagram reference image.
- Using the same analysis mode for a controlled comparison.
- Reviewing both the GUI summary and generated reasoning-trace JSON.
- Confirming that generation declarations are recognized from image metadata rather than filenames.
- Checking that all supporting and contradicting evidence is hypothesis-relevant.

Do not open, inspect, alter or commit `test_images/` without explicit authorization.

---

## 7. Preserve scope and repository integrity

Work on the existing Phase 1 reasoning branch.

First inspect the Git status. The previous implementation may still contain uncommitted changes.

Do not overwrite or discard those changes.

If currently on `chore/repository-foundation`, report that fact and, if safe, create or switch to `fix/reasoning-correctness-phase1` while retaining the working tree.

Do not stage, commit, push, merge, tag or publish anything.

Do not change:

- Forensic detector algorithms
- Detection thresholds
- Hypothesis score weights
- Dependencies
- PyInstaller packaging
- GUI layout
- External resource files
- Windows build scripts

Keep the changes narrowly focused on evidence interpretation, narrative construction and test coverage.

---

## 8. Required deliverables

### A. Implementation summary

List every changed file and explain the correction.

### B. Before/after narrative comparison

For the Midjourney and Instagram reference cases, show:

- Overall conclusion
- Primary hypothesis
- Confidence tier
- Supporting Signals
- Contradicting Signals
- Relevant secondary hypotheses

Highlight evidence that was previously misclassified or displayed under the wrong hypothesis.

### C. Test report

Provide:

- Total tests passed
- Total failed
- Total skipped
- New tests added
- Existing tests affected
- Any testing limitations

### D. Compatibility report

Confirm whether:

- The five-element synthesis API remains unchanged.
- Existing JSON trace fields remain available.
- New hypothesis fields serialize correctly.
- Summary and GUI consumers remain compatible.

### E. Remaining issues

Record any defects discovered in:

- Correlated evidence weighting
- Scorecard consistency
- Confidence calibration
- Provenance verification
- Detector reliability

Do not implement these broader changes without separate authorization.

### F. Git status

Report the branch, modified files, untracked files and staging status.

---

## Success criteria

Phase 1.1 is complete when:

1. Every reported Supporting Signal is relevant to the hypothesis it supports.
2. Every reported Contradicting Signal genuinely challenges that hypothesis.
3. Contextual evidence is not mislabeled as direct contradiction.
4. Structured reasoning and human-readable explanations agree.
5. Embedded-generation metadata survives the complete extraction-to-reasoning pipeline.
6. Existing Midjourney and Instagram conclusions remain logically consistent.
7. Automated regression tests pass.
8. No forensic detection algorithms or thresholds have changed.

**The goal is not to produce more confident conclusions. The goal is to ensure SignalLens explains exactly what its evidence supports, what it does not support, and why.**

Do not commit or push. Leave the final implementation ready for review.
