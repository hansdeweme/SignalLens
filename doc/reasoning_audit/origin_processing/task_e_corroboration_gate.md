# Task E: corroboration gate transparency and consistency

2026-11-08. Bounded diagnostic implementation on `main`, HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`. Task D and other inherited work preserved. No staging, commit, push, tag or publication.

## Root cause and exact production decision

**Diagnostic-only defect.** `decision_logic._boundary_corroborated` correctly returns false. Its production predicate is positive-indicator count >= 2 **and** at least one qualifying strength witness. `production_corroboration.evaluate_corroboration` describes only its structural requirement, which for this compound is indicator count. The caller adds `gate_passed=False` and strength fields without extending that explanation. `reasoning_persistence.build_reasoning_trace_text` previously placed the overall boolean next to the count-only explanation and omitted strength details. Thus a passing subcondition appeared to explain a failing complete decision.

The exact unmet condition is **supporting strength**. No threshold, detector, numerical weight, eligibility predicate, confidence policy, origin precedence, OSINT behavior or investigation lifecycle changed in Task E.

Reference: the existing saved Midjourney report at:

`analyzed/high-quality, realistic fashion portrait of a young woman , soft hair, natural dabbled window light f 1.8/3162fff16c3e438b8a8302a77906ff7b/ce576b6ed5c74e02a6539e562118dbc5/report_revisions/ce576b6ed5c74e02a6539e562118dbc5-a2-8b1f870f47ec4010ac928d1eedbc1f28/summary/final_summary.json`

Source SHA-256: `b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`. Existing measurements were resynthesized in memory; no image detector was rerun and no stored result was overwritten.

| Condition | Required value | Observed value | Outcome |
|---|---|---|---|
| Positive indicator eligibility | Suspicious polarity and medium/strong status | Boundary strong/suspicious; subject boundary medium/suspicious | Both eligible |
| Indicator count | >= 2 eligible positive indicators | 2 | PASS |
| Focus eligibility | Suspicious medium/strong observation | Inconclusive/neutral | Excluded from positive count and strength |
| Alignment eligibility | Suspicious medium/strong observation | Weak/neutral, score 0 | Excluded from positive count |
| Boundary strength candidate | Eligible normalized score >= 0.45 | Score absent | No witness |
| Subject-boundary strength candidate | Eligible normalized score >= 0.45 | 0.39331629938549467 | No witness |
| Focus strength candidate | Eligible `boundary_focused_transition_anomaly` or `boundary_focused_processing_mismatch` pattern, embodying existing ratio/boost qualifications | `boundary_processing_inconclusive`; retained intensity 2.153749108314514 | No witness; intensity is not normalized strength |
| Compound strength | At least one qualifying strength witness | 0 | FAIL |
| Ancestry | Shared ancestry allowed for compound interpretations; no distinct-source minimum | Boundary has ELA/residual ancestry; subject boundary intrinsic-edge ancestry | Not a veto |
| Other gate safeguards | None inside this boolean | No additional reliability or geometry veto in this function | Not applicable |
| Overall | Count AND strength | True AND False | FAIL |

The caller's positive status/polarity flags are reused for strength eligibility. Inconclusive or benign Focus cannot supply strength. A valid positive Focus pattern can supply detector-specific strength, while other positive patterns may contribute count only. Alignment contributes count but is intentionally not a strength candidate. These component differences are explicit rather than a universal requirement that all gates use identical semantics. Normal production scorecard validation remains unchanged; Task E does not introduce a second numerical-input validation policy.

Geometry sufficiency, person-mask reliability, local-support score, camera moderation and contextual safeguards are evaluated by the surrounding local route/confidence policy, not hidden predicates inside this compound gate. They must not be presented as the reason this gate failed. `confidence_policy_inputs.snapshot_confidence_facts` reads its exact `gate_passed` boolean into `boundary_compound`; `_localized` consumes that fact. The reference remains `localized.camera_moderated_uncertainty`, Low.

## Small diagnostic correction

- `production_corroboration.py`: added `explain_gate`, which records named production condition outcomes, failure reasons and an overall explanation. It does not assign or recalculate `gate_passed`.
- `decision_logic.py`: supplies the existing predicates at their evaluation sites. Boundary diagnostics retain each strength candidate's actual score, status, polarity, pattern and eligibility alongside qualifying witnesses. Generic diversity diagnostics include indicator count, source count and score requirement. Synthetic compounds disclose their derived flags and the regional geometry guard; accumulation identifies its existing OR-style scorecard support flag.
- `reasoning_persistence.py`: labels the old explanation **Structural Corroboration**, then renders overall outcome, each condition, candidate strength values, exclusions, witnesses, failure reasons and existing ancestry. Legacy records without the additive fields still render their recorded structural explanation; no historical evidence is reconstructed or migrated.
- `tests/test_confidence_policy.py` and `tests/test_production_corroboration.py`: extended existing negative, positive and trace-serialization owners. No new module or collected test case.

The existing `requirement_satisfied`, `gate_passed`, strength fields and audit version `2b3` remain compatible; added diagnostic fields do not change their meanings. A compound passing its structural subcondition must not be mistaken for passing all production conditions.

## Before / after

Before:

```text
boundary.compound_support: passed=False;
2 observed supporting indicator(s) satisfy the 2-indicator compound_interpretations condition
Eligible Evidence: evidence:boundary, evidence:subject_boundary
```

After (abbreviated without changing values):

```text
boundary.compound_support: passed=False
Structural Corroboration: 2 observed supporting indicator(s) satisfy the 2-indicator condition
Overall FAIL: require eligible normalized score >= 0.45 or positive eligible Focus pattern;
              0 qualifying strength witnesses
indicator_count: PASS - 2 suspicious medium/strong supporting indicators; require >= 2
supporting_strength: FAIL - 0 qualifying strength witnesses
Strength evidence:boundary: eligible=True; score=None; qualifies=False
Strength evidence:boundary_focus: eligible=False; inconclusive/neutral;
    score=2.153749108314514; pattern=boundary_processing_inconclusive; qualifies=False
Strength evidence:subject_boundary: eligible=True; score=0.39331629938549467;
    requirement=eligible_normalized_score >= 0.45; qualifies=False
```

## Related-gate consistency audit

| Gate | Reference production outcome | Predicates now disclosed / consumer |
|---|---|---|
| `boundary.compound_support` | False | Count passes; strength fails. Routes and confidence adapter consume the same false value. |
| `confidence.strong_source_diversity` | False | Count 2 passes; 1 measurement-disjoint source < 2 fails; score 18.04075 >= 3 passes. Generic confidence consumes structural diversity and applies the same score threshold, so the combined High-eligibility result agrees. |
| `synthetic.additional_support_flag` | True | Existing metadata OR OSINT-context OR strong-material flag. Used in the synthetic route, not as an independent-source claim. |
| `synthetic.fft_patch_compound` | False | FFT structured true, patch structured false. Route and confidence visual-global fact agree. Clone similarity is not a generation-structure pattern. |
| `synthetic.material_asymmetry_compound` | False | Both strong-material and strong-asymmetry flags false; geometry guard passes. Route and confidence visual-regional fact agree. |

The same reporting limitation existed wherever callers attached extra production predicates to structural results, particularly suspicious-score and regional-geometry requirements. All five now report their actual complete predicates. The synthetic legacy gates intentionally use derived pattern/support flags; their generic structural audit is descriptive rather than an additional production veto. This distinction is retained and labeled, not silently replaced with a new policy. A passed individual gate does not imply a passed whole synthetic route: boost, total score, applicability and route-specific safeguards remain separate and unchanged.

For all five reference gates, serialized `gate_passed` equals the conjunction of recorded production conditions. Existing positive and negative compound coverage verifies the same relationship. Structural ancestry is not statistical independence.

## Reference behavior and validation

**Midjourney:** rebuilding from the saved sections/context yields exact equality with the saved Task D `decision`, `hypothesis_assessments`, `causal_interpretation`, `scorecard`, and full `scorecard_calculation`. Primary synthetic origin / Medium, localized Low, separate edit unestablished, declared process `unspecified_generation_process`, authenticity unverified; suspicious **18.04075**, benign **1.50**. Boundary false and generic diversity false are preserved. No measured values or selection changed.

**ComfyUI:** read the existing actual source `test_images/stablediffusion/the-greatest-amateur-photo-realism-i-have-ever-achieved-v0-ovys259b8xyg1.png` through the existing metadata extractor, without writing artifacts or rerunning pixel detectors. Connected `full_image_generation` remains recognized; signals `EMBEDDED_GENERATION_PROMPT`, `AI_TOOL_NAME_MATCH`; no `DECLARED_ENHANCEMENT`. Metadata-only reasoning gives synthetic origin / Medium, and each reported gate matches its production predicates. The existing four connected-workflow cases and visual compound positive control also pass. Task D's full-image ComfyUI measurements were not recomputed: its comparison JSON is retained as historical evidence, not claimed as a fresh full-pipeline comparison.

Coverage audit reused the behavioral matrix's corroboration, confidence, ancestry, arithmetic, reasoning serialization and metadata owners. Newly protected behavior: a passing count with failing strength must render the actual failure and retained measured value; positive compounds must report no failure; repeat trace evaluation must report outcomes matching all stated production predicates. Existing authoritative source-diversity, inactive evidence, lineage, deterministic serialization, compound behavior and workflow cases were reused.

Baseline collection: **525**. Added **0**, removed **0**, consolidated **0**; final **525**, net **0**. Focused command:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests/test_confidence_policy.py tests/test_production_corroboration.py tests/test_reasoning.py -q`

**130 passed in 0.29s.** The first extension used an incomplete trace fixture and failed two cases; changed it to the existing complete synthesis API, then the focused group passed. No production workaround for that fixture error was introduced.

Because the shared trace serialization contract changed, ran the final complete acceptance gate:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q`

**525 passed in 16.53s; 0 failed, 0 skipped.** `git diff --check` passes for the five changed code/test files. No baseline or fixture regeneration.

## Git discipline and limitations

Captured the inherited status/content inventory before edits. Task E changes only the five code/test files listed above plus this report. Inherited Task D production work, version changes, user documents/images, deleted artifacts and existing audit documents are preserved. Permission-denied inherited paths cannot be byte-verified. Nothing staged, committed, pushed, tagged or published.

Historical traces without strength diagnostics cannot disclose facts they never recorded; they retain the legacy rendering path. Native/package GUI inspection and empirical classification calibration were not performed and are not implied by the automated suite. No claim of improved classification accuracy is made.

**Task E status: Complete.** This is a diagnostic correction; broader release/package readiness remains separate.
