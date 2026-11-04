# Reasoning source inventory (before implementation)

Reviewed the UI-0 visibility audit, UI-1 presentation/lifecycle contracts, UI-2 shell/design system, UI-3 data mapping, UI-4 contracts/integration, Phase 2A scorecard source, Phase 2B lineage schema and numerical-allocation audit, Phase 3 confidence implementation, and final acceptance reference records. Production source and actual UI-3 saved normal-profile traces are authoritative.

| Category | Backend source | Persisted source under summary JSON | UI-1 contract / gaps | Presentation |
|---|---|---|---|---|
| Hypotheses | decision_logic._build_reasoning_trace; authoritative HypothesisAssessment | reasoning_trace.hypothesis_assessments; decision | HypothesisView has roles, rationale, limitations; specificity may be absent | Scoped assessments; primary marked from decision only |
| Evidence | hypothesis_evidence.evidence_presentation | hypothesis_assessments[].evidence_details and role arrays | EvidenceView lacks observations, observed status/score and detail limitations | One row per hypothesis/role/evidence ID, observation separate from inference |
| Availability | detector section status; pipeline stages | sections; section_snapshot; pipeline_status | StageView; detector strength is not reliability | Preserve recorded status; unknown remains unknown |
| Lineage | evidence_lineage.REGISTRY; optional dependency shadow | optional evidence_dependency_analysis.lineage; numeric contributions.measurement_ancestry; corroboration_audit | lineage_reference rarely populated; full run graph often absent | Persisted ancestry and schema-only direct parents labeled separately; no build_lineage call |
| Scorecard | hypothesis_engine; scorecard_integrity | scorecard; scorecard_calculation | Not projected by existing UI-1 contracts | Raw/base/credited/reliability/final columns, operation ledger, aggregate transforms and recorded validation |
| Numerical deduplication | numerical_evidence allocation | scorecard_calculation.numerical_deduplication | Not projected | Classification, suppressed credit, adjustment stage and recorded reason; no scoring changes |
| Corroboration | production_corroboration / marginal_corroboration | corroboration_audit.evaluated_gates | Not projected | Ordered gates, requirement kind, passed state, witnesses, shared ancestry and explanation |
| Confidence | centralized confidence_policy | confidence_policy.assessments | HypothesisView already prioritizes final policy result | Exact final tier/rule, roles, limitations; no threshold application |
| Routes | decision_logic candidate evaluation | decision_route_trace in recorded order | Modal has older projection only | Selected/matched/disposition/reason and hypothesis; no inferred supersession |
| Provenance and coverage | metadata_evidence; controller coverage | provenance_evidence; pipeline_status | Existing ProvenanceView/StageView | Context links and recorded constraints; no verification changes |
| Artifacts | UI-4 scoped artifact presenter | UI-4 catalog with evidence_ids | ForensicArtifact already immutable | Join by explicit evidence ID; no detector-name guess |

Raw observations can be empty; scorecard evidence IDs (`evidence:<section>`) differ from hypothesis evidence IDs (`<section>:<pattern>`). Joins use the explicitly recorded detail.section, never string-prefix parsing. Unknown/malformed containers must remain explicit. No additional calculations are needed to populate the explorers. Optional lineage shadow output is diagnostic, not a production score replacement.
