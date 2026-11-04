# Regression and reference results

Baseline before implementation: **468 passed, 0 failed, 0 skipped**, main at 656df834f209f9c03161d25074b81e2c317e6a57. Final: **509 passed, 0 failed, 0 skipped**. See regression_results.xml for exact cases/duration. Command: `py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q --junitxml=doc/gui_modernization/ui5/regression_results.xml`. The established UI-4 runner retains sandbox-readable workspace temporary folders and disables the inaccessible old pytest cache; no assertions or tests are bypassed.

The 41 UI-5 cases cover immutable projections, three hypothesis families, role-specific duplicates, detector/reliability/status filters, empty matches, final policy precedence/caps, ordered route dispositions, compound-gate semantics, raw/credited/suppressed numerical values, invalid numerics, schema versus recorded ancestry, cyclic/missing intermediate nodes, absent lineage, malformed/partial results, missing targets, Overview/Evidence/Reasoning routing, stale selection, annotation refresh, reanalysis, closing, explicit artifact identities, arithmetic replay/mismatch/incomplete/error outcomes and bounded Back navigation. Existing UI-1 through UI-4, scoring, confidence, OSINT and report regressions remain passing.

| Reference | Profile | Suspicious (exact stored) | Benign | Finding / tier | Scoped evidence | Routes | Gates | Base rows | Arithmetic |
|---|---|---:|---:|---|---:|---:|---:|---:|---|
| Instagram | normal | 21.327049999999996 | 2.25 | possible_foreground_background_processing_mismatch / High | 22 | 20 | 5 | 13 | Reconciled |
| Midjourney | normal | 6.674999999999999 | 1.5 | provenance_supported_synthetic_context / Medium | 15 | 20 | 4 | 6 | Reconciled |

Reference validation reopens the actual saved UI-3 production reports without rerunning detectors. Source hashes and profile match baseline; every `(hypothesis, role, evidence ID)` matches the stored assessment arrays. Recorded confidence rules remain unchanged. Explicit UI-4 navigation succeeds for CFA evidence/artifact in Instagram and sensor evidence/artifact in Midjourney. Both summary JSON and original report-pointer bytes remain unchanged. reference_results.json records hashes, rules, counts and targets. No native desktop/DPI validation or broad empirical calibration is claimed.
