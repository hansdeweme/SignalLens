# Cross-workspace navigation

Existing ExplorerIdentity checks still guard session ID, invocation ID, result ID, analysis revision and lifecycle status. UI-6 adds an optional annotation_revision argument to navigate_context for revision-sensitive Provenance/Reports actions. A stale annotation target is rejected before navigation. Generic Evidence navigation now preserves its existing selection unless an explicit hypothesis/evidence/role/detector target is supplied.

Overview's existing Provenance and Reports destinations remain available. Evidence adds a Provenance action scoped to the selected evidence ID. Reasoning's existing Provenance action passes the selected explicit evidence reference where one exists. Provenance fields obtain evidence links only when a recorded metadata observation has the same raw_key and original value. Source names, metadata wording and arbitrary software names never create a relationship.

Provenance can open related Evidence, Reasoning or Reports; Reports can return to Overview, Evidence or Provenance/contextual research. A missing requested field association reports unavailable instead of selecting an unrelated field. The `tab='OSINT'` route opens contextual research explicitly. Returning by generic navigation preserves existing metadata filters and evidence selection. Metadata worker completions additionally compare their full forensic key to the current snapshot; annotation-only edits update the research view without reloading metadata.

The optional annotation guard does not reinterpret UI-5 evidence navigation: forensic evidence remains bound to the analysis result, while current research/export targets can additionally require the annotation revision. No navigation action runs detectors, modifies a report or commits an annotation.
