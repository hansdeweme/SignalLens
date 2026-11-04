# Phase 3 confidence-policy implementation report

## Baseline and isolation

Branch `fix/scorecard-integrity-phase2a`, HEAD `f64f226` (`phase 1`). Inherited
Phase 2A-2B.3 work remained uncommitted. Baseline: **262 passed, 0 failed,
0 skipped**. An exact 75-file inherited snapshot and SHA-256 manifest were
preserved under ignored `analyzed/phase3_validation/inherited_baseline/`;
Python copies use `.py.baseline` suffixes. No branch, stage, commit, stash, reset
or discard was performed.

`analyzed/phase3_validation/phase3_only.patch` isolates this phase from inherited
work. Previous audit reports and production lineage/shadow/corroboration modules
are preserved. `test_images/` remains ignored and was only read.

## Inventory and migration

The audit covered **26 route-return assignments, four generic branches and five
hypothesis construction/override paths**, plus invalid/default placeholders and
presentation consumers. All authoritative final assignments are now centralized.
The 26 provisional route tiers remain for compatibility and diagnostics only;
the five construction paths now create placeholders resolved by policy.

See [confidence_rule_inventory.md](confidence_rule_inventory.md) for baseline
functions, evidence conditions, proposed/implemented equivalents and qualifiers.
Measurement confidence in ExifTool or person-mask detectors is separate metadata
and was not treated as forensic hypothesis confidence.

## Changed files

| File | Responsibility |
| --- | --- |
| `confidence_policy.py` (new) | Frozen structured inputs/results, typed finding specificity, named hypothesis-specific policy rules, centralized existing generic thresholds |
| `confidence_policy_inputs.py` (new) | Read-only adapter from existing card/derived/corroboration/coverage data; no loose narrative interpretation or detector execution |
| `decision_logic.py` | Typed finding claims on 26 route returns; confidence-independent selection; policy after evidence scoping; authoritative presentation and route-trace audit |
| `hypothesis_engine.py` | Additive policy-rule/rationale fields on HypothesisAssessment only; mathematical functions unchanged |
| `summary_synthesizer.py` | Supply coverage before confidence and remove independent post-policy limitation mutation |
| `reasoning_persistence.py` | Render policy version, rules, rationale and limitations alongside existing traces |
| `tests/test_confidence_policy.py` (new) | 35 policy and complete integration regressions |
| Four documents in this directory | Inventory, semantics/specification, implementation and actual reference comparison |

## Architecture

1. Existing detectors, summaries, scorecard and corroboration produce observations.
2. Matching routes produce typed finding claims and provisional compatibility data.
3. Existing deterministic hypothesis selection uses typed specificity instead of
   checking a route's High/Medium label. Route priorities, specificity meanings
   and boundary-versus-clone safeguards remain intact.
4. Existing evidence scoping populates supporting/contradicting/moderating/
   contextual records for each hypothesis.
5. The pure policy consumes immutable snapshots and assigns each assessment a
   tier, stable rule, scoped evidence, limitations and rationale.
6. Final results, route-trace authoritative tiers and presentation consume that
   policy. The primary interpretation is not reselected by maximum confidence.

Route names, branch strings, prose and provisional confidence do not enter the
policy inputs. All matching typed findings are consolidated independent of
evaluation order. Unknown hypotheses/findings cannot use a legacy High label to
create a confident interpretation. Presentation restores policy tiers even if
an external caller mutates a provisional result or an assessment tier afterward.

## Meaningful behavior changes

- A general anomaly route no longer bypasses the existing 2B.3 source-diversity
  policy by hardcoding High. A saved baseline-module replay confirms High ->
  Medium at unchanged S=8.155, B=0 for two related boundary/cross descendants.
  The primary pattern remains `multi_signal_suspicious_convergence`; the named
  rule is `generic.one_strong_observation`.
- Required person-boundary reliability is enforced by policy even if a caller
  supplies a route subset omitting safeguard routes. The existing 0.6 boundary
  requirement and reliable-person/geometry contract are reused, not recalibrated.
- Policy, hypothesis and decision coverage limitations are produced together,
  eliminating independent after-the-fact mutation by summary orchestration.

There is no global contradiction penalty. Existing direct counter-evidence
remains visible, while valid alternative compound/reuse support can retain its
existing tier. Unverified declarations remain Medium and camera-compatible
structure remains compatibility rather than authentication. A typed future
verified-assertion result has a distinct rule/rationale but does not invent a
High pixel-origin guarantee from signature authenticity alone.

## Compatibility and invariants

- Five-element synthesis return API preserved; existing positional parameters
  remain. Coverage is an optional keyword-only input.
- Existing JSON fields retained. New fields are policy audit, assessment
  rule/rationale and route-trace legacy/source data.
- All new authoritative tiers have named rules. Secondary assessments are
  evaluated separately; no cross-hypothesis confidence transfer.
- Numerical scorecard functions, coefficients, reliability multipliers and
  detector thresholds are unchanged. HypothesisAssessment adds two defaulted
  fields without changing ScoreCard or EvidenceSnapshot contracts.
- Phase 2B.2 modules/policy and Phase 2B.3 corroboration helper remain unchanged.
  Full reference sidecars and corroboration audit records match baseline JSON.
- Current GUI/controller integration is unchanged. Full text/HTML consume the
  policy's primary tier and existing evidence presentation.
- No new dependencies, packaging or workflow changes.

## Tests and real-image validation

Final suite: **297 passed, 0 failed, 0 skipped**, including all original 262 and
35 new tests. Coverage includes unverified/typed verified provenance, forged
verification flags, missing metadata, local-versus-generation scope, camera
coexistence, reliability caps independent of route presence, contradictions,
moderation, coverage, descendant source inflation, distinct sources, reordered
routes, repeated evaluation, tier tampering, non-maximum primary selection,
JSON/text/HTML consistency and numerical/shadow/corroboration invariants.

Both actual references completed full headless `subject_based` pipelines with
zero failed stages and unchanged read-only image hashes. Instagram remains High
at S=20.47705/B=2.25 under `localized.reliable_boundary_compound`; Midjourney
remains Medium at S=6.0375/B=1.5 under
`synthetic.unverified_generation_declaration`. The latter keeps rejected person
geometry and partial regional coverage. These are validation examples, not a
calibration dataset. See [confidence_policy_reference_comparison.md](confidence_policy_reference_comparison.md).

## Remaining limitations

The policy consolidates existing heuristic meanings; it does not statistically
calibrate tiers, independence or probabilities. Compound rule thresholds and
correlated numerical weighting still need a representative labeled benchmark.
Verified provenance integration remains outside this phase because the current
extractor has no cryptographic validator; metadata flags are never promoted to
verification.

Existing structured mechanism scores remain trusted policy inputs, including
legacy programmatic callers that inject scorecard values for decision-only
fixtures. The policy does not rerun detectors or reinterpret such overrides as
new measured observations. Normal production scorecards retain Phase 2A's
finite/reconstructable calculation contract. Partial input coverage is recorded
without inventing evidence or replacing established mechanism rules with new
global thresholds.

No required Phase 3 functionality is deferred: final confidence authority,
hypothesis separation, typed selection, rationale and policy audit are integrated
and tested. Empirical calibration, cryptographic validation and numerical
dependency weighting remain separate scope limitations, not hidden policy rules.

Nothing was staged, committed, pushed, merged, tagged, stashed, reset or discarded.
