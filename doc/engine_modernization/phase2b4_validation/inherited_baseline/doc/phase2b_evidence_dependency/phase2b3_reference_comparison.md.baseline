# Phase 2B.3 reference comparison

Both existing images ran the full headless pipeline in `subject_based` mode. They were read-only; SHA-256 image hashes matched before/after. Before traces are the preserved Phase 2B.2 results. No raw image, prompt, creator value or complete detector payload is exported here.

## Before / after overview

| Metric | Instagram before | Instagram after | Midjourney before | Midjourney after |
| --- | --- | --- | --- | --- |
| Suspicious score | 20.47705 | 20.47705 | 6.0375 | 6.0375 |
| Benign score | 2.25 | 2.25 | 1.5 | 1.5 |
| Final pattern | possible_foreground_background_processing_mismatch | possible_foreground_background_processing_mismatch | provenance_supported_synthetic_context | provenance_supported_synthetic_context |
| Confidence | High | High | Medium | Medium |
| Primary hypothesis | localized_editing | localized_editing | synthetic_origin | synthetic_origin |
| Completed stages | 23 | 23 | 14 | 14 |
| Unavailable / skipped | 0 | 0 | 9 | 9 |
| Failed stages | 0 | 0 | 0 | 0 |
| Default shadow S | 20.47705 | 20.47705 | 6.0375 | 6.0375 |
| Audit-A diagnostic S | 13.46455 | not activated; policy unchanged | 3.9125 | not activated; policy unchanged |

Production scorecards, the entire Phase 2A calculation ledger, section snapshots and hypothesis assessments match the baseline exactly. Phase 2B.2 dependency sidecars match after normal JSON tuple/list normalization; their policy and numbers are unchanged. The first validation equality check was tightened to compare serialized representations rather than in-memory tuples against JSON lists. This representation adjustment was not a production or shadow-policy change.

## Evaluated gate results

The table reports actual production subpredicate results. A passed compound subpredicate does not imply its entire route passed. Complete route pass/fail/selection remains in `decision_route_trace`. The source-diversity gate uses its existing score threshold as well as its source requirement.

### Instagram

| Gate / semantics | Passed | Eligible indicators | Disjoint witness count | Selected ancestry |
| --- | --- | --- | --- | --- |
| boundary.compound_support / compound_interpretations | True | evidence:boundary, evidence:boundary_focus, evidence:subject_boundary | 2 | evidence:boundary: measurement:ela_recompression_difference, measurement:luminance_residual; evidence:subject_boundary: measurement:intrinsic_edge_ring_features |
| confidence.strong_source_diversity / distinct_measurement_sources | False | evidence:boundary | 1 | evidence:boundary: measurement:ela_recompression_difference, measurement:luminance_residual |
| synthetic.additional_support_flag / general_accumulation | False | none | 0 | none |
| synthetic.fft_patch_compound / compound_interpretations | True | evidence:fft, evidence:patch_similarity | 2 | evidence:fft: measurement:global_spectral_features; evidence:patch_similarity: measurement:retained_patch_matches |
| synthetic.material_asymmetry_compound / compound_interpretations | False | none | 0 | none |

Shared ancestry / limitations:

- `boundary.compound_support`: 3 observed supporting indicator(s) satisfy the 2-indicator compound_interpretations condition; shared ancestry is allowed and is not independent confirmation.
  Shared `measurement:ela_recompression_difference`: evidence:boundary, evidence:boundary_focus.
  Shared `measurement:luminance_residual`: evidence:boundary, evidence:boundary_focus.
- `confidence.strong_source_diversity`: 1 measurement-disjoint supporting indicator(s) do not satisfy the existing 2-source diversity requirement.
- `synthetic.additional_support_flag`: 0 observed supporting indicator(s) do not satisfy the 1-indicator general_accumulation condition; shared ancestry is allowed and is not independent confirmation.
- `synthetic.fft_patch_compound`: 2 observed supporting indicator(s) satisfy the 2-indicator compound_interpretations condition; shared ancestry is allowed and is not independent confirmation.
- `synthetic.material_asymmetry_compound`: 0 observed supporting indicator(s) do not satisfy the 2-indicator compound_interpretations condition; shared ancestry is allowed and is not independent confirmation.

Hypothesis assessments (unchanged):

| Hypothesis | Tier | Polarity | Decision branch |
| --- | --- | --- | --- |
| synthetic_origin | Inconclusive | neutral | none |
| localized_editing | High | suspicious | possible_foreground_background_processing_mismatch |
| camera_acquisition | Medium | benign | camera_acquisition_compatibility |

Stage statuses: `{"success": 23}`; no stage errors. Mask status `reliable`, coverage 0.5961422390407987.

### Midjourney

| Gate / semantics | Passed | Eligible indicators | Disjoint witness count | Selected ancestry |
| --- | --- | --- | --- | --- |
| confidence.strong_source_diversity / distinct_measurement_sources | False | evidence:cross_signal | 1 | evidence:cross_signal: measurement:ela_recompression_difference, measurement:luminance_residual |
| synthetic.additional_support_flag / general_accumulation | True | evidence:metadata | 1 | evidence:metadata: measurement:embedded_assertions |
| synthetic.fft_patch_compound / compound_interpretations | True | evidence:fft, evidence:patch_similarity | 2 | evidence:fft: measurement:global_spectral_features; evidence:patch_similarity: measurement:retained_patch_matches |
| synthetic.material_asymmetry_compound / compound_interpretations | False | none | 0 | none |

Shared ancestry / limitations:

- `confidence.strong_source_diversity`: 1 measurement-disjoint supporting indicator(s) do not satisfy the existing 2-source diversity requirement.
- `synthetic.additional_support_flag`: 1 observed supporting indicator(s) satisfy the 1-indicator general_accumulation condition; shared ancestry is allowed and is not independent confirmation.
- `synthetic.fft_patch_compound`: 2 observed supporting indicator(s) satisfy the 2-indicator compound_interpretations condition; shared ancestry is allowed and is not independent confirmation.
- `synthetic.material_asymmetry_compound`: 0 observed supporting indicator(s) do not satisfy the 2-indicator compound_interpretations condition; shared ancestry is allowed and is not independent confirmation.

Hypothesis assessments (unchanged):

| Hypothesis | Tier | Polarity | Decision branch |
| --- | --- | --- | --- |
| synthetic_origin | Medium | suspicious | provenance_supported_synthetic_context |
| localized_editing | Inconclusive | neutral | none |
| camera_acquisition | Medium | benign | camera_acquisition_compatibility |

Stage statuses: `{"skipped": 8, "success": 14, "unavailable": 1}`; no stage errors. Mask status `unreliable`, coverage 0.9181777419747081.

## Why the reference decisions remain unchanged

Instagram: the generic diversity check has only one strong indicator (boundary), so it does not provide generic High confidence. The localized mechanism route still has strong compound boundary evidence. Boundary, focus and intrinsic subject-boundary summaries satisfy the unchanged compound count/strength condition. Boundary and focus share ELA/residual ancestry; intrinsic edge-ring features are a distinguishable additional extraction. The compound result does not assert statistical independence. This supports the same localized-editing route at its existing High tier.

Midjourney: cross is the only eligible strong generic indicator. The two-source High requirement fails, and the unverified declaration route remains Medium. FFT/patch compound structure and the declaration support flag can individually pass, but the full synthetic-visual route still lacks its required synthetic boost. The boundary compound predicate is not evaluated because no qualifying boundary-route condition reaches it; it is not fabricated as a pass or a failure.

Midjourney mask coverage remains 0.9181777419747081, rejected under the unchanged 0.90 maximum. Region selection is unavailable and eight regional consumers skip; global cross-signal continues. No unavailable regional measurement supplies a source witness. Instagram coverage remains 0.5961422390407987 with reliable segmentation and all 23 stages completed.

The only reference wording change is Midjourney selection scope: the declaration supports creation ?without requiring a conclusive localized-editing result.? The former ?independently of inconclusive localized editing? wording was ambiguous about logical scope versus independence. No reference hypothesis explanation, evidence role or tier changed.

## Controlled changed-decision regression

| Metric | Inherited production module | Corrected production module |
| --- | --- | --- |
| Pattern | moderate_suspicious_convergence | moderate_suspicious_convergence |
| Confidence | High | Medium |
| Suspicious score | 4.905 | 4.905 |
| Benign score | 0.0 | 0.0 |
| Strong detector indicators | 2 | 2 |
| Source diversity test | two flags treated as multiple support | one measurement-disjoint witness; requirement fails |

This synthetic fixture contains measured neutral ELA/residual parents, strong boundary, strong cross and reliable-but-reduced boundary support r=0.75. Raw local support is 3; adjusted local is 2.25; edit is 0.405; caution is 0.25; base S is 4.75; therefore S=4.75+0.405-0.25=4.905. No specific local mechanism route dominates, so `route_moderate_suspicious` inherits the generic tier.

The exact inherited `decision_logic.py` module was loaded read-only from the baseline snapshot and replayed against the same fixture. Its card and full numerical ledger equal the new card/ledger exactly. Only `confidence.strong_source_diversity` changes multiplicity interpretation: boundary and cross both derive from the same ELA/residual ancestry, giving one disjoint witness rather than two. The fallback changes High to Medium; no weight was adjusted to force it.

This demonstrates the intended logical correction. It does not establish an empirical improvement, recalibrate confidence or prove statistical independence of other sources.

## Artifacts and reproducibility

Ignored local outputs: `analyzed/phase2b3_validation/{instagram,midjourney}/summary/reasoning_trace.json`, `.txt`, final summaries, `validation_result.json`, `console.txt`, and `regression_case_comparison.json`. Reports retain only identifiers/aggregates and gate ancestry. The 69-file inherited snapshot and isolated Phase 2B.3 patch allow review separately from earlier uncommitted work.
