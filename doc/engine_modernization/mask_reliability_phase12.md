# Phase 1.2: mask reliability and failure-tolerant analysis

## Root cause

The reported failure was reproduced by executing the real controller pipeline
on both named reference images, read-only, before changing the implementation.
The existing Phase 1/1.1 baseline was 89 passing tests.

For the Midjourney reference, the actual backend was
`mediapipe_tasks_image_segmenter`, MediaPipe 1.2.0, with the bundled
`selfie_segmenter.tflite`. No backend exception occurred. The prepared image
and mask were 1024 by 771 pixels. The measured quality values were:

| Metric | Value |
| --- | --- |
| Foreground area ratio | 0.9181777419747081 |
| Largest-component fraction of foreground | 0.9987391451293618 |
| Connected foreground components | 3 |
| Mean foreground confidence proxy | 0.9260292053222656 |
| Existing quality classification | Low |

The quality gate accepts at most 90% foreground for a Medium mask; this mask
occupied 91.82%. The classification therefore followed the existing policy.
The confidence proxy is an average over the confidence map, not a calibrated
probability that a usable person contour was detected. It does not override
the coverage gate. High quality additionally requires 8%-85% foreground, at
least 70% largest-component concentration and at most three components;
Medium requires 3%-90% foreground and at least 50% concentration.

Visual inspection of the generated overlay showed near-full-frame coverage,
including foreground flowers. Very little comparative background remained.
This is a conservative geometry/coverage rejection, not a model execution
failure. It does not prove the segmentation is accurate or inaccurate against
ground truth, nor establish that the calibration is optimal for tight portraits.
No quality cutoff was relaxed.

There were three independent pipeline defects:

1. Expected quality rejection raised `ValueError`, recording a failed stage.
2. `RUN_LEGACY_REGION_MASKS` was False. Even if enabled, the old legacy stage was
   scheduled after the person-derived selection tried to use it. Its payload
   also lacked the flat ratios, dimensions and reliability metadata expected
   by newer consumers. Edge saliency is not person segmentation.
3. Cross-signal analysis declared ELA/residual dependencies but obtained image
   dimensions from `region_masks_payload`. Rejection made that payload None,
   causing the reproduced NoneType crash. The cross-signal algorithm itself
   does not require a person mask.

The audit additionally found undeclared gatekeeper dependencies in global FFT
and patch analysis, coordinate-grid inconsistency between original ELA/residual
hotspots and resized person masks, and a person-specific interpretation applied
to an independent image-edge detector without validated subject geometry.

## Corrections and file inventory

| File changed in Phase 1.2 | Change |
| --- | --- |
| `mask_contract.py` (new) | Explicit availability states, controlled unavailability, canonical mask metadata, schema/file/geometry validation and person-geometry guard |
| `vf_person_subject_mask.py` | Additive quality reasons and backend/version diagnostics; retain backend exceptions; distinguish approximate/absent outputs; canonical region output; ensure output directory exists |
| `vf_region_masks.py` | Preserve legacy measurements; return canonical approximate-region metadata; handle empty saliency regions as controlled unavailability |
| `signallens_controller.py` | Controlled rejection, deterministic selection/fallback, reliability guards, declared dependencies, independent cross-signal geometry, stage ledger and coverage |
| `vf_segmentation_alignment.py` | Align binary hotspots from their actual image grid to the resized boundary grid before existing overlap calculation |
| `run_reporting.py` | Persist stage skip/unavailability reasons and compact diagnostics; distinguish complete, partial and error-bearing completion |
| `summary_sections.py` | Label approximate masks as diagnostic-only; preserve reliable/limited person-mask compatibility fields |
| `summary_synthesizer.py` | Present missing outputs as unavailable/neutral; qualify image-edge measurements without person geometry; persist coverage in trace and prose |
| `hypothesis_evidence.py` | Explicit contextual relationship for unvalidated image-edge boundary observations |
| `hypothesis_engine.py` | Availability guard: a missing/not-run material measurement cannot activate the existing low-realism counterevidence signal |
| `reasoning_persistence.py` | Concise coverage, mask-rejection and disabled-stage information in text traces |
| `tests/test_mask_pipeline.py` (new) | 32 additional parameterized regression cases using synthetic data |
| This report (new) | Diagnosis, policy, real-pipeline comparison, tests and compatibility |

Existing uncommitted Phase 1/1.1 work was retained. Other dirty files shown by
Git include inherited changes; they were not discarded or broadly rewritten.

### Availability and canonical contract

`MaskStatus` distinguishes `reliable`, `limited`, `unreliable`, `unavailable`,
`error` and `approximate`. `StageUnavailable` represents expected missing or
unusable evidence. Genuine unexpected execution exceptions remain errors.

Available region payloads retain `region_masks`, mask paths, `source`, `shape`,
flat ratios and the older nested `ratios`. They now consistently include height,
width, `mask_source`, `mask_reliability`, `mask_status`, `fallback_used`,
`fallback_reason` and `person_specific`. The existing
`person_mask_reliability` compatibility field remains.

Validation checks required keys, positive dimensions, known status/reliability,
boolean flags, source eligibility, finite ratios, readable binary files,
matching dimensions, actual coverage against stored ratios, and nonempty
foreground/background/boundary. Availability is separate from an artifact's
existence. Invalid/inconsistent outputs are recorded as validation errors,
invalidated once, and cannot cause repeated NoneType failures downstream.

Masks remain files referenced by paths. No image-sized arrays enter reasoning
JSON. `hotspot_mask` remains an in-memory cross-signal implementation detail.

The legacy background excludes its boundary band, whereas existing person-derived
background is the complement of the foreground and can overlap the band. The
contract records `background_excludes_boundary` rather than silently changing
reliable-mask pixels or pretending the two producers have identical partition
semantics. Approximate legacy geometry is not admitted to person-specific
forensic stages.

### Selection and fallback policy

1. High MediaPipe person masks retain their existing usable status. Medium masks
   remain usable with explicit limitations. Their detector pixels, morphology
   and quality thresholds are unchanged.
2. The existing HOG fallback is attempted when MediaPipe provides no mask or
   raises. A HOG bounding box is explicitly approximate, even if its geometric
   coverage alone satisfies the old quality test. It is not a validated person
   contour and cannot enable person-specific forensic conclusions.
3. The center-box diagnostic remains explicitly unavailable as person geometry.
   It is never silently substituted into forensic analysis.
4. Legacy saliency fallback stays disabled by default. If explicitly enabled
   through the existing flag or the optional controller setting
   `use_legacy_region_masks=True`, it runs on demand before selection needs it.
   A successful result is labeled approximate, records the original rejection
   reason, and is available only for diagnostic display under the current policy.
5. If no meaningful candidate is available, region selection returns controlled
   unavailability. Backend execution errors remain recorded even when a fallback
   produces an artifact.

No legacy implementation was removed. No dependency or settings-file change was
made to force fallback activation.

### Downstream policy

| Stage family | Actual requirement and execution policy |
| --- | --- |
| Metadata, ELA, residual, sensor, CFA, global compression | Independent of segmentation; continue |
| Global FFT and patch similarity | Require their prepared image, not segmentation; missing gatekeeper output now causes a declared skip |
| Cross-signal and shared contour overlays | Require ELA/residual outputs and compatible grids; no person dependency |
| Independent subject-boundary detector | Image-edge measurements still execute; person-specific interpretation requires validated person geometry |
| Region segmentation analysis | Requires meaningful person geometry; approximate-mask fragmentation or rectangular cleanliness is not forensic evidence |
| Boundary focus and segmentation alignment | Require a meaningful person contour; cannot use box/saliency boundaries as person contours |
| Region FFT and patch spatial analysis | Mathematically capable of arbitrary region comparisons, but current outputs carry subject/person semantics; conservatively require usable person geometry |
| Subject texture, process asymmetry and material realism | Require usable person-specific masks; High and Medium follow the existing policy |

Thus all eight regional forensic stages run on accepted High/Medium masks and
remain unavailable for approximate/rejected masks. Approximate regions can be
inspected diagnostically without generating invented person-specific findings.

Two narrowly scoped evidence-validity corrections were necessary:

- The independent subject-boundary detector builds its own intrinsic image-edge
  bands. Without a validated person mask, its measured score and raw detector
  pattern are retained, but the summary becomes a neutral
  `image_edge_boundary_observation`. It is contextual, not evidence identifying
  a person/background segmentation artifact. Reliable person cases preserve
  their existing interpretation. The raw payload is not mutated.
- Absent material analysis previously defaulted to score zero and activated
  `material_realism_low`. It now requires an executed, usable measurement. The
  0.20 threshold and all scorecard coefficients/calculations remain unchanged.

These are availability/interpretation guards, not confidence tuning or changes
to route priorities.

### Cross-signal geometry correction

Hotspot coordinates belong to the ELA/residual images, which use original image
dimensions. They must not be cropped to the resized person-mask dimensions.
The controller obtains geometry from ELA/residual metadata or their map images,
with original-image geometry as a mask-independent fallback. Incompatible
signal geometries or block sizes cause explicit unavailability.

Segmentation alignment uses nearest-neighbor mapping of that binary hotspot
grid to the boundary-mask grid. The overlap formula and classification
thresholds are unchanged. For the Instagram reference, this corrects alignment
score from the old cropped-grid 0.1267569820 to 0.2013549572. Both remain below
the existing moderate-support threshold, and the overall result is unchanged.

## Actual pipeline before/after

These are **full, headless controller/image-pipeline executions**, not mocked
tests or trace-only replays. Both original reference files were available and
read read-only. Both stored runs used `subject_based`; the controlled reruns used
that same mode for both images. No interactive GUI validation is claimed.

All runs used MediaPipe Tasks 1.2.0 and `selfie_segmenter.tflite`. No fallback was
used for either reference.

| Reference | Phase | Mask reliability | Cross-signal | Completed | Skipped/unavailable | Failed | Overall reasoning |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| Instagram: Curvy Leggings Outfit | Before | High | Success | 23 | 0 | 0 | High/suspicious, localized foreground/background processing mismatch |
| Instagram: Curvy Leggings Outfit | After | High (`reliable`) | Success | 23 | 0 | 0 | Same pattern, tier and primary localized-editing hypothesis |
| Midjourney: theart1300 portrait | Before | Low | Failed: NoneType | 12 | 9 | 2 | Medium/suspicious, person/background segmentation-artifact interpretation |
| Midjourney: theart1300 portrait | After | Low (`unreliable`) | Success | 14 | 9 | 0 | Medium/suspicious, unverified generation declaration; primary synthetic origin |

After correction, the Midjourney count of nine unavailable/skipped stages is one
controlled region-selection rejection plus eight regional forensic skips.
Cross-signal and shared contour overlays now complete. Metadata, global FFT,
patch similarity, sensor, CFA, compression, ELA/residual and independent edge
measurements remain available. Localized editing is Inconclusive/neutral;
camera compatibility remains Medium/benign. Missing regional evidence is
explicitly reported as incomplete coverage.

The Midjourney primary-hypothesis change comes from no longer interpreting
unvalidated image edges as a person-specific artifact. The embedded prompt and
IPTC generation declaration remain available and explicitly unverified.
Confidence was not inflated to High to compensate for missing regional sensors.

The Instagram subject, boundary and background masks were compared against the
pre-change run and are **pixel-identical**. Its High localized-editing finding
remains intact. The changed alignment score is the justified coordinate fix
described above, not a threshold adjustment.

Do not interpret the shorter rejected-mask run as a speed optimization. Eight
regional forensic measurements are unavailable.

### Generated validation artifacts

All artifacts are under the existing ignored output tree:

- `analyzed/phase12_validation/baseline/instagram/validation_result.json`
- `analyzed/phase12_validation/baseline/midjourney/validation_result.json`
- `analyzed/phase12_validation/final/instagram/validation_result.json`
- `analyzed/phase12_validation/final/midjourney/validation_result.json`

Final folders also contain the ordinary `analysis_run.json`, `logs/run.log`,
summary JSON/HTML/text, JSON/text reasoning traces, masks/overlays and model QA
diagnostics. Existing reference audit folders were not overwritten. No private
images were added to test fixtures or staged; `test_images/` remains ignored.

## Tests and validation

Final result: **121 passed, 0 failed, 0 skipped**. All original 89 Phase 1/1.1
cases pass unchanged. There are 32 new cases in `test_mask_pipeline.py`.
There were no pre-existing failing tests.

New coverage includes High/Medium/Low quality, missing person output, backend
exceptions, missing ELA/residual, cross-signal with no regions, legacy fallback
availability/unavailability, HOG and center approximations, invalid contract
fields/files, explicit alignment skips, neutral unavailable sections, coverage
persistence, reliable-mask pixel preservation, original quality-gate behavior,
original/resized coordinate mapping, missing gatekeeper inputs, image-edge
interpretation eligibility, correctly attributed skip reasons, incompatible
signal geometries and missing-material counterevidence.

Tests use synthetic images, masks and mocked detector payloads. They do not
depend on private image fixtures. Real-image runs are separately identified
above. The first filesystem-fixture run encountered Windows sandbox access
denial in pytest's temporary directory; the authorized rerun completed. A newly
exposed output-directory creation failure in direct mask derivation was fixed.

Validation command:

```powershell
py -3.13 -m pytest -p no:cacheprovider --ignore=test_images --ignore=legacy --ignore=exiftool_files -q --tb=short
```

Python syntax checks and relevant module imports passed, including worker,
controller and GUI import smoke checks. JSON serialization, old trace fields,
existing summary/HTML/text rendering, failure-status persistence and missing
regional evidence are covered. `git diff --check` passes.

Static comparison against the original source confirms that MediaPipe mask
refinement, mask cleanup, component metrics, HOG detector parameters, the
existing quality-classification conditions, and the cross-signal detector
algorithm are unchanged. No evidence score weights, confidence thresholds,
decision-route priorities, dependencies, extraction rules, GUI layout or build
scripts were modified in this phase.

## Compatibility and remaining limitations

The controller and worker entry points remain compatible. The synthesis API
still returns five elements. Existing payload/trace fields remain available;
mask metadata, stage reasons, coverage and diagnostics are additive. Stage
records now include skips rather than silently omitting them. Run status can
be `completed_partial` or `completed_with_errors`, as well as `completed`.
The current GUI consumes the completed state and summary, rather than requiring
the manifest status to equal `completed`; no GUI-layout change is needed.

Reliable person-mask behavior is preserved, with the explicit alignment-grid
correction. Approximate HOG/legacy/center outputs now carry their actual limits.
No arrays are serialized into reasoning traces. The final summary and text
trace prominently identify incomplete coverage and the unavailable stages.

Outstanding work outside scope:

- Mask reliability calibration for tight crops and synthetic people still needs
  annotated validation; this work does not establish model accuracy.
- The selfie segmentation model is not an instance-aware full-body ground-truth
  detector. Model-version metadata is unavailable; the model filename and backend
  version are recorded without inventing a version.
- Edge-saliency masks and bounding boxes are not validated person contours.
  Enabling their mathematical region comparisons as forensic evidence would
  require separate, explicitly scoped interpretations.
- Correlated evidence weighting, scorecard recalculation timing and broader
  confidence calibration remain the previously documented separate concerns.
- Cryptographic provenance verification remains unimplemented; generation
  declarations stay unverified.
- The local joblib runtime prints a physical-core discovery warning because
  Windows `wmic` is unavailable, then uses logical cores. This did not fail a
  forensic stage and was not addressed by changing dependencies or settings.

For interactive confirmation, restart with `py -3.13 signallens_gui.py`, use
`subject_based` mode for both named references, and compare the GUI summary
against `summary/reasoning_trace.json` and `analysis_run.json`. Expect the table
above, explicit partial coverage for Midjourney, and no NoneType crash.

## Git status

Branch: `fix/reasoning-correctness-phase1`. The inherited working tree remains.
Nothing was staged, committed, pushed, tagged or published.

Modified tracked files: `decision_logic.py`, `exiftool_backend.py`,
`hypothesis_engine.py`, `reasoning_persistence.py`, `run_reporting.py`,
`signallens_controller.py`, `summary_sections.py`, `summary_synthesizer.py`,
`vf_person_subject_mask.py`, `vf_region_masks.py`, `vf_segmentation_alignment.py`.
Some entries are inherited Phase 1/1.1 changes, as distinguished in the inventory.

Untracked files: the three supplied task Markdown files; the Phase 1, 1.1 and
1.2 reports under `doc/`; `metadata_evidence.py`, `hypothesis_evidence.py`,
`mask_contract.py`; and the three regression modules under `tests/`.

Generated analysis artifacts and private reference images remain excluded from
Git. The index is empty, ready for review without publication.
