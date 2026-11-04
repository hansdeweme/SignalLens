# UI-7 performance baseline

Repeatable local measurements use `performance_validation.py` with offscreen Qt, explicitly loaded Windows Segoe UI/Consolas fonts, a 10 ms GUI heartbeat and Windows process working-set counters. These are application timings, not native input-latency or cold-process benchmarks. Python imports precede the startup timer. The controlled comparison runs use identical fonts/inputs: `--eager-baseline` reconstructs the pre-fix Reports render function without editing production files; `--after` uses the current implementation. Both ran without a concurrent build. Earlier actual pre-change measurements are retained as `performance_initial_before.json`; their unconfigured offscreen fonts were unsuitable for visual inspection, so reference screenshots were recaptured with fonts and timing comparisons repeated under matched conditions. Intermediate build-loaded/profile runs support attribution only. Single-run differences are descriptive, not statistical claims.

| Operation / workload | Before seconds | After seconds | After largest heartbeat gap seconds |
|---|---:|---:|---:|
| QApplication/window startup after imports | 0.144 | 0.140 | not separately measured |
| Typical saved Instagram load and preview readiness | 0.112 | 0.110 | 0.034 |
| Workspace navigation | 0.000–0.011 | 0.000–0.013 | at most 0.007 |
| Artifact switch and decode readiness | 0.011 | 0.012 | 0.010 |
| 30 MP PNG bounded source preview | 0.091 | 0.102 | 0.020 |
| 81 MP PNG controlled preview failure | 0.055 | 0.055 | 0.035 |
| Large trace plus 2,048,000-character narrative binding | 0.572 | 0.415 | 0.379 |
| Evidence filter: 2,500 rows | 0.010 | 0.005 | below heartbeat resolution |
| Reasoning route detail: 1,000 routes | 0.033 | 0.006 | below heartbeat resolution |
| Metadata bind: 5,000 fields | 0.044 | 0.017 | 0.017 |
| Metadata filter | 0.005 | 0.003 | 0.002 |
| Legacy automatic report synchronization | 0.186 | 0.157 | 0.156 |
| Explicit captured background export | 0.126 | 0.105 | 0.061 |
| Ten new investigation selections | 0.085 | 0.067 | 0.062 |

Large data is an explicit synthetic performance fixture, not a forensic result or a calibrated interpretation. The 30 MP image decodes successfully to a bounded preview. The 81 MP PNG returns `Preview unavailable: Unable to read image data`, zero decoded dimensions and no application crash. The exact decoder failure cause was not established; image format/allocation limits remain a documented limit, not a successful large-image preview claim. There is no detector run for these generated images.

Working set after final startup was 219.98 MiB, after typical load 234.92 MiB, after large bind 316.89 MiB, before switching 352.03 MiB and after ten replacements/settling 262.55 MiB. Eager baseline post-switch was 260.14 MiB. This short run shows cleanup of large transient content, not proof against a long-session leak. There is no multi-hour soak, slow/network disk or exhaustive image-format benchmark.

Profiling attributed substantial main-thread time to eager Qt HTML layout of a hidden Reports page. Matched-font comparison reduced large bind from 0.572 to 0.415 seconds, and largest GUI heartbeat gap from 0.533 to 0.379 seconds. It remains a moderate one-time delay for this deliberately large fixture. The visible Reports page still performs required layout; no claim is made that all rendering is asynchronous.

Automatic save decision: retain the existing synchronous publisher. It took 0.157 seconds in the controlled after run (initial unconfigured-font after run 0.219 seconds), with a similar GUI pause. The measured change does not demonstrate a serious freeze that warrants a new publication state machine or ordering risk. Explicit export already runs off the GUI thread (verified by authoritative regression), with a 0.061-second maximum heartbeat gap here. Revisit automatic publication if actual supported workloads or slower storage show a significant freeze; this is an open bounded performance limitation.
