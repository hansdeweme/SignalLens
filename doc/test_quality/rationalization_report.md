# Test suite rationalization report

## Baseline and scope

main at 656df834f209f9c03161d25074b81e2c317e6a57, the committed UI-4 baseline. UI-5 remained inherited/uncommitted: .gitignore, the shell/theme/state and Overview/artifact navigation changes, three explorer modules, its tests and documentation. Both task documents were untracked. The inaccessible tracked audit/pytest_verified fixtures continued to appear deleted in Git; none were repaired, deleted or discarded. No production source file was changed during this task.

The successful baseline full run collected and passed 509 cases, with zero failures/skips/warnings (pytest summary 17.73 s). The audit records all 509 node IDs and 309 source groups across 14 modules. Source calls, assertions, fixture dependency locations and setup/call/teardown costs are preserved in baseline.json and the node/group inventory. A reporter collection bug was corrected before any baseline tests executed; the baseline results shown here are the subsequent complete successful run.

## Decisions and accounting

Four confirmed overlapping groups were consolidated, with six original case executions absorbed by retained owners. Two original function groups were removed: duplicate confidence-policy order/repetition (2 cases) and separate scoping card-immutability (2 cases). Two duplicate parameter inputs were removed: empty synthesis polarity and IPTC digitalCapture classification. The stronger card/shadow audit gained one Midjourney parameter instance. No new regression test function/group was added. Final collection is **504 cases / 307 groups**, net **−5**.

The remaining 503 original cases are retained at their behavioral boundaries; one existing owner is parameterized over the additional preserved input. Parameter IDs for benign results and invalid display values were made explicit/expanded without losing the retained inputs. Counts are cases, not just function definitions. Most of the suite was kept deliberately: similar names often protected distinct source/decoder/widget, session/worker/navigation, policy/presentation or serializer/GUI boundaries. The reviewed distinctions are in test_overlap_matrix.md.

## Fixture and assertion improvements

- tests/conftest.py owns one session-scoped QApplication and function-scoped ordinary window/source fixtures. Fonts are registered once; windows/settings/results remain isolated.
- tests/gui_helpers.py holds the existing publish, bounded-preview wait and set_trace helpers. Four GUI modules use this ordinary helper module; dependent modules no longer import fixtures/helpers from another test module, avoiding repeated app registration and hidden collection coupling.
- The worker suite retains its specialized semaphore-aware window teardown, now with test-local QSettings instead of the user's ordinary workspace preferences.
- Six pure UI-5 projection checks use a minimal completed InvestigationSession and recorded trace; they no longer launch a full window merely to inspect immutable adapter values. Live filter, routing, lineage-selection and stale-content tests remain GUI integrations.
- Filter tests now include an excluded row and require the exact returned tuple. Previously the detector/reliability/status cases could pass when a control was ignored because all rows shared the same attribute.
- Invalid numeric-display cases distinguish absent/non-numeric inputs from non-finite values exactly. Lifecycle-label cases assert the actual label; repeated confidence/color assertions moved to their existing owner groups, preserving all state/tier inputs.

This is a small shared-fixture arrangement, not a factory framework. Existing reasoning section/reference helpers remain where they are; moving every helper was not necessary to remove demonstrated duplication.

## Coverage-preservation evidence

tools/check_test_retention.py runs six isolated targeted probes. It monkeypatches only in-memory callables/signals in separate child processes; no production file is edited and no mutation-testing dependency is added. All six faults were detected by retained **call-phase assertions**, with no setup/teardown errors: reverse-order policy changes, repeat-evaluation changes, scorecard mutation, non-neutral empty synthesis, digitalCapture falsely marked enhancement, and ignored detector filtering. See fault_injection_results.json. The Qt filter probe explicitly replaces the existing signal callback because Qt retains the bound slot connected before monkeypatching the class.

No central worker, session, report-bundle, arithmetic oracle, numerical-allocation, image-registration or confidence/provenance boundary group was removed. Matrix rows explain which retained test owns each invariant and why adjacent integration layers remain. A green reduced suite alone was not used as proof of equivalence. These six probes are concrete examples, not an exhaustive mutation score.

The final complete suite was run after the final test/fixture change: **504 passed, 0 failed, 0 skipped, 0 warnings**, pytest summary 15.57 s. Targeted runs were used during edits and for deliberate faults; no additional full reference pipelines were launched. Existing synthetic/reference-derived reasoning, scorecard, policy and controller regressions passed. Native Windows DPI and empirical calibration gaps remain separate from this test-only task.

## Mandatory future discipline

Root AGENTS.md requires reading TEST_DISCIPLINE.md and consulting the behavioral coverage matrix before adding tests. The policy mandates coverage searches, stable contracts, shared ownership, minimal pipeline repetition, justified new groups, transparent case accounting and a final complete-suite gate. A net growth greater than 10 collected cases per future GUI phase requires explicit final-report justification; it is not a hard cap and cannot be gamed with giant unrelated tests.

## Remaining concerns

Legacy narrative/compatibility assertions and older reasoning fixture dictionaries may contain additional overlap, but equivalent defect protection was not established, so they remain. Several tests inspect private state to protect real Qt/session failure paths; replacing them requires an equally strong observable oracle. The optional reporter uses pytest fixture metadata for inventory, so a major pytest API change may require a tooling-only update. Single-run timing differences are not a reliable performance benchmark; the durable benefit is clearer ownership, six fewer desktop constructions, shared setup and fewer redundant scenarios.

No files were staged, committed, pushed, merged, tagged, reset or stashed. No reference images or existing forensic outputs were modified. UI-6 was not started.
