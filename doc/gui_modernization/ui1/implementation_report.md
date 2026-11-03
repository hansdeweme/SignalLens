# UI-1 implementation report

## Baseline and preserved work

Branch main, HEAD `00c5eb2ea179470fcde7f4bf25a704feaa8b28fd`. Inherited: modified `doc/SignalLens - Modernizing the Forensic Reasoning Engine.docx`; untracked UI-0 task Markdown, UI-1 task Markdown, doc/gui_modernization audit artifacts and Word lock file. Baseline tracked hashes/status are in baseline.json. No inherited modifications were overwritten. No stage, commit, push, merge, tag, reset or stash was performed.

UI-0's component/journey/visual/reasoning/architecture/design/roadmap documents were reviewed against actual GUI, settings, OSINT, worker, controller, summary and persistence code. The UI-1 task narrows the earlier roadmap: theme tokens, shell/sidebar and dashboard work are deferred. This implementation intentionally addresses integrity and contracts only.

## Changed production files

|File|Change|
|---|---|
|investigation_session.py (new)|InvestigationState, frozen AnalysisInvocation, controlled InvestigationSession, snapshot serialization, source identity, lifecycle/result/annotation/report revisions.|
|presentation_models.py (new)|Frozen summary, hypothesis, evidence, provenance, stage and investigation snapshot contracts.|
|investigation_presenters.py (new)|Pure build_presentation adapter for dataclasses/persisted mappings; unknown-safe recorded field projection.|
|investigation_workers.py (new)|InvocationWorker QObject bridge and InvestigationWorkers registry; named queued GUI-thread slots and both-terminal-path retirement.|
|investigation_reports.py (new)|ReportSnapshot, annotation appendix/restoration, current/stale checks, versioned bundle publication and non-destructive load_investigation.|
|signallens_gui.py|Session ownership and snapshot signals; selection/Clear/reanalysis invalidation; guarded status/log/success/error; launch context/settings/OSINT snapshots; source checks; annotation draft commits; current report generation/retry; stored-summary File action; deferred close and archive deletion guard. Existing widgets/theme/navigation remain.|
|analysis_worker.py|Optional copied settings_snapshot passed to controller; original signals/positional constructor API retained.|
|signallens_controller.py|Optional copied settings snapshot supplies the existing patch/subject-background profile dictionaries. Original getter behavior remains when absent. No detector arguments/defaults, thresholds, score computation, hypotheses or confidence rules changed.|
|summary_persistence.py|Supports frozen report dictionaries alongside existing dataclass inputs for text/HTML/generator fields; existing output names/format retained.|
|.gitignore|Scoped UI-1 generated reference and pytest-workspace exclusions. test_images and existing output exclusions retained.|

New tests: tests/test_investigation_contracts.py and tests/test_investigation_gui.py. Existing tests were not modified. Documentation/utilities are confined to doc/gui_modernization/ui1/. integrate_gui.py records the one-time method integration, not a production dependency. run_tests.py is the sandbox-compatible test harness; verify_references.py produces local ignored forensic outputs and reviewable comparison JSON.

## Architectural decisions and deviations

- No second forensic engine: initial synthesis still calls build_summary_result, using frozen invocation inputs; post-analysis annotations only change a separately attributed appendix. Explicit rerun incorporates them into a new forensic result.
- Serialized compact summaries/annotations provide detached reads; raw detector state is a single retained reference. No image arrays enter presentation contracts.
- Named QObject relays ensure widget callbacks execute on the GUI thread; identity is attached by the handle, not guessed from mutable worker fields. Superseded workers are retained with isolated output paths.
- No physical cancellation or unsafe termination. Standard close is deferred and nonblocking until every owned worker retires. Hanging backends can delay close indefinitely; external forced quit/logout are unsupported.
- Reports use immutable generation folders and an atomic pointer rather than overwriting several current files in place. This adds directory nesting while preserving existing formats/serializers and prior forensic outputs. Failures remain explicit and retryable.
- Imports create explicit local identities and retain original metadata; no destructive migration or invented old revisions. Full raw detector state is not reconstructed from a summary.
- Reentrant selection during snapshot delivery is guarded; archive deletion is disabled while physical workers exist. Source hashes prevent a file overwritten at the same path from being accepted as the original input.

## Remaining limits

No UI-2 features, theme changes, source/detector viewer, Evidence Explorer, probability gauges, new dependencies or packaging rebuild. Optional full lineage sidecars remain optional; missing lineage/reliability/provenance data stays unknown. The old Decision Trace remains a selected-field view, with escaped display values. Current native offscreen Qt tests verify functionality/lifecycle; this task did not perform a new manual native-window/DPI audit. Synchronous summary/report generation remains on the GUI thread. Earlier archive configured-root inconsistencies are not generalized into an archive redesign, although deleting artifacts during worker execution is now blocked. Generation cleanup and a historical-investigations browser remain future work.
