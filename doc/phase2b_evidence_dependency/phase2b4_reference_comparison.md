# Phase 2B.4 reference-image comparison

Both original images ran through `SignalLensController.run_analysis` in
`subject_based` mode, followed by summary synthesis and text/HTML/JSON reasoning
persistence. Final runner and outputs are under ignored
`analyzed/phase2b4_validation/`; the runner is `run_reference_validation.py`,
with results in `reference_results.json`. Before values come from the preserved
final acceptance-audit traces. Historical outputs were not rewritten.

| Metric | Instagram before | Instagram after | Midjourney before | Midjourney after |
| --- | --- | --- | --- | --- |
| Suspicious score | 20.47705 | 20.47705 | 6.0375 | 5.4 |
| Benign score | 2.25 | 2.25 | 1.5 | 1.5 |
| Raw/eligible suspicious base weight | 20.5 / 20.5 | 20.5 / 20.5 | 8 / 8 | 8 / 7.5 |
| Suspicious domain bonus | 2.5 | 2.5 | 1 | 0.75 |
| Base suspicious total | 23 | 23 | 9 | 8.25 |
| Final additive boosts | 2.973 | 2.973 | 0.75 | 0.75 |
| Camera multiplier | 0.85 | 0.85 | 0.85 | 0.85 |
| Caution penalty | 1.6 | 1.6 | 2.25 | 2.25 |
| Geometry/photo multipliers | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |
| Deduplicated base rows | None | None | None | Fragmented boundary: 0.5 |
| Deduplicated component rows | None | None | None | Fragment local 0.5 and fragment/cross edit 0.5 before reliability |
| Remaining provisional scored relationships | Not enumerated by production | 6 | Not enumerated by production | 1 |
| Primary hypothesis | Localized editing | Localized editing | Synthetic origin | Synthetic origin |
| Confidence | High | High | Medium | Medium |
| Completed stages | 23 | 23 | 14 | 14 |
| Unavailable / skipped stages | 0 / 0 | 0 / 0 | 1 / 8 | 1 / 8 |
| Failed stages / recorded errors | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

The provisional relationship count names scored composites with uncalibrated
marginal value or incomplete ancestry, not a count of known duplicate defects.
Instagram's entries are boundary, boundary focus, cross signal, patch spatial,
material realism and process asymmetry. Midjourney's is cross signal. Related
primary extraction families also have the empirical limits in the classification
report; this count is not an exhaustive covariance inventory.

## Instagram

`possible_foreground_background_processing_mismatch` requires the positive
contour branch of `classify_boundary_convergence`. Contour extent/elongation/fill
adds information beyond overlap. Boundary focus measures mask-relative intensity;
patch spatial measures retained-pair topology. Full credit is preserved:

| Relevant section | Raw base | Eligible base | Reason |
| --- | ---: | ---: | --- |
| Cross signal | 0.5 | 0.5 | Measured overlap relationship |
| Boundary | 3 | 3 | Positive measured contour property |
| Boundary focus | 1.5 | 1.5 | Regional intensity localization |
| Patch similarity | 1.5 | 1.5 | Retained matches |
| Patch spatial | 1.5 | 1.5 | Endpoint topology/localization |

Other base/component contributions remain unchanged. The aggregate reconstructs
as `(23 + 2.973) * 0.85 - 1.6 = 20.47705`.
All route match states, primary hypothesis and policy rule
`localized.reliable_boundary_compound` are unchanged. No new safeguard fires.
The retained selected person mask remains reliable; complete coverage is preserved.

## Midjourney

The observed weak boundary finding is the fragmented-overlap fallback. It does
not pass the positive contour criterion. Its overlap is already counted by the
medium cross section (1.5). The 0.5 boundary base is withheld, and `boundary`
ceases to supply an extra weighted domain. Metadata, frequency and patch
contributions retain full weight; the unverified declaration remains separate
from localized-processing evidence.

The 0.5 fragment local-support term and 0.5 fragment/cross edit term are also
withheld before mechanism reliability. Raw local support changes from 1.5 to
1.0; local-support conversion changes from 0.27 to 0.18, while the separate 0.5
fragment/cross boost is removed. Boundary reliability is zero in this image,
so these mechanism terms were already zero in the final score. They contribute
no additional final-score difference here, but the focused reliable-geometry
test proves the corrected mechanism behavior when reliability is nonzero.

The final difference is exactly `(0.5 + 0.25) * 0.85 = 0.6375`.
Before: `(9 + 0.75) * 0.85 - 2.25 = 6.0375`.
After: `(8.25 + 0.75) * 0.85 - 2.25 = 5.4` (floating representation
`5.3999999999999995`). No threshold was changed or conclusion forced.

All route match states remain unchanged. The primary hypothesis remains
synthetic origin from the unverified embedded-generation declaration; the policy
rule remains `synthetic.unverified_generation_declaration`, Medium. Person-mask
reliability remains low, with one unavailable regional mask stage and eight
dependent regional skips; independent stages continue. No new safeguard fires.

## Reproducibility and arithmetic

The final runner independently replays eligible base rows, domain bonuses,
component operations, reliability operations and aggregate transformations,
without calling the production reconstruction helper. Both cards reconcile.
Each image's repeated reasoning dictionaries are equal. Enabling shadow analysis
leaves scorecard, decisions, hypotheses, confidence policy and corroboration audit
equal to normal production output. The final tier appears in text and HTML.

Image SHA-256 values matched before/after:

- Instagram: `1feeccab1ddce2b24ddec95447e5c86cbbf2b77deabf7b01c76bdf3388d219f9`.
- Midjourney: `08c27f51a3bc9f6546d9ca3f99ad910ae293d2610679d1fdea6e53130902dda9`.

These two images establish integration behavior, not empirical accuracy or
independence. Neither diagnostic ablation score was adopted.
