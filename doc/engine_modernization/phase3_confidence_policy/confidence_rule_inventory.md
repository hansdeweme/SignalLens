# Confidence rule inventory (Phase 3 baseline)

Baseline: branch `fix/scorecard-integrity-phase2a`, HEAD `f64f226`, inherited uncommitted Phase 2A-2B.3 work; 262 tests passed. Baseline line anchors refer to the preserved Phase 3 entry snapshot.

## Route-return assignments

26 return sites were inspected and consolidated into typed finding/evidence rules. Their provisional labels remain only for direct route-call compatibility and diagnostic comparison. They no longer determine final confidence or selection specificity. No policy rule receives the route name, branch string, narrative or provisional tier.

| Stable rule ID | Source | Hypothesis | Provisional assignment | Existing evidence / safeguard condition | Typed policy finding | Expected effect |
| --- | --- | --- | --- | --- | --- | --- |
| legacy.route_real_photo_context_prior.1 | decision_logic.py:749 route_real_photo_context_prior | localized_editing | 'Medium' | env.real_photo_context_prior and (not env.ds.metadata_synthetic) and (env.card.synthetic_boost <= 0.25) | PHOTO_CONTEXT | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_boundary_support_limited.1 | decision_logic.py:761 route_boundary_support_limited | localized_editing | 'Medium' | env.ds.strong_local_edit and env.ds.boundary_reliability_score < 0.6 | BOUNDARY_LIMITED | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_region_geometry_unreliable.1 | decision_logic.py:773 route_region_geometry_unreliable | localized_editing | 'Medium' | env.ds.region_geometry_unreliable and env.ds.strong_local_edit | GEOMETRY_LIMITED | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_localized_multi_mechanism.1 | decision_logic.py:793 route_localized_multi_mechanism | localized_editing | 'High' | env.card.local_edit_support_score >= 3.0 and env.card.clone_support_score >= 3.0 and (score_gap < 1.0) and (not env.card.contextual_false_positive_risk) | MULTI_LOCAL | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_strong_local_edit.1 | decision_logic.py:816 route_strong_local_edit | localized_editing | 'High' | env.card.local_edit_support_score >= 3.5 and env.card.local_edit_support_score >= env.card.clone_support_score + 1.0 and (env.card.camera_counter_support < 2.0) and (not env.card.contextual_false_positive_risk) and _boundary_corroborated(env) | BOUNDARY_DECISIVE | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_strong_local_edit.2 | decision_logic.py:831 route_strong_local_edit | localized_editing | confidence | env.card.local_edit_support_score >= 3.5 and env.card.local_edit_support_score >= env.card.clone_support_score + 1.0 and (env.card.camera_counter_support < 2.0) and (not env.card.contextual_false_positive_risk) | LOCAL_UNCERTAIN | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_clone_reuse.1 | decision_logic.py:852 route_clone_reuse | localized_editing | 'High' | env.card.clone_support_score >= 3.5 and env.card.clone_support_score >= env.card.local_edit_support_score + 1.0 and (env.card.camera_counter_support < 2.0) | CLONE_DECISIVE | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_moderated_local_edit.1 | decision_logic.py:872 route_moderated_local_edit | localized_editing | 'Medium' | env.ds.strong_local_edit and dominant_localized_score >= 2.5 and _boundary_corroborated(env) | BOUNDARY_SUPPORTED | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_moderated_local_edit.2 | decision_logic.py:884 route_moderated_local_edit | localized_editing | 'Low' | env.ds.strong_local_edit and dominant_localized_score >= 2.5 | LOCAL_WEAK | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_clone_ambiguous.1 | decision_logic.py:901 route_clone_ambiguous | localized_editing | 'Low' | env.card.clone_ambiguous and env.card.clone_support_score >= 2.0 and env.card.camera_counter_support >= 1.5 | CLONE_CAMERA_AMBIGUOUS | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_clone_ambiguous.2 | decision_logic.py:910 route_clone_ambiguous | localized_editing | env.confidence_tier | env.card.clone_ambiguous and env.card.clone_support_score >= 2.0 and env.ds.material_realism_strong | CLONE_MATERIAL_AMBIGUOUS | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_clone_ambiguous.3 | decision_logic.py:918 route_clone_ambiguous | localized_editing | 'Medium' | env.card.clone_ambiguous and env.card.clone_support_score >= 2.0 | CLONE_AMBIGUOUS | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_structured_recurrence_inconclusive.1 | decision_logic.py:943 route_structured_recurrence_inconclusive | synthetic_origin | 'Medium' | env.ds.fft_structured and env.ds.patch_structured and env.ds.local_signals_weak and env.ds.provenance_clean and (env.ds.coverage_ratio >= 0.18) and (env.ds.camera_like_support or env.ctx.decorative_geometric or env.ctx.natural_repetition or env.ctx.smartphone_computational or env.ctx.screen_origin) | RECURRENCE_CAUTION | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_synthetic_multi_signal.1 | decision_logic.py:988 route_synthetic_multi_signal | synthetic_origin | 'High' | env.card.synthetic_boost >= 1.0 and env.card.suspicious_score >= 5.0 and env.card.synthetic_supported_by_other_domains and (env.ds.fft_structured and env.ds.patch_structured or (env.ds.material_realism_strong and env.ds.subject_process_asymmetry_strong and (not env.ds.region_geometry_unreliable))) and (not (env.ds.local_signals_weak and env.ds.provenance_clean and (env.ds.coverage_ratio >= 0.18))) | VISUAL_GENERATION | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_localized_processing.1 | decision_logic.py:1000 route_localized_processing | localized_editing | 'Medium' | env.card.edit_boost >= 0.5 and env.card.suspicious_score >= 4.5 | LOCAL_PROCESSING | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_subject_boundary.1 | decision_logic.py:1017 route_subject_boundary | localized_editing | 'Medium' | env.ds.subject_boundary_strong and env.card.suspicious_score >= 4.0 | SUBJECT_BOUNDARY | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_unreliable_boundary_context.1 | decision_logic.py:1039 route_unreliable_boundary_context | localized_editing | 'Medium' | not env.ds.person_mask_reliable and env.ds.boundary_reliability_score <= 0.1 and (env.dominant_pattern in {'possible_boundary_transition_inconsistency', 'possible_subject_background_segmentation_artifact', 'possible_foreground_background_processing_mismatch'}) | UNRELIABLE_BOUNDARY | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_boundary_transition.1 | decision_logic.py:1056 route_boundary_transition | localized_editing | 'Medium' | env.ds.subject_boundary_medium and env.card.suspicious_score >= 3.5 and (env.ds.fragmented_local_edit or env.ds.strong_cross or env.ds.patch_structured) | BOUNDARY_TRANSITION | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_provenance.1 | decision_logic.py:1071 route_provenance | synthetic_origin | 'Medium' | state == ProvenanceState.UNVERIFIED_GENERATION_DECLARATION | GENERATION_DECLARATION | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_provenance.2 | decision_logic.py:1081 route_provenance | synthetic_origin | 'Medium' | state == ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION | ENHANCEMENT_DECLARATION | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_provenance.3 | decision_logic.py:1088 route_provenance | synthetic_origin | 'Low' | env.ds.osint_ai_context | SOURCE_CONTEXT | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_camera_like.1 | decision_logic.py:1108 route_camera_like | camera_acquisition | 'Medium' | env.ds.camera_like_support and env.ds.provenance_clean and env.ds.local_signals_weak and (env.card.suspicious_score < 4.0) | CAMERA_COMPATIBLE | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_multi_signal_suspicious.1 | decision_logic.py:1138 route_multi_signal_suspicious | unresolved_anomaly | 'High' | env.card.suspicious_score >= 7.0 and high_support_present and (not env.ds.local_signals_weak) and (not (env.ds.camera_like_support or env.ctx.natural_repetition or env.ctx.decorative_geometric or env.ctx.smartphone_computational or env.ctx.screen_origin)) | ANOMALY_ACCUMULATION | Mechanism meaning retained; general accumulation subject to centralized generic source-diversity policy |
| legacy.route_moderate_suspicious.1 | decision_logic.py:1152 route_moderate_suspicious | unresolved_anomaly | env.confidence_tier | env.card.suspicious_score >= 3.5 | GENERAL_ANOMALY | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_photo_like_consistency.1 | decision_logic.py:1172 route_photo_like_consistency | camera_acquisition | 'Medium' | env.card.suspicious_score < 1.5 and env.card.benign_score >= 2.0 and _photo_like_clean_signals(env) | PHOTO_CONSISTENCY | Existing meaning retained; required geometry/coverage explicitly reconciled |
| legacy.route_fallback.1 | decision_logic.py:1193 route_fallback | unresolved_anomaly | fallback_confidence | fallback | FALLBACK | Existing meaning retained; required geometry/coverage explicitly reconciled |

## Other confidence assignments and consumers

- Four generic helper branches (High/Medium/Low/Inconclusive) move to `confidence_policy.generic_confidence()`, preserving thresholds 3/2/1.2, the strong-observation count and the Phase 2B.3 source-diversity result.
- Five hypothesis construction/override paths (synthetic, localized, camera, unresolved, selected-camera override) become nonauthoritative placeholders; Stage D assigns every final tier after scoping.
- Invalid-scorecard return/default dataclass tiers are placeholders resolved by named `integrity.invalid_scorecard` policy before presentation.
- `build_confidence_rationale()` consumes authoritative policy rationale for new assessments; the old explanation-only path remains for legacy callers/traces.
- `finish_decision()`, summary JSON/text/HTML and GUI consumption use the primary assessment's policy tier, never the selected route's provisional label.
- `vf_person_subject_mask` detection confidence, ExifTool signal confidence, and module status strength are measurement metadata, not final forensic hypothesis confidence. They are inspected but not recalibrated.

## Contradictions, reliability and precedence

Existing boundary/person-geometry safeguards apply only to region-dependent interpretations; spatial reuse and declarations keep their own scope. Camera compatibility moderates unconfirmed localized mechanisms but does not disprove generation declarations. Direct boundary consistency remains contradictory within the boundary mechanism; it is contextual for clone reuse. Surviving compound evidence can retain its existing tier without a newly invented global contradiction deduction.

## Selection coupling removed

The old `_specific_finding()` and decisive-local selection branch read route confidence. They now use explicit finding specificity (unspecific/specific/decisive mechanism), preserving the same route evidence meaning and priorities. The primary hypothesis is selected before policy assignment and is not automatically changed to whichever secondary hypothesis receives the highest confidence.

## Named policy equivalents and evidence qualifiers

Each row is route-dependent only for the provisional diagnostic return; the final policy evaluates the complete hypothesis finding set and structured facts. The independent policy does not receive the route ID.

| Typed finding | Named policy rule | Contradiction / moderation scope | Reliability / coverage controls |
| --- | --- | --- | --- |
| PHOTO_CONTEXT | localized.photo_context_ambiguity | Camera context moderates local interpretation; not contradiction | Existing photo-context prior |
| BOUNDARY_LIMITED | localized.boundary_support_limited | No automatic penalty on generation | Boundary support <0.6 |
| GEOMETRY_LIMITED | localized.geometry_limited | Local mechanism only | Unreliable region geometry |
| MULTI_LOCAL | localized.multiple_mechanisms | Distinct mechanisms; retain scoped contradictions | Person/geometry support; existing local/clone requirements |
| BOUNDARY_DECISIVE | localized.reliable_boundary_compound | Boundary contradiction retained if other compound support survives | Person/geometry, r>=0.6 and compound requirement |
| LOCAL_UNCERTAIN | localized.camera_moderated_uncertainty / localized.unspecific_local_processing | Camera observation moderates rather than disproves editing | Unconfirmed compound; existing camera restriction |
| CLONE_DECISIVE | localized.spatial_reuse | Boundary consistency is contextual for copy-move | Existing spatial-reuse score/dominance; boundary caps do not erase reuse |
| BOUNDARY_SUPPORTED | localized.supported_boundary | Scoped boundary challenge remains visible | Applicable person/r support and compound gate |
| LOCAL_WEAK | localized.limited_mechanism | Insufficient mechanism corroboration | No invented evidence from missing detectors |
| CLONE_CAMERA_AMBIGUOUS | localized.reuse_camera_ambiguity | Camera compatibility moderates ambiguous reuse | Existing clone ambiguity and camera support |
| CLONE_MATERIAL_AMBIGUOUS | localized.reuse_ambiguity.generic.* | Material regularity does not establish copy-move or generation | Existing generic source-diversity support |
| CLONE_AMBIGUOUS | localized.reuse_unspecific | Natural repetition remains plausible | Spatial/mechanism uncertainty recorded |
| RECURRENCE_CAUTION | synthetic.recurrence_ambiguity | Context affects visual recurrence, not authenticated origin | Existing recurrence/context guard |
| VISUAL_GENERATION | synthetic.visual_compound | Camera observations are moderation; no generic transfer | Existing visual compound; regional branch requires reliable person geometry |
| LOCAL_PROCESSING | localized.qualified_processing | Unspecific processing is not AI-generation proof | Existing edit support; applicable missing coverage disclosed |
| SUBJECT_BOUNDARY | localized.qualified_processing | Intrinsic edge evidence is not a person contour by itself | Person/r geometry cap reconciled |
| UNRELIABLE_BOUNDARY | localized.person_boundary_unavailable | Does not refute generation declaration | Required person support unavailable |
| BOUNDARY_TRANSITION | localized.qualified_processing | Qualified mechanism only | Person/r support reconciled |
| GENERATION_DECLARATION | synthetic.unverified_generation_declaration | Camera-compatible observations do not refute declaration | Authenticity remains unverified; no regional requirement |
| ENHANCEMENT_DECLARATION | synthetic.unverified_enhancement_declaration | Enhancement differs from whole-image generation | Unverified declaration cap |
| SOURCE_CONTEXT | synthetic.source_context | Reviewed source is contextual rather than authenticated | Source-context limitation |
| CAMERA_COMPATIBLE | camera.acquisition_compatibility | May coexist with generation and local editing | Existing camera compatibility, no authenticity proof |
| ANOMALY_ACCUMULATION | generic.* | Anomaly magnitude does not identify a mechanism | Existing 2B.3 distinct-source gate; no route-High bypass |
| GENERAL_ANOMALY | generic.* | No confidence transfer to specific origin | Existing 2B.3 generic support thresholds |
| PHOTO_CONSISTENCY | camera.acquisition_compatibility | Photo-like coherence is not cryptographic acquisition proof | Existing consistency conditions; limitations retained |
| FALLBACK | generic.* | Unresolved interpretation remains unresolved | Existing generic support and coverage |
