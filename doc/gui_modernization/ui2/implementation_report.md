# UI-2 implementation report

## Baseline

Branch main, HEAD `00c5eb2ea179470fcde7f4bf25a704feaa8b28fd`. Starting tests: **378 passed in 3.93s**. UI-1 was implemented but uncommitted. Inherited tracked changes were .gitignore, analysis_worker.py, signallens_controller.py, signallens_gui.py, summary_persistence.py and the reasoning-engine DOCX. Inherited untracked work included investigation/presentation modules, two UI-1 test files, UI-0/UI-1 documentation/artifacts, task Markdown files and the Word lock file. Entry status and content hashes are recorded in inherited_baseline.json.

No critical UI-1 defect blocked shell integration. Guarded worker ownership, frozen launch inputs, non-destructive imports, annotation/report revisions and pure presentation contracts were verified by the starting suite and retained. No detector, scoring, confidence, provenance interpretation or lineage logic was changed.

## UI-2 files

New production modules: gui_design_system.py, gui_components.py, gui_workspace.py and gui_workspace_state.py. New tests: tests/test_workspace_shell.py. Modified existing production files: signallens_gui.py (QMainWindow shell/retained-widget integration and display-only rich-text styling), settings_dialog.py (theme plus scroll wrappers), osint_dialogs.py (theme), and .gitignore (local GUI preferences/validation output exclusions). UI-1's worker/controller/session/presenter/report modules and original test files are unchanged from entry.

The combined working-tree Git diff naturally includes inherited UI-1 changes. UI-2's specific change list above, inherited_baseline.json and final validation.json distinguish these phases. No inherited file was replaced with an earlier Git version. No staging, commit, push, merge, tag, reset or stash occurred.

## Architecture and behavior

SignalLensGui becomes QMainWindow while retaining its class name, widget attributes and UI-1 methods. WorkspaceShell provides a persistent command row, lifecycle/status, six destinations, resizable panels and initial read-only content. Exactly one Configure dialog contains the original profile/context controls. Exactly one OSINT group remains, now on Provenance. Existing summary, log, trace, archive, Help and report actions remain connected to their original handlers.

Shell snapshots are checked against session, invocation, result, analysis revision, annotation revision and lifecycle. Tests cover obsolete results and same-session superseded analyzing snapshots. Navigation does not mutate forensic data or trigger work. Confidence comes from existing presentation fields; provenance verification and availability remain separate. SourcePreview is fit-only, downsampled for display, and reset by identity; it adds no detector interpretation or coordinate overlay.

Central tokens, root-local palette/QSS and reusable components provide the visual system. Existing rich text is themed only at display time; frozen summaries and exported reports are unchanged. Native file dialogs and modal workflows are retained. QSettings saves only geometry/maximized state, splitter sizes and destination, separately from forensic settings. Restore validates visible screen placement and handles malformed preferences.

## Diagnostic and validation

The bounded score diagnostic found a real subject_based-versus-normal profile mismatch and historical numerical-allocation snapshots. The current reasoning function reproduces 20.47705 / 5.4 from the recorded subject_based measurements; current normal-profile references remain 21.32705 / 6.675. All prepared-image RGB pixels match across historical/UI-1 outputs; coverage counts are unchanged. Exact historical raw-container hashes/commit are not recorded, so they are not invented. See score_baseline_diagnostic.md.

Final suite: **406 passed in 7.53s, 0 failures/errors/skips**, including 28 UI-2 cases. Both full reference analyses match UI-1's measured scores, hypotheses, confidence, evidence details and source hashes. Native Windows validation and 18 actual captures are documented in visual_validation.md. See regression_results.xml and reference_verification.json for machine-readable evidence.

## Scope and remaining limitations

No UI-3 complete dashboard, advanced image viewer/comparison, evidence filters/models, reasoning graph, new provenance verification or redesigned report content. Existing artifact files are accessible externally; complete detector viewers remain later work. The Overview context may scroll at the minimum size; this is deliberate transitional content. No new dependency or image asset was introduced.

Dark-first only; a light token palette is injectable but not exposed/certified. Native primary-monitor rendering was checked; other DPI settings, screen readers and packaging remain unverified. Portable GUI preferences use the app directory, so read-only installed locations may not persist them. UI-1 logical cancellation and potentially delayed closure for a stuck backend remain unchanged. Existing archive configured-root issues are not expanded into an archive redesign here.

UI-3 can begin on the existing immutable contracts and shell. There is no identified blocker, but it should retain these ownership guards, clarify compact Overview scrolling, and treat image coordinate registration as explicit future work rather than assuming the thumbnail supplies it.
