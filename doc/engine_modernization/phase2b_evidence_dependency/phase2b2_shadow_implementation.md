# Phase 2B.2 — evidence lineage and marginal corroboration implementation

## Baseline and isolation

Branch remains `fix/scorecard-integrity-phase2a`, HEAD `f64f226` (`phase 1`).
Phase 2A and the Phase 2B.1 audit were inherited uncommitted. No branch was
created and no inherited work was staged, moved, discarded or folded into a
commit. Baseline suite: **184 passed, 0 failed, 0 skipped**.

An exact 61-file inherited snapshot and SHA-256 manifest are kept locally under
`analyzed/phase2b2_validation/inherited_baseline/`. Python copies end in
`.py.baseline` so pytest cannot collect them. The first baseline attempt exposed
duplicate test discovery before this suffix was corrected; an unprivileged run
then encountered the existing Windows temporary-directory restriction. The
properly permitted baseline run passed all 184 tests. These were verification
setup issues, not production regressions.

The isolated `analyzed/phase2b2_validation/phase2b2_only.patch` identifies this
phase's modifications relative to that snapshot, separately from Phase 2A.
Local generated outputs/snapshots remain ignored by Git. Prior audit reports,
inventories, graph, script and Phase 2A implementation are preserved.

## Audited architecture discrepancies resolved before implementation

- Regional FFT performs fresh masked-crop transforms with the same FFT analyzer;
  it does not consume global FFT results. The graph records shared feature code,
  rather than an invented serial detector dependency.
- Material realism independently samples metrics using asymmetry's feature
  helpers; it does not feed material results into asymmetry. Actual optional
  asymmetry inputs are subject texture and regional FFT.
- Cross and boundary interpretation consume a common ELA/residual overlap; a
  shared family does not make every child a pure restatement. Focus and alignment
  add localization, patch spatial adds topology, and asymmetry adds comparative
  measurements/interpretation.
- The executed region-segmentation morphology stage is not synthesized as a
  scoring section. The existing snapshot alias points at region masks. No new
  mask-morphology scoring path is activated.

These distinctions follow Phase 2B.1's actual code audit. They prevent the task's
illustrative dependencies from becoming fictitious production relationships.

## Added architecture

| File | Responsibility |
| --- | --- |
| `evidence_lineage.py` | Frozen records/enums, validated family registry, stable IDs, required/optional ancestry, finite-size JSON restoration |
| `marginal_corroboration.py` | Pure ancestry-ordered credit allocation, exact-restatement suppression, counter-evidence protection, explicit experimental credit parameters |
| `evidence_dependency_analysis.py` | Phase 2A ledger lineage, base-credit shadow reconstruction, family effects, gate diagnostics, fail-tolerant optional sidecar |
| `tests/test_evidence_lineage.py` | Structural, availability, cycle, determinism, serialization, allocation and production-invariance regressions |

Modified integration files are deliberately small:

- `decision_logic.synthesize_overall()` adds a keyword-only, default-false
  `evidence_dependency_shadow` option. The existing production evaluation and
  five-element return complete first; an optional sidecar is attached afterward.
- `summary_synthesizer.build_summary_result()` forwards the optional flag.
- `reasoning_persistence.build_reasoning_trace_text()` renders the optional
  diagnostic section and states that it assigns no confidence or decision.

`ScoreCard`, `EvidenceSnapshot`, production coefficients/aggregation and all
decision functions remain unchanged relative to Phase 2A. No detector, threshold,
mask, provenance-verification, dependency, GUI layout, build or workflow changed.

Example opt-in:

```python
result = synthesize_overall(sections, evidence_dependency_shadow=True)
diagnostic = result[4]["evidence_dependency_analysis"]

summary = build_summary_result(state, evidence_dependency_shadow=True)
```

No flag is set globally; existing GUI/controller callers continue to use the
authoritative production behavior. No expensive detector is rerun by the layer.

## Marginal allocation policy and numerical boundary

The default implements a structural rule, not an invented calibrated formula:

1. Retain supported primary base credits.
2. Withhold positive diagnostic base credits with unknown/missing required ancestry.
3. Suppress a registered pure restatement only when an already credited actual
   ancestor supplies the same measurements and hypothesis/target/polarity.
4. Preserve contradictory/moderating evidence in its hypothesis scope; shared
   ancestry alone does not erase it.
5. Record new localization, relationships or interpretation separately. Retain
   the existing base value provisionally, with numerical marginal value **null**
   and an explicit empirical-validation requirement.

No current audited detector is asserted to be a pure restatement with no added
information. Consequently the default reference shadow aggregates equal
production. Removing every composite would adopt the uncalibrated Phase 2B.1
ablation, which the task explicitly prohibits as a default replacement.
The layer supports exact structural deduplication (covered by constructed
tests) without inventing duplicate equivalence in real detectors.

An explicit `ExperimentalCredits` policy can vary supported suspicious base
credit units. The optional sidecar API exposes this for isolated experiments;
the production synthesis hook does not accept experimental allocations.
The audit-A experiment sets the existing downstream-composite base credits to
zero. It reproduces the prior numerical sensitivity, clearly labeled unvalidated,
without a shadow tier or hypothesis. No new coefficient or budget is hidden in
the default policy.

## Arithmetic and auditability

Existing final component terms and camera/floor/geometry/photo transforms are
read from `scorecard_calculation`. Shadow base status credits and domain bonuses
are reconstructed separately. Retained component operations carry exact source
references and stable rule IDs, but are not independently added a second time.

Family tables show existing/shadow base amounts and references to multi-family
component operations. Domain diversity credit remains its own accounting item.
Mixed-family operation references are not disjoint additive shares of final S;
nonlinear floors and moderation make naive per-detector totals misleading.

Known missing-mask penalties reference their reliability control even when the
mask itself provides no measured ancestry. Absence cannot create new positive
corroboration. Inconclusive parent interpretations can still have actual measured
features, which is necessary for the existing ELA/residual cross-signal pipeline.

Unknown future sections are marked unregistered with positive shadow base credit
withheld. Unknown operation aliases or unattributed positive operations mark the
sidecar partial, retaining explicitly legacy component arithmetic. Invalid
production cards produce no shadow score. Diagnostic exceptions yield an error
sidecar; they cannot alter the already completed production decision.

## Corroboration and wording

Diagnostics report weighted/supporting indicator counts, distinct feature
extraction IDs, shared ancestors, overlap groups, composites, missing parents and
single-family concentration. `independent_observation_count` is always null:
the graph does not estimate statistical independence. No alternative gate result
or replacement threshold is invented.

Reviewed gates include strong-signal confidence counts, boundary corroboration,
suspicious-domain diversity, FFT/patch and material/asymmetry synthetic
conjunctions, synthetic support from other domains and camera convergence.
The reference comparison records actual memberships and ancestry overlap.
Production gates are unchanged.

| Existing wording | Assessment | Recommended wording |
| --- | --- | --- |
| `signal_language` no-convergence label says “independent forensic signals” | Unsupported statistical independence adjective | “ELA and residual hotspot checks do not meaningfully overlap” |
| Boundary-focused “corroboration” | Corroborative but shared anomaly/mask ancestry | “Agreement among related boundary checks” with parent measurements named |
| “Multiple visual signals” in synthetic routes | Different interpretations/extractions, incremental value needs validation | “Related visual measurements show consistent structure; their incremental support is uncalibrated” |
| Declaration acts “independently of inconclusive localized editing” | Logical hypothesis scope separation, not statistical independence | “Without requiring a conclusive localized-editing result” |
| Rationale says outputs may be correlated and tiers are not probabilities | Accurate limitation | Retain |

No production wording was changed, preserving full text/HTML equality. These
recommendations remain separate from classification and confidence rules.

## Validation

Final suite: **232 passed, 0 failed, 0 skipped** — all original 184 plus 48 new
cases. Tests cover required scenarios including explicit contradiction roles,
five descendants of one measurement, registry/serialized cycles, missing parents,
unknown signals, immutable collections, no payload arrays, stable IDs/order,
repeated shared inputs, JSON restoration, experimental allocations, sidecar
errors and exact production trace equality. No test dependency was added.

Both actual references ran the full headless pipeline in `subject_based` mode.
Production scorecards, Phase 2A calculations, hypotheses, decision dictionaries,
rendered text and HTML were compared exactly. Read-only image hashes matched
before/after. Instagram completed 23 stages; Midjourney completed 14 with one
unavailable mask-selection stage and eight regional skips; both had zero errors
or failed stages. Full details are in [phase2b2_reference_comparison.md](phase2b2_reference_comparison.md).

Warm pure-sidecar overhead was measured externally over 30 calls per reference,
approximately 0.5–0.6 ms median on this machine. It includes no detector work;
it is not a hardware-independent performance guarantee. Timings are excluded
from deterministic sidecar JSON.

## Activation recommendation

Keep production scoring authoritative. The structural rule is implemented and
auditable, but real child localization/interpretation weights and gate reliability
remain uncalibrated. See [phase2b2_activation_criteria.md](phase2b2_activation_criteria.md).
Do not apply existing confidence thresholds to experimental scores.

No staging, commits, pushes, merges, tags, stashes, resets or publication were
performed. Reference outputs and baseline snapshots remain ignored; no image
was modified or added to Git.
