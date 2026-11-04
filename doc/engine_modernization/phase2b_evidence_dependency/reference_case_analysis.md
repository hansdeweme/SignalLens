# Reference-case contribution and dependency analysis

Source: existing local Phase 2A full headless `subject_based` traces. No detector rerun was necessary. This report exports only section identifiers, arithmetic and hypothesis evidence identifiers; no images, filenames, embedded prompts, attribution values or raw detector payloads.

## Diagnostic definitions and limits

- A: remove only downstream composite suspicious base rows (cross, boundary, focus, alignment, regional FFT, spatial patch, process asymmetry), recomputing the remaining domain bonus. Keep boosts/penalties fixed. This isolates base duplication exposure, not a full causal ablation.
- B: remove positive raw local/edit/clone additions whose recorded reason depends on cross/boundary/segmentation-alignment/asymmetry/spatial corroboration; recalculate the 0.18 local-support conversion, then replay original reliability operations. Keep base rows, guards, synthetic/sensor/compression boosts and cautions fixed. Shared subject-boundary/alignment alias contributions are retained because the ledger cannot uniquely attribute their OR source.
- C: keep the maximum suspicious base weight per illustrative family, with recurrence+surface combined, and replace domain diversity with family diversity. All boosts and penalties stay fixed. This deliberately broad grouping can discard new information.
- D: set the five final boost fields to zero; retain all base, camera and caution terms. This isolates the additive boost layer, not evidence independence.
All alternatives freeze original camera/geometry/photo transforms and penalty applicability. They do not reroute or recalculate confidence. These are conditional arithmetic diagnostics, not empirically validated replacement models. Any adopted formula needs recalibration; do not compare alternative totals to current tier thresholds.

## Instagram

Baseline: S=20.47705000, B=2.25; pattern `possible_foreground_background_processing_mismatch`, confidence High. Both serialized aggregates and all components reconstruct within 1e-12.

### Complete base ledger

| Section | Polarity | Status | Domain | Weight | Family |
| --- | --- | --- | --- | --- | --- |
| boundary | suspicious | strong | boundary | 3.0 | processing |
| boundary_focus | suspicious | medium | boundary_focus | 1.5 | processing |
| cfa_demosaic | benign | weak | sensor_cfa | 0.5 | acquisition |
| compression_history | suspicious | strong | compression | 3.0 | compression |
| cross_signal | suspicious | weak | cross_signal | 0.5 | processing |
| fft | suspicious | strong | frequency | 3.0 | spectral |
| patch_similarity | suspicious | medium | patch | 1.5 | recurrence |
| patch_spatial | suspicious | medium | patch_spatial | 1.5 | recurrence |
| sensor_origin | benign | medium | sensor | 1.5 | acquisition |
| subject_boundary | suspicious | strong | boundary_semantic | 3.0 | edge_transition |
| subject_material_realism | suspicious | medium | subject_material | 1.5 | surface |
| subject_process_asymmetry | suspicious | weak | region_asymmetry | 0.5 | surface |
| subject_texture_consistency | suspicious | medium | subject_texture | 1.5 | surface |

Base S=23.0 includes domain bonus; B=2.25 includes its separate domain bonus.

### Complete component ledger

| Index | Field | Operation | Operand | Reason |
| --- | --- | --- | --- | --- |
| 1 | camera_counter_support | add | 1.25 | ds.camera_like_support |
| 2 | caution_penalty | add | 0.35 | ds.camera_like_support and ds.provenance_clean |
| 3 | local_edit_support_score | add | 2 | ds.strong_local_edit |
| 4 | local_edit_support_score | add | 0.75 | boundary_strong |
| 5 | local_edit_support_score | add | 0.4 | ds.compression_inconsistency |
| 6 | local_edit_support_score | add | 0.75 | ds.subject_texture_strong |
| 7 | local_edit_support_score | add | 0.4 | otherwise / asym_medium |
| 8 | local_edit_support_score | add | 0.75 | otherwise / ds.material_realism_medium |
| 9 | local_edit_support_score | add | -0.2 | ds.camera_like_support |
| 10 | edit_boost | add | 0.4 | ds.subject_texture_strong |
| 11 | edit_boost | add | 0.15 | otherwise / asym_medium |
| 12 | edit_boost | add | 0.4 | otherwise / ds.material_realism_medium |
| 13 | edit_boost | add | 0.873 | local_support_conversion |
| 14 | clone_support_score | add | -0.9 | usable_observation(ev.patch_similarity) / camera_benign |
| 15 | clone_support_score | maximum | 0 | clone_floor |
| 16 | synthetic_boost | add | 0.4 | otherwise / ds.material_realism_medium |
| 17 | compression_boost | add | 0.75 | ds.compression_inconsistency and (ds.strong_cross or ds.strong_local_edit or ds.subject_boundary_strong) |
| 18 | caution_penalty | add | 1.25 | measured_camera_caution |

### Raw and adjusted components

| Field | Raw | Adjusted |
| --- | --- | --- |
| camera_counter_support | 1.25 | 1.25 |
| local_edit_support_score | 4.85 | 4.85 |
| clone_support_score | 0 | 0 |
| synthetic_boost | 0.4 | 0.4 |
| edit_boost | 1.823 | 1.823 |
| provenance_boost | 0 | 0 |
| sensor_boost | 0 | 0 |
| compression_boost | 0.75 | 0.75 |
| caution_penalty | 1.6 | 1.6 |

Aggregate transforms: `{"camera_multiplier": 0.85, "geometry_multiplier": 1.0, "measured_camera_support": 1.25, "photo_context_multiplier": 1.0, "photo_context_prior": false, "suspicious_floor": 0.0}`.

### Base contributions grouped by mechanism

| Family | Suspicious weights before domain bonus | Benign weights before domain bonus |
| --- | --- | --- |
| acquisition | 0.0 | 2.0 |
| compression | 3.0 | 0.0 |
| edge_transition | 3.0 | 0.0 |
| processing | 5.0 | 0.0 |
| recurrence | 3.0 | 0.0 |
| spectral | 3.0 | 0.0 |
| surface | 3.5 | 0.0 |

B removed component reasons: `ds.strong_local_edit`; `otherwise / asym_medium`; `otherwise / asym_medium`.

### Hypothesis-specific support

- `synthetic_origin`: Inconclusive; supporting: none; moderating: `cfa_demosaic:weak_camera_cfa_supported`, `sensor_origin:camera_like_acquisition_supported`.
- `localized_editing`: High; supporting: `boundary:possible_foreground_background_processing_mismatch`, `boundary_focus:boundary_focused_processing_mismatch`, `compression_history:localized_compression_inconsistency`, `cross_signal:partial_hotspot_convergence`, `subject_boundary:possible_subject_background_segmentation_artifact`; moderating: `cfa_demosaic:weak_camera_cfa_supported`, `sensor_origin:camera_like_acquisition_supported`.
- `camera_acquisition`: Medium; supporting: `cfa_demosaic:weak_camera_cfa_supported`, `sensor_origin:camera_like_acquisition_supported`; moderating: none.

Coverage status: `complete`. Unavailable section keys: osint.

## Midjourney

Baseline: S=6.03750000, B=1.5; pattern `provenance_supported_synthetic_context`, confidence Medium. Both serialized aggregates and all components reconstruct within 1e-12.

### Complete base ledger

| Section | Polarity | Status | Domain | Weight | Family |
| --- | --- | --- | --- | --- | --- |
| boundary | suspicious | weak | boundary | 0.5 | processing |
| cross_signal | suspicious | medium | cross_signal | 1.5 | processing |
| fft | suspicious | strong | frequency | 3.0 | spectral |
| metadata | suspicious | medium | metadata | 1.5 | provenance |
| patch_similarity | suspicious | medium | patch | 1.5 | recurrence |
| sensor_origin | benign | medium | sensor | 1.5 | acquisition |

Base S=9.0 includes domain bonus; B=1.5 includes its separate domain bonus.

### Complete component ledger

| Index | Field | Operation | Operand | Reason |
| --- | --- | --- | --- | --- |
| 1 | camera_counter_support | add | 1.25 | ds.camera_like_support |
| 2 | local_edit_support_score | add | 0.5 | otherwise / ds.fragmented_local_edit |
| 3 | local_edit_support_score | add | 1 | ds.strong_cross |
| 4 | local_edit_support_score | add | -0.2 | ds.camera_like_support |
| 5 | edit_boost | add | 0.5 | ds.fragmented_local_edit and ds.strong_cross |
| 6 | edit_boost | add | 0.234 | local_support_conversion |
| 7 | clone_support_score | add | 0.35 | usable_observation(ev.patch_similarity) / detail(ev.patch_similarity, 'coverage_ratio', None) is not None and ds.coverage_ratio <= 0.18 |
| 8 | clone_support_score | add | -0.9 | usable_observation(ev.patch_similarity) / camera_benign |
| 9 | clone_support_score | maximum | 0 | clone_floor |
| 10 | provenance_boost | add | 0.75 | otherwise / ds.metadata_synthetic or ds.metadata_enhancement |
| 11 | caution_penalty | add | 1.25 | measured_camera_caution |
| 12 | local_edit_support_score | multiply | 0 | boundary_reliability |
| 13 | edit_boost | multiply | 0 | boundary_reliability |
| 14 | caution_penalty | add | 1 | boundary_reliability_caution |

### Raw and adjusted components

| Field | Raw | Adjusted |
| --- | --- | --- |
| camera_counter_support | 1.25 | 1.25 |
| local_edit_support_score | 1.3 | 0 |
| clone_support_score | 0 | 0 |
| synthetic_boost | 0 | 0 |
| edit_boost | 0.734 | 0 |
| provenance_boost | 0.75 | 0.75 |
| sensor_boost | 0 | 0 |
| compression_boost | 0 | 0 |
| caution_penalty | 1.25 | 2.25 |

Aggregate transforms: `{"camera_multiplier": 0.85, "geometry_multiplier": 1.0, "measured_camera_support": 1.25, "photo_context_multiplier": 1.0, "photo_context_prior": false, "suspicious_floor": 0.0}`.

### Base contributions grouped by mechanism

| Family | Suspicious weights before domain bonus | Benign weights before domain bonus |
| --- | --- | --- |
| acquisition | 0.0 | 1.5 |
| processing | 2.0 | 0.0 |
| provenance | 1.5 | 0.0 |
| recurrence | 1.5 | 0.0 |
| spectral | 3.0 | 0.0 |

B removed component reasons: `otherwise / ds.fragmented_local_edit`; `ds.strong_cross`; `ds.fragmented_local_edit and ds.strong_cross`.

### Hypothesis-specific support

- `synthetic_origin`: Medium; supporting: `metadata:DECLARED_SYNTHETIC`, `metadata:EMBEDDED_GENERATION_PROMPT`; moderating: `sensor_origin:camera_like_acquisition_supported`.
- `localized_editing`: Inconclusive; supporting: `boundary:possible_boundary_fragment_convergence`, `cross_signal:strong_hotspot_convergence`; moderating: `sensor_origin:camera_like_acquisition_supported`.
- `camera_acquisition`: Medium; supporting: `sensor_origin:camera_like_acquisition_supported`; moderating: none.

Coverage status: `partial`. Unavailable section keys: osint, region_masks, segmentation_alignment, region_fft, boundary_focus, subject_texture_consistency, subject_process_asymmetry, subject_material_realism, patch_spatial.

## Conditional numerical ablations

| Case | Baseline | A composites base removed | B corroboration components removed | C representative family bases | D boost layer removed |
| --- | --- | --- | --- | --- | --- |
| instagram | 20.477050000 | 13.464550000 | 19.982350000 | 13.252050000 | 17.950000000 |
| midjourney | 6.037500000 | 3.912500000 | 6.037500000 | 5.400000000 | 5.400000000 |

## Interpretation of ancestry and numerical exposure

Instagram processing ancestry contributes base cross 0.5 + boundary 3 + focus 1.5 = 5, plus two incremental domain bonuses (0.5 relative to keeping one existing processing domain). Its boundary local +2 contributes 0.36 through conversion to edit; cross is partial so strong-cross component synergies are inactive; focus adds no dedicated boost. Holding everything else fixed, keeping only boundary of these three removes 2.5 from Q, or 2.125 from S. The broader A also removes patch spatial 1.5 and asymmetry 0.5 and their diversity credit.

Instagram recurrence/surface base weights are patch 1.5 + spatial patch 1.5 + texture 1.5 + asymmetry 0.5 + material 1.5 = 6.5 (diversity accounted separately). Texture contributes local 0.75 -> edit 0.135 plus direct edit 0.4. Asymmetry contributes local 0.4 -> edit 0.072 plus direct edit 0.15. Material contributes local 0.75 -> edit 0.135 plus direct edit 0.4 and synthetic 0.4. Their respective additive extras in Q are 0.535, 0.222 and 0.935; these are multiple paths, not independent likelihoods. Compression contributes base 3, local 0.4 -> edit 0.072 and compression boost 0.75. Subject boundary contributes base 3 and boundary-alias local 0.75 -> edit 0.135. These explain all 1.823 edit units once camera local tempering contributes -0.036. Do not add local total 4.85 again.

Midjourney processing base cross 1.5 + boundary 0.5 derives from the same hotspot overlap. Its raw local 0.5 + 1 - 0.2 = 1.3 and raw edit synergy 0.5 + conversion 0.234 = 0.734 are both zero after boundary reliability r=0. Base cross/boundary weights remain: reliability applies to mechanisms, not the whole base layer. Its metadata base 1.5 + provenance boost 0.75 represents one declaration family; two supporting metadata identifiers in the narrative do not add two further score terms. With five suspicious domains, attributing an incremental domain bonus to removal of metadata adds 0.25: removing that base row and boost alone reduces Q by 2.5 and S by 2.125, holding other terms fixed. Hypothesis support remains unverified, and the reference is not proof that provenance is correct.

Camera support is reused deliberately in both cases: sensor benign base 1.5; measured camera +1.25 produces m=0.85 and caution 1.25; local tempering -0.2 propagates through edit (removed by r=0 on Midjourney). Instagram additionally receives clean-context caution 0.35, and weak benign CFA adds base 0.5 plus a 0.25 second-domain bonus but no measured-camera increment. These are separate model effects, not extra independent observations.

Instagram has 23 completed / 0 skipped / 0 failed stages and reliable mask coverage 0.5961422390407987. Midjourney has 14 completed / 9 unavailable-or-skipped / 0 failed and unreliable coverage 0.9181777419747081 under the unchanged 0.90 limit. Cross-signal succeeds on both. No unavailable regional measurement is imputed. Two cases cannot estimate dependence, false-positive rates, accuracy or calibration.
