# production_corroboration.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

"""Production corroboration semantics over Phase 2B.2 lineage.
Measurement-disjoint witnesses are a structural diversity check, never a test
of statistical independence. Compound mechanisms retain related interpretations.
"""
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from numbers import Real

from evidence_lineage import Addition, Family, Kind, LineageError, build_lineage, lineage_from_json, lineage_to_json


class RequirementKind(str, Enum):
    DISTINCT_SOURCES = 'distinct_measurement_sources'
    COMPOUND = 'compound_interpretations'
    ACCUMULATION = 'general_accumulation'


@dataclass(frozen=True)
class CorroborationRequirement:
    gate_id: str
    hypothesis: str
    kind: RequirementKind
    minimum_indicators: int = 1
    minimum_sources: int = 1
    distinct_families: bool = False

    def __post_init__(self):
        if not self.gate_id or not self.hypothesis or not isinstance(self.kind,RequirementKind):
            raise LineageError('A gate needs an identifier, hypothesis and declared semantics.')
        if any(type(v) is not int or v<1 for v in (self.minimum_indicators,self.minimum_sources)) or type(self.distinct_families) is not bool:
            raise LineageError('Corroboration requirements must be positive integer counts and a boolean family rule.')


CONTROL_ANCESTRY = frozenset({'measurement:selected_mask_geometry'})
ACTIVE = frozenset({'weak','medium','strong'})


def _valid_observation(section):
    if section is None or section.status not in ACTIVE:
        return False
    score=section.score
    return score is None or (not isinstance(score,bool) and isinstance(score,Real) and isfinite(score))


def _disjoint_witnesses(candidates, require_families):
    """Largest disjoint subset, deterministic tie-break; never greedy clustering.

    Adding a composite AB must not collapse genuinely separate primary A and B.
    Identical ancestry/family candidates can be coalesced for the search only.
    """
    unique={}
    for key,ancestry,family in sorted(candidates):
        token=(ancestry,family if require_families else '')
        unique.setdefault(token,(key,ancestry,family))
    rows=sorted(unique.values())
    best=()
    def search(index,chosen,used_measurements,used_families):
        nonlocal best
        if len(chosen)>len(best) or (len(chosen)==len(best) and chosen<best):
            best=chosen
        if len(chosen)+len(rows)-index<len(best):
            return
        for i in range(index,len(rows)):
            key,ancestry,family=rows[i]
            if not used_measurements.intersection(ancestry) and (not require_families or family not in used_families):
                search(i+1,chosen+(key,),used_measurements.union(ancestry),used_families|{family})
    search(0,(),set(),set())
    return best


def evaluate_corroboration(sections, evidence_ids, requirement, *, lineage=None, roles=None):
    """Pure hypothesis-scoped source/compound assessment; never mutates evidence.

    An observed compound summary may remain interpretable when callers omit its
    raw parent summaries. Such provisional lineage cannot count as a distinct
    measurement source. This preserves legacy compound-summary APIs without
    inventing upstream observations.
    """
    records=lineage_from_json(lineage_to_json(tuple(lineage))) if lineage is not None else build_lineage(sections)
    nodes={record.evidence_id:record for record in records}
    if len(nodes)!=len(records):
        raise LineageError('Duplicate lineage identifiers in corroboration input.')
    considered=tuple(sorted(set(evidence_ids)))
    eligible=[]; excluded={}; provisional={}; increments=[]; candidates=[]
    limitations=[]; all_ancestry={}; role_map={}
    for key in considered:
        node=nodes.get(key)
        section=sections.get(key.removeprefix('evidence:'))
        role=(roles or {}).get(key,'supporting_evidence')
        role_map[key]=role
        if not node or not node.known:
            excluded[key]='Unknown lineage cannot establish corroboration.'
            continue
        if role not in {'supporting_evidence','contradicting_evidence','moderating_evidence','contextual_evidence'}:
            raise LineageError('Unknown hypothesis evidence role.')
        if role!='supporting_evidence':
            excluded[key]='Retained as '+role+'; not counted as supporting corroboration.'
            continue
        if requirement.hypothesis!='unresolved_anomaly' and requirement.hypothesis not in node.hypotheses:
            excluded[key]='The observation is outside this hypothesis scope.'
            continue
        expected='benign' if requirement.hypothesis=='camera_acquisition' else 'suspicious'
        if not _valid_observation(section) or not node.available or section.polarity!=expected:
            excluded[key]='No valid available supporting observation in this hypothesis polarity.'
            continue
        roots=tuple(sorted(set(node.measurement_ancestry)-CONTROL_ANCESTRY))
        all_ancestry[key]=roots
        if node.addition in {Addition.LOCALIZATION,Addition.RELATIONSHIP,Addition.INTERPRETATION}:
            increments.append({'evidence_id':key,'addition':node.addition.value,
                'new_measurement_claim':bool(node.kind==Kind.PRIMARY),
                'numeric_weight_changed':False})
        complete=not node.missing_dependencies and bool(roots)
        if not complete:
            provisional[key]=list(node.missing_dependencies) or ['No non-control measurement ancestry is established.']
        if requirement.kind==RequirementKind.DISTINCT_SOURCES and not complete:
            excluded[key]='Required measurement ancestry is missing or provisional.'
            continue
        eligible.append(key)
        if complete:
            candidates.append((key,roots,node.family.value))
    selected=_disjoint_witnesses(candidates,requirement.distinct_families)
    shared={}
    for root in sorted({r for roots in all_ancestry.values() for r in roots}):
        ids=[key for key,roots in sorted(all_ancestry.items()) if root in roots]
        if len(ids)>1:
            shared[root]=ids
    overlapping={}
    for key in eligible:
        for group in nodes[key].overlap_groups:
            if group!='selected_geometry': overlapping.setdefault(group,[]).append(key)
    overlapping={k:v for k,v in sorted(overlapping.items()) if len(v)>1}
    satisfied=len(eligible)>=requirement.minimum_indicators
    if requirement.kind==RequirementKind.DISTINCT_SOURCES:
        satisfied=satisfied and len(selected)>=requirement.minimum_sources
        explanation=(f'{len(selected)} measurement-disjoint supporting indicator(s) satisfy' if satisfied else
            f'{len(selected)} measurement-disjoint supporting indicator(s) do not satisfy')+f' the existing {requirement.minimum_sources}-source diversity requirement.'
    else:
        explanation=f'{len(eligible)} observed supporting indicator(s) '+('satisfy' if satisfied else 'do not satisfy')+f' the {requirement.minimum_indicators}-indicator {requirement.kind.value} condition; shared ancestry is allowed and is not independent confirmation.'
    if provisional:
        limitations.append('Provisional compound summaries do not establish missing upstream measurements or additional distinct sources.')
    if overlapping:
        limitations.append('Feature-definition/content overlap remains; disjoint extraction IDs do not demonstrate statistical independence.')
    limitations.append('Source groups are structural measurement ancestry, not probabilities or statistically independent samples.')
    return {'gate_id':requirement.gate_id,'hypothesis':requirement.hypothesis,
        'requirement_kind':requirement.kind.value,
        'minimum_indicators':requirement.minimum_indicators,'minimum_sources':requirement.minimum_sources if requirement.kind==RequirementKind.DISTINCT_SOURCES else None,
        'distinct_families_required':requirement.distinct_families,
        'considered_evidence':list(considered),'eligible_evidence':sorted(eligible),
        'excluded_evidence':excluded,'evidence_roles':role_map,
        'distinct_ancestry_groups':[{'witness':key,'measurements':list(all_ancestry[key]),'family':nodes[key].family.value} for key in selected],
        'corroborating_source_count':len(selected),'shared_ancestry':shared,
        'overlapping_feature_groups':overlapping,'incremental_support_findings':increments,
        'provisional_lineage':provisional,'requirement_satisfied':satisfied,
        'explanation':explanation,'limitations':limitations}


def record_gate(collector, result):
    """Replace an existing gate result, avoiding repeated-evaluation state growth."""
    if collector is not None:
        collector[:]=[entry for entry in collector if entry['gate_id']!=result['gate_id']]+[result]
        collector.sort(key=lambda entry:entry['gate_id'])
    return result


def explain_gate(result, conditions):
    """Describe the caller's actual production predicates, not just ancestry counts.

    `requirement_satisfied` remains the structural corroboration subcondition.
    Some legacy production predicates intentionally use derived pattern flags
    rather than that subcondition; callers must state those predicates explicitly.
    """
    result['conditions'] = [dict(condition_id=key, passed=bool(passed), explanation=text)
        for key, passed, text in conditions]
    result['failure_reasons'] = [c['explanation'] for c in result['conditions'] if not c['passed']]
    result['overall_explanation'] = ('Overall PASS: all production conditions satisfied.'
        if result['gate_passed'] else 'Overall FAIL: ' + '; '.join(result['failure_reasons']))
    return result
