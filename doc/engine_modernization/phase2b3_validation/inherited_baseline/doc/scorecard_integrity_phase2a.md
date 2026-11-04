# Phase 2A: scorecard mathematical integrity

## Committed baseline and inspection

Started from clean commit `f64f226` (`phase 1`) on
`fix/reasoning-correctness-phase1`; created `fix/scorecard-integrity-phase2a`.
The baseline suite passed: 121 passed, 0 failed, 0 skipped. No inherited work
was staged, stashed, discarded or moved.

Before implementation, inspection found this calculation sequence:

1. Status/polarity weights plus domain bonuses form the separate base totals.
2. Camera counter-support, local/edit/clone/synthetic/provenance/sensor/compression
   contributions and context cautions are accumulated.
3. The suspicious subtotal is camera-attenuated, caution is subtracted and the
   total is floored at zero.
4. Unreliable geometry then changes local/edit components, multiplies the already
   finalized suspicious total, and adds another caution.
5. Boundary reliability then changes local/edit components and adds another
   caution without recomputing the total.
6. `build_decision_env()` can add a photo-context camera bonus and caution, and
   multiply the already finalized total again.

The serialized components therefore do not describe the values that generated
the final total. A separate absence defect awards 0.35 clone compactness support
when missing patch coverage defaults to zero. Derived pattern flags can also
activate from unavailable or inconclusive sections because status is not checked
consistently outside base scoring.

## Scorecard API and consumers

`compute_base_scores(sections)` returns suspicious total, benign total and two
domain sets. `compute_scorecard(sections, context, evidence, derived)` returns a
fresh `ScoreCard`. `build_decision_env()` is the production bridge to routing.
The decision routes consume aggregate totals, mechanism support, boosts,
camera/caution values and boolean flags. Trace serialization and the GUI/text
trace expose scorecard values; summary/HTML builders use the resulting decision.
Confidence rationale already uses hypothesis-scoped explanations rather than
recalculating scores. The historical text-trace fallback still interprets old
score fields for legacy traces.

| Fields | Existing mathematical meaning / range |
| --- | --- |
| `suspicious_score` | Nonnegative, unbounded aggregate after attenuation, penalties and floor; routed and traced |
| `benign_score` | Nonnegative, unbounded status/domain sum; independent of suspicious attenuation; routed and traced |
| `local_edit_support_score` | Signed net local support: positive observations less explicit camera tempering, then reliability; routed and traced |
| `edit_boost` | Signed net edit contribution, including 0.18 times net local support, then reliability; routed and traced |
| `clone_support_score` | Nonnegative, unbounded patch mechanism support after metadata damping and zero floor; routed and traced |
| `synthetic_boost` | Nonnegative synthetic-structure contribution after existing context multipliers; routed and traced |
| `provenance_boost` | Nonnegative existing declaration/OSINT contribution; routed and traced |
| `sensor_boost`, `compression_boost` | Nonnegative mechanism corroboration contributions; aggregated and traced |
| `caution_penalty` | Nonnegative sum of distinct existing caution terms; not a probability |
| `camera_counter_support` | Nonnegative measured camera support plus the existing optional context-prior routing bonus |
| `suspicious_domains`, `benign_domains` | Nonempty domain identifiers from available weighted sections only |

Local support/edit can legitimately be negative: the existing model explicitly
subtracts 0.20 per camera signal even when no local concern is present. These
signed net values are not arbitrarily clipped to make a field named "boost"
positive. Aggregate suspicious and clone scores retain their existing zero floor.

## Implementation boundaries

Move reliability adjustments and cautions before final aggregation, with a
single aggregation point. Preserve each existing coefficient. Preserve the
measured-camera attenuation, geometry aggregate attenuation and photo-context
attenuation as distinct documented operations. Measured camera caution and the
separate photo-context caution remain separate terms; the context's routing
bonus is not silently counted a second time as measured camera evidence.

Record raw components, final components, caution terms, multipliers and operation
order so that serialized aggregates can be reconstructed. Pure computation and
validation should reject invalid numeric states clearly; production synthesis
should withhold a forensic conclusion and report an explicit invalid scorecard.

Unavailable and inconclusive observations must not activate weighted domains or
mechanism bonuses. Legitimate zero-valued measurements remain distinct from
missing values. No detection thresholds, score coefficients, confidence tiers,
route priorities, hypothesis selection rules or dependence policy are retuned.

## Implemented corrections and changed files

| File | Change |
| --- | --- |
| `hypothesis_engine.py` | Availability-aware inputs, fresh per-call ledger, reliability before aggregation, centralized photo prior, validation before returning a card |
| `scorecard_integrity.py` (new) | Finite-input contracts, operation replay, independent reconstruction helper, pure consistency validator |
| `decision_logic.py` | Removes late scorecard mutations; adds calculation trace and conservative invalid-card handling; sanitizes non-finite diagnostic values for JSON |
| `hypothesis_evidence.py` | Prevents unavailable observations from reappearing as supporting hypothesis evidence |
| `reasoning_persistence.py` | Renders the new calculation section while retaining legacy-trace support |
| `tests/test_scorecard_integrity.py` (new) | Mathematical, availability, determinism, validation, serialization and reference-fixture regressions |
| `doc/scorecard_integrity_phase2a.md` (new) | This audit and validation report |

The final formula uses adjusted contributions:

```text
Q = base_suspicious + synthetic_boost + edit_boost + provenance_boost
    + sensor_boost + compression_boost
S = max(0, Q * camera_multiplier - final_caution)
    * geometry_multiplier * photo_context_multiplier
B = base_benign
```

Base totals retain status weights weak=0.5, medium=1.5, strong=3.0 and
0.25 per additional distinct domain. Camera attenuation uses measured support:
1.0 below 1, 0.85 from 1, 0.70 from 2, 0.55 from 3. Geometry applies 0.45
once to local/edit components, adds caution 1, and retains its separate 0.75
aggregate factor. Applicable boundary reliability multiplies local/edit once
and adds `1-r` caution. It is applicable when raw local or edit support is
positive; an absent mechanism alone does not justify a missing-sensor penalty.
The photo prior retains its separate 0.70 aggregate factor, routing camera bonus
1.5 and caution 1.0. Its routing bonus is not measured camera evidence.

The existing clone zero floor, suspicious zero floor, camera convergence bonus,
within-mechanism moderation and context attenuation remain. Local/clone scores
are mechanism indicators; they are not additional terms to add directly to Q.
No upper aggregate cap or probability interpretation has been introduced.

## Before and after arithmetic examples

1. **Boundary ordering.** With base 6.25, raw edit 0.54 and r=0.75, the old
   aggregate stayed 6.79 even though reported edit became 0.405 and caution
   became 0.25. It is now `6.25 + 0.405 - 0.25 = 6.405`. At r=0, the
   corrected result is `6.25 + 0 - 1 = 5.25`.
2. **Multiple reliability adjustments.** Adding unreliable geometry to that
   example formerly left `(6.25 + 0.54) * 0.75 = 5.0925`, with later
   component/caution changes omitted. The corrected result is
   `(6.25 + 0.54 * 0.45 * 0.75 - 1.25) * 0.75 = 3.8866875`.
   The component attenuation and aggregate geometry factor are distinct
   preserved policy operations, not accidental duplicate multipliers.
3. **Photo-context mutation.** With the same geometry/boundary example and
   camera metadata plus smartphone context, measured camera support is 1.5,
   final routing support is 3.0, camera multiplier remains 0.85, and final
   caution is `1.5 + 0.4 + 1 + 1 + 0.25 = 4.15`. The corrected aggregate is
   `max(0, (6.25 + 0.54 * 0.45 * 0.75) * 0.85 - 4.15) * 0.75 * 0.70`
   `= 0.6916415625`. Previously it was
   `((6.25 + 0.54) * 0.85 - 1.9) * 0.75 * 0.70 = 2.0325375`;
   the late cautions and adjusted edit did not participate. The environment now receives precisely the
   card computed by the pure calculator, without mutating it again.
4. **Missing patch evidence.** Previously a missing patch object defaulted
   coverage to zero and received 0.35 compactness support. It now receives
   zero. A present observation with missing/null coverage gets no compactness
   bonus either; a genuinely measured zero retains the existing 0.35 policy.
5. **Missing observation versus uncertainty.** An empty input previously
   acquired boundary caution 1 because reliability defaulted to zero, despite
   having no local mechanism. It now has all components and aggregates zero.
   Unavailable/inconclusive camera or synthetic patterns likewise cannot
   activate boosts, domain counts, routing patterns or positive hypothesis
   evidence. Weak observations retain their existing status weight. Null
   optional numeric scores do not erase a valid qualitative observation.
6. **Invalid numbers.** Active NaN/infinity or invalid status/context/range
   values formerly could contaminate comparisons and JSON. Pure calculation
   now raises `ScorecardIntegrityError`. Production returns an explicitly
   invalid scorecard, neutral Inconclusive decision and withheld assessments.
   Its default numeric fields are non-assessment placeholders, not repaired
   evidence. Trace errors identify the invalid input; non-finite diagnostic
   values serialize as null. Stale numbers on unavailable observations do not
   invalidate independent usable evidence.

## Full reference-image validation

Both images were read without modification and rerun through the full headless
pipeline in `subject_based` mode. Before values come from the committed Phase
1.2 validation artifacts. After values are actual pipeline outputs, not frozen
decision-fixture scores.

| Metric | Instagram before | Instagram after | Midjourney before | Midjourney after |
| --- | --- | --- | --- | --- |
| Suspicious score | 20.47705 | 20.47705 | 7.6614 | 6.0375 |
| Benign score | 2.25 | 2.25 | 1.5 | 1.5 |
| Edit boost (reported final) | 1.823 | 1.823 | 0 | 0 |
| Caution penalty (reported final) | 1.6 | 1.6 | 2.25 | 2.25 |
| Final pattern | possible_foreground_background_processing_mismatch | possible_foreground_background_processing_mismatch | provenance_supported_synthetic_context | provenance_supported_synthetic_context |
| Confidence tier | High | High | Medium | Medium |
| Completed stages | 23 | 23 | 14 | 14 |
| Unavailable/skipped stages | 0 | 0 | 9 | 9 |
| Failed stages | 0 | 0 | 0 | 0 |

Instagram reconciles as `(23 + 0.4 + 1.823 + 0.75) * 0.85 - 1.6 = 20.47705`.
Its mask remains reliable at coverage 0.5961422390407987; all expected stages
run. Midjourney's mask remains rejected at coverage 0.9181777419747081 under
the unchanged 0.90 maximum. Eight regional forensic stages and region selection
remain unavailable; cross-signal still succeeds independently. Its generation
declaration remains unverified provenance, not authenticated origin.

Midjourney has base 9, raw edit 0.734, provenance 0.75, measured camera 1.25,
camera multiplier 0.85 and raw caution 1.25. Boundary reliability is zero:
final local/edit become zero and final caution becomes 2.25. The old aggregate
used the stale raw values: `(9 + 0.734 + 0.75) * 0.85 - 1.25 = 7.6614`.
It now uses final values: `(9 + 0 + 0.75) * 0.85 - 2.25 = 6.0375`.
The entire reduction, 1.6239, is `0.734 * 0.85 + 1`; no threshold was tuned.

Artifacts are under `analyzed/phase2a_validation/{instagram,midjourney}/`:
`before_scorecard.json`, `validation_result.json`, `console.txt`, and
`summary/reasoning_trace.json` / `summary/reasoning_trace.txt`. These generated
outputs are ignored by Git. Both runs report no stage errors and successful
serialized arithmetic reconstruction.

## Tests, auditability and compatibility

Final automated suite: **184 passed, 0 failed, 0 skipped**, including all
121 original tests and 63 new mathematical cases. A seeded generated test
additionally checks 250 evidence combinations. Hypothesis is not installed;
no dependency was added. Coverage includes full/reduced/zero reliability,
multiple adjustments, missing/null/inconclusive/weak inputs, genuine zero,
non-finite input, camera factor boundaries, zero floors, signed contributions,
repeated shared-input evaluation, insertion order, tampered calculations,
strict JSON round trips and recomputed Instagram/Midjourney fixtures.

The trace's top-level `scorecard_calculation` is version `2a`. It records
weighted base evidence/domain accounting, ordered component operations, the
raw-operation boundary, raw/final snapshots, reliability applicability,
penalties, nonlinear aggregate transforms and final totals. Each operation has
an operand and a reason. The calculation is stored once, outside the existing
scorecard object; existing scorecard fields remain available.

`reconstruct_scorecard_calculation()` replays serialized operations without
detectors or a live scorecard. `validate_scorecard()` checks component/base/
domain/aggregate reconciliation, finite values, defined nonnegative ranges,
multiplier bounds and single application of reliability and prior adjustments.
Tests also implement a separate reconstruction without production calculator
or replay calls. Both actual image traces reconstruct every numeric component
and aggregate within `math.isclose(rel_tol=1e-12, abs_tol=1e-12)`. This tolerance
allows floating-point accumulation noise while rejecting meaningful arithmetic
disagreement; scores are not rounded during calculation.

The five-element synthesis API, hypothesis structure, legacy trace rendering,
controller and summary integration remain compatible. Core/controller/summary
imports pass. AST comparisons verify route functions, route registry/order and
confidence threshold logic are unchanged. Existing decision-only fixtures that
manually override card values remain supported; the new math fixtures recompute
real cards. Production cards are validated before routing. No detector, mask
threshold, dependency, GUI, packaging or workflow file changed.

## Deferred policy questions (Phase 2B)

- Correlated ELA/boundary/cross-signal and base/boost evidence may deserve a
  dependence model. Existing intentional aggregation is preserved here.
- Aggregate magnitudes and coefficients are not calibrated probabilities;
  the measured-zero compactness bonus and signed local/edit semantics remain
  explicit existing policy questions.
- Confidence tiers need separate empirical calibration; unchanged tiers on
  these references do not establish broader accuracy.
- Metadata declarations remain unauthenticated; verification needs independent
  provenance evidence.
- Segmentation reliability remains governed by the existing quality contract
  and 90% coverage limit. Numerical integrity does not establish mask accuracy.

## Final Git state

Branch: `fix/scorecard-integrity-phase2a`, based on committed `f64f226`.
Four tracked files modified: `decision_logic.py`, `hypothesis_engine.py`,
`hypothesis_evidence.py`, `reasoning_persistence.py`. Three untracked source/
report files: `scorecard_integrity.py`, `tests/test_scorecard_integrity.py`,
`doc/scorecard_integrity_phase2a.md`. Nothing staged; `git diff --check` passes.
No files under `test_images/` changed. No commit, push, merge, tag or publication.
