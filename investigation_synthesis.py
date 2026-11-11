"""Investigation-level interpretation of frozen facts and associated source review.

No detectors, score arithmetic, network access or modification of the forensic
trace. Qualitative dimensions share evidence; they are not independent votes.
"""
from dataclasses import asdict, dataclass
from types import SimpleNamespace
from math import isfinite
from metadata_evidence import metadata_creation_context
from workflow_interpretation import workflow_description
from evidence_relationships import assess_relationships, relationship_text

POLICY_VERSION = 'investigation.origin_processing.v3'


def mapping(value):
    return value if isinstance(value, dict) else {}


@dataclass(frozen=True)
class Assessment:
    status: str
    interpretation: str
    support_tier: str | None = None
    evidence_refs: tuple[str, ...] = ()
    supporting_observations: tuple[str, ...] = ()
    contradicting_observations: tuple[str, ...] = ()
    moderating_observations: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    review_status: str = 'frozen_forensic_assessment'


def _assessment(h, status, interpretation, *, limits=(), supporting=()):
    return asdict(Assessment(status, interpretation, h.get('confidence_tier'),
        tuple(h.get('supporting_evidence') or ()) + tuple(h.get('contradicting_evidence') or ())
        + tuple(h.get('moderating_evidence') or ()) + tuple(h.get('contextual_evidence') or ()) + tuple(supporting),
        tuple(h.get('supporting_evidence') or ()) + tuple(supporting),
        tuple(h.get('contradicting_evidence') or ()), tuple(h.get('moderating_evidence') or ()),
        tuple(dict.fromkeys([*(h.get('limitations') or ()), *limits]))))


def build_synthesis(forensic_data, annotations, source_sha256, *, verifications=None):
    """Pure, deterministic content; session/revision provenance is supplied by owner."""
    data, notes = mapping(forensic_data), mapping(annotations)
    trace = mapping(data.get('reasoning_trace'))
    hypotheses = {h.get('hypothesis_id'): h for h in trace.get('hypothesis_assessments', []) if isinstance(h, dict)}
    origin, local = hypotheses.get('synthetic_origin', {}), hypotheses.get('localized_editing', {})
    sections = mapping(data.get('sections')) or mapping(trace.get('section_snapshot'))
    raw_metadata = mapping(sections.get('metadata'))
    if not raw_metadata.get('details'):
        raw_metadata = mapping(mapping(trace.get('evidence_snapshot')).get('metadata')) or raw_metadata
    creation = metadata_creation_context(SimpleNamespace(pattern=raw_metadata.get('pattern'), details=raw_metadata.get('details')))
    # Historical partial traces may retain scoped declarations without raw tags.
    declared = creation['kind'] in {'structured_workflow', 'explicit_generation_declaration'} and creation['declared_process'] not in {'enhancement', 'unspecified_enhancement_process'}
    declared = declared or any(e in {'metadata:DECLARED_SYNTHETIC', 'metadata:EMBEDDED_GENERATION_PROMPT'} for e in origin.get('supporting_evidence', []))
    if declared and creation['declared_process'] is None:
        creation.update(kind='explicit_generation_declaration', declared_process='unspecified_generation_process', provenance_authenticity='unverified')

    association = ('matched' if source_sha256 and notes.get('image_sha256') == source_sha256 else
                   'mismatched' if source_sha256 and notes.get('image_sha256') else 'unassociated')
    matches = [m for m in notes.get('matches', []) if isinstance(m, dict) and m.get('page_url')]
    def meaningful_review(m):
        score = m.get('similarity_score')
        return (type(score) in {int, float} and isfinite(score) and 0 <= score <= 1) or bool(m.get('title') or m.get('notes') or m.get('claim_text'))
    reviewed = (notes.get('analyst_reviewed') is True and notes.get('review_status') == 'reviewed_matches_found'
                and any(meaningful_review(m) for m in matches) and association == 'matched')
    ai_matches = [m for m in matches if m.get('source_type') == 'ai_gallery' and meaningful_review(m)
                  and m.get('claim_process', 'not_recorded') in
                  {'not_recorded', 'full_image_generation', 'unspecified_generation_process'}] if reviewed else []
    external_refs = tuple(f'osint:match:{i}' for i, m in enumerate(matches) if m in ai_matches)
    source_refs = tuple(f'osint:match:{i}' for i, m in enumerate(matches) if reviewed and meaningful_review(m))
    source_status = ('reviewed_manual_match' if reviewed else 'image_identity_mismatch' if association == 'mismatched'
                     else 'reviewed_no_match' if notes.get('analyst_reviewed') and not matches and association == 'matched'
                     else 'unreviewed_or_unassociated' if matches else 'not_recorded')
    source_text = ('Reviewed source classification supplies generation context; external image identity remains separately assessed.' if ai_matches else
                   'Reviewed source matches are recorded as context.' if reviewed else
                   'Source evidence does not currently supply reviewed, image-associated corroboration.')
    external = asdict(Assessment(source_status, source_text, evidence_refs=source_refs,
        supporting_observations=source_refs,
        limitations=('Manual similarity is analyst-reported; it is not a computed file-hash match or cryptographic authentication.',
                     'Repeated metadata and source claims are not assumed independent.'), review_status=source_status))
    external.update(image_association=association, source_image_match_status='manual_similarity_unverified' if reviewed else 'not_assessed',
        matches=matches, creator_generation_claim=[{'evidence_ref': f'osint:match:{i}', 'page_url': m['page_url'],
            'image_url': m.get('image_url', ''), 'claim': m.get('title', ''), 'analyst_notes': m.get('notes', ''),
            'normalized_similarity': m.get('similarity_score'), 'basis': 'analyst_reviewed_source_context'}
            for i, m in enumerate(matches) if m in ai_matches],
        evidence_dependency=[{'evidence_ref': r, 'related_refs': origin.get('supporting_evidence', []),
                              'relationship': 'may_repeat_same_creation_claim; no_independent_score_credit'} for r in external_refs])

    relationships = assess_relationships(creation, raw_metadata, matches, reviewed=reviewed,
        identity_status=association, image_sha256=source_sha256, verifications=verifications)
    external['local_record_binding'] = external.pop('image_association')
    external['source_image_associations'] = [r['image_association'] for r in relationships['relationships']]
    if any(s in {'byte_identical', 'visually_verified'} for s in external['source_image_associations']):
        external['source_image_match_status'] = 'verified_assets_recorded'
    external['cross_source_assessment'] = relationships
    external['assessment_status'] = relationships['assessment_status']
    external['interpretation'] = relationships['interpretation']
    associated_refs = {ref for rel in relationships['relationships']
        if rel['image_association'] in {'analyst_associated', 'byte_identical', 'visually_verified'}
        for ref in rel['evidence_refs']}
    # Keep unassociated source claims visible, but do not let their category
    # manufacture image-specific origin support or a generation heading.
    ai_matches = [m for i, m in enumerate(matches) if m in ai_matches and f'osint:match:{i}' in associated_refs]
    external_refs = tuple(ref for ref in external_refs if ref in associated_refs)
    external_refs = tuple(dict.fromkeys((*external_refs, *(ref for rel in relationships['relationships']
        if rel['status'] == 'corroborated_declaration' for ref in rel['evidence_refs'] if ref.startswith('osint:')))))

    regional_refs = tuple(e for e in local.get('supporting_evidence', []) if not e.startswith('metadata:'))
    regional = bool(regional_refs)
    specific = (local.get('decision_branch') in {'possible_clone_reuse', 'localized_editing_multi_mechanism'}
                and local.get('confidence_tier') == 'High')
    limits = ['Regional processing differences do not establish a distinct edit or its chronology.']
    masks = mapping(mapping(trace.get('evidence_snapshot')).get('region_masks'))
    geometry = mapping(masks.get('details'))
    if geometry:
        limits.append(f"Segmentation quality: {geometry.get('mask_reliability') or geometry.get('person_mask_reliability') or 'not recorded'}; "
                      f"boundary support: {mapping(trace.get('derived_signals')).get('boundary_reliability_score', 'not recorded')}. These are different reliability concepts.")
    asymmetry = mapping(mapping(sections.get('subject_process_asymmetry')).get('details'))
    if asymmetry.get('baseline_reliability_score') is not None:
        limits.append(f"Background comparison baseline reliability: {asymmetry['baseline_reliability_score']}; regional sampling may not represent an independent baseline.")
    alignment = mapping(sections.get('segmentation_alignment'))
    if alignment.get('score') == 0 and alignment.get('status') not in {'not_run', 'unavailable', 'failed', 'error', 'skipped'}:
        limits.append('Cross-signal hotspots do not demonstrate alignment with the person boundary.')

    origin_status = ('declared_generation_with_source_context' if declared and ai_matches else 'declared_generation' if declared
                     else 'source_generation_context' if ai_matches else 'not_established')
    origin_text = workflow_description(creation.get('workflow_interpretation'))
    if not origin_text:
        origin_text = ('Embedded metadata declares generation; the detailed process and authenticity are unverified.' if declared else
                       'Origin is not established by the frozen forensic assessment.')
    if ai_matches:
        origin_text += ' ' + source_text
    if relationships['relationships']:
        origin_text += ' ' + relationships['interpretation']
    corroborated_generation = (relationships['assessment_status'] == 'corroborated_declaration'
        and creation.get('declared_process') in {'full_image_generation', 'unspecified_generation_process'})
    if corroborated_generation:
        origin_status = 'cross_source_corroborated_generation_declaration'
    origin_assessment = _assessment(origin, origin_status, origin_text, supporting=external_refs,
        limits=('Source context does not authenticate the complete creation history.',))
    origin_assessment['creation_context'] = creation
    origin_assessment['external_corroboration_status'] = relationships['assessment_status']
    anomaly = _assessment(local, 'observations_present' if regional else 'not_established',
        'Regional forensic observations are retained; their support tier is scoped to processing anomalies.', limits=limits)
    edit = _assessment(local, 'specific_mechanism_supported' if specific else 'not_established',
        'Specific reuse/mechanism evidence remains independently scoped; chronology is unknown.' if specific else
        'A distinct editing operation is not established by regional anomalies or source declarations.', limits=limits)
    edit['support_tier'] = local.get('confidence_tier') if specific else None
    provenance = mapping(trace.get('provenance_evidence'))
    technical = asdict(Assessment('unverified' if provenance or declared else 'not_assessed',
        'No cryptographic validator and image-binding result authenticates the creation history.',
        evidence_refs=('forensic:provenance_evidence',) if provenance else (),
        limitations=('Metadata declarations, source review and normalized similarity do not verify technical provenance.',),
        review_status='no_validator_result'))
    title = ('Specific mechanism evidence and creation context' if specific else
             'Generation context with regional observations' if (declared or ai_matches) and regional else
             'Generation context; edit history unresolved' if declared or ai_matches else
             'Regional observations; edit history unresolved' if regional else 'Origin and editing history unresolved')
    if relationships['assessment_status'] == 'conflicting_claims':
        title = 'Conflicting creation declarations; history unresolved'
    elif corroborated_generation:
        title = 'Corroborated generation declaration; history remains qualified'
    text = origin_text + ' ' + edit['interpretation']
    scope = f"Frozen forensic support — origin: {origin.get('confidence_tier') or 'not recorded'}; regional: {local.get('confidence_tier') or 'not recorded'}. These are not probabilities or an overall verdict tier."
    return {'policy_version': POLICY_VERSION, 'origin_assessment': origin_assessment,
            'regional_anomaly_assessment': anomaly, 'separate_edit_assessment': edit,
            'technical_provenance_authenticity': technical, 'external_source_corroboration': external,
            'lead': {'title': title, 'interpretation': text, 'confidence_scope': scope},
            'limitations': ['Dimensions may share measurements and creation claims; no statistical independence is assumed.']}


def synthesis_text(record):
    if not record:
        return ''
    lines = ['Current investigation synthesis', record['lead']['title'], record['lead']['interpretation'],
             record['lead']['confidence_scope'],
             f"Revision: {record.get('revision_id', 'not recorded')} | Evidence revision: {record.get('osint_evidence_revision', 0)}",
             f"Forensic snapshot: {record.get('forensic_snapshot_id')} | Source SHA-256: {record.get('image_sha256')}"]
    for key in ('origin_assessment', 'regional_anomaly_assessment', 'separate_edit_assessment',
                'technical_provenance_authenticity', 'external_source_corroboration'):
        value = record[key]
        lines += [f"{key}: {value['status']}", value['interpretation']]
        lines += [f'- {s}' for s in value.get('limitations', [])]
    for claim in record['external_source_corroboration'].get('creator_generation_claim', []):
        lines += [f"Source: {claim['page_url']}", f"Source claim: {claim['claim']}",
                  f"Analyst-reported normalized similarity: {claim['normalized_similarity']}"]
    relationships = record['external_source_corroboration'].get('cross_source_assessment')
    if relationships:
        lines += ['', relationship_text(relationships)]
    return '\n'.join(lines)
