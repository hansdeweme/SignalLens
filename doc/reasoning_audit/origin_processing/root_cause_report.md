# Task C: origin versus regional processing

Date: 2026-11-08. Investigation/documentation only. Working tree based on `main`, HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`, including inherited Task B changes and subsequent user work. No implementation or test execution occurred.

## Executive conclusion

Three distinct issues explain this case:

1. **Semantic selection mismatch:** a boundary-anomaly finding still has the machine meaning `BOUNDARY_DECISIVE` / `localized_editing` and wins causal precedence, even though Task B's explanation explicitly says a separate edit is not established. Task B intentionally preserved selection and added qualifications afterward. It did not create separate authoritative origin, anomaly and edit conclusions.
2. **Graph-only declaration/trust projection:** the added causal record reads only `workflow_interpretation`. Non-graph generation declarations are recognized elsewhere but disappear from its `declared_process` and authenticity fields. Consequently `not_assessed` in the causal record conflicts with the broader provenance record's explicit unverified declaration. This is a scope/adapter defect, not absence of generation evidence.
3. **A newly demonstrated boundary-strength gate defect:** an **inconclusive** Boundary Focus score of 2.1537491083 supplies the compound rule's strength requirement. That observation is excluded from positive indicator counting, but not from the raw maximum used for strength. The only scored supporting indicator is Subject Boundary at 0.3933162994, below 0.45. Mixed score scales aggravate the defect.

There is also a separate availability-state defect: the completed, spatially inconclusive patch result is filtered out before clone ambiguity/damping checks. This explains why the trace says `clone_ambiguous=false` despite that result. It does not make the selected route a clone route.

The result is arithmetically reproducible from current rules but semantically overloaded. “High regional-anomaly support” and “a separate edit is not established” can coexist. Calling their combined result the **primary editing hypothesis**, using decisive-mechanism specificity, and placing it ahead of the origin declaration is misleading. A label change alone is insufficient. Recommend the bounded multidimensional model and state/eligibility repairs in [architecture review](origin_processing_architecture.md) and [implementation plan](test_coverage_and_implementation_plan.md).

## Exact investigation artifact

The supplied numerical signature occurs in this existing report revision; no substitute image was used:

**RUN**:

`analyzed/high-quality, realistic fashion portrait of a young woman , soft hair, natural dabbled window light f 1.8/11c6caab8e124743badec2d6925d5143/90275a72b4794b7292ab0ad2889962fc/`

**TRACE**:

`RUN/report_revisions/90275a72b4794b7292ab0ad2889962fc-a0-77ae98a3e0734857a2cd21d7150a35a6/summary/reasoning_trace.json`

Companion `final_summary.json`, `RUN/analysis_run.json`, saved ELA/residual/patch/extractor JSON and mask diagnostics were inspected read-only. Useful TRACE anchors: causal record line 3; boundary compound line 149; generic diversity line 201; decision line 360; derived signals line 823; provenance authenticity line 1894; scorecard line 1897; Boundary Focus score line 2578.

Original source exists:

`test_images/midjourney/high-quality, realistic fashion portrait of a young woman , soft hair, natural dabbled window light f 1.8.png`

SHA-256: `b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`. Size 1,958,740 bytes; dimensions 928 x 1232. The saved investigation annotation identity has the same hash. Prepared person geometry is 771 x 1024. Profile is `normal`; all recorded scene-context flags are false. Persisted patch settings: size 24, stride 12, descriptor size 8, threshold 0.965, retained-pair limit 300, overlay limit 60.

No forensic pipeline or detector was rerun. Inspection commands read source/JSON and compared file hashes; they were not an exploratory test harness. Prior reports and all production modules modified during Task B were reviewed, together with the policy, metadata, presentation and mask test owners.

## External correspondence: confirmed, with limited claim scope

The [reference article](https://embracepresets.com/best-midjourney-prompts-for-realistic-photos/) describes its second example as generated imagery. Its linked [PNG asset](https://embracepresets.com/wp-content/uploads/2024/08/theart1300_httpss.mj_.runhx-xd-s5Gos_real_photo_-chaos_10_-a_33717b8b-eb01-4bd6-8719-f4b4c9d59fa8_3.png) was retrieved once into memory on 2026-11-08. Its SHA-256, byte size and decoded dimensions match the analyzed source exactly; byte comparison and decoded RGB comparison both returned true. This is stronger than filename, prompt or visual similarity alone.

The local descriptive filename follows the article's example caption, while the actual asset filename and embedded job identifier are different. Exact byte equality resolves that mismatch. The page's claim and file correspondence are confirmed; neither authenticates Midjourney execution, authorship, chronology or absence of subsequent editing. No webpage text or remote asset was persisted outside these four audit documents, and no source annotation was injected into SignalLens.

## A. Evidence aggregation to the primary finding

| Stage | Source and function | Confirmed behavior |
|---|---|---|
| Aggregate measurements | `hypothesis_engine.py:185`, `build_evidence_snapshot`; `:336`, `compute_scorecard` | Builds active evidence, derives pattern flags, records weighted scores and synergies. See [boundary audit](boundary_reliability_audit.md) for exact arithmetic. |
| Boundary candidate | `decision_logic.py:851`, `route_strong_local_edit` | 5.25 >= 3.5; 5.25 >= 2.10 + 1; camera 1.25 < 2; context risk false. Compound success returns `Finding.BOUNDARY_DECISIVE`. |
| Specificity | `confidence_policy.py:55`, `finding_specificity` | Boundary decisive is classified as decisive local mechanism; declaration is only specific. This classification survives Task B's weaker causal prose. |
| Candidate selection | `decision_logic.py:1336`, `evaluate_hypotheses`, especially 1368-1408 | Evaluates every route; sorts by priority/name; applies per-hypothesis safeguards and then cross-hypothesis precedence. A decisive suspicious local result wins at 1391-1393. It is not a route-order accident or maximum-confidence selection. |
| Scoped confidence | `decision_logic.py:1311`, `_apply_confidence_policy`; `confidence_policy.py:187`, `_localized` | Applied after selection. The passed boundary compound and geometry/score conditions yield `localized.reliable_boundary_compound: High`. Synthetic declaration independently receives Medium. |
| Causal qualification | `decision_logic.py:1515`, `_qualify_causal_interpretation` | Runs only after selection/confidence (caller at 1511-1512). It changes text and an additive record, not chosen hypothesis, route or tier. |
| Graph-only projection | Same helper, 1521-1529 and 1556-1559 | Reads only metadata `workflow_interpretation`; without it assigns null process and `not_assessed` authenticity. Ignores already-known declaration state for these fields. |
| Freeze/persist | `decision_logic.py:707`, `finish_decision`; `investigation_session.py:110`, `complete` | Serializes both legacy primary/tiers and causal qualifications, then freezes the result. |
| Overview | `investigation_presenters.py:32`, `build_presentation`, 61-81; `overview_workspace.py:216`, `bind`, 230-252 | Projects selected policy tier and causal lead separately. The visible title is **Localized processing anomalies**, High is scoped in the qualifier. Machine primary, dominant pattern, reasoning links and hypothesis cards still use the old hypothesis semantics. |
| Reports | `reasoning_persistence.py:299`, `build_reasoning_trace_text`, Final Decision block; `narrative_builder.py:36/99` | Trace report includes primary `localized_editing`, High and causal qualifiers; text/HTML use the recorded overall narrative. Reports faithfully expose the semantic mismatch rather than independently causing it. |

All three hypotheses coexist in the trace. There is no prohibition on simultaneous synthetic and local support. The limitation is that the single authoritative primary field still places unlike causal/observational categories in competition. The actual Overview has already improved its label; changing that label again would not repair the selected finding's machine semantics or downstream report consumers.

## B-D. Boundary, mask and synthetic evidence

Detailed findings are in [boundary_reliability_audit.md](boundary_reliability_audit.md). The most important distinction is that inconclusive Focus is **not** formal counter-evidence and must not automatically erase positive observations. Nevertheless it cannot supply affirmative strength to a boundary-mismatch mechanism. Alignment zero limits the claim that generic hotspot contours coincide with the person boundary; it does not refute the existence of hotspot clusters elsewhere.

The limited/medium mask is usable under existing criteria. Boundary reliability 1.0 measures usable person geometry plus band area, not perfect segmentation or edit certainty. Quality limitations are preserved diagnostically but not separately represented in central confidence facts. Background support exists, but its measured repetitive character reduces the asymmetry baseline reliability to 0.6. A universal Medium-mask confidence cap is not established by this audit.

Precise metadata in TRACE `/evidence_snapshot/metadata/details/metadata_signals`:

- `PNG:Description` has a Midjourney short reference URL, `--chaos 10`, `--ar 3:4`, `--stylize 1000`, `--v 6.1`, and Job ID `33717b8b-eb01-4bd6-8719-f4b4c9d59fa8`.
- `PNG:Author` is `theart1300`, an attribution, not an authenticity check.
- `XMP-iptcExt:DigitalSourceType` is the exact controlled value `http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia`.

`exiftool_backend.py:465`, `_explicit_generation_workflow`, recognizes job UUID + generation parameter + version/style signature. `_source_type_declarations` and `metadata_evidence.py:34-44` map the IPTC declaration. These yield `EMBEDDED_GENERATION_PROMPT` and `DECLARED_SYNTHETIC`; neither validates origin. The description strongly identifies Midjourney-format declared context, while the IPTC value declares generation generically. There is no supported connected graph, so graph-specific process details should be unknown; the general generation declaration should still be represented as such.

`workflow_interpretation.py:36`, `workflow_container`, and `:232`, `interpret_workflows`, do not interpret this prose as graph JSON. `summary_sections.py:55`, `build_metadata_section`, preserves declaration signals and unverified provenance but has no generalized creation-claim adapter for the causal helper. Task B therefore improved ComfyUI-specific contextual synthesis while leaving non-graph declarations on the original precedence path. Its own documentation explicitly preserved the legacy primary field; this is a bounded implementation limitation, not an undisclosed attempt to promote metadata.

`route_synthetic_multi_signal` (`decision_logic.py:1009-1050`) fails for two independent outer reasons: synthetic boost 0.4 < 1.0, and neither visual compound is satisfied. FFT structured is true, but patch structured is false because the patch pattern is `possible_clone_reuse`, not one of the generation-structure patterns (`hypothesis_engine.py:286-287`). Strong material and strong asymmetry flags are both false; medium material alone supplies 0.4 (`hypothesis_engine.py:581-609`). The stricter FFT/patch boost would also fail FFT 0.5536 < 0.80 and axis bias 0.5148 < 0.60. Suspicious score and the metadata-based additional-support flag pass; the clean-provenance/weak-local veto does not apply.

The three patch metrics fixed in Task B are present (270 separated pairs, mean 0.97944, maximum 0.99716); this case is not another omitted-metric failure. FFT/material/texture/asymmetry become contextual unless a visual-generation route is established (`hypothesis_evidence.py:99-109,190-203`; `decision_logic.py:1489`). This route-to-role coupling conservatively avoids nonspecific measurements becoming generation proof, but favors local anomaly accumulation over an origin explanation and does not solve causal selection. Camera compatibility is a scoped moderator, not authentication or a refutation of generation (`hypothesis_evidence.py:110-119`).

## F. What OSINT does and does not consume

This investigation's captured analysis annotations and report annotations contain no matches, no best URL, no analyst review, and no provider attempts. The article URL is supplied in Task C externally; it is **not recorded as source evidence in this saved SignalLens investigation**. A cancelled or unsaved earlier UI action cannot be inferred from these artifacts.

`osint_reverse_search.py:24-86` stores manual match URLs, titles, optional similarity and analyst notes; `:384`, `add_manual_match`, persists supplied attributes, not fetched page contents. `classify_source_type` (`:133`) uses URL/title keywords, and `summarize_matches` (`:174`) ranks analyst/provider-entered similarity. Neither performs a page/image retrieval or computes exact/perceptual matches. `open_reverse_search` (`:354`) opens a provider homepage for manual use. There is no built-in exact-hash or perceptual matching engine in this path. A high entered similarity is not a computed match certificate.

When OSINT exists at analysis time, `summary_sections.py:16`, `build_osint_section`, can map an AI-gallery context into synthesis (`hypothesis_engine.py:274`, `decision_logic.py:1151`, provenance route). After analysis, `_commit_osint` (`signallens_gui.py:158-188`) saves and displays a separate annotation revision; it does not resynthesize. `InvestigationSession.commit_annotations` (`investigation_session.py:140`) invalidates report revision, not frozen analysis. `investigation_reports.py:51-86` appends current annotations to an immutable forensic snapshot. Thus external claims can appear in exports while the original technical decision stays unchanged.

Technical authenticity and external corroboration are only partially separated today: a provenance verification flag and an annotation object exist, but no typed retrieval/match/creator-claim/dependency contract exists. Existing annotations suffice to record an analyst's documented source correspondence without a new retrieval feature. Generalized primary semantics still require a model correction; OSINT retrieval is not a prerequisite. Future computed matching may be a separate bounded feature. This audit's in-memory exact-source comparison is evidence for the report, not an application capability added during Task C.

## Remaining limits and change discipline

No calibrated false-positive rate, true generation history, hidden editing chronology or statistical independence is established. Exact remote-file equality validates source correspondence only. Native GUI behavior was inspected through source and existing tests, not by launching the application. The raw generic hotspot contour is not persisted with all its provenance in the compact section snapshot; no new detector measurements were generated to fill that gap.

Read the five original causal audit reports and Task B implementation report; the new strength-witness and filtered-ambiguity findings extend that audit rather than changing its historical documents. Existing Task B findings, version edits and other inherited work remain untouched. The previously documented acceptance run was 521 passing cases; Task C collected and ran none. Zero tests/fixtures/baselines changed. Only the four requested files in this directory were added; no production or application-report artifacts were edited, and nothing was staged, committed or pushed.
