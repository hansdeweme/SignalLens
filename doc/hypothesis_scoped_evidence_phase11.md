# Phase 1.1: hypothesis-scoped evidence and validation

## Implementation

The selected hypothesis assessment is now the source for both overall evidence
lists and JSON evidence fields. Reporting no longer reselects supporting or
contradicting patterns from aggregate polarity, score or module count.

| File changed in this phase | Correction |
| --- | --- |
| `hypothesis_evidence.py` (new) | Exact section/pattern and metadata-signal relationships; scoped roles, qualified interpretations, original metadata observations, and a shared presentation projection |
| `hypothesis_engine.py` | Adds defaulted `contradicting_evidence`, `contextual_evidence`, and `evidence_details` to the assessment dataclass; no scoring changes |
| `decision_logic.py` | Populates scoped assessments and uses them for prose/JSON; hypothesis-aware confidence rationale; qualified anomaly/fallback wording |
| `reasoning_persistence.py` | Uses the same evidence interpretations in the text report; retains rendering fallbacks for old traces |
| `tests/test_hypothesis_scoping.py` (new) | 28 additional regression cases, including parameterized metadata paths and rendering/schema checks |
| This report (new) | Behavioral comparisons, validation, compatibility, remaining concerns and manual checks |

The inherited Phase 1 edits to `exiftool_backend.py`, `summary_sections.py`,
`metadata_evidence.py`, `tests/test_reasoning.py` and `doc/reasoning_phase1.md`
were retained and not edited during this phase. Both supplied task files were
left unchanged.

### Evidence relationships

Every assessment retains supporting, contradicting, moderating and contextual
evidence separately, with limitations. `evidence_details` records each reference's
source section, pattern, observed status/score, role and scoped interpretation.
For metadata, it also retains the original signal's evidence observations.
No pattern-name substring inference is used.

- Explicit generation declarations support synthetic origin. Enhancement
  declarations remain qualified as enhancement, not whole-image generation.
- Structural observations become direct visual-generation support only when
  the existing visual-generation route supports that finding. Otherwise they
  remain nonspecific context. This presentation rule does not alter routing.
- Boundary, regional compression and localized cross-signal anomalies support
  localized-processing concern. Suspected copy-move reuse requires existing
  spatial corroboration to be presented as direct duplication support; otherwise
  it is qualified context.
- Measured boundary-band consistency challenges a selected boundary-mismatch
  mechanism. It does not contradict synthetic origin or an independent
  duplication mechanism. Weak counterevidence with score zero is not hidden.
- Camera metadata, sensor and CFA compatibility can support camera compatibility
  and moderate other hypotheses, but never authenticate an image or categorically
  exclude generation or later editing.
- Missing metadata, creator attribution, tool mentions and unverified C2PA
  presence remain contextual rather than synthetic-origin support. Creator
  attribution keeps its own label even alongside a generation declaration.

Each overall list is a projection of the selected assessment. Other hypotheses
remain visible with their own evidence lists and explanations. Supporting lists
are no longer restricted to three generic secondary patterns, and the primary
measurement can appear as relevant support.

General anomaly/fallback outcomes have an explicit `unresolved_anomaly`
assessment when selected, keeping the primary assessment and overall outcome
consistent without inventing a generation/editing mechanism. A photo-like
consistency route without direct acquisition evidence is explicitly limited to
photo-like compatibility. An empty run does not claim measured boundary
unreliability or favor an unsupported alternative explanation.

### Confidence explanation audit

The numerical scorecard, support tiers, thresholds and routing conditions are
unchanged. `build_confidence_rationale()` explains what the existing tier concerns
using the selected assessment. It no longer recounts modules as independent
domains, recalculates an effective score, or claims that camera structure cancels
generation/localized editing. Relevant counterevidence is described with its
specific scope; its presence does not imply an additional numerical confidence
adjustment. Route prose also avoids an unsupported independence claim and avoids
claiming that an evidence-free fallback favors a particular explanation.

## Before/after reference comparisons

These comparisons replay **existing saved summary JSON** under `analyzed/`.
The existing sections are passed to the real synthesis and reporting functions.
No original images or detector outputs are regenerated, no artifact paths in
the JSON are opened, and the saved reports are not overwritten. This is not an
end-to-end image analysis or an interactive GUI test.

### Midjourney

| Field | Before Phase 1.1 | After Phase 1.1 |
| --- | --- | --- |
| Overall pattern | `provenance_supported_synthetic_context` | Unchanged |
| Primary hypothesis | `synthetic_origin` | Unchanged |
| Confidence / polarity | Medium / suspicious | Unchanged |
| Supporting Signals | Subject stochastic texture, possible copy-move reuse, subject/background process asymmetry | Explicit generation declaration and embedded generation prompt |
| Contradicting Signals | Camera-like acquisition; boundary-processing consistency | Empty: neither establishes a contradiction of generation |
| Moderating evidence | Mixed into the generic contradiction list | Camera-compatible sensor structure, with an explicit coexistence limitation |
| Context | Mixed into support | Nonspecific structural regularity and creator attribution, each qualified |
| Secondary hypotheses | Localized editing Low/neutral; camera compatibility Medium/benign | Same outcomes, with separate scoped evidence |

Boundary consistency is still shown as localized-editing counterevidence,
specifically weakening the boundary-mismatch mechanism. Copy-move concern
remains accessible under localized editing as context because spatial
corroboration is insufficient. The saved Midjourney scorecard remains identical
after replay, including suspicious score 22.193; the new explanation does not
raise confidence.

### Instagram

| Field | Historical saved report | Phase 1.1 replay |
| --- | --- | --- |
| Overall pattern | `possible_foreground_background_processing_mismatch` | Unchanged |
| Primary hypothesis | Not recorded in this older trace | `localized_editing` |
| Confidence / polarity | High / suspicious | Unchanged |
| Supporting Signals | Boundary-focused anomaly, subject stochastic texture, structured patch recurrence | Boundary mismatch, boundary-focused transition anomaly, localized compression inconsistency, localized cross-signal convergence, region-frequency mismatch, subject-boundary artifact |
| Contradicting Signals | Camera-like sensor and weak CFA compatibility | Empty; camera compatibility does not rule out later localized editing |
| Moderating evidence | Mixed into the generic contradiction list | Camera-like sensor and weak CFA compatibility, qualified |
| Secondary hypotheses | No separate assessment fields in the historical trace | Synthetic origin Inconclusive/neutral; camera compatibility Medium/benign |

Sparse metadata supplies no positive suspicious evidence. The historical saved
Instagram trace predates Phase 1's scoring-input corrections: it records
25.4776 and includes a metadata suspicious domain. Replaying its sections with
the already-existing Phase 1 code gives 24.8401 and excludes that domain. This
historical difference is not a Phase 1.1 score adjustment. Its High localized
conclusion remains intact. Phase 1.1 tests independently assert that evidence
scoping changes no scorecard value.

## Automated validation

Baseline: **61 passed, 0 failed, 0 skipped**. Final full suite:
**89 passed, 0 failed, 0 skipped**. All original 61 cases pass unchanged;
28 new cases were added in the new test module.

The new extraction-oriented cases start from controlled ExifTool-style records
and run watchlist extraction, signal construction/classification, metadata
summary construction, derived signals, hypothesis assessment and synthesis.
They cover:

1. An embedded Midjourney prompt/job signature.
2. The exact IPTC `trainedAlgorithmicMedia` identifier.
3. A generic non-generative workflow.
4. Creator attribution without generation evidence.
5. AI text appearing only in host filenames/directories.
6. Sparse technical-only metadata.
7. C2PA metadata without verification.
8. Camera metadata coexisting with an explicit generation declaration.

Tests compare the original signal evidence against the assessment's retained
observations. Negative controls reject arbitrary populated Digital Source Type
values and lookalike domains. The inherited HTTP/HTTPS, generative-editing and
other source-type controls also continue to pass.

The four required hypothesis scenarios are covered: Midjourney with inconclusive
localized editing, Instagram-like strong localized processing, simultaneous
generation/localized/camera evidence, and no meaningful evidence. Additional
cases check genuine boundary counterevidence, independent duplication, unknown
pattern names, creator/declaration label separation, deterministic route order,
scorecard immutability, and hypothesis-aware rationale.

Validation commands:

```powershell
py -3.13 -m pytest -p no:cacheprovider --ignore=test_images --ignore=legacy --ignore=exiftool_files -q
```

Python syntax checks passed for all five Python files changed/added in this
phase. Relevant module imports and controller/GUI import smoke tests passed.
JSON serialization with `allow_nan=False`, old/new trace compatibility and
the existing summary orchestration, plain-text and HTML renderers are tested.
`git diff --check` passes.

AST fingerprints checked against the beginning of this phase confirm that
signal derivation, base/full score computation, environment construction,
dominant-pattern/confidence helpers and route conditions are unchanged. The
only route-body edits are prose in the broad-anomaly and fallback routes.
Evidence population is also tested not to mutate any scorecard field.

## Compatibility

- `synthesize_overall()` retains its arguments and five-element return value.
- Existing trace top-level keys, decision keys and assessment keys remain.
- Existing `supporting_signals` and `contradicting_signals` remain lists of pattern
  identifiers, now correctly projected from the primary assessment.
- Additive assessment fields are `contradicting_evidence`, `contextual_evidence`
  and `evidence_details`. Existing `moderating_evidence` is retained with more
  precise membership.
- The decision adds evidence references/details, moderating/contextual pattern
  lists, qualified explanation lists and limitations. JSON and prose use the
  same projection; the trace is no longer rebuilt with independent heuristics.
- Old traces without the additions still render. Such historical traces retain
  their historical generic fields; missing evidence relationships cannot be
  reconstructed reliably from those fields alone.
- The existing GUI summary receives the scoped narrative through its existing
  interface. Its layout and controller source were not changed. The text trace
  report uses the same evidence interpretations. GUI import validation is not
  interactive Windows validation.

## Exact manual validation steps

1. Close the running SignalLens process and restart it from this working tree:
   `py -3.13 signallens_gui.py`.
2. Keep analysis settings and mode identical for both controlled comparisons.
   The saved Midjourney trace used `normal` mode. Do not compare a new mode with
   the previous run.
3. Select the original Midjourney reference yourself and run the analysis.
   Expect Medium/suspicious, primary `synthetic_origin`, with generation
   declarations as direct support. Expect localized editing Low/neutral and
   camera compatibility Medium/benign in their separate assessments.
4. Check that copy-move concern is absent from overall generation support,
   camera compatibility is moderation rather than contradiction, and consistent
   boundary processing appears only in the localized mechanism's counterevidence.
5. Run the Instagram reference in the same mode. Expect the High/suspicious
   localized-processing conclusion to remain recognizable, with local boundary
   and processing evidence. Sparse metadata must not support AI generation.
6. Compare the GUI summary with each generated
   `analyzed/<image-name>/summary/reasoning_trace.json`. Check
   `decision.primary_hypothesis`, confidence, polarity and evidence lists against
   the matching item in `hypothesis_assessments`.
7. Follow `evidence_details` for generation references. Original observations
   should identify embedded fields such as `PNG:Description` or
   `XMP-iptcExt:DigitalSourceType`, not `SourceFile`, host filenames or folders.
   The automated filename-only control must remain neutral.
8. Review the generated text trace as well. Confirm all support/contradiction
   explanations are relevant to their stated hypothesis and that metadata
   authenticity remains explicitly unverified.

No images under `test_images/` were opened, inspected or changed by this work.
Full original-image/interactive validation remains a manual developer step
because the task explicitly prohibits accessing that directory.

## Remaining issues outside scope

- Correlated detector outputs still contribute to the legacy scorecard. This
  phase removes unjustified independence claims, not correlated weighting.
- Some scorecard reliability/caution adjustments occur after the suspicious
  total is calculated. Recalculation consistency remains a separate task.
- Confidence tiers remain heuristic and need broader empirical calibration.
  Metadata authenticity is not inferred from a declaration's syntax or URI.
- No cryptographic provenance validator exists. C2PA presence remains unverified.
- Camera metadata richness uses existing key-presence/suffix logic rather than
  validating all field values. Some existing suffixes differ from ExifTool's
  compact tag spelling. No extractor/detector algorithm was changed here.
- Person-mask and region geometry reliability can limit structural evidence;
  no detector measurements or thresholds were retuned.
- Unsupported patterns remain visible in section snapshots. A new pattern must
  receive an explicit evidence relationship before it can support a specific
  hypothesis in the scoped narrative.

## Repository status

Started on `chore/repository-foundation` with uncommitted Phase 1 work and an empty
index. Created the local `fix/reasoning-correctness-phase1` branch while retaining
the working tree. No existing changes were discarded.

Modified tracked files at completion: `decision_logic.py`, `exiftool_backend.py`,
`hypothesis_engine.py`, `reasoning_persistence.py`, `summary_sections.py`.

Untracked files: both supplied task Markdown files, `metadata_evidence.py`,
`hypothesis_evidence.py`, `tests/test_reasoning.py`,
`tests/test_hypothesis_scoping.py`, `doc/reasoning_phase1.md`, and this report.

Nothing was staged, committed, pushed, merged, tagged or published. No dependency,
detector, threshold, score weight, GUI layout, external resource, packaging or
Windows build-script change was made during Phase 1.1.
