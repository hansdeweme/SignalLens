# Task D: lifecycle, source evidence and reasoning correction

Implemented 2026-11-08 for the `0.1.0-beta.1` preparation scope. Based on `main`, HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`, with inherited Task B implementation, audits, version edits and other user work preserved. No staging, commit, tag, publish or push.

## Implementation summary

The existing investigation owner now projects two distinct records:

- **Frozen forensic result:** original measurements, module observations, lineage, scorecard, hypothesis assessments and captured invocation context. Source edits never call pixel analysis or forensic synthesis again.
- **Current investigation synthesis:** an immutable JSON record for the current result/evidence revision, derived from the frozen facts and reviewed image-associated source evidence. This record supplies the current overall conclusion and report lead.

`investigation_synthesis.py` is a pure projection/interpretation module with no detectors, numerical score calculation, network access or database. It reuses the existing hypothesis assessments and provides five explicit dimensions: `origin_assessment`, `regional_anomaly_assessment`, `separate_edit_assessment`, `technical_provenance_authenticity`, and `external_source_corroboration`. Each carries evidence references, interpretation, scope/limitations and review status; existing supporting, contradicting and moderating forensic roles are preserved. The dimensions may share evidence and do not constitute independent votes or artificial probabilities.

No overall maximum tier is manufactured. Existing per-hypothesis tiers remain in the forensic cards. Overview now shows the canonical joint investigation lead and per-claim confidence scope, rather than presenting the selected forensic hypothesis's tier as the complete verdict.

## Reasoning corrections

### Boundary compound eligibility

`decision_logic._boundary_corroborated` no longer uses a maximum of every available raw score. Inconclusive/benign observations cannot provide affirmative strength while being excluded from eligible positive indicators.

The gate now records `strength_witnesses`, including evidence ID, field/value, scale and predicate. Positive Boundary Focus patterns use their already-established detector-specific ratio/boost semantics; normalized eligible subject/boundary scores retain the existing >= 0.45 requirement. Raw intensity differences are not compared with normalized anomaly scores. The existing positive indicator count requirement remains. No detector threshold or weight was tuned for this reference.

For the Midjourney case, the old inconclusive Focus intensity 2.1537491 no longer supplies strength. The scored supporting subject-boundary result 0.3933163 does not meet the existing normalized requirement. The compound fails and the local High boundary branch is no longer eligible.

### Completed spatial outcomes

`hypothesis_engine.compute_scorecard` reads the completed spatial outcome separately from positive scoring eligibility. A genuinely completed `spatial_patch_recurrence_inconclusive` result now reaches the existing clone ambiguity/damping logic. Missing, skipped, failed and unavailable outputs do not become negative measurements. No new weight was introduced.

This changes reference clone support from **2.10 to 0.75**, through the existing spatial-inconclusive adjustments (-0.75 and the camera-related -0.60). It changes neither the measured similarities nor the suspicious total. The changed component is explicitly documented, not concealed by baseline regeneration.

### Origin, anomalies and edit history

`metadata_evidence.metadata_creation_context` distinguishes coherent structured workflow declarations, explicit non-graph generation/processing declarations, ambiguous tool/workflow references and unspecified context. Non-graph generation declares an `unspecified_generation_process`; it is not forced through the graph parser or misrepresented as authenticated topology. The causal adapter and current investigation synthesis use these general semantics.

Regional observations remain present even when the edit history is unestablished. Specific existing clone/reuse or multi-mechanism findings retain their own scoped interpretation; source declarations do not refute them or establish chronology. A generation declaration or a strong regional anomaly does not itself establish a distinct subsequent edit.

Segmentation quality, boundary support, measured hotspot alignment and background comparison reliability are carried as separate interpretation limitations. Medium masks are still usable under the existing policy; boundary reliability is not forced to equal mask quality. No new blanket cap or area threshold was added. The investigation detail and Overview tooltip show these limitations.

## OSINT lifecycle and association

After image selection, **Source & Context…** is available directly in the command area. It opens the existing source-finding dialog, which already supports page URL, optional image URL, source description/claim, analyst similarity and notes. Entry remains optional. Saving is clearly labeled as the analyst's assessment; the application does not retrieve the page or authenticate its claim.

The existing SHA-256 identity is reused. Source records with a different known image hash are rejected before persistence; unassociated legacy/source data are explicitly flagged and cannot contribute reviewed corroboration. Session ownership and the existing stale-dialog/worker guards remain authoritative. Saved investigations with recorded identity can accept source context without requiring the original image bytes to be present; missing identity is not invented.

Before analysis, reviewed evidence is captured in the invocation as before. `build_summary_result` now excludes external claims from forensic scoring regardless of entry timing; they are consumed by the current investigation synthesis instead. After analysis, changing/removing source evidence commits the existing annotation revision, recomputes only the pure investigation projection, refreshes views/reports, and leaves `session.summary_json` unchanged. Explicit forensic reanalysis remains separate.

Reviewed evidence must be image-associated and include meaningful source description/notes or reported match information. A bare URL does not become generation corroboration. Source similarity 1.0 is represented as **manual normalized similarity, unverified**; no hash comparison or cryptographic verification is inferred. Source claims can meaningfully support generation context without upgrading frozen forensic tiers or authenticating creation history. Evidence-dependency records explicitly allow repetition of the same metadata/source claim, with no independent numerical credit.

## Revisions, reports and six workspaces

`InvestigationSession` owns a cached immutable synthesis record keyed by existing result identity, source hash, annotation revision, policy version, forensic fingerprint and OSINT fingerprint. The record includes revision ID, timestamp, parent revision reference, forensic snapshot ID and evidence revision. No second image identity system or database was introduced.

`create_report_snapshot` freezes the current synthesis together with exact current source annotations and existing forensic content. Its immutable report generation and atomic publication mechanism are reused. Old report snapshots never change. Text, HTML and structured JSON exports contain the current investigation lead followed by clearly labeled frozen forensic analysis and source annotations.

On import, new-format synthesis records are restored exactly when their policy, evidence association, fingerprints and deterministic contents agree with the preserved forensic/source records. A modified cached authenticity claim is not accepted simply because a record says it is verified. Existing fresh import identity and historical identity retention remain intact. Legacy files retain their frozen forensic content and receive an explicitly current investigation projection without modifying the old files or resynthesizing pixels.

All six workspaces share the same snapshot-bound investigation revision banner. Overview projects its canonical lead; Image Forensics and Evidence retain frozen artifacts/observations under that revision context. Reasoning has an **Investigation synthesis** tab explicitly separate from its frozen hypothesis/route/score tabs. Provenance distinguishes technical authenticity from external corroboration. Reports/exports use the same canonical record and revision. Long explanations are not repeated in every workspace.

## Reference results

Machine-readable identities, settings, outcomes and revision records: [task_d_reference_comparison.json](task_d_reference_comparison.json).

### Midjourney

Source: `test_images/midjourney/high-quality, realistic fashion portrait of a young woman , soft hair, natural dabbled window light f 1.8.png`.

SHA-256: `b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`; profile `normal`. The persisted normal patch settings are size 24, stride 12, descriptor 8, threshold 0.965, retained pairs 300, overlay pairs 60; recorded scene-context flags are false.

The original Task C report directory is no longer present in the inherited working tree. An existing later saved report with the same image hash, normal profile, **18.04075** scorecard and matching observations was identified and used explicitly; its exact path is recorded in the comparison. It was not silently substituted with a different image or a different-score experiment.

| Quantity | Baseline | Corrected forensic result |
|---|---|---|
| Primary hypothesis | localized_editing | synthetic_origin |
| Synthetic support | Medium | Medium |
| Localized support | High | Low |
| Camera compatibility | Medium | Medium |
| Suspicious / benign totals | 18.04075 / 1.50 | unchanged |
| Local support / edit boost | 5.25 / 2.295 | unchanged |
| Clone support | 2.10 | 0.75, completed spatial-outcome correction |
| Boundary compound | passed using inconclusive Focus intensity | failed, no eligible strength witness |
| Detailed creation context | graph-only null | explicit declaration; unspecified generation process |
| Separate edit | not established | not established |

Saved pixel observations were reused; no Midjourney detectors were rerun. The reviewed manual OSINT record was found locally with the matching SHA-256, source URL, reported similarity 1.0 and article claim. Three required states were demonstrated:

- A: same corrected forensic record without source review — declared generation, no external corroboration recorded.
- B: reviewed record present before analysis completion — generation context with reviewed, image-associated manual source corroboration.
- C: identical completed forensic record, then the same reviewed evidence committed afterward — **identical dimension contents and lead to B**, with separate auditable revision metadata.

The forensic JSON is byte-for-byte unchanged by the post-analysis commit. Technical provenance stays unverified. The current lead incorporates the source claim, and the original forensic trace remains explicitly frozen rather than falsely claiming a new detector/OSINT analysis occurred.

### ComfyUI / FLUX.2

SHA-256: `f5aade08871a13d91c89689517b0a895cf04ca27e95cdf42637664ddcdbb2480`; profile `subject_based`. Historical measurement artifacts from the earlier ComfyUI run are absent from the current inherited `analyzed` tree, so one fresh pipeline run was necessary to satisfy the requested regression comparison. Captured settings are in the comparison JSON. Temporary artifacts were exclusively created under a verified workspace child and removed afterward; original sources/reports were not overwritten.

All 23 stages succeeded; no errors. Full-generation connected workflow declaration is recognized. Signals are `EMBEDDED_GENERATION_PROMPT` and `AI_TOOL_NAME_MATCH`; **no `DECLARED_ENHANCEMENT`**. Legacy forensic tiers remain synthetic Medium / local High / camera Medium, suspicious score **21.30815**. Current investigation context is declared full-image generation with regional observations; separate edit remains unestablished and authenticity unverified. This preserves Task B's correction without a generator-specific override.

### Conventional photograph

Existing fixture: `test_images/real_camera/test-nikon-d7500-nikonpassion-small-16.jpg`; SHA-256 `aed004440af3abfde913604d0a311418da412ea85c106ff9da83b25428be8b09`; `normal` profile. One fresh pipeline run was performed for the required conventional-photo check; no fixture was added.

The result retains camera compatibility Medium, synthetic origin Inconclusive and a qualified local assessment Medium. Origin and a separate edit are not established; technical authenticity remains unverified. Sparse metadata does not become generation evidence. Coverage is explicitly **partial**: the person mask is unusable, 14 stages succeeded, 8 were skipped and one unavailable, with no execution errors. Regional checks are not fabricated from the absent geometry. This is a coherent representative check, not an empirical accuracy claim or proof of photographic history.

## Coverage discipline and acceptance

Before edits, inspected the existing lifecycle, annotation, report, workspace, confidence, metadata, mask, lineage and numerical coverage owners identified in Task C. Baseline collection: **521** cases; inherited prior acceptance evidence was 521 passing cases. No baseline or fixture was regenerated.

Added **four** collected cases:

1. Two parameterized boundary negative controls: nonzero inconclusive and nonzero benign Focus cannot supply compound strength while excluded from supporting eligibility. Existing positive compound tests remain authoritative.
2. One non-graph declaration/region/edit integration case: declaration context is retained without a graph and does not prove a separate edit.
3. One review-timing equivalence case: equivalent associated evidence before/after analysis yields the same investigation dimensions, with frozen forensic JSON and separate historical revisions.

Extended existing owner cases for source-button access before analysis, mismatched/stale source rejection, removal, report/view revision equivalence, no post-run forensic synthesis, save/load reproducibility, altered cached authenticity rejection, completed spatial ambiguity and OSINT-independent forensic building. The existing round-trip fixture now explicitly supplies the source hash that real GUI selection captures. Overview tests were updated intentionally: the current lead comes from investigation synthesis, while forensic primary/pattern/tiers remain recorded and available. No additional GUI automation framework, test modules, duplicate lifecycle suite or independent fixture pipeline was created.

Final focused group: **173 passed**; broader focused groups also passed during development. The complete suite was run once after final source/test changes:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q`

**525 passed in 15.97 seconds; 0 failed, 0 skipped.** Baseline 521; added 4; removed 0; consolidated 0; final 525; net **+4**, within the strict maximum. No weight/threshold tuning, golden baseline replacement or claims of improved empirical classification accuracy.

## Change inventory and limits

New pure module: `investigation_synthesis.py`. Existing owners extended: `investigation_session.py`, `investigation_reports.py`, `investigation_presenters.py`, `presentation_models.py`, `gui_workspace.py`, `overview_workspace.py`, `provenance_workspace.py`, `osint_dialogs.py`, `signallens_gui.py`, `summary_synthesizer.py`, `decision_logic.py`, `hypothesis_engine.py` and `metadata_evidence.py`. Test changes remain in six existing owner modules. Documentation additions are this report and the single comparison JSON. Task C's four audit documents remain unchanged.

No autonomous retrieval, scraping, external API, perceptual matching engine, cryptographic validator, new workspace, database or detector recalibration was added. Exact source hashing performed during Task C is not silently attached to the manual similarity record. Native packaged Windows/DPI and release-distribution checks were not performed. The inherited version file was preserved rather than replacing user work to rename the release.

Release readiness is **conditional**: the bounded implementation and automated regression gate are accepted; native/package release checks remain separate. Reported source claims and real-image examples do not constitute a population calibration study.

Git discipline: the baseline status/content inventory was captured before implementation. Unrelated inherited changes, including prior reasoning work, `signallens_version.py`, diagnostic prints, existing reports/images, deleted historical artifacts and other user data, are preserved. Nothing is staged or committed. Rollback can revert this implementation's changes without rewriting original forensic snapshots or historical report files; optional synthesis records are versioned and older files remain loadable.
