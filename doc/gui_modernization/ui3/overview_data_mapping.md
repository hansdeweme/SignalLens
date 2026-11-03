# Overview data mapping

All forensic fields flow through the immutable UI-1 projection. `SourceIdentityView` is the only new contract: frozen path/hash/profile/import marker/error values copied from the existing session. It is an optional final snapshot field for construction compatibility. No engine import or narrative parsing was added.

| Display field | Presentation contract | Backend source | Fallback behavior |
|---|---|---|---|
| Filename | summary.image_name | session.image_path basename | Investigation overview |
| Lifecycle | summary.status | session.state | Explicit lifecycle text; no completed finding |
| Result availability | result_id + summary.status | active session result identity | No completed result |
| Session/invocation/result IDs | snapshot identity fields | session/invocation | Missing IDs labeled not recorded in header tooltip |
| Captured profile | source.profile | invocation.profile; stored historical investigation.profile | Not captured yet / unavailable; never current combo-box value |
| Recorded path | source.path | session.image_path | Source unavailable; full path in identity dialog |
| Recorded SHA-256 | source.sha256 | session.source_sha256; stored report metadata/annotations imported by UI-1 | Identity unrecorded; no invented historical identity |
| Stored marker | source.stored | bool(session.imported_from) | No stored marker for live investigations |
| Failure explanation | source.error | session.error | Lifecycle-specific recovery instruction |
| Preview and encoded dimensions | viewer load result, not a forensic contract | QImageReader of the selected source, auto-oriented preview, encoded header dimensions | Explicit loading/unavailable/changed message |
| Primary hypothesis | summary.primary_hypothesis | reasoning_trace.decision.primary_hypothesis | Primary hypothesis not recorded; never choose one from scores |
| Dominant pattern | summary.primary_finding | reasoning_trace.decision.dominant_pattern | Not recorded |
| Primary confidence | summary.confidence_tier | matching confidence_policy assessment tier, then recorded decision tier | Unavailable, never inferred |
| Primary explanation | matching HypothesisView.finding | hypothesis_assessments[].explanation | Structured interpretation not recorded; narrative access |
| Qualifiers | summary.limitations | primary assessment + recorded policy reliability limitations | General support-tier explanation |
| Three hypothesis tiers/explanations | HypothesisView | corresponding recorded assessment/policy fields | Missing assessment or explanation explicitly unavailable |
| Hypothesis limitations | HypothesisView.limitations | assessment limitations + policy reliability_limitations | Not recorded; full entries in scope/Reasoning |
| Evidence role and identity | EvidenceView.role/hypothesis_id/evidence_id | assessment role lists, existing order | No observations recorded; not authenticity evidence |
| Evidence label/source/description | EvidenceView.label/source_detector/interpretation | evidence_details.label/section/interpretation | ID / source not recorded / interpretation not recorded |
| Reliability and lineage | EvidenceView.reliability/lineage_reference | directly recorded detail fields only | Not recorded; no detector-strength conversion |
| Provenance declaration | provenance.declaration_status | provenance_evidence.state | Not recorded |
| Verification | provenance.verification_status | metadata_authenticity_verified boolean | Unknown unless explicit True/False |
| Coverage | coverage_status | pipeline_status.coverage.status | Not recorded |
| Stage availability/reason | StageView | pipeline_status.stages status/reason | Retain unavailable/skipped/failed separately; unknown explicit |
| Full narrative | existing host.summary_box | frozen summary HTML + current revisioned annotation appendix | No completed narrative |

The first-two-per-role cap is a display budget, not evidence ranking. Repeated IDs across hypotheses remain distinct observations. No score, confidence, lineage, provenance or hypothesis selection is calculated by the dashboard.
