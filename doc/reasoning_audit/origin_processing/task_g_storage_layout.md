# Task G: investigation storage layout and artifact lifecycle

2026-11-08. Bounded storage implementation on `main`, HEAD `6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`. Baseline: 525 passing cases with inherited Tasks B-F, version edits and other user work. Storage audit completed before changing allocation. No existing `analyzed/` history was moved, renamed, migrated or deleted.

## A. Storage architecture findings

| Original layer / artifact | Actual meaning and consumer |
|---|---|
| `<image stem>/` | Original basename grouping, not cryptographic identity. Old allocation did not normalize/truncate it or prevent basename collisions. |
| First 32-character UUID | `InvestigationSession.session_id`: independent investigation identity, including a new selection of identical bytes. `_session_dir` held mutable current source annotations. |
| Second 32-character UUID | `AnalysisInvocation.analysis_id`, also the completed `result_id`. A distinct invocation for each detector rerun. It is not the separate recorder's timestamp/short-UUID `RunRecorder.run_id`. |
| `analysis_run.json` | Execution, input, stage status, errors, diagnostics and artifact associations. Report publication adds investigation identity/summary paths. GUI recovery checks result ID and source SHA-256. |
| Investigation `osint_results.json` | Mutable current analyst evidence, saved through staging/replacement. Each immutable report also captures its own annotation state. |
| `report_revisions/<result>-a<revision>-<UUID>/summary/` | Unique physical report generation; JSON binds it to frozen result and current evidence revision. The extra random directory prevents overwriting an earlier bundle. `summary/` comes from shared serializers, not a separate identity. |
| `current_report.json` | Atomic publication pointer to a complete immutable report; not another authoritative summary. |
| `ui_artifacts_v1.json` | Existing source/result-bound artifact catalog: payload paths, raster hashes, identities and registration metadata. GUI rejects mismatched identities, escaped paths or changed rasters. |
| `prepared_images/` | Global/patch/subject RGB/resolution variants consumed by different detectors. Default prepared ELA RGB copy had no production reader: ELA reads the original source. |
| Regional `*_tmp.png` | Actual masked FFT inputs, retained in the regional payload's artifact references. Their names did not make them disposable. |
| Detector PNG/JPEG/JSON and masks | Measurements, diagnostics, GUI views and downstream inputs. Static `fft_results.json` was overwritten by regional calls; global plus earlier regional JSON could be lost although in-memory results survived. |
| `logs/` | Execution diagnostics and partial-run evidence. |

Writers/readers inspected: `InvestigationSession`, GUI selection/import/annotation/report methods, worker invocation, controller stages, gatekeeper, all naming producers, recorder, summary/trace serializers, report publisher/loader/exporter, artifact/provenance adapters and archive manager. Legacy artifact and summary recovery inferred roots from `summary/` and `report_revisions/` parents; metadata recovery also assumed the old stem-prefixed EXIF filename. These assumptions required explicit new-format paths while retaining legacy fallback.

Canonical image association remains the **full SHA-256**. Session, invocation/result, recorder-run and synthesis-revision identifiers retain their existing distinct meanings. Folder ordinals are presentation and allocation slots, never substitutes for these identities.

## B. Sources of path complexity

The original design deliberately isolated investigations, detector reruns and immutable report exports. The problem was expressing all identities as full directory UUIDs, repeating the complete image stem in many filenames, and adding a second serializer-created report directory. No flattening may collapse the three ownership boundaries.

Shared static FFT JSON naming also conflated global and regional computations on disk. Most `tmp`, mask and preview files have real consumers or diagnostic value; removing them by filename pattern would damage restoration or reproducibility. The only proven unconsumed prepared image was the default ELA copy.

## C. Implemented layout and allocation

```text
analyzed/
  .storage.lock
  high-quality, realistic fashion portrait of a yo/
    manifest.json                         # storage_format=2, full SHA, original name/path
    inv_001/                              # full investigation ID in manifest
      manifest.json
      .storage.lock
      osint_results.json                  # mutable current review, created when saved
      latest.json                         # single current-report publication pointer
      run_001/
        run_identity.json                 # full invocation/result/session IDs and source SHA
        analysis_run.json                 # recorder ID, execution and artifact associations
        ui_artifacts_v1.json
        evidence/
          metadata.json
          image_ela.png
          image_noise_residual.png
          global_fft.json
          global_fft_spectrum.png
          subject_input.png
          subject_input_fft.json
          boundary_input_fft.json
          background_input_fft.json
          ...
        prepared_images/
          global.png
          patch.png
          subject.png
        logs/run.log
      run_002/...
      reports/
        rev_001/                          # complete immutable bundle, no summary/ subdirectory
          final_summary.json
          final_summary.html
          final_summary.txt
          reasoning_trace.json
          reasoning_trace.txt
          osint_results.json
        rev_002/...
    inv_002/...                           # independent investigation of the same content
```

All names above are examples of actual format-2 contracts, not renamed historical files. Global/subject/boundary/background FFT results retain separate filenames. Detector-specific suffixes retain measurement/region/stage distinctions. CLI/direct producer calls outside a format-2 stage retain their prior naming contract.

`investigation_storage.py` owns the physical allocation adapter. Image wording is preserved, invalid Windows characters/control codes replaced, trailing periods/spaces removed, reserved device names prefixed, and the recognizable stem limited to **48 UTF-16 units**. Complete original filenames remain in image and investigation manifests and recorder input metadata.

An image container is reused only for a matching full SHA-256. A different image with the same case-insensitive normalized name gets `--<hash prefix>`; full hashes are checked and a colliding prefix expands rather than merging images. A same-content renamed source reuses the image container but receives a distinct investigation. Unknown-hash synthetic/legacy sessions are explicitly unknown and are not merged by filename.

Short ordinal directories use exclusive `mkdir` allocation under OS file locks. Windows locks are automatically released on process exit, so a crash does not leave an eternal application lock. Full identities live in manifests; simultaneous run reservations cannot collide. Existing legacy folders without format-2 manifests are never adopted or overwritten merely because their names match.

The controller scopes compact naming to each worker's stage using `ContextVar`; concurrent legacy and new stages cannot change one another's naming mode. No detector input pixels, thresholds, numerical weights, confidence or precedence rules changed.

## D. Compatibility and restoration

- New invocations allocate the compact layout. Existing trees, standalone summaries and `current_report.json` pointers remain readable in place.
- New `latest.json` uses the existing pointer schema and a relative path to the immutable bundle. No per-run competing current pointer is added for format 2.
- New summary investigation metadata records the physical forensic root and original forensic result ID. Artifact and metadata recovery validate that association against the recorder's full result/hash identity. Fresh import IDs do not impersonate original invocation IDs.
- Re-exporting a restored result preserves its original forensic-root/result association. A fresh import creates an independent investigation directory, **not another forensic run**; only explicit detector analysis allocates a run.
- Explicit export destinations use their own compact image/investigation/report namespace, separate from the live-run publication pointer. The captured report payload is unchanged.
- `ui_artifacts_v1.json` remains version 1, with the same path/hash/identity checks. Fallback discovery supports both short new filenames and the exact old contracts; global FFT recovery checks its recorded input.
- Investigation schema 1, original full result IDs, annotation revisions and synthesis revision IDs remain intact. Storage format 2 is a physical-layout distinction, not a changed forensic meaning.

No startup migration, destructive migration command, parent-directory UUID inference or prose-based recovery was introduced. Absolute original artifact-root associations remain intentional; moving a whole history tree or creating a standalone portable artifact bundle is not added by this task. Report pointers themselves are relative within their investigation.

## E. Artifact retention and failure lifecycle

| Class | Retention / cleanup |
|---|---|
| Frozen measurements, masks, overlays, previews, FFT diagnostics and catalogs | Retained. GUI discovery, later stages, interpretation auditing and saved restoration use these contracts. |
| Global/patch/subject prepared inputs | Retained as role-specific reproducibility inputs. Some may have identical pixels under current resolution policy, but roles can use different resolutions and have distinct consumers. |
| Default prepared ELA duplicate | Not generated for format-2 production defaults. ELA already reads the unchanged source. Legacy calls and explicit custom preparation policies retain their contract. |
| Regional FFT inputs | Retained under descriptive `subject_input`, `boundary_input`, `background_input` names. Never deleted merely because legacy names contained `tmp`. |
| Global and regional FFT JSON | All four retained separately; fixes output overwrite without changing any measurements. |
| Current OSINT and revision OSINT copies | Both required: mutable current evidence versus exact historical source state. Independent investigations never share a mutable record. |
| Immutable report formats/revisions | Retained. No deduplication or removal of previous bundles; supported HTML/TXT/JSON and trace exports remain available. |
| ELA recompression scratch JPEG | Existing producer cleanup remains unchanged. No historical referenced file is newly deleted. |
| JSON staging files / failed new allocations | Own staging file removed after success/failure. Failed metadata initialization removes only its newly reserved empty slot. A failed new report removes only its exclusive unpublished generation. |
| Interrupted detector runs | Retained with run identity, stage records, errors/logs and partial artifacts. No empty-success interpretation or automatic evidence deletion. Partial execution resume is not added; completed stored summaries remain the import boundary. |

Manifest and report-pointer writes now use same-directory temporary JSON, flush/fsync and atomic replacement. A real Windows sharing violation observed during manual GUI artifact reading led to a bounded retry: up to 10 replacement attempts, 20 ms between attempts; it never falls back to truncating a valid old record. Persistent write failure leaves the old record intact. Existing annotation commit/stale-result guards remain authoritative.

Report publication still happens only after all files are written and the captured session/revision remains current. Concurrent reservations have distinct slots. No general cache, transaction manager or cross-investigation OSINT sharing was introduced. Archive-manager destructive controls remain explicitly user-invoked; Task G adds no automatic historical cleanup.

## F. Before/after measurements and reference validation

Fresh controlled runs used the existing Midjourney PNG, SHA-256 `b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`, normal profile, the same recorded settings and source bytes. One legacy-layout/naming invocation and one compact invocation each completed all **23 stages**, without errors. Each measurement checkpoint contains one initial report and one GUI artifact catalog, before later OSINT edits/imports. No existing user run was used as a write destination.

| Measurement | Fresh legacy layout | Fresh compact layout |
|---|---:|---:|
| Maximum directory depth below the case output root (file excluded) | 6 | 4 |
| Longest actual generated Windows path | 379 characters | 169 characters |
| Longest relative path below the case output root | 328 characters | 121 characters |
| Files at initial checkpoint | 78 | 85 |
| Directories at initial checkpoint | 8 | 8 |
| Total bytes at initial checkpoint | 43,593,697 | 41,610,114 |
| Available GUI raster artifacts | 37 | 37 |

Actual control roots were `D:\Coding\SignalLens\.g_0727ea43\midjourney_legacy` and `...\midjourney_new`; their prefix lengths differ by three characters. The relative-path row removes that small prefix difference and is the like-for-like layout comparison. At the repository's ordinary `analyzed` root, these relative maxima correspond to 356 versus 149 characters (projection, not a write into the user's history).

The old longest generated filename repeated the full image name plus `_subject_background_tmp_fft_multi_grid_response.png`. The new longest path ended in `evidence/subject_subject_texture_consistency_overlay.png`. Directory count stays equal because named evidence/report groups remain, while report nesting and path components shrink.

The **seven additional files** are intentional: three recovered FFT JSON records previously overwritten, three identity/version manifests, two allocation-lock files, minus one unconsumed prepared ELA copy. Total size falls by 1,983,583 bytes, principally the omitted ELA copy and shorter repeated path strings. This is not a claim that all intermediate diagnostics were redundant.

The complete Midjourney scorecards from the two fresh runs are exactly equal: suspicious **18.04075**, benign **1.50**, local support **5.25**, edit boost **2.295**, clone support **0.7500000000000001**. Primary synthetic origin / Medium, localized Low, camera Medium; existing qualified separate-edit semantics unchanged.

Manual source-state update demonstrated unchanged frozen forensic JSON and byte-identical first report files, with a distinct later immutable report. Reopened through `latest.json`, re-exported under a fresh import, reopened again and recovered the same **37 raster hashes**. No detector rerun occurred during those source/report actions.

The existing Nikon D7500 photograph was also freshly analyzed: 14 stages succeeded, 8 skipped, one unavailable, no failures; known partial mask coverage remained explicit. Initial compact checkpoint: **49 files, 8 directories, 8,071,479 bytes**, maximum depth **4**, maximum actual path **162 characters**, **23 available raster artifacts**. Source revision, report immutability, repeated restoration and artifact-hash equality passed. No new source image fixture was added.

A generated path under a longer Unicode portable/output location measured **229 characters**, below 260, including the actual workspace/control root and the longest representative artifact basename. Reserved names, separators/traversal, trailing characters, case-insensitive collisions, Unicode UTF-16 length, same-content reuse, short-hash collisions and concurrent run allocation are covered by the bounded regression checks. Arbitrarily deep user-chosen output roots cannot be made universally shorter than Windows limits; this implementation does not depend exclusively on long-path support.

The full standalone measurement harness completed its checkpoint assertions; one invocation returned a nonzero process status after printing its result, so that invocation is not claimed as clean shutdown evidence. A separate final GUI reopen/export check completed with exit 0 and no asynchronous Qt errors. The complete regression process also exited 0. Controlled experiments were repeated only after the demonstrated sharing failure and subsequent retention/export changes, not to accumulate equivalent green runs.

Packaged storage smoke finalized on 2026-11-10: the isolated PyInstaller executable exited **0**, with `sys.frozen=True`, all **23 stages successful**, no errors/skips/unavailable stages, **37 available raster artifacts**, and matching artifact hashes after saved-report restoration. Suspicious score remained **18.04075**, benign **1.50**, local support **5.25**, edit boost **2.295**, and clone support **0.7500000000000001**. Longest generated path under the longer packaged `dist/SignalLens/analyzed` root was **194 characters**. Evidence is retained in `.g_0727ea43/packaged_check/smoke_result_complete.json`.

The first continuation attempt failed because the inherited isolated bundle lacked `exiftool_files/lib/Image/ExifTool.pm`. Copying the complete existing `exiftool_files` directory, as required by `run_pyinstaller.cmd`, repaired the validation bundle; production code and packaging scripts needed no changes. The failed investigation remains separate as `inv_001`, and the successful retry allocated `inv_002/run_001`, preserving the failed-run evidence. The earlier smoke-hook ndarray serialization failure was confined to the validation harness. This is a frozen storage/pipeline smoke check, not native visual or DPI acceptance.

## G. Regression results and test discipline

Baseline **525**. Added **2**, removed **0**, consolidated **0**; final **527**, net **+2**, within the task maximum.

Newly protected contracts:

1. Existing investigation-contract module: Windows-safe recognizable allocation, full-identity collision discrimination, independent investigation ownership and concurrent run reservation. No prior physical-layout allocator existed to extend for this invariant.
2. Existing mask/pipeline module: real gatekeeper preserves the exact bytes of all consumed prepared roles while omitting only the unused default ELA copy. Previous pipeline tests stubbed preparation and could not detect that failure.

Extended authoritative annotation/report immutability, report failure/pointer publication/retry, saved roundtrip and patch producer-output tests. Reused existing legacy import, source-hash rejection, worker ownership, artifact-path/hash/registration, metadata recovery and export byte-consistency coverage. The shared GUI setup helper now accepts the intentionally pre-reserved run directory; no lifecycle assertions were removed. No golden baseline or private-image fixture changed.

Latest focused group:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests/test_mask_pipeline.py tests/test_investigation_contracts.py tests/test_scorecard_integrity.py tests/test_provenance_reporting.py -q`

**133 passed in 4.25s.** Earlier broader storage/artifact/lifecycle group: **190 passed** before the second added preparation case. Final complete gate after all production/test edits:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q`

**527 passed in 22.31s; 0 failed, 0 skipped.** No repeated complete run for documentation/build-only work.

Continuation on 2026-11-10 independently reconfirmed **527 collected cases** using the established runner with `tests --collect-only -q` (exit 0). No production/test changes or additional collected cases were made during continuation; the full-suite outcome above is the recorded final implementation gate, not a newly executed run.

## H. Change inventory, Git discipline and limits

New production adapter: `investigation_storage.py`. Allocation/lifecycle integration: `investigation_session.py`, `signallens_gui.py`, `investigation_workers.py`. Report persistence/recovery/export: `investigation_reports.py`, `summary_persistence.py`, `reasoning_persistence.py`, `report_workspace.py`, `run_reporting.py`. Artifact/provenance recovery: `artifact_presenter.py`, `provenance_presenter.py`. Controller/preparation: `signallens_controller.py`, `image_gatekeeper.py`.

Output-name-only adapters: `vf_ela.py`, `vf_noise.py`, `vf_fft.py`, `vf_region_fft.py`, `vf_overlay.py`, `vf_patch_similarity.py`, `vf_person_subject_mask.py`, `vf_region_masks.py`, `vf_boundary_focus.py`, `vf_sensor_origin.py`, `vf_cfa_demosaic.py`, `vf_subject_boundary.py`, `vf_subject_texture_consistency.py`, `vf_subject_process_asymmetry.py`, `vf_subject_material_realism.py`, `vf_compression_history.py`. These retain all detector calculations and default legacy producer contracts.

Tests changed only in `tests/test_investigation_contracts.py`, `tests/test_mask_pipeline.py`, `tests/test_scorecard_integrity.py`, and `tests/gui_helpers.py`. This report is the only permanent Task G documentation addition. Measurement/build files remain confined to the existing `.g_*` workspace children and `.task_g_validate.py`; the continuation retained these inherited validation artifacts for review rather than deleting them.

Captured the inherited status/content inventory before changes. Unrelated inherited code, version edits, user Word/images, existing audit documents, old deleted artifacts and original history remain preserved. Permission-denied inherited paths cannot be byte-verified. Nothing staged, committed, pushed, tagged or published.

Native visual/DPI inspection, a whole-machine release matrix, relocated historical artifact bundles and automatic incomplete-run resumption remain outside this bounded storage correction. No claim of improved forensic accuracy is made.

## Completion status

**Complete** for bounded Task G. The pending packaged storage check is now passed. Nothing was staged, committed, pushed, tagged or published during continuation. Only this report and isolated validation outputs/support files changed; unrelated inherited work and the user's original `analyzed/` history were preserved.
