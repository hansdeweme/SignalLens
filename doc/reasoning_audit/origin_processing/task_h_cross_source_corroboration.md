# Task H: cross-source corroboration and evidence relationships

2026-11-10. **Complete** for the bounded investigation-level implementation. Based on inherited `main`, HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`. Read the test discipline, behavioral ownership matrix and Tasks D–G before implementation. Baseline collection independently confirmed **527**; prior acceptance was **527 passed**. Captured existing source/test/audit hashes in `.h_task_h/baseline.json` before changes. No detector, scorecard, confidence-policy, hypothesis-precedence or storage-layout changes.

## 1. Existing data flow and root cause

`OSINTFindingDialog` -> `add_manual_match` / `replace_match` -> draft `ReverseSearchResult` -> GUI `_commit_osint` -> hash/session-bound staged persistence -> `InvestigationSession.commit_annotations` -> current synthesis / view snapshot -> immutable report publication.

The previous synthesis already retained URLs, titles, source classifications, similarity and notes. It also recorded a generic possible-dependence warning. It did **not** compare individual creation-process claims. Reviewed `ai_gallery` records supplied generation context using classification and meaningful title/notes/score, even without a demonstrated external image match. Its `image_association=matched` meant the annotation container had the investigated file's SHA-256; it did not mean a remote source image was matched. `manual_similarity_unverified` already qualified similarity but could not express an explicit association method or its basis.

The missing layer was typed external claim attributes, a separate external source-image association, and an explicit comparison with embedded declarations. The record did not reduce entirely to `ai_source_context_detected`; relevant original source records survived, but their substantive relationship was not evaluated. Creator/publisher attribution, claimed process, explicit claim text, model/workflow details, association basis and source dependencies had no dedicated review controls.

The inspected current Stable Diffusion report is `analyzed/stabldiff_003/inv_001/reports/rev_003/final_summary.json`. Its annotation is reviewed, hash-bound to the local image, classifies the page as `ai_gallery`, includes both URLs, and has null similarity. Its cached synthesis uses policy v1. No source-image verification or authorship authentication is present.

## 2. Claim and relationship semantics

New pure adapter `evidence_relationships.py` extends the existing synthesis rather than creating a second verdict engine. A claim records its source reference, origin, creation process, supporting details, review/authenticity status and limitations. External claims additionally retain URLs, reported claimant/attribution, model family, workflow details and explicit image-association evidence. Embedded claims retain the existing workflow interpretation, declaration fingerprint and supporting node paths.

External creation processes use a bounded vocabulary. General AI-tool usage is not a full-generation claim. Free prose and source categories are not parsed into full-generation assertions. Legacy AI-gallery records can supply contextual compatibility, with their missing process claim made explicit. Missing metadata does not contradict an external generation claim.

Comparison outcomes distinguish compatible declarations, noncomparable claims, conflicting full-generation versus **unmodified** camera claims, and potentially different stages with unresolved chronology. Ordinary camera capture, enhancement, inpainting and image-to-image processing are not automatically exclusive of earlier/later generation. Known model-family discrepancies remain visible and unresolved; they do not settle pixel origin or stage chronology.

Where available, model details come from named inputs on connected API workflow loader nodes, following ancestors of the already recognized saved-output sinks. Disconnected nodes and prompt prose cannot supply model agreement. Only bounded family tokens are normalized; exact versions and actual execution remain unverified. UI-only graphs or unsupported loader schemas can retain process comparison without inferred model details. External workflow prose is retained literally; the comparison explicitly says `process_comparison_only` rather than claiming exact workflow equivalence.

## 3. Source-image association

Local annotation SHA-256 binding remains separate from the remote association:

| Status | Current handling |
|---|---|
| Unestablished | Default; URL, direct image URL, review flag and manual similarity do not establish identity. |
| Analyst-associated | Requires explicit association, an analyst assertion/visual-check method, and a nonempty recorded basis. Remains an analyst statement. |
| Visually verified | Distinguished in the assessment's association-level registry; unavailable without a reproducible matcher. Manual visual checks do not receive this status. |
| Byte-identical | Distinguished in that registry; unavailable without a supported verified source-file comparison. Manual scores or imported assertions cannot receive it. |
| Rejected | Analyst explicitly rejects the association; cannot supply image-specific corroboration. |

Unsupported imported `visually_verified` / `byte_identical` assertions are preserved as assertions but downgraded to unestablished, with the missing verifier disclosed. Unknown local binding stays unestablished; a known mismatching local hash remains a mismatch. No downloader, image matcher, hash-verification infrastructure or provider integration was added. Earlier Task C byte-comparison findings are not silently inserted into current OSINT annotations.

## 4. Dependence, authenticity and strength

Each relationship records agreement, source-image association, source dependence, model comparison, reasons, evidence references and limitations. Dependence can be unknown, reported same-creator, repeated claim or analyst-asserted independent source. All remain `independence=not_established`; two storage locations or a user assertion cannot manufacture independently verified confirmation.

Qualitative assessment states are `not_assessed`, `insufficient_association`, `contextual_agreement`, `corroborated_declaration`, and `conflicting_claims`. The declaration-corroboration state requires reviewed compatible process claims and an explicit qualified analyst association. It means mutually consistent **declarations**, not independently verified execution. Unresolved conflicts take precedence over compatible relationships in the aggregate assessment; rejected/mismatched sources do not acquire image-specific corroboration.

Family-name agreement alone cannot upgrade association, authenticate metadata, establish authorship, or increase numerical confidence. No probability, weight or independent score credit is assigned. Technical provenance stays independently unverified, and regional anomalies do not establish a separate edit.

## 5. Implementation and consistent presentation

- `osint_reverse_search.py`: optional dataclass attributes and compatible keyword arguments preserve the structured claim, attribution, association and dependency fields through add/edit/save/load. Old records get conservative defaults.
- `osint_dialogs.py`: the existing review form gains those fields in a scrollable form. Saving an analyst association requires its method and basis. Existing source information is prefilled on editing; no structured metadata must be re-entered.
- `investigation_synthesis.py`: policy v2 adds one canonical `cross_source_assessment` under external corroboration. The existing external record/review status remains compatible; `assessment_status` carries the new relationship result. Compatible associated generation declarations explicitly strengthen the investigation's origin description, while conflicts get an unresolved-conflict lead. Frozen tiers and all other dimensions remain scoped separately.
- `gui_workspace.py`: Overview consumes the canonical synthesis lead; Evidence has a Source relationships tab; Reasoning retains its current-synthesis tab beside frozen forensic tabs; Provenance separates technical authenticity from external assessment.
- `provenance_workspace.py`: selected source detail shows explicit source claims, attribution, association and uncertainty.
- Existing report serializers use `synthesis_text`: JSON retains claims/relationships and their reasons; TXT/HTML include both sources, process/model comparison, node paths/fingerprint, source association, dependence limits and revision identity. External prose is HTML-escaped through the established report path.

No new workspace, network integration, dependency, detector pass, broad reasoning refactor or release build was introduced.

## 6. Stable Diffusion / Reddit reference

Source SHA-256: `b4f305f65537010b4d2926b41e4ec092889ea0a1607075323da10f02dbf8ac5e`.

The [Reddit page](https://www.reddit.com/r/StableDiffusion/comments/1t2kyjt/the_greatest_amateur_photo_realism_i_have_ever/) was read for task validation only. Its author presents photorealistic AI work and identifies Klein Base 9B in replies. This is a source claim, not authenticated authorship. The product does not scrape Reddit. The supplied direct image URL remains a reference, not identity proof.

| State | Investigation interpretation |
|---|---|
| Previous v1 synthesis | Reviewed manual AI-gallery context, without explicit creation-claim comparison. |
| New synthesis, unchanged real annotations | Contextual compatibility with the embedded generation declaration; **insufficient association**. Missing typed process and unverified source-image identity are disclosed. |
| Isolated reviewed-claim enrichment | Embedded full-image generation and external unspecified generation compare as **compatible**; connected LoRA input and reported FLUX family are compatible. Association remains **unestablished**, so overall corroboration remains limited. |
| Counterfactual explicit analyst association | **Corroborated generation declaration**, qualified by unauthenticated sources, unestablished independence and analyst-only association. This is an acceptance scenario, not a newly verified association for the user's record. |

The embedded connected LoRA filename specifies v13; the source post describes v14. The isolated review explicitly records this limitation. No exact workflow/version match is asserted. Both original page/image references, process declarations and the technical graph fingerprint/node paths remain available for review.

Frozen primary remains `localized_editing`; suspicious score remains **24.3401**. The recorded High regional / Medium synthetic interpretation is not retuned. Embedded `full_image_generation` remains recognized, technical authenticity remains unverified and separate edit remains `not_established`. The complete frozen reasoning trace and original report bytes were compared unchanged.

## 7. Midjourney and conventional-photo checks

Saved-reference validation reused Task G detector outputs and Task D's recorded Midjourney article evidence; no pixel pipeline was rerun.

**Midjourney:** SHA-256 `b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`. The [earlier article](https://embracepresets.com/best-midjourney-prompts-for-realistic-photos/) still describes its second example as generated imagery. Its recorded source/image references were reused in an isolated claim-enrichment scenario. The claimant is a publisher; original creator status and independence are not assumed. Unestablished association yields insufficient association; a separately labeled counterfactual analyst association yields compatible declaration corroboration. The non-graph embedded generation declaration is retained; missing structured model attributes do not become an exact model match. Suspicious score **18.04075**, primary synthetic origin, frozen trace and separate-edit status are unchanged.

**Nikon D7500 photograph:** SHA-256 `aed004440af3abfde913604d0a311418da412ea85c106ff9da83b25428be8b09`. A deliberately hypothetical external generation claim with unestablished association supplies no image-specific corroboration. Even with a counterfactual explicit analyst association there is no compatible embedded generation declaration, so origin remains `not_established`. Sparse metadata is not contradictory generation evidence. Suspicious score **7.6**, original local/camera findings and the entire frozen trace remain unchanged. The hypothetical URL is a validation input, not an asserted real source.

Validation script and detailed results are retained under `.h_task_h/validate_references.py` and `.h_task_h/reference_results.json`. Each reference was exported/reopened at three evidence states, verifying equal canonical view/report synthesis, exact frozen trace, immutable earlier report hashes and different revision identifiers. Outputs are isolated under `.h_task_h`; originals were read only. The script was repeated after adding model-comparison explanations, report node paths and lead wording so retained results match final code.

## 8. Revision and backward-compatibility behavior

Existing annotation revision/fingerprint ownership recomputes synthesis on claim, association, review, dependency or source-removal edits without invoking forensic analysis. Policy v2 participates in the existing synthesis key and revision identifier. Report snapshots freeze relationships with their exact annotation revision; later claims cannot mutate prior bundles.

Task G's `inv_*/run_*`, immutable `reports/rev_*` and relative publication pointer are unchanged. Existing legacy-import tests and report roundtrips remain authoritative. A v1 saved summary loads without changing its forensic content or files; its current investigation synthesis is recomputed under v2. Valid current-policy synthesis is restored only when fingerprints and recomputed canonical content agree. Reopening an old report does not rewrite that historical report. No history migration or source-annotation modification was performed.

## 9. Test ownership and results

Searched existing OSINT, annotation, source-identity, synthesis, report, workspace and reasoning tests before changing tests. No existing case compared typed cross-source claims. Reused the authoritative behavioral ownership matrix rather than creating new lifecycle or GUI suites.

Added **three parameterized cases** in `test_investigation_contracts::test_cross_source_claim_relationships_are_qualified`:

1. Compatible embedded generation and associated reviewed creator declarations, qualified same-creator dependence, connected model-family details, unchanged forensic data.
2. Reviewed URLs/null similarity do not establish image identity; even a maximal manual score plus an unsupported byte-identity assertion cannot replace a verifier.
3. Unmodified camera versus full-generation claims remain explicitly conflicting; neither is silently discarded or authenticated.

Extended existing authoritative owners:

- Annotation/report revision test now revises compatible -> conflicting -> removed source evidence, checks distinct synthesis revisions and frozen forensic/report history using the existing Task G allocation path.
- Review-timing equivalence test retains its original invariants and explicitly rejects strong corroboration from manual similarity alone.
- OSINT provenance-display test exercises the real existing dialog's new fields and prefill roundtrip, committed source details, canonical Evidence/Provenance/Reasoning bindings, and clearing of the new relationship view on selection replacement. Its original frozen-result assertion remains.

Existing stale-dialog, source-hash rejection, no-forensic-resynthesis, report failure/publication, legacy import, serialization, numerical/scorecard, confidence and workspace tests were reused unchanged where they already own the invariant. No new image fixture, test module or golden baseline was added.

Focused final broad group: **156 passed in 14.81s**, using investigation contracts/GUI, provenance reporting, Evidence/Reasoning, shell and Overview modules. Smaller focused checks also passed during development.

Final complete acceptance command:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q`

**530 passed in 21.49s; 0 failed, 0 skipped; exit 0.** One complete run after the final production/test edit. Baseline **527**, added **3**, removed **0**, consolidated **0**, final **530**, net **+3**. This meets Task H's target. Documentation-only work followed the full gate.

## 10. Change inventory, Git and limits

New production module: `evidence_relationships.py`. Existing files changed for Task H: `investigation_synthesis.py`, `osint_reverse_search.py`, `osint_dialogs.py`, `gui_workspace.py`, `provenance_workspace.py`, `tests/test_investigation_contracts.py`, `tests/test_provenance_reporting.py`. This report is the sole permanent documentation addition. Baseline hash comparison identified exactly those seven existing files as changed; unrelated inherited source/test/audit files remain unchanged. Isolated validation files are retained under `.h_task_h` for review.

Targeted changed-file whitespace checks passed. Inherited inaccessible audit folders, deleted artifact statuses and unrelated pre-existing whitespace issues were not repaired or claimed byte-verified. Existing user history, Word/images, version changes, Tasks B–G and other working-tree changes were preserved. **Nothing staged, committed, pushed, tagged or published.**

Remaining limits: no authenticated source authorship, independently verified visual/byte association, automated exact workflow/version reconciliation, source-independence verification, cryptographic provenance validator or empirical forensic accuracy claim. Native/DPI and executable validation are separate release activities and were explicitly excluded. Actual Stable Diffusion source-image association remains unestablished; the stronger associated examples are clearly counterfactual acceptance scenarios. These are represented uncertainties, not hidden prerequisites for the bounded implementation.

**Status: Complete.** Claims, agreement, image association, dependence and technical authenticity now have separate, reproducible investigation-level meanings.
