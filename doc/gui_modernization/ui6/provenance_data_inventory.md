# Provenance and report source inventory (before implementation)

Reviewed session/presentation/report contracts, UI-2 design/workspace architecture, UI-3 data mapping, UI-4 artifact contracts, UI-5 navigation and the mandatory test-quality reports. Current source is authoritative.

| Field | Backend / persisted source | Recorded value and trust | Existing UI | UI-6 presentation |
|---|---|---|---|---|
| Source identity / profile | UI-1 session/invocation; historical import identity | Path/hash/profile are identity, not origin authentication | Overview | Copyable identity and revision header |
| EXIF, IPTC, XMP, PNG/container fields | ExifTool payload raw_watchlist_hits; summary metadata_signals[].evidence | Original raw_key/group/tag/value; selected watchlist, not all extracted tags | Summary narrative | Namespace filter, search, selected exact value |
| Software/workflow/prompt/declaration | Existing metadata signals and their evidence | Existing signal summary; declaration remains unverified | Narrative/Reasoning | Recorded interpretation beside original field; no software-name classification |
| C2PA/JUMBF presence | C2PA_PRESENT signal/watchlist bucket | Presence only; no cryptographic verification exists here | Provenance summary | Explicit unsupported cryptographic verification |
| Missing / ambiguous provenance | trace.provenance_evidence.state and metadata section | Recorded neutral missing/ambiguous state | Summary labels | Availability distinct from declaration and verification |
| Extraction status/error | pipeline_status.stages assign_attr=exif_payload; extractor tool/version/time | Stage success/failure independent of metadata finding strength | Stage details | Extraction status and recorded reason |
| Raw-payload persistence | <run>/<stem>_exif_signals.json | Only trust under matching historical run identity and file SHA-256 | File only | Guarded asynchronous recovery; otherwise summary signal evidence only |
| OSINT sources and notes | Existing ReverseSearchResult/Match annotations | Analyst-entered URLs/title/source type/notes/first-seen estimate; not measured origin proof | Existing finding dialog/list | Same editors, current revision and copyable selected source detail |
| Research timestamps | started_at_utc/completed_at_utc/first_seen_estimate where recorded | No invented per-match timestamp | Stored annotation JSON | Recorded dates labeled as research time or analyst estimate |

ExifTool does not persist the full original record, only file/extractor properties, watchlist hits, signals, classifications and notes. The UI must not imply complete EXIF coverage. Summary-only legacy results can expose fewer fields. Binary objects are represented as descriptors rather than decoded ordinary text. Missing fields never imply successful verification.

| Existing report section / format | Source | Revision identity | Limitation / UI-6 action |
|---|---|---|---|
| final_summary.json | create_report_snapshot.payload_json | Session/result/analysis/annotation identity in investigation | Authoritative structured preview/export source |
| final_summary.html / .txt | Same payload full_html/full_text plus existing generator footer | Same report snapshot | Render exact existing content; no template/forensic narrative rewrite |
| Current OSINT appendix | annotation_appendix | Current annotation revision, separate from analysis-time annotations | Preserve frozen findings and contextual separation |
| Reasoning JSON/text | Same payload reasoning_trace | Same result; existing partial-trace text fallback | Keep detailed records in bundle; default human preview remains narrative |
| Artifact references | Existing sections.artifacts/overlay_paths | Frozen result | No new image embedding or unsupported registration claims |
| current_report.json | Existing immutable-generation publisher | Atomic pointer and revision guard | Reuse existing publication; explicit background exports use distinct request directories |

Supported formats are JSON, HTML and TXT. There is no PDF exporter, new provenance validator, watermark detector or general report-template framework in scope.
