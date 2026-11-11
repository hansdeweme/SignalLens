# Task B implementation and acceptance

Completed 2026-11-07 on `main`, based on HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`. No staging, commit, baseline regeneration or push.

## Result and causal rule

The original ComfyUI case now presents **Declared generation with regional anomalies**. Its lead states that the workflow declares empty-latent full-image generation, authenticity is unverified, and regional measurements do not establish a separate editing operation. The false `DECLARED_ENHANCEMENT` finding is absent.

The legacy `primary_hypothesis=localized_editing`, route eligibility and hypothesis confidence architecture are retained. A versioned `causal_interpretation` records the qualified lead, its explicit rule, declared process, trust, separate-edit status and confidence scope. This is an intentional additive synthesis correction, not a promotion of unsigned metadata over pixel evidence. High local support is explicitly described as regional-anomaly support, not certainty about editing history. Specific spatial reuse/multiple-mechanism findings retain their own assessment; a graph cannot refute them or establish their chronology. Supporting and contradictory evidence remain in their scoped lists.

For boundary-only mechanisms, route wording now describes regional processing anomalies and explicitly limits the editing-history inference even when there is no generation metadata. Deterministic selection continues to evaluate all routes and apply existing safeguards; the causal record qualifies its interpretation without ranking by the highest tier. Missing workflow fields in historical results retain existing presentation fallback; loading a saved investigation does not reinterpret or rewrite it.

## Workflow and metadata semantics

`workflow_interpretation.py` is a bounded pure parser, not an executor. It normalizes ComfyUI API references and UI links, traverses dependencies from active recognized saved-image outputs, and classifies recognized paths as full generation, image-to-image, inpainting/masked processing, enhancement/upscaling, mixed stages or indeterminate. Full generation requires empty latent -> sampling -> decoding -> saving, with no connected existing-image/masked processing path. Required connected sampler/decoder inputs are checked; keyword/model names cannot establish the process.

Recognized custom interfaces in the supplied workflow include Image Saver and its model/literal helpers. Their runtime implementations are assumptions, never authenticated provenance. Unknown nodes on the output dependency path, missing dependencies, invalid/cyclic/deep graphs, nested definitions and muted/bypassed reachable nodes abstain. Disconnected nodes do not supply process evidence. Multiple recognized outputs are examined separately; different supported processes are mixed. Invalid or disagreeing graph copies do not produce a coherent full-generation claim.

Bounds: 2,000,000 characters for serialized graph input, 512 nodes, 4096 UI links and 64 dependency levels. The initial supported node set is explicit; e.g. general arbitrary resizing/custom enhancement nodes are not interpreted as AI enhancement. Unsupported cases are represented as such, not coerced into a positive process class.

Prompt and Workflow representations are compared using their connected interface graph. UI layout, scalar widget defaults, prompt/model strings and disconnected preview nodes do not create independent evidence. Matching representations yield `declaration_count=1` and retain both source-field/node-path references. This fingerprint identifies declared graph structure, not executed parameter equality, authenticated image binding or statistical independence.

The interpretation has separate `declared_process`, `graph_interpretation_status`, `provenance_authenticity`, supporting paths and limitations. It is propagated through metadata details and the saved reasoning trace. Provenance remains unverified even for coherent/transplanted graphs. Supplied verification/process flags are not a validator result; the summary adapter derives interpretation from raw observations.

The enhancement bug originated in whole-value substring matching: `denoised` matched unused sampler output `denoised_output`. Structured workflow containers now bypass natural-language generation/enhancement substring matching, including graphs exported in Description/Comment fields. Standard sampling, decoding, incidental model/LoRA names and bare denoise parameters cannot declare enhancement. Supported active upscaling/masked operations can declare the corresponding processing context. Legitimate unstructured descriptive enhancement wording and exact IPTC declarations retain their existing detection path. Tool attribution remains available as context; raw metadata is preserved.

## Patch metric defect and scope discrepancy

Task A proposed deferring this as a separate repair; Task B explicitly authorizes correcting a proven data-flow defect. Inspection confirms an **output contract mismatch**, not an intended restriction or detector computation failure: `compute_similarity_features` already computes separated-pair count, mean similarity and maximum similarity, but `run_patch_similarity_analysis` omitted them from its returned/saved payload. The summary adapter requested these keys and reasoning substituted zero for missing values.

The producer now exposes those three existing measurements. Detector formulas, pair search, thresholds, weights and confidence policies are unchanged. Old historical artifacts are not backfilled. No values are inferred from truncated top-pair lists.

For the original case, replayed only the patch computation from the original prepared image using its persisted invocation settings, through full retained-pair feature calculation. This was necessary to quantify the missing-metric repair without inventing whole-population statistics. Existing repetition, clone-suspicion, coverage, pair count and pattern reproduce the saved values. Newly exposed values:

- separated pair count: **276**;
- mean similarity: **0.9572603106498718**;
- maximum similarity: **0.9817931056022644**.

There is one documented numerical effect: clone support changes from **0 to 0.15** because existing score arithmetic can now consume real separated-pair information. The suspicious total **21.30815**, local support **6.05**, synthetic boost **0.4**, primary hypothesis and all confidence tiers remain unchanged. This is an intentional consequence of fixing the missing data, not a weight adjustment. The synthetic multi-signal route still fails: FFT 0.5673 < 0.80 and patch score 0.5901 < 0.70 independently prevent the stricter boost. No thresholds were lowered.

## Reference comparison

Full source identities, settings, per-hypothesis tiers, signals, workflow paths and numerical differences are in [reference_comparison.json](reference_comparison.json). Original saved reports were read, not overwritten.

| Source / profile | Before -> after legacy primary | Before -> after tiers (synthetic / local / camera) | Measurement / numerical effect |
|---|---|---|---|
| ComfyUI PNG, `subject_based` | localized_editing -> localized_editing, now qualified lead | Medium / High / Medium -> same | Existing patch measurements reproduced; three omitted metrics exposed; clone support 0 -> 0.15 only. |
| MidjourneyBeauty.webp, `normal` | unresolved_anomaly -> unresolved_anomaly | Inconclusive / Inconclusive / Inconclusive -> same; unresolved Medium retained | Saved-section replay; scorecard identical, no detectors rerun. |
| IMG_20260327_095046_222.jpg, `normal` | localized_editing -> localized_editing, now anomaly-qualified wording | Inconclusive / High / Inconclusive -> same | Saved-section replay; scorecard identical, no detectors rerun. |

SHA-256 identities:

- ComfyUI: `f5aade08871a13d91c89689517b0a895cf04ca27e95cdf42637664ddcdbb2480`.
- MidjourneyBeauty: `d2b95ecf7dd3a4a8577c1c824a80174082f7c1fac8acf9e660e4485052042363`.
- Instagram-named JPEG: `e4ce2a62044f147b10eeb2f7fb48280c3841086f054af8b12a2bbdcd381155e0`.

The ComfyUI replay uses patch size 16, stride 8, descriptor size 8, similarity threshold 0.945, retained pairs limit 500, overlay limit 80 and producer max dimension 768. The other two saved normal invocations use 24 / 12 / 8 / 0.965 / 300 / 60. All recorded scene-context flags are false. No source context was invented. Bundled ExifTool was used read-only on the ComfyUI PNG to confirm current raw metadata classification. The source hash matches the original extractor record.

Another persistence discrepancy was observed: this historical ComfyUI file's top-level `analysis_mode` is null while its invocation profile and reasoning trace both say `subject_based`. Comparison uses the recorded invocation profile/settings, not the nullable top-level field. No migration or unrelated persistence fix was bundled into Task B.

The existing synthetic Midjourney/Instagram reference-owner tests also retain their expected primary hypotheses and tiers. They are distinct from the newer saved image investigations listed above. Saved-section replay does not claim that a fresh full detector pipeline on every other image would reproduce omitted-metric-dependent score components; those consumers can now receive the corrected measurements on future analyses.

## Coverage and validation

Coverage audit before test edits reused Task A's inspected owner matrix and the mandatory discipline/matrix. Baseline collection: **516**. Baseline execution evidence: the preceding task's **516 passed**, plus focused owner checks during this implementation. No initial complete suite was rerun.

Added **5** collected cases, within the ceiling:

- Four parameterized connected workflow cases in `test_reasoning.py`: empty latent, external-image encoding, masked input and unsupported reachable custom operation. These protect previously unmodeled process classification, duplicate graph interpretation, false enhancement and unverified trust at the metadata/reasoning boundary.
- One producer-output contract case in `test_scorecard_integrity.py`: fixed upstream measured values pass through the real producer and saved JSON into the summary/reasoning adapter, preventing missing metrics from silently becoming zero. Existing arithmetic tests retain score ownership.

Extended existing enhancement, clone-safeguard, primary-selection, report-rendering, immutable-presentation and Overview display cases. Three pre-existing sampler-signature-only positive fixtures now contain connected saved-output graphs: signature presence alone is intentionally no longer sufficient for structured declarations. The text-parameter case and generic unstructured negatives remain. No cases were removed or consolidated; no new test module was created. `tests/reasoning_helpers.py` is an ordinary uncollected graph helper, not a parallel suite or pipeline fixture.

New contracts are divided by their observable boundaries: graph classification, producer serialization, shared report rendering, pure immutable projection and the actual Overview widgets. Existing lifecycle/worker/navigation/export/score/lineage suites were reused, not duplicated.

Focused final owner run: **236 passed**. Complete final gate, run once after the final source/test changes:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q`

**521 passed in 15.70 seconds; 0 failed, 0 skipped.** Final collection 521; added 5, consolidated 0, removed 0; net **+5**. No expected-image baseline was regenerated. The existing real Qt projection tests ran offscreen through the established runner. Native Windows/DPI/packaging and population-level forensic calibration were not performed or claimed.

The isolated real patch replay emitted environment warnings about missing WMIC physical-core discovery and OpenBLAS thread metadata; computation completed, reproduced the existing metrics and required no dependency/settings changes.

## Change inventory and Git discipline

Production: new `workflow_interpretation.py`; changes to `exiftool_backend.py`, `summary_sections.py`, `vf_patch_similarity.py`, `decision_logic.py`, `presentation_models.py`, `investigation_presenters.py`, `overview_workspace.py` and `reasoning_persistence.py`. Shared text/HTML builders consume the qualified recorded overall narrative without new report inference. No new workspace or GUI redesign; session/report publication ownership is unchanged.

Tests: five existing owner modules extended, plus an ordinary shared helper. Documentation added: this report and the single machine-readable comparison. The five Task A reports remain historical audit findings.

Inherited duplicate-caveat changes in `investigation_presenters.py` and `tests/test_overview_workspace.py` were preserved. Existing `signallens_gui.py` diagnostic prints, Word edits, deleted historical audit artifacts and unrelated untracked files were not changed. Its pre-existing trailing whitespace is excluded from Task B diff checks. Nothing was staged, committed, tagged or pushed; the working tree remains intentionally dirty with the user's inherited work and this implementation.

Rollback: revert only this implementation's source changes, retain optional additive fields as ignorable historical data, and never rewrite original reports. Unsupported parser outcomes remain explicit; they do not abort the forensic pipeline or fall back to declaration matching inside structural JSON.
