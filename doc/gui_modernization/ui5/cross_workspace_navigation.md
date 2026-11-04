# Cross-workspace navigation

WorkspaceShell.navigate_context accepts a destination and ExplorerIdentity plus optional hypothesis, evidence, role, artifact, detector and reasoning-tab IDs. It compares the key to the current session/invocation/result/revision/status, rejects closing windows and rejects requests whose explorer snapshot is no longer current. No request runs analysis or mutates a result.

Overview's existing Evidence/Reasoning actions target the recorded primary hypothesis; hypothesis cards target their own hypothesis. Their layout and findings are unchanged. Existing limitations/coverage/narrative access remains available.

UI-4's Evidence/Reasoning buttons use only the selected artifact's explicit evidence and hypothesis IDs. An artifact without these references states that an association is unavailable; the GUI does not select an unrelated evidence item based on its filename. Catalog completion notifies the shell to rebuild explicit links, without re-running detectors or changing the UI-4 comparison design.

Evidence can open a selected associated UI-4 artifact, the scoped assessment, confidence explanation or detector's contribution row. Reasoning can open a selected explicit evidence reference, its associated visualization or Provenance. Canonical `evidence:<section>` references from gates are resolved through recorded detail.section/lineage mappings to existing scoped evidence, never by parsing hypothesis evidence IDs.

Missing targets clear the relevant evidence/artifact detail and report unavailable. Missing hypotheses clear scoped assessments/confidence. Selection is preserved for annotation-only refreshes and catalog updates where possible; new investigations reset it. Evidence Back history is bounded to 64 scoped keys and cleared on identity changes. Source and artifact image loading still belongs to UI-4 and its existing monotonic request guards.
