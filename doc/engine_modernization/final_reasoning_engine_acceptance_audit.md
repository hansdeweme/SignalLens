# Final acceptance audit: original ten reasoning-engine corrections

Audit date: 2026-11-01. Repository: SignalLens. Branch: `fix/scorecard-integrity-phase2a`. Audited HEAD: `f64f226` (`phase 1`), **including the inherited uncommitted implementation described below**. Line references refer to this working tree, not necessarily HEAD.

## A. Executive summary

**FAIL — One or more original corrections remain materially incomplete.**

The original roadmap cannot yet be closed: **9 ACCEPTED, 1 PARTIALLY ACCEPTED, 0 FAILED**. Correction **#6**, preventing correlated-signal double-counting, is partially accepted. Production now prevents related descendants from masquerading as distinct sources in the generic High-confidence gate. It does **not** resolve potentially redundant numerical credit across related section weights, domain bonuses and mechanism boosts. That is a material remainder of the original requirement, explicitly included in this acceptance task.

This is a roadmap-closure verdict. It does not mean that either reference pipeline failed or that the nine accepted corrections are ineffective. All **297 collected tests passed**, with **0 failed, 0 skipped and 0 pytest warnings reported**. Fresh full runs of both original images reproduce the supplied scores and conclusions. Independent arithmetic replay reconciles both ledgers. No production code, tests, coefficients, thresholds, dependencies or images were changed during this audit.

Additional probes found nonblocking robustness and internal-extension limitations: oversized integers escape numeric validation as `OverflowError`; malformed inactive metadata details can raise `AttributeError`; removing the provenance route through the internal route-subset seam can produce a policy-supported secondary declaration with an inconsistent default explanation. These do not reproduce through the normal controller/summary route on valid detector payloads. Their exact scope and suggested tests are recorded below, rather than being hidden by the passing suite.

Acceptance establishes the specified qualitative reasoning behavior, not calibrated probabilities, statistical independence of image features, authenticity certification, or exhaustive coverage of arbitrary malformed Python objects.

## B. Ten-point acceptance matrix

Test paths in this table are under `tests/`. Named tests were inspected and executed as part of the complete suite; parametrization accounts for the difference between function counts and collected cases.

| # | Correction | Status | Source evidence | Test evidence | Remaining limitation |
|---|---|---|---|---|---|
| 1 | Prevent premature decision-route termination | **ACCEPTED** | `decision_logic.py:1328 evaluate_hypotheses` evaluates every supplied route before sorting by priority/name, selecting scoped findings, and applying policy. `_specific_finding:1298` uses typed specificity. Boundary safeguards constrain local mechanisms without suppressing generation; clone support has its own handling. | `test_reasoning.py:269 test_strong_local_edit_is_not_overwritten_by_metadata`, `:281 test_boundary_safeguards_do_not_block_generation`, `:361 test_supported_visual_generation_survives_local_uncertainty`, `:210 test_irrelevant_route_order_does_not_change_assessments`; `test_confidence_policy.py:188 test_route_order_and_repeated_evaluation_do_not_set_policy_confidence`. | Custom removal of routes is distinct from equivalent route reordering; see F03. No normal-path premature termination found. |
| 2 | Separate synthetic-origin and localized-edit hypotheses | **ACCEPTED** | `hypothesis_engine.py:141 HypothesisAssessment`; `decision_logic.py:1328 evaluate_hypotheses` retains synthetic, localized and camera assessments even when only one leads. Each has roles, confidence, limitations and explanation. | `test_hypothesis_scoping.py:69 test_all_three_hypotheses_remain_visible_and_deterministic`, `:218 test_json_and_all_narratives_use_the_authoritative_assessment`; `test_confidence_policy.py:136 test_strong_visual_generation_and_limited_local_findings_are_assessed_separately`, `:143 test_camera_compatibility_and_generation_declaration_coexist`. Fresh image runs retain all three. | Primary selection expresses interpretation specificity/precedence, not the highest secondary confidence tier. |
| 3 | Correct embedded-prompt propagation | **ACCEPTED** | `exiftool_backend.py:142 _is_embedded_metadata_entry`, `:405 find_term_matches`, `:461 _explicit_generation_workflow`, `:481 _source_type_declarations`, `:496 build_signals`; `summary_sections.py:54 build_metadata_section`; `metadata_evidence.py:42 classify_metadata_signals`; `hypothesis_engine.py:208 derive_signals`; `decision_logic.py:1118 route_provenance`. Explicit prompt/IPTC declarations survive the complete path. | `test_reasoning.py:133 test_embedded_prompt_propagates`, `:404 test_midjourney_raw_metadata_path_regression`, `:432 test_iptc_source_type_alone_is_scoped_unverified_declaration`, `:452 test_other_source_type_values_do_not_declare_ai_generation`, `:465 test_midjourney_prompt_signature_is_not_just_an_arbitrary_description`, `:476 test_host_paths_and_extractor_diagnostics_are_not_embedded_evidence`; `test_hypothesis_scoping.py:129 test_ai_text_only_in_paths_does_not_survive_as_generation_evidence`. Fresh Midjourney extraction reaches both declaration IDs. | Recognition is rule based. Ordinary creator identity and populated workflow fields alone are not generation proof. |
| 4 | Correct provenance weighting and interpretation | **ACCEPTED** | `metadata_evidence.py:6 ProvenanceState`, `:84 metadata_provenance_state`; `decision_logic.py:1118 route_provenance` no longer requires a provenance-boost threshold. `confidence_policy.py:162 _synthetic`; `confidence_policy_inputs.py:14 snapshot_confidence_facts` supplies `verification=None`. Production metadata cannot manufacture a validated assertion. | `test_reasoning.py:118 test_metadata_only_generation_declaration`, `:243 test_unverified_c2pa_is_neutral_and_never_camera_support`, `:258 test_enhancement_is_distinct_from_generation`; `test_hypothesis_scoping.py:142 test_conflicting_camera_metadata_and_declaration_both_survive_extraction`; `test_confidence_policy.py:42 test_verified_assertion_requires_actual_typed_validator_and_image_binding`, `:53 test_metadata_verification_flags_and_ambiguity_cannot_create_high`, `:61 test_verification_enum_or_json_dictionary_is_not_a_validator_result`. | No production cryptographic validator exists. The typed assertion facility is a policy interface, not proof of validation from metadata. |
| 5 | Remove suspicious scoring for missing metadata | **ACCEPTED** | `summary_sections.py:54 build_metadata_section` returns neutral sparse/stripped metadata, score 0; `hypothesis_engine.py:161 is_suspicious`, `:165 is_benign` exclude missing-metadata patterns defensively; `:312 compute_base_scores` gives no weight/domain for neutral evidence. Missing provenance remains a limitation in `evaluate_hypotheses`. | `test_reasoning.py:165 test_stripped_metadata_is_neutral_and_scores_zero`, `:327 test_sparse_metadata_never_becomes_support_alongside_declaration`, `:334 test_metadata_absence_does_not_change_scores_or_domains`; `test_scorecard_integrity.py:79 test_no_evidence_has_no_fabricated_support_or_penalty`, `:175 test_missing_metadata_supplies_no_provenance_boost`. Fresh Instagram metadata is neutral and not generation support. | `provenance_clean` is a legacy absence-of-adverse-declaration flag, not authenticated provenance. Existing camera conjunctions must not be interpreted as authentication. |
| 6 | Prevent double-counting correlated signals | **PARTIALLY ACCEPTED** | `evidence_lineage.py:109 _SPECS`, `:164 build_lineage`; `production_corroboration.py:47 _disjoint_witnesses`, `:73 evaluate_corroboration`; `decision_logic.py:295 determine_confidence`. Generic source diversity is corrected. However, `hypothesis_engine.py:312 compute_base_scores`, `:324 compute_scorecard`, `:487 local_support_conversion` retain numerical reuse; `marginal_corroboration.py:45 allocate_marginal` is a shadow allocator with unvalidated margins for interpretive/localizing additions. | `test_production_corroboration.py:42 test_primary_and_two_descendants_cannot_be_three_sources`, `:58 test_composite_does_not_become_third_source_or_collapse_distinct_primaries`, `:66 test_true_compound_boundary_condition_is_not_replaced_by_source_uniqueness`, `:162 test_corrected_gate_changes_only_generic_high_confidence_eligibility`; `test_evidence_lineage.py:241 test_full_snapshot_card_trace_integration_preserves_entire_production_result`. Fresh runs verify shadow isolation, not numerical deduplication. | **F01 blocks closure.** Related observations can still receive full separate base/domain credit and mechanism boosts without a demonstrated marginal numerical attribution. |
| 7 | Make contradictory evidence hypothesis-specific | **ACCEPTED** | `hypothesis_evidence.py:76 _rules`, `:152 scope_hypothesis_evidence`, `:267 evidence_presentation`. Exact section/pattern mappings distinguish support, contradiction, moderation and context. Boundary consistency is scoped to boundary editing; camera observations qualify generation/local conclusions and support acquisition compatibility. | `test_hypothesis_scoping.py:24 test_midjourney_support_and_counterevidence_are_scoped`, `:168 test_weak_zero_score_boundary_counterevidence_is_not_hidden`, `:179 test_boundary_consistency_is_not_a_contradiction_of_clone_reuse`, `:189 test_spatial_corroboration_is_needed_to_present_copy_move_support`, `:200 test_unknown_pattern_names_do_not_infer_hypothesis_relevance`; `test_confidence_policy.py:153 test_direct_contradiction_changes_mechanism_eligibility_without_global_penalty`. | Unknown patterns require explicit mapping; their names do not imply relevance. Empty contradiction lists in the two references are valid, not missing camera observations: those are moderators. |
| 8 | Correct inconsistent scorecard calculations | **ACCEPTED** | `hypothesis_engine.py:324 compute_scorecard`, especially `:663` raw boundary, `:677` boundary adjustment and `:687` final subtotal; `scorecard_integrity.py` `ComponentLedger`, `reconstruct_scorecard_calculation`, `validate_scorecard`. Final aggregates follow adjustments and reconcile with serialization. | `test_scorecard_integrity.py:134 test_multiple_reliability_adjustments_are_applied_once_in_declared_order`, `:218 test_nonfinite_input_is_rejected_purely_and_withheld_in_production`, `:257 test_validator_detects_inconsistent_or_duplicated_calculations`, `:276 test_serialized_trace_is_independently_reconstructable_and_rendered`, `:353 test_randomized_calculations_are_finite_deterministic_and_reconstructable` (250 generated combinations inside one test). Independent fresh-image replay also passes. | Arithmetic correctness does not establish nonredundant evidential weighting (#6). F02 is an overflow-handling gap, not a demonstrated confident invalid result or ledger mismatch. |
| 9 | Decouple confidence from route-specific hardcoding | **ACCEPTED** | `confidence_policy.py:225 evaluate_confidence`; `confidence_policy_inputs.py:14 snapshot_confidence_facts`; `decision_logic.py:1303 _apply_confidence_policy`, `:701 finish_decision`, `:1503 synthesize_overall`. Final tiers come from policy after scoped assessment. Typed findings/specificity, not legacy route tiers, drive selection. Finishing restores policy tiers even after provisional-tier mutation. | `test_confidence_policy.py:96 test_reliability_cap_does_not_depend_on_safeguard_route_presence`, `:114 test_descendants_cannot_bypass_general_high_gate_via_a_high_route_label`, `:201 test_tampering_with_every_route_tier_cannot_change_selection_or_policy`, `:214 test_branch_names_text_and_legacy_assessment_tier_are_not_policy_inputs`, `:236 test_presentation_cannot_be_overridden_by_a_provisional_or_mutated_tier`, `:296 test_invalid_scorecard_has_named_inconclusive_policy_for_every_assessment`. | Legacy route labels remain diagnostic. F03 concerns incomplete assessment construction on an internal extension path, not a bypass granting legacy confidence authority. |
| 10 | Improve reasoning trace and regression coverage | **ACCEPTED** | `decision_logic.py:98 _build_reasoning_trace`, `:701 finish_decision`; `reasoning_persistence.py:13 persist_reasoning_trace`, `:467 persist_reasoning_trace_text`; `summary_synthesizer.py:73 build_summary_result`. Traces expose observations, derived state, provenance, candidates/dispositions, assessments/roles, selection, calculations, gates, policy and limitations. Optional dependency analysis adds the full lineage sidecar. | `test_reasoning.py:218 test_json_compatibility_and_text_adapter`, `:308 test_summary_and_render_integration_preserves_interface`; `test_hypothesis_scoping.py:265 test_legacy_trace_without_new_evidence_fields_still_renders`; `test_confidence_policy.py:245 test_json_and_text_use_one_authoritative_policy_for_all_hypotheses`, `:265 test_summary_gui_consumption_and_coverage_are_compatible`; lineage round-trip/shadow-failure tests. Both fresh runs persist JSON/text/HTML and reasoning JSON/text. | Full lineage is opt-in; normal traces include gate-specific ancestry. Summaries are not complete raw detector-array archives. GUI clicks and full real-image execution are not automated by the 297 tests; see D/H. |

## C. Critical findings, ranked by severity

### F01 — High: numerical overlap remains unresolved (closure blocker, correction #6)

The dependency registry accurately identifies common measurements for cross-signal convergence, its boundary interpretation, boundary focus and segmentation alignment. It also identifies patch-spatial localization as consuming the retained patch matches. These are known computational dependencies, not merely a suspicion that arbitrary image features might be statistically correlated.

Nevertheless, `compute_base_scores` independently sums every active suspicious section's full status weight and awards additional domain credit without consulting lineage. `compute_scorecard` then adds mechanism terms, including conversion of local support into `edit_boost`. These terms are arithmetically documented, but their incremental evidential credit has not been reconciled across the overlapping observations.

Fresh Instagram evidence demonstrates the active paths:

| Section | Base status/weight | Domain | Relevant common source |
|---|---|---|---|
| `cross_signal` | weak / 0.5 | `cross_signal` | ELA and residual hotspot measurements |
| `boundary` | strong / 3.0 | `boundary` | Interpretation of those same hotspot measurements |
| `boundary_focus` | medium / 1.5 | `boundary_focus` | ELA/residual maps localized with mask geometry |
| `patch_similarity` | medium / 1.5 | `patch` | Retained patch matches |
| `patch_spatial` | medium / 1.5 | `patch_spatial` | Spatial interpretation of those patch matches |

The first three receive 5.0 total base weight and count as three suspicious domains; their distinct domain labels can increase the diversity bonus despite shared measurement ancestry. Other suspicious sections also contribute to the overall domain count, so this is not a claim that 5.0 is the whole score or that subtracting 5.0 would be correct. The full Instagram base is 23.0, local support is 4.85, and its conversion adds 0.873 to `edit_boost` alongside other edit terms. Midjourney similarly retains both cross-signal (1.5) and boundary (0.5) base weights.

Localization and interpretation can add real information. This finding **does not** establish that every term above is wholly duplicate or prescribe deleting every derived observation. The unresolved issue is that production still awards full accumulated credit without an accepted account of which credit is shared and which is incremental. The shadow allocator explicitly leaves such margins unvalidated and preserves existing values provisionally. No current production registry detector is designated a pure restatement whose shadow suppression would solve these cases.

Minimal follow-up: explicitly reconcile these existing contribution paths by hypothesis, target and measurement ancestry; identify preserved compound interpretation versus repeated numerical credit; implement only the necessary reviewed numerical attribution and domain-credit correction. Add integration regressions showing descendants cannot inflate the same evidence credit, genuinely added localization can retain justified credit, separate primaries remain usable, and both ledgers still reconcile. **Do not activate arbitrary experimental weights or treat a blanket family discount as the solution.** This audit implements none of that work.

### F02 — Medium: numeric validation can leak overflow (nonblocking robustness limitation)

`scorecard_integrity.py:finite_number` calls `math.isfinite(value)` before converting/normalizing conversion errors into `ScorecardIntegrityError`. A Python integer of `10**1000` is a `Real`, but conversion inside `isfinite` raises `OverflowError`. `decision_logic.py:664 build_decision_env` catches only `ScorecardIntegrityError`, so synthesis raises instead of returning the controlled invalid-scorecard assessment.

Reproduction: pass a `ModuleSummary(name='measurement', status='strong', polarity='suspicious', domain='measurement', pattern='observed', score=10**1000)` to `synthesize_overall` under key `measurement`. Observed: `OverflowError: int too large to convert to float`. Equivalent NaN and positive-infinity probes return Inconclusive, with `integrity.invalid_scorecard` on all four assessments.

This does not manufacture a confident conclusion and does not invalidate the corrected aggregate ordering. Current detector outputs are bounded ordinary numeric measurements; no normal image reproduces it. Therefore it does not block closure of the original mathematical correction. Minimal hardening: translate numeric conversion/range errors to the existing integrity exception; test huge integer inputs and overflow during accumulation through the public synthesis boundary, asserting controlled abstention and no input mutation.

### F03 — Medium: internal alternate assessment paths can misdescribe provenance (nonblocking extension limitation)

Using `build_metadata_section({'signals':[{'id':'DECLARED_SYNTHETIC','evidence':[]}]})`, build an environment, then call `evaluate_hypotheses` with only the `route_fallback` specification, followed by `finish_decision`.

Observed: primary `unresolved_anomaly`, overall Low, dominant pattern `provenance_supported_synthetic_context`; secondary synthetic assessment Medium under `synthetic.unverified_generation_declaration`, with supporting declaration evidence, but its unchanged default explanation says synthetic origin is not established. Policy reads the metadata independently; candidate-derived explanation/selection does not reconstruct the omitted provenance route. Calling `finish_decision(env, route_provenance(env))` directly similarly defaults to an unresolved assessment, although confidence still comes from policy.

The supported five-element `synthesize_overall` path always evaluates the registered routes before finishing. Controller and GUI callers do not invoke these alternate constructions. Route reordering, omission of safeguard routes, and provisional confidence tampering are separately covered and do not demonstrate this problem. Consequently #1/#9 remain accepted for production integration. Minimal follow-up: either define and enforce the full-evaluation precondition for internal helpers, or construct coherent scoped hypotheses/explanations for partial route sets. Add a declaration-only route-subset/direct-finisher regression before advertising either path as a supported extension API.

### F04 — Low: inactive malformed metadata details escape validation (nonblocking contract hardening)

A metadata summary with status `inconclusive`, neutral polarity, pattern `inconclusive` and `details=['malformed']` passes the active-observation-only input validator, then raises `AttributeError: 'list' object has no attribute 'get'` during evidence scoping. `ModuleSummary.details` is defined as a dictionary and normal metadata builders satisfy that contract. This probe is an out-of-contract object, not an absent optional metadata payload; absent payloads are tested and work.

Minimal follow-up: validate structural fields regardless of scoring availability, or guard dictionary access in scoping. Test malformed inactive details alongside valid missing/stale unavailable numeric payloads so defensive checking does not accidentally turn missing evidence into support. No normal-image regression or confident false conclusion was observed.

## D. Integrated validation

### Complete automated suite

Executed `py -3.13 -m pytest -q --tb=short`: **297 passed in 2.59 seconds**, exit 0. **Failed: 0. Skipped: 0. Pytest warnings reported: 0.** Separate collection with `py -3.13 -m pytest --collect-only -q -p no:cacheprovider` confirmed **297 collected** (exit 0). This exactly matches the prior baseline; no tests were added or edited to obtain it.

| Test file | Collected cases |
|---|---:|
| `tests/test_reasoning.py` | 61 |
| `tests/test_hypothesis_scoping.py` | 28 |
| `tests/test_mask_pipeline.py` | 32 |
| `tests/test_scorecard_integrity.py` | 63 |
| `tests/test_evidence_lineage.py` | 48 |
| `tests/test_production_corroboration.py` | 30 |
| `tests/test_confidence_policy.py` | 35 |
| **Total** | **297** |

Environment: Windows 11, platform string `Windows-11-10.0.26300-SP0`; CPython **3.13.13**, 64-bit AMD64, MSC v.1944; pytest **9.1.1**. Installed runtime versions observed: MediaPipe **1.2.0**, NumPy **2.2.6**, Pillow **12.3.0**, OpenCV **4.13.0.92**, PyQt6 **6.10.2**. The complete suite required the existing approved pytest escalation for Windows temporary-file fixtures. No dependency installation/update was performed.

The suite exercises units, builder/synthesis/render/persistence integration, contradictions, missing data, stale unavailable fields, invalid numbers, repeated evaluation, ordering, lineage cycles and unknown lineage, shadow failure isolation and controlled controller failures. The generated mathematics test runs 250 combinations but remains one collected test. Reference-like automated fixtures are synthetic/reconstructed observations, not fresh executions of the original images. The following runs supply that additional integration evidence.

### Fresh full headless reference runs

Both accessible original images were processed with `SignalLensController.run_analysis(..., analysis_mode='subject_based')`, followed by `build_summary_result`, text/HTML/JSON persistence and reasoning JSON/text persistence. Fresh outputs are in ignored `analyzed/final_acceptance_audit/instagram/` and `midjourney/`. The reproducible audit runner is `analyzed/final_acceptance_audit/run_reference_audit.py`; structured results are `reference_results.json`. Existing Phase 3 traces were comparison evidence only, not substituted for these runs.

| Metric | Instagram | Midjourney |
|---|---|---|
| Input | `test_images/insta_fake/Curvy Leggings Outfit.jpg` | `test_images/midjourney/theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png` |
| Suspicious / benign | **20.47705 / 2.25** | **6.0375 / 1.5** |
| Primary hypothesis | `localized_editing` | `synthetic_origin` |
| Overall confidence | **High** | **Medium** |
| Dominant pattern | `possible_foreground_background_processing_mismatch` | `provenance_supported_synthetic_context` |
| Primary supporting evidence | Boundary mismatch, boundary focus, localized compression inconsistency, cross-signal convergence, subject-boundary segmentation artifact | `metadata:DECLARED_SYNTHETIC`, `metadata:EMBEDDED_GENERATION_PROMPT` |
| Primary contradicting evidence | None | None |
| Primary moderating evidence | Camera-like sensor microstructure and weak CFA compatibility | Camera-like sensor microstructure |
| Segmentation status | Reliable person mask; foreground ratio **0.5961422390407987** | Low-reliability person mask; ratio **0.9181777419747081**, above unchanged **0.90** usable maximum; regional consumers withheld |
| Successful stages | **23** | **14** |
| Unavailable / skipped / failed | **0 / 0 / 0** | **1 / 8 / 0** |
| Recorded errors | **0** | **0** |
| Coverage | Complete | Partial; unavailable regional evidence is a limitation, not authenticity or generation support |
| Primary policy rule | `localized.reliable_boundary_compound` | `synthetic.unverified_generation_declaration` |
| Secondary hypotheses | Synthetic Inconclusive; camera Medium | Localized Inconclusive; camera Medium |
| Deviation from supplied baseline | None in scores, primary tier or conclusion | None in scores, primary tier or conclusion |

Midjourney's unavailable stage is person-derived region masks. Eight dependent stages are skipped: region segmentation, boundary focus, regional FFT, segmentation alignment, subject texture, subject process asymmetry, subject material realism and patch-spatial analysis. Independent stages continue. Intrinsic edge measurements are not promoted to validated person-boundary findings.

For each image, repeated summary construction produced identical reasoning dictionaries. With shadow mode enabled, `scorecard`, `decision`, `hypothesis_assessments`, `confidence_policy` and `corroboration_audit` exactly equaled the normal-mode values. Final confidence appeared in both rendered text and HTML. Original-image SHA-256 hashes before and after execution matched:

- Instagram: `1feeccab1ddce2b24ddec95447e5c86cbbf2b77deabf7b01c76bdf3388d219f9`.
- Midjourney: `08c27f51a3bc9f6546d9ca3f99ad910ae293d2610679d1fdea6e53130902dda9`.

Native runtime diagnostics included TensorFlow Lite XNNPACK initialization and MediaPipe feedback-tensor warnings. These were not pytest warnings or recorded failed pipeline stages. GUI interaction, packaging and cross-platform execution were not performed; those are not inferred from headless success.

## E. Mathematical verification

The audit runner implements its own arithmetic replay without importing the production reconstruction/validation helpers. It uses literal status weights (weak 0.5, medium 1.5, strong 3.0), reconstructs separate suspicious/benign domain bonuses at 0.25 per additional domain, replays serialized add/multiply/maximum operations, checks raw and final component snapshots, and compares card and serialized aggregate values within relative/absolute tolerance **1e-12**.

Let `B_s` be the suspicious base, `Q` be `B_s + synthetic_boost + edit_boost + provenance_boost + sensor_boost + compression_boost`, `m` the measured-camera attenuation, `P` the final caution penalty, `g` the aggregate geometry factor and `p` the photo-context factor. Production's final aggregate is:

`S = max(0, Q*m - P)*g*p`; benign aggregate is its separately reconstructed base.

| Replay quantity | Instagram | Midjourney |
|---|---:|---:|
| Suspicious base | 23.0 | 9.0 |
| Benign base | 2.25 | 1.5 |
| Final subtotal Q | 25.973 | 9.75 |
| Measured camera support | 1.25 | 1.25 |
| Camera multiplier m | 0.85 | 0.85 |
| Caution P | 1.6 | 2.25 |
| Geometry g / photo p | 1.0 / 1.0 | 1.0 / 1.0 |
| Replayed S | **20.47705** | **6.0375** |

Thus `(25.973*0.85)-1.6 = 20.47705`, and `(9.75*0.85)-2.25 = 6.0375`. All final contributions match ledger replay. The runner independently checks reliability-operation occurrence counts and transform factors. These two images do not exercise every attenuation branch: the suite separately covers geometry mechanism factor 0.45, reduced boundary reliability, their declared order/exactly-once use, geometry aggregate factor 0.75, photo factor 0.70, measured-camera attenuation thresholds and separate routing/context bonuses. NaN/infinity abstention was independently probed; oversized-integer failure is explicitly F02.

The integrity validator also rejects duplicated/missing adjustment operations, incorrect raw/final boundaries, altered penalties and serialized inconsistencies. Deterministic arithmetic and honest missing-evidence treatment are demonstrated. They do not resolve F01: an exactly calculated sum can still contain unjustified repeated evidential credit.

## F. Confidence-policy verification

The normal call chain is GUI/controller state → `build_summary_result` → `synthesize_overall` → `evaluate_hypotheses` → scoped evidence → `_apply_confidence_policy` → `finish_decision`. Every authoritative final tier in this chain comes from `evaluate_confidence`. The invalid-scorecard early return also invokes policy and names `integrity.invalid_scorecard`; the finisher's fallback invokes policy if prior policy results are absent.

Selection compares typed findings/specificity and scoped priority rules before policy application. It does not rank candidates by their legacy High/Medium/Low labels. Policy facts contain typed findings, score/support/reliability/gate/provenance observations and coverage, not route names, prose or legacy confidence. Selected tiers are restored in the finisher; route-trace confidence is replaced with the corresponding assessment policy result, while `legacy_confidence` remains diagnostic. Unassessed alternatives do not become authoritative final tiers.

Reliable localized compounds can support High without transferring High to synthetic origin. The generic High source-diversity requirement is lineage aware. Rejected geometry and limited boundary support cap the appropriate mechanism even if safeguard routes are omitted. Missing detector coverage becomes a limitation rather than negative evidence. Contradictions and moderators remain scoped to their assessment. Every final assessment includes a rule and rationale, and the final decision repeats the primary assessment's tier.

An unverified declaration gives Medium for declared generation context; it does not authenticate metadata or prove pixel origin. Enhancement is distinct. C2PA presence/JSON verification booleans cannot create a trusted result. Confidence is explicitly qualitative heuristic support, not a probability. No route-specific authoritative-confidence bypass was found in normal, invalid-card, reordered-route or tested safeguard-omission paths. F03 remains an explicit limitation of alternate internal assessment construction.

## G. Corroboration verification

The registry covers the 20 built summary sections and contextual controls. Its dependencies agree with controller and detector consumption: ELA/residual feed convergence and boundary interpretation; masks constrain localized consumers; patch-spatial consumes patch matches; asymmetry can consume optional texture/regional-FFT payloads. Regional FFT computes its own regional transforms rather than consuming the global FFT result. Material realism shares some feature code with asymmetry but is not simply a consumer of its result payload. Shared code is not automatically identical measurement. Controls/masks are not counted as independent forensic sources.

The production generic diversity gate uses a maximum set of measurement-disjoint eligible witnesses. It preserves separate primary extractions even if a composite links them, rejects missing/unknown lineage as a basis for new source credit, checks hypothesis/polarity/availability, and records exclusions and ancestry. It does not claim statistical independence. Boundary and synthetic mechanism predicates explicitly remain compound-interpretation conditions; their shared ancestry is allowed and recorded instead of being relabeled independent confirmation.

The required distinctions are:

| Category | Audit determination |
|---|---|
| Duplicate numerical contributions | **Unresolved in production** for potentially redundant overlapping interpretations/localizations; concrete active paths are F01. No justified total overcount or replacement coefficient is established by this audit. |
| Duplicate independent-source credits | Corrected in the generic High gate: descendants cannot satisfy extra disjoint-source requirements. Multiple measurement primaries are preserved. |
| Legitimate compound evidence | Retained. A spatial/semantic relationship can be useful without being a new independent measurement. Compound gates are not automatically defects. |
| Repeated narrative presentation | A signal may appear in a primary explanation, per-hypothesis lists and trace. Repetition in presentation is not an additional score operation. |
| Empirically unverified correlation | Feature/content overlap is disclosed. A broad statistical calibration project is not automatically necessary for acceptance; F01 rests on actual computational reuse and unreconciled numerical credit. |

`allocate_marginal` can suppress explicitly designated pure restatements in shadow analysis, but retains unvalidated localization/interpretation margins provisionally. Explicit experimental credits stay outside production. Shadow failures are isolated by tests, and fresh normal/shadow comparison confirms no production decision changes. Therefore Phase 2B's structural/gate work is meaningful, but it is not equivalent to completion of the original numerical double-counting correction.

## H. Compatibility

- **Synthesis API:** the existing positional arguments and five-element return `(pattern, text, confidence, polarity, trace)` remain. Dependency shadow/coverage are additive keyword arguments. Existing successful, missing-evidence and invalid-card integrations are tested.
- **JSON/text/HTML:** legacy decision and scorecard fields remain, with additive hypothesis roles, calculation ledger, policy and corroboration data. Old traces lacking newer role fields still render. Final rendered confidence and role lists use the authoritative primary assessment. Round-trip tests and fresh persistence succeeded. Compatibility evidence does not prove every unversioned external consumer tolerates additive fields.
- **Trace scope:** normal traces contain section observations, derived/provenance state, candidate route dispositions, complete assessments, ledger, policy, reliability/coverage and gate-specific lineage. Full dependency lineage/component diagnostics require `evidence_dependency_shadow=True`; GUI default does not request that full sidecar. Raw detector arrays/images remain separate local analysis artifacts, not a promise that the reasoning JSON alone can rerun all detectors.
- **Controller/GUI:** `signallens_controller.py:309 run_analysis` and mask-contract stage handling preserve unavailable versus failed status. `signallens_gui.py:317` consumes `build_summary_result(...).full_html`; it does not recompute confidence. Summary persistence retains JSON/text/HTML. The suite's GUI-consumption test uses a constructed state, not live Qt interaction. GUI responsiveness, dialogs and packaged distribution were not exercised.
- **Runtime:** installed MediaPipe 1.2.0 successfully executes both original images. The earlier ExifTool/MediaPipe dependency update is already in history, not part of this audit's dirty implementation. No dependency or packaging change is proposed. No claim of cross-platform verification is made.

## I. Git readiness

### Inventory and hygiene

Branch: `fix/scorecard-integrity-phase2a`; HEAD `f64f226`. Recent history already contains `5da828e` (ExifTool 13.60 / MediaPipe 1.2.0 dependency record), `e8b672c` cleanup and `f64f226` Phase 1. Reasoning/metadata/scoped-evidence/mask work already present at HEAD must not be presented as newly introduced by the current six-file tracked diff.

The inherited tracked diff is **6 files, 501 insertions, 242 deletions**:

`decision_logic.py`, `hypothesis_engine.py`, `hypothesis_evidence.py`, `reasoning_persistence.py`, `signal_language.py`, `summary_synthesizer.py`.

Untracked implementation: **7 modules** — `scorecard_integrity.py`, `evidence_lineage.py`, `marginal_corroboration.py`, `evidence_dependency_analysis.py`, `production_corroboration.py`, `confidence_policy.py`, `confidence_policy_inputs.py`. Untracked regression files: **4** — `tests/test_scorecard_integrity.py`, `tests/test_evidence_lineage.py`, `tests/test_production_corroboration.py`, `tests/test_confidence_policy.py`.

Untracked prior documentation: `doc/scorecard_integrity_phase2a.md`, **15 files** in `doc/phase2b_evidence_dependency/` (12 Markdown documents, `audit_dependency.py`, two CSV inventories), and **4 Markdown files** in `doc/phase3_confidence_policy/`. The phase 2B CSVs are intended evidence inventories, not leaked image payloads. The five untracked root task specifications are `Forensic Evidence Dependency & Double-Counting Audit.md`, `Evidence Lineage & Marginal Corroboration.md`, `Production Corroboration Integrity.md`, `Hypothesis-Aware Confidence Policy Consolidation.md`, and this audit's input task. Their inclusion as project documentation should be an explicit review choice.

This report is the only new nonignored audit deliverable. Supplementary audit scripts, environment/inventory records, probes, image outputs and traces are under ignored `analyzed/final_acceptance_audit/`. Existing phase-specific patch artifacts remain local comparison/recovery aids; their existence does not prove that they can be applied independently to the final shared-file diff.

Checks: index empty; `git diff --check` reports no whitespace errors. Git reports an LF-to-CRLF notice for `hypothesis_evidence.py`; no normalization was performed. `git check-ignore` confirms both reference-image paths/output locations are ignored, and `git ls-files -- test_images analyzed` returns no tracked files. Changed/untracked candidate files contain no binary/NUL content, no matches for the audit's private-key/token/credential-assignment patterns, and no absolute user-profile/workspace path matches. This is a bounded change-set scan, not a comprehensive security audit of repository history. Tests reference ignored images by relative path; no image contents were added to fixtures. No unrelated detector algorithm or dependency changes appear in the inherited tracked diff.

An initial SHA-256 manifest protects **82** pre-existing source/test/document files. Final verification matched all **82**, with **0 changed files**, excluding this new report. No staging, commit, push, tag, merge, stash, reset or deletion was executed.

Continuation verification on 2026-11-01: the complete suite passed again (**297 passed in 2.91 seconds; 0 failed; 0 skipped**). The initial sandboxed attempt encountered Windows temporary-directory permission errors in 28 fixture setups; the rerun with approved directory access completed successfully. Saved reference results confirm baseline score equality, deterministic summary construction and shadow/production equality for both images. The reference pipelines were not rerun during this continuation; the fresh executions documented in section D remain the image-run evidence.

### Recommended commit plan — recommendation only

Do not label the current state a closed ten-correction baseline until F01 is resolved. Preserve/review the current work independently of that closure claim. Logical review groups are:

1. **Phase 2A mathematics:** `scorecard_integrity.py`, corresponding engine/decision/persistence hunks, its regression file and Phase 2A document.
2. **Phase 2B lineage/shadow and production corroboration:** four lineage/allocator/dependency/corroboration modules, associated decision/language/persistence hunks, two regression files and dependency documentation/inventories. Separate shadow from production gate changes if the existing phase patches can be verified against their actual bases.
3. **Phase 3 confidence policy:** two policy modules, associated hypothesis/decision/summary/evidence/persistence hunks, policy tests and four policy documents.
4. **Acceptance record:** this report and deliberately selected task specifications, with F01 and any subsequent resolution recorded accurately. Keep ignored runtime/image artifacts excluded.

These groups share files and cannot safely be separated merely by staging whole filenames. Reconstruct and verify each intermediate state before splitting. If reliable separation cannot be demonstrated, prefer **one explicitly inventoried, reviewed accumulated implementation baseline commit**, followed by its acceptance record; do not manufacture historical phase commits from mixed final files. Run the established suite for the chosen baseline. The later F01 correction should have its own focused review and tests. No commit operation is authorized by this audit task.

## J. Final disposition and follow-up

| Issue | Blocks original roadmap closure? | Reason / exact affected modules | Minimal corrective action | Required follow-up regression |
|---|---|---|---|---|
| **F01: unresolved numerical overlap** | **Yes** | Original #6 includes numerical double-counting. `hypothesis_engine.py:compute_base_scores/compute_scorecard`, informed by `evidence_lineage.py` and `marginal_corroboration.py`, still fully accumulate related observation/domain/mechanism credit. | Review and resolve shared versus incremental credit for the existing affected paths; preserve justified compounds. Do not import arbitrary shadow weights. | Parent/descendant and peer-descendant production score/domain tests, preservation of distinct primaries and valid compounds, deterministic ledger reconciliation and both image reruns. |
| **F02: oversized numeric overflow** | No | `scorecard_integrity.py:finite_number`; `decision_logic.py:build_decision_env`. Exceptional malformed input crashes but does not produce a confident invalid conclusion. | Convert numeric overflow to controlled integrity failure. | Huge integer/overflow via public synthesis; Inconclusive named policy, no mutation. |
| **F03: internal route-subset/direct-finisher explanation** | No, for the current production API | `decision_logic.py:evaluate_hypotheses/finish_decision/route_fallback`. Registered synthesis path is coherent; unsupported partial construction can disagree with its policy-supported provenance. | Enforce/document preconditions or reconcile hypotheses and explanations before supporting partial route APIs. | Declaration fixture with omitted provenance route/direct finisher; selected pattern, explanation, roles and policy consistent. |
| **F04: inactive malformed details** | No | `scorecard_integrity.py:validate_score_inputs`; `hypothesis_evidence.py:scope_hypothesis_evidence`. Dictionary contract is violated by the probe, not by normal builders. | Validate structure or guard scoping access while retaining unavailable-evidence semantics. | Inactive list/scalar details fail safely; valid absent metadata stays neutral. |
| Full real-image/GUI automation | No | Existing tests use constructed observations/mocked pipeline stages; fresh headless image validation was performed separately here. | Optionally add an opt-in local image integration job and a small Qt consumption smoke test without committing images or local traces. | Explicit local fixture availability and skip reporting; no claim that mocks are full detector execution. |
| Full default lineage export / broad statistical calibration | No | Full lineage is optional; structural disjointness is not empirical statistical independence. Neither optional expansion is itself a newly imposed acceptance requirement. | Document export choice; pursue calibration only as a separately scoped project if needed. | Optional export-schema tests / separately designed calibration evaluation. |

**Final acceptance: 9 accepted; #6 partially accepted; none failed individually. Overall FAIL for closure because #6 remains materially incomplete.** The passing regressions and unchanged reference conclusions support continued review of the present implementation; they do not remove the blocker. This audit stops at findings and minimal follow-up requirements, without changing behavior to obtain acceptance.
