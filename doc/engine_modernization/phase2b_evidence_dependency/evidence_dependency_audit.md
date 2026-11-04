# Phase 2B.1 — forensic evidence dependency and double-counting audit

## Scope and baseline

This is a source-code and saved-trace audit, not a scoring change or empirical
correlation study. Branch: `fix/scorecard-integrity-phase2a`; latest committed
baseline: `f64f226` (`phase 1`). Phase 2A is present in the working tree and
remains uncommitted. At entry, four tracked Python files were modified and its
integrity module, test module and report were untracked. The user's Phase 2B.1
task file was also untracked. Those files were preserved; no branch was created.

Baseline validation: **184 passed, 0 failed, 0 skipped**. Existing Phase 2A
reference traces are compatible and reconstruct within relative/absolute
tolerance 1e-12, so no image rerun was necessary. No image, production Python,
test, dependency, scoring coefficient, threshold, confidence rule or narrative
was edited. Reviewable audit deliverables are restricted to this directory. Root Python
and test file hashes are checked against the entry snapshot at final validation.

The audit distinguishes:

- **Computational dependency:** confirmed from arguments, arrays or transformations.
- **Measurement overlap:** confirmed shared feature definitions/regions, or explicitly
  suspected common effects; does not imply identical values.
- **Statistical correlation:** output covariance across samples; **not measured here**.
- **Forensic redundancy:** lack of additional hypothesis information; needs
  validation and cannot be inferred from module names alone.

## Five highest-priority risks

| Rank / severity | Finding | Confirmed exposure | What remains unverified |
| --- | --- | --- | --- |
| 1 / High | Processing composites can be treated as separate weighted domains and corroborating checks | Same ELA/residual ancestry → cross, boundary, focus, alignment → separate base weights/domain credit, local/edit terms and boundary corroboration | Whether their spatial/contour distinctions improve discrimination enough to justify each weight |
| 2 / High | Subject-surface regularity is rewarded through multiple overlapping pathways | Texture and regional FFT feed asymmetry; material imports asymmetry's patch feature helpers; texture/asymmetry/material all have base and edit paths, with material also synthetic and interaction bonuses | Conditional information gain beyond smoothing, depth of field, clothing texture and computational photography |
| 3 / High | Confidence/corroboration gates count child indicators without ancestry accounting | `_boundary_corroborated` can count boundary + focus + alignment; `determine_confidence` counts boundary + cross; synthetic route can combine material + asymmetry | Tier reliability under these shared-parent combinations; score arithmetic correctness alone does not establish it |
| 4 / Medium-high | Patch recurrence is counted before and after localization; frequency support overlaps | Spatial patch consumes the identical retained matches; separate base/domain and clone support; regional FFT reuses global FFT code on overlapping source content and feeds asymmetry | Incremental localization value versus crop/mask/retained-pair bias; output covariance of independent calculations |
| 5 / Medium-high | Camera/provenance observations affect several model controls | One generation declaration produces base + provenance boost + route flags; sensor/CFA compatibility produces benign base, measured support, attenuation, cautions and local tempering | Whether intended multi-role moderation is too strong; provenance and OSINT may refer to the same originating assertion |

These are confirmed multiple contribution paths and potential redundancy risks.
They are not proof that all duplicated paths are bugs or that all correlated
evidence should be removed. Phase 2A already fixed arithmetic duplication and
stale aggregation. Existing coefficients explicitly implement many of these
multi-path effects; changing them is policy, not an arithmetic repair.

## What actually contributes

`summary_synthesizer.build_summary_result()` builds **20 section keys**.
`hypothesis_engine.compute_base_scores()` gives each active suspicious/benign
section weak=0.5, medium=1.5 or strong=3.0, then adds 0.25 per extra distinct
domain within that polarity. A domain name is an organizational label, not a
statistical test of independence. Neutral ELA and residual sections add **zero**
base weight and **zero** direct boosts in the actual builders. Their influence
is downstream through composites, gating and narratives.

`compute_scorecard()` has **103 ledger-operation sites**, including conditional
branches and reliability/floor operations. The lineage CSV records each site's
field, operand expression, guard, upstream source and exact line. It also covers
20 section base paths, domain accounting, five aggregate transforms and 24
pattern/route/confidence consumers. Guards include inactive alternatives, not
103 simultaneously active contributions. Component dependencies such as
`component:local_edit_support_score` reference the same CSV's producer rows.

There are 148 inventory rows: 25 detectors/integration records, 66 concrete
summary-pattern contracts, and 57 derived interpretation fields. The executed
but unwired region-segmentation detector and disabled legacy mask path are
explicitly distinguished from active scoring. Pattern contracts record adapter
recognition, not proof of reachability on a real image; their possible
status/polarity values remain tied to the exact source branch.

The final aggregate remains:

```text
Q = baseS + synthetic + edit + provenance + sensor + compression
S = max(0, Q * measured_camera_multiplier - caution) * geometry * photo_prior
B = baseB
```

Local support is converted to edit at 0.18 once, then reliability is applied;
it is not also added directly to Q. Clone support is used by routing and is not
a separate Q term. Camera support changes attenuation/cautions/routes, rather
than being another additive suspicious weight. This audit does not incorrectly
sum these intermediates with the final score.

## A. ELA, residual, cross-signal and boundaries

Confirmed lineage in `SignalLensController._cross_signal`:
`ela.blockwise.top_blocks` + `noise.blockwise.top_blocks` + parent patterns →
`vf_cross_signal.compute_spatial_overlap` → cross classification and
`classify_boundary_convergence`. The latter adds contour/clustering information
from the **same** overlap. Alignment consumes the returned filtered
`hotspot_mask`, resized into selected mask coordinates.

`vf_boundary_focus.run_boundary_focus_analysis` consumes the saved ELA/residual
maps with masks and compares masked intensity levels, not a third recompression
or new independent residual. It is not a child of the cross *classification*,
despite an outdated controller comment saying it depends on cross. Its actual
required payloads are ELA, residual and masks. It adds distinct localization
information, but the anomaly measurements have common ancestry.

Thus **four scoring interpretations** can derive from two image transforms:
cross, boundary, focus and alignment. Their respective strongest adapter base
weights are 1.5, 3, 3, 3; treating them as four domains adds 0.75 over the first
domain. Raw local terms can be 2 + 1 + 0.75 + 0.5 + 1.25 = 5.5 (last two
are alignment/cross and boundary-stack interactions). Local conversion yields
0.99 edit, and explicit alignment/cross/stack edit terms add 0.25+0.25+0.5=1.
Those paths can therefore expose 10.5 + 0.75 + 1.99 = **13.24 Q units** before
camera/reliability/other terms. This is a synthetic flag-combination illustration,
not an empirical maximum for real images or a calibrated likelihood. The strong
stack additionally requires FFT; its own 3 base weight and incremental 0.25
frequency-domain credit are excluded from 13.24. An isolated valid-card fixture
with those inputs reconstructs S=16.49, base=14.5, local=5.5, edit=1.99 and no
camera/caution attenuation. This confirms paths can coexist in the calculator.

Instagram's actual case is smaller: cross 0.5 + boundary 3 + focus 1.5 = 5
base units, plus 0.5 incremental domain credit relative to retaining one of
those domains. Alignment is neutral and strong-cross synergies are inactive.
The shared observations still influence boundary corroboration through both
boundary and focus. Distinct morphology/localization is additional information;
independence of those outputs has not been established.

## B. Global and regional frequency analysis

`vf_region_fft.run_region_fft_analysis` creates mean-filled, soft-masked crops
for subject, boundary and background and calls `vf_fft.run_fft_analysis` three
times. It does **not** consume the cached global FFT payload. This is shared
feature code and overlapping pixel ancestry, not identical spectral arrays.
Regional localization can be new information, while masks/crops/resizing can
introduce common structure or alter peaks. Global `frequency` and regional
`region_frequency` domains can both contribute base weights; regional gaps also
enter asymmetry through a 0.06 sigmoid carry-forward. Global FFT contributes
through FFT/patch synthetic and boundary-stack conditions. No code estimates
conditional dependence between these paths. In both reference traces regional
FFT supplies no base weight (Instagram inconclusive; Midjourney unavailable).

## C. Patch similarity, spatial recurrence and subject texture

`vf_patch_similarity.run_patch_similarity_analysis` actively uses accelerated
nearest-neighbor matching of normalized descriptors and constructs recurrence
coverage from retained pairs. Alternate bucketed/brute-force functions exist,
but are not separate active detectors. `vf_patch_spatial.run_patch_spatial_analysis`
uses exactly those `top_pairs` and `scale_info`, remaps endpoints to mask space,
and reports region/topology densities. Its separate domain and clone-support
bonus are confirmed downstream reuse. It adds location, not new matching.

`vf_subject_texture_consistency` computes new masked hybrid gradient/DCT/
residual-stat descriptors and neighbor comparisons. It does not consume global
patch matches. Its recurrence is a related measurement family, not an identical
pair list. Shared content and preprocessing suggest overlap; covariance and
redundancy need measurement. Retained-pair limits and mask focus can affect
apparent spatial concentration.

## D. Sensor, CFA and process asymmetry

Sensor origin uses luminance high-pass energy and 2x2 phase imbalance;
CFA/demosaicing uses R-G/B-G high-pass phase structure plus directional
interpolation features (`compute_block_maps` in the respective modules).
Both use Gaussian sigma 1.2 and acquisition-structure proxies but compute
different channels/maps. Neither consumes the other's output. These are
partially overlapping measurements, not independently validated PRNU evidence.

Process asymmetry does **not** consume sensor/CFA payloads. Its own patch
features include Gaussian residual energy, entropy, gradients and DCT
(`_extract_patch_features`), so low-level feature overlap is real. It also
consumes texture results for baseline penalties/carry-forward and regional FFT
gaps for carry-forward. Material realism imports its sampler/aggregator/helper
code but independently extracts subject patch metrics. Asymmetry's subject-only
fallback uses the same families as material realism, increasing potential
redundancy when the comparative background is weak.

Camera-like support and local suspicion can coexist logically: camera-compatible
structure does not rule out an edited photograph. However, benign base,
convergence camera bonus, multiplier, additive caution, local tempering and
clone damping can multiply the effect of the same compatibility observation.
That is intentional current policy, not independent counter-evidence. Missing
metadata gives no positive acquisition observation, although `provenance_clean`
means **no adverse declaration**, not authenticated clean history; it can enable
extra camera caution. Naming/semantics should make this distinction explicit.

## E. Subject boundary, boundary focus and alignment

`vf_subject_boundary.make_boundary_mask` thresholds normalized image gradients
and forms morphological rings. Its texture/sharpness/residual/color/contrast
comparisons are not computed from the MediaPipe person contour. Reliable person
mask presence permits the current subject/background interpretation in
`summary_synthesizer`, but does not verify that the internally selected edges
actually track that person. This is a scope-validation gap, not a proven
dependency identity. With unreliable person geometry it is correctly demoted
to a neutral image-edge observation.

Focus and alignment share selected masks; focus shares anomaly maps with
cross/boundary. `_boundary_corroborated()` counts boundary, focus, intrinsic
subject boundary and alignment, requiring at least two and a numeric maximum
strength >=0.45. Those scores have heterogeneous units: alignment fraction,
subject-boundary bounded heuristic and focus raw intensity boost. An OR/count
and maximum do not establish common calibration or independent corroboration.
The function can accept two descendants of the same parents. This deserves
family-aware gating review, even if no numerical weights are changed.

## F. Metadata, OSINT and repeated presentation

One declared-generation family produces a suspicious medium metadata base
weight 1.5, sets derived synthetic flags and selects provenance boost 0.75
(1.25 for joint AI-gallery context). OSINT alone uses the alternative 0.50
branch; these boosts are mutually exclusive, **not** 0.75+0.50+1.25. A
metadata flag may also enable synthetic support or choose a declaration route.
The metadata section's scalar 0.75 is not separately added as a third numeric
term: the base uses its status, not its numeric score.

In Midjourney, `DECLARED_SYNTHETIC` and `EMBEDDED_GENERATION_PROMPT` appear as
two supporting narrative identifiers, but they produce one section base and one
provenance boost. This is repeated reporting within a common provenance family,
not two additional score terms. Counts of evidence-list entries should not be
used to claim independent confirmations. Metadata authentication is unverified,
and OSINT's source label can describe the same declaration rather than an
independent verification. The headless controller does not run OSINT searches;
the summary consumes an optional recorded review.

## Independence language review

| Source / claim | Classification | Recommendation |
| --- | --- | --- |
| `decision_logic.build_confidence_rationale`: outputs are not assumed statistically independent; tiers are not probabilities | Supported description of limitations | Retain; no independence estimator exists |
| `route_multi_signal_suspicious`: checks may be correlated | Supported limitation | Retain; optionally name shared parent family |
| `signal_language.SIGNAL_LANGUAGE` entry `no_meaningful_convergence`: “independent forensic signals do not converge meaningfully” | Unsupported independence adjective; separate transforms do not prove it | “ELA and residual hotspot checks do not meaningfully overlap” |
| `evaluate_hypotheses` selection explanation: declaration supports creation “independently of inconclusive localized editing” | Supported logical scope separation, not statistical independence | “without requiring a conclusive localized-editing result” avoids ambiguity |
| `_boundary_corroborated` and route text “boundary-focused corroboration” | Spatial agreement plausible; independent corroboration unverified | “agreement among related boundary checks” and state parent families |
| `route_synthetic_multi_signal`: “Multiple visual signals support...” | Plausible but unverified additional information; material/asymmetry can overlap | “Related visual measurements show...” with lineage and empirically assessed incremental support |
| `route_localized_multi_mechanism`: duplicated content and foreground/background inconsistency | Distinct mechanism interpretations, supported by code separation at interpretation level | Retain as candidate mechanisms, disclose shared pixel features and avoid “independent” |
| `hypothesis_evidence` structure statements “does not independently establish synthetic origin” | Correct caution about insufficiency | Retain; lists are roles, not a statistical evidence count |

No active claim of “independent forensic domains” was found in the inspected
rationale/route sources. Domain-count bonuses nevertheless behave as diversity
credit. Source-code separation supports only separate calculations; distinct
measurement families improve interpretability but do not prove independence.
No production wording was changed.

## Reference impact and limits

See [reference_case_analysis.md](reference_case_analysis.md) for every base row,
every executed component operation, raw/final values, mechanism grouping,
hypothesis support and diagnostic definitions.

| Conditional calculation | Instagram S | Midjourney S |
| --- | --- | --- |
| Actual Phase 2A baseline | 20.47705 | 6.0375 |
| A: remove downstream-composite base rows, preserve boosts/penalties | 13.46455 | 3.9125 |
| B: remove selected corroboration component bonuses, preserve bases/gates | 19.98235 | 6.0375 |
| C: maximum base representative per broad family, preserve boosts/penalties | 13.25205 | 5.4 |
| D: remove additive boost layer, preserve base/camera/caution | 17.95 | 5.4 |

These alternatives are isolated conditional arithmetic, not rerouted full
counterfactuals or a calibrated replacement formula. All leave B unchanged.
They must not be interpreted against current confidence thresholds. No accuracy
claim follows from a lower total. The reference cases are selected examples,
not a labeled benchmark; no statistical correlations or false-positive rates
have been estimated.

Actual outcomes remain Instagram **High localized editing**, Midjourney **Medium
unverified synthetic-origin declaration**. Both retain zero failed stages; mask
and coverage behavior remain unchanged. The Midjourney boundary mechanism boost
is zero at reliability zero, but its cross/boundary base weights still exist.
This is an explicit existing reliability scope, not a new arithmetic defect.

## Integration and reliability issues requiring separate review

1. Region-segmentation morphology runs but is absent from section synthesis;
   its scorecard branches are dormant in the normal pipeline. Document whether
   it is intended solely as diagnostics before reconnecting it. Activating a new
   scoring signal would require policy validation, not a silent wiring fix.
2. `determine_confidence` reads raw section patterns/scores without active-status
   checks, unlike Phase 2A's available evidence snapshot. Some downstream helpers
   also consult raw `env.sections`. Stale unavailable strong patterns could
   contaminate counts/gates for programmatic callers, although normal controller
   synthesis clears unavailable patterns. Mandatory status-contract hardening
   should be separately tested; no such change is made here.
3. Asymmetry caps comparative scores for unreliable geometry before subject-only
   and reverse fallback lifts. `_interpret_pattern` retains a geometry guard,
   so a late numerical lift is not proof that the guard is bypassed. Review
   final-score versus emitted-pattern reliability contracts before changing it.
4. Boundary focus can fall back to display overlays as measurement maps, and its
   raw boost is compared with differently scaled boundary scores by the gate.
   Prefer an explicit numeric feature/units contract in subsequent work.

## Recommendation and deliverable validation

Prefer a **lineage registry with marginal corroboration (B), bounded by explicit
family budgets (A)**, introduced first as shadow diagnostics. Give a composite
credit for the information it adds (localization/topology), not a full new
independent observation. The exact budget/bonus values remain undecided pending
benchmark evidence. See [phase2b2_implementation_proposal.md](phase2b2_implementation_proposal.md)
for four approaches, implementation boundaries, tests and empirical design.

`audit_dependency.py` deterministically regenerates both CSVs and the reference
analysis from source/saved traces. It asserts coverage of all 20 built sections,
unique evidence identifiers, finite/reconstructed reference components and
unchanged root/test Python hashes. The inventories intentionally retain dormant
contracts and inactive ledger alternatives with source explanations.

Final review checks CSV row counts and operation sites, source function anchors,
graph family coverage, deterministic regeneration, protected-file hashes,
ignored image/output status and `git diff --check`. No raw reference image or
raw trace was copied into the deliverables. No staging, commits, pushes,
merges, tags, stashes or publication were performed.
