# Reasoning correctness corrections, phase 1

## Behavior

All decision routes now run and record candidate findings. A deterministic
synthesis selects an overall conclusion after assessing three questions:

- `synthetic_origin`: support for synthetic generation or declared AI-mediated
  creation, including enhancement declarations explicitly scoped to enhancement.
- `localized_editing`: support for localized processing, compositing or reuse.
- `camera_acquisition`: compatibility with a camera acquisition pipeline, without
  treating compatibility as proof of authenticity.

Boundary-reliability and region-geometry safeguards apply to the mechanisms that
depend on them. They cannot reject an independent generation declaration or
independent clone-reuse evidence. Unreliable region geometry also limits
generation findings that depend on subject-region measurements. The existing
recurrence caveat still limits ambiguous visual recurrence.

Selection rules are explicit, rather than based on whichever route runs first:

1. A specific, corroborated High localized-mechanism finding leads over an
   unverified declaration; all generation evidence remains separately visible.
2. Supported generation-relevant visual convergence can lead when the localized
   mechanism is weaker or inconclusive.
3. A supported specific localized mechanism leads over unverified declaration
   context at the same Medium support tier.
4. An explicit unverified generation or enhancement declaration can lead when
   localized mechanisms remain inconclusive. Its tier is Medium, even without
   OSINT corroboration or a legacy provenance boost of at least 1.0.
5. Scoped cautions, contextual source findings, general anomalies, camera
   compatibility and fallback outcomes remain available. Broad score-based routes
   cannot borrow a specific generation or editing mechanism from the dominant
   pattern helper.

Fixed priorities express specificity within each hypothesis. Reordering the
route registry does not change these priorities or the overall result. Neither
the largest aggregate score nor the highest confidence label alone determines
the result. Heuristic scores and support tiers are not probabilities.

## Metadata and provenance

`metadata_evidence.py` owns shared classification semantics. ExifTool extraction,
metadata summaries and derived signals use the same evidence categories:

| State | Meaning |
| --- | --- |
| `verified_generation_assertion` | Reserved for a future actual validator; never emitted by the current path |
| `unverified_generation_declaration` | Explicit declaration or generation-specific embedded workflow |
| `unverified_enhancement_declaration` | Enhancement declaration, not a whole-image generation assertion |
| `ambiguous_tool_or_workflow_metadata` | Tool mentions, generic editing or ambiguous workflow fields |
| `provenance_present_unverified` | Potential C2PA presence, without validation |
| `no_substantive_provenance_evidence` | No substantive generation/provenance assertion; camera fields may still exist |

Generation-specific embedded workflow recognition covers sampler-node structure
and diffusion parameter bundles. An arbitrary populated `prompt`, `parameters`
or `workflow` field no longer establishes generation. Explicit declarative text
continues through the existing declaration-term rules. Raw signal IDs and their
evidence survive in the metadata summary and the trace's evidence snapshot.

Tool names alone are ambiguous. C2PA presence is neutral and is no longer counted
as camera support. No incoming verification flag is trusted as cryptographic
verification. This implementation does not add a validator.

Sparse metadata is neutral, has a zero suspicious contribution and adds no
suspicious domain. Defensive scoring also excludes stale sparse summaries with
an incorrectly suspicious polarity. Missing provenance coverage is reported as
a limitation. `metadata_missing` now inspects the pattern rather than comparing
a summary object with a string. `metadata_synthetic` describes generation;
`metadata_enhancement` separately describes enhancement.

Intentional differences from the previous behavior include Medium rather than
automatic strong/High interpretation of embedded prompts, neutral rather than
benign C2PA presence, and no generation declaration from tool names alone.
Existing numerical score fields and coefficients remain, but these corrected
metadata inputs can change recalculated totals.

## Reference-case comparison

The initial comparisons below use **partial trace fixtures**, not image-pipeline
replays. Tests inject the supplied legacy scorecard
values into synthetic summaries and exercise the real decision functions. No
private images are read. The unchanged strong-local-edit route reproduces each
original result before the new synthesis is applied.

| Field | Midjourney fixture | Instagram fixture |
| --- | --- | --- |
| Legacy suspicious score, held fixed | 22.193 | 25.4776 |
| Local-edit support | 4.50 | 6.70 |
| Legacy provenance boost | 0.75 | 0.0 |
| Boundary reliability | 0.75 | 1.0 |
| Camera counter-support | 1.25 | 0.0 |
| Original dominant pattern | `localized_processing_inconclusive` | `possible_foreground_background_processing_mismatch` |
| Original confidence / polarity | Low / neutral | High / suspicious |
| New dominant pattern | `provenance_supported_synthetic_context` | `possible_foreground_background_processing_mismatch` |
| New confidence / polarity | Medium / suspicious | High / suspicious |
| Synthetic-origin assessment | Medium / suspicious; explicit declaration, authenticity unverified | Inconclusive / neutral; no substantive generation support |
| Localized-editing assessment | Low / neutral; boundary corroboration mixed | High / suspicious; boundary-focused corroboration |
| Camera-acquisition assessment | Medium / benign compatibility, retained alongside the declaration | Inconclusive / neutral; no camera evidence supplied in this fixture |

Midjourney changes because uncertainty about localized editing no longer ends
assessment of declared generation. The result does not assert verified
provenance. Instagram retains its supported localized mechanism, while metadata
absence contributes no generation evidence. A live recalculation would remove
the old sparse-metadata base weight and any associated domain bonus; its exact
new total cannot be established without the complete original sections.

## Interfaces and audit trail

`synthesize_overall()` retains its arguments and five-element return value:
pattern, narrative, confidence, polarity and reasoning trace. Controller entry
points, analysis modes, GUI rendering and packaging are unchanged.

All existing top-level reasoning-trace keys and existing decision keys remain.
Additions are:

- `hypothesis_assessments`: typed assessment records serialized as objects with
  hypothesis ID, polarity, confidence tier, supporting/moderating evidence IDs,
  limitations, decision branch and explanation.
- `provenance_evidence`: structured state and an explicit false authenticity-
  verification flag.
- `decision.primary_hypothesis` and `decision.selection_reason`.
- Route-trace hypothesis IDs, selection flags and candidate dispositions.
- Declared fields for missing metadata, enhancement and provenance state in
  derived signals. The existing dynamic strong-asymmetry flag is now declared
  so it also survives dataclass serialization.

Routes can now have multiple `matched=true` entries; `selected=true` identifies
the overall winner. Existing GUI fields still work, and the narrative explains
each hypothesis. The text trace adapter includes the assessments and candidate
dispositions, uses the actual selection reason, and continues to render old
traces without the added fields. Sets of scorecard domains now serialize as
sorted JSON arrays instead of opaque Python set strings.

## Verification

Baseline: no existing tests or test configuration were found outside excluded
directories. Initial pytest collection/cache creation encountered a Windows
sandbox access error. An authorized rerun, with caching disabled and the
temporary cache directory excluded, confirmed that no tests were collected.
There were no pre-existing failing test assertions to repair.

Initial phase focused and repository-wide suites: **38 passed, 0 failed, 0 skipped**.
All ten requested scenarios are covered, with parameterized metadata/workflow
cases and additional scoped-safeguard tests. The summary orchestration and both
text and HTML renderers are exercised using synthetic payloads.

```powershell
py -3.13 -m pytest tests/test_reasoning.py -p no:cacheprovider -q
py -3.13 -m pytest -p no:cacheprovider --ignore=test_images --ignore=legacy --ignore=exiftool_files --ignore-glob=pytest-cache-files-* -q
```

Syntax checks passed for the six implementation modules, the test module and
the existing summary, controller and GUI integration modules. Imports of the
summary, controller and GUI passed. No interactive Windows GUI execution,
image-pipeline replay or packaged-app validation is claimed.

## Changed files and remaining concerns

Implementation: `decision_logic.py`, `hypothesis_engine.py`,
`metadata_evidence.py` (new), `summary_sections.py`, `exiftool_backend.py`, and
`reasoning_persistence.py`. Regression suite: `tests/test_reasoning.py` (new).
This document is the technical report. The supplied `SignalLens Reasoning.md`
is unchanged.

No detector measurement algorithm or forensic threshold was changed. No
dependencies, GUI/controller source, PyInstaller files or packaging were changed.
Nothing under `test_images/` was accessed or changed. Nothing was staged,
committed, pushed, tagged or published.

Remaining work outside this phase:

- Correlated evidence can still be counted repeatedly in the legacy scorecard;
  hypothesis separation is not a statistical independence model.
- Existing scorecard timing applies some reliability reductions after computing
  the suspicious total. This phase preserves that behavior; recalculation and
  double camera moderation in legacy helper rationale need separate review.
- Broader confidence calibration needs validation beyond these synthetic
  regressions. High visual/localized tiers remain heuristic support labels.
- Workflow recognition is deliberately conservative and cannot cover every
  generator/export format. Metadata declarations can be fabricated or copied.
- Historical summaries without raw signal IDs use their existing classification
  pattern for compatibility; re-extraction is needed to disambiguate historical
  tool-only classifications reliably.
- Cryptographic provenance validation is not implemented. The reserved verified
  state requires a dedicated validator and a validated assertion integration.

Branch at completion: `chore/repository-foundation`. The five existing
implementation files are modified; the helper, tests, report and supplied task
file are untracked. The Git index remains unchanged.

## Follow-up: real Midjourney metadata regression

The user subsequently reran the same image and obtained Low/neutral again. The
new hypothesis narrative confirmed that the updated routing was active, but
generation evidence had been lost earlier in extraction/classification.

Read-only inspection of the existing JSON artifacts under `analyzed/` identified
two embedded declarations that the initial fixtures had not exercised:

- `XMP-iptcExt:DigitalSourceType` was the exact IPTC controlled-vocabulary URI
  ending in `trainedAlgorithmicMedia`.
- `PNG:Description` contained a prompt with `--chaos`, `--stylize`, `--style raw`,
  `--v`, and a UUID-shaped `Job ID`.

The old tool-name match actually came from `SourceFile`, because a local folder
was named after the generator. That is host context, not embedded evidence. The
earlier summary-only test fixture injected `DECLARED_SYNTHETIC` directly, missing
both the extraction gap and this misleading source for the tool match.

The extractor now:

- Recognizes exact HTTP/HTTPS IPTC Digital Source Type identifiers. Generation
  maps to an unverified generation declaration; the generative-editing and
  generative-composite identifiers map to an enhancement declaration without
  asserting whole-image generation. Ordinary capture, algorithmic enhancement,
  unknown identifiers and lookalike domains do not activate these declarations.
- Recognizes a Midjourney job signature in embedded descriptions, requiring a
  UUID-shaped Job ID together with generation-specific parameter structure.
  A bare job ID, arbitrary description or aspect-ratio flag alone is insufficient.
- Excludes host paths and extractor diagnostics before metadata interpretation.
  Tool names in actual embedded fields remain ambiguous on their own.
- Keeps Digital Source Type in a dedicated evidence bucket, preventing substring
  matches such as treating `algorithmicallyEnhanced` as an AI declaration.

These interpretations follow the [IPTC Photo Metadata User Guide](https://www.iptc.org/std/photometadata/documentation/userguide/),
the [Midjourney parameter documentation](https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List),
and [Midjourney Job ID documentation](https://docs.midjourney.com/hc/en-us/articles/32635695384461-Show-Command).
All resulting declarations remain unverified, regardless of their syntax.

Replaying the actual saved Midjourney summaries with metadata reinterpreted from
the saved watchlist entries changes the overall result from
`localized_processing_inconclusive` / Low / neutral to
`provenance_supported_synthetic_context` / Medium / suspicious. Synthetic origin
is Medium/suspicious, localized editing remains Low/neutral, and camera
compatibility remains Medium/benign. The recalculated suspicious score is 22.193.
No folder-name tool match is used. This is a saved-JSON reasoning replay, not a
new detector execution or an image-pipeline replay; saved artifacts are not
overwritten and source image paths are never opened.

The saved Instagram JSON replay retains
`possible_foreground_background_processing_mismatch` / High / suspicious.
Sparse metadata stays neutral and synthetic origin stays Inconclusive/neutral.

Follow-up test baseline: the prior 38 tests passed. New tests reproduced the
metadata defects (11 failures before the fix). The final suite contains
**61 passed, 0 failed, 0 skipped**. Added cases start from mocked raw ExifTool
records, exercise extraction through overall synthesis, and cover negative
controls for paths, diagnostics, ambiguous descriptions and unrelated source
types. Only the extractor, shared metadata semantics, tests and this report
were changed in the follow-up. The no-commit and no-private-image constraints
remain in force.
