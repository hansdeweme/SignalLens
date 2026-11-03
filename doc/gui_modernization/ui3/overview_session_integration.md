# Overview session integration

`SignalLensGui` retains sole ownership of InvestigationSession, worker invocations, frozen synthesis and revisioned reports. `WorkspaceShell.bind_snapshot` still rejects mismatching session, invocation, result, analysis revision, annotation revision or lifecycle **before** updating Overview or any other workspace. Overview receives only that accepted immutable snapshot. It has no result cache, analysis controller or recomputation path.

| Transition | Overview response |
|---|---|
| New empty session | Clear image, tier, evidence and hypotheses; explain selection |
| Source selected/reselected | New identity; display matching preview; no completed findings |
| Analysis starts/restarts | Captured profile shown; prior finding/evidence cleared; existing indeterminate progress and guarded execution status retained |
| Matching completion | Recorded primary/pattern/tier and all available structured views appear together |
| Obsolete completion/failure/status | Existing UI-1 invocation guard rejects; no dashboard mutation |
| Cancelled/superseded | Explicit abandoned lifecycle; no completed interpretation |
| Analysis failure | Recorded error/recovery guidance; no forensic conclusion |
| Annotation edit | Existing revision advances; frozen forensic JSON remains unchanged; narrative appendix/reports synchronize through UI-1 |
| Stored-summary import | Fresh local identity; historical profile/hash/path retained where recorded; absent structured fields remain unavailable |
| Source disappears/changes | Viewer clears changed pixels, explicitly warns; historical finding remains tied to recorded hash |
| Delayed image completion | Serial + path + session/invocation/hash request mismatch rejects delivery; stat recheck rejects changes before delivery |

Modeless narrative content follows the same current summary widget even if the active investigation changes while it is open. Evidence/scope/source detail dialogs are modal, preventing selection underneath a historical detail view. Navigation routes to the existing shell, never starts analysis or publishes a report. Actions retain keyboard focus and explain disabled states. Viewer jobs are independent of report and analysis worker lifetimes.
