# Contextual OSINT integration

The existing build_osint_group, OSINTFindingDialog and add/edit/delete/review/provider handlers remain single-owned by SignalLensGui. UI-6 relocates those controls into the contextual tab and adds a committed annotation-revision label plus a copyable selected-source view. At minimum window size, the research section scrolls instead of compressing its button grid or source list.

Source attribution preserves provider, page/image URLs, title, notes, analyst-entered source classification and first-seen estimate. Research start/completion timestamps are shown only when recorded. Per-match timestamps are not invented. Existing general analyst_notes are readable; supported finding notes remain editable through the existing dialog. Provider buttons continue the existing browser workflow; UI-6 does not perform automated reverse-search research or contact sources.

Edits still make a draft copy, use Save/Cancel, check the originating session, stage annotation persistence and advance the revision only on a committed change. Cancelled edits, session switches, no-ops and failed saves retain the existing UI-1 guarantees and tests. Global save/error feedback remains in the status bar; the contextual panel shows the committed revision. No parallel annotation database is added.

The frozen session.summary_json is not synthesized after an edit. Existing update_summary appends current context separately, and the Reports projection refreshes to the new annotation revision. The original analysis-time context remains in the report investigation record. Current OSINT is an analyst/external-source record, not a new detector measurement or confidence upgrade. The new view and the export preserve this distinction.
