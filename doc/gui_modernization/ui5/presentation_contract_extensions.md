# Compatible presentation extensions

New frozen Qt-free contracts in explorer_models.py leave all UI-1 dataclass constructors unchanged. ExplorerIdentity binds session ID, analysis ID, result ID, analysis revision and lifecycle status. Annotation revisions do not change the forensic identity.

| Contract | Source / meaning |
|---|---|
| EvidenceDetailView | Scoped ID/role, evidence_details observation and interpretation, explicit detector section, reliability/status/limitations, immutable technical fields and explicit artifact IDs |
| LineageNodeView | Persisted diagnostic graph, production numerical ancestry or explicitly labeled current registry schema; no reconstructed run edges |
| AuditRecordView | Stable source record/order ID, title, hypothesis, recorded outcome/explanation, immutable field pairs and explicit evidence references |
| ScoreContributionView | Existing raw/credited/reliability/final-adjusted/suppressed allocation fields as exact strings; absent fields stay None |
| ExplorerSnapshot | Identity, tuples of all projections, original raw-trace string, primary finding, coverage and schema-availability issues |

`build_explorer` consumes the active immutable UI-1 snapshot and detached session.summary_data, plus immutable UI-4 catalog descriptors. Mutable backend objects are never retained. Nested technical data is serialized into immutable strings and decoded only for selected-row text formatting. The original JSON remains available separately. Construction is deterministic; repeated evidence within one hypothesis/role scope does not produce extra rows. No route is ranked and no evidence role is inferred.

Malformed top-level containers and missing hypothesis IDs are reported where detected. Wrong-type labels/reliability fields are treated as unavailable instead of becoming arbitrary filter categories. Legacy raw narrative remains accessible independently. Existing evidence_details/reasoning_details shell aliases retain hidden read-only compatibility projections for earlier consumers/tests; the visible explorers use the new contracts.
