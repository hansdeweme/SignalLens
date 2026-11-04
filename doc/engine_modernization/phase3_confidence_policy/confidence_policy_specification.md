# Phase 3 confidence semantics and policy specification

## Semantics established before implementation

Confidence describes the strength and reliability of support for a particular
forensic interpretation. It is not the probability that an image is AI-generated,
authentic or edited. An image can support camera-acquisition compatibility,
localized processing and unverified generation context simultaneously.

- **Strength:** existing structured mechanism/support values and observed statuses;
  this task does not change their coefficients.
- **Reliability:** applicable mask/geometry/measurement safeguards. A rejected
  person mask cannot justify a High person-boundary interpretation.
- **Specificity:** what the finding establishes (localized mechanism, visual
  structure, declaration, compatibility or unresolved anomaly).
- **Corroboration:** the existing typed production source-diversity or compound
  check. Shared descendants do not manufacture distinct-source support.
- **Contradiction:** a directly challenging observation in the assessed hypothesis
  and mechanism scope. It remains visible even when other mechanism evidence
  survives; it is not a universal numerical penalty.
- **Moderation:** contextual limits that do not directly disprove the hypothesis.
  Camera-compatible structure does not refute an unverified declaration.
- **Coverage:** missing evidence is neither support nor contradiction. It can
  prevent a rule from establishing a mechanism requiring that evidence.

## Consolidation boundary

Stages remain interpretation, hypothesis assessment, deterministic primary
selection, centralized confidence policy, then presentation. Confidence does not
select the primary hypothesis. Typed finding specificity replaces the old
selection dependence on provisional route tiers; candidate priorities and scope
safeguards remain unchanged.

Existing mechanism-specific rule meanings are retained. The policy consumes
structured assessments, typed findings, existing score/derived facts and
corroboration results. It does not interpret free-text narratives, route names,
unrecognized pattern strings or the provisional route tier as confidence input.

Unverified generation/enhancement declarations remain bounded at Medium; source
context alone remains Low. Genuine provenance verification requires a typed
upstream validator result with image binding, not a metadata boolean. The
production extractor has no such validator. Signature/claim authenticity alone
will not silently become proof of the pixel-generating process.

Strong reliable compound localized processing or spatial reuse can remain High
without transferring that confidence to synthetic origin. General anomaly
confidence uses the existing generic thresholds and Phase 2B.3 source-diversity
gate, so an accumulation route cannot bypass that gate by returning High.

No arbitrary global deduction for contradiction/moderation, new score threshold,
new coefficient, empirical family budget, probability estimate or shadow-scoring
activation is introduced. New numerical calibration questions remain unresolved.

## Authoritative interface

`AssessmentEvidence` freezes the existing scoped supporting, contradicting,
moderating and contextual evidence identifiers plus assessment limitations.
`ConfidenceFacts` freezes typed finding claims, existing numerical support,
provenance state, reliability, coverage and the existing corroboration results.
`ConfidencePolicyResult` returns hypothesis, tier, stable rule ID, the same
evidence roles, reliability limitations and policy rationale.

Neither the assessment's old tier, its route/branch name, its narrative nor the
route's provisional tier is an input. `confidence_policy_inputs.py` is a small
adapter over structured score/derived/gate objects; no detector is rerun and no
raw pixel/mask/prompt payload is copied into confidence facts.

## Precedence and existing rule equivalents

| Hypothesis / precedence | Policy rule family | Tier and rationale |
| --- | --- | --- |
| All: invalid scorecard | `integrity.invalid_scorecard` | Inconclusive; no confident output from invalid numerical state |
| Synthetic: qualifying visual compound, without recurrence caveat | `synthetic.visual_compound` | High using existing boost >=1 / S>=5 and approved global or reliable regional compound requirements |
| Synthetic: trusted assertion validation and image binding | `synthetic.verified_assertion` | Medium with authenticated-claim rationale; no new unsupported upgrade to pixel-origin proof |
| Synthetic: generation/enhancement declaration | `synthetic.unverified_generation_declaration`, `.unverified_enhancement_declaration` | Medium; authenticity remains unverified; enhancement does not establish whole-image generation |
| Synthetic: reviewed source context | `synthetic.source_context` | Low; source context is not image-history authentication |
| Synthetic: recurrence caveat | `synthetic.recurrence_ambiguity` | Medium confidence in a qualified ambiguity finding, not positive proof of generation |
| Synthetic: required geometry absent / no specific evidence | `synthetic.required_region_unavailable`, `.not_established` | Inconclusive; missing local evidence neither proves nor disproves generation |
| Localized: decisive spatial reuse | `localized.spatial_reuse` | High under existing clone >=3.5, dominance >=1 and camera <2 requirements; not a person-boundary claim |
| Localized: supplied photo context / existing boundary or geometry safeguard | `localized.photo_context_ambiguity`, `.boundary_support_limited`, `.geometry_limited`, `.person_boundary_unavailable` | Existing qualified Medium findings; scope limited to the affected mechanism |
| Localized: required person geometry or boundary support missing | `localized.required_geometry_cap`, `.boundary_support_limited` | A person-boundary interpretation cannot be High without required reliable geometry; existing boundary threshold 0.6 applies even if a caller omits safeguard routes |
| Localized: multiple mechanisms / decisive boundary compound | `localized.multiple_mechanisms`, `.reliable_boundary_compound` | Existing High requirements: support thresholds, camera/context restrictions and typed compound support |
| Localized: unconfirmed strong local concern | `localized.camera_moderated_uncertainty`, `.unspecific_local_processing` | Existing Low with camera moderation, otherwise Medium unspecific local processing |
| Localized: supported boundary / weak mechanism | `localized.supported_boundary`, `.limited_mechanism` | Existing Medium / Low, respectively |
| Localized: ambiguous reuse | `localized.reuse_camera_ambiguity`, `.reuse_ambiguity.generic.*`, `.reuse_unspecific` | Existing Low camera ambiguity, generic support for material ambiguity, or Medium nonspecific recurrence |
| Localized: other qualified processing | `localized.qualified_processing` | Medium for the existing processing/subject-boundary/transition interpretations |
| Localized: no established mechanism | `localized.not_established` | Inconclusive, without borrowing generation confidence |
| Camera compatibility | `camera.acquisition_compatibility`, `.not_established` | Medium for existing camera-compatible observations or coherent photo-like consistency; otherwise Inconclusive. No authenticity claim |
| Unresolved anomaly | `generic.distinct_strong_sources`, `.one_strong_observation`, `.nonspecific_anomaly`, `.insufficient_support` | Existing 2B.3 generic High/Medium/Low/Inconclusive rules; no route-High bypass |
| Unknown hypothesis | `scope.unknown_hypothesis` | Inconclusive with an explicit missing-policy interpretation |

Generic thresholds remain S>=3 with the existing distinct-source requirement,
S>=2 with one valid strong observation, S>=1.2 for nonspecific Low, otherwise
Inconclusive. They are not applied as a universal formula to all three forensic
hypotheses. Mechanism-specific High rules remain valid compound interpretations,
not assertions of statistical independence.

## Selection, legacy compatibility and contradictions

Typed `Finding`/`Specificity` describes the evidentiary meaning used for selection:
unspecific concern, specific mechanism/declaration, or decisive local mechanism.
All matching findings are collected as a canonical hypothesis set for policy
evaluation. Selection still uses the existing route priorities and scoped
safeguards; it occurs before confidence. The highest-confidence hypothesis does
not automatically become primary.

The 26 route return tiers remain available for direct route callers and are
recorded as `legacy_confidence`. They are not authoritative. Matched route-trace
confidence comes from its assessed hypothesis policy; alternatives without an
assessment are explicitly marked nonauthoritative rather than emitting an
unexplained final tier. Tier-tampering regressions verify the separation.

Direct contradiction is preserved in its hypothesis/mechanism scope. Changing
boundary-focused support to boundary consistency can remove the existing compound
requirement and change the local rule. Surviving intrinsic/other compound support
can still justify its prior tier; no arbitrary global downgrade is introduced.
Boundary consistency does not contradict copy-move reuse. Camera compatibility
moderates generation/local interpretation without becoming a contradiction of a
generation declaration.

## Coverage and presentation

Pipeline coverage is supplied before policy evaluation. Missing relevant detector
results add explicit limitations, not positive/negative evidence. A missing
modality can prevent a rule that actually requires it (notably person geometry),
while a generation declaration does not require regional detectors to remain
Medium. Summary code no longer independently appends assessment limitations after
policy assignment.

`confidence_policy.version` is `3`; each assessment has a named rule and rationale.
The primary assessment tier is authoritative for overall confidence and GUI/text/
HTML presentation. Existing JSON fields remain, with additive rule/rationale and
policy-audit fields. Policy evidence IDs and limitations match the hypothesis
assessment; primary rationale adds only the existing selection explanation.

## Verification trust boundary

`VerifiedGenerationAssertion` is a typed result from a trusted upstream validator,
including successful validation and image binding. A JSON flag, C2PA presence,
enum string or metadata declaration cannot construct that trusted production
input. The current production adapter always supplies None because no validator
exists in the extraction path. Fixtures test the future typed contract without
implementing cryptographic validation. Even authenticated claim/image binding is
not automatically equivalent to independently verified pixel-generation history.
