# Task F: raw signal semantics and qualified causal conclusions

2026-11-08. Bounded presentation/documentation correction on `main`, HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`. Tasks B-E, version edits, user assets and other inherited work preserved. No staging, commit, push, tag or publication.

## Root cause and chosen correction

`hypothesis_engine.derive_signals` constructs `strong_local_edit` by comparing an available boundary summary's pattern to `possible_foreground_background_processing_mismatch`. It does **not** mean a separate edit was established. It does not wait for the boundary compound, inspect its strength witnesses, apply camera moderation or compute a hypothesis tier. Its name preserves a legacy mechanism-oriented vocabulary for a preliminary pattern trigger.

`strong_cross` similarly identifies `strong_hotspot_convergence`, not an independently corroborated editing event or a High-confidence hypothesis. These triggers can legitimately remain true when the compound fails and localized support is Low/neutral.

The demonstrated defect is presentation: an unscoped **Derived Signals** block and original technical dialog presented these legacy names without their stage/claim. Legacy text fallback also described a raw trigger as localized-editing support and could infer absence of a mechanism from absence of a trigger. Current traces normally bypass that fallback using recorded `selection_reason`, but it remains a supported historical rendering path.

Selected **Option A**: retain keys and values, document the contract, add shared presentation scope descriptions, and qualify the affected legacy explanations. No alias, new mutable signal record, schema, numerical adjustment or policy change. No computational consumer defect requiring Option C was demonstrated. Presentation inference was corrected; valid numerical contributions were retained.

## Semantic inventory

All `DerivedSignals` fields below are computed **before corroboration and qualified confidence**, from the active evidence snapshot. General availability/finite-value validation applies first. Pattern flags are not necessarily detector-strength checks: a matching pattern can produce a true flag even when the observation's status is weak. Except where explicitly stated, they incorporate no contradictory or moderating evidence.

| Field | Exact source / kind | Moderation incorporated? | Persistence and consumers |
|---|---|---|---|
| `strong_local_edit` | Boundary pattern equals `possible_foreground_background_processing_mismatch`; raw pattern trigger | No compound, geometry or camera qualification | Serialized in `derived_signals`; local-support +2, synergies, weak-local condition, clone/sensor/compression contextual additions; local candidate/safeguard routes; diagnostics and ancestry shadow |
| `strong_cross` | Cross pattern equals `strong_hotspot_convergence`; hotspot-relationship trigger | No independent-source or boundary-strength qualification | Serialized; local-support +1, synergies, clone/sensor/compression context, routes, diagnostics/shadow |
| `fragmented_local_edit` | Boundary pattern equals `possible_boundary_fragment_convergence`; fragment trigger | No | Serialized; fragment-allocation path, synergies and transition candidate |
| `boundary_stack_medium` | `strong_local_edit AND strong_cross AND (boundary_strong OR boundary_medium)`; local scoring composite | Uses eligible intrinsic-boundary/alignment classifications, not the later compound-strength gate | Transient local variable in `compute_scorecard`; operation reason retained in ledger; +0.60 if stronger stack did not apply |
| `subject_boundary_medium` | Subject-boundary pattern equals `possible_boundary_transition_inconsistency`; intrinsic-edge trigger | No person-boundary registration or final confidence | Serialized; stack, score conversion/synergies and transition candidate |
| `region_geometry_unreliable` | Process-asymmetry details' existing geometry-warning boolean | Encodes that detector's applicability warning, not global origin/edit confidence | Serialized; numerical moderation, geometry safeguard route, synthetic regional compound and confidence geometry fact |
| `person_mask_reliable` | Region-mask source `person_subject_mask`, quality `high` **or** `medium`; eligibility heuristic | Accepts medium quality; not proof of alignment or authenticity | Serialized; band reliability heuristic, route applicability and confidence person-eligibility fact |
| `boundary_reliability_score` | Existing usable-mask/band-area tiers, from 0 to 1 | Geometry sufficiency only | Serialized; route and qualified confidence safeguards; not a causal probability |
| `subject_boundary_strong`, `segmentation_boundary_*` | Intrinsic-edge pattern / alignment-score tiers | Detector-specific, no final mechanism assessment | Serialized; score components, compound/candidate context and applicability safeguards |
| `fft_structured`, `patch_structured` | Named frequency/recurrence patterns | No final synthetic confidence | Serialized; boost prerequisites, structured-recurrence alternatives and synthetic compound predicates |
| `material_realism_*`, `subject_process_asymmetry_*`, texture flags | Existing score bands or named masked-feature patterns | Detector-specific applicability where measured; no independent-cause conclusion | Serialized; local/synthetic scores and scoped route candidates |
| `metadata_synthetic`, `metadata_enhancement` | Existing unverified declaration state | Explicitly unverified; no cryptographic assertion | Serialized; declaration support/context, not authenticated history |
| `provenance_clean`, `local_signals_weak` | Absence of selected declaration/context triggers / composite weak-or-missing local observations | Limited input-state combination only | Serialized; candidate moderation, not proof of authentic or unedited imagery |
| `clone_candidate`, `clone_ambiguous` | Scorecard patch-pattern candidate and existing coverage/spatial/camera/context ambiguity checks | Candidate alone no; ambiguity combines specific checks | Serialized in scorecard, not DerivedSignals; qualified clone routes additionally require support, dominance and camera safeguards |
| `synthetic_supported_by_other_domains` | Scorecard OR of metadata, OSINT-context or strong-material flags | No independent-source guarantee | Serialized scorecard; route prerequisite, explicitly explained by Task E accumulation audit |

`boundary_strong` in the stack combines strong intrinsic-boundary/alignment triggers; `boundary_medium` combines their medium triggers. The stack is not a second corroboration gate or confidence tier. Several stored names remain unfortunate, but renaming would break audit/ledger associations without improving the production decision.

## Downstream consumer audit and semantic layers

1. **Measurements:** `ModuleSummary` sections preserve original scores, patterns, statuses, polarity, details and artifacts. Intrinsic image edges, generic hotspot contours and person-mask geometry are different measurements; available masks do not prove alignment.
2. **Raw/derived signals:** `build_evidence_snapshot` and `derive_signals` map available measurements into pre-gate conditions. `DerivedSignals` now documents this stage explicitly. These values remain available for arithmetic reconstruction.
3. **Qualified support:** production corroboration evaluates scoped supporting evidence, count, strength and ancestry. `confidence_policy_inputs.snapshot_confidence_facts` consumes the actual boundary-compound boolean plus score, geometry, finding and camera facts. `_localized` applies the existing qualified policy; it does not read raw `strong_local_edit` as an established operation. Routes construct candidates, then all-candidate selection, hypothesis scoping and centralized confidence apply existing safeguards.
4. **Causal conclusion:** `decision_logic._qualify_causal_interpretation` qualifies region-only findings; `investigation_synthesis.build_synthesis` uses frozen qualified hypotheses and associated source review. It does not read the raw boundary trigger to establish separate editing. Existing High specific clone/multiple-mechanism branches retain their own scoped mechanism interpretation; chronology remains unknown.

Raw triggers continue to contribute to numerical ledgers and cautious route candidates even after a compound fails. That is intentional: a failed strength condition does not erase observed anomalies. Neither the Low concern branch nor the retained score components establish a separate operation. Generic/synthetic source gates retain their separate semantics from Task E.

Boundary and cross share ELA/residual ancestry; local-support, synergy and edit-boost conversion reuse these observations in explicitly named model components. The ledger and shadow dependency audit disclose that reuse. These are not independent causal confirmations. No newly demonstrated duplicate numerical-credit defect was found; recalibrating marginal weights is outside scope and would not repair the naming/display problem.

The consumer search covered the root production Python modules, scorecard and lineage owners, qualified policies/routes, presenters, loaders, all six workspaces, reports and diagnostics. No production consumer was found that directly converts `strong_local_edit=True` into `separate_edit_status=established`.

## GUI and report surfaces

| Workspace / output | Verified source dependency and correction |
|---|---|
| Overview | Existing canonical investigation synthesis still supplies the lead; qualified hypothesis cards retain their tiers. No raw-flag inference. |
| Image Forensics | Artifact/measurement catalog, recorded detector status and geometric registration; no `strong_local_edit` consumer. No change needed. |
| Evidence | Scoped observations, hypothesis roles, recorded interpretation, lineage and numerical contribution details. Detector status remains distinct from hypothesis confidence. No raw-flag promotion. |
| Reasoning | Structured hypothesis, gate and ledger tabs remain authoritative. Raw-trace tab/dialog now explain intermediate scope while preserving exact JSON. Original technical dialog now displays recorded qualified hypotheses and causal scope alongside clearly scoped raw values. |
| Provenance | Metadata trust and associated external-source records remain separate; no raw boundary flag used to infer edit history. |
| Reports | Shared technical text renderer labels raw signals/scopes and retains qualified hypothesis, corroboration and causal blocks. Existing current-synthesis lead and frozen forensic text/HTML export paths are untouched. |
| Debug output | Existing diagnostic list now opens with the same raw-trigger scope notice; numerical/decision data unchanged. |

No new panel, workspace, navigation or storage layout. The original technical dialog remains a historical **forensic** view; it does not replace the current investigation synthesis or invent post-analysis source findings.

## Files changed and compatibility

- `signal_language.py`: shared notice and presentation-only descriptions for existing diagnostic keys.
- `hypothesis_engine.py`: `DerivedSignals` contract docstring only.
- `reasoning_persistence.py`: raw-signal heading/scopes; expose already-recorded fragment/intrinsic-boundary flags; correct legacy raw-trigger/segmentation prose.
- `decision_logic.py`: scope notice in optional debug text only; no decision predicate or weight changes.
- `signallens_gui.py`: scope raw diagnostic rows; display recorded qualified hypotheses and causal fields in the existing trace dialog.
- `explorer_workspace.py`: scope notice in the existing raw-trace tab and copyable JSON dialog; JSON bytes/content remain recorded values.
- `tests/test_reasoning.py`, `tests/test_workspace_shell.py`: extend existing serialization/reference and technical-dialog owners, respectively.
- This report is the only Task F documentation addition.

`reasoning_trace.json` and `final_summary.json` already persist legacy raw keys; saved report revisions and loaders preserve them. They are unchanged, not renamed, recomputed on load or supplemented by independently mutable aliases. `analysis_run.json` records execution/settings/artifact references rather than defining these derived fields. `current_report.json` points to a revision and `ui_artifacts_v1.json` contains artifact/payload metadata, not a replacement derived-signal schema. No change to any of those contracts, schemas, versions or publication behavior is needed. Consumers of existing JSON retain its historical pre-qualification meaning; this document describes that meaning rather than introducing a new one.

Old reports are never rewritten. Newly rendered technical text can clarify existing recorded fields without changing their values or retrospectively assigning missing qualified conclusions. Saved full-text/HTML narratives remain historical recorded content.

## Before / after trace

Before:

```text
Derived Signals
strong_local_edit: true
strong_cross: true
```

After (abbreviated; these blocks remain distinct in the technical report):

```text
Qualified hypothesis: localized_editing
confidence_tier: Low
polarity: neutral
separate_edit_status: not_established_from_regional_anomalies

Derived Measurement Signals (raw triggers)
Raw derived triggers precede corroboration and confidence assessment.
Their strength labels are not hypothesis confidence ...
strong_local_edit: true
  Scope: Raw regional-processing trigger: boundary mismatch pattern.
strong_cross: true
  Scope: Raw ELA/residual hotspot-convergence trigger; shares upstream measurements with boundary.
```

The existing Task E gate block still reports count PASS, strength FAIL, overall FAIL. The raw section never overrides it. Disclaimers are centralized at the raw block, not repeated for each hypothesis.

## Reference validation

**Midjourney:** replayed saved summary sections/context in memory from the same reference revision used by Task E (`3162fff16c3e438b8a8302a77906ff7b/ce576b6ed5c74e02a6539e562118dbc5`, report revision ending `8b1f870f47ec4010ac928d1eedbc1f28`). Source SHA-256 `b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`. No pixel detector rerun or source/report write.

Exact equality to stored `derived_signals`, `section_snapshot`, `scorecard`, entire `scorecard_calculation`, `decision`, `hypothesis_assessments`, `confidence_policy` and `causal_interpretation`. Both raw triggers remain true; fragment false; intrinsic-boundary medium true; usable person mask true; geometry warning false. Synthetic origin Medium; localized Low/neutral; camera Medium. Separate edit unestablished, process `unspecified_generation_process`, authenticity unverified. Suspicious **18.04075**, benign **1.50** unchanged. Current synthesis also retains separate edit `not_established`.

**ComfyUI / FLUX.2:** read existing source metadata with the existing bundled extractor, without writing outputs. Full-generation graph remains recognized; signals `EMBEDDED_GENERATION_PROMPT`, `AI_TOOL_NAME_MATCH`; no `DECLARED_ENHANCEMENT` from `denoised_output`. To isolate the semantic contract without rerunning the pixel pipeline, combined this real metadata with explicit synthetic boundary/cross summaries: raw trigger true, declared-generation context retained, separate edit `not_established`. This is a bounded mixed-input reasoning check, **not** a fresh measurement claim about the image. Existing connected-workflow, corroboration and scoped-mechanism regression owners pass. Prior full-image scores remain historical Task D evidence.

**Conventional photograph:** used the existing Nikon D7500 fixture from Task D. Its actual extracted metadata is sparse, not a generation declaration. The same explicitly synthetic anomaly summaries demonstrate raw trigger true while origin and separate edit remain unestablished; the legacy selected local concern is not an authenticated compositing history. This is an applicability/semantic check using existing metadata, not a claim that the photograph's detectors measured those injected anomalies. No new image fixture or image pipeline run.

## Test discipline and acceptance

Coverage audit reused the behavioral coverage matrix's reasoning serialization, confidence, provenance, scorecard, lineage, saved-import and workspace owners. Extended `test_midjourney_raw_metadata_path_regression` to protect the previously unasserted **true raw trigger + Low/neutral qualified local finding + unestablished separate edit** combination, scoped text, JSON roundtrip and rendering immutability. Extended `test_legacy_narrative_and_artifact_access_still_available` to inspect the distinct real Qt technical-dialog rendering with recorded qualified fields; it does not replay backend semantics or lifecycle tests.

Baseline **525** collected cases (prior Task E acceptance); collection confirmed **525**. Added **0**, removed **0**, consolidated **0**; final **525**, net **0**. No new test module, image fixture, golden update or duplicated GUI numerical assertions.

Focused:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests/test_reasoning.py tests/test_workspace_shell.py tests/test_confidence_policy.py tests/test_production_corroboration.py tests/test_explorer_workspace.py -q`

**199 passed in 5.27s.** Final complete gate, once after final code/test changes:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q`

**525 passed in 15.70s; 0 failed, 0 skipped.** Targeted diff whitespace checks pass; `signallens_gui.py` retains its inherited unrelated diagnostic-print trailing whitespace, with no new trailing whitespace introduced by Task F.

## Git status, limitations and outcome

Captured inherited status/content hashes before editing. Only the eight code/test files listed above and this report belong to Task F. Other inherited changes, prior audits, image/report artifacts, version edits and existing deleted paths are preserved. Inherited permission-denied paths cannot be byte-verified. Nothing staged, committed, pushed, tagged or published.

No native/DPI/package inspection or empirical accuracy study was performed. Existing full narratives/raw JSON retain historical wording and field names; external consumers must treat derived values as intermediate inputs. Task F supplies explicit diagnostic scope without migrating old reports or changing numerical policies.

**Status: Complete.** Raw measurements/triggers, qualified support and causal conclusions remain separate through the inspected production and presentation paths.
