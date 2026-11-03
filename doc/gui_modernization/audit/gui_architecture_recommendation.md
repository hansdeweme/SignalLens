# UI-0: recommended architecture

Choose **Option B: workspace modernization**. Preserve PyQt6, the Qt-free controller, worker bridge, detector outputs, SummaryResult, policy/scorecard semantics and existing serializers. Introduce a coherent shell and structured result views behind a read-only presentation boundary.

|Option|UX improvement|Complexity / regression risk|Architecture / maintenance|Migration and compatibility|
|---|---|---|---|---|
|A: incremental refinement|Medium: clearer report, colors, spacing; image/evidence workflow still fragmented|Low–Medium / Low for styling; higher if patched lifecycle remains implicit|Existing QWidget monolith and duplicated fields persist; recurring growth burden|Easy with current callbacks, useful preparatory quick wins; cannot solve core image-centered task alone|
|B: workspace modernization|High: source/detector comparison, hypothesis/evidence navigation, visible limits|High overall, bounded by phases / Medium with stable result adapter and snapshot tests|Reusable panels and model/view reduce duplication; moderate ongoing maintenance|Retain controller/worker and narrative fallback during migration; enable pages incrementally without changing reasoning|
|C: full GUI rebuild|Potentially High, uncertain beyond B|Very High / High: all workflows revalidated at once|Can clean ownership, but discards working forms and requires replacement behavior|OSINT, settings, archive, reports, failure states and packaging all migrate together; no demonstrated need for framework replacement|

## Proposed ownership

`QMainWindow` owns menus, toolbars and status. A compact left navigation selects a `QStackedWidget`: Overview, Image Forensics, Evidence, Reasoning, Provenance, Reports. A central QSplitter divides source/analysis viewing from findings; use a second splitter inside image comparison. Prefer fixed predictable regions initially; optional QDockWidget for execution log/technical inspector only after core behavior is stable. Docking every card would make default layouts difficult to maintain.

A session coordinator owns input configuration, an immutable request/run ID, lifecycle (empty / selected / running / completed / partial / failed), paths and result snapshot. It starts the existing worker and associates completion with its run ID. While running, destructive/replacing session actions are disabled or explicitly managed. Close/error cleanup must join the same documented lifecycle. Cooperative cancellation requires a controller/worker protocol and is **not** a theme feature; do not promise it in UI-1.

A read-only presentation adapter exposes SummaryResult plus trace, stage statuses and validated artifact descriptors. It translates labels and missing values, not forensic meaning. Evidence models (`QAbstractTableModel` + QTableView / proxy filtering) reference authoritative hypothesis evidence_details by stable ID; the same evidence can have different roles for different hypotheses. QTreeView suits route/policy hierarchies and available production ancestry. Never count rows as independent corroboration or create a new scoring model.

GUI currently invokes summary synthesis on its thread. First centralize that existing call and its inputs into one application-level operation; subsequently move expensive invocation off the GUI thread only with deterministic serialization/ownership checks. Preserve exact output tiers, hypotheses, explanations and scorecard values. OSINT changes create a visible new revision using that same operation; Reports must export the revision displayed. Keep analyst additions distinct from measured detector data.

## Image architecture and data boundaries

Use QGraphicsView/QGraphicsScene/QGraphicsPixmapItem for fit, zoom and pan; Qt supplies transforms, fitInView and rendering ([Qt QGraphicsView](https://doc.qt.io/qt-6/qgraphicsview.html)). Decode lazily, cache bounded display rasters, keep full-resolution coordinates separate from viewport/DPI. Never resample or overwrite source evidence files. QSplitter supplies panel resizing; QMainWindow saveState/restoreState supports native dock/toolbar state ([Qt QMainWindow](https://doc.qt.io/qt-6/qmainwindow.html)). Store window geometry, page and splitter state with versioned QSettings; keep forensic settings JSON separate. No new plotting dependency is required: display existing FFT radial plots/spectra as images first.

Artifact descriptors reference existing payload paths, role, input image, dimensions and transforms. Many ModuleSummary.artifacts entries already exist, but ELA/noise/masks require raw payload paths. Resolve relative/legacy paths explicitly and show unavailable-file states. This adapter is a presentation catalog of existing outputs, not a competing evidence model.

|Feasibility boundary|Examples|
|---|---|
|Presentation-only from existing data|Source view; named artifact picker; standalone fit/zoom/pan; report/trace search; hypothesis-scoped role table; current policy rationale, stage list and corroboration explanations|
|Conditional on validated existing geometry|Linked cursors/pan across prepared scales; patch-pair selection; mask outline; regional crop-to-source mapping. Disable link when transform absent. Show FFT spectra separately.|
|Requires new backend/result contract|New detector heatmaps, arbitrary ROI reanalysis, cryptographic provenance validation, cooperative cancellation, universal recorded lineage sidecar where not emitted, statistically calibrated probabilities. Not included in B's presentation scope.|

## Compatibility and migration gates

Keep SettingsDialog and OSINTFindingDialog initially, refining sizing/labels. Retain readable narrative and raw exports as fallbacks; every detector and archive command remains reachable. Snapshot old/new views against the same SummaryResult; display adapter tests must check missing/partial/invalid inputs and preserve exact policy fields. Native Qt styling should use palettes/QSS tokens and supported rich-text CSS; do not copy browser CSS variables/media queries into QTextEdit. Do not add WebEngine, QML, Fluent libraries or a chart framework merely to achieve a modern surface.

Structural bug fixes (thread lifetime, stale actions, report revision persistence, configured archive path) should be reviewed as explicit changes with focused tests before new navigation depends on them. This audit performs none of those fixes.
