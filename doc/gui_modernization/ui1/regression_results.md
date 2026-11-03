# UI-1 regression results

## Test runs

|Run|Result|
|---|---|
|Baseline, before production edits|334 passed in 2.75s|
|Original tests after first integration|334 passed in 2.84s|
|Final complete tests directory|**378 passed in 3.98s; 0 failed, 0 errors, 0 skipped**|
|New tests|44 additional cases: 23 pure contract/report cases and 21 offscreen GUI/worker cases|

Final machine-readable evidence: regression_results.xml. Command:

```powershell
py -3.13 -B doc/gui_modernization/ui1/run_tests.py tests -q -p no:cacheprovider --basetemp=doc/gui_modernization/ui1/test_runs/final_verified --junitxml=doc/gui_modernization/ui1/regression_results.xml
```

Use a fresh basetemp name for a repeat run to preserve prior diagnostic files. Tests are selected from `tests/` so inherited audit temporary directories are not accidentally collected.

Initial baseline attempts hit missing temporary-directory parent and Python 3.13 Windows mode=0700 sandbox ACL problems. The elevated rerun was declined; no elevated testing occurred. run_tests.py changes only mkdir's 0700 test-runner mode to inherited/default permissions inside the existing sandbox and creates basetemp's parent. It does not change production code/ACLs or tests. Intermediate new tests exposed incomplete legacy trace rendering; the report writer now preserves exact raw fields with an explicitly labeled fallback instead of fabricating missing interpretation. A later test-runner parent-path error was fixed in the harness. No final test is skipped or suppressed.

## What the new tests establish

Session UUID uniqueness, same-file independent investigations, distinct reanalysis IDs/output folders, launch configuration immutability, invalid/duplicate terminal handling, failure recovery, logical cancellation, clearing/reselection invalidation and explicit legacy import identity.

Actual QThread execution with semaphore-controlled workers verifies named queued GUI-thread delivery, success/error cleanup, newer run finishing before older work, obsolete terminal progress/log/error rejection, and nonblocking deferred close without publication. Signal-driven event loops use deadlines solely for test failure detection; there are no arbitrary sleeps. Additional cases exercise launch through the actual Run method, completion while an OSINT dialog is open, selection during immutable snapshot emission, archive deletion guards and source replacement checks.

Annotation/report tests cover repeated commits, cancelled dialogs, switching investigations with unsaved drafts, no silent resynthesis, annotation save failures, current/report revision parity, stale snapshot rejection, atomic-pointer preservation on export failure, retry, stored annotations, and legacy/new import round trips. Presentation tests cover recorded fields, missing vs empty roles, separate hypotheses, policy tier preservation, low/inconclusive outcomes, explicit verification states, unavailable stages, source/lineage references, determinism and original input immutability.

Text-only legacy imports are displayed/exported literally with escaped text; missing hypotheses remain unknown rather than inferred from that narrative.

## Real-image before/after

Both specified source images were available and run headlessly **before** and **after** production changes using the established controller/summary pipeline. The after run also exercised captured settings, presentation building, report identity checks and publication. Exact recorded evidence is in reference_before.json, reference_after.json and reference_comparison.json; generated images and result directories are ignored by Git.

|Reference|Measured pre-change score suspicious / benign|Post-change|Conclusion|
|---|---|---|---|
|Instagram `insta_fake/Curvy Leggings Outfit.jpg`|21.327049999999996 / 2.25|Identical|High; possible_foreground_background_processing_mismatch / localized editing|
|Midjourney specified PNG|6.674999999999999 / 1.5|Identical|Medium; provenance_supported_synthetic_context / unverified generation declaration|

The task quoted older suspicious scores 20.47705 and 5.4. The **actual pre-edit** checkout produced 21.32705 and 6.675. No scoring was changed to chase historical numbers. All per-hypothesis assessments—including confidence tiers, evidence roles/details and limitations—match exactly before/after. Both input SHA-256 hashes match before and after both runs.

Instagram coverage remained complete: 23 successful stages. Midjourney remained partial: 14 success, 8 skipped, 1 unavailable, 0 failed. Its person mask failed the existing usable-area bound, and nine regional stages remain explicitly unavailable/skipped, not converted to benign findings. The pure adapter preserves stage status/reasons and authoritative hypothesis/decision fields; report metadata points to the correct source and invocation. Backend durations naturally differ and are not forensic-equivalence assertions.

Joblib emitted a Windows missing-WMIC physical-core lookup warning and fell back to logical cores. Both runs completed successfully; no dependency was installed or environment configuration changed.

## Unsupported / unverified

No physical cancellation, no forced termination/logout safety guarantee, no new manual native GUI/DPI audit and no packaged executable rebuild. Standard application close is covered by offscreen QThread integration. A permanently stuck backend remains owned and can delay closure; report disk failures remain visible and retryable. Presentation contracts do not manufacture missing historical fields or cryptographic provenance validation.
