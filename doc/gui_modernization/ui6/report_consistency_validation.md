# Preview/export consistency validation

The new UI-6 tests target additional boundaries rather than replaying generic session/worker coverage:

| Scenario | Evidence |
|---|---|
| Preview equals actual output | test_preview_export_bytes_share_snapshot_and_legacy_text_fallback writes through the existing publisher and compares HTML/TXT/JSON bytes with ReportPresentation; legacy literal text remains escaped |
| Export uses the captured snapshot off the GUI thread | test_background_export_uses_captured_snapshot_off_gui_thread records thread identity and snapshot equality, then compares saved JSON payload |
| Annotation changes invalidate the previous snapshot | Existing annotation tests remain authoritative; test_obsolete_preview_and_late_export_cannot_become_current rejects the old presentation before dispatch and rejects a late completion after clearing |
| Export errors do not appear saved | test_background_export_failure_never_reports_saved injects a write failure and checks explicit error status and empty success paths |
| Current research is visible at the right revision | test_osint_workspace_displays_committed_source_and_revision reuses the existing commit path and checks the new source/revision detail while the frozen summary stays equal |
| Stale annotation navigation is rejected | test_provenance_navigation_checks_annotation_revision_and_recorded_field_link checks the new revision-bearing target and explicit field association |

Existing investigation_contracts and investigation_gui tests continue to own atomic report publication, failed run-bundle retry, cancelled/switched annotation dialogs, annotation-save failure, reanalysis, source replacement and worker ownership. They were not recreated or weakened.

capture_validation.py reopens both saved normal-profile production references, verifies source hashes, applies one controlled annotation edit to the imported local session, checks revision advancement and exact frozen summary equality, and exports into new validation directories. It compares preview HTML/TXT and structured JSON to the actual saved bundle. Original report-pointer hashes remain unchanged. reference_validation.json records the output pointers and outcomes. The temporary stale/failure screenshots are explicitly labeled UI fixtures; original baseline artifacts are not altered.
