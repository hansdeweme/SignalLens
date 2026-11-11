# Codex Task A — SignalLens: Causal Provenance & Hypothesis Selection Audit

**Repository:** `D:\Coding\SignalLens`  
**Task type:** Root-cause investigation and technical design  
**Priority:** High — before next public beta  
**Scope:** Reasoning engine, metadata interpretation, provenance classification, hypothesis selection  
**Implementation:** NOT AUTHORIZED

## 1. Mission

Investigate why SignalLens selects **High-confidence localized editing** as its primary finding for an image containing a detailed, embedded ComfyUI/FLUX.2 generation workflow, while assigning only **Medium confidence to synthetic origin**.

Additionally, investigate an apparent metadata false positive where the internal ComfyUI identifier `denoised_output` triggers a `DECLARED_ENHANCEMENT` finding.

Determine the precise causes and propose the **smallest architecturally sound correction** for Task B.

Do not implement corrections during Task A.

The objective is to understand the existing system, not to force a particular conclusion for this image.

## 2. Mandatory constraints

### Read-only investigation

- Do not modify production source code.
- Do not refactor modules.
- Do not alter detector thresholds, weights, confidence tiers or decision-route priorities.
- Do not change metadata detection rules.
- Do not modify the GUI.
- Do not update existing tests.
- Do not create new tests.
- Do not regenerate reference baselines.
- Do not commit, stage, push, tag or publish.
- Documentation may be created only under `doc/reasoning_audit/`.

**Explicit prohibition: regression testing**

This is an investigation task, not a test-development task.

- **Zero new regression tests.**
- **Zero new test files.**
- **Zero new parameterized test cases.**
- **Zero changes to existing test fixtures.**
- **Zero expansion of the collected test count.**
- Do not run the complete test suite merely to demonstrate diligence.
- Reuse existing test results and inspect existing test coverage.
- Execute an existing focused test only if necessary to resolve a specific uncertainty; explain why it was needed.
- Prefer static code inspection and analysis of the supplied reasoning trace.
- Do not create temporary test scripts that effectively constitute a parallel regression suite.

For Task B, recommend only the minimum additional coverage not already provided by existing tests. Do not implement it.

Follow `AGENTS.md` and `doc/test_quality/TEST_DISCIPLINE.md` where applicable.

## 3. Investigation input

The supplied reasoning trace comes from a `subject_based` analysis of a PNG containing embedded ComfyUI metadata.

Locate the original source image, if available, using the investigation artifacts and existing local project data.

Do not assume the image is available merely because its original path appears in the trace.

### Reported result

| Property | Value |
|---|---|
| Primary hypothesis | `localized_editing` |
| Primary confidence | `High` |
| Selected route | `route_strong_local_edit` |
| Selected pattern | `possible_foreground_background_processing_mismatch` |
| Synthetic-origin confidence | `Medium` |
| Synthetic route | `route_provenance` |
| Provenance state | `unverified_generation_declaration` |
| Analysis profile | `subject_based` |

The trace records:

```text
selection_reason:
"Corroborated localized-mechanism evidence leads;
generation evidence is assessed separately."
```

### Relevant derived signals

```text
strong_local_edit = true
strong_cross = true
boundary_reliability_score = 1.0
metadata_synthetic = true
provenance_state = unverified_generation_declaration
camera_like_support = true
```

The following route did not match:

```text
route_synthetic_multi_signal
```

Determine exactly why.

Do not infer the answer from the route name.

## 4. The embedded generation workflow

The metadata contains `PNG:Prompt` and `PNG:Workflow` records describing a ComfyUI graph.

Relevant declared components include:

| Node | Component |
|---|---|
| 86 | `UNet loader with Name (Image Saver)` |
| 72 | `LoraLoader` |
| 97 | `EmptyFlux2LatentImage` |
| 98 | `RandomNoise` |
| 93 | `SamplerCustomAdvanced` |
| 8 | `VAEDecode` |
| 87 | `Image Saver` |

Base checkpoint:

```text
flux-2-klein-base-9b.safetensors
```

LoRA:

```text
FLUX.2-klein-base-9B_LoRa_by-AI_Characters_STYLE_SmartphoneSnapshotPhotoReality_v13_TRIGGER$casual snapshot
```

Other metadata includes a text prompt, seed `1234567890`, Euler sampling, a nominal 1024 × 1024 generation canvas, and an Image Saver parameter `denoise: 1.0`.

The recorded graph appears to contain this active output path:

```text
Model loader → LoRA → CFG guider
Empty latent ─────────┐
Random noise ─────────┤
Scheduler/sampler ────┤
                      ↓
              SamplerCustomAdvanced
                      ↓
                   VAEDecode
                      ↓
                  Image Saver
```

**Important:** This is an interpretation of embedded, unauthenticated metadata, not proof that the described process produced the actual image.

Task A must independently reconstruct and check the relevant node/edge relationships rather than accepting this diagram as verified.

## 5. Investigation questions

### A1 — Metadata extraction and classification

Trace the complete data path:

```text
PNG metadata extraction
    ↓
Metadata normalization
    ↓
Pattern/keyword matching
    ↓
Evidence creation
    ↓
Evidence-role assignment
    ↓
Hypothesis assessment
```

Determine:

1. Which modules and functions extract `PNG:Prompt` and `PNG:Workflow`?
2. Are these values parsed as structured JSON or treated primarily as text?
3. Which rules recognize ComfyUI, FLUX, LoRA, samplers and generation prompts?
4. What makes `EMBEDDED_GENERATION_PROMPT` a supporting signal for synthetic origin?
5. Why is `AI_TOOL_NAME_MATCH` treated as contextual evidence?
6. Are repeated representations of the same ComfyUI graph deduplicated?
7. Can the engine distinguish a declared full-generation workflow from image-to-image, inpainting, enhancement and unclassified processing?

For each important answer, provide the exact source file, function and line reference.

### A2 — The `denoised` false positive

Investigate the finding:

```text
metadata:DECLARED_ENHANCEMENT
matched_terms: ["denoised"]
source: PNG:Workflow
```

The workflow contains:

```text
denoised_output
```

It also contains:

```text
denoise: 1.0
```

Determine:

1. Which exact rule produces `DECLARED_ENHANCEMENT`?
2. Which field and substring caused the match?
3. Does the implementation search the entire serialized JSON payload?
4. Does it distinguish node names, output-port names, parameter names and descriptive metadata?
5. Can `denoise: 1.0` independently trigger an enhancement finding?
6. Does the finding influence localized editing, synthetic origin, scoring, reporting or only contextual evidence?
7. Are there other generic ComfyUI identifiers that could produce similar false positives?

Identify the smallest safe correction.

**Required semantic distinction:**

A sampler output named `denoised_output` is not, by itself, a declaration that an existing photograph underwent a separate enhancement operation.

Likewise, the presence of a denoising parameter does not by itself establish enhancement.

Do not remove legitimate enhancement detection to solve this case.

### A3 — ComfyUI workflow semantics

Reconstruct the active graph leading to the saved image.

Distinguish:

- Nodes that contribute to the saved output.
- Nodes that are disconnected or inactive.
- Data sources.
- Model inputs.
- Latent initialization.
- Sampling operations.
- Image encoding/decoding.
- Image editing or masking operations.
- Postprocessing.
- Output saving.

Determine whether the embedded workflow structurally declares:

- Full-image generation from an empty latent.
- Image-to-image generation.
- Inpainting.
- Enhancement/upscaling.
- Multiple creation stages.
- An indeterminate process.

Pay particular attention to whether an existing image enters the generation path.

Do not classify solely from the presence of a particular model or LoRA name.

Consider unsupported/custom nodes, nested graphs, graph links, bypassed nodes and incomplete workflow information.

Recommend a minimal representation separating:

```text
declared_process
graph_interpretation_status
provenance_authenticity
supporting_node_paths
interpretation_limitations
```

Determine whether existing SignalLens models can represent these fields without substantial architectural changes.

### A4 — Synthetic-origin hypothesis

Trace:

```text
metadata:EMBEDDED_GENERATION_PROMPT
    ↓
synthetic_origin supporting evidence
    ↓
route_provenance
    ↓
synthetic.unverified_generation_declaration
    ↓
Medium confidence
```

Answer:

1. Why is the confidence Medium?
2. Is Medium an intentional ceiling for unverified generation metadata?
3. Why does `route_synthetic_multi_signal` fail despite FFT and patch-recurrence findings?
4. How are nonspecific image-based observations distinguished from generation-specific evidence?
5. Are synthetic-supporting signals unintentionally relegated to contextual status?
6. How does `camera_like_acquisition_supported` moderate synthetic origin?
7. Could stronger workflow interpretation be represented without falsely claiming authenticity or changing the numerical score?

Do not assume that the synthetic confidence tier must be raised.

### A5 — Localized-editing hypothesis

Trace:

```text
boundary
compression_history
cross_signal
subject_boundary
    ↓
localized.reliable_boundary_compound
    ↓
route_strong_local_edit
    ↓
High confidence
```

Determine:

1. Which precise conditions cause `strong_local_edit = true`?
2. Which measurements establish the compound boundary requirement?
3. Which evidence sources share measurement ancestry?
4. Does the reasoning engine distinguish a regional anomaly from an established separate editing process?
5. Could a fully generated image satisfy the same localized-editing conditions?
6. How does the contradictory `boundary_processing_convergence_supported` observation affect confidence?
7. Why does camera-like acquisition support remain compatible with localized editing?
8. Does the generated report use language stronger than the available evidence warrants?

Audit the relevant corroboration gates, including:

```text
boundary.compound_support
confidence.strong_source_diversity
synthetic.fft_patch_compound
```

Preserve the distinction between measurement-disjoint ancestry and genuine statistical independence.

### A6 — Primary finding selection

Locate the exact implementation selecting `localized_editing` over `synthetic_origin`.

Determine whether selection depends on:

- Route evaluation order.
- Hypothesis-specific confidence tiers.
- Route specificity.
- Precedence rules.
- Evidence counts.
- Numeric scorecards.
- Candidate-ranking logic.
- Other policy constraints.

Explain the actual selection algorithm, including tie-breaking and safeguards.

Then answer the central design question:

**Can SignalLens prefer a coherent declared full-generation interpretation over an ambiguous localized-processing interpretation without treating unauthenticated metadata as verified ground truth?**

If yes, propose the smallest policy-compatible change.

If not, identify the minimal architectural extension required.

Do not implement either approach.

## 6. Evaluate possible design corrections

Compare at least these approaches:

| Option | Description |
|---|---|
| A | Structured workflow classification, without changing primary selection |
| B | Structured workflow classification plus a narrowly scoped causal-compatibility rule |
| C | Introduce explicit creation-process and editing-process dimensions instead of forcing them into one mutually exclusive primary finding |
| D | Alter confidence weights or route precedence |

Evaluate each against:

- Forensic defensibility.
- False-positive risk.
- Risk of trusting forged metadata.
- Compatibility with current reasoning architecture.
- Evidence traceability.
- Impact on existing reports and GUI.
- Implementation complexity.
- Regression risk.

Recommend one option, potentially combining A–C if justified.

**Do not default to Option D.** Weight and precedence changes require a strong explanation of why the underlying interpretation model is already sufficient.

## 7. Existing test coverage audit — NO NEW TESTS

Inspect relevant tests before recommending future coverage.

Create a compact coverage matrix for:

| Scenario | Existing coverage? | Gap, if any |
|---|---|---|
| Embedded generation prompt | | |
| ComfyUI structured workflow | | |
| Full-image generation graph | | |
| Image-to-image graph | | |
| Inpainting graph | | |
| `denoised_output` false positive | | |
| Unverified or transplanted metadata | | |
| Localized versus synthetic primary selection | | |
| Evidence ancestry and deduplication | | |
| Report consistency | | |

For every row, cite existing test modules and relevant test names where available.

**Strict testing rules:**

- Do not add tests.
- Do not modify tests.
- Do not create exploratory regression suites.
- Do not introduce new fixtures or mock pipelines.
- Do not run native GUI tests.
- Do not run packaging tests.
- Do not rerun the full test suite.
- Avoid invoking image-analysis stages unless essential to resolve a documented uncertainty.

Task B should extend existing tests wherever possible.

If new coverage is genuinely necessary, recommend only a small number of parameterized scenarios rather than a new module for each finding.

The number of added tests is not a success metric.

## 8. Deliverables

Create the following files under:

`doc/reasoning_audit/causal_provenance/`

### `root_cause_report.md`

Include:

- Executive conclusion.
- Confirmed observations versus hypotheses.
- Exact causes of the primary-selection behavior.
- Exact cause of the enhancement false positive.
- Source-file/function references.
- Relevant evidence lineage and policy interactions.
- Remaining uncertainties.

### `workflow_graph_analysis.md`

Include:

- Reconstructed active generation path.
- Node/edge evidence.
- Declared process classification.
- Unsupported or ambiguous graph elements.
- Authenticity limitations.
- Proposed workflow-interpretation data contract.

### `hypothesis_selection_review.md`

Include:

- Existing candidate-selection algorithm.
- Why localized editing wins.
- Why synthetic multi-signal routing fails.
- Whether the conclusion is defensible.
- Recommended correction with alternatives and risks.

### `test_coverage_audit.md`

Include:

- Existing relevant tests.
- Confirmed coverage.
- Genuine uncovered behaviors.
- Minimal proposed Task B test changes.
- Explicit confirmation that Task A created zero tests.

### `task_b_implementation_plan.md`

Provide a bounded implementation plan containing:

1. Required production changes.
2. Exact modules likely to change.
3. Contracts to preserve.
4. Compatibility and migration considerations.
5. Smallest necessary test changes.
6. Acceptance criteria.
7. Rollback strategy.
8. Risks and unresolved decisions.

Do not implement this plan.

## 9. Acceptance criteria

Task A is complete only when:

- The reason for selecting localized editing is demonstrated from actual source code.
- The `denoised` matching rule is precisely identified.
- The reason `route_synthetic_multi_signal` failed is established.
- The active ComfyUI generation graph is reconstructed.
- The distinction between declared process and provenance authenticity is preserved.
- The recommended correction addresses the general class of failure, not just this image or LoRA.
- Existing relevant test coverage has been inspected.
- No production code has changed.
- No tests have been added or modified.
- No thresholds, confidence policies or detector settings have changed.
- No files outside the authorized documentation directory have changed.
- Nothing has been staged, committed or pushed.

## 10. Final Codex response format

Keep the final response concise and decision-oriented.

Report:

**1. Root cause:** Why localized editing won.

**2. False positive:** Why `denoised_output` triggered enhancement.

**3. Workflow interpretation:** What the embedded graph actually declares.

**4. Recommended correction:** The smallest defensible solution.

**5. Implementation impact:** Modules and contracts affected.

**6. Test discipline:** Existing coverage, minimal identified gaps, zero new tests.

**7. Git status:** Confirm only authorized documentation was added.

**8. Task B readiness:** Ready / Blocked, with reasons.

Do not claim successful implementation, improved detection accuracy or resolved forensic behavior. Task A is investigation and design only.

**Success criterion:** A source-grounded explanation and a narrowly scoped, defensible implementation plan—not additional code, test counts or documentation volume.