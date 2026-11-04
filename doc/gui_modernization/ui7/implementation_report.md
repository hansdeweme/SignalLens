# UI-7 implementation report

Baseline verified on `main`, HEAD `fb66d7025e73818b164d7be29aaff9f96bb68ef3` (UI-6 ready). UI-5/UI-6/rationalization work was already committed at the start of this phase. Python 3.13.13, PyQt 6.10.2, Qt 6.10.0; 514 freshly collected tests. `baseline.json` records the initial tracked/untracked state. Inaccessible tracked files under old audit pytest directories appeared deleted and were preserved. The UI-7 task was untracked. A Word temporary lock file changed during the session; it was not edited by this work.

The application uses `signallens_gui.py:main` / `SignalLensGui`; the documented Windows build is `run_pyinstaller.cmd`, with an existing `SignalLens.spec`. Packaging retains the existing windowed onedir workflow and installed dependencies. The script still names a machine-specific installed MediaPipe DLL; portability of that build prerequisite is documented rather than redesigned.

Production corrections are narrow:

- `report_workspace.py`: defer expensive document layout while Reports is hidden, render the current presentation on show, and clear obsolete preview contents. Snapshot creation, report bytes, revision checks and background export ownership remain unchanged.
- `run_pyinstaller.cmd`: replace the nonexistent old project path for ExifTool dependency copy with paths relative to the build script. Include dynamically imported installed SciPy NumPy compatibility submodules after a native packaged-startup failure demonstrated the missing import.
- `SignalLens.spec`: apply the same SciPy collection correction for the existing spec entry point.
- `signallens_gui.py`: frozen portable startup anchors the working directory to the executable directory. Frozen startup exceptions retain their original traceback through the windowed bootloader instead of invoking a nonexistent console input stream.

Two focused regressions protect hidden preview layout and portable frozen bootstrap. The coverage matrix records their distinct ownership. Final complete gate: 516 passes, no failures/skips/warnings; net +2, no cases consolidated or removed. A 515-pass gate preceded the packaged runtime failures. The subsequent production bootstrap correction justified one repeated full gate after the final application/test source change, as well as a package rebuild/native launch. There were no unchanged repeated full baseline runs.

QA additions under this directory establish reproducible native capture, synthetic/saved-result timing, reference snapshot/export checks and isolated build validation. `.gitignore` excludes generated images, local settings, compiled bundles, forensic output and exported reports under `validation_output/`. Deliberate screenshot/JSON/XML/Markdown diagnostics remain reviewable.

Native Windows execution covered actual 100% and 150% displays and one full real Instagram analysis. Both saved normal references were freshly verified without repeated detectors. Reports, limits and final package outcome are documented in the companion validation files. No UI feature, redesign, dependency upgrade, forensic detector, score coefficient, hypothesis selection, confidence rule, lineage/provenance semantics or report producer was changed.

No stage, commit, push, merge, reset, stash or tag operation was performed. Generated packages are local validation artifacts only; nothing was published or distributed. Release verdict and outstanding conditions are in `release_readiness.md`.
