"""Pure structural credit allocation; no learned weights or default family caps."""
from dataclasses import asdict, dataclass
from math import isfinite

from evidence_lineage import Addition, Kind, LineageError


@dataclass(frozen=True)
class Contribution:
    contribution_id: str
    evidence_ids: tuple[str, ...]
    target: str
    value: float
    polarity: str
    hypotheses: tuple[str, ...]
    domain: str | None = None
    # Arithmetic transforms and explicit multi-role policy are not new independent
    # observation credits. They remain visible but cannot be silently reweighted.
    credit_role: str = 'observation_credit'
    evidence_role: str = 'supporting_evidence'

    def __post_init__(self):
        if type(self.evidence_ids) is not tuple or type(self.hypotheses) is not tuple:
            raise LineageError('Contribution references and hypotheses must be immutable tuples.')
        if self.evidence_role not in {'supporting_evidence','contradicting_evidence','moderating_evidence','contextual_evidence'}:
            raise LineageError('Unknown hypothesis evidence role.')


@dataclass(frozen=True)
class ExperimentalCredits:
    """Explicit units of base credit, never a default coefficient or family cap."""
    name: str
    overrides: tuple[tuple[str, float], ...]

    def __post_init__(self):
        if not isinstance(self.name,str) or type(self.overrides) is not tuple or any(type(item) is not tuple or len(item)!=2 for item in self.overrides):
            raise LineageError('Experimental policy must have immutable name/credit pairs.')
        if not self.name.strip() or len(dict(self.overrides)) != len(self.overrides):
            raise LineageError('Experimental policy needs a name and unique credit identifiers.')
        for key,value in self.overrides:
            if not isinstance(key,str) or not key.startswith('base:') or isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value) or value < 0:
                raise LineageError('Experimental overrides must be finite, nonnegative base-credit units.')


def allocate_marginal(contributions, lineage, *, experimental=None):
    """Ancestry-ordered, hypothesis-specific allocation without input mutation.

    Pure restatement is a registry assertion, not an inference from a family name.
    Novel localization/relationships are reported with unknown calibrated margin;
    their existing value is retained provisionally, not endorsed as independent.
    """
    if experimental is not None and not isinstance(experimental,ExperimentalCredits):
        raise LineageError('Experimental credits require an explicit typed policy.')
    records = tuple(contributions)
    if len({c.contribution_id for c in records}) != len(records):
        raise LineageError('Duplicate contribution identifier.')
    lineage = tuple(lineage)
    nodes = {r.evidence_id:r for r in lineage}
    if len(nodes) != len(lineage):
        raise LineageError('Duplicate lineage identifier.')
    depth_cache = {}
    def depth(key, pending=()):
        if key in pending:
            raise LineageError('Cyclic lineage record: '+key)
        if key in depth_cache:
            return depth_cache[key]
        node = nodes.get(key)
        parents = node.direct_dependencies+node.optional_dependencies if node else ()
        depth_cache[key] = 1+max((depth(p,pending+(key,)) for p in parents),default=-1)
        return depth_cache[key]
    for key in sorted(nodes):
        depth(key)
    credits = dict(experimental.overrides) if experimental else {}
    if set(credits)-{c.contribution_id for c in records}:
        raise LineageError('Experimental override refers to an unknown contribution.')
    accepted = []
    output = []
    for c in sorted(records,key=lambda c:(max((depth(s) for s in c.evidence_ids),default=0),c.contribution_id)):
        if isinstance(c.value,bool) or not isinstance(c.value,(int,float)) or not isfinite(c.value):
            raise LineageError('Contribution must be finite: '+c.contribution_id)
        parents = [nodes.get(key) for key in c.evidence_ids]
        valid = bool(parents) and all(r and r.known and r.available and not r.missing_dependencies for r in parents)
        ancestry = tuple(sorted({a for r in parents if r for a in r.measurement_ancestry}))
        adjusted, marginal, pending = c.value, c.value, False
        reason = 'Primary measurement credit retained; no independence assertion.'
        if c.credit_role != 'observation_credit':
            marginal = None
            reason = 'Existing arithmetic/control policy preserved; not a separate independent observation credit.'
            pending = not valid and c.value > 0
        elif c.value > 0 and not valid:
            adjusted = marginal = 0.0
            reason = 'Unknown, missing or unavailable ancestry: positive shadow credit withheld.'
        elif c.polarity == 'benign' or c.value <= 0 or c.evidence_role in {'contradicting_evidence','moderating_evidence'}:
            reason = 'Counter-evidence/signed contribution retained in its hypothesis scope.'
        elif all(r.addition == Addition.RESTATEMENT for r in parents):
            # Counted evidence must be an actual ancestor, not a sibling that merely
            # shares a coarse family. Hypothesis and sign/target must also agree.
            def ancestors(key):
                node=nodes.get(key)
                return set().union(*( {p}|ancestors(p) for p in node.direct_dependencies)) if node and node.direct_dependencies else set()
            ancestor_ids=set().union(*(ancestors(key) for key in c.evidence_ids))
            covered = {a for prior,prior_ancestry in accepted
                if prior.target == c.target and prior.polarity == c.polarity
                and prior.hypotheses == c.hypotheses and set(prior.evidence_ids) <= ancestor_ids
                for a in prior_ancestry}
            if ancestry and set(ancestry) <= covered:
                adjusted = marginal = 0.0
                reason = 'Pure restatement of already credited ancestors in the same hypothesis/target; no additional observation.'
            else:
                reason = 'Restatement has no previously credited equivalent ancestor; existing credit retained.'
        elif any(r.kind != Kind.PRIMARY and r.addition != Addition.CONTROL for r in parents):
            marginal, pending = None, True
            reason = 'Added '+', '.join(sorted({r.addition.value for r in parents}))+' is identifiable; numerical marginal value is unvalidated. Existing credit retained provisionally.'
        if c.contribution_id in credits:
            if c.credit_role != 'observation_credit' or c.polarity != 'suspicious' or not valid:
                raise LineageError('Experimental allocations apply only to supported suspicious base credits.')
            if credits[c.contribution_id] > c.value:
                raise LineageError('Experimental credit may not exceed the existing credit.')
            adjusted, marginal, pending = credits[c.contribution_id], None, True
            reason = 'Explicit unvalidated experimental allocation: '+experimental.name
        if adjusted > 0 and valid and c.credit_role == 'observation_credit':
            accepted.append((c,ancestry))
        output.append({**asdict(c),'existing_contribution':c.value,'diagnostic_contribution':adjusted,
            'difference':adjusted-c.value,'marginal_contribution':marginal,
            'measurement_ancestry':ancestry,'reason':reason,'requires_empirical_validation':pending})
    return sorted(output,key=lambda r:r['contribution_id'])
