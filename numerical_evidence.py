"""Production base-credit identity/restatement correction, without reweighting.

Reuse the existing lineage graph. Shared ancestry alone never suppresses new
localization or a related measurement. Component formulas keep their explicit
scoring roles; this allocator does not treat them as independent observations.
"""
from math import fsum

from evidence_lineage import (
    Addition, Kind, build_lineage, numerical_restatement_sources,
)
from scorecard_integrity import ScorecardIntegrityError, finite_number


def allocate_base_evidence(sections, raw_rows, *, registry=None):
    """Return copied effective base rows and a deterministic allocation ledger.

    Object identity proves duplicate representation in this call. Equal-valued
    distinct objects do not prove observation identity. No IDs derived from
    memory addresses are persisted. Registered keys win identity ties.
    """
    lineage = build_lineage(sections, **({'registry': registry} if registry is not None else {}))
    nodes = {r.evidence_id.removeprefix('evidence:'): r for r in lineage}
    raw_rows = tuple(raw_rows)
    rows = {r['section']: dict(r) for r in raw_rows}
    if len(rows) != len(raw_rows):
        raise ScorecardIntegrityError('Duplicate base contribution identifiers.')
    representatives = {}
    for key in sorted(rows, key=lambda k: (not nodes[k].known, k)):
        representatives.setdefault(id(sections[key]), key)

    def ancestors(key):
        node = nodes[key]
        result = set()
        for reference in node.direct_dependencies + node.optional_dependencies:
            parent = reference.removeprefix('evidence:')
            result.add(parent)
            result.update(ancestors(parent))
        return result

    allocations = {}
    for key in sorted(rows, key=lambda k: (len(ancestors(k)), k)):
        row, node = rows[key], nodes[key]
        raw = finite_number(row['weight'], 'base:' + key)
        final, category, credited_by = raw, 'D', []
        reason = 'Related or unregistered observation retained provisionally; no independence claim.'
        unresolved = not node.known or node.kind != Kind.PRIMARY
        if node.known and node.kind == Kind.PRIMARY:
            category, reason = 'C', 'Distinct primary measurement retained at its existing status weight.'
        elif node.addition in {Addition.LOCALIZATION, Addition.RELATIONSHIP}:
            category, reason = 'C', 'Additional measured localization/relationship retained; shared ancestry is not redundancy.'
        elif key in {'boundary', 'subject_material_realism'} and node.known:
            category, reason = 'C', 'Additional contour/material properties retained under the existing scoring rules.'

        representative = representatives[id(sections[key])]
        sources = numerical_restatement_sources(key, sections[key].pattern)
        # A registered pure restatement can be added without a second lineage
        # system. It must have an actually credited ancestor in the same scope.
        if node.addition == Addition.RESTATEMENT:
            sources = tuple(sorted(ancestors(key)))
        for source in sources:
            source_row = rows.get(source)
            source_node = nodes.get(source)
            source_final = allocations.get(source, {}).get('credited_contribution', 0.0)
            if source == 'cross_signal':
                # Sibling contract above: its active overlap summary is the
                # canonical counted representation, even if parents were omitted.
                source_final = source_row['weight'] if source_row else 0.0
                if not source_row or sections[source].pattern not in {'partial_hotspot_convergence', 'strong_hotspot_convergence'}:
                    continue
            if (source_row and source_final > 0 and source_row['polarity'] == row['polarity']
                    and source_node.hypotheses == node.hypotheses
                    and set(node.measurement_ancestry) <= set(source_node.measurement_ancestry)):
                credited_by.append('evidence:' + source)
        if representative != key:
            final, category, unresolved = 0.0, 'A', False
            credited_by = ['evidence:' + representative]
            reason = 'Identical summary instance already represented by its canonical section key.'
        elif credited_by:
            final, category, unresolved = 0.0, 'B', False
            reason = 'Existing overlap/measurement already credited; this representation adds no positive measured property.'
        elif node.addition == Addition.RESTATEMENT and node.missing_dependencies:
            final, category, unresolved = 0.0, 'B', False
            reason = 'Pure restatement has no available upstream measurement to credit.'
        elif sources:
            category, unresolved = 'B', False
            reason = 'Single overlap/measurement representation retained; no other counted representation exists in this scope.'
        if node.missing_dependencies and final:
            unresolved = True
            reason += ' Raw parent summaries are missing; the observed summary contract remains provisional.'
        row['credited_weight'] = final
        allocations[key] = {
            'evidence_id': 'evidence:' + key, 'section': key,
            'raw_contribution': raw, 'measurement_ancestry': list(node.measurement_ancestry),
            'previously_credited_evidence': sorted(credited_by),
            'additional_information': node.addition.value,
            'classification': category, 'eligible_marginal_contribution': final,
            'credited_contribution': final, 'suppressed_contribution': raw - final,
            'reliability_multiplier': 1.0, 'final_adjusted_contribution': final,
            'adjustment_stage': 'base_before_aggregate_attenuation_penalties_and_floor',
            'hypotheses': list(node.hypotheses), 'polarity': row['polarity'],
            'missing_dependencies': list(node.missing_dependencies),
            'unresolved': unresolved, 'reason': reason,
        }
    effective = [rows[key] for key in sorted(rows)]
    audit = {'version': '2b4', 'contributions': [allocations[key] for key in sorted(allocations)],
             'unresolved_relationships': [allocations[key]['evidence_id'] for key in sorted(allocations)
                                          if allocations[key]['unresolved']],
             'aggregate_reconciliation': {}}
    for polarity in ('suspicious', 'benign'):
        selected = [r for r in effective if r['polarity'] == polarity]
        original_domains = {r['domain'] for r in selected if r['domain']}
        credited_domains = {r['domain'] for r in selected if r['domain'] and r['credited_weight'] > 0}
        audit['aggregate_reconciliation'][polarity] = {
            'raw_base_weight': fsum(r['weight'] for r in selected),
            'credited_base_weight': fsum(r['credited_weight'] for r in selected),
            'suppressed_base_weight': fsum(r['weight'] - r['credited_weight'] for r in selected),
            'raw_domain_bonus': max(0, len(original_domains) - 1) * 0.25,
            'credited_domain_bonus': max(0, len(credited_domains) - 1) * 0.25,
            'credited_domains': sorted(credited_domains),
        }
    return effective, audit


def add_fragment_component(ledger, audit, field, operand, reason):
    """Withhold the same confirmed restatement in its mechanism paths too.

    Local-support conversion then consumes the corrected support naturally;
    no post-aggregate subtraction or new conversion coefficient is needed.
    """
    duplicate = any(r['section'] == 'boundary' and r['classification'] == 'B'
                    and r['suppressed_contribution'] > 0 for r in audit['contributions'])
    ledger.add(field, 0.0 if duplicate else operand, reason)
    if duplicate:
        index = len(ledger.operations) - 1
        ledger.operations[index]['raw_operand'] = operand
        ledger.operations[index]['numerical_allocation'] = 'B:overlap_restatement'
        audit.setdefault('component_allocations', []).append({
            'ledger_index': index, 'field': field, 'evidence_id': 'evidence:boundary',
            'classification': 'B', 'raw_contribution': operand,
            'credited_contribution': 0.0, 'suppressed_contribution': operand,
            'reliability_multiplier': 1.0, 'final_adjusted_contribution': 0.0,
            'reason': 'Fragment fallback adds no positive measurement beyond the credited cross-overlap; mechanism restatement withheld.',
        })


def finalize_component_allocations(audit, operations):
    for row in audit.get('component_allocations', []):
        factor = 1.0
        for later in operations[row['ledger_index'] + 1:]:
            if later['field'] == row['field'] and later['operation'] == 'multiply':
                factor *= later['operand']
        row['reliability_multiplier'] = factor
        row['final_adjusted_contribution'] = row['credited_contribution'] * factor
