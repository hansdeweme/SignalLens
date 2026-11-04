# SignalLens development requirements

Before adding or changing tests, read [TEST_DISCIPLINE.md](doc/test_quality/TEST_DISCIPLINE.md)
and consult [the behavioral coverage matrix](doc/test_quality/behavioral_coverage_matrix.md).

- Search existing tests for the invariant first. Reuse authoritative coverage and simple fixtures.
- Each new test group must identify a previously unprotected behavior or failure mode.
- Keep common session, worker, scorecard and navigation guarantees in their authoritative tests;
  workspace tests should cover their distinct integration behavior.
- Use targeted tests while developing; run the complete suite as the final acceptance gate.
  Repeat full runs only for a stated risk, failure or subsequent change.
- Report baseline collection, added/consolidated/removed cases, final collection, net change,
  newly protected behaviors and existing coverage reused.
- A net increase above **10 collected cases per future GUI phase** requires explicit justification
  in the final report. This is a review threshold, not a cap or a reason to combine unrelated cases.
- Preserve unrelated work and forensic production behavior. Test count is not a quality target.
