# Codex Task C — SignalLens: Origin vs Regional Processing Reasoning Audit

**Repository:** `D:\Coding\SignalLens`  
**Task type:** Root-cause investigation and architecture review  
**Priority:** High — before SignalLens 0.1 Beta  
**Authorization:** Investigation and documentation only  
**Production changes:** NOT AUTHORIZED

## 1. Mission

Investigate why SignalLens continues to select `localized_editing` as the primary hypothesis for an image publicly presented as Midjourney-generated, despite detecting embedded generation metadata and explicitly acknowledging that regional anomalies do not establish a separate editing operation.

This is the second case exposing the issue, following the earlier ComfyUI/FLUX.2 investigation.

The previous correction introduced structured workflow interpretation and a distinction between declared creation, regional anomalies and separate-edit causality. That correction successfully improved the ComfyUI example.

However, the current Midjourney example indicates the underlying primary-selection architecture may still be insufficiently general.

**Determine the exact root causes and propose the smallest defensible, generalizable correction. Do not implement it.**

Do not assume the desired outcome must be `synthetic_origin: High`. The goal is causal accuracy, not a predetermined classification.

## 2. Required reading

Read:

- `AGENTS.md`
- `doc/test_quality/TEST_DISCIPLINE.md`
- All five original causal-provenance audit reports in `doc/reasoning_audit/causal_provenance/`
- `doc/reasoning_audit/causal_provenance/implementation_report.md`
- The actual production code modified during Task B
- Existing reasoning-policy, provenance, metadata and presentation tests

Reference source:

https://embracepresets.com/best-midjourney-prompts-for-realistic-photos/

Use the supplied Midjourney reasoning trace as the primary investigation artifact. Locate its original file and corresponding image in the project if available.

The article presents Midjourney-generated photorealistic imagery. Establish whether the precise analyzed image corresponds to a displayed source image; do not infer exact correspondence from the article's subject matter alone.

If the trace or original image is unavailable locally, document that limitation rather than silently substituting another example.

## 3. Mandatory restrictions

### Read-only investigation

- Do not modify production code.
- Do not modify reasoning thresholds, confidence policies or scoring weights.
- Do not refactor modules.
- Do not modify the GUI or reports.
- Do not update existing fixtures or baselines.
- Do not add or change tests.
- Do not introduce new dependencies.
- Do not stage, commit, push, tag or publish.
- Do not modify inherited working-tree changes.

Documentation may be created only under:

`doc/reasoning_audit/origin_processing/`

### Explicit prohibition: excessive regression testing

**Zero new tests are authorized.**

Specifically:

- Zero new test files.
- Zero new test cases.
- Zero parameterized test expansions.
- Zero fixture modifications.
- Zero baseline regenerations.
- Zero exploratory test harnesses.
- No full-suite execution.
- No repeated image-analysis runs without a documented investigative reason.

Inspect existing test coverage statically.

A focused existing test may be executed only if essential to resolve a specific uncertainty. Explain why.

Do not use test-count growth as a measure of engineering quality.

## 4. Reference-case observations

The Midjourney trace reports:

| Field | Value |
|---|---|
| Analysis mode | `normal` |
| Primary hypothesis | `localized_editing` |
| Primary confidence | `High` |
| Primary rule | `localized.reliable_boundary_compound` |
| Synthetic origin | `Medium` |
| Synthetic rule | `synthetic.unverified_generation_declaration` |
| Camera acquisition | `Medium` |
| Suspicious score | `18.04075` |
| Benign score | `1.50` |
| Synthetic boost | `0.40` |
| Local-edit support | `5.25` |
| Edit boost | `2.295` |
| Clone support | `2.10` |
| Declared process | `null` |
| Provenance authenticity | `not_assessed` |
| Separate-edit status | `not_established_from_regional_anomalies` |

The final decision reports:

```text
rule: separate_process_and_observation
declared_process: null
provenance_authenticity: not_assessed
separate_edit_status: not_established_from_regional_anomalies

lead_explanation:
Regional processing measurements do not by themselves
establish a separate editing operation.
```

Yet it still selects:

```text
primary_hypothesis: localized_editing
confidence_tier: High
```

Its explanation states:

```text
Corroborated regional-processing evidence leads;
creation history and separate-edit causality
are assessed separately.
```

Determine whether this is an intentional distinction with inadequate presentation, an incomplete implementation of Task B, or a more fundamental reasoning-model problem.

## 5. Investigation A — Primary-finding semantics

Trace the complete pipeline from evidence aggregation to the displayed primary finding.

Identify:

1. Where `primary_hypothesis` is selected.
2. Where `confidence_tier` is assigned.
3. Where `separate_process_and_observation` intervenes.
4. How the lead explanation is constructed.
5. Whether `localized_editing` still represents an inferred editing operation or now merely a category for regional anomalies.
6. Whether the GUI and reports distinguish these meanings.
7. Whether the system can represent synthetic origin and regional processing simultaneously without forcing one to be the dominant causal conclusion.

Answer the central question:

**Why does SignalLens continue to present `localized_editing: High` as the primary finding when the same decision explicitly states that a separate editing operation is not established?**

Determine whether this is a contradiction in the data model, an overly broad hypothesis name, a policy-selection issue, or a presentation-layer mismatch.

Provide source-file, function and line references for every confirmed cause.

Do not recommend simply changing the displayed label without addressing the underlying semantics.

## 6. Investigation B — Contradictory boundary evidence

The reference trace contains the following observations:

| Detector | Result |
|---|---|
| Boundary Signal | Strong suspicious |
| Boundary Focus | Inconclusive |
| Subject Boundary | Medium suspicious |
| Segmentation Alignment | Weak, no meaningful alignment |
| ELA | Weak/inconclusive |
| Residual | Weak/inconclusive |
| Compression History | Inconclusive |

The general boundary detector reports a possible foreground/background processing mismatch.

However, the dedicated Boundary Focus detector states that the boundary region does not differ strongly from the subject and background.

Segmentation Alignment also reports that cross-signal hotspots do not meaningfully align with the subject boundary.

Investigate:

1. Which measurements feed each detector.
2. Whether these outputs genuinely contradict one another or measure different properties.
3. Whether Boundary Focus contributes to confidence moderation.
4. Whether Segmentation Alignment contributes to confidence moderation.
5. Whether inconclusive ELA and residual outputs should affect interpretation of a strong combined boundary finding.
6. Whether the existing compound rule accounts for contradictory observations.
7. Whether the evidence-role assignment inflates support through repeated interpretation of related measurements.

**Required:** Distinguish measurement-level contradiction from interpretation-level disagreement.

Do not suppress legitimate evidence merely because another detector is inconclusive.

The objective is to determine whether the High confidence tier is justified by the available evidence and existing policy.

## 7. Investigation C — Segmentation reliability

The trace reports:

```text
subject_area_ratio = 0.8600
boundary_support_ratio = 0.0452
boundary_reliability_score = 1.0000

person_mask_reliable = true
mask_status = limited
mask_reliability = medium
```

The subject occupies approximately 86% of the image.

The segmentation stage describes the mask as usable with limitations.

Investigate:

1. How `person_mask_reliable` is derived.
2. Why `mask_status = limited` coexists with `person_mask_reliable = true`.
3. What `boundary_reliability_score = 1.0` actually measures.
4. Whether boundary reliability and segmentation reliability are distinct concepts.
5. Whether the available background area is sufficient for reliable region comparison.
6. Whether limited mask quality affects downstream confidence gates.
7. Whether a subject-dominant image can produce spurious foreground/background differences.

Do not assume `boundary_reliability_score = 1.0` is incorrect solely because mask reliability is Medium.

Determine what each quantity means and whether the policy uses it appropriately.

## 8. Investigation D — Synthetic-origin evidence

The trace reports:

```text
metadata_synthetic = true
synthetic_boost = 0.4
fft_structured = true
patch_structured = false

synthetic_origin:
Medium / synthetic.unverified_generation_declaration
```

Relevant observations include:

- Embedded generation prompt or workflow.
- Structured frequency anomalies.
- Subject material regularization.
- Subject surface regularization.
- Subject texture regularization.
- Camera-like acquisition compatibility.

Investigate:

1. What precise metadata was detected.
2. Whether it identifies Midjourney or only generic generation context.
3. Why `declared_process` remains `null`.
4. Whether this is expected because the metadata is not a supported connected workflow graph.
5. Why frequency and subject-material observations remain contextual.
6. Whether several synthetic-related observations share measurement ancestry.
7. Why `route_synthetic_multi_signal` fails.
8. Whether a general synthetic-origin hypothesis is disadvantaged by the current routing architecture.
9. Whether the prior ComfyUI fix inadvertently left all non-graph generation evidence on the original decision path.

Do not treat model attribution or a generation prompt as authenticated proof.

Do not artificially increase `synthetic_boost`.

## 9. Investigation E — Regional anomaly scoring

Trace the calculations underlying:

```text
local_edit_support_score = 5.25
edit_boost = 2.295
clone_support_score = 2.10
```

Determine:

1. Which individual measurements contribute to each score.
2. Whether any inputs are counted more than once.
3. Whether shared ancestry is correctly disclosed and handled.
4. Whether related observations are being treated as independent corroboration.
5. Why `boundary.compound_support` passes.
6. Why `confidence.strong_source_diversity` fails.
7. Whether the confidence policy appropriately distinguishes these two results.
8. Why the clone detector reports strong candidate similarity while spatial analysis is inconclusive.
9. Whether these scores describe measurable anomalies or specific editing mechanisms.

Pay particular attention to:

```text
boundary.compound_support: passed
confidence.strong_source_diversity: failed

synthetic.fft_patch_compound: failed
```

Investigate whether the current localized and synthetic hypotheses face materially different corroboration requirements.

Do not assume that equal numerical thresholds would be scientifically justified.

## 10. Investigation F — External source and OSINT integration

The reference source publicly presents the relevant imagery as Midjourney-generated.

However, the trace reports:

```text
osint:
status = not_run
note = No reverse-image OSINT review
       has yet been recorded for this image.
```

Determine:

1. Whether the user supplied the source URL inside SignalLens or only externally.
2. Whether source URLs are persisted as annotations.
3. Whether SignalLens retrieves source-page information.
4. Whether it compares the investigated image against source-page images.
5. Whether it supports exact image matching and qualified perceptual matching.
6. Whether external corroboration can appear in the final investigation report.
7. Whether a frozen forensic decision is intentionally isolated from later OSINT findings.
8. Whether provenance authenticity and external corroboration are represented as separate fields.

Do not add network retrieval, scraping or external APIs during Task C.

Evaluate a minimal future design distinguishing:

```text
technical_provenance_authenticity
external_source_corrobation
source_image_match_status
creator_generation_claim
evidence_dependency
```

Use correctly spelled `external_source_corroboration` in any proposed actual data contract.

A user-supplied URL must not be treated as verified source evidence without retrieval and inspection.

Likewise, an article discussing Midjourney generally must not be treated as proof of an exact image match.

The audit should determine whether this case needs an OSINT feature or whether a clearer existing presentation would be sufficient.

## 11. Evaluate architectural alternatives

Compare these options:

### Option A — Presentation-only clarification

Keep current hypothesis selection but clarify that High localized confidence refers to regional anomalies, not established editing history.

### Option B — Generalized primary-selection correction

Change the primary-finding policy to distinguish creation history from regional processing observations across all supported metadata formats.

### Option C — Multidimensional conclusion model

Represent:

- Origin assessment.
- Processing-anomaly assessment.
- Separate-edit assessment.
- Technical provenance verification.
- External source corroboration.

These can be presented together without forcing them into a single mutually exclusive primary hypothesis.

### Option D — Numerical recalibration

Modify detector thresholds, evidence weights or confidence gates.

For each option, evaluate:

- Scientific and forensic defensibility.
- Compatibility with existing data models.
- Backward compatibility of saved reports.
- GUI and presentation impact.
- False-positive risks.
- Risk of overtrusting metadata.
- Implementation complexity.
- Regression risk.
- Likely generalization to other synthetic generators and conventional photographs.

Recommend the smallest solution that addresses the actual root cause.

Avoid a Midjourney-specific exception or a rule that always prioritizes generation metadata.

## 12. Existing test coverage audit

Inspect the existing suite without modifying it.

Determine current coverage for:

| Behavior | Existing test? | Gap? |
|---|---|---|
| General primary-hypothesis selection | | |
| Structured ComfyUI creation history | | |
| Non-graph generation declarations | | |
| Conflicting boundary observations | | |
| Limited-quality subject masks | | |
| Subject-dominant images | | |
| Regional anomalies without a proven edit | | |
| Synthetic evidence versus localized evidence | | |
| Strong patch similarity with weak spatial support | | |
| Source URL annotations and OSINT | | |
| Frozen forensic results versus source corroboration | | |
| GUI/report consistency | | |

Cite existing test functions where possible.

**Do not add tests during this investigation.**

For the subsequent implementation, recommend the minimum number of nonredundant cases required to cover genuinely new behavior.

Prefer existing fixtures and parameterized tests.

Do not propose a large new regression matrix.

## 13. Deliverables

Create only the following documentation under:

`doc/reasoning_audit/origin_processing/`

### `root_cause_report.md`

Include:

- Executive conclusion.
- Verified root causes.
- Whether the current result is semantically contradictory.
- The role of prior Task B changes.
- Source-grounded evidence for every significant finding.
- Remaining uncertainties.

### `boundary_reliability_audit.md`

Include:

- Boundary versus Boundary Focus behavior.
- Segmentation reliability interpretation.
- Measurement ancestry and compound support.
- Whether confidence moderation is appropriate.
- Recommended corrections, if justified.

### `origin_processing_architecture.md`

Include:

- Existing primary-selection architecture.
- Evaluation of Options A–D.
- Recommended model.
- Data-contract impact.
- Backward compatibility and reporting implications.

### `test_coverage_and_implementation_plan.md`

Include:

- Existing relevant coverage.
- Genuine coverage gaps.
- Minimal implementation sequence.
- Expected modules and contracts.
- Essential acceptance criteria.
- Minimal proposed test changes.
- Risks and rollback strategy.

Avoid additional reports unless essential.

## 14. Acceptance criteria

Task C is complete only when:

- The reason `localized_editing` remains primary is established from actual code.
- The interpretation of `High` localized confidence is clarified.
- The boundary-versus-Boundary Focus discrepancy is explained.
- Segmentation and boundary reliability are correctly distinguished.
- The synthetic multi-signal failure is explained.
- The role of non-graph generation metadata is established.
- The external-source handling path is identified.
- The proposed correction generalizes beyond Midjourney and ComfyUI.
- No arbitrary threshold or score adjustments are recommended without evidence.
- Existing relevant test coverage has been inspected.
- Zero tests have been added, modified or run unless an essential focused test was explicitly justified.
- No production files have changed.
- Nothing has been staged, committed or pushed.

## 15. Final Codex response

Return a concise technical summary with:

1. **Root cause:** Why localized editing still leads.
2. **Contradictions:** Which boundary observations genuinely conflict.
3. **Reliability:** Whether segmentation limitations are appropriately reflected.
4. **Synthetic evidence:** Why generation declarations remain secondary.
5. **OSINT:** Whether source evidence is consumed or only recorded.
6. **Architecture recommendation:** Smallest defensible general correction.
7. **Test discipline:** Current coverage and minimal necessary future additions.
8. **Git status:** Documentation changes only.
9. **Implementation readiness:** Ready / Blocked, with reasons.

**Success is a precise root-cause explanation and a bounded engineering recommendation—not additional code, tests or increased confidence scores.**