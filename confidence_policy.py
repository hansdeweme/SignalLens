# confidence_policy.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

"""Hypothesis-scoped confidence policy, version 3 (heuristic, not probability).
Route tiers/names and narrative text are deliberately absent from policy inputs.
Rules consolidate existing mechanism constraints and generic 2B.3 corroboration.
"""
from dataclasses import dataclass
from enum import Enum
from math import isfinite

from metadata_evidence import ProvenanceState


class Finding(str, Enum):
    UNSPECIFIED='unspecified'
    PHOTO_CONTEXT='photo_context_ambiguity'
    BOUNDARY_LIMITED='boundary_support_limited'
    GEOMETRY_LIMITED='region_geometry_limited'
    MULTI_LOCAL='multiple_local_mechanisms'
    BOUNDARY_DECISIVE='decisive_boundary_mechanism'
    LOCAL_UNCERTAIN='strong_local_concern_unspecific'
    CLONE_DECISIVE='decisive_spatial_reuse'
    BOUNDARY_SUPPORTED='supported_boundary_mechanism'
    LOCAL_WEAK='limited_local_mechanism'
    CLONE_CAMERA_AMBIGUOUS='reuse_camera_ambiguity'
    CLONE_MATERIAL_AMBIGUOUS='reuse_material_ambiguity'
    CLONE_AMBIGUOUS='reuse_nonspecific'
    RECURRENCE_CAUTION='recurrence_context_ambiguity'
    VISUAL_GENERATION='visual_generation_compound'
    LOCAL_PROCESSING='differential_processing_unspecific'
    SUBJECT_BOUNDARY='intrinsic_boundary_transition'
    UNRELIABLE_BOUNDARY='unreliable_person_boundary'
    BOUNDARY_TRANSITION='supported_transition_anomaly'
    GENERATION_DECLARATION='unverified_generation_declaration'
    ENHANCEMENT_DECLARATION='unverified_enhancement_declaration'
    SOURCE_CONTEXT='source_context'
    CAMERA_COMPATIBLE='camera_acquisition_compatible'
    ANOMALY_ACCUMULATION='general_anomaly_accumulation'
    GENERAL_ANOMALY='general_anomaly'
    PHOTO_CONSISTENCY='photo_like_consistency'
    FALLBACK='unresolved_interpretation'
    INVALID='invalid_analysis'


class Specificity(str, Enum):
    UNSPECIFIC='unspecific'
    SPECIFIC='specific_mechanism_or_declaration'
    DECISIVE='decisive_local_mechanism'


def finding_specificity(finding):
    if finding in {Finding.MULTI_LOCAL,Finding.BOUNDARY_DECISIVE,Finding.CLONE_DECISIVE}:
        return Specificity.DECISIVE
    if finding in {Finding.BOUNDARY_SUPPORTED,Finding.SUBJECT_BOUNDARY,Finding.BOUNDARY_TRANSITION,
                   Finding.VISUAL_GENERATION,Finding.GENERATION_DECLARATION,Finding.ENHANCEMENT_DECLARATION}:
        return Specificity.SPECIFIC
    return Specificity.UNSPECIFIC


@dataclass(frozen=True)
class VerifiedGenerationAssertion:
    """Trusted upstream validator result, never constructed from metadata flags.

    Current production has no validator and never populates this input. Tests
    can model a future successful signature/assertion/image-binding validation.
    Authentication of a claim alone is not proof of pixel origin.
    """
    evidence_id: str
    validator_id: str
    validation_succeeded: bool
    image_binding_verified: bool

    def __post_init__(self):
        if not self.evidence_id or not self.validator_id or any(type(v) is not bool for v in (self.validation_succeeded,self.image_binding_verified)):
            raise ValueError('Verification needs a named validator and explicit validation/binding results.')


@dataclass(frozen=True)
class ConfidenceFacts:
    valid: bool = True
    findings: tuple[tuple[str,tuple[Finding,...]],...] = ()
    suspicious: float = 0.0
    local_support: float = 0.0
    clone_support: float = 0.0
    camera_support: float = 0.0
    synthetic_boost: float = 0.0
    person_reliable: bool = False
    boundary_reliability: float = 0.0
    geometry_unreliable: bool = False
    context_risk: bool = False
    boundary_compound: bool = False
    generic_source_diversity: bool = False
    generic_strong_count: int = 0
    visual_global: bool = False
    visual_regional: bool = False
    camera_observed: bool = False
    provenance: ProvenanceState = ProvenanceState.NO_SUBSTANTIVE_PROVENANCE_EVIDENCE
    osint_ai_context: bool = False
    missing_detectors: tuple[str,...] = ()
    verification: VerifiedGenerationAssertion | None = None
    coverage_limitations: tuple[str,...] = ()

    def __post_init__(self):
        if type(self.findings) is not tuple or type(self.missing_detectors) is not tuple or type(self.coverage_limitations) is not tuple:
            raise ValueError('Policy snapshots must use immutable collections.')
        if len(dict(self.findings))!=len(self.findings):
            raise ValueError('Duplicate hypothesis finding set.')
        for hypothesis,findings in self.findings:
            if not isinstance(hypothesis,str) or type(findings) is not tuple or any(not isinstance(f,Finding) for f in findings):
                raise ValueError('Findings must be typed immutable hypothesis claims.')
        if not isinstance(self.provenance,ProvenanceState) or (self.verification is not None and not isinstance(self.verification,VerifiedGenerationAssertion)):
            raise ValueError('Provenance confidence requires typed state/validator evidence.')

    def for_hypothesis(self,hypothesis):
        return frozenset(dict(self.findings).get(hypothesis,()))


@dataclass(frozen=True)
class AssessmentEvidence:
    hypothesis: str
    supporting_evidence: tuple[str,...] = ()
    contradicting_evidence: tuple[str,...] = ()
    moderating_evidence: tuple[str,...] = ()
    contextual_evidence: tuple[str,...] = ()
    limitations: tuple[str,...] = ()

    def __post_init__(self):
        for name in ('supporting_evidence','contradicting_evidence','moderating_evidence','contextual_evidence','limitations'):
            if type(getattr(self,name)) is not tuple:
                raise ValueError('Scoped policy evidence must use immutable tuples.')

    @classmethod
    def from_assessment(cls,assessment):
        return cls(assessment.hypothesis_id,*(tuple(getattr(assessment,role)) for role in (
            'supporting_evidence','contradicting_evidence','moderating_evidence','contextual_evidence')),
            tuple(assessment.limitations))


@dataclass(frozen=True)
class ConfidencePolicyResult:
    hypothesis: str
    tier: str
    policy_rule: str
    supporting_evidence: tuple[str,...]
    contradicting_evidence: tuple[str,...]
    moderating_evidence: tuple[str,...]
    contextual_evidence: tuple[str,...]
    reliability_limitations: tuple[str,...]
    rationale: tuple[str,...]


def generic_confidence(suspicious, strong_count, source_diversity):
    """Exact existing generic thresholds; distinct-source result is from 2B.3."""
    if source_diversity and suspicious>=3.0:
        return 'High','generic.distinct_strong_sources'
    if strong_count>=1 and suspicious>=2.0:
        return 'Medium','generic.one_strong_observation'
    if suspicious>=1.2:
        return 'Low','generic.nonspecific_anomaly'
    return 'Inconclusive','generic.insufficient_support'


def _synthetic(facts,findings):
    if Finding.VISUAL_GENERATION in findings and Finding.RECURRENCE_CAUTION not in findings and facts.synthetic_boost>=1.0 and facts.suspicious>=5.0:
        if facts.visual_global or (facts.visual_regional and facts.person_reliable and not facts.geometry_unreliable):
            return 'High','synthetic.visual_compound','Existing generation-relevant compound evidence supports visual structure; this is not authenticated origin.'
    v=facts.verification
    if v is not None and v.validation_succeeded and v.image_binding_verified:
        return 'Medium','synthetic.verified_assertion','A validator authenticated a generation assertion and its image binding; claim authentication alone does not establish pixel origin.'
    if facts.provenance==ProvenanceState.UNVERIFIED_GENERATION_DECLARATION:
        return 'Medium','synthetic.unverified_generation_declaration','An explicit generation declaration supports declared creation context; metadata authenticity is unverified.'
    if facts.provenance==ProvenanceState.UNVERIFIED_ENHANCEMENT_DECLARATION:
        return 'Medium','synthetic.unverified_enhancement_declaration','An enhancement declaration supports AI-mediated processing context, not whole-image generation.'
    if facts.osint_ai_context:
        return 'Low','synthetic.source_context','Reviewed source context supports a provisional origin interpretation, without authenticating creation history.'
    if Finding.RECURRENCE_CAUTION in findings:
        return 'Medium','synthetic.recurrence_ambiguity','Structured recurrence is measurable but remains compatible with scene content or processing.'
    if Finding.VISUAL_GENERATION in findings and facts.visual_regional and not facts.person_reliable:
        return 'Inconclusive','synthetic.required_region_unavailable','Region-dependent generation evidence lacks reliable required person geometry.'
    return 'Inconclusive','synthetic.not_established','No specific generation interpretation is established; localized anomalies do not supply missing generation support.'


def _localized(facts,findings):
    # Spatial reuse is not a person-boundary claim and survives boundary safeguards.
    if Finding.CLONE_DECISIVE in findings and facts.clone_support>=3.5 and facts.clone_support>=facts.local_support+1.0 and facts.camera_support<2.0:
        return 'High','localized.spatial_reuse','Existing spatial-reuse mechanism support is decisive within its stated limitations, not proof of AI use.'
    for finding,rule,why in (
        (Finding.PHOTO_CONTEXT,'localized.photo_context_ambiguity','Camera metadata and supplied processing context limit localized interpretation.'),
        (Finding.BOUNDARY_LIMITED,'localized.boundary_support_limited','Boundary support fails the existing mechanism reliability requirement.'),
        (Finding.GEOMETRY_LIMITED,'localized.geometry_limited','Region geometry is unreliable for a decisive boundary interpretation.'),
        (Finding.UNRELIABLE_BOUNDARY,'localized.person_boundary_unavailable','Required reliable person-boundary geometry is unavailable.'),
    ):
        if finding in findings:return 'Medium',rule,why
    regional_findings={Finding.MULTI_LOCAL,Finding.BOUNDARY_DECISIVE,Finding.BOUNDARY_SUPPORTED,
        Finding.SUBJECT_BOUNDARY,Finding.BOUNDARY_TRANSITION}
    if regional_findings&findings:
        if not facts.person_reliable or facts.geometry_unreliable:
            return 'Medium','localized.required_geometry_cap','A person-boundary interpretation cannot be High without reliable required geometry.'
        if facts.boundary_reliability<0.6:
            return 'Medium','localized.boundary_support_limited','The existing boundary-reliability requirement is not met, regardless of which candidate routes were supplied.'
    if {Finding.MULTI_LOCAL,Finding.BOUNDARY_DECISIVE}&findings:
        if Finding.MULTI_LOCAL in findings and facts.local_support>=3.0 and facts.clone_support>=3.0 and abs(facts.local_support-facts.clone_support)<1.0 and not facts.context_risk:
            return 'High','localized.multiple_mechanisms','Existing local-processing and reuse mechanism requirements are satisfied.'
        if Finding.BOUNDARY_DECISIVE in findings and facts.local_support>=3.5 and facts.local_support>=facts.clone_support+1.0 and facts.camera_support<2.0 and not facts.context_risk and facts.boundary_compound:
            return 'High','localized.reliable_boundary_compound','Strong local-processing support and the existing compound boundary requirement are satisfied.'
    if Finding.LOCAL_UNCERTAIN in findings:
        if facts.camera_support:
            return 'Low','localized.camera_moderated_uncertainty','Camera-compatible structure moderates an unconfirmed local mechanism; it does not exclude later editing.'
        return 'Medium','localized.unspecific_local_processing','Strong local concern lacks sufficient boundary corroboration for a specific mechanism.'
    if Finding.BOUNDARY_SUPPORTED in findings and facts.boundary_compound:
        return 'Medium','localized.supported_boundary','The existing compound transition requirements support a qualified localized interpretation.'
    if Finding.LOCAL_WEAK in findings:
        return 'Low','localized.limited_mechanism','The local mechanism remains insufficiently corroborated.'
    if Finding.CLONE_CAMERA_AMBIGUOUS in findings:
        return 'Low','localized.reuse_camera_ambiguity','Camera compatibility limits an ambiguous reuse interpretation.'
    if Finding.CLONE_MATERIAL_AMBIGUOUS in findings:
        tier,rule=generic_confidence(facts.suspicious,facts.generic_strong_count,facts.generic_source_diversity)
        return tier,'localized.reuse_ambiguity.'+rule,'Material-related regularity leaves the reuse mechanism ambiguous; generic support does not establish synthetic origin.'
    if Finding.CLONE_AMBIGUOUS in findings:
        return 'Medium','localized.reuse_unspecific','Repeated content is present but natural repetition remains a plausible explanation.'
    if findings&{Finding.LOCAL_PROCESSING,Finding.SUBJECT_BOUNDARY,Finding.BOUNDARY_TRANSITION}:
        return 'Medium','localized.qualified_processing','Existing transition or processing evidence supports a qualified localized concern.'
    return 'Inconclusive','localized.not_established','A specific localized mechanism is not established.'


def evaluate_confidence(evidence, facts):
    """Authoritative pure policy over scoped evidence and typed factual snapshots."""
    hypothesis=evidence.hypothesis
    findings=facts.for_hypothesis(hypothesis)
    finite=all(isfinite(v) for v in (facts.suspicious,facts.local_support,facts.clone_support,facts.camera_support,facts.synthetic_boost,facts.boundary_reliability))
    if not facts.valid or not finite:
        tier,rule,why='Inconclusive','integrity.invalid_scorecard','Numerical integrity failed; confidence is withheld.'
    elif hypothesis=='synthetic_origin':
        tier,rule,why=_synthetic(facts,findings)
    elif hypothesis=='localized_editing':
        tier,rule,why=_localized(facts,findings)
    elif hypothesis=='camera_acquisition':
        if facts.camera_observed or findings&{Finding.CAMERA_COMPATIBLE,Finding.PHOTO_CONSISTENCY}:
            tier,rule,why='Medium','camera.acquisition_compatibility','Camera-like structure or coherent photo-like processing supports compatibility, not photographic authenticity.'
        else:
            tier,rule,why='Inconclusive','camera.not_established','Camera acquisition is not established.'
    elif hypothesis=='unresolved_anomaly':
        tier,rule=generic_confidence(facts.suspicious,facts.generic_strong_count,facts.generic_source_diversity)
        why='General anomaly support uses the existing source-diversity policy; it does not identify an origin or localized mechanism.'
    else:
        tier,rule,why='Inconclusive','scope.unknown_hypothesis','Unknown hypothesis has no registered confidence interpretation.'
    limits=list(evidence.limitations)+list(facts.coverage_limitations)
    relevant={
        'synthetic_origin':{'metadata','fft','patch_similarity','subject_material_realism','subject_process_asymmetry'},
        'localized_editing':{'region_masks','boundary_focus','segmentation_alignment','subject_boundary','patch_spatial'},
        'camera_acquisition':{'sensor_origin','cfa_demosaic'},
        'unresolved_anomaly':set(),
    }.get(hypothesis,set())
    missing=sorted(relevant.intersection(facts.missing_detectors))
    if missing:limits.append('Coverage limitation (not negative evidence): unavailable '+', '.join(missing)+'.')
    rationale=[f'Confidence policy {rule}: {why}']
    if evidence.contradicting_evidence:
        rationale.append('Direct counter-evidence remains scoped to this mechanism. Surviving compound/reuse requirements, not a global point deduction, determine the tier.')
    if evidence.moderating_evidence:
        rationale.append('Moderating observations qualify this interpretation; they do not automatically refute it or support a different hypothesis.')
    rationale.append('Confidence tiers are heuristic support levels, not calibrated probabilities; related module outputs are not assumed statistically independent.')
    return ConfidencePolicyResult(hypothesis,tier,rule,evidence.supporting_evidence,evidence.contradicting_evidence,
        evidence.moderating_evidence,evidence.contextual_evidence,tuple(dict.fromkeys(limits)),tuple(rationale))
