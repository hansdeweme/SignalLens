# Boundary evidence, reliability and score audit

Evidence identity and RUN/TRACE aliases: [root-cause report](root_cause_report.md). All values below come from the saved normal-profile Midjourney trace. No detector was rerun and no score was changed.

## Different measurements, overlapping interpretations

| Output | Measurement and code | Saved result | What it establishes / does not establish |
|---|---|---|---|
| ELA | JPEG recompression-difference map and high-value blocks, `vf_ela.py`, `run_ela`; saved `RUN/*_ela.json` | `ela_inconclusive`, weak/neutral | No decisive standalone ELA interpretation; high-ranked blocks still exist. |
| Residual | Luminance residual magnitude and high-value blocks, `vf_noise.py`, `run_noise_analysis`; saved `RUN/*_noise.json` | `noise_inconclusive`, weak/neutral | No decisive standalone residual interpretation; does not assert zero residual structure. |
| Cross Signal | Spatial proximity of high-ranked ELA/residual blocks, `vf_cross_signal.py:18`, `classify_cross_signal_overlap`; `:224`, `compute_spatial_overlap` | `strong_hotspot_convergence`, medium/suspicious | Relative hotspot overlap. Not independent of its parents and not a detected editing event. |
| Boundary Signal | Connected-component/contour shape of those same overlapping blocks, `vf_cross_signal.py:62`, `classify_boundary_convergence` | `possible_foreground_background_processing_mismatch`, strong/suspicious in summary | Generic contour-like hotspot arrangement; **does not require coincidence with the person boundary**. Producer strength is medium; `summary_sections.py:471-474` maps the pattern to strong. |
| Boundary Focus | ELA/residual mean and variation in actual subject, contour-band and background masks, `vf_boundary_focus.py:124`, `run_boundary_focus_analysis` | `boundary_processing_inconclusive`, neutral; raw score 2.1537491 | No clear contour-band-specific elevation. Not the explicit convergence/benign pattern and not formal evidence that all processing is uniform. |
| Segmentation Alignment | Fraction of cross hotspots on the actual person contour band, resized consistently, `vf_segmentation_alignment.py:26-58` | raw overlap 0, score 0; weak/neutral | No measured person-boundary alignment. Limits person-localization interpretation; does not disprove hotspots elsewhere. |
| Subject Boundary | Image-gradient threshold and rings around intrinsic edges; texture, sharpness, residual proxy, color, contrast, `vf_subject_boundary.py:61-79,190-238` | medium/suspicious; bounded score 0.3933163 | Measured edge-ring irregularity. Detector does not take the person mask as an input. A usable mask elsewhere is not proof that these edges are the person's contour. |
| Compression History | Block-grid/save-history proxies, `vf_compression_history.py:150`, `interpret_compression_history` | inconclusive/neutral | No affirmative save-history corroboration; no universal refutation of processing. |

Saved Boundary Focus values: combined ratio **1.0725998242**, boost **0.5818681717**, transition score **2.1537491083**; ELA band ratio **0.9904039256**, residual band ratio **1.1547957229**. Positive classification thresholds are detector-specific (`vf_boundary_focus.py:175-194`): a strong transition requires ratio >= 1.35, boost > 8 and transition > 6; medium mismatch has other ratio/boost conditions. These values do not meet positive conditions. They also fail explicit convergence because residual ratio is outside [0.92,1.08]. Therefore “inconclusive,” rather than benign convergence, is consistent with that detector's code.

There is **no demonstrated measurement-level contradiction** between a generic contour cluster, weak global component classifiers and a non-elevated actual person band. They summarize different properties and spatial selections. There is a significant **interpretation-level disagreement** when generic contours are described as foreground/background editing while mask-based tests do not localize them there. The subject-boundary result independently concerns image edges, which further weakens the claim that all checks refer to one person boundary.

`summary_synthesizer.py:117-136` correctly demotes intrinsic-edge results to contextual scope when usable person geometry is absent. For `mask_status=limited`, it allows the person-specific interpretation to remain. That eligibility guard does not perform edge-to-person registration. Future causal claims should distinguish available person geometry from demonstrated measurement alignment.

## Newly confirmed defect: ineligible raw strength witness

`decision_logic._boundary_corroborated` (`decision_logic.py:568-619`) computes two different things:

1. Indicator count accepts only suspicious medium/strong boundary, focus, subject-boundary or alignment sections (573-598).
2. Strength takes `max(section.score)` over **all** focus, subject-boundary and boundary sections without checking status, polarity or pattern (599-602); requires >= 0.45 (603-606).

The case therefore passes with:

| Source | Accepted for positive count? | Score consulted for strength? |
|---|---|---|
| Boundary | Yes | null |
| Subject Boundary | Yes | 0.3933163 |
| Boundary Focus | **No: inconclusive/neutral** | **2.1537491** |
| Alignment | No: weak/neutral | Not included in the strength maximum |

Count = 2; maximum = 2.1537491; both gate predicates pass. The score that makes the strength condition pass is not among the gate's recorded eligible supporting witnesses. `boundary.compound_support` records `strength_requirement_satisfied=true` without recording this actual source, so its compact audit is insufficient to reconstruct the strength provenance.

The adapter explicitly retains an inconclusive Focus score as `max(combined_boost, transition_score, 0)` (`summary_sections.py:551-554`). Retaining a measured value is legitimate; consuming it as affirmative mechanism strength is not. This is a code-contract defect, **not a recommendation to treat inconclusiveness as negative evidence**.

There is also a units problem: Focus scores are residual/recompression intensity differences, whereas Subject Boundary is normalized to [0,1]. The scalar maximum across them does not have a common scientific scale. A benign score 0 happens not to poison this case, but merely checking numerical finiteness would not repair the semantics.

Smallest correction to investigate in implementation: use explicitly eligible, detector-specific strength witnesses; record source ID, field, scale, required pattern/status and satisfied predicate. Do not compare intensity units with normalized anomaly units or choose a new threshold to fit this example. Existing qualifying Focus patterns already embody their own ratio/boost criteria; bounded Subject Boundary has its own documented threshold. Preserve legitimate compound agreement and positive controls.

Static counterfactual: if only eligible current score sources contribute, the available maximum here is **0.3933163 < 0.45**, so the present compound-strength condition fails. That alone removes the basis for the current High boundary branch. This is evaluation of written predicates and saved numbers, not a corrected-engine run or a predetermined final hypothesis. Exact future tier/selection must be validated after the rule contract is implemented.

## Inconclusive components and confidence moderation

`classify_boundary_convergence` explicitly permits `ela_inconclusive` and `noise_inconclusive` as component patterns (`vf_cross_signal.py:67-74`), then uses hotspot proximity/shape thresholds. `classify_cross_signal_overlap` requires at least four matched blocks and its Jaccard-like threshold for the named strong pattern, but returns strength medium. Relative rankings can produce matching clusters without strong absolute component evidence; the geometry is still an observation. It should not automatically be translated into a specific separate-edit mechanism or independent confirmation.

The formal role table has an explicit counter-evidence mapping only for `boundary_processing_convergence_supported` (`hypothesis_evidence.py:120-123`). Inconclusive Focus has no role mapping and is skipped by `usable_observation`. Alignment's named pattern maps to support only when suspicious; neutral zero fails that condition (`hypothesis_evidence.py:47-57,190-203`). No explicit person-localization limitation from alignment zero reaches the current local confidence policy. These results should constrain the applicability of a person-boundary mechanism; they need not become global negative weights.

Central `_localized` (`confidence_policy.py:187-226`) consumes the compound boolean, region eligibility and mechanism scores. It does not independently inspect raw Focus/alignment measurements. It therefore assigns High under existing inputs. That is explainable as current policy, but this case does not provide a defensible strength witness for that policy input. The failure of the generic diversity gate is a separate issue, not the reason this specific High is wrong.

## Mask quality versus geometry support

`vf_person_subject_mask._quality_from_mask` (`vf_person_subject_mask.py:222-264`) gives high quality when detected-person area is [0.08,0.85], largest component >= 0.70 and component count <= 3. Medium permits [0.03,0.90] with largest component >= 0.50. Actual subject area **0.8599715771** is just outside the high area interval, but inside medium; one component covers all selected foreground. Mean foreground confidence is 0.86835, explicitly not a person-detection probability. Thus medium/limited is expected.

`mask_contract.person_mask_diagnostics` (`mask_contract.py:32-83`) treats reliable and limited MediaPipe person masks as usable. Its boolean `person_mask_reliable` is really eligibility for downstream regional analysis. `hypothesis_engine.derive_signals` (`hypothesis_engine.py:292-309`) similarly accepts source `person_subject_mask` plus high **or medium** reliability. Band fraction 0.0451676 >= 0.03 produces `boundary_reliability_score=1.0`.

These quantities are distinct:

- mask quality: heuristic support/limitations of segmented foreground;
- person-mask eligibility: sufficient for attempted regional analysis;
- boundary support: geometry/band-size sufficiency under current tiers;
- background comparison reliability: texture/content and sampling adequacy;
- causal confidence: strength of a specific interpretation, not any of the above proxies.

No inconsistency follows solely from medium mask and boundary score 1.0. The problem is treating a geometry sufficiency proxy and boolean eligibility as comprehensive confidence inputs. `confidence_policy_inputs.py:20-46` carries the boolean, band score and `geometry_unreliable`, not the detailed medium-quality reasons or background baseline reliability. There is no automatic medium-quality cap; the policy admits high with usable geometry and a qualifying compound.

Background is about **14%**, 110,553 pixels at prepared geometry; subject is 678,951 pixels. Available samples are subject 96, boundary 64, background 128. These meet the asymmetry sampler's minimum count checks. Count sufficiency does not establish representativeness: the background is flagged highly repetitive, with baseline reliability **0.6** (`vf_subject_process_asymmetry.py:591-620`). The measured region-geometry rejection checks subject coverage < 0.08, not subject dominance (`:921-945`).

Important distinction: the asymmetry fallback's `subject_dominant` is based on **sample-count ratio** (`:954-961`), not foreground pixel area. Here 96/(96+128) is approximately 0.429, so the 86% pixel ratio alone does not prove that flag is true. Its appended note says weak background **or** subject dominance; a weak-background entropy condition can trigger that note. Do not infer the exact flag solely from prose when the compact summary omits it.

The asymmetry computation can lift comparative scores using subject-internal/reverse regularization when the background is weak (`:970-990`). A large, smooth or generated subject and a small repetitive background can show genuine differences without a separate edit. The measurements should remain visible with comparative applicability and baseline limitations. This audit does not justify an arbitrary area threshold, discarding medium masks, or equating all subject-dominant scenes with false positives.

## Score reconstruction and ancestry

The component ledger directly explains the requested values (`hypothesis_engine.compute_scorecard`, lines 394-609):

**Local support 5.25**:

`2.00 boundary-pattern + 1.00 cross-pattern + 0.35 medium subject-boundary + 0.35 moderate texture + 0.40 moderate asymmetry + 0.75 medium material - 0.20 camera + 0.60 medium boundary-stack synergy = 5.25`.

**Edit boost 2.295**:

`0.20 texture + 0.15 asymmetry + 0.40 material + 0.20 material/cross synergy + 0.40 subject-boundary/cross synergy + 0.18 * 5.25 local-support conversion = 2.295`.

**Clone support 2.10**:

`1.25 candidate + 0.50 patch score>=0.85 + 0.35 mean>=0.92 + 0.35 separated>=10 + 0.35 coverage<=0.18 + 0.15 cross/candidate + 0.05 boundary/candidate - 0.90 camera = 2.10`.

Patch candidate score 0.8915, mean 0.97944, max 0.99716, 270 separated pairs, 300 retained pairs and 0.1307 coverage establish strong similarity, not a particular reuse layout. The spatial stage uses 200 published pairs: 155 background-background, 24 cross-region bridges, 20 subject-subject and 1 boundary-boundary; boundary involvement 0.005, bridge fraction 0.13636 and subject density ratio 0.03119. No supported regional mechanism emerges. Relative to the region-specific question, this is not inconsistent with strong similarity among repeated structures elsewhere. The subset limit is explicit in `vf_patch_similarity.py:149-158`; `vf_patch_spatial.py` consumes those published pairs.

### Additional availability-state defect

`scorecard_integrity.py:21,43-55` excludes status `inconclusive` from active observations; `build_evidence_snapshot` (`hypothesis_engine.py:185-207`) filters through it. Thus TRACE `/evidence_snapshot/patch_spatial` is null, although the full section records successful spatial analysis with an inconclusive outcome.

`compute_scorecard` again filters evidence at `hypothesis_engine.py:340`. It later checks `ev.patch_spatial.pattern == spatial_patch_recurrence_inconclusive` (508-510), uses that flag for clone ambiguity (529-535) and intended -0.75/-0.60 dampings (555-572). Those checks cannot see this completed inconclusive result. The saved ledger contains neither damping and records `clone_ambiguous=false`. Missing evidence and a completed nonconfirming measurement have been conflated.

This does **not** authorize making missing data negative or blindly applying fixed penalties. The minimum repair is a separate complete outcome/applicability channel alongside positive scoring eligibility, followed by explicit review of how existing ambiguity predicates should consume it. It is a distinct defect from Task B's now-correct patch metric serialization.

### Shared ancestry is disclosed, not removed universally

Registry `evidence_lineage.py:109-128`: boundary and cross share ELA/luminance-residual ancestry; focus/alignment add regional localization; subject boundary adds intrinsic edge-ring features; texture/asymmetry share masked descriptors and geometry; material/asymmetry share feature-definition families; regional FFT contributes masked spectral features.

TRACE numerical allocation retains boundary 3.0 and cross 1.5 as additional interpretations, flags unresolved overlap, and retains related surface observations provisionally. The local support, synergies and edit conversion reuse these observations in named mechanism components. They are not independent experiments. Arithmetic is reconstructable, but multiple contributions are not empirical proof of multiple causes; the current deduplication policy does not establish optimal marginal weighting.

`boundary.compound_support` permits two eligible interpretations, here boundary plus intrinsic-edge subject boundary. `confidence.strong_source_diversity` instead sees boundary plus cross as one measurement-disjoint witness and fails. `synthetic.fft_patch_compound` fails because only FFT is a structured-generation pattern. These requirements intentionally answer different questions (`production_corroboration.py:78-161`). Their differing results are not themselves a bug. Structural ancestry is not statistical independence, even for distinct extraction IDs.

## Recommended bounded corrections

First repair strength-witness eligibility/provenance and preserve completed nonconfirming outcomes. Then separate anomaly support from person-boundary applicability and separate-edit mechanism support. Carry existing mask and background limitations to the interpretation layer rather than inventing universal penalties or caps. Preserve explicit counter-evidence and unrelated clone mechanisms. Evaluate detector recalibration only with a dedicated empirical dataset; it is not needed to demonstrate these state/semantic defects.
