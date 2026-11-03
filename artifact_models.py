"""Immutable UI-4 artifact contracts. No scoring or forensic inference."""
from dataclasses import dataclass
from enum import Enum
import math


class Registration(str, Enum):
    REGISTERED = 'REGISTERED'
    TRANSFORMABLE = 'TRANSFORMABLE'
    UNREGISTERED = 'UNREGISTERED'
    UNKNOWN = 'UNKNOWN'
    NOT_APPLICABLE = 'NOT_APPLICABLE'


@dataclass(frozen=True)
class SpatialTransform:
    """Source edge coordinates -> artifact edge coordinates, affine 2×3.

    Pixel (i,j) has center (i+.5,j+.5). Bounds use [0,width] × [0,height].
    """
    a: float = 1
    b: float = 0
    c: float = 0
    d: float = 1
    tx: float = 0
    ty: float = 0

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.a,self.b,self.c,self.d,self.tx,self.ty)) or abs(self.a*self.d-self.b*self.c) < 1e-12:
            raise ValueError('Invalid or singular spatial transform')

    def map(self, x, y):
        return self.a*x + self.c*y + self.tx, self.b*x + self.d*y + self.ty

    def inverse(self):
        determinant = self.a*self.d - self.b*self.c
        a,b,c,d = self.d/determinant,-self.b/determinant,-self.c/determinant,self.a/determinant
        return SpatialTransform(a,b,c,d,-a*self.tx-c*self.ty,-b*self.tx-d*self.ty)


@dataclass(frozen=True)
class ForensicArtifact:
    artifact_id: str
    session_id: str
    analysis_id: str | None
    result_id: str
    analysis_revision: int
    source_sha256: str | None
    detector_id: str
    label: str
    artifact_type: str
    path: str | None
    width: int | None
    height: int | None
    sha256: str | None
    registration: Registration
    transform: SpatialTransform | None
    source_dimensions: tuple[int, int] | None
    source_orientation: int | None
    reliability: str | None
    evidence_ids: tuple[str, ...]
    hypothesis_ids: tuple[str, ...]
    stage_status: str | None
    available: bool
    reason: str | None
    description: str
    details_json: str
    overlay_legend: str | None = None

    @property
    def can_sync(self):
        return (self.available and self.registration in (Registration.REGISTERED, Registration.TRANSFORMABLE)
                and self.transform is not None and self.source_dimensions is not None)

    @property
    def can_overlay(self):
        return self.can_sync and bool(self.overlay_legend)
