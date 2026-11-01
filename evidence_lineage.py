"""Versioned, immutable measurement ancestry. A family is not independence.

Registry follows the Phase 2B.1 code audit. Measurement IDs denote distinguishable
feature extractions, not statistically independent samples or sensor attribution.
"""
from dataclasses import asdict, dataclass
from enum import Enum
from types import MappingProxyType


class LineageError(ValueError):
    pass


class Family(str, Enum):
    PROVENANCE = 'provenance'
    PROCESSING = 'processing_residual'
    SPECTRAL = 'spectral'
    RECURRENCE = 'patch_recurrence'
    SURFACE = 'subject_surface'
    ACQUISITION = 'camera_pipeline'
    COMPRESSION = 'compression_history'
    EDGE = 'intrinsic_edge_transition'
    GEOMETRY = 'geometry'
    CONTEXT = 'analyst_context'
    UNKNOWN = 'unknown'


class Kind(str, Enum):
    PRIMARY = 'primary'
    DERIVED = 'derived'
    COMPOSITE = 'composite'


class Addition(str, Enum):
    OBSERVATION = 'new_measurement'
    LOCALIZATION = 'localization'
    RELATIONSHIP = 'cross_measurement_relationship'
    INTERPRETATION = 'interpretation'
    RESTATEMENT = 'restatement'
    CONTROL = 'reliability_or_context'


@dataclass(frozen=True)
class EvidenceSpec:
    key: str
    detector: str
    family: Family
    measurements: tuple[str, ...]
    parents: tuple[str, ...] = ()
    optional_parents: tuple[str, ...] = ()
    hypotheses: tuple[str, ...] = ()
    kind: Kind = Kind.PRIMARY
    addition: Addition = Addition.OBSERVATION
    overlap_groups: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.key,str) or not self.key or not isinstance(self.detector,str) or not self.detector:
            raise LineageError('Evidence key and source detector must be nonempty text.')
        for name in ('measurements','parents','optional_parents','hypotheses','overlap_groups'):
            values=getattr(self,name)
            if type(values) is not tuple or any(not isinstance(v,str) or not v for v in values) or len(set(values))!=len(values):
                raise LineageError('Evidence collections must be immutable unique text tuples: '+name)
        if self.addition==Addition.RESTATEMENT and self.measurements:
            raise LineageError('A pure restatement cannot declare a new measurement.')


@dataclass(frozen=True)
class LineageRecord:
    evidence_id: str
    source_detector: str
    family: Family
    measurement_ancestry: tuple[str, ...]
    direct_dependencies: tuple[str, ...]
    optional_dependencies: tuple[str, ...]
    missing_dependencies: tuple[str, ...]
    hypotheses: tuple[str, ...]
    status: str
    available: bool
    scoring_available: bool
    kind: Kind
    addition: Addition
    overlap_groups: tuple[str, ...] = ()
    known: bool = True

    def __post_init__(self):
        if not isinstance(self.evidence_id,str) or not self.evidence_id.startswith('evidence:') or not isinstance(self.source_detector,str) or not isinstance(self.status,str):
            raise LineageError('Lineage identity, source and status must be text.')
        if not isinstance(self.family,Family) or not isinstance(self.kind,Kind) or not isinstance(self.addition,Addition):
            raise LineageError('Record categories must use lineage enums.')
        for name in ('measurement_ancestry','direct_dependencies','optional_dependencies','missing_dependencies','hypotheses','overlap_groups'):
            values=getattr(self,name)
            if type(values) is not tuple or any(not isinstance(v,str) for v in values):
                raise LineageError('Lineage records cannot retain mutable payload collections.')
        if any(type(getattr(self,name)) is not bool for name in ('available','scoring_available','known')):
            raise LineageError('Availability flags must be booleans.')


SYN = ('synthetic_origin',)
EDIT = ('localized_editing',)
CAM = ('camera_acquisition',)
SYN_EDIT = SYN + EDIT
UNAVAILABLE = frozenset({'not_run', 'unavailable', 'skipped', 'failed', 'error'})
ACTIVE = frozenset({'weak', 'medium', 'strong'})

# Masks are required geometric inputs of regional consumers. They are controls,
# not independent evidence of generation. Optional parents record actual payload
# reuse without requiring parents the detector can run without.
_SPECS = (
    EvidenceSpec('metadata','exiftool_backend.analyze_file_with_exiftool',Family.PROVENANCE,('embedded_assertions',),hypotheses=SYN+CAM,overlap_groups=('provenance_assertion',)),
    EvidenceSpec('osint','summary_sections.build_osint_section',Family.PROVENANCE,('reviewed_source_context',),hypotheses=SYN,overlap_groups=('provenance_assertion',)),
    EvidenceSpec('ela','vf_ela.run_ela',Family.PROCESSING,('ela_recompression_difference',),hypotheses=EDIT,overlap_groups=('processing_anomalies',)),
    EvidenceSpec('noise','vf_noise.run_noise_analysis',Family.PROCESSING,('luminance_residual',),hypotheses=EDIT,overlap_groups=('processing_anomalies','highpass_features')),
    EvidenceSpec('cross_signal','vf_cross_signal.compute_cross_signal_payload',Family.PROCESSING,(),('ela','noise'),hypotheses=EDIT,kind=Kind.COMPOSITE,addition=Addition.RELATIONSHIP,overlap_groups=('processing_anomalies',)),
    EvidenceSpec('boundary','vf_cross_signal.classify_boundary_convergence',Family.PROCESSING,(),('ela','noise'),hypotheses=EDIT,kind=Kind.COMPOSITE,addition=Addition.INTERPRETATION,overlap_groups=('processing_anomalies','contour_interpretation')),
    EvidenceSpec('boundary_focus','vf_boundary_focus.run_boundary_focus_analysis',Family.PROCESSING,(),('ela','noise','region_masks'),hypotheses=EDIT,kind=Kind.COMPOSITE,addition=Addition.LOCALIZATION,overlap_groups=('processing_anomalies','selected_geometry')),
    EvidenceSpec('segmentation_alignment','vf_segmentation_alignment.compute_segmentation_boundary_alignment',Family.PROCESSING,(),('cross_signal','region_masks'),hypotheses=EDIT,kind=Kind.COMPOSITE,addition=Addition.LOCALIZATION,overlap_groups=('processing_anomalies','selected_geometry')),
    EvidenceSpec('fft','vf_fft.run_fft_analysis',Family.SPECTRAL,('global_spectral_features',),hypotheses=SYN_EDIT,overlap_groups=('spectral_feature_code',)),
    EvidenceSpec('region_fft','vf_region_fft.run_region_fft_analysis',Family.SPECTRAL,('regional_spectral_features',),('region_masks',),hypotheses=SYN_EDIT,kind=Kind.DERIVED,addition=Addition.LOCALIZATION,overlap_groups=('spectral_feature_code','selected_geometry')),
    EvidenceSpec('patch_similarity','vf_patch_similarity.run_patch_similarity_analysis',Family.RECURRENCE,('retained_patch_matches',),hypotheses=SYN_EDIT,overlap_groups=('texture_recurrence',)),
    EvidenceSpec('patch_spatial','vf_patch_spatial.run_patch_spatial_analysis',Family.RECURRENCE,(),('patch_similarity','region_masks'),hypotheses=SYN_EDIT,kind=Kind.DERIVED,addition=Addition.LOCALIZATION,overlap_groups=('texture_recurrence','selected_geometry')),
    EvidenceSpec('subject_texture_consistency','vf_subject_texture_consistency.run_subject_texture_consistency_analysis',Family.SURFACE,('masked_hybrid_texture_descriptors',),('region_masks',),hypotheses=SYN_EDIT,overlap_groups=('texture_recurrence','surface_feature_definitions','selected_geometry')),
    EvidenceSpec('subject_process_asymmetry','vf_subject_process_asymmetry.run_subject_process_asymmetry_analysis',Family.SURFACE,('regional_patch_statistics',),('region_masks',),('subject_texture_consistency','region_fft'),SYN_EDIT,Kind.COMPOSITE,Addition.INTERPRETATION,('surface_feature_definitions','highpass_features','selected_geometry')),
    EvidenceSpec('subject_material_realism','vf_subject_material_realism.run_subject_material_realism_analysis',Family.SURFACE,('subject_material_patch_statistics',),('region_masks',),hypotheses=SYN_EDIT,kind=Kind.DERIVED,addition=Addition.INTERPRETATION,overlap_groups=('surface_feature_definitions','highpass_features','selected_geometry')),
    EvidenceSpec('sensor_origin','vf_sensor_origin.run_sensor_origin_analysis',Family.ACQUISITION,('luminance_phase_residual',),hypotheses=CAM+EDIT,overlap_groups=('highpass_features','acquisition_phase_features')),
    EvidenceSpec('cfa_demosaic','vf_cfa_demosaic.run_cfa_demosaic_analysis',Family.ACQUISITION,('chroma_phase_directionality',),hypotheses=CAM+EDIT,overlap_groups=('highpass_features','acquisition_phase_features')),
    EvidenceSpec('compression_history','vf_compression_history.run_compression_history_analysis',Family.COMPRESSION,('aligned_offgrid_boundary_energy',),hypotheses=EDIT+CAM,overlap_groups=('processing_anomalies',)),
    EvidenceSpec('subject_boundary','vf_subject_boundary.run_subject_boundary_analysis',Family.EDGE,('intrinsic_edge_ring_features',),hypotheses=EDIT,overlap_groups=('highpass_features','image_gradients')),
    EvidenceSpec('region_masks','vf_person_subject_mask.derive_region_masks_from_person_mask',Family.GEOMETRY,('selected_mask_geometry',),kind=Kind.DERIVED,addition=Addition.CONTROL,overlap_groups=('selected_geometry',)),
    EvidenceSpec('scene_context','hypothesis_engine.build_context',Family.CONTEXT,(),addition=Addition.CONTROL),
)


def validate_registry(specs):
    records = tuple(specs)
    mapping = {s.key: s for s in records}
    if len(mapping) != len(records):
        raise LineageError('Duplicate evidence registration.')
    for s in records:
        if not isinstance(s.family,Family) or not isinstance(s.kind,Kind) or not isinstance(s.addition,Addition):
            raise LineageError('Lineage category must be a declared enum.')
        if not s.key or any(p not in mapping for p in s.parents+s.optional_parents):
            raise LineageError('Empty identifier or unregistered parent.')
        if len(set(s.parents+s.optional_parents)) != len(s.parents+s.optional_parents):
            raise LineageError('Duplicate parent.')
    visited, pending = set(), set()
    def visit(key):
        if key in pending:
            raise LineageError('Cyclic evidence ancestry: '+key)
        if key in visited:
            return
        pending.add(key)
        for parent in mapping[key].parents+mapping[key].optional_parents:
            visit(parent)
        pending.remove(key); visited.add(key)
    for key in sorted(mapping):
        visit(key)
    return MappingProxyType(mapping)


REGISTRY = validate_registry(_SPECS)


def numerical_restatement_sources(key, pattern):
    """Pattern-specific equivalence, not a family-wide suppression rule.

    The fragment/partial fallback in classify_boundary_convergence only tests
    existing overlap thresholds. The contour-positive branch adds measured
    topology and deliberately is NOT in this contract. Cross and boundary are
    sibling consumers of the same overlap, not independent extractions.
    """
    if key == 'boundary' and pattern in {
        'possible_boundary_fragment_convergence', 'partial_boundary_convergence',
    }:
        return ('cross_signal',)
    return ()


def build_lineage(sections, *, context=None, registry=REGISTRY):
    """Snapshot status/ancestry only; never retain summaries, details or arrays.

    Inconclusive detector interpretation can still provide a measured upstream
    feature (e.g. ELA/noise maps). It has no status-weighted scoring credit.
    Missing optional payloads do not invalidate a detector's own measurements.
    """
    registry = validate_registry(tuple(registry.values()))
    results = {}
    def build(key):
        if key in results:
            return results[key]
        spec = registry.get(key)
        section = sections.get(key)
        status = getattr(section,'status','not_run')
        available = status in ACTIVE or status == 'inconclusive'
        if key == 'scene_context':
            status = 'available' if context is not None else 'not_run'
            available = context is not None
        if spec is None:
            record = LineageRecord('evidence:'+key,'unregistered',Family.UNKNOWN,(),(),(),(),(),status,
                available,False,Kind.DERIVED,Addition.INTERPRETATION,known=False)
        else:
            parents = {p:build(p) for p in spec.parents+spec.optional_parents}
            missing = tuple('evidence:'+p for p in spec.parents if not parents[p].available or parents[p].missing_dependencies)
            ancestry = {'measurement:'+m for m in spec.measurements} if available else set()
            for p,record in parents.items():
                if record.available:
                    ancestry.update(record.measurement_ancestry)
            record = LineageRecord('evidence:'+key,spec.detector,spec.family,tuple(sorted(ancestry)),
                tuple('evidence:'+p for p in spec.parents),tuple('evidence:'+p for p in spec.optional_parents),
                missing,spec.hypotheses,status,available,status in ACTIVE and not missing,
                spec.kind,spec.addition,spec.overlap_groups)
        results[key]=record
        return record
    for key in sorted(set(registry)|set(sections)):
        build(key)
    return tuple(sorted(results.values(),key=lambda r:r.evidence_id))


def lineage_to_json(records):
    return [asdict(record) for record in sorted(records,key=lambda r:r.evidence_id)]


def lineage_from_json(items):
    """Restore validated immutable records, without accepting payload fields."""
    result=[]
    fields=set(LineageRecord.__dataclass_fields__)
    tuple_fields=('measurement_ancestry','direct_dependencies','optional_dependencies','missing_dependencies','hypotheses','overlap_groups')
    for item in items:
        if set(item)!=fields:
            raise LineageError('Serialized lineage fields do not match version 2b2.')
        values=dict(item)
        for name in tuple_fields:
            if not isinstance(values[name],(list,tuple)):
                raise LineageError('Serialized references must be lists.')
            values[name]=tuple(values[name])
        try:
            for name,enum in (('family',Family),('kind',Kind),('addition',Addition)):
                values[name]=enum(values[name])
        except ValueError as exc:
            raise LineageError('Unknown serialized lineage category.') from exc
        result.append(LineageRecord(**values))
    nodes={r.evidence_id:r for r in result}
    if len(nodes)!=len(result):
        raise LineageError('Duplicate serialized evidence identifier.')
    visited=set()
    def visit(key, pending=()):
        if key not in nodes or key in pending:
            raise LineageError('Missing or cyclic serialized lineage parent.')
        if key in visited: return
        for parent in nodes[key].direct_dependencies+nodes[key].optional_dependencies:
            visit(parent,pending+(key,))
        visited.add(key)
    for key in nodes: visit(key)
    return tuple(sorted(result,key=lambda r:r.evidence_id))
