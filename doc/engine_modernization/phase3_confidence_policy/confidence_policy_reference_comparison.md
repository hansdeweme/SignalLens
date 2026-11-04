# Phase 3 full reference confidence-policy comparison

Both existing references ran full headless `subject_based` analyses. Image SHA-256 hashes matched before/after; no file under test_images was modified. Saved pipeline summaries were also replayed through the final policy after the last central reliability-cap change; policy, hypothesis, arithmetic, shadow and corroboration records match the full-run output.

This report contains only aggregate values, evidence identifiers, named policy rules and limitations. It exports no raw image, prompt, creator value or detector array. Full outputs remain ignored under `analyzed/phase3_validation/{instagram,midjourney}/`.

## Primary outcomes

| Metric | Instagram before | Instagram policy | Midjourney before | Midjourney policy |
| --- | --- | --- | --- | --- |
| Primary hypothesis | localized_editing | localized_editing | synthetic_origin | synthetic_origin |
| Dominant pattern | possible_foreground_background_processing_mismatch | possible_foreground_background_processing_mismatch | provenance_supported_synthetic_context | provenance_supported_synthetic_context |
| Confidence | High | High | Medium | Medium |
| Suspicious score | 20.47705 | 20.47705 | 6.0375 | 6.0375 |
| Benign score | 2.25 | 2.25 | 1.5 | 1.5 |
| Policy rule | route provisional tier | localized.reliable_boundary_compound | route provisional tier | synthetic.unverified_generation_declaration |
| Completed stages | 23 | 23 | 14 | 14 |
| Unavailable / skipped | 0 | 0 | 9 | 9 |
| Failed stages | 0 | 0 | 0 | 0 |

No reference tier was forced. Policy rules were defined from the existing structured evidence constraints before reference validation. These two cases do not calibrate confidence or establish accuracy.

## Instagram

| Hypothesis | Previous tier | Policy tier | Policy rule |
| --- | --- | --- | --- |
| synthetic_origin | Inconclusive | Inconclusive | synthetic.not_established |
| localized_editing | High | High | localized.reliable_boundary_compound |
| camera_acquisition | Medium | Medium | camera.acquisition_compatibility |

### synthetic_origin

- Supporting evidence: none.
- Contradictory evidence: none.
- Moderating evidence: `cfa_demosaic:weak_camera_cfa_supported`, `sensor_origin:camera_like_acquisition_supported`.
- Policy rationale: Confidence policy synthetic.not_established: No specific generation interpretation is established; localized anomalies do not supply missing generation support. Moderating observations qualify this interpretation; they do not automatically refute it or support a different hypothesis. Confidence tiers are heuristic support levels, not calibrated probabilities; related module outputs are not assumed statistically independent.

Reliability and coverage limitations:

- Heuristic support levels are not probabilities.
- Missing provenance coverage is a limitation, not positive generation evidence.
- No substantive generation declaration or specific visual generation finding is established.

### localized_editing

- Supporting evidence: `boundary:possible_foreground_background_processing_mismatch`, `boundary_focus:boundary_focused_processing_mismatch`, `compression_history:localized_compression_inconsistency`, `cross_signal:partial_hotspot_convergence`, `subject_boundary:possible_subject_background_segmentation_artifact`.
- Contradictory evidence: none.
- Moderating evidence: `cfa_demosaic:weak_camera_cfa_supported`, `sensor_origin:camera_like_acquisition_supported`.
- Policy rationale: Confidence policy localized.reliable_boundary_compound: Strong local-processing support and the existing compound boundary requirement are satisfied. Moderating observations qualify this interpretation; they do not automatically refute it or support a different hypothesis. Confidence tiers are heuristic support levels, not calibrated probabilities; related module outputs are not assumed statistically independent.

Reliability and coverage limitations:

- Localized editing evidence does not by itself establish AI generation.

### camera_acquisition

- Supporting evidence: `cfa_demosaic:weak_camera_cfa_supported`, `sensor_origin:camera_like_acquisition_supported`.
- Contradictory evidence: none.
- Moderating evidence: none.
- Policy rationale: Confidence policy camera.acquisition_compatibility: Camera-like structure or coherent photo-like processing supports compatibility, not photographic authenticity. Confidence tiers are heuristic support levels, not calibrated probabilities; related module outputs are not assumed statistically independent.

Reliability and coverage limitations:

- Camera compatibility does not authenticate an image and may coexist with synthetic creation or later editing.

Mask status `reliable`, coverage 0.5961422390407987. The maximum usable coverage remains 0.90. Stage statuses: `{"success": 23}`; no errors.

## Midjourney

| Hypothesis | Previous tier | Policy tier | Policy rule |
| --- | --- | --- | --- |
| synthetic_origin | Medium | Medium | synthetic.unverified_generation_declaration |
| localized_editing | Inconclusive | Inconclusive | localized.not_established |
| camera_acquisition | Medium | Medium | camera.acquisition_compatibility |

### synthetic_origin

- Supporting evidence: `metadata:DECLARED_SYNTHETIC`, `metadata:EMBEDDED_GENERATION_PROMPT`.
- Contradictory evidence: none.
- Moderating evidence: `sensor_origin:camera_like_acquisition_supported`.
- Policy rationale: Confidence policy synthetic.unverified_generation_declaration: An explicit generation declaration supports declared creation context; metadata authenticity is unverified. Moderating observations qualify this interpretation; they do not automatically refute it or support a different hypothesis. Confidence tiers are heuristic support levels, not calibrated probabilities; related module outputs are not assumed statistically independent.

Reliability and coverage limitations:

- Heuristic support levels are not probabilities.
- Metadata authenticity is unverified; C2PA presence alone is not validation.
- Analysis coverage is incomplete. Unavailable stages: Person-derived region masks, Region segmentation analysis, Boundary-focused analysis, Region-aware FFT analysis, Segmentation alignment analysis, Subject texture consistency analysis, Subject process asymmetry analysis, Subject material realism analysis, Patch spatial analysis. Missing regional evidence supports neither authenticity nor synthetic origin.
- Coverage limitation (not negative evidence): unavailable subject_material_realism, subject_process_asymmetry.

### localized_editing

- Supporting evidence: `boundary:possible_boundary_fragment_convergence`, `cross_signal:strong_hotspot_convergence`.
- Contradictory evidence: none.
- Moderating evidence: `sensor_origin:camera_like_acquisition_supported`.
- Policy rationale: Confidence policy localized.not_established: A specific localized mechanism is not established. Moderating observations qualify this interpretation; they do not automatically refute it or support a different hypothesis. Confidence tiers are heuristic support levels, not calibrated probabilities; related module outputs are not assumed statistically independent.

Reliability and coverage limitations:

- Localized editing evidence does not by itself establish AI generation.
- Boundary reliability is reduced (0.00).
- Analysis coverage is incomplete. Unavailable stages: Person-derived region masks, Region segmentation analysis, Boundary-focused analysis, Region-aware FFT analysis, Segmentation alignment analysis, Subject texture consistency analysis, Subject process asymmetry analysis, Subject material realism analysis, Patch spatial analysis. Missing regional evidence supports neither authenticity nor synthetic origin.
- Coverage limitation (not negative evidence): unavailable boundary_focus, patch_spatial, region_masks, segmentation_alignment.

### camera_acquisition

- Supporting evidence: `sensor_origin:camera_like_acquisition_supported`.
- Contradictory evidence: none.
- Moderating evidence: none.
- Policy rationale: Confidence policy camera.acquisition_compatibility: Camera-like structure or coherent photo-like processing supports compatibility, not photographic authenticity. Confidence tiers are heuristic support levels, not calibrated probabilities; related module outputs are not assumed statistically independent.

Reliability and coverage limitations:

- Camera compatibility does not authenticate an image and may coexist with synthetic creation or later editing.
- Analysis coverage is incomplete. Unavailable stages: Person-derived region masks, Region segmentation analysis, Boundary-focused analysis, Region-aware FFT analysis, Segmentation alignment analysis, Subject texture consistency analysis, Subject process asymmetry analysis, Subject material realism analysis, Patch spatial analysis. Missing regional evidence supports neither authenticity nor synthetic origin.

Mask status `unreliable`, coverage 0.9181777419747081. The maximum usable coverage remains 0.90. Stage statuses: `{"skipped": 8, "success": 14, "unavailable": 1}`; no errors.

## Interpretation and preserved safeguards

Instagram retains High confidence in localized processing because reliable person geometry, strong local support and the existing compound boundary requirement are satisfied. This confidence is specific to processing inconsistency; synthetic origin remains Inconclusive. Camera-compatible observations remain moderation and do not rule out later editing. No global contradiction deduction or new score formula was applied.

Midjourney retains Medium confidence in an explicit unverified generation declaration. Camera-compatible structure can coexist with that declaration. Its 0.9181777419747081 person-mask coverage remains rejected under the existing 0.90 limit: region selection is unavailable and eight regional analyses skip. Missing regional evidence does not become either authenticity support or synthetic-origin support, and does not arbitrarily reduce the declaration tier. The policy and presentation share the same coverage limitation.

The full numerical scorecard, Phase 2A operation ledger, section snapshot, Phase 2B.2 dependency sidecar and Phase 2B.3 corroboration audit were compared to baseline and remain unchanged. The policy adds authoritative confidence rules, scoped rationale and consistent limitations; it does not replace shadow scores or modify gate semantics.

## Actual baseline-module replay of the corrected route bypass

| Metric | Inherited Phase 2B.3 | Centralized Phase 3 |
| --- | --- | --- |
| Pattern | multi_signal_suspicious_convergence | multi_signal_suspicious_convergence |
| Primary hypothesis | unresolved_anomaly | unresolved_anomaly |
| Tier | High | Medium |
| Suspicious score | 8.155 | 8.155 |
| Benign score | 0.0 | 0.0 |
| Authority | hardcoded route High | generic.one_strong_observation |

The fixture has strong boundary and cross indicators from the same ELA/residual ancestry, reliable reduced boundary support, and an additional nonspecific weighted observation. The score is 8.155 in both implementations. The Phase 2B.3 generic diversity gate already fails, but the general accumulation route previously bypassed it by returning High. The exact inherited module was loaded read-only from the baseline snapshot and replayed against the same inputs. Phase 3 assigns Medium under `generic.one_strong_observation`; the scorecard and mathematical ledger are identical.

This is an explained reasoning correction, not evidence that a lower tier is statistically more accurate. A separate regression proves that omitting safeguard routes cannot evade the existing required-geometry/boundary reliability cap. Tier tampering and route reordering tests show that provisional labels do not control final confidence.

## Artifact and consistency checks

- `summary/reasoning_trace.json` and `.txt`: named policy audit alongside the unchanged arithmetic and corroboration audits.
- `summary/final_summary.json`, `.txt`, `.html`: primary policy tier and scoped evidence presentation.
- `validation_result.json`, `console.txt`: actual pipeline counts, mask diagnostics, invariant checks and reference policy records.
- `route_bypass_comparison.json`: sanitized before/after replay of the explained behavioral change.
- `inherited_baseline/` and `phase3_only.patch`: isolated review boundary from prior uncommitted work.

The selected primary tier equals its hypothesis tier and policy tier. Supporting/contradicting/moderating/contextual IDs and limitations agree between policy and hypothesis records. The final rationale is generated by the policy, with only the existing selection explanation prepended for presentation. No shadow confidence or probability is assigned.
