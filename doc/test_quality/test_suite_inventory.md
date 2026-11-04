# Test suite inventory

Baseline: main at 656df834f209f9c03161d25074b81e2c317e6a57, 509 passing cases / 309 source groups in 14 modules. Final: 504 passing cases / 307 groups. Zero failures, skips or warnings in both complete runs. No whole-function exact duplicate was established; four reviewed overlaps were consolidated.

The complete per-node inventory is [test_node_inventory.csv](test_node_inventory.csv); the readable per-group inventory is [test_group_inventory.md](test_group_inventory.md). Baseline/final JSON retain the original assertions, calls, fixture closures, phase outcomes, durations and slowest nodes. Requirements and production-owner descriptions were classified against source; AST assertion similarity was used only to find candidates.

| Module | Baseline | Final | Baseline summed test-phase s | Final summed test-phase s | Responsibility |
|---|---:|---:|---:|---:|---|
| tests\test_confidence_policy.py | 35 | 34 | 0.093 | 0.093 | Central confidence rules, typed verification, policy precedence, coverage limits and serialized policy consistency. |
| tests\test_evidence_lineage.py | 48 | 48 | 0.045 | 0.045 | Immutable lineage registry, diagnostic ancestry/credit, malformed graphs and non-mutating shadow analysis. |
| tests\test_explorer_workspace.py | 41 | 41 | 4.116 | 3.236 | Scoped explorer projections, filters/details, reference routing, missing targets and selection integrity. |
| tests\test_forensic_workspace.py | 36 | 36 | 3.501 | 3.763 | Artifact identity/path/hash, source registration, native coordinates, comparison gates and Qt scene lifecycle. |
| tests\test_hypothesis_scoping.py | 28 | 26 | 0.061 | 0.060 | Hypothesis-relative observations/roles and authoritative JSON/text/HTML narratives. |
| tests\test_investigation_contracts.py | 23 | 23 | 0.159 | 0.169 | Pure session/invocation/revision contracts, report bundles, import identity and presentation mapping. |
| tests\test_investigation_gui.py | 21 | 21 | 2.100 | 2.137 | Owned Qt worker threads, terminal callback ownership, annotation dialogs, report failure and import transactions. |
| tests\test_mask_pipeline.py | 32 | 32 | 0.368 | 0.356 | Synthetic mask geometry, availability and controller stage isolation with deterministic detector stubs. |
| tests\test_numerical_evidence.py | 37 | 37 | 0.034 | 0.040 | Production numerical identity/restatement suppression, ledger validation and adjusted-score propagation. |
| tests\test_overview_workspace.py | 26 | 26 | 2.300 | 2.296 | Bounded source preview plus Overview recorded findings, display budgets, lifecycle and layout. |
| tests\test_production_corroboration.py | 30 | 30 | 0.032 | 0.032 | Production source diversity versus compound requirements, eligibility and trace propagation. |
| tests\test_reasoning.py | 61 | 59 | 0.101 | 0.099 | Decision routing, metadata interpretation, source-type/prompt extraction and reference-derived synthesis. |
| tests\test_scorecard_integrity.py | 63 | 63 | 0.320 | 0.342 | Status weights, arithmetic transforms, invalid inputs, ledger corruption and independent reconstruction. |
| tests\test_workspace_shell.py | 28 | 28 | 1.667 | 2.207 | Theme/components, shell navigation, snapshot binding, preferences and existing command/report access. |

## Domain classification

The reporter assigns one primary domain per case for navigation; many cases cross a second boundary. These are not coverage percentages. In particular, mask pipeline tests use controlled detector substitutes and do not constitute blanket validation of every vf_* implementation.

| Domain | Baseline cases | Final cases |
|---|---:|---:|
| Confidence policy | 34 | 33 |
| Stored-result compatibility | 18 | 18 |
| Evidence lineage and corroboration | 78 | 78 |
| Evidence and Reasoning explorers | 40 | 40 |
| OSINT and report consistency | 13 | 13 |
| Image artifact viewing | 45 | 45 |
| Reasoning and hypothesis selection | 87 | 83 |
| Investigation sessions | 14 | 14 |
| Worker lifecycle | 12 | 12 |
| Forensic detectors and signal extraction | 29 | 29 |
| Scorecard calculation | 100 | 100 |
| GUI navigation and state | 39 | 39 |

## Runtime and fixtures

Baseline pytest summary: 17.73 s; final pytest summary: 15.57 s. Reporter wall measurements from plugin construction through session finish are separately 18.018 s and 17.457 s. Both include collection overhead differently; compare like with like. Summed per-test setup/call/teardown durations are 14.897 s and 14.874 s. A single run per state does not establish a statistically reliable speedup.

Baseline test closures requested window 108 times; final closures request it 102 times. Six adapter-only checks now use a pure projection fixture. The shared application has one session lifetime; every ordinary window/source/settings/projection is function-scoped. The real-worker window fixture intentionally remains separate for semaphore release and safe teardown.

| Slowest baseline node (total phases) | Seconds |
|---|---:|
| `tests/test_scorecard_integrity.py::test_randomized_calculations_are_finite_deterministic_and_reconstructable` | 0.2567 |
| `tests/test_investigation_gui.py::test_osint_edits_refresh_view_and_report_without_any_resynthesis` | 0.2501 |
| `tests/test_explorer_workspace.py::test_projection_is_immutable_and_does_not_mutate_recorded_result` | 0.2232 |
| `tests/test_forensic_workspace.py::test_bad_artifacts_fail_closed[corrupt]` | 0.2134 |
| `tests/test_workspace_shell.py::test_workspace_preferences_contain_no_forensic_content_and_restore` | 0.2110 |
| `tests/test_overview_workspace.py::test_profile_is_captured_and_imported_source_identity_is_preserved` | 0.1837 |
| `tests/test_investigation_gui.py::test_real_gui_launch_path_freezes_settings_context_and_run_annotations` | 0.1831 |
| `tests/test_workspace_shell.py::test_all_destinations_and_keyboard_navigation_do_not_mutate_session` | 0.1792 |
| `tests/test_overview_workspace.py::test_navigation_and_narrative_preserve_snapshot_and_annotations` | 0.1792 |
| `tests/test_workspace_shell.py::test_settings_and_osint_dialog_workflows_still_open` | 0.1727 |

The preserved randomized scorecard oracle is inexpensive relative to the whole suite and protects independently reconstructed arithmetic. GUI windows and representative large decode/coordinate tests dominate the measured cases. No image dimensions or random sample sizes were reduced to make the suite appear faster. Optional tools/test_suite_report.py regenerates node/module/domain/timing data without a new dependency.
