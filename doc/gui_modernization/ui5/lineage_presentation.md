# Lineage presentation and limits

Three sources are distinguished:

1. Persisted `evidence_dependency_analysis.lineage` provides diagnostic run direct dependencies, optional dependencies, family, kind, status and measurement ancestry where present.
2. Production `scorecard_calculation.numerical_deduplication.contributions[].measurement_ancestry` provides recorded allocation ancestry, but not direct dependency edges.
3. The immutable current `evidence_lineage.REGISTRY` provides schema-only required/optional parent relationships, family and kind. These are explicitly labeled as current schema, not reconstructed historical run facts. The GUI never invokes build_lineage or dependency diagnostics to manufacture missing run records.

A hypothesis observation maps to a section-level lineage node only through its explicit detail.section or lineage_reference. Prefixes in evidence IDs are never parsed to infer relationships. Unknown nodes in persisted allocation records retain their ancestry without fabricated parents.

The direct-neighborhood table includes the selected node, required/optional parents, direct descendants and nodes with shared **recorded** measurement ancestry. No recursive graph traversal occurs, so cycles and missing intermediate nodes cannot hang the GUI. Double-click follows a node only when a real evidence item under the current hypothesis maps to it. Otherwise it remains an intermediate/unlisted node with an explicit message.

Shared computational ancestry does not prove statistical redundancy or statistical independence. Numerical duplicate suppression comes only from the recorded allocation classification, suppressed amount and reason. Registry overlap or shared IDs do not cause GUI deductions, discounts or independence scores. Current production references do not serialize the full optional shadow graph; their ancestry and schema boundaries remain visible in the source labels.
