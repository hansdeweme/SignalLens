"""Read-only adapters for recorded reasoning; unknown fields stay unknown."""
import json
import math
from dataclasses import replace
from explorer_models import (ExplorerIdentity, EvidenceDetailView, LineageNodeView,
    AuditRecordView, ScoreContributionView, ExplorerSnapshot)
from evidence_lineage import REGISTRY

ROLES = ('supporting_evidence','contradicting_evidence','moderating_evidence','contextual_evidence')


def mapping(value):
    return value if isinstance(value,dict) else {}


def sequence(value):
    return value if isinstance(value,(list,tuple)) else ()


def strings(value):
    return tuple(v for v in sequence(value) if isinstance(v,str))


def text(value):
    return value if isinstance(value,str) else None


def display(value):
    if value is None:
        return 'Not recorded'
    if isinstance(value,float) and not math.isfinite(value):
        return 'Invalid non-finite value: '+str(value)
    if isinstance(value,(dict,list,tuple)):
        return json.dumps(value,ensure_ascii=False,indent=2,default=str)
    return str(value)


def fields(value):
    return tuple((str(k),display(v)) for k,v in mapping(value).items())


def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        return None
    return repr(value) if math.isfinite(value) else 'Invalid non-finite value'


def identity(snapshot):
    return ExplorerIdentity(snapshot.session_id,snapshot.analysis_id,snapshot.result_id,
                           snapshot.analysis_revision,snapshot.summary.status)


def record(record_id, title, block, hypothesis=None, outcome=None, explanation=None):
    block = mapping(block)
    evidence = tuple(dict.fromkeys(e for role in ROLES for e in strings(block.get(role))))
    evidence += tuple(e for e in strings(block.get('considered_evidence')) if e not in evidence)
    return AuditRecordView(str(record_id),str(title),hypothesis,outcome,explanation,fields(block),evidence)


def check_recorded_calculation(calc,card):
    """Use the existing pure audit formula, never assign a replacement score."""
    from scorecard_integrity import reconstruct_scorecard_calculation, COMPONENT_FIELDS
    if calc.get('calculation_version') != '2a' or calc.get('status') != 'valid':
        return record('reconciliation','Arithmetic reconciliation',{},outcome='Unavailable',
                      explanation='A complete valid version 2a ledger is required; recorded totals remain authoritative.')
    try:
        values = reconstruct_scorecard_calculation(calc)
        names = ('suspicious_score','benign_score',*COMPONENT_FIELDS)
        missing = [name for name in names if number(card.get(name)) is None]
        mismatch = [name for name in names if name not in missing and
                    not math.isclose(card[name],values[name],rel_tol=1e-12,abs_tol=1e-12)]
        status = 'Mismatch' if mismatch else 'Incomplete' if missing else 'Reconciled'
        return record('reconciliation','Arithmetic reconciliation',
            {'recorded':{name:card.get(name) for name in names},'reconstructed':values,
             'mismatches':mismatch,'missing_card_fields':missing,'relative_and_absolute_tolerance':1e-12},
            outcome=status,explanation='Existing Phase 2A pure audit replay. No authoritative value is replaced.')
    except (ValueError,KeyError,TypeError,OverflowError) as error:
        return record('reconciliation','Arithmetic reconciliation',{'audit_error':str(error)},
            outcome='Unavailable / invalid ledger',explanation='Audit could not replay this ledger; original totals are preserved.')


def build_explorer(snapshot, data, artifacts=()):
    """Detach a completed result. Does not call lineage/scoring/decision functions."""
    data = mapping(data)
    trace = mapping(data.get('reasoning_trace')) if snapshot.summary.status == 'completed' else {}
    issues = []
    if snapshot.summary.status == 'completed' and not isinstance(data.get('reasoning_trace'),dict):
        issues.append('Structured reasoning trace unavailable or malformed; original narrative remains accessible.')
    for key in ('hypothesis_assessments','decision_route_trace'):
        if key in trace and not isinstance(trace[key],list):
            issues.append(key+' has an unsupported or malformed container.')
    calc = mapping(trace.get('scorecard_calculation'))
    card = mapping(trace.get('scorecard'))
    allocation = mapping(calc.get('numerical_deduplication'))
    allocations = tuple(mapping(v) for v in sequence(allocation.get('contributions')) if isinstance(v,dict))
    sections = mapping(data.get('sections'))
    decision = mapping(trace.get('decision'))
    nodes = {}
    # Static schema is explicitly distinct from a reconstructed run graph.
    for key,spec in REGISTRY.items():
        nodes['evidence:'+key] = LineageNodeView('evidence:'+key,spec.family.value,spec.kind.value,
            tuple('evidence:'+p for p in spec.parents),tuple('evidence:'+p for p in spec.optional_parents),
            (),None,'Current registry schema; actual run dependencies not recorded')
    shadow = mapping(trace.get('evidence_dependency_analysis'))
    for item in sequence(shadow.get('lineage')):
        item = mapping(item)
        node_id = item.get('evidence_id')
        if isinstance(node_id,str):
            nodes[node_id] = LineageNodeView(node_id,item.get('family'),item.get('kind'),
                strings(item.get('direct_dependencies')),strings(item.get('optional_dependencies')),
                strings(item.get('measurement_ancestry')),item.get('status'),'Persisted diagnostic run lineage')
    # Numerical allocations record ancestry, but not direct dependency edges.
    for row in allocations:
        node_id = row.get('evidence_id')
        if isinstance(node_id,str) and node_id not in nodes:
            nodes[node_id] = LineageNodeView(node_id,None,None,(),(),strings(row.get('measurement_ancestry')),
                                           None,'Recorded numerical ancestry; direct dependencies unavailable')
        elif isinstance(node_id,str) and nodes[node_id].origin.startswith('Current'):
            node = nodes[node_id]
            nodes[node_id] = replace(node,measurements=strings(row.get('measurement_ancestry')),
                origin='Recorded numerical ancestry; parent edges from current registry schema')
    policy = mapping(trace.get('confidence_policy'))
    policies = {p['hypothesis']:p for item in sequence(policy.get('assessments'))
                if (p := mapping(item)) and isinstance(p.get('hypothesis'),str)}
    evidence, seen, hypotheses, confidence = [],set(),[],[]
    for raw in sequence(trace.get('hypothesis_assessments')):
        assessment = mapping(raw)
        hid = assessment.get('hypothesis_id')
        if not isinstance(hid,str):
            issues.append('Hypothesis assessment missing a valid ID.')
            continue
        final_policy = policies.get(hid,{})
        tier = final_policy.get('tier',assessment.get('confidence_tier'))
        hfields = {key:value for key,value in assessment.items() if key!='evidence_details'}
        hfields['final_confidence_tier'] = tier
        hfields['primary'] = hid == decision.get('primary_hypothesis')
        hypotheses.append(record(hid,hid,hfields,hid,tier,assessment.get('explanation')))
        confidence.append(record(hid,hid,final_policy or {
            'tier':tier,'policy_rule':assessment.get('confidence_policy_rule'),
            'rationale':assessment.get('confidence_rationale'),
            'limitations':assessment.get('limitations'),
            'availability':'Full centralized policy record not recorded'},hid,tier,
            final_policy.get('policy_rule',assessment.get('confidence_policy_rule'))))
        details = mapping(assessment.get('evidence_details'))
        for role in ROLES:
            for eid in strings(assessment.get(role)):
                ek = (hid,role,eid)
                if ek in seen:
                    continue
                seen.add(ek)
                detail = mapping(details.get(eid))
                detector = detail.get('section') if isinstance(detail.get('section'),str) else None
                section = mapping(sections.get(detector))
                section_details = mapping(section.get('details'))
                lineage_id = detail.get('lineage_reference')
                if not isinstance(lineage_id,str):
                    lineage_id = 'evidence:'+detector if detector and 'evidence:'+detector in nodes else None
                links = tuple(dict.fromkeys(a.artifact_id for a in artifacts
                    if a.session_id == snapshot.session_id and a.result_id == snapshot.result_id
                    and a.analysis_revision == snapshot.analysis_revision and eid in a.evidence_ids))
                observation = {'observed_status':detail.get('observed_status'),
                               'observed_score':detail.get('observed_score'),'observations':detail.get('observations')}
                evidence.append(EvidenceDetailView(eid,hid,role,text(detail.get('label')) or eid,detector,
                    text(detail.get('reliability')) or text(section_details.get('mask_reliability')),
                    text(detail.get('availability')) or text(detail.get('observed_status')) or text(section.get('status')),
                    '\n'.join(k.replace('_',' ').title()+': '+display(v) for k,v in observation.items()),
                    text(detail.get('interpretation')),strings(detail.get('limitations')),lineage_id,links,
                    fields({**detail,'detector_section':section or None})))
    for hid,final_policy in policies.items():
        if not any(row.hypothesis_id==hid for row in confidence):
            confidence.append(record(hid,hid,final_policy,hid,final_policy.get('tier'),final_policy.get('policy_rule')))
    routes = []
    for index,raw in enumerate(sequence(trace.get('decision_route_trace'))):
        block = mapping(raw)
        state = block.get('disposition')
        if block.get('selected') is True:
            state = 'Selected'
        elif not state:
            state = 'Not selected' if block.get('selected') is False else 'Not recorded'
        routes.append(record(str(index),block.get('route') or 'Unnamed route',block,
            block.get('hypothesis_id'),state,block.get('reason')))
    gates = tuple(record(str(index),block.get('gate_id') or 'Unnamed gate',block,
        block.get('hypothesis'),'Passed' if block.get('gate_passed') is True else
        'Not passed' if block.get('gate_passed') is False else 'Not recorded',block.get('explanation'))
        for index,raw in enumerate(sequence(mapping(trace.get('corroboration_audit')).get('evaluated_gates')))
        if (block := mapping(raw)))
    contributions = []
    for raw in allocations or sequence(calc.get('base_evidence')):
        row = mapping(raw)
        section = row.get('section')
        contributions.append(ScoreContributionView(row.get('evidence_id') or 'base:'+str(section),section,
            row.get('polarity'),number(row.get('raw_contribution',row.get('weight'))),
            number(row.get('credited_contribution',row.get('credited_weight'))),number(row.get('reliability_multiplier')),
            number(row.get('final_adjusted_contribution')),number(row.get('suppressed_contribution')),
            row.get('classification'),row.get('reason'),fields(row)))
    score_records = []
    for name in ('base_suspicious','base_benign','domain_bonus','aggregate_scores','aggregate_transforms',
                 'raw_contributions','reliability_adjustments','final_contributions','penalties','component_operations',
                 'numerical_deduplication'):
        value = calc.get(name)
        if isinstance(value,list):
            for index,item in enumerate(value):
                score_records.append(record(name+'/'+str(index),name,mapping(item),outcome=str(index)))
        elif value is not None:
            # Keep large audit groups as lazy selected details, not thousands of widgets.
            score_records.append(record(name,name,value if isinstance(value,dict) else {'value':value}))
    summary = ('Suspicious: '+display(card.get('suspicious_score'))+' · Benign: '+display(card.get('benign_score'))+
        '\nRecorded calculation status: '+display(calc.get('status'))+' · Recorded card validity: '+display(card.get('is_valid'))+
        '\nHeuristic scores are not probabilities. Base allocation precedes aggregate transforms and penalties.')
    if not calc:
        summary += '\nHistorical contribution ledger unavailable.'
    if card.get('validation_errors'):
        summary += '\nValidation errors: '+display(card['validation_errors'])
    reconciliation = check_recorded_calculation(calc,card)
    score_records.insert(0,reconciliation)
    summary += '\nArithmetic audit: '+reconciliation.outcome
    return ExplorerSnapshot(identity(snapshot),tuple(evidence),tuple(nodes.values()) if trace else (),tuple(hypotheses),
        tuple(routes),gates,tuple(confidence),tuple(contributions),tuple(score_records),summary,
        text(decision.get('primary_hypothesis')),text(decision.get('dominant_pattern')),text(snapshot.coverage_status),tuple(issues),
        json.dumps(trace,ensure_ascii=False,indent=2,default=str))
