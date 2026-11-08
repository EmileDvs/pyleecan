# Experimental dataclass generated from Generator/ClassesRef/Machine/Magnet.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .material import Material


@dataclass(eq=False)
class Magnet(PyleecanClass):
    """Magnet class

    Attributes
    ----------
    mat_type : Material or None
        The Magnet material
        Default: None
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

    mat_type: Material | None = None
    """The Magnet material"""
    type_magnetization: int = 0
    """Permanent magnet magnetization type: 0 for radial, 1 for parallel, 2 for Hallbach, 3 Tangential"""
    Lmag: float = 0.95
    """Magnet axial length"""
    Nseg: int = 1
    """Number of segments"""
