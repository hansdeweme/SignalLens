# Legacy summary migration

Overview now presents structured primary hypothesis, dominant pattern, exact tier, three independent hypothesis assessments, capped role-specific evidence and coverage/limitations. These values were already recorded by the engine and exposed through UI-1; no legacy prose was parsed into new findings.

The existing `host.summary_box` QTextEdit now lives in an owned **Full investigation narrative** dialog, reached by **Open full investigation narrative** below Overview's limitations. The dialog is modeless and uses the same single widget and `update_summary` path. Complete original narrative, detector sections, narrative qualifiers and current annotation appendix remain available, selectable and scrollable. GUI theme projection does not alter frozen HTML or report contents.

Choose/Configure/Run/Clear, execution log, menus, Settings, OSINT dialogs, Decision Trace, detector artifact folder, JSON export and stored-summary import retain their established ownership and actions. Reasoning's existing text view additionally includes the recorded limitations and policy-rule name so Overview's reasoning link exposes complete card details. No workspace outside Overview was redesigned.

Legacy summaries without reasoning show explicit missing structured fields and retain narrative access. Source files may be unavailable; a stored narrative is not grounds to fabricate an image or infer a missing hash. Reports continue using the same immutable forensic content and separately revisioned current annotations.

UI-4 can add advanced artifact comparison. Evidence Explorer, fuller reasoning visualization, provenance tooling and Reports redesign remain later phases. The bounded source preview is not an artifact-alignment or pixel-measurement contract.
