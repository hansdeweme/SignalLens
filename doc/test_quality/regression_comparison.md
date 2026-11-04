# Baseline versus final regression comparison

| Metric | Baseline | Final | Change |
|---|---:|---:|---:|
| Collected cases | 509 | 504 | −5 |
| Source function groups | 309 | 307 | −2 |
| Modules | 14 | 14 | 0 |
| Passed | 509 | 504 | All collected cases passed |
| Failed | 0 | 0 | 0 |
| Skipped | 0 | 0 | 0 |
| Test warnings | 0 | 0 | 0 |
| pytest summary duration | 17.73 s | 15.57 s | −2.16 s (12.2%) |
| Reporter wall duration through session finish | 18.018 s | 17.457 s | −0.562 s (3.1%) |
| Summed setup/call/teardown duration | 14.897 s | 14.874 s | Approximately unchanged |
| Case fixture closures requesting a desktop window | 108 | 102 | −6 |

Different clock boundaries explain the different timing reductions: pytest's summary and the report plugin include startup/collection overhead differently. A single run per state is not statistical evidence of a repeatable speedup. No repeated full runs were performed to select a faster sample. Raw measurements, phase timings and the 20 slowest total-phase nodes are in baseline.json/final.json; final_results.xml records the final gate. The inventory also reports per-module phase costs and slow baseline nodes.

## Reproducible commands

Baseline: `py -3.13 tools/test_suite_report.py --output doc/test_quality/baseline.json tests -q`.

Final: `py -3.13 tools/test_suite_report.py --output doc/test_quality/final.json tests -q --junitxml=doc/test_quality/final_results.xml`.

Retained-assertion fault probes: `py -3.13 tools/check_test_retention.py`. These intentionally make selected assertions fail in child processes; success means the faults were detected, not that production tests fail. The six final probes all passed this detection check.

The reporting runner reuses the established UI-4 sandbox-readable temporary directory fixture and disables the inaccessible legacy pytest cache. It neither skips nor rewrites assertions. Plain pytest remains appropriate outside this Windows sandbox.

## Critical coverage comparison

| Area | Before / after protection |
|---|---|
| Reasoning/provenance/confidence | All substantive inputs retained; repeated-order/policy and metadata-classification assertions consolidated into stronger owners. Empty-input neutrality remains in the full no-invented-evidence test. |
| Scorecard/numerical allocation | Independent/randomized arithmetic oracles and corruption matrices untouched. Card immutability now shares the stronger shadow/replay owner for both references. |
| Lineage/corroboration | All 48 diagnostic-lineage and 30 production-corroboration cases retained. Schema, diagnostic and production boundaries remain separate. |
| Sessions/worker/report safety | All 23 pure session/report and 21 worker GUI cases retained. Specialized safe worker teardown remains. |
| Source/artifact/registration | All 26 Overview/source and 36 artifact cases retained, including stale delivery, affine mapping, EXIF, synchronization and native overlay-item lifetime. |
| Evidence/Reasoning Explorer | All 41 cases retained. Six pure cases use pure inputs; actual widget integration remains. Filter and numeric-state assertions are stronger. |
| Navigation/OSINT/stored compatibility | All 28 shell cases retained. Shared app lifetime and isolated settings replace duplicated setup without removing command, preference or import scenarios. |

No production scoring, detector, decision, confidence, lineage, provenance or report-content file was edited for this task. Existing reference regression mechanisms ran as part of the suite; full private-image pipelines were not repeated. Their scores/outcomes are protected by the retained reasoning/scorecard/policy reference cases. Native DPI/maximization and empirical generalization beyond the limited reference dataset remain unverified; no new claim is made here.
