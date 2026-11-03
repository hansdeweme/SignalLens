# UI-0: reasoning visibility and conclusion audit

## Actual contract

`summary_synthesizer.build_summary_result` constructs module sections, passes coverage to `decision_logic.synthesize_overall`, and renders the returned SummaryResult. `decision_logic._build_reasoning_trace` is the canonical trace producer. `finish_decision` appends hypothesis evidence and limitations, confidence rationale, and separate hypothesis summaries to overall_text. Therefore these concepts are **not absent** merely because the GUI has no dedicated cards. `narrative_builder` shows overall_text followed by each section's name and note; it does not iterate arbitrary section.details or artifacts.

|Capability|Available in backend / exact contract|Visible in GUI and location|Problem|Recommended presentation|
|---|---|---|---|---|
|Synthetic origin|Yes: hypothesis_assessments[synthetic_origin], primary_hypothesis|Present but difficult: overall prose includes ID, confidence, explanation|Raw ID; scope easily lost while scrolling|Separate assessment row with authoritative tier, explanation and limitations|
|Localized editing|Yes: hypothesis_assessments[localized_editing]|Present but difficult: same prose|Can coexist with synthetic declaration; no parallel comparison|Separate row, explicitly avoid equating edit support with generation|
|Camera-acquisition compatibility|Yes: hypothesis_assessments[camera_acquisition]|Present but terminology is technical: same prose and detector notes|Benign/green can imply authenticity; metadata not authenticated|Camera-compatible evidence, with qualification next to tier|
|Primary selection|decision.primary_hypothesis / selection_reason|Indirect prose; dialog only branch/pattern/tier/polarity|No primary-hypothesis field or selection reason in dialog|Prominent finding title and expandable selection explanation|
|Supporting evidence|assessment.supporting_evidence + evidence_details; decision projection|Clearly labeled in narrative, hard to navigate at length|No stable row selection, filter or jump|Hypothesis-scoped evidence table; preserve evidence IDs|
|Contradicting evidence|assessment.contradicting_evidence|Narrative when nonempty|Empty role omitted, can look like overlooked review|Explicit “none recorded” vs missing data; never create a contrary finding|
|Moderating evidence|assessment.moderating_evidence|Narrative when nonempty; not all role headings styled consistently|Moderating differs from contradiction|Separate role label and interpretation column|
|Contextual evidence|assessment.contextual_evidence; context and contextual_priors|Narrative plus scene-context note; trace dialog shows priors|Analyst assertion and measured observation can appear adjacent without provenance|Show source type and applied context snapshot|
|Reliability|scorecard_calculation.reliability_adjustments, assessment limitations, mask diagnostics|Selected derived numbers in trace; limitations in prose|Reliability is not uniformly a detector percentage|Named reliability state, backend explanation and applicable scope; no synthesized universal rating|
|Coverage|AnalysisState.stage_statuses/analysis_coverage; trace.pipeline_status; policy inputs|Unavailable module notes and confidence limitations; full stage counts not rendered|No overview of failed/skipped/unavailable stages|Coverage list with reason, dependencies and run state|
|Provenance declaration|metadata details; trace.provenance_evidence.state|Metadata note and hypothesis explanations explicitly say unverified|Correct caveat can be below fold|Pinned provenance state; raw tag/value and source signal|
|Authenticated provenance|Enum exists, but classifier always returns provenance_verified=False and trace metadata_authenticity_verified=False|No implemented validator or verified-result screen|A possible enum must not be marketed as an available validator|“Not verified” today; verified state reserved for a future validated backend contract|
|Corroboration|trace.corroboration_audit.evaluated_gates: kind, ancestry groups, shared ancestry, eligibility, explanation|Detailed production gates only in exported trace; summary has narrative qualifications|Related indicators may be mistaken for independent votes|Gate list, compound vs distinct-source label, shared ancestry explanation|
|Numerical scores|trace.scorecard and scorecard_calculation, numerical_deduplication in current source|11 selected scorecard scalars in dialog; full ledger only exports|Heuristic quantities have no universal probability semantics|Technical ledger with contributions/transforms and non-probability label|
|Confidence tier|overall_confidence; assessment.confidence_tier; confidence_policy.assessments[].tier|Clearly labeled at top, also per-hypothesis prose|Color tied to suspicious/benign polarity; primary scope not prominent|Text tier attached to hypothesis; neutral badge and policy link|
|Confidence-policy decisions|confidence_policy.assessments[].policy_rule / rationale / reliability_limitations|Rule identifiers and rationale in prose; full policy objects absent from dialog|Rules are identifiers, not navigable explanations|Show already-computed rationale and rule ID with input facts|
|Evidence lineage|evidence_lineage registry/build_lineage; production gate ancestry; scorecard numerical source/component allocation|Only exported gate/ledger fields, no dedicated GUI lineage view|Full dependency shadow is opt-in, not universally in ordinary GUI traces|Show available production ancestry; “not recorded” for absent edges; optional diagnostic sidecar clearly labeled|
|Unavailable detector results|run_stage statuses; summary adapter override to not_run/neutral/score=None|Explicit unavailable notes where stage status maps to section; generic Not run yet otherwise|A note is not a complete pipeline status display; no-data vs no-anomaly still takes reading|Separate run state from finding strength; missing score displayed as —|
|Candidate findings/routes|decision_route_trace contains evaluated candidates/selection information|Route Evaluation table in Decision Trace|Legacy six-column projection omits newer route metadata|Tree/table using available fields; no recomputation or inferred rejection reasons|

Full optional dependency analysis is enabled only by `evidence_dependency_shadow=True`; GUI update_summary does not set it. Do not claim every normal SummaryResult contains a complete serialized lineage graph. Production corroboration and numerical allocation already use lineage-aware safeguards. Showing existing ancestry is presentation work; emitting a new universal graph/snapshot is a separately reviewed backend contract extension.

## Primary conclusion: nine questions

|Question|Current answer quality|Evidence / needed improvement|
|---|---|---|
|What was found?|Good narrative, weak scan hierarchy|R: opening localized-processing paragraph is readable; raw dominant pattern appears first|
|Which hypothesis leads?|Partial immediate visibility|S: primary ID is in trace; GUI header shows pattern, prose includes assessments farther down|
|Confidence tier?|Immediate|R: High displayed explicitly; label should state which hypothesis|
|Why this tier?|Available after scrolling|S: build_confidence_rationale and policy rule text; structured rationale absent from dialog|
|Supporting evidence?|Available after scrolling|R: Supporting Signals section; many observations consume whole viewport|
|Contradictions/limits?|Present where supplied, not pinned|S: roles/limitations authoritative; no persistent limitations panel|
|Declared vs authenticated?|Accurate in metadata notes|S: explicit unverified declarations; no authentication path; expose this near overview|
|Unavailable detectors?|Partial|S: unavailable notes and policy limits; no run coverage panel|
|What is not established?|Present in qualified narrative/Help|S/R: local processing does not identify AI use; camera-like base does not authenticate history. Keep limits adjacent to finding|

The GUI is not currently a numeric AI-versus-real gauge. Preserve that restraint. No proposed authenticity percentage, probability gauge, binary red/green truth signal, frontend confidence calculation, independent hypothesis selection or threshold tuning belongs in this modernization.

## Validation evidence

Source mapping verified against `decision_logic.py` functions `_build_reasoning_trace`, `finish_decision`, `_apply_confidence_policy`, `evaluate_hypotheses`; `hypothesis_engine.HypothesisAssessment`; `hypothesis_evidence.evidence_presentation`; `metadata_evidence.classify_metadata_signals`; `summary_synthesizer.build_summary_result`; and GUI `update_summary` / `show_decision_trace_dialog`. Their exact source locations are in source_index.json.

The historical instagram summary contains all three assessments, confidence_policy, corroboration_audit, pipeline_status and provenance_evidence. It is used only to assess long-text rendering. Its stored ledger is older than current source and must not be treated as proof that all current numerical fields existed in that run.
