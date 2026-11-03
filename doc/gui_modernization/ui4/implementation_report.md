# UI-4 implementation report

Baseline: main at 1ce194a647e20f75f8a64983fe92399c0834d8d9, origin/main +0/-0 according to local tracking (no fetch). The recorded baseline suite had 432 passing tests. The inherited tree was dirty: the renamed UI-3 task, UI-4 task/draft modules, source-viewer edits, and inaccessible tracked audit fixtures reported as deleted. These were preserved. See baseline.json for the original record.

New modules: artifact_models.py (frozen contracts), artifact_presenter.py (scoped discovery and identity checks), forensic_image_viewer.py (native coordinate scenes on UI-3 previews), image_forensics_workspace.py (catalog, side-by-side, linked views, guarded overlays and metadata). gui_workspace.py replaces the placeholder and binds snapshots. gui_workspace_state.py persists splitters. source_image_viewer.py adds lifecycle/view signals and handles expired Qt pools. gui_design_system.py extends existing theme tokens to the new tree and horizontal scrollbars. .gitignore excludes local UI-4 validation workspaces and capture preferences.

Production detector algorithms, scoring, confidence policy, hypothesis selection, evidence lineage and report formats were not edited. No UI-5 work was started. The full suite has 468 passing tests, including 36 UI-4 cases. During validation, a native overlay-item lifetime crash and a Windows source-file deletion race were found and corrected.

Reopened actual UI-3 production reference runs cover all 19 catalog producers: Instagram has 41 entries (7 A, 25 B, 3 C, 6 D); Midjourney has 33 (7 A, 13 B, 3 C, 1 D, 9 E). Counts include structured/shared references, not independent forensic evidence. UNKNOWN B entries are candidates for independent inspection; they are not demonstrated transforms. Three Instagram B masks have demonstrated transforms. Registration and exact dimensions are recorded in reference_validation.json. The original patterns and confidence tiers remain unchanged.

Validation captures are offscreen Qt on Windows at 1280Ã—900 and 1040Ã—720. Native desktop/DPI checks remain outstanding; this report does not claim full native acceptance. UI-5 can consume the artifact/evidence IDs and session keys, but row-level deep linking and relationships absent from current evidence metadata still require explicit backend contracts. Full-resolution tiled inspection, arbitrary crop registration, mask compositing and transform support for compound detector outputs remain deferred.

Nothing was staged, committed, pushed, merged, tagged, reset or stashed. Existing test images and detector artifacts were preserved. The only new forensic-facing persistence is the optional UI-only sidecar for new live sessions.

