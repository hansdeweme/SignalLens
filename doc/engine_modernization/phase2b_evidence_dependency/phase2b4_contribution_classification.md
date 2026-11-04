# Phase 2B.4 numerical contribution classification

## Baseline readiness and review boundary

Branch `fix/scorecard-integrity-phase2a`, HEAD `f64f2262126da2a539813415f2bf49685f392571`.
Initial suite: **297 passed, 0 failed, 0 skipped**. Six inherited tracked files
were modified: decision logic, hypothesis engine, hypothesis evidence, reasoning
persistence, signal language and summary synthesis. Phase 2A, lineage/shadow,
production corroboration and confidence-policy modules, tests and documents were
untracked. The exact entry inventory, 169-file byte snapshot and hashes are in
ignored `analyzed/phase2b4_validation/`. No staging or Git history operation is
needed. A phase-only patch against that snapshot will isolate this work.

Reviewed the acceptance audit, Phase 2B.1 audit/graph and both CSV inventories,
lineage schema, shadow implementation/activation criteria, production gate audit
and remaining limitations, and their source implementations. The earlier
activation criteria prohibit adopting experimental scoring; this task authorizes
only structurally demonstrated duplicate-credit corrections. No experimental
weights, family budgets or calibrated marginal fractions are activated.

## Classification before implementation

Categories apply to contribution relationships, not entire detector names.
Identical ancestry alone is insufficient to assign category B.

| Contribution | Shared source | Relationship | Evidence of redundancy or added information | Proposed action |
| --- | --- | --- | --- | --- |
| Same summary instance entered under multiple section keys | Identical `ModuleSummary` object | A | `compute_base_scores` iterates dictionary values without identity checking; the same observation can be added repeatedly (its domain already uses set semantics) | Credit once; prefer its registered key, then lexical key; no content-equality deduplication of separate observations |
| Fragmented-boundary **base** plus cross-convergence base/domain | Identical ELA/residual overlap | B | `classify_boundary_convergence` fragment fallback tests supportive component labels and the same overlap count/ratios. Unlike the preceding contour branch, it requires no positive contour/topology property. The adapter assigns weak suspicious weight solely from this fallback label | When a suspicious partial/strong cross summary already represents that overlap, withhold the fragment base and its extra domain; keep the boundary observation and mechanism-specific interpretation |
| Fragment local-support 0.5 and fragment/cross edit 0.5 | Same overlap fallback already represented by cross | B | These guards require only the redundant fragment flag and, for the latter, cross itself. Neither measures positive contour/localization information | Withhold both when the fragment base is demonstrably redundant; existing 0.18 conversion consumes corrected support; retain observations/routes |
| Contour-boundary base plus cross base | Same overlap, with connected-cluster contour measurement | C | `find_connected_clusters` and `score_contour_shape` add extent, elongation and fill information; the strong branch requires `is_contour_like` | Retain existing weights and domain, disclose common ancestry |
| Boundary focus plus cross/boundary | Same ELA/residual maps and selected masks | C | `_extract_ela_map`, `_extract_noise_map` and regional intensity comparisons measure anomaly localization relative to masks | Retain; no blanket composite removal |
| Segmentation alignment plus cross | Filtered hotspot mask and selected boundary band | C | Spatial alignment fraction against selected geometry is additional measured information | Retain under existing availability/reliability policy |
| Patch spatial plus patch similarity | Retained matches and mask geometry | C | Endpoint region densities and topology classify location; no new matching is claimed | Retain existing base and spatial clone-support rule |
| Regional/global FFT | Overlapping pixels and shared FFT helper | C | Regional detector reruns transforms on masked crops, rather than recopying global result | Retain |
| Texture, asymmetry and material measurements | Shared gradient/residual/DCT definitions; optional texture/region-FFT carry-forward | D | Separate samples/statistics and comparative gaps exist; quantifiable conditional redundancy is not established, including carry-forward's effect on final status | Retain provisionally, explicitly unresolved |
| Sensor versus CFA | Shared high-pass scale/phase family | D | Luminance and chroma/directional maps differ | Retain provisionally |
| Compression versus residual/boundary | Same pixels/processing history | D | JPEG grid-energy measurements differ from recompression/residual maps | Retain provisionally |
| Other base weights plus single-signal mechanism terms and local-support conversion | Same signal, different explicitly specified scoring roles | D | Existing formulas explicitly prescribe these terms; local support is converted once and is never separately added to final suspicious score | Preserve formulas outside the confirmed fragment restatement; their combined empirical strength remains unresolved, rather than relabeling them as independent measurements |
| Boundary-stack, alignment/cross, material/cross, material/asymmetry, intrinsic-boundary interactions | Related measurements | C | Explicit existing compound predicates encode contour/location/measurement agreement | Preserve coefficients and conjunctions; compounds are not independence claims |
| Clone candidate, similarity, separation, coverage and localization | Same retained matches | C | Existing rules test different quantitative properties; clone support routes decisions and is not also summed into suspicious score | Preserve |
| Camera benign base, convergence, attenuation, cautions, local/clone moderation | Same acquisition observations | D | Intentional multi-role policy, not duplicate addition of camera support into the suspicious aggregate | Preserve, disclose empirical uncertainty |
| Metadata base/provenance boost and OSINT/context combination | Assertions that may share an originating declaration | D | Existing mutually exclusive provenance branches specify these roles; no authenticated claim identity is available across metadata and OSINT | Preserve; never claim verified or independent corroboration |
| Repeated metadata IDs/narratives/overlays | Same section observation | D | Reporting does not itself add score; both prompt/declaration IDs produce one metadata base | No numerical change |
| Domain bonus for preserved C/D findings | Existing credited domains | D | Domain is a scoring category, not an independence count; incremental value is uncalibrated | Retain 0.25 coefficient; remove only domains whose entire numerical base was proven duplicate |

The two reference images do not establish empirical independence or calibration.
An unknown future pattern or equal-valued separate summary is not silently
declared a restatement. Omitted parent summaries remain a provisional legacy
summary contract, not invented measurements. Explicitly unavailable evidence
cannot itself earn a base credit.
