# UI-2 regression results

|Validation|Result|
|---|---|
|Entry suite, before production edits|378 passed in 3.93s|
|Original suite after first shell integration|378 passed in 4.88s|
|Final complete suite|**406 passed in 7.53s; 0 failures, 0 errors, 0 skipped**|
|New UI-2 cases|28 cases in tests/test_workspace_shell.py|

Final command:

```powershell
py -3.13 -B doc/gui_modernization/ui1/run_tests.py tests -q -p no:cacheprovider --basetemp=doc/gui_modernization/ui2/test_runs/final_verified --junitxml=doc/gui_modernization/ui2/regression_results.xml
```

The inherited sandbox-compatible runner preserves test behavior while using inherited Windows temporary-directory permissions. Existing test source files were not modified. Intermediate layout testing found the offscreen plugin did not enumerate installed Windows fonts; tests/rendering now explicitly register the same installed fonts used natively. No failing case was skipped or weakened into a screenshot tolerance.

## New coverage

Tokens/contrast, scoped theme and injectable palette, component creation, textual lifecycle and confidence semantics, neutral tier styling, keyboard-copy metadata, disclosure, all six destinations, one checked active item, Ctrl+3 activation, navigation/result immutability, empty/selected/running/completed states, real progress routing, stale callback/snapshot rejection, same-session supersession, report/annotation synchronization, minimum-size control reachability, bounded status layout, split/navigation/geometry persistence, invalid/off-screen restore, maximized restore, no forensic content in preferences, modal Settings/OSINT opening/cancel and legacy narrative/artifact access. Stored-summary import updates the shell without analysis.

The full 378 inherited tests continue to cover session UUIDs, worker/QThread cleanup, deferred shutdown, source identity, ordered/late callback behavior, annotation draft failures, report publication, legacy loading and reasoning regressions. No timing sleeps or pixel-perfect screenshot assertions were added.

## Reference behavior

Final headless normal-profile analyses use the same controller/settings and authoritative summary as UI-1. reference_verification.json records exact comparisons of scores, patterns, confidence, full hypothesis assessments/evidence details and source hashes. The shell's offscreen visual validation also runs Instagram through the actual GUI worker/session/report path.

|Case|UI-1 measured suspicious / benign|Final UI-2|Finding|
|---|---|---|---|
|Instagram|21.327049999999996 / 2.25|Identical|High localized-editing support|
|Midjourney|6.674999999999999 / 1.5|Identical|Medium unverified generation declaration|

Instagram coverage remains 23 success. Midjourney remains 14 success, 8 skipped, 1 unavailable, zero failed; regional unavailability is preserved with reasons. Both source files are byte-for-byte unchanged against UI-1's recorded hashes. The earlier 20.47705 / 5.4 comparison is diagnosed separately in score_baseline_diagnostic.md; no scores were forced to match it.

Joblib emitted its pre-existing missing-WMIC physical-core warning and used logical cores; both pipelines completed. No dependency or Windows setting was changed.

## Visual and preservation checks

Native Windows: restored/maximized empty Overview, Settings and keyboard Reports navigation at primary DPR 1.0. Offscreen Qt: all six workspaces, actual selected/running/completed analysis, minimum 1040×720 and large 1600×1000 layouts, Settings and OSINT. Native completed/progress/other-DPI/packaged-build behavior is not claimed. UI-2-specific new source files and allowed existing-file changes are recorded in validation.json; inherited core/UI-1 modules, tests, settings and the user's DOCX match their entry hashes. Git diff whitespace checks pass. Nothing was staged or committed.
