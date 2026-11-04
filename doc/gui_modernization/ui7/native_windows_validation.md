# UI-7 native Windows validation

Native validation **was performed**, with Qt platform `windows`, Python 3.13.13, PyQt 6.10.2, Qt 6.10.0. `native_validation.py` launches the normal SignalLensGui with an isolated output root and QSettings. It does not set a scale override or offscreen platform. Visible interaction used the Computer Use plugin (`@oai/sky`). The launcher adds only an F8 QA screenshot action. It does not change detectors or result handling.

Initial client geometry was 1280 x 900. Startup through QApplication/window construction and show was 0.427 seconds on the final launch, excluding Python imports; it is not a cold-process-to-first-paint benchmark. See `native_environment.json`.

| Condition / operation | Result | Evidence / limits |
|---|---|---|
| Actual 100% DELL U2412M | PASS | DPR 1.0, logical DPI 96, 1920 x 1200 desktop. Startup, source choice, configuration, real progress/completion, stored load, report export and artifact viewing. |
| Actual 150% second display | PASS for inspected states | DPR 1.5, 1707 x 1067 logical desktop. Windows move-to-monitor shortcut used; manifest records 1.5 after migration. Registered overlay, Evidence, Reasoning, metadata, OSINT, Reports, Overview, Settings and OSINT editor inspected. |
| 125% | NOT TESTED | No actual display at that scale; Windows settings were not changed. Environment-variable simulation is not claimed. |
| Maximize / restore | PASS | Native maximized client 1707 x 996, then restored 1281 x 902 at DPR 1.5. |
| Exhaustive native minimum resizing | NOT TESTED | A corner-drag attempt did not establish a changed client size. Automated minimum-layout tests pass, but are separate evidence. |
| Mouse / keyboard navigation | PASS for exercised controls | Sidebar/commands, Ctrl+1..6, comparison popup and Overlay, chooser Open, modal Escape cancellation. |
| Modal focus | PASS for exercised dialogs | Configuration, Settings, OSINT Finding; settled controls visible and Escape returns focus without saving drafts/settings. |
| Shutdown | PASS idle / automated active worker | First native process exited code 0; fresh regression protects active-worker shutdown. Final native close recorded in validation notes. |

`native_capture_manifest.json` identifies native QWidget captures with logical dimensions, DPR and maximize state; these are real windows, not offscreen renders. `native_02_Overview.png` is an earlier native progress capture from the first launch; the final launcher manifest restarted numbering, so it is retained separately as a progress artifact. Other screenshot names in that manifest correspond to the final launch. Computer Use transient modal screenshots were visually inspected but not all saved as standalone files.

Limits: full manual replacement/failure recovery and overlapping-reanalysis stress, minimum geometry across all dialogs, screen-reader speech and 125% remain open. Ordinary reanalysis was subsequently verified in the final native portable package, all 23 stages successful; see packaging_validation.md. The full native grid must not be inferred from a subset of successful native checks.
