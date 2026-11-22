# Experimental pydantic model generated from Generator/ClassesRef/Material/Material.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from .mat_economical import MatEconomical
from .mat_electrical import MatElectrical
from .mat_ht import MatHT
from .mat_magnetics import MatMagnetics
from .mat_structural import MatStructural


class Material(LegacyModel):
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
    path : str
        Path to the material file
        Default: ""
    """

    name: str = "Material"
    """name of the material"""
    is_isotropic: bool = False
    """If Isotropic, uniformity in all orientations"""
    elec: MatElectrical = Field(default_factory=lambda: MatElectrical())
    """Electrical properties of the material"""
    mag: MatMagnetics = Field(default_factory=lambda: MatMagnetics())
    """Magnetic properties of the material"""
    struct: MatStructural = Field(default_factory=lambda: MatStructural())
    """Structural properties of the material"""
    HT: MatHT = Field(default_factory=lambda: MatHT())
    """Heat Transfer properties of the material"""
    eco: MatEconomical = Field(default_factory=lambda: MatEconomical())
    """Economical properties of the material"""
    desc: str = "Material description"
    """material description"""
    path: str = ""
    """Path to the material file"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
