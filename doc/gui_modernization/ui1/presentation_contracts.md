# UI-1 presentation contracts

## Public boundary

`build_presentation(session, result=None)` in investigation_presenters.py accepts the active session's recorded summary, a persisted mapping, or the existing dataclass-style result. It constructs frozen dataclasses in presentation_models.py with tuples for nested collections. It imports no detector, scoring, hypothesis-selection or confidence-policy engine. It does not parse prose, rank routes, calculate scores/probabilities or infer verification/reliability. Results and the input session's forensic snapshot are unchanged.

|Contract|Field provenance and semantics|
|---|---|
|InvestigationSummaryView|session_id/image_name/status from session; primary_hypothesis and primary_finding from trace.decision; tier from authoritative matching confidence_policy assessment, falling back to recorded decision tier; limitations from recorded primary assessment/policy. No primary is selected if absent.|
|HypothesisView|hypothesis_id/explanation and all four evidence-role lists from hypothesis_assessments; exact tier/policy_rule/rationale from matching confidence_policy assessment, falling back to explicitly recorded assessment fields; limitations retain recorded reliability limitations. Backend order preserved.|
|EvidenceView|evidence_id plus hypothesis_id and role are the stable composite row identity. label, interpretation, source_detector (`evidence_details.section`), reliability and lineage_reference are copied only when recorded. An observation may occur in multiple hypotheses/roles; no global vote/deduplication is introduced.|
|ProvenanceView|declaration state from provenance_evidence.state; verification_status is verified only for boolean True, unverified only for boolean False, otherwise unknown. Description is the existing Metadata section note. No C2PA/tool-name reclassification occurs.|
|StageView|stage_id/status/reason/assign_attr from pipeline_status.stages. Failed, skipped, unavailable and success remain distinct. coverage_status is copied from pipeline_status.coverage.status.|
|InvestigationViewSnapshot|session ID, invocation ID or None, result ID, local analysis/annotation revisions, launch-time annotation revision, summary/hypotheses/evidence/provenance/stages and immutable annotations_json.|
|ReportSnapshot|frozen identity/result ID/annotation revision plus payload_json containing a detached report generation. Reports must reject snapshots whose identity/revision no longer matches the active completed session.|

Required IDs originate in session creation/analysis launch, never filenames. For a legacy import, a new local result/session identity is explicit; historical IDs remain source metadata rather than pretending that old revision numbers were recorded. `analysis_revision` counts completed runs in the local session, while imported content starts at local revision 1 without an invocation. `annotation_revision` counts committed local edits; no-op/cancelled/obsolete edits do not advance it. Historical annotation revisions remain discoverable in import metadata.

## Unknown, empty and unavailable

Optional scalar fields use None for absent/unrecorded data. A missing evidence-role list is None, distinct from a present empty tuple. Unknown evidence details retain their IDs/roles with other fields None. Missing reasoning yields empty hypothesis/evidence collections and unknown summary/provenance fields; narrative text is never reverse-engineered into a finding. No missing detector becomes negative/benign evidence. Coverage reasons and hypothesis limitations remain available independently of whether a visualization exists.

Full lineage is not invented. A directly recorded lineage_reference is preserved. Current production evidence details often omit that field; production ancestry/corroboration remains in the unchanged raw trace, and absent references stay None. This contract does not enable optional dependency-shadow analysis. Likewise no uniform reliability score is synthesized from detector strength or confidence.

## Future Qt views

The current GUI stores `view_snapshot` and emits `snapshot_changed(snapshot)`. `session_changed((session_id, state, analysis_id))` carries lifecycle identity. Both are emitted on the GUI thread. Future Overview/Evidence/Reasoning/Provenance/Reports views subscribe to these signals; delayed work must recheck session_id/result_id/revisions. Tables use `(hypothesis_id, role, evidence_id)` keys, not row numbers. Detector navigation can use recorded source_detector and evidence_id; unavailable artifact geometry does not authorize a fabricated overlay.

Widgets must not call build_summary_result to react to annotation edits or configuration toggles. Current GUI invokes the existing synthesis operation once after a matching worker finishes, using its launch snapshot. Reanalysis is the explicit way to obtain a new context-aware forensic result. Reports and current narrative share that frozen forensic summary and a separately versioned current-annotation appendix.

No sidebar, new dashboard, image viewer, Qt table model or reasoning visualization is implemented here.
