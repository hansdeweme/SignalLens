# Hypothesis selection and causal adequacy

Evidence identity/TRACE paths: [root-cause report](root_cause_report.md). Graph reconstruction: [workflow analysis](workflow_graph_analysis.md).

## Actual selection algorithm

`decision_logic.evaluate_hypotheses` (`decision_logic.py:1328-1500`) does the following:

1. Rebuilds candidate audit state; invalid scorecards lead to withheld conclusions (`:1331-1344`).
2. Evaluates **every** route and records whether it matched (`:1345-1358`). It does not stop at the first match.
3. Sorts successful candidates by `(priority, route function name)` (`:1359`). Priorities express specificity within a hypothesis; alphabetical route name provides deterministic tie-breaking for equal priority.
4. Chooses a localized candidate. If boundary safeguards matched, a specific clone-reuse candidate can survive them; otherwise the highest-priority safeguard governs. Without safeguards, the first sorted local candidate is retained (`:1364-1370`).
5. Chooses a synthetic candidate. Supported visual generation leads unless the recurrence caution matched; a provenance declaration survives that caution (`:1371-1377`).
6. Applies explicit cross-hypothesis precedence (`:1382-1408`): decisive suspicious local mechanism; specific visual generation; other specific local mechanism; specific generation declaration; remaining local; remaining synthetic; then general anomaly/camera/fallback.
7. Builds all hypothesis assessments, scopes evidence, records selection and route dispositions (`:1440-1499`).
8. Applies the authoritative confidence policy **after choosing** (`:1500`, `_apply_confidence_policy` at `:1303`). Each hypothesis receives its own tier; legacy route labels are rewritten to the authoritative tier without reranking the primary finding.

`DecisionRoute` definitions are at `decision_logic.py:1264-1296`. `finding_specificity` (`confidence_policy.py:55`) classifies `BOUNDARY_DECISIVE`, `MULTI_LOCAL` and `CLONE_DECISIVE` as decisive; visual generation and declarations are specific. Consequently the algorithm is not “High beats Medium,” even if that happens to describe this output. Altering route confidence strings alone cannot alter selection. Numeric mechanism scores influence route eligibility, not a global candidate ranking. Generic supporting-evidence counts and suspicious totals do not arbitrate between generation and editing.

## Why this local route wins

Saved TRACE `/decision_route_trace` marks `route_strong_local_edit` as selected and `route_provenance` as the synthetic candidate. Boundary safeguards, multi-local and clone routes did not match.

| Predicate | Saved value | Outcome |
|---|---:|---|
| Local support >= 3.5 | 6.05 | Pass |
| Local support >= clone + 1.0 | 6.05 >= 1.0 | Pass |
| Camera support < 2.0 | 1.25 | Pass |
| Contextual false-positive risk absent | false | Pass |
| Boundary corroboration count >= 2 | boundary + subject_boundary | Pass |
| Maximum boundary-specific score >= 0.45 | 0.500713508932127 | Pass |

These are `route_strong_local_edit` (`decision_logic.py:844`) and `_boundary_corroborated` (`:562-613`). The latter counts medium/strong suspicious outputs from boundary, focus, subject boundary and segmentation alignment; maximum score is taken across focus/subject-boundary/boundary. This image's focus is benign/weak, alignment neutral/weak. Neither counts positively. The remaining boundary strong plus subject boundary medium satisfy the two-indicator condition, with the subject transition score providing the strength requirement.

Local score arithmetic in the saved component ledger and `hypothesis_engine.compute_scorecard` (`hypothesis_engine.py:394-482`):

`2.0 boundary-pattern + 1.0 cross-pattern + 0.35 medium subject transition + 0.40 compression + 0.75 subject texture + 0.40 asymmetry + 0.75 material - 0.20 camera + 0.60 boundary-stack synergy = 6.05`.

Note the important distinction: subject texture/material/asymmetry contribute to numeric local support even when their final hypothesis role is contextual. Role scoping happens after route evaluation; roles are not an independent score recalculation. This is existing architecture, not evidence that those signals establish a separate editing operation.

`strong_local_edit=true` means the boundary pattern matches a named constant (`hypothesis_engine.py:277`). That pattern comes from contour-like spatial overlap of ELA/noise hotspots (`vf_cross_signal.classify_boundary_convergence`, `vf_cross_signal.py:62-115`), including component patterns that may themselves be inconclusive. Its adapter elevates that named pattern to section status strong (`summary_sections.build_boundary_section`, `summary_sections.py:456`). The producer's own `boundary_strength` is medium. The boolean name is therefore stronger sounding than the underlying causal assertion.

Person-mask reliability is high, boundary area ratio 0.05065346, geometry-unreliable false. `derive_signals` (`hypothesis_engine.py:292-309`) assigns boundary reliability 1.0 from region source/reliability and band size. This is a geometry eligibility check, not a probability that an edit occurred. Central `_localized` (`confidence_policy.py:188-226`) checks required reliable geometry, boundary reliability >= 0.6 and the compound plus score conditions; assigns `localized.reliable_boundary_compound`, High. The selection reason comes directly from `decision_logic.py:1384`.

### Counter-evidence and camera compatibility

`boundary_processing_convergence_supported` is direct local counter-evidence (`hypothesis_evidence.py:120-123`). The focus note reports combined boundary ratio 0.936, boost -0.984 and no meaningful contour-band mismatch. Alignment reports no meaningful subject-boundary alignment. Focus is not silently discarded: it appears in TRACE `/decision/contradicting_evidence` and policy rationale. However, `_boundary_corroborated` counts positive eligible indicators rather than vetoing on a contradictory check; the other two survive. `evaluate_confidence` (`confidence_policy.py:265` onward) records the contradiction but does not subtract a universal penalty. Existing coverage explicitly allows High to survive this situation.

Camera support slightly reduces local support and supplies caution/attenuation (`hypothesis_engine.py:371`, `:425`, `:673-701`), but 1.25 remains below the local route's 2.0 exclusion threshold. Camera-compatible structure can describe a base image or a generated camera-like texture, so it is a moderator, not authentication or a veto (`hypothesis_evidence.py:110-119`). It also moderates synthetic origin without refuting an unverified generation declaration.

## Why synthetic multi-signal fails

`route_synthetic_multi_signal` (`decision_logic.py:1001-1042`) requires **all** outer conditions; a successful FFT/patch compound alone is insufficient.

| Required condition | Saved evidence | Result |
|---|---|---|
| synthetic_boost >= 1.0 | 0.4 | **Fail: immediate decisive cause** |
| suspicious_score >= 5.0 | 21.30815 | Pass |
| synthetic_supported_by_other_domains | true, from metadata | Pass |
| FFT+patch structured OR strong material+strong asymmetry with reliable geometry | FFT+patch true; regional pair false | Pass via global pair |
| Not weak local + clean provenance + coverage >= 0.18 | local_signals_weak=false; provenance_clean=false; coverage=0.0382 | Pass |

The 1.0 boost in `hypothesis_engine.py:585-603` requires structured patterns plus FFT >= 0.80, periodicity >= 0.70, symmetry >= 0.55, peak count >= 4, axis bias >= 0.60, patch score >= 0.70, repetition >= 0.60, separated pairs >= 8, total pairs >= 12, mean similarity >= 0.88 and maximum >= 0.92.

Actual failures: FFT 0.5673; patch 0.5901; separated-pair count 0; mean/max similarity 0. The last three are **missing metrics defaulted to zero**, not measured absence. `vf_patch_similarity.py:131-168` omits them from the output despite computing them internally. Periodicity 1, symmetry 1, 200 peaks, axis bias 0.6062, repetition 0.7477 and 289 pairs meet their thresholds. No segmentation or strong-material boosts apply. Medium material realism gives the only 0.4 synthetic boost. Fixing producer serialization alone would still leave the FFT and patch score failures for this image; no claim of a changed route is warranted.

`scope_hypothesis_evidence` (`hypothesis_evidence.py:99-109`, `:168-201`) makes generation-structure observations supporting only when the visual-generation candidate is established and not recurrence-cautioned (`decision_logic.py:1480`). Otherwise it falls back to contextual. Thus contextual FFT/patch evidence here is a deliberate gate-driven outcome, not a lost metadata declaration. There is a policy coupling: the route enables the supporting role, rather than independently supporting roles determining the route. Calling these contextual is conservative, but it does not constitute a full causal model.

`route_provenance` (`decision_logic.py:1118-1147`) remains successful because metadata has the unverified-generation state. `_synthetic` (`confidence_policy.py:167-185`) assigns Medium via `synthetic.unverified_generation_declaration`. Medium is the intentional declaration-only bound, not a blanket ceiling when separately qualifying visual generation exists. Even the authenticated-assertion branch distinguishes authenticated claim from pixel origin. There is no production validator in this path (`confidence_policy_inputs.py:43-45`). Graph coherence can add specificity about a declared process without changing this confidence or numerical score.

## Corroboration gates: no independence contradiction

| TRACE gate | Recorded result | Meaning |
|---|---|---|
| `boundary.compound_support` | Pass; two eligible indicators, strength pass | Compound spatial/processing interpretation. Related ancestry is allowed. Here boundary and subject-boundary have different recorded measurement ancestry. |
| `confidence.strong_source_diversity` | Fail; boundary + cross count as one disjoint witness | Generic anomaly High gate. Both inherit ELA/luminance residual; it does not constrain a specific local compound route. |
| `synthetic.fft_patch_compound` | Pass; FFT + patch | Structured pattern pair, not the full synthetic route or its boost threshold. |

Registry sources: `evidence_lineage.py:109-127`. Gate implementation: `production_corroboration.evaluate_corroboration`; explicit compound-vs-disjoint behavior and limitations at `production_corroboration.py:119-161`. A disjoint extraction ancestry is structural accounting, never statistical independence. Scores, lineage, compound eligibility and causal specificity are separate concerns; satisfying one does not establish the others.

## Is the conclusion defensible?

It is defensible as a statement of **strong heuristic regional-anomaly concern under the existing rules**, and it correctly keeps generation unverified. It is insufficiently qualified as a claim that a separate localized editing/compositing process occurred. A wholly generated image can show the same boundaries, local compression-like block energy, subject texture and camera-compatible microstructure. The implementation has no predicate requiring a prior photograph, an independently identified edit event or a mechanism that excludes whole-image generation. The contradictory band/focus result makes unqualified compositing language particularly questionable.

The metadata does not prove the alternative either. A forged/transplanted graph can be coherent. A safe correction must not erase image-based anomalies, manufacture verified provenance or promote synthetic High simply to make the primary label feel more plausible.

## Design options

| Option | Forensic defensibility / false-positive and forgery risk | Architecture, trace/report/GUI impact | Complexity / regression risk |
|---|---|---|---|
| A: classify workflow only | Precisely describes declarations and fixes structural-token errors; preserves unverified status. Does not resolve causal overstatement of local editing. | Add optional metadata/trace details and render them. Existing selection unchanged. | Low to moderate; parser abstention and compatibility matter. |
| B: classification + causal-compatibility rule | Useful if it separates anomaly confidence from event specificity. Unsafe if a coherent graph simply vetoes localized evidence: forgery could suppress true edits. | Needs an explicit causal-status input and documented selection/lead narrative rule. Preserve independent spatial reuse and raw anomaly assessments. | Moderate; changes selection semantics if wired directly to `primary_hypothesis`. |
| C: creation and editing dimensions | Most faithful: declared full generation and regional anomalies can coexist; separate edit remains unestablished. Does not use declaration as proof. | Small additive synthesis fields can coexist with legacy three hypotheses; presentation must show trust and role distinctly. Full replacement of the hypothesis model is unnecessary. | Moderate, bounded if additive; historical files need fallback. |
| D: weights/confidence/precedence | Does not fix structural-token semantics or causal ambiguity. Can reward forged metadata or broadly suppress local evidence. | Easy code change, broad behavior/report changes; poor traceable justification. | Superficially low implementation cost, high interpretive regression risk. Not recommended. |

**Recommendation: A plus the smallest additive part of C, using B only to qualify the lead interpretation, not to veto evidence.** Introduce an explicit synthesis record with declared creation process/authenticity, regional observations, and `separate_edit_status=not_established_from_these_signals`. For this case, lead wording can be: “Embedded workflow declares full-image generation; authenticity is unverified. Regional forensic anomalies are also present; a separate editing operation is not established.” Display the existing Medium declaration support and regional support separately, never as a new global confidence.

The existing binary choice cannot express that lead cleanly without changing the meaning of `primary_hypothesis`. Preserve its legacy value and record an additive `lead_interpretation`/causal qualification for presentation. Use it consistently in the primary explanation and report; describe High local support as anomaly support, not established editing history. Also qualify boundary-route wording independently of metadata so absence/forgery does not control whether causality is overstated. Direct clone/reuse evidence must retain its own scoped conclusion.

Thus SignalLens **can prefer the coherent declared process as explanatory context without accepting it as truth**, but that is an editorial/causal synthesis decision, not a finding that synthetic origin has higher factual confidence. If the product instead requires replacing the actual `primary_hypothesis` with synthetic origin, an explicit new causal-selection contract and migration of precedence coverage are required; do not hide that policy change in route priorities. Task B's recommended scope is the additive approach above, with unchanged numeric and confidence contracts.
