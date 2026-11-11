# Static coverage audit and bounded follow-up plan

Task C only: zero tests added, changed, collected or executed. No fixtures, baselines or production modules changed. Existing acceptance evidence is Task B's documented **521 passed**; it was not rerun or presented as validation of a future correction. Test count remains unchanged by this task: added/consolidated/removed **0/0/0**, net **0**.

Read `AGENTS.md`, `doc/test_quality/TEST_DISCIPLINE.md`, Task A's five reports, Task B's implementation report and the relevant test bodies/fixtures. Below, coverage is what the inspected assertions protect, not an inference from names or a claim of empirical forensic calibration.

## Existing coverage and specific gaps

| Behavior | Existing test bodies inspected | Coverage and genuine gap |
|---|---|---|
| General primary selection | `tests/test_reasoning.py::test_irrelevant_route_order_does_not_change_assessments`; `tests/test_confidence_policy.py::test_tampering_with_every_route_tier_cannot_change_selection_or_policy`, `test_policy_does_not_promote_the_highest_confidence_secondary_to_primary` | Deterministic route evaluation, tier authority and avoiding maximum-secondary-tier selection are protected. Does not prove that unlike causal categories should compete under the old primary meaning. |
| Structured ComfyUI creation history | `tests/test_reasoning.py::test_connected_workflow_process_and_unverified_semantics` (four process cases), `test_embedded_prompt_propagates`, `test_enhancement_is_distinct_from_generation` | Connected full generation, external image, masked and unknown-node semantics; duplicate representation count, false enhancement and unverified trust. Does not establish a generalized conclusion contract for all formats. |
| Non-graph generation declarations | `tests/test_reasoning.py::test_midjourney_raw_metadata_path_regression`, `test_midjourney_prompt_signature_is_not_just_an_arbitrary_description`, `test_iptc_source_type_alone_is_scoped_unverified_declaration`; `test_metadata_only_generation_declaration` | UUID/parameters/version signatures, exact IPTC values, supporting roles and Medium unverified context are covered. No assertion reconciles non-graph declarations with the graph-only causal record's null/not_assessed fields under strong regional evidence. |
| Conflicting boundary observations | `tests/test_confidence_policy.py::test_direct_contradiction_changes_mechanism_eligibility_without_global_penalty`, `test_counter_evidence_is_not_deleted_when_other_compound_support_survives`; `tests/test_hypothesis_scoping.py::test_weak_zero_score_boundary_counterevidence_is_not_hidden` | Explicit benign/convergence counter-evidence is retained and can affect eligibility. These fixtures use zero benign scores or other strong witnesses; they do not catch **nonzero inconclusive Focus supplying strength** while excluded from positive indicator count. |
| Limited-quality masks | `tests/test_mask_pipeline.py::test_high_and_medium_person_masks_retain_regional_execution` (high/medium), `test_low_mask_is_controlled_unavailable_and_independent_stages_continue`, `test_image_edge_detector_needs_valid_person_geometry_for_person_specific_interpretation` | Usable medium geometry versus rejected/approximate geometry and demotion of unvalidated edge interpretations are covered. Does not prove actual edge-to-person alignment or carry medium-quality limitations into distinct conclusion dimensions. |
| Subject-dominant images | `tests/test_mask_pipeline.py::test_original_midjourney_coverage_is_rejected_by_unchanged_quality_policy` uses 92% foreground; medium fixture uses about 88% foreground | Area eligibility/rejection is protected. No direct production asymmetry test for this 86%-pixel/43%-sample distinction, repetitive-background baseline, or semantic interpretation of fallback. Heavy asymmetry implementations are stubbed in pipeline tests. No new area threshold is justified. |
| Regional anomalies without a proven edit | `tests/test_reasoning.py::test_strong_local_edit_is_not_overwritten_by_metadata` includes structured generation plus qualified lead; `tests/test_overview_workspace.py::test_primary_pattern_and_exact_confidence_are_recorded` projects a supplied causal lead | Task B's additive qualification is protected and legacy local primary is deliberately retained. Missing is authoritative dimensional edit-history status distinct from anomaly tier, independent of metadata format. |
| Synthetic versus localized evidence | `tests/test_reasoning.py::test_localized_visual_signals_do_not_become_generation_from_metadata`, `test_supported_visual_generation_survives_local_uncertainty`, `test_boundary_safeguards_do_not_block_generation`; `tests/test_hypothesis_scoping.py::test_all_three_hypotheses_remain_visible_and_deterministic` | Prevents transfer of local High to generation, preserves competing assessments and scoped geometry constraints. Future causal eligibility needs an intentional new contract, not deletion of these safeguards. |
| Strong patch / weak spatial support | `tests/test_hypothesis_scoping.py::test_spatial_corroboration_is_needed_to_present_copy_move_support`, `test_boundary_consistency_is_not_a_contradiction_of_clone_reuse`; `tests/test_reasoning.py::test_clone_reuse_is_independent_of_boundary_safeguards` | Role-level spatial corroboration and true reuse independence from person-boundary safeguards are covered. No direct case protects a completed **inconclusive** spatial outcome from being discarded before clone ambiguity checks. |
| Source URL annotations and OSINT | `tests/test_provenance_reporting.py::test_osint_workspace_displays_committed_source_and_revision`; `tests/test_investigation_gui.py::test_cancelled_dialog_and_switched_session_cannot_commit_annotations`, `test_annotation_save_failure_does_not_commit_draft` | Actual committed URL/notes display, revision/session ownership and persistence failures are covered. No retrieval, exact hashing, perceptual matching or creator-claim/dependency contract exists to validate. These tests must not be described as source-authentication coverage. |
| Frozen forensic result versus corroboration | `tests/test_investigation_gui.py::test_osint_edits_refresh_view_and_report_without_any_resynthesis`; `tests/test_investigation_contracts.py::test_annotation_revisions_freeze_forensics_and_invalidate_old_report`, `test_new_report_load_preserves_forensic_fields_and_does_not_reappend_old_annotations` | Explicitly forbids post-analysis synthesis, checks unchanged trace and current annotation appendix. Reuse these owners; new external interpretation belongs to a separate versioned report contract, not a mutable old trace. |
| GUI/report consistency | `tests/test_hypothesis_scoping.py::test_json_and_all_narratives_use_the_authoritative_assessment`, `test_rendering_through_summary_builders_includes_scoped_lists`; `tests/test_confidence_policy.py::test_json_and_text_use_one_authoritative_policy_for_all_hypotheses`; `tests/test_investigation_contracts.py::test_presentation_preserves_hypotheses_roles_policy_sources_and_input`; Overview test above | Projected recorded fields and shared narrative/tiers are protected. They can consistently display the same semantically overloaded result; no current test establishes the missing origin/anomaly/edit dimensions. |

Lineage/numerical owners remain authoritative: `tests/test_production_corroboration.py::test_primary_and_two_descendants_cannot_be_three_sources`, `test_true_compound_boundary_condition_is_not_replaced_by_source_uniqueness`, `test_texture_and_asymmetry_share_ancestry_while_own_measurements_remain_visible`, `test_metadata_and_pixels_are_different_sources_without_authenticating_declaration`; `tests/test_numerical_evidence.py::test_identical_observation_repeated_in_production_gets_one_base_credit`, `test_fragment_restatement_and_its_domain_are_suppressed_in_public_synthesis`, `test_uncertain_shared_surface_information_is_preserved_and_flagged`, `test_contradictory_polarity_is_not_erased_by_related_supporting_measurement`.

Their bodies distinguish source diversity from compound interpretations and preserve explicitly uncertain overlap. They do not validate marginal detector weights empirically. In particular the compound test supplies a **positive** Focus score of 8; it is not a negative control for a score of 2.154 on an inconclusive Focus result.

## Minimal implementation sequence, not executed

### 1. Define the outcome and strength contracts

Owner: `decision_logic._boundary_corroborated`, relevant `confidence_policy_inputs` facts and trace gate serialization. Specify eligible positive indicators independently of strength witnesses, require compatible per-detector strength semantics, and record actual witness provenance. Preserve existing positive compound support and scoped counter-evidence. Do not use a raw maximum across normalized anomaly units and intensity units. No threshold/weight changes are needed to demonstrate or repair ineligible-witness consumption.

Keep complete measurement outcome (`observed_support`, `observed_nonconfirming`, `inconclusive`, `missing`, `unavailable`, `failed`) separate from positive scoring eligibility. `scorecard_integrity.available_sections` may still guard positive credit; ambiguity/applicability facts must be derived from the unfiltered completed section status. Review `hypothesis_engine.py:508-572` consumers so existing ambiguity intent is not silently bypassed. Do not make absent measurements negative or blindly restore unreviewed penalties.

### 2. Add authoritative multidimensional synthesis

Owner: a small immutable conclusion type/adapter, likely `decision_logic.py`, `metadata_evidence.py`, `summary_sections.py`, `confidence_policy.py`/`confidence_policy_inputs.py` only where distinct claim facts are needed. Use the shape in [architecture review](origin_processing_architecture.md). Preserve numerical detector observations and ledger. Any route/tier changes from repaired eligibility must be reported explicitly.

Recognize declarations independently of graph support: controlled vocabulary and guarded text signatures establish declared generation context, not detailed graph topology. Map known unverified provenance consistently across fields; do not label the general technical claim not_assessed merely because detailed process interpretation is unavailable. Preserve generator attribution as unauthenticated context.

Require explicit operation/mechanism eligibility before an edit-history conclusion competes with origin. Allow simultaneous origin declaration, processing observations and unresolved separate-edit status. Keep decisive spatial reuse scoped; never add an automatic metadata-priority rule or transfer anomaly High to generation High.

### 3. Project one recorded conclusion consistently

Owners: `presentation_models.py`, `investigation_presenters.py`, `overview_workspace.py`, existing Reasoning/Provenance adapters, `reasoning_persistence.py`, shared text/HTML builders. Display each tier with its actual claim. Generate the primary/headline from recorded typed dimensions, not from the largest tier or a renamed legacy identifier. Preserve existing surfaces; no new workspace is required.

Store versioned optional fields; retain legacy primary/tiers with explicit compatibility meaning. Old investigations remain frozen and use historical fallback without reclassification. No baseline regeneration or mass migration.

### 4. External evidence: record appropriately, defer new network features

For this case, an analyst can record the checked source URL, exact matching asset/hash, inspection date and source claim in existing annotations. Any later structured corroboration object should distinguish URL-only, inspected claim and match evidence plus dependency and technical authenticity. Do not update the frozen analysis in place. Network retrieval/scraping/API integration and perceptual matching are separate potential projects, not prerequisites for the core semantic fix.

## Minimum future test changes

Recommend **four additional collected cases** for the core correction, extending existing groups rather than creating new modules:

1. Two closely related negative strength-witness cases: nonzero inconclusive Focus and nonzero explicitly benign Focus cannot supply affirmative strength when eligible supporting strength is insufficient. Reuse existing positive compound controls. This protects the newly demonstrated gate defect without re-testing all routes.
2. One completed-spatial-outcome case: an inconclusive completed result must survive as an ambiguity/applicability fact, distinct from absent/not-run evidence, without gaining positive score or becoming a fabricated negative measurement. Reuse existing inactive-source and clone-scoping tests for other availability guarantees.
3. One non-graph generation-plus-regional-evidence integration case asserting the authoritative origin/anomaly/edit/authenticity dimensions and qualified unresolved relationship. Use simple Midjourney-format/controlled-vocabulary metadata, independent of source filenames. Existing graph and metadata-only cases can be extended to assert the same contract without additional cases.

Extend existing presentation/render/immutability/trust tests for the new fields and source-record status; do not duplicate lifecycle/export matrices. A source retrieval/matching implementation, if separately authorized later, would need its own minimal exact/mismatch/perceptual distinction coverage. It is not part of these four proposed core cases. No tests or fixtures were written during Task C.

Before later implementation, record current collection, inspect these owner bodies again, and use focused checks during development plus one full final acceptance gate as repository policy requires. This audit's zero-execution restriction is not permission to skip acceptance of actual code changes.

## Essential acceptance criteria

- A neutral/inconclusive observation cannot supply positive compound strength; witness field/status/scale is traceable. Real positive/independent reuse support survives.
- A completed nonconfirming spatial check is not silently changed into absence, and absent evidence does not become negative evidence.
- Non-graph declarations and graph declarations share general origin/authenticity semantics without fabricating a detailed creation process or authenticated origin.
- Regional-anomaly support does not establish separate editing or chronology. The overall lead presents the dimensions together when causal selection is unresolved; it does not force generation High.
- Boundary Focus/alignment limitations and mask/background applicability remain visible without a universal inconclusive veto, arbitrary mask cap or new weights.
- The supplied case is compared using its exact source hash, profile/settings and frozen measurements; changed outcomes from repaired eligibility are disclosed. No reference baselines are rewritten to conceal regressions.
- The GUI, saved JSON, reasoning trace and text/HTML/exported reports consume the same recorded typed conclusion. Old saved investigations and later annotation revisions remain immutable and identity-bound.
- Existing authoritative score arithmetic, source-diversity, confidence, session and report ownership tests remain green. No calibrated probability or population accuracy claim is invented.

## Risks, rollback and readiness

Risks: changing meaning while retaining legacy field names; treating unsigned declarations or an exact hosted-file match as authenticated origin; overcorrecting inconclusive evidence into a global veto; restoring unreachable clone penalties without confirming intended semantics; replacing detector scales with arbitrary normalization; and silently recomputing old reports.

Mitigation: explicit versioned claim/outcome records, no generic tier ranking, source-linked strength predicates, additive legacy compatibility, small isolated fixes and one authoritative projection. Keep empirical threshold calibration outside this change. Revert only future implementation commits to roll back; historical artifacts remain untouched and optional fields can be ignored by older readers.

**Readiness: Ready for separately authorized implementation of the bounded state/semantic correction.** No missing trace or image blocks it; exact source correspondence is established. Per-detector strength-witness semantics and the final versioned contract must be agreed/documented during implementation. Broader numerical recalibration, autonomous source retrieval and perceptual matching remain separate scope decisions.

## Task C verification

A 156-entry status/content fingerprint was captured before investigation. Final verification compares the pre-existing readable files and Git statuses, with pre-existing unreadable paths explicitly marked rather than claimed content-verified. Only these four requested Markdown documents may be added. No tests, production files, saved reports, original images, settings or existing audit documents are changed by Task C; no dependency was installed and no staging, commit, tag, publish or push was performed.

Observed final comparison: **156 existing entries unchanged; four authorized Markdown additions; zero staged entries.** Relative documentation links and source-reference bounds were checked. No full suite, focused test, image-analysis stage or exploratory regression harness was executed.
