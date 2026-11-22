# Experimental pydantic model generated from Generator/ClassesRef/Machine/Magnet.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from ..material.material import Material


class Magnet(LegacyModel):
    """Magnet class

    Attributes
    ----------
    mat_type : Material or None
        The Magnet material
        Default: Material()
    type_magnetization : int
        Permanent magnet magnetization type: 0 for radial, 1 for parallel, 2 for Hallbach, 3 Tangential
        Default: 0; Minimum: 0; Maximum: 3
    Lmag : float
        Magnet axial length
        Default: 0.95; Minimum: 0
    Nseg : int
        Number of segments
        Default: 1; Minimum: 1
    """

    mat_type: Material = Field(default_factory=lambda: Material())
    """The Magnet material"""
    type_magnetization: int = Field(default=0, ge=0, le=3)
    """Permanent magnet magnetization type: 0 for radial, 1 for parallel, 2 for Hallbach, 3 Tangential"""
    Lmag: float = Field(default=0.95, ge=0)
    """Magnet axial length"""
    Nseg: int = Field(default=1, ge=1)
    """Number of segments"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""
