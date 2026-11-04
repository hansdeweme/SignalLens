# Reasoning-engine Git baseline review

Review date: 2026-11-01. Entry branch: `fix/scorecard-integrity-phase2a`.
Entry HEAD: `f64f2262126da2a539813415f2bf49685f392571`.
Local `main` at entry: `1e77b1d`; it is an ancestor of the reviewed branch.

## Reviewed scope and disposition

The accumulated working-tree changes implement reconstructable score arithmetic,
evidence ancestry and diagnostic marginal analysis, production corroboration,
centralized hypothesis-specific confidence, and numerical restatement
deduplication. Integration edits are confined to the hypothesis/decision engine,
evidence scoping, signal wording, summary synthesis and reasoning persistence.
No unintended detector, dependency, GUI, packaging or settings modification was
found in the accumulated uncommitted diff.

The implementation commit contains **19 files**: 14 production Python modules
(six previously tracked integrations and eight new modules) and five new
regression files. The documentation commit contains **32 files**: six task
specifications, the Phase 2A/2B/3 reports and source inventories, the historical
acceptance audit and subsequent correction-6 reassessment, the source-audit
script, and this review record. Source-derived CSV inventories are deliberately
retained documentation; raw forensic output files are excluded.

The branch also contains three pre-existing commits above local main: ExifTool/
MediaPipe dependency documentation (`5da828e`), repository cleanup (`e8b672c`),
and Phase 1 reasoning/masking corrections (`f64f226`). Their existing history is
preserved. They are not silently rewritten as new phase commits.

## Reviewable commit structure

1. Commit the accumulated production corrections together with their regressions.
   Shared integration files make a fabricated historical phase split unsafe;
   this commit represents the actual tested final implementation.
2. Commit the reviewed specifications, inventories, reports and this record.
   Historical audit findings retain their original context; the Phase 2B.4
   acceptance reassessment records the later resolution.
3. Verify the index/working tree against the reviewed file lists and tested
   source hashes, then fast-forward local `main` to the reviewed branch.

This record describes the review and authorized merge procedure. Actual commit
identifiers and the completed merge are reported in Git history and the final
task response, avoiding a self-referential documentation commit hash.

## Validation and retained limitations

One focused run of the eight reasoning/pipeline regression modules completed:
**334 passed, 0 failed, 0 skipped**, in 2.65 seconds. This covers the entire
relevant regression set without running unrelated tooling or regenerating
historical audit inventories. The seven earlier regression files remain intact;
the numerical-deduplication file supplies the new Phase 2B.4 cases.

Previously completed full `subject_based` reference runs were reviewed from
the preserved Phase 2B.4 results: Instagram 23 successful stages, suspicious
20.47705 / benign 2.25, High localized editing; Midjourney 14 successful stages,
one unavailable and eight skipped regional stages, suspicious 5.4 / benign 1.5,
Medium unverified generation declaration. Neither had a failed stage or recorded
error. Independent arithmetic, input-image hashes, repeated-summary equality and
shadow/production equality passed. No source behavior was changed during this
repository-closing review, so the image pipelines were not repeated.

`git diff --check` passes. Reviewed additions contain no detected debug hooks,
private-key markers or common access-token prefixes. Known nonblocking numeric
overflow, malformed inactive details and unsupported partial-route limitations
remain documented in the acceptance audit. Statistical calibration and
independence are not claimed by this baseline.

## Exclusions and local review artifacts

Existing ignore rules exclude `test_images/`, `analyzed/`, prepared images,
Python caches and local logs. No file under those directories is tracked or
selected for either commit. The phase-only patch and byte snapshots remain
under ignored `analyzed/phase2b4_validation/`; the selected-file inventory and
validated source hashes for this closing review remain under ignored
`analyzed/git_baseline_review/`.

The authorized operation establishes a local Git baseline and merges it into
local main. No push, remote publication, tag, deletion, reset or history rewrite
is part of this review.
