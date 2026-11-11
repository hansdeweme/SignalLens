"""Bounded declaration comparisons for investigation synthesis, never score votes.

No prose classifier, retrieval, image matcher or provenance validator lives here.
External attributes are explicit analyst records; loader names remain declarations.
"""
import json
import re

CLAIM_PROCESSES = ('not_recorded', 'full_image_generation', 'unspecified_generation_process',
                   'image_to_image', 'inpainting', 'enhancement', 'localized_editing',
                   'camera_capture', 'unmodified_camera_capture', 'ai_tool_usage')
ASSOCIATIONS = ('unestablished', 'analyst_associated', 'rejected')
DEPENDENCIES = ('unknown', 'same_creator', 'repeated_claim', 'independent_source_asserted')


def _family(value):
    """Controlled model-family tokens, never a process or authenticity classifier."""
    value = str(value).casefold()
    for family, pattern in (('flux', r'\bflux(?:[._ -]?2)?\b'),
                            ('midjourney', r'\bmidjourney\b'),
                            ('stable_diffusion', r'\b(?:stable[ _-]diffusion|sdxl)\b')):
        if re.search(pattern, value):
            return family
    return None


def _model_details(metadata, workflow):
    """Use named inputs on connected API loader nodes; no prompt-text matching."""
    output = []
    sinks = {str(p['sink_node']) for p in workflow.get('supporting_node_paths', [])
             if isinstance(p, dict) and p.get('sink_node') is not None}
    if workflow.get('graph_interpretation_status') != 'coherent':
        return output
    for signal in metadata.get('details', {}).get('metadata_signals', []):
        if not isinstance(signal, dict):
            continue
        for entry in signal.get('evidence', []):
            if not isinstance(entry, dict) or entry.get('raw_key') not in workflow.get('source_fields', []):
                continue
            graph = entry.get('value')
            try:
                graph = json.loads(graph) if isinstance(graph, str) else graph
            except (ValueError, TypeError, RecursionError):
                continue
            if not isinstance(graph, dict) or 'nodes' in graph or len(graph) > 1024:
                continue
            pending, active = list(sinks), set()
            while pending:
                node_id = pending.pop()
                if node_id in active:
                    continue
                active.add(node_id)
                node = graph.get(node_id)
                if not isinstance(node, dict) or not isinstance(node.get('inputs'), dict):
                    continue
                inputs = node['inputs']
                pending.extend(str(v[0]) for v in inputs.values()
                               if isinstance(v, list) and len(v) == 2 and str(v[0]) in graph)
                key = {'CheckpointLoaderSimple': 'ckpt_name', 'UNETLoader': 'unet_name',
                       'LoraLoader': 'lora_name'}.get(node.get('class_type'))
                if key and isinstance(inputs.get(key), str):
                    detail = {'source_field': entry['raw_key'], 'node_id': node_id,
                              'attribute': key, 'value': inputs[key], 'model_family': _family(inputs[key])}
                    if detail not in output:
                        output.append(detail)
    return sorted(output, key=lambda r: (r['source_field'], r['node_id'], r['attribute']))


def assess_relationships(creation, metadata, matches, *, reviewed, identity_status, image_sha256, verifications=None):
    workflow = creation.get('workflow_interpretation') or {}
    process = creation.get('declared_process')
    models = _model_details(metadata, workflow)
    technical = {'claim_id': 'claim:embedded:process', 'source_ref': 'forensic:metadata',
        'origin': 'embedded_metadata', 'claim_type': 'creation_process', 'process': process,
        'image_sha256': image_sha256, 'verification_status': creation['provenance_authenticity'],
        'review_status': 'recorded_forensic_declaration', 'details': creation,
        'model_details': models, 'limitations': ['Declaration is not proof of execution or pixel origin.']}
    claims, relationships = [technical], []
    technical_families = {m['model_family'] for m in models if m['model_family']}
    generations = {'full_image_generation', 'unspecified_generation_process'}
    for index, match in enumerate(matches):
        ref = f'osint:match:{index}'
        claimed = match.get('claim_process', 'not_recorded')
        claimed = claimed if claimed in CLAIM_PROCESSES else 'not_recorded'
        assertion = match.get('image_association', 'unestablished')
        method, basis = match.get('association_method', ''), match.get('association_details', '')
        verification = (verifications or {}).get(match.get('record_id'))
        association = ('image_identity_mismatch' if identity_status == 'mismatched' else
            'unestablished' if identity_status != 'matched' else
            'rejected' if assertion == 'rejected' else
            verification['association'] if verification and verification['association'] in
                {'byte_identical', 'visually_verified', 'rejected'} else
            'analyst_associated' if assertion == 'analyst_associated' and method in
                {'analyst_assertion', 'analyst_visual_check'} and isinstance(basis, str) and basis.strip() else
            'unestablished')
        if verification and verification['association'] in {'byte_identical', 'visually_verified', 'rejected'}:
            method = verification.get('metrics', {}).get('method', '')
            basis = 'Retained source bytes and authenticated local verification receipt; no publisher authentication.'
        dependency = match.get('source_dependency', 'unknown')
        dependency = dependency if dependency in DEPENDENCIES else 'unknown'
        claim = {'claim_id': f'claim:{ref}:process', 'source_ref': ref,
            'origin': 'external_analyst_record', 'claim_type': 'creation_process', 'process': claimed,
            'page_url': match.get('page_url'), 'image_url': match.get('image_url', ''),
            'claim_text': match.get('claim_text') or match.get('title', ''),
            'model_family': match.get('model_family', ''), 'workflow_details': match.get('workflow_details', ''),
            'claimed_by': match.get('claimed_by', 'unknown'), 'attribution': match.get('attribution', ''),
            'review_status': 'analyst_reviewed' if reviewed else 'not_reviewed',
            'verification_status': 'unverified', 'image_sha256': image_sha256,
            'local_record_binding': identity_status,
            'image_association': association, 'association_assertion': assertion,
            'association_method': method, 'association_details': basis,
            'source_image_verification': verification,
            'limitations': [match.get('claim_limitations', '')] if match.get('claim_limitations') else []}
        claims.append(claim)
        if not process or claimed in {'not_recorded', 'ai_tool_usage'}:
            agreement = ('contextual_compatibility' if process in generations and claimed == 'not_recorded'
                         and match.get('source_type') == 'ai_gallery' else 'not_comparable')
            reason = 'Source classification supplies context only; no comparable creation-process claim is recorded.'
        elif process == claimed or process in generations and claimed in generations:
            agreement, reason = 'compatible', 'The recorded creation-process declarations are compatible.'
        elif (process in generations and claimed == 'unmodified_camera_capture') or (
                process == 'unmodified_camera_capture' and claimed in generations):
            agreement, reason = 'conflicting', 'Generation and unmodified camera origin conflict if they concern the same image.'
        else:
            agreement, reason = 'different_stages_unresolved', 'These processes may describe different stages; chronology is not established.'
        family = _family(match.get('model_family', ''))
        model_agreement = ('not_comparable' if not family or not technical_families else
                           'compatible' if family in technical_families else 'differing_declarations')
        if model_agreement == 'compatible':
            reason += ' A recorded connected loader and the source name a compatible model family; exact versions and execution are not verified.'
        elif model_agreement == 'differing_declarations':
            reason += ' Recorded model families differ; this discrepancy may concern different stages and is unresolved.'
        limits = ['Source independence is not established; repeated creator claims receive no independent score credit.',
                  'Agreement does not authenticate metadata, authorship or the external account.']
        if association == 'unestablished':
            limits.append('A URL, review flag or analyst similarity score does not establish source-image identity.')
        elif association == 'analyst_associated':
            limits.append('Image association is an explicit analyst assertion, not reproducible visual verification or a file-hash match.')
        if verification:
            limits.extend(verification['limitations'])
        elif match.get('verification'):
            limits.append('Verification evidence is missing, corrupted, invalidated or bound to a different source; association was not accepted.')
        if assertion in {'visually_verified', 'byte_identical'} and not verification:
            limits.append('Claimed automated association has no supported reproducible verifier; it was not accepted.')
        status = ('not_assessed' if not reviewed else 'insufficient_association' if association in
                  {'image_identity_mismatch', 'rejected'} else 'conflicting_claims' if agreement == 'conflicting' or
                  model_agreement == 'differing_declarations' else 'insufficient_association' if association == 'unestablished'
                  else 'corroborated_declaration' if agreement == 'compatible' else 'contextual_agreement' if
                  agreement == 'contextual_compatibility' else 'not_assessed')
        relationships.append({'relationship_id': f'relationship:embedded:{index}',
            'claim_refs': [technical['claim_id'], claim['claim_id']], 'evidence_refs': ['forensic:metadata', ref],
            'agreement': agreement, 'reason': reason, 'model_agreement': model_agreement,
            'workflow_agreement': 'process_comparison_only; external workflow details remain analyst-reported',
            'image_association': association, 'source_dependency': dependency,
            'independence': 'not_established', 'status': status, 'limitations': limits})
    # Unresolved conflicts must remain visible even alongside compatible declarations.
    states = {r['status'] for r in relationships}
    status = next((s for s in ('conflicting_claims', 'corroborated_declaration', 'insufficient_association',
                             'contextual_agreement') if s in states), 'not_assessed')
    text = {'conflicting_claims': 'Cross-source declarations conflict; image association and authenticity leave the conflict unresolved.',
        'corroborated_declaration': 'Compatible embedded and reviewed external declarations support synthetic creation context for the associated image. Their independence and authenticity remain unestablished.',
        'insufficient_association': 'External claims or source context have been compared, but source-image association is insufficient for image-specific corroboration.',
        'contextual_agreement': 'External source context is compatible with the embedded declaration; the source has no explicit comparable process claim.',
        'not_assessed': 'No reviewed, comparable cross-source creation-process agreement is established.'}[status]
    # This label can also apply to compatible processing declarations, without implying synthetic origin.
    if status == 'corroborated_declaration' and process not in generations:
        text = 'Compatible embedded and reviewed external processing declarations corroborate a declaration, not its execution, independence or authenticity.'
    return {'schema_version': 1, 'assessment_status': status, 'interpretation': text,
            'claims': claims, 'relationships': relationships,
            'association_levels': {'unestablished': 'No demonstrated source-image association',
                'analyst_associated': 'Explicit analyst association with recorded method and basis',
                'visually_verified': 'Reproducible visual match with retained asset and valid local receipt',
                'byte_identical': 'Actual downloaded source bytes have the same SHA-256'},
            'limitations': ['No probabilities, score changes, independent confirmations or technical authentication are inferred.']}


def relationship_text(record):
    if not record:
        return ''
    lines = [f"Cross-source assessment: {record['assessment_status']}", record['interpretation']]
    for claim in record['claims']:
        lines += [f"Claim {claim['claim_id']} | Source: {claim.get('page_url') or claim['source_ref']}",
                  f"Process: {claim['process']} | Review: {claim['review_status']} | Authenticity: {claim['verification_status']}"]
        if claim['origin'] == 'external_analyst_record':
            lines += [f"Source image URL: {claim['image_url']}", f"Claim: {claim['claim_text']}",
                f"Claimed by: {claim['claimed_by']} | Attribution (unverified): {claim['attribution']}",
                f"Model: {claim['model_family']} | Workflow: {claim['workflow_details']}",
                f"Image association: {claim['image_association']} | Method: {claim['association_method']} | Basis: {claim['association_details']}"]
            if claim.get('source_image_verification'):
                lines += ['Source-image verification: ' + json.dumps(claim['source_image_verification'], ensure_ascii=False)]
        else:
            workflow = claim['details'].get('workflow_interpretation') or {}
            if workflow:
                lines += [f"Workflow status: {workflow.get('graph_interpretation_status')} | Declaration fingerprint: {workflow.get('graph_fingerprint')}",
                    'Supporting node paths: ' + json.dumps(workflow.get('supporting_node_paths', []), ensure_ascii=False)]
            if claim.get('model_details'):
                lines += ['Embedded model details: ' + json.dumps(claim['model_details'], ensure_ascii=False)]
        lines += ['Limitation: ' + s for s in claim['limitations']]
    for rel in record['relationships']:
        lines += [f"Relationship {rel['relationship_id']} | Claims: {', '.join(rel['claim_refs'])}",
            f"Agreement: {rel['agreement']} | Model agreement: {rel['model_agreement']} | {rel['reason']}",
            f"Workflow comparison: {rel['workflow_agreement']}",
            f"Association: {rel['image_association']} | Dependence: {rel['source_dependency']} | Independence: {rel['independence']}",
            f"Assessment: {rel['status']}"]
        lines += ['Limitation: ' + s for s in rel['limitations']]
    return '\n'.join(lines)
