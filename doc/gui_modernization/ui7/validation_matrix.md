# UI-7 validation matrix

PASS means fresh evidence for the stated scope. Native and DPI columns apply only to visibly inspected states. NOT TESTED is not a failure. All DPI rows retain an untested 125% condition; no whole-product DPI certification is claimed.

| Area | Functional | Native Windows | DPI | Performance | Accessibility | Status |
|---|---|---|---|---|---|---|
| Overview | PASS | PASS | PASS: inspected 100/150; 125 NOT TESTED | PASS | PASS: names/state/navigation; speech NOT TESTED | PASS within scope |
| Image Forensics | PASS | PASS | PASS: inspected 100/150; 125 NOT TESTED | PASS | PASS: zoom/comparison names; exhaustive keyboard NOT TESTED | PASS within scope |
| Evidence | PASS | PASS | PASS: inspected 150; complete 100/125 grid NOT TESTED | PASS | PASS: Ctrl+3/focus/detail; speech NOT TESTED | PASS within scope |
| Reasoning | PASS | PASS | PASS: inspected 150; complete 100/125 grid NOT TESTED | PASS | PASS: Ctrl+4/focus/detail; speech NOT TESTED | PASS within scope |
| Provenance metadata / OSINT | PASS | PASS | PASS: inspected 150; complete 100/125 grid NOT TESTED | PASS | PASS: textual trust/state; speech NOT TESTED | PASS within scope |
| Reports preview / export | PASS | PASS | PASS: inspected 100/150; 125 NOT TESTED | PASS with synchronous-save limit | PASS: Ctrl+6/focus/state; speech NOT TESTED | PASS within scope |
| Configuration | PASS | PASS | PASS: native 100; complete 125/150 grid NOT TESTED | NOT APPLICABLE | PASS: modal cancellation | PASS within scope |
| Settings | PASS | PASS | PASS: native 150; complete 100/125 grid NOT TESTED | NOT APPLICABLE | PASS: modal cancellation | PASS within scope |
| OSINT Finding editor | PASS | PASS | PASS: native 150; complete 100/125 grid NOT TESTED | NOT APPLICABLE | PASS: focus/cancel; speech NOT TESTED | PASS within scope |
| Image / stored file chooser | PASS | PASS | PASS: native 100; complete 125/150 grid NOT TESTED | PASS | PASS: path input and Open | PASS within scope |
| Progress and completed analysis | PASS | PASS | PASS: native 100; complete 125/150 grid NOT TESTED | PASS | PASS: textual status | PASS within scope |
| Failure / warnings / recovery | PASS automated | NOT TESTED complete manual journey | NOT TESTED | PASS controlled 81 MP failure | PASS textual errors automated; speech NOT TESTED | PASS automated |
| Session replacement | PASS automated | NOT TESTED complete manual journey | NOT TESTED | PASS switching fixture | NOT TESTED complete keyboard journey | PASS automated |
| Ordinary reanalysis | PASS | PASS packaged native | PASS: inspected 100; complete 125/150 grid NOT TESTED | PASS one packaged run | PASS Ctrl navigation and textual state within scope | PASS; overlap stress automated |
| Shutdown during worker | PASS automated | NOT TESTED during real analysis | NOT APPLICABLE | PASS automated | NOT APPLICABLE | PASS automated |
| Packaged application | PASS stored load/export and 23-stage reanalysis | PASS idle launch/close and all workspaces | PASS inspected 100; complete package grid NOT TESTED | PASS one pipeline; cold startup NOT TESTED instrumented | PASS exercised navigation/state; speech NOT TESTED | PASS within portable smoke scope |

Fresh artifacts: `regression_results.json/xml`, `reference_validation.json`, native environment/manifest, performance before/after JSON. Matrix limits are release conditions, not implicit product defects. Final verdict is in `release_readiness.md`.
