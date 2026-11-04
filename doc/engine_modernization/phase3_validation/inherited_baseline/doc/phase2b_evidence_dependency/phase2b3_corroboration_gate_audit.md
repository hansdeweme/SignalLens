# Phase 2B.3 production corroboration gate audit

## Inventory boundary and classification

Inspected **20 gate groups** across `decision_logic.py`, `hypothesis_engine.py`,
`hypothesis_evidence.py`, `signal_language.py` and narrative/trace consumers.
Groups collect related predicates and their route consumers; this is not a count
of every Python `if` or every ledger operation. The existing Phase 2B.1 operation
inventory remains the exhaustive numerical lineage reference.

- **A:** a multiplicity/source-diversity requirement: one observation must not
  satisfy it by being relabeled as several detector outputs.
- **B:** accumulation/moderation, without a defined independent-source requirement.
- **C:** a mechanism-specific compound observation, where related measurements
  and added localization can legitimately be required together.

**One source-diversity predicate was corrected; 19 other groups retain their
production conditions and numerical policy.** The confidence group's single-
indicator fallback also now excludes inactive/non-supporting observations,
consistent with Phase 2A availability. No new weight, score threshold, family
budget or confidence tier was introduced.

## Complete gate inventory

| # / function or group | Type / hypothesis | Inputs and existing condition | Shared ancestry / risk | Action and expected effect |
| --- | --- | --- | --- | --- |
| 1. `determine_confidence` generic High path | A diversity predicate; general anomaly | Material score >=0.58, strong asymmetry, strong boundary, strong cross; originally count >=2 and S>=3 | Boundary and cross reuse ELA/residual; texture/asymmetry can also share measured inputs. Counting module flags can inflate multiplicity | Corrected to >=2 eligible measurement-disjoint indicator witnesses, keeping S>=3. Unknown/incomplete sources cannot satisfy it. Medium S>=2 / one valid indicator and Low S>=1.2 thresholds remain |
| 2. `_boundary_corroborated` | C; localized editing | >=2 suspicious medium/strong boundary/focus/intrinsic subject-boundary/alignment summaries; max boundary-specific strength >=0.45 | Boundary/focus/alignment reuse maps or masks; localization/contour comparisons add mechanism information | Preserve compound predicate. Audit shared ancestry and label it compound agreement, not independent-source proof. No new source requirement imposed |
| 3. `determine_dominant_pattern`: local compound | C; localized editing | `(boundary_strong or segmentation_strong) and cross_strong` | Cross/contour/alignment related | Preserve pattern conjunction; preliminary pattern is not an independent measurement count |
| 4. `determine_dominant_pattern`: structure/subject compounds | C; synthetic structure | FFT + patch, or material + asymmetry | Frequency/recurrence overlap; subject metrics can share helpers or optional payloads | Preserve. Does not directly establish statistical independence or a calibrated generation probability |
| 5. `route_localized_multi_mechanism` | C; localized editing | Local and clone support >=3, difference <1, no context risk | Clone recurrence and local processing can use shared supporting checks | Preserve distinct mechanism interpretations. A new independent-family threshold would change policy |
| 6. `route_synthetic_multi_signal`: structure alternatives | C; synthetic origin | Synthetic boost >=1, S>=5, support flag, `(FFT and patch) or (strong material and strong asymmetry and reliable geometry)` with existing caveat | Related interpretation may still add information; different feature definitions do not prove independence | Preserve all route conditions; instrument FFT/patch and material/asymmetry predicates separately |
| 7. `ScoreCard.synthetic_supported_by_other_domains` | B; synthetic origin | OR of metadata declaration, AI-gallery context, strong material | Material can already be part of a compound; metadata/OSINT can describe same assertion | Preserve flag and its consumer. Name is not proof of a distinct/independent family. Further requirement would need separately defined semantics/validation |
| 8. Provenance / context routes | B; synthetic/camera context | `route_provenance` generation/enhancement/OSINT branches; `route_real_photo_context_prior` camera metadata + supplied smartphone context, boost <=0.25 | Assertions/context can co-occur and are not authenticated measurements | Preserve declaration categories and context routing; remove ambiguous “independently of” selection wording only |
| 9. Camera convergence / damping | B; acquisition moderation | Measured camera support >=2 adds 0.5; piecewise damping/cautions, local tempering and clone damping | Sensor/CFA share phase/residual families; metadata is a separate assertion family | Preserve every numerical term. Dependence-aware numerical changes are prohibited here |
| 10. `compute_base_scores`: domain diversity | B; separate S/B accumulation | 0.25 per additional weighted domain | Composite domain labels may reward shared ancestors | Preserve coefficients and aggregation. Domain identifiers are not promoted to independent-source counts |
| 11. `compute_scorecard`: local/edit synergies | C; localized processing | Boundary stack with cross/FFT, alignment/cross, material/cross, material/asymmetry and subject-boundary combinations | Parent reuse is intentional compound weighting but empirically uncalibrated | Preserve all 2A operations; no new coefficients or silent suppression |
| 12. Clone/spatial recurrence support | C; localized reuse | Candidate/quality/coverage/separation, supportive or inconclusive spatial interpretation, camera/natural repetition controls | Spatial analysis consumes original retained pairs | Preserve localization value and clone routing. It is not a second independent matching observation |
| 13. FFT/patch synthetic boost | C; synthetic structure | Existing joint spectral/pair-metric thresholds and context factors | Similar regularity may appear in several measurements | Preserve numerical/pattern conjunction. Independence is unestablished |
| 14. Sensor/CFA/compression corroboration boosts | C; localized processing | Inconsistency plus cross/local/boundary patterns | Residual and processing features overlap | Preserve boosts; this is numerical compound policy, not a separate source-diversity gate |
| 15. Local and subject-boundary routes | C; localized editing | Strong/moderated local thresholds use group 2; standalone `route_subject_boundary` / `route_boundary_transition` require existing boundary/cross/patch conditions | Contour/ring/localization comparisons related | Preserve route conditions and fixed tiers. Generic diversity does not replace a valid compound mechanism |
| 16. Clone ambiguity / structured recurrence caution | C; localized/synthetic ambiguity | Clone ambiguity/score, material override, natural/geometry/smartphone context, FFT+patch and weak local signals | Shared patches and material/context moderators | Preserve predicates. Branches inheriting generic confidence can reflect group 1; no other tier changed |
| 17. `route_camera_like`, `_photo_like_clean_signals` | B; camera compatibility | Camera support, no adverse declaration, weak local signals, low S; clean/absent pattern conjunctions | Absence/compatibility is not authentication or independent verification | Preserve existing acquisition interpretation and caveats; availability already handled by snapshot logic |
| 18. General anomaly / moderate / fallback routes | B; unresolved anomaly | `route_multi_signal_suspicious` S>=7 plus named support/no camera/context; moderate S>=3.5; fallback uses generic confidence | Aggregate and OR flags do not prove source independence | Predicates/fixed High anomaly tier unchanged. Generic inherited tier can change through group 1 only |
| 19. Geometry / boundary support safeguards | C reliability controls | Region unreliable, person-mask support/reliability, boundary r thresholds | Shared spatial support, not new forensic evidence | Preserve masks, coefficients, safeguard priority and scope |
| 20. Hypothesis selection, evidence roles, rationale | B scope/presentation | Candidate specificity/priority, declaration versus visual/local mechanisms; roles by section/pattern | Repeated reporting does not add numerical evidence; list length is not an independence measure | Preserve selection architecture and roles; narrow wording corrections only; negative independence/probability caveats retained |

## Why group 1 is a justified narrow correction

The generic High path explicitly distinguishes **two strong indicators** from
the Medium path's **one strong indicator**, separately from the numerical score.
Its multiplicity check is therefore formalized as structural source diversity,
not simply a second accumulation of already scored module flags. The old code
had no formal definition of independence; this change does not retroactively
claim that its outputs were statistically independent. It defines and audits
the narrow existing “more than one” purpose without selecting a new threshold.

The minimum remains two, and all score/tier boundaries remain exactly the same.
Only eligibility to satisfy multiplicity changes. A candidate witness must have
known, valid, hypothesis-appropriate, complete non-control measurement ancestry.
Two selected witnesses must not share a measurement extraction ID. The helper
does not infer statistical independence from this property.

A maximum disjoint subset is used rather than naive connected components. For
primary A, primary B and composite AB, A+B can still provide two sources; adding
AB neither creates a third source nor merges A and B into a single source.
Primary A plus descendants A or AB cannot automatically manufacture multiple
disjoint witnesses. Added localization/relationships remain in the result as
incremental findings, without invented numeric credit.

Sharing a broad family or feature-code group is **not** automatic identity.
Material and asymmetry may have distinct extracted statistics while sharing
feature definitions; the helper reports that limitation. Optional distinct-family
requirements are explicit API semantics, not enabled universally or added to
the production generic confidence gate.

## Compound versus independent-source semantics

Group 2's use of the word “corroborated” is spatial/mechanism agreement, not a
pre-existing requirement for independent source families. Replacing its count
with a universal distinct-family rule would destroy meaningful compound
conditions and violate the task's type-C boundary. It is left unchanged and
explicitly audited as compound.

Older summary-only callers can provide valid compound summaries without the
raw parent summaries. Such outputs remain eligible for the existing compound
predicate, with provisional-parent limitations. They cannot supply a distinct
measurement witness to group 1. No missing upstream measurement is invented.

The “other domains” flag is an unresolved naming/weighting concern. Existing
tests and route structure deliberately support material/asymmetry compounds
without mandatory metadata. Requiring a new third-family observation would be a
new model rule. This phase records the flag as accumulation and does not silently
introduce that requirement.

## Runtime coverage

The additive `corroboration_audit` records the evaluated generic diversity gate,
boundary compound gate when requested by a qualifying route, the two synthetic
compound alternatives, and the synthetic support OR flag. Existing
`decision_route_trace` retains full route candidate pass/fail/selection outcomes.
Numerical and presentation groups are documented here rather than duplicating
the entire score ledger or lineage graph in every gate result. A lower-level
condition passing does not mean its complete route qualifies.
