# Task B: bounded proposed implementation

**Status: Ready for separately authorized implementation. Nothing in this plan has been implemented.** Use [root causes](root_cause_report.md), [graph evidence](workflow_graph_analysis.md), [selection review](hypothesis_selection_review.md) and [coverage audit](test_coverage_audit.md) as the design basis.

## 1. Required production changes

Implement structured declaration interpretation and additive causal synthesis. Preserve raw metadata, observed anomalies, numerical scores, existing hypothesis IDs/tiers and authenticity safeguards. Do not change detector thresholds or give unsigned metadata a confidence bonus.

### Work package 1: bounded graph interpretation

Create a small pure parser for recognized Prompt/API and Workflow/UI schemas. Parse with size/depth/node limits, never execute nodes, resolve explicit links from declared saver image inputs, and identify image/latent/conditioning paths separately from model and saver-description inputs. Record recognized node/interface assumptions, source-field and node/edge witnesses, explicit ambiguity status and trust limitations.

Support a deliberately small documented node set for the observed path and the minimum img2img/inpaint/enhancement forms. Unknown image-flow semantics, incomplete links, cycles, conflicting copies, muted/bypassed or nested constructs must produce explicit partial/unsupported/invalid outcomes unless independently implemented. Multiple savers require per-output results; a single whole-file claim must abstain when they disagree. Preserve both original fields as observations of one declared workflow, not two independent sources.

Return the contract proposed in `workflow_graph_analysis.md`. Keep a distinction between successful parsing, coherent declared process and authenticated provenance. Metadata-only graph parsing cannot produce the last of these.

### Work package 2: semantic enhancement evidence

In recognized workflow containers, prevent structural identifiers, port names, sampler parameters, model filenames and prompt contents from becoming natural-language enhancement declarations. Use supported active operation semantics when available; retain descriptive declaration detection in appropriate fields and exact IPTC generation/enhancement values. Unknown workflow text must not regain declaration status through an unrestricted fallback scan. Keep ambiguous tool attribution available as context.

Require precise source locations in enhancement evidence. Do not delete legitimate `denoised` statements globally, special-case this model/LoRA/seed, or treat `denoise=1.0` as an enhancement operation. Preserve raw extractor observations for forensic review.

### Work package 3: causal synthesis and presentation

Add an optional versioned synthesis record with:

- Declared creation process and interpretation status, including explicit unverified authenticity.
- Observed regional anomalies and their existing support assessment.
- Separate-edit causal status and its limitations; anomaly-only boundary evidence does not uniquely establish an editing event.
- A recorded lead interpretation and reason, separate from global confidence or the legacy `primary_hypothesis` field.

For the audited case the lead must explain a coherent **declared** full-generation workflow plus regional anomalies; a separate edit is not established by those signals. Preserve `localized_editing` as the legacy selected hypothesis and the existing Medium/High policy outputs, but describe local High as support for regional anomaly, not certainty about compositing history. The visible lead and report must make those meanings clear. Do not show a bare High “editing established” headline beside an explanatory disclaimer that contradicts it.

Qualify generic boundary-route causal language even when metadata is absent. A forged graph must not be able to delete anomalies, suppress contradictions, establish a source photograph, refute an independently supported clone/reuse mechanism or invent authentication. No new synthetic High should appear from graph coherence alone. Do not silently change the old primary-selection contract: a future requirement to replace `primary_hypothesis` would be a separate policy/migration decision.

## 2. Exact modules likely to change

| Module | Planned responsibility |
|---|---|
| New `workflow_interpretation.py` (proposed name) | Pure bounded graph parser and immutable result contract; no external dependencies or execution. |
| `exiftool_backend.py` | Invoke interpretation for recognized fields; separate structural evidence from declarative enhancement text; preserve raw matches/fields as appropriate. |
| `metadata_evidence.py` | Shared optional process vocabulary/adapter if needed. Existing authenticity enum/classification precedence stays compatible. |
| `summary_sections.py` | Carry structured interpretation in metadata details without new scored sections or bonuses. |
| `decision_logic.py` | Record additive synthesis/lead reason; qualify boundary-route prose. Keep route predicates and legacy primary-selection precedence. |
| `summary_types.py` / `gui_semantics.py` | Prefer existing `reasoning_trace` / `details` containers; add typed fields only where a stable internal/public boundary needs them. |
| `hypothesis_evidence.py` | Render declared-process specificity and separate-edit limitations without counting another supporting source. |
| `reasoning_persistence.py`, `narrative_builder.py` | Show the recorded new synthesis/trust qualification consistently in text/HTML/trace. |
| `investigation_presenters.py`, `presentation_models.py`, `overview_workspace.py` | Project and display the new recorded lead; maintain historical fallback and distinguish support from causal certainty. |

`confidence_policy.py`, detector implementations, scorecard/numerical allocation and route priorities do **not** need behavioral changes for this recommendation. Report-specific adapters should be changed only if the new persisted record otherwise fails to reach their existing shared renderer. No broad controller/session/worker or GUI navigation refactor is needed.

The patch metric omission is a confirmed **separate** issue: repair `vf_patch_similarity.py`'s output serialization and validate its producer/consumer contract in a separately reviewed change. Such a repair may alter scores/routes for other images and must not be disguised as provenance presentation work. It cannot alone make this image pass the stricter FFT/patch thresholds. Do not infer missing whole-population values from truncated `top_pairs`.

## 3. Contracts to preserve

The five-element synthesis API; existing hypothesis IDs; exact raw metadata; no provenance verification from flags, JSON, graph coherence or matching file hashes; metadata-only Medium bound; scoped counter-evidence; camera compatibility rather than authentication; route-order invariance; numerical ledger integrity; no independent-source credit for duplicate graph representations; shared-measurement limitations; immutable stored investigations; historic text/JSON import and export behavior.

Explicitly retain real enhancement detection, especially exact IPTC vocabulary and descriptive enhancement declarations. Preserve clone/reuse mechanisms independently of person-boundary interpretation and workflow context. No new detector score, weight, threshold or empirical accuracy claim is authorized by this design.

## 4. Compatibility and migration

Version the new optional record. Missing fields in old results mean “process not interpreted,” not “no generation” or “no editing.” Keep historical stored conclusions frozen; new presentation must not re-run or rewrite an old investigation's reasoning. New analyses may populate the record, with safe presentation fallback for old imports.

No bulk baseline regeneration. Preserve legacy `primary_hypothesis`, confidence policy and scorecard fields for existing consumers. Update lead display/report wording as an additive projection with recorded reasons. If the product later removes the legacy primary field or changes its meaning, require an explicit schema/policy version and review of selection-owner tests.

## 5. Smallest necessary test changes

Use existing extraction/reasoning, hypothesis-scoping, confidence, report/presentation owners. See [coverage audit](test_coverage_audit.md#smallest-proposed-task-b-changes-not-implemented): about 10 distinct new scenarios at most for the initial narrow parser, reduced where existing cases can be extended. Rejection of unsupported semantics needs explicit coverage; implementing additional semantics expands scope and requires justified cases. No new suites per finding, fixture pipelines, private-image detector reruns or native/packaging tests merely for diligence.

## 6. Acceptance criteria

1. Source PNG's two graph representations produce one coherent, unverified empty-latent declaration with traceable saver paths. Generic tool/model names alone cannot establish a process.
2. `denoised_output` and denoise parameters produce no enhancement declaration; legitimate descriptive/IPTC enhancement still works. Unsupported workflow semantics abstain safely.
3. Actual scores, authoritative confidence tiers, legacy primary and anomaly/counter-evidence remain unchanged for equivalent section inputs. No new source-diversity credit arises from graph copies.
4. New results' primary explanation/report lead distinguish declared creation, regional observations and unestablished separate editing; direct spatial reuse remains independently scoped. Forged/coherent metadata never upgrades authenticity or hides evidence.
5. Text, HTML, JSON and Overview project one recorded synthesis with proper historical fallback; no stored source forensic result is mutated by presentation.
6. Existing targeted owner checks pass; one full suite after final code/test changes passes. Report collection changes and genuine remaining limits. No claim of population-level detector improvement without separate empirical validation.

## 7. Rollback strategy

Keep parser/synthesis changes isolated from detector/policy arithmetic. Revert the implementation commit(s) to restore legacy projection; optional versioned fields remain ignorable by older readers. Do not migrate or overwrite saved forensic artifacts. Retain the original false-positive and graph evidence as audit documentation. A parser failure must yield explicit unavailable/unsupported interpretation, not fail the full analysis or fall back to false declarative classification.

## 8. Risks and decisions

Largest risks: forged metadata changing perceived narrative authority; unknown custom-node behavior; confusing an anomaly support tier with edit-history confidence; graph variants yielding false certainty; semantic filtering discarding real declarations; historic renderers recomputing conclusions; parser resource exhaustion. Bound schemas and resources, preserve evidence and uncertainty, and make failures visible.

Recommended decision is fixed for this plan: additive lead interpretation with unchanged legacy selection. A true replacement of the selected primary hypothesis or a new confidence dimension is outside this bounded Task B scope and needs explicit policy design. Supported-node allowlist and rejection behavior must be written down before implementation; custom node runtime semantics remain assumptions, never authentication. The separate producer-metric repair should be sequenced and reviewed independently.

## Task A delivery and Git verification

Task A added only these five Markdown files under `doc/reasoning_audit/causal_provenance/`. Baseline status/content fingerprint was captured before creation; final comparison checks every pre-existing readable status entry plus additions. Unreadable pre-existing audit paths cannot be content-verified and are not claimed as such. No production/tests/settings/baselines were changed by this audit, no tests were collected or executed, and nothing was staged, committed or pushed. Earlier duplicate-caveat fix and unrelated user changes remain inherited work, so the repository as a whole is not claimed clean.
