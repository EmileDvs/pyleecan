# Experimental dataclass generated from Generator/ClassesRef/Material/Material.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from ._pyleecan_class import PyleecanClass
from .mat_economical import MatEconomical
from .mat_electrical import MatElectrical
from .mat_ht import MatHT
from .mat_magnetics import MatMagnetics
from .mat_structural import MatStructural


@dataclass(eq=False)
class Material(PyleecanClass):
    """Material

    Attributes
    ----------
    name : str
        name of the material
        Default: "Material"
    is_isotropic : bool
        If Isotropic, uniformity in all orientations
        Default: False
    elec : MatElectrical or None
        Electrical properties of the material
        Default: MatElectrical()
    mag : MatMagnetics or None
        Magnetic properties of the material
        Default: MatMagnetics()
    struct : MatStructural or None
        Structural properties of the material
        Default: MatStructural()
    HT : MatHT or None
        Heat Transfer properties of the material
        Default: MatHT()
    eco : MatEconomical or None
        Economical properties of the material
        Default: MatEconomical()
    desc : str
        material description
        Default: "Material description"
    path : str or None
        Path to the material file
        Default: None
    """

    name: str = "Material"
    """name of the material"""
    is_isotropic: bool = False
    """If Isotropic, uniformity in all orientations"""
    elec: MatElectrical | None = field(
        default_factory=lambda: MatElectrical(),
        metadata={"default_class": "MatElectrical"},
    )
    """Electrical properties of the material"""
    mag: MatMagnetics | None = field(
        default_factory=lambda: MatMagnetics(),
        metadata={"default_class": "MatMagnetics"},
    )
    """Magnetic properties of the material"""
    struct: MatStructural | None = field(
        default_factory=lambda: MatStructural(),
        metadata={"default_class": "MatStructural"},
    )
    """Structural properties of the material"""
    HT: MatHT | None = field(
        default_factory=lambda: MatHT(), metadata={"default_class": "MatHT"}
    )
    """Heat Transfer properties of the material"""
    eco: MatEconomical | None = field(
        default_factory=lambda: MatEconomical(),
        metadata={"default_class": "MatEconomical"},
    )
    """Economical properties of the material"""
    desc: str = "Material description"
    """material description"""
    path: str | None = None
    """Path to the material file"""
