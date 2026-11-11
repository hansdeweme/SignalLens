# Causal provenance audit: root causes

Audit date: 2026-11-07. Task A only: investigation and design, no implementation.
Source baseline: branch `main`, HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`.
Line references describe the working tree inspected at that revision; inherited changes are recorded below.

## Executive conclusion

The reported behavior is reproducible from the saved trace and current source without running detectors. It is not caused by route iteration order or by choosing the highest confidence label. The engine first classifies a boundary compound as a **decisive localized mechanism**, then explicitly prefers that class over an unverified generation declaration. Confidence is assigned afterward. The result follows existing policy, but the policy's causal interpretation is stronger than these measurements alone justify: regional processing anomalies do not uniquely establish a separate compositing or editing event.

The metadata path recognizes a sampler signature, but does not reconstruct the graph or distinguish empty-latent generation from image-to-image, inpainting or enhancement. Independent inspection finds an internally coherent empty-latent generation declaration. That interpretation can be reported more precisely while preserving its unverified authenticity and the current Medium metadata-based confidence.

`DECLARED_ENHANCEMENT` is a separate, confirmed classification false positive: unrestricted substring matching finds `denoised` inside an **unconnected sampler output-port name**, `denoised_output`. The Image Saver's `denoise: 1.0` does not match that rule.

Recommended Task B: structured process interpretation plus a small additive synthesis contract separating declared creation process, observed regional anomalies and the evidence for a separate edit. Do not change weights, thresholds, metadata authenticity policy or numeric scores to obtain a preferred answer. See [selection review](hypothesis_selection_review.md) and [bounded plan](task_b_implementation_plan.md).

## Evidence identity and method

The original image exists:

`test_images/stablediffusion/the-greatest-amateur-photo-realism-i-have-ever-achieved-v0-ovys259b8xyg1.png`

It is 1024 x 1024; SHA-256:

`f5aade08871a13d91c89689517b0a895cf04ca27e95cdf42637664ddcdbb2480`

The hash matches the saved extractor payload's `file.sha256`. PNG `prompt` and `workflow` JSON values read directly with Pillow are semantically equal to saved `PNG:Prompt` and `PNG:Workflow`. This verifies artifact consistency, **not the truth or image binding of the creation claim**. No image-analysis stage or ExifTool process was rerun.

Artifact directory, abbreviated **RUN** throughout this audit:

`analyzed/the-greatest-amateur-photo-realism-i-have-ever-achieved-v0-ovys259b8xyg1/0f4d1bf7d2d843f39a00eac7611aa207/0ddbbabad0a948a5b619247398413b9f/`

Relevant artifacts:

- `RUN/analysis_run.json`: completed run `20261107_113434_5a4704c4`.
- `RUN/the-greatest-amateur-photo-realism-i-have-ever-achieved-v0-ovys259b8xyg1_exif_signals.json`: original fields, term matches and metadata signals.
- `RUN/patch_similarity_results.json`: actual producer payload, including omitted summary metrics discussed below.
- **TRACE** = `RUN/report_revisions/0ddbbabad0a948a5b619247398413b9f-a0-8071c92a57964ecf9830e929c5213b41/summary/reasoning_trace.json`.

Useful TRACE anchors: decision line 360; failed synthetic route line 751; derived signals line 833; scorecard line 2329; section snapshot line 3044. The companion `final_summary.json` records the same report revision. JSON pointers below are relative to these existing artifacts.

Investigation used static source/test inspection and read-only JSON/PNG inspection. Inline inspection commands only read and summarize artifacts or compare their representations; they are not a test suite. No tests, GUI or packaging checks were run in Task A.

## A1. Metadata extraction to hypothesis roles

| Step | Exact implementation | Finding |
|---|---|---|
| Invocation | `signallens_controller.py:356`, EXIF stage lambda | Calls `analyze_file_with_exiftool` on the selected image and assigns `exif_payload`. |
| Extraction | `exiftool_backend.py:213`, `run_exiftool_json` | Invokes ExifTool with `-j -G1 -a -u -struct -api RequestAll=2`; parses the outer extractor JSON at line 241. This is not workflow graph interpretation. |
| Orchestration | `exiftool_backend.py:900`, `analyze_file_with_exiftool`, lines 909-915 | Extraction -> watchlist -> text matches -> signals. |
| Field routing | `exiftool_backend.py:251`, `extract_watchlist_hits`; `exif_config.py:23`, `GENERATION_PROMPT_TAGS` | `Prompt` and `Workflow` enter `generation_prompt`; host paths and diagnostics are excluded by `_is_embedded_metadata_entry`, line 142. |
| Normalization | `exiftool_backend.py:103`, `normalize_text` | Dict/list values are JSON-serialized and lowercased; strings are lowercased. Nested workflow JSON strings are not parsed into graph semantics. |
| Recognition | `exiftool_backend.py:405`, `find_term_matches`; `exif_rules.json:25` onward | Whole values are scanned for tool names/aliases. ComfyUI, sampler, CLIP, VAE, safetensors/LoRA and FLUX aliases match the saved fields. |
| Generation signature | `exiftool_backend.py:461`, `_explicit_generation_workflow`; line 501, `build_signals` | Regex recognizes `class_type`/`type` beginning with KSampler or SamplerCustom; alternatively diffusion parameter text or the guarded Midjourney signature. A sampler anywhere in the field is sufficient; output reachability is not checked. |
| Classification | `metadata_evidence.py:46`, `classify_metadata_signals` | Generation IDs take precedence over enhancement IDs and produce `unverified_generation_declaration`. Tool names alone remain ambiguous. No authentication occurs. |
| Summary adapter | `summary_sections.py:54`, `build_metadata_section`, lines 64-101 | Retains IDs and raw evidence. Embedded-generation override sets medium/suspicious, score 0.75; does not separately score every matching alias. |
| Roles | `hypothesis_evidence.py:156`, `scope_hypothesis_evidence`, lines 205-244 | Generation declaration supports synthetic origin; contextual for local editing/camera. Enhancement supports declared AI-mediated processing in the synthetic assessment and is contextual for local editing. Tool-name matches are contextual, because tool presence does not establish which operation occurred. |

`AI_TOOL_NAME_MATCH` therefore does not become another generation declaration merely because the graph has many tool names. `EMBEDDED_GENERATION_PROMPT` supports synthetic origin through an explicit, conservative mapping (`hypothesis_evidence.py:215`), not through generic suspicious polarity.

**Deduplication is partial and operates at different levels.** `deduplicate_match_items` (`exiftool_backend.py:157`) uses group/tag/value/terms/category identity. Prompt and Workflow have different tags and representations, so both remain as observations under one `EMBEDDED_GENERATION_PROMPT` signal. Tool rules yield several evidence matches under one tool signal. Role insertion deduplicates evidence IDs at `hypothesis_evidence.py:176`; base scoring consumes the metadata section, not each serialized graph copy (`hypothesis_engine.py:319`). There is no canonical graph identity or semantic deduplication of Prompt versus Workflow. Do not describe the two fields as independent provenance corroboration.

Current models cannot tell full generation, img2img, inpainting, upscaling or mixed stages apart. `ProvenanceState` (`metadata_evidence.py:10`) distinguishes declaration/trust categories, not active creation processes. A sampler signature can occur in all these processes, even in an inactive/disconnected graph.

## A2. Enhancement false positive and its actual impact

The exact configured term is `declarative_enhancement_terms[2] = "denoised"` (`exif_rules.json:189-196`, loaded by `exif_config.py:21`). `find_term_matches` builds tag plus normalized whole value at `exiftool_backend.py:419`, calls `contains_any` at lines 446-447, and `contains_any` uses `if term in text` at lines 150-155. `build_signals` creates `DECLARED_ENHANCEMENT` at lines 645-660.

Saved match: `term_matches.declarative_enhancement_terms[0]`, source `PNG:Workflow`, matched terms `["denoised"]`. Exact semantic location:

`Workflow.nodes[id=93].outputs[1].name = "denoised_output"`

The output's `links` is null. The saved image is connected to sampler output **0**, named `output`, not output 1. Even a connected denoised port would not by itself declare enhancement of an existing photograph.

The matcher distinguishes neither structural keys nor node types, port labels, widget data, prompt prose or descriptive declarations. `Prompt["87"].inputs.denoise = 1.0` contains `denoise`, not `denoised`, and cannot independently match the current configured term. Denoising parameters are not evidence of a separate enhancement event in any case.

Impact in this trace:

- The false signal appears as synthetic supporting evidence and localized contextual evidence, and contaminates their explanations/report lists (`hypothesis_evidence.py:224-228`). It is not merely hidden diagnostic data.
- Generation wins classification precedence, so `metadata_synthetic=true`, `metadata_enhancement=false` (`metadata_evidence.py:55`; `hypothesis_engine.py:264-269`). The local score does not consume this extra signal.
- `build_metadata_section` returns through the embedded prompt override. Base metadata status/score and the existing provenance boost remain determined by generation. Removing only this false enhancement finding would not change the current numeric score, selected route or confidence. This is a source-grounded counterfactual, not a rerun.
- Without a genuine generation declaration, the same lexical error could classify an enhancement declaration, activate a provenance route/boost and report Medium AI-mediated context. The defect matters beyond this one image.

Other vulnerable identifiers/text include `upscaled_image`, an `Enhanced...` node title, `restored_*`, workflow filenames/model names, and prompt text containing configured terms. These are examples of the matching mechanism's exposure, not additional observed hits in this artifact. Tool names similarly can match filenames without establishing execution.

Smallest safe correction: parse recognized workflow containers and restrict enhancement declarations to appropriate semantic evidence. Structural identifiers and sampler parameters must not be scanned as natural-language enhancement declarations. Recognize supported active enhancement operations separately, preserve explicit enhancement statements in genuine descriptive fields and exact IPTC declarations, and abstain for unknown/malformed graph semantics. A word-boundary fix alone removes this substring but leaves node labels and misleading descriptive/prompt text unresolved. Deleting `denoised` globally would discard legitimate declarations.

## A4-A5. Scores, confidence and lineage

The separate [selection review](hypothesis_selection_review.md) gives the complete predicate values. The immediate synthetic-route failure is `synthetic_boost=0.4 < 1.0`, despite suspicious score 21.30815, additional-support flag true and the FFT/patch compound true. `hypothesis_engine.py:585-605` requires much stronger quantitative FFT/patch metrics to earn its 1.0 boost. Only medium material realism contributes 0.4 here (`:606-609`).

Additional producer-contract defect: `vf_patch_similarity.py:131-168`, `run_patch_similarity_analysis`, serializes neither `spatially_separated_pair_count`, `mean_similarity` nor `max_similarity`, although `compute_similarity_features` computes them at lines 480-552. `build_patch_similarity_section` requests them (`summary_sections.py:938-940`), obtains null, and `derive_signals` defaults them to zero (`hypothesis_engine.py:261-263`, helper `detail`). The saved payload confirms omission. This structurally prevents the strict FFT/patch boost through this producer path. It is not the only reason this image fails: FFT 0.5673 < 0.80 and patch 0.5901 < 0.70 independently fail. Do not reconstruct full-population metrics from truncated `top_pairs[:200]` or lower thresholds as a workaround. Track this as a separate bounded producer-contract repair.

Local support is 6.05, clone support 0, camera support 1.25, context risk false. The compound accepts suspicious boundary and subject-boundary indicators, with subject-boundary score 0.5007135 >= 0.45. Boundary reliability 1.0 means sufficient reliable region geometry under current rules, not authenticated edit history or detector certainty. `strong_local_edit` and `strong_cross` are pattern-derived flags (`hypothesis_engine.py:277-279`), not independent causal findings.

The contrary boundary-focus observation remains explicitly recorded. It is excluded from positive compound counting, but it is not a veto if two other eligible checks survive. Thus High persists. This behavior is expressly covered by existing tests, not an accidental omission from the display.

Lineage (`evidence_lineage.py:109-127`): boundary and cross-signal share ELA/residual ancestry; focus adds regional localization to those measurements; alignment adds mask localization to cross-signal; subject boundary has intrinsic edge-ring measurements; compression has aligned/off-grid boundary-energy measurements. All may still share image content or feature families. The trace's failed generic source-diversity gate and successful local compound are compatible: one requires disjoint witnesses, the other explicitly allows related interpretations. Neither proves statistical independence.

A fully generated image can meet all local route predicates: they use pixel regularities, regions and geometry without a requirement for an existing photographic input or an identified edit operation. This establishes logical compatibility, not an empirical false-positive rate. The generated prose, “Strong evidence of localized compositing or subject-level editing” (`decision_logic.py:856`), overstates causal specificity relative to those measurements and the conflicting focus/alignment observations. The engine preserves cautions but has no explicit causal-adequacy field to keep anomaly strength separate from editing-history certainty.

## Confirmed facts, interpretation and limits

Confirmed: artifact identity, metadata content, graph edges/modes, false-match location, saved gate/score values, explicit selection precedence and current coverage contracts.

Interpretation: the graph coherently declares full-image empty-latent generation. Regional anomalies do not uniquely establish an additional edit. This is the audit's causal assessment, not a cryptographic or empirical origin determination.

Unknown: actual generation/execution history, hidden behavior of custom node implementations, metadata transplantation, model binaries, external postprocessing and population error rates. No workflow was executed, model downloaded, native GUI exercised or detector calibrated. Saved hotspot source details are less complete than their summarized interpretations; no new measurements were manufactured.

## Change discipline

Inherited before this audit: changes in `investigation_presenters.py`, `tests/test_overview_workspace.py` from the preceding duplicate-caveat fix; separate diagnostic prints in `signallens_gui.py`; an edited Word document, pre-existing deleted audit artifacts and untracked project data. These were preserved. A 114-entry Git status/content fingerprint was captured before documentation creation, including unreadable entries marked as such; final verification is described in the plan.

Task A changed only the five Markdown deliverables in this directory. No source/test/settings changes, test collection, test execution, baseline regeneration, staging, commit or push occurred. The preceding task's 516 passing tests are inherited evidence only, not a new acceptance run for a correction that has not been implemented.
