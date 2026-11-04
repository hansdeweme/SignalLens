# UI-6 test accounting and validation

| Metric | Count |
|---|---:|
| Baseline collected (fresh collection) | 504 |
| Added collected cases / new function groups | 10 / 10 |
| Consolidated in UI-6 | 0 |
| Removed in UI-6 | 0 |
| Final collected | 514 |
| Net change | +10 |
| Final passed | 514 |
| Failed / skipped / warnings | 0 / 0 / 0 |

The inherited baseline's previous full gate was 504 passes; UI-6 verified current collection and used targeted owner tests during implementation. The single final complete gate ran after the final source/test edits: **514 passed in 16.16 seconds**, zero failures/skips/warnings. regression_results.xml lists exact cases; regression_results.json includes node/fixture/phase timings and reporter-clock duration. No additional complete run is required for these documentation changes.

Command: `py -3.13 tools/test_suite_report.py --output doc/gui_modernization/ui6/regression_results.json tests -q --junitxml=doc/gui_modernization/ui6/regression_results.xml`. The established sandbox-readable temporary fixture is reused; nothing is skipped.

The ten new tests in test_provenance_reporting.py follow the preimplementation coverage audit. Four protect recorded field trust/value/association, unavailable-versus-missing status, negative metadata filtering/binary description and stored payload identity. One connects existing OSINT commit to the new visible revision/source detail. Four cover exact preview/export bytes with legacy fallback, actual off-GUI captured-snapshot export, rejected obsolete presentation/completion and actual background write failure. One covers explicit provenance-field navigation plus annotation revision. Each protects a new UI-6 boundary; the group does not repeat the complete session/worker lifecycle. Existing cancellation, save failure, reanalysis, report atomicity, metadata classification, confidence semantics and reference-derived scoring tests remain their authoritative owners. No full image pipeline was repeated and no new fixture framework/dependency was introduced.

Saved-reference acceptance reopens the real normal-profile UI-3 reports. Source hashes and confidence wording remain as recorded. Instagram exposes 7 retained metadata/source fields; Midjourney exposes 10. Both record verification as unverified. A controlled imported-session annotation edit advances revision 0→1 and updates report preview without changing frozen forensic JSON. The actual exported HTML/TXT sources and structured JSON match ReportPresentation, while original baseline report-pointer hashes remain equal. reference_validation.json records exact scores, findings, hashes, revisions and output pointers. Original images and saved baseline artifacts were not modified.

Native Windows/DPI validation remains unavailable in this offscreen run and is recorded for UI-7. Passing synthetic/contract tests and these two saved references do not establish empirical forensic calibration or complete metadata coverage.
