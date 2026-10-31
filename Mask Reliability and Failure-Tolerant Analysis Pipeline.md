# CODEX TASK — SignalLens Phase 1.2: Mask Reliability and Failure-Tolerant Analysis Pipeline

## Mission

You are the principal Python engineer and computer-vision architect for SignalLens.

Phases 1 and 1.1 corrected the forensic reasoning engine, introduced hypothesis-specific evidence assessments, and improved metadata extraction.

During real-image testing, a new problem surfaced: **an unreliable person segmentation mask caused most region-dependent analysis stages to be skipped, while cross-signal analysis crashed because it accessed an unavailable region-mask payload.**

Your task is to investigate and correct this failure without compromising forensic reliability.

**Primary objective:** SignalLens must degrade gracefully when person segmentation fails, preserving every independent forensic analysis and clearly identifying unavailable or lower-reliability evidence.

This is a pipeline correctness and reliability task, not a detector recalibration or reasoning-engine redesign.

---

## 1. Reproduction case

The following failure occurred using Python 3.13 and the current updated MediaPipe installation:

```text
[SignalLens] Analysis started for:
D:\Coding\SignalLens\test_images\midjourney\
theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png

[SignalLens] Stage failed: Person-derived region masks after 0.00s
(Person subject mask is not reliable enough and no legacy fallback exists: low)

[SignalLens] Stage skipped: Region segmentation analysis
(missing dependency: region_masks_payload)

[SignalLens] Stage failed: Cross-signal analysis after 0.00s
('NoneType' object is not subscriptable)

[SignalLens] Stage skipped: Boundary-focused analysis
(missing dependency: region_masks_payload)

[SignalLens] Stage skipped: Region-aware FFT analysis
(missing dependency: region_masks_payload)

[SignalLens] Stage skipped: Segmentation alignment analysis
(missing dependency: cross_signal_payload)

[SignalLens] Stage skipped: Subject texture consistency analysis
(missing dependency: region_masks_payload)

[SignalLens] Stage skipped: Subject process asymmetry analysis
(missing dependency: region_masks_payload)

[SignalLens] Stage skipped: Subject material realism analysis
(missing dependency: region_masks_payload)

[SignalLens] Stage skipped: Patch spatial analysis
(missing dependency: region_masks_payload)

[SignalLens] Stage skipped: Shared boundary overlays
(missing dependency: cross_signal_payload)

[SignalLens] Full analysis completed in 3.13s
```

The Instagram reference image completed normally in 8.46 seconds.

Do not interpret the shorter Midjourney processing time as an optimization. Most regional analysis stages were skipped.

### Important test-data constraint

The `test_images/` directory must remain excluded from Git.

Do not modify, rename, delete, stage, commit or copy reference images into the repository.

You may inspect and analyze existing local test images read-only for diagnosis and validation, provided they are available.

---

## 2. Inspect the actual masking pipeline

Before implementing changes, inspect:

- `signallens_controller.py`
- `analysis_worker.py`
- `image_gatekeeper.py`
- The person-segmentation module and MediaPipe integration
- Region-mask generation and legacy fallback implementation
- Cross-signal analysis and dependency registration
- Downstream modules consuming region masks
- Relevant settings and configuration files
- Reasoning-trace and analysis-status persistence

Trace the complete execution path from person segmentation through region-mask generation and downstream stage scheduling.

Determine:

1. Which segmentation backend produced the Low reliability result.
2. Why the mask was classified Low.
3. Whether it was a genuine segmentation failure or an overly restrictive quality assessment.
4. Whether a legacy fallback exists and why it was unavailable.
5. Which downstream algorithms genuinely require person-derived masks.
6. Which algorithms could execute without segmentation.
7. Whether other stages can encounter the same missing-payload defect.

**Do not assume the previously identified cause is exhaustive. Verify it against the current code.**

Produce a concise diagnosis before changing the implementation.

---

## 3. Correction A — Graceful handling of unreliable masks

### Current problem

A Low-reliability person mask raises an exception that causes the region-mask stage to fail.

That failure removes the `region_masks_payload` dependency for multiple downstream analyses.

### Required behavior

Introduce explicit mask availability and reliability handling.

At minimum, distinguish:

- Reliable person mask
- Usable but limited person mask
- Unreliable person mask
- Segmentation unavailable
- Segmentation execution error

A rejected or unavailable mask must not be silently presented as a valid mask.

Represent expected quality rejection as a controlled pipeline outcome rather than an unhandled stage exception.

A genuine unexpected execution exception must still be recorded as an error.

### Acceptance criteria

- Low-quality segmentation no longer causes an uncontrolled pipeline failure.
- The analysis continues with unaffected forensic modules.
- The reason for rejection is retained.
- No fake or fabricated subject mask is silently substituted.
- Final reporting accurately reflects incomplete regional evidence.

---

## 4. Correction B — Investigate and repair fallback behavior

Inspect the existing legacy region-mask implementation and its execution ordering.

Determine whether the legacy fallback is appropriate for the current person-based forensic analyses.

If an existing fallback can safely produce useful approximate regions, implement an explicit controlled fallback policy.

### Requirements

- Fallback activation must be deterministic and documented.
- The original failure reason must remain available.
- The fallback source must be clearly identified.
- Legacy region masks must not be misrepresented as reliable MediaPipe person segmentation.
- Downstream algorithms must know whether the mask represents a detected person or merely approximate regions.
- Do not automatically enable fallback-based person-specific conclusions unless their interpretation is valid for the fallback method.

Where a legacy fallback cannot provide meaningful subject geometry, allow the corresponding person-specific analyses to remain unavailable.

**Do not lower the person-mask reliability threshold merely to force more analyses to run.**

### Acceptance criteria

- An unreliable person mask produces either an explicitly labeled safe fallback or a controlled unavailable result.
- The fallback cannot silently receive the same evidentiary authority as a reliable person mask.
- Mask selection and fallback reasoning are traceable.

---

## 5. Correction C — Make cross-signal analysis independent of segmentation

### Current problem

Cross-signal analysis accesses `region_masks_payload` despite not declaring it as a required dependency.

When the mask stage fails, cross-signal analysis raises:

```python
TypeError: 'NoneType' object is not subscriptable
```

### Required implementation

Inspect the actual cross-signal algorithm and identify the minimum inputs it requires.

Where possible, obtain image geometry directly from the prepared analysis image, ELA payload or residual payload.

Do not require person segmentation merely to determine image dimensions.

If some cross-signal features genuinely require region masks, separate the global analysis from those optional region-specific enhancements.

### Acceptance criteria

- Cross-signal analysis runs without a person mask when its independent inputs are available.
- Missing optional region data does not produce a `NoneType` exception.
- Region-specific enhancements are skipped or qualified independently.
- Required dependencies accurately reflect actual code requirements.
- Segmentation-alignment analysis remains unavailable when no meaningful subject boundary exists.

---

## 6. Correction D — Normalize region-mask payload contracts

Inspect the payload structures created by:

- MediaPipe person segmentation
- Any alternative person detector
- Legacy region segmentation
- Fallback paths

Identify differences in:

- Mask arrays
- Region names
- Image dimensions
- Area ratios
- Boundary representations
- Source identifiers
- Reliability metadata

Introduce a consistent contract for downstream consumers.

Prefer a small typed data structure or a validated canonical dictionary schema compatible with current code.

Do not rewrite every downstream module unnecessarily.

### Required metadata

Where appropriate, record:

```python
{
    "mask_source": "...",
    "mask_reliability": "...",
    "mask_status": "...",
    "fallback_used": False,
    "fallback_reason": None,
    "person_specific": True
}
```

Use exact names and enum values that fit the existing architecture.

Do not serialize large image arrays into reasoning-trace JSON.

Preserve existing output keys where required for backward compatibility.

### Acceptance criteria

- Every supported mask producer satisfies the canonical contract.
- Invalid or incomplete payloads are detected before use.
- Downstream consumers do not have to guess the backend.
- Existing reliable-mask processing remains compatible.

---

## 7. Correction E — Reliability-aware downstream execution

Audit every stage consuming `region_masks_payload`.

At minimum, examine:

- Region segmentation analysis
- Boundary-focused analysis
- Region-aware FFT
- Segmentation alignment
- Subject texture consistency
- Subject process asymmetry
- Subject material realism
- Patch spatial analysis
- Shared boundary overlays

For each stage, determine its actual requirements.

Classify stages as:

1. Independent of segmentation
2. Compatible with approximate regions
3. Requires meaningful subject/background geometry
4. Requires a reliable person-specific mask

Implement appropriate execution guards.

An approximate mask must not silently produce strong person-specific forensic conclusions.

Where a stage cannot execute reliably, preserve an explicit `not_run`, `unavailable` or equivalent status rather than treating missing evidence as benign evidence.

### Important

Do not invent substitute forensic measurements.

Do not modify detector thresholds, weighting coefficients or decision-routing logic simply to compensate for missing masks.

If reliability gating reveals a genuine dependency issue in the reasoning engine, document it and implement only the minimum necessary correction.

---

## 8. Correction F — Improve diagnostics and traceability

The current console message:

```text
Person subject mask is not reliable enough ... low
```

is insufficient to diagnose the underlying problem.

Add structured diagnostics for segmentation outcomes.

Where available, include:

- Segmentation backend
- Backend or model version
- Detection confidence
- Foreground area ratio
- Mask coverage
- Mask quality metrics
- Reliability classification
- Rejection reason
- Fallback selection
- Mask dimensions
- Downstream stages disabled because of mask quality

Persist a concise diagnostic summary in the reasoning trace or existing analysis-status output.

Do not include enormous raw arrays or duplicate the entire model output.

Ensure diagnostic artifacts are written to existing generated-output locations, not tracked source directories.

---

## 9. Automated regression tests

Add targeted tests for these scenarios.

| Test | Expected behavior |
|---|---|
| High-reliability person mask | Existing regional analysis runs |
| Medium-reliability person mask | Runs according to documented policy |
| Low-reliability person mask | Controlled fallback or explicit unavailable result |
| Missing person detection | No uncontrolled exception |
| Segmentation backend exception | Error recorded; independent stages continue |
| Missing `region_masks_payload` | Cross-signal analysis still works |
| Missing ELA input | Cross-signal follows its declared dependency policy |
| Missing residual input | Cross-signal follows its declared dependency policy |
| Legacy fallback available | Correct schema and reliability labeling |
| Legacy fallback unavailable | Controlled regional-stage skips |
| Approximate fallback mask | No unjustified person-specific conclusions |
| Invalid region-mask payload | Validation failure handled predictably |
| Cross-signal without segmentation | Valid independent output produced |
| Segmentation alignment without boundary | Explicit unavailable result |
| Reasoning trace with missing regions | Missing evidence not treated as benign |
| Reliable-mask reference case | No unexpected output changes |

Use synthetic masks, mocked payloads and synthetic images for automated tests.

Do not depend on private image fixtures.

Preserve all existing Phase 1 and Phase 1.1 tests.

---

## 10. Real-image validation

After implementing and passing the automated tests, validate the actual application if the local runtime and reference images are accessible.

### Case A — Instagram reference

```text
test_images/insta_fake/Curvy Leggings Outfit.jpg
```

Expected:

- Existing reliable segmentation continues to work.
- Regional forensic analyses complete.
- Cross-signal analysis completes.
- Existing localized-editing evidence is preserved.
- No unexpected classification change.

### Case B — Midjourney reference

```text
test_images/midjourney/
theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png
```

Expected:

- Low mask reliability is explained.
- No `NoneType` cross-signal crash.
- Independent forensic analyses complete.
- Regional analyses run only when valid input is available.
- Missing regional evidence is accurately reported.
- Synthetic-generation metadata remains available to the reasoning engine.
- The analysis does not claim full forensic coverage when segmentation was unavailable.

Run the two cases using their existing modes to check behavioral regression. If practical, additionally run both in the same analysis mode for controlled comparison.

If full-image validation cannot be performed, provide explicit manual validation instructions. Never claim validation that was not actually executed.

---

## 11. Scope restrictions

Do not modify:

- Evidence-score weighting
- Decision-route priorities
- Confidence calibration
- Existing forensic detection thresholds
- ExifTool extraction rules unrelated to this issue
- Dependency versions
- GUI layout
- PyInstaller packaging
- GitHub workflows

Do not perform broad codebase cleanup or refactoring.

Do not remove the legacy masking implementation without proving it is obsolete and obtaining approval.

Preserve all Phase 1 and 1.1 corrections.

Do not stage, commit, push, tag or publish changes.

Work on the existing `fix/reasoning-correctness-phase1` branch, preserving all current uncommitted changes.

---

## 12. Required deliverables

### A. Root-cause report

Identify the precise reason for the Midjourney mask rejection, including the actual backend and quality criteria.

Distinguish between:

- Segmentation model failure
- Quality-threshold rejection
- Mask geometry problems
- Fallback configuration problems
- Stage dependency problems

### B. Implementation report

For each correction, describe the changes and files modified.

### C. Pipeline before/after comparison

Produce a table showing for both reference images:

- Segmentation backend
- Mask reliability
- Fallback used
- Cross-signal status
- Number of completed stages
- Number of skipped stages
- Number of failed stages
- Overall reasoning result

Clearly distinguish full image-pipeline results from mocked tests.

### D. Test report

Provide exact passed, failed and skipped counts.

List newly added tests and any pre-existing failures.

### E. Compatibility review

Confirm that:

- Reliable person-mask behavior remains unchanged unless explicitly justified.
- Existing JSON fields and GUI consumers remain compatible.
- Phase 1 and Phase 1.1 reasoning behavior is preserved.
- No detector thresholds or score weights were modified.

### F. Outstanding issues

List any issues discovered but not addressed, particularly:

- MediaPipe reliability calibration
- Segmentation accuracy on synthetic people
- Fallback-mask validity
- Correlated forensic evidence
- Scorecard mathematical consistency

### G. Git status

Report the current branch, modified files, untracked files and staging status.

Leave the working tree ready for review.

---

## Success criteria

Phase 1.2 is complete when:

1. Unreliable segmentation no longer causes an uncontrolled pipeline cascade.
2. Cross-signal analysis works without person segmentation when its independent inputs are available.
3. Safe fallbacks are used only when their limitations are explicit.
4. Person-specific detectors never mistake approximate region masks for reliable subject masks.
5. Missing evidence is clearly identified rather than treated as benign or suspicious.
6. Reliable-mask analyses retain their existing behavior.
7. Automated regression tests pass.
8. Real-image validation is completed where feasible, with honest reporting of any remaining coverage gaps.

**Core principle: A failed forensic sensor must reduce evidence coverage, not corrupt the reasoning process or produce unjustified confidence.**

Implement the corrections, execute the tests and report the results. Do not commit or push.
