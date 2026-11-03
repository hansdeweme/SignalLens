# UI-3 regression results

Baseline: `main` at `05fd6dc685a7c704aadf482d512f8f6026fd089b`; **406 passed**, 0 failed/errors/skipped. Final: **432 passed in 40.96s**, 0 failed/errors/skipped. Original test files were not changed. New `tests/test_overview_workspace.py` contributes 26 cases.

Run from repository root:

```powershell
py -3.13 -B doc/gui_modernization/ui1/run_tests.py tests -q -p no:cacheprovider --basetemp=doc/gui_modernization/ui3/test_runs/final --junitxml=doc/gui_modernization/ui3/regression_results.xml
```

The existing wrapper only avoids the inherited Windows sandbox mkdir(0700) ACL problem. It does not change forensic algorithms or test assertions. Generated test workspaces and detector outputs remain ignored/local. GUI tests register the already-installed Segoe UI fonts for the Windows offscreen plugin; this is not native font/DPI certification.

New coverage: portrait/panorama/tall/large sources; missing/corrupt/hash-mismatched sources; actual off-GUI-thread photo loading; fit/zoom without pixel reload; stale delivery and file-change rejection; exact High/Medium/Inconclusive/unavailable primary tiers; three distinct cards/missing assessments; missing confidence data; capped role order/source identity; unavailable masks/provenance caveats; five destination actions; narrative and annotation consistency; lifecycle clearing; imported profile/hash/missing-source handling; long structured text and no horizontal scrolling at 1040×720, 1280×900 and 1600×1000. Existing UI-1/UI-2 tests continue covering reentrancy, stale worker callbacks, report revisions, menus/dialogs, keyboard navigation and preferences.

Both full GUI reference analyses were executed by capture_validation.py. It asserts exact equality to UI-2 for source hash, suspicious/benign scores, pattern, confidence, complete hypothesis structures (including role lists, evidence details and limitations) and coverage counts. It checks unchanged source bytes and current reports. See reference_verification.json for captured settings/profile/context and full data.

| Reference | Profile | Suspicious | Benign | Primary result | Stage success/skipped/unavailable/failed |
|---|---|---:|---:|---|---|
| Instagram | normal | 21.327049999999996 | 2.25 | High localized editing | 23 / 0 / 0 / 0 |
| Midjourney | normal | 6.674999999999999 | 1.5 | Medium synthetic context, unverified declaration | 14 / 8 / 1 / 0 |

Instagram SHA-256: `1feeccab1ddce2b24ddec95447e5c86cbbf2b77deabf7b01c76bdf3388d219f9`.

Midjourney SHA-256: `08c27f51a3bc9f6546d9ca3f99ad910ae293d2610679d1fdea6e53130902dda9`.

Midjourney's 0.918178 foreground area exceeds the existing 0.90 usable-mask bound: regional stages remain unavailable/skipped. It is not negative evidence. The existing joblib WMIC physical-core warning falls back to logical cores; analyses complete successfully. No thresholds/dependencies were modified to suppress it.

Native Windows analysis, source selection, normal/minimum/maximized rendering and detail navigation were additionally inspected as documented in visual_validation.md. Deterministic inconclusive/failed/missing-source visual fixtures are explicitly not claimed as new measured reference outcomes.
