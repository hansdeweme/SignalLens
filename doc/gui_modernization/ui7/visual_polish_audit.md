# UI-7 visual polish audit

Visible native review covered startup, selected source/progress/completion, stored Reports preview/export, Image Forensics with registered ELA overlay, Evidence, Reasoning, Provenance metadata/OSINT, configuration, OSINT Finding and Settings. Actual monitor migration from 100% to 150% retained image/artifact layout and usable commands. Native maximization was captured at 1707 x 996 logical pixels, DPR 1.5. Fresh offscreen captures of both reference cases cover all six workspaces at 1280 x 900; these are explicitly named `_offscreen.png`.

Hierarchy, dark surfaces, type roles, spacing, state text, focus borders and selected-row treatment remain consistent with the existing design system. Long technical values truncate in table cells with scrollable/copyable detail. A registered ELA image can overlay the source; registration/reliability labels remain visible and unsupported geometry is still gated by the authoritative tests. No restyling, new features or forensic wording changes were justified by this inspection.

The measured polish correction is deferred layout of a hidden Reports HTML document. Its snapshot/presentation remains current and exports remain available; the text document renders when Reports is shown. This removes unnecessary work during another workspace's result update. No evidence or report content changes.

Remaining limits: 125% was not available without changing Windows configuration. Native exhaustive minimum-size checks across every tab and actual screen-reader output remain open. Immediate desktop screenshots during Windows modal/window animation sometimes show transitional blank or ghosted content; settled observations and native QWidget captures were used for assessment. No clipping defect was inferred solely from a transitional capture.

Low wording issue retained in the defect register: an imported session's Overview still prefixes `Stored result` after a new native reanalysis; current result/revision/report remain correct. This marker can confuse historical source ancestry with result age. No redesign or evidence/source contract change was made to conceal that limitation.
