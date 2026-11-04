# Phase 2B.2 — bounded dependency-management proposal

This document proposes future work. No approach below has been implemented or
empirically calibrated. Existing Phase 2A behavior remains the reference.

## Four candidate approaches

| Approach | Complexity / explainability | Current-scorecard fit | Overconfidence resistance | Data requirement | Sensitivity / deterministic suitability |
| --- | --- | --- | --- | --- | --- |
| A. Evidence-family grouping and caps | Low–medium; simple family budgets and transparent saturation | Add a family aggregation stage before final Q; must reconcile base, boosts and domain credit together | Limits repeated children, but a bad grouping can still conflate unrelated mechanisms | Labels needed to choose/validate budgets; code can establish lineage before fitting | May suppress real weak signals that combine meaningfully; highly deterministic with fixed budgets |
| B. Marginal corroboration | Medium; distinguish primary observations from added location/topology information | Keep direct observations; downstream cross/focus/alignment/spatial evidence earns explicit incremental credit rather than another full independent base | Directly addresses known reuse; incremental value must not simply be asserted | Conditional ablations and labels needed to set increments; do not guess them from two references | Can preserve localization sensitivity better than broad caps; deterministic after policy is frozen |
| C. Dependency-aware allocation on a graph | Medium–high; audit paths are clear but multi-parent allocation rules can become opaque | Allocate credit across source observations and transformations; make shared-parent attribution explicit in versioned trace | Can prevent ancestor/descendant credit inflation; graph incompleteness remains a risk | Labeled data plus validation of graph attribution; code graph alone cannot determine evidence value | May create fragile order/path effects unless tested; deterministic DAG traversal feasible, avoid treating graph edges as statistical probabilities |
| D. Empirically calibrated weighting | High initial data/maintenance cost; coefficients or constrained models can remain explainable | Replace heuristic weights or add a calibrated hypothesis layer; preserve raw evidence and provenance separation | Can learn dependencies only where data cover them; vulnerable to dataset shortcuts and drift | Substantial labeled, lineage-controlled development/calibration/test data; external held-out groups | Potentially better sensitivity/specificity but no guarantee; inference can remain deterministic with fixed versions |

Preferred sequence: **B with a small explicit lineage registry, protected by A's
family budgets**, first in shadow mode. Use C's graph for attribution/audit,
without inventing a probabilistic causal model. Evaluate D once adequate labels
exist. Shared code or image pixels alone are too broad a criterion for rejecting
evidence: the policy should recognize useful spatial localization and different
measurement channels, while preventing relabeling the same observation as
independent confirmation.

Initial families should distinguish provenance assertions, processing/residual
anomalies, spectral periodicity, recurrence/material regularity, acquisition
structure, compression history and geometry/coverage. These are **candidate**
groups, not calibrated independent factors. Multi-parent evidence may refer to
more than one family; do not duplicate its full credit in each. Mask geometry
should normally modify reliability and coverage, not act as independent proof
of image generation.

## Correctness work versus statistical policy

| Category | Proposed work | Boundary |
| --- | --- | --- |
| Mandatory contract correctness | Make status availability consistent in `determine_confidence` and raw-section corroboration helpers; test stale unavailable patterns, while preserving legitimate weak observations | Demonstrable input-contract inconsistency; no weight tuning required |
| Mandatory audit correctness | Store immutable evidence IDs, source-family ancestry, transformation IDs and units; explain multi-role reuse explicitly; remove unsupported independence wording | Can be introduced without changing scores; lineage metadata is descriptive |
| Mandatory integration decision/documentation | Resolve whether the executed region-segmentation stage is diagnostic only; correct/document the `region_segmentation` snapshot alias | Do not silently connect unused scoring branches; activation would be an optional new scoring policy |
| Mandatory feature-contract review | Separate boundary focus numeric measurements from display artifacts and document units; test coordinate and empty-mask behavior | Prefer authoritative numeric maps; changing map source may change outputs and requires detector-equivalence review |
| Optional statistical improvement | Family budgets, representative weights, marginal bonuses and dependence-aware gating | Requires benchmark selection and confidence recalibration; do not label as arithmetic repair |
| Optional reliability-policy change | Change whether r=0 also discounts base cross/boundary evidence, or change subject-only fallback rules | Current reliability scope is explicit; changing it is model policy |
| Optional geometric validation | Validate intrinsic image-edge bands against actual person contours before a subject-specific claim | Requires geometric benchmark evidence and potential detector/interpretation changes |

Independent correctness changes should be reviewed separately from a new scoring
formula, so a useful availability fix does not implicitly authorize weight or
confidence changes. “Mandatory” here means necessary to satisfy the intended
contracts in the next approved task, not permission to implement them in this
audit.

## Bounded implementation plan

1. **Freeze and identify the baseline.** Commit/review Phase 2A through the normal
   user-controlled workflow before a future implementation branch. Preserve the
   184 tests and reference traces. Version every new policy independently.
2. **Descriptive registry only.** Add a small module such as `evidence_lineage.py`
   with stable observation IDs, feature families, parent IDs, geometry source,
   units and transformation role (direct/localization/composite/context). Avoid
   copying arrays. `summary_sections.py` attaches source IDs;
   `summary_synthesizer.py` records masks/preprocessing lineage and availability.
   Same declaration signals should share an assertion family rather than claim
   independent origin verification.
3. **Shadow allocation.** `hypothesis_engine.py` and `scorecard_integrity.py`
   retain current production totals and produce an optional dependency audit
   alongside them. Trace direct base, repeated base, domain credit, incremental
   localization, synergies and cautions separately. Do not subtract an aggregate
   and its upstream local intermediate twice. Preserve signed local/edit
   semantics, camera attenuation order and calculation replay.
4. **Pre-register candidate policies.** Evaluate a small number of family caps
   and marginal-child-credit choices on development data only. Specify parent
   availability behavior: a child cannot invent missing raw evidence; valid
   localization can remain useful even when a global summary was inconclusive.
   Attribute multi-parent terms once, using a documented allocation convention.
   Do not choose values to recover the Instagram/Midjourney tiers.
5. **Dependency-aware route review.** In `decision_logic.py`, avoid counting
   cross+boundary as two independent mechanisms; treat focus/alignment as added
   location evidence. Replace heterogeneous maximum-score comparisons with
   typed, separately validated support gates if justified. Evaluate synthetic
   material/asymmetry conjunctions similarly. This changes selection behavior
   and needs explicit approval as a model revision, not a documentation fix.
6. **Explanation and persistence.** In `hypothesis_evidence.py`,
   `reasoning_persistence.py`, `signal_language.py` and
   `decision_logic.build_confidence_rationale`, expose “same processing family;
   added spatial localization” and report coverage. Separate logical hypothesis
   scope from statistical independence. Count evidence families descriptively,
   never label a count a probability.
7. **Validate before activation.** A candidate can become the default only after
   held-out evaluation of sensitivity, false positives and tier reliability,
   including metadata-blind analysis. Keep old/new policy outputs comparable by
   explicit version, not by applying old score thresholds to a new formula.

Suggested affected files are bounded to the reasoning/section/persistence
modules above, one small lineage registry, focused tests and documentation.
Detector thresholds, GUI layout, dependencies, packaging and workflows remain
outside this proposal unless a separately scoped feature-contract fix is
approved. No graph library or statistical dependency is required for the
descriptive/shadow phase.

## Test strategy

- Preserve all current tests, including Phase 2A's finite arithmetic and ledger
  replay checks. Extend exact serialized reconstruction to allocated credits,
  domain/family bonuses and suppressed duplicate paths.
- Test all parent/child combinations: ELA/residual summaries neutral but valid
  raw maps; unavailable parent; child-only synthetic fixture; malformed ancestry;
  duplicate evidence IDs; multi-parent credit; genuine additional localization.
- Test shared-input repetition and insertion-order invariance, graph acyclicity,
  stable IDs and identical totals across trace serialization.
- Assert that duplicate reporting identifiers do not manufacture numerical
  contributions, and multi-role cautions have documented separate effects.
- Test availability contracts for every raw-section consumer, missing metadata,
  optional OSINT and all reliability levels. An absent modality must not become
  either authenticity or generation support.
- Test boundaries between different units; a raw intensity boost must not be
  interpreted as a normalized likelihood. Test overlapping person masks and
  intrinsic edge bands without assuming they coincide.
- Add metamorphic image checks using known transformations, evaluated as
  controlled cohorts rather than invariance promises: recompression, resize,
  crop, sharpen, blur, denoise, local insertion and metadata swaps.
- Treat reference images as regression/debug examples only. No mandatory target
  score or tier under a newly calibrated policy. Document every behavioral
  difference by lineage and changed policy.

## Proposed empirical benchmark

No sufficient labeled dataset is available in this workspace; empirical results
are pending. The two existing examples are inadequate for correlation, accuracy
or calibration claims. The following is a collection/evaluation design, not a
claim about datasets already obtained.

| Cohort | Required variation and ground truth |
| --- | --- |
| Authentic camera photographs | Multiple physical camera units/models, lenses, ISO/exposure, scenes and raw-to-JPEG pipelines; retained originals and acquisition records |
| Smartphone computational photography | HDR, portrait blur, multi-frame denoise, night mode, beauty/smoothing and sharpening; process flags recorded |
| Social-media photographs | Known authentic roots with controlled platform recompression/resizing/crops and repeated upload generations |
| Conventional edits | Global color/exposure plus local retouching, compositing, copy-move and background replacement; masks and operation histories |
| AI-enhanced photographs | Denoise, upscale, restoration and generative fill with original roots, tools/versions and edited-region masks |
| Fully generated images | Multiple generator families/versions and prompt/content styles; original generation records, outputs and seeds where available |
| Local synthetic insertion | Camera-base images with synthetic replacements/inserts; masks and proportion of changed area, blended boundaries and recompression |
| Explicit generation metadata | Verified process label retained; authentic embedded workflow/source declarations varied independently of content |
| Stripped metadata | Matched content pairs with metadata removed without pixel changes; absence is a coverage condition |
| Forged/misleading metadata | Controlled swaps/additions including camera fields on generated content and declarations on camera images; declared versus known origin kept separate |

Labels are multi-axis: acquisition origin, local-edit mechanism/location,
AI enhancement, whole-image generation, processing history and provenance
authenticity. A conventional edited photograph is not a negative example of
localized editing and a generated image is not automatically evidence of a
specific local edit. Annotators should have access to generation/edit records;
ambiguous web images remain an uncertainty cohort, not definitive ground truth.

Use source-root grouping: all edits/recompressions/metadata variants/crops from
one root stay in one split. Group bursts, near-duplicates, prompt/seed families,
source sessions and recurring subjects/scenes where feasible. Deduplicate by
pixel/near-duplicate fingerprints and review borderline matches. Split by camera
unit/model, generator/version, platform and tool family for external robustness
tests; keep a generator/version completely unseen where feasible. Record
provenance of every sample and license/consent constraints. Fit candidate
policies only on development data; calibrate on a distinct partition; evaluate
once on untouched held-out groups. Bootstrap intervals by source group, not by
derived image count. Avoid treating hundreds of recompressions of one photo as
hundreds of independent observations.

Measure outputs at both feature and decision levels:

- Conditional joint rates and residual correlations within each origin/process/
  resolution/compression cohort; separate availability from observed zeros.
  Correlation alone does not prove forensic redundancy; compare incremental
  predictive value of child information given parents.
- False-positive rate and true-positive rate per hypothesis/cohort, precision/
  recall with the evaluation prevalence reported, and uncertainty intervals.
- Tier reliability: fraction of High/Medium/Low conclusions supported by known
  mechanism labels, with denominators and coverage/abstention rates. Scores are
  not probabilities; calibration error/Brier/reliability plots become appropriate
  only after explicit probabilistic predictions are introduced and calibrated.
- Paired ablation sensitivity, per-generator/camera/platform robustness,
  localization accuracy when masks are available, and changes under recompression,
  resizing and blur. Report both favorable and adverse changes.
- Content-only versus metadata-only versus combined performance. Randomize or
  swap metadata in controlled pairs to expose provenance shortcuts. Keep
  unverified declarations and cryptographically authenticated provenance distinct.
- Segmentation coverage and mask accuracy separately, stratified by person size,
  pose, clothing, background complexity, generator and acquisition process. Score
  reliable and rejected masks without using missing regional evidence as a label.

Sample sizes should follow pre-specified error tolerances and cohort analyses.
Zero observed false positives must not be presented as zero population risk.
Design for the desired uncertainty bound before collection, account for source
grouping, and report when a cohort is underpowered.

## Acceptance, risks and rollback

Shadow deployment must leave production results byte-equivalent in relevant
decision fields, except separately approved contract corrections. Gate activation
on pre-registered cohort metrics and coverage requirements; choose tolerances
with the stakeholder before examining held-out results. Retain a versioned
legacy policy and reproducible traces. Do not rewrite prior saved results.

Stop or roll back if arithmetic no longer reconstructs, duplicate IDs earn
additional credit, evaluation becomes order-dependent, missing evidence changes
polarity, a child silently substitutes for an unavailable parent, or routing
loses source-family explanation. For a candidate statistical policy, roll back
if held-out false positives exceed the agreed limit, sensitivity loss exceeds
the agreed budget, confidence tiers become less reliable, or generator/platform
performance is dominated by metadata or compression shortcuts. These limits
remain to be set; none are invented from the two references.

The core tradeoff is explicit: reducing redundant support can reduce false
confidence, but broad caps can also remove useful localized information. A
deterministic, inspectable system still needs empirical validation of that
tradeoff. No Phase 2B.2 production implementation is authorized by this audit.
