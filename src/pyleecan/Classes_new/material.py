# Experimental dataclass generated from Generator/ClassesRef/Material/Material.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .conductor import Conductor
from .frame import Frame
from .hole import Hole
from .lamination import Lamination
from .magnet import Magnet
from .mat_economical import MatEconomical
from .mat_electrical import MatElectrical
from .mat_ht import MatHT
from .mat_magnetics import MatMagnetics
from .mat_structural import MatStructural
from .notch import Notch
from .shaft import Shaft
from .slot import Slot


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
        Default: None
    mag : MatMagnetics or None
        Magnetic properties of the material
        Default: None
    struct : MatStructural or None
        Structural properties of the material
        Default: None
    HT : MatHT or None
        Heat Transfer properties of the material
        Default: None
    eco : MatEconomical or None
        Economical properties of the material
        Default: None
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
    elec: MatElectrical | None = None
    """Electrical properties of the material"""
    mag: MatMagnetics | None = None
    """Magnetic properties of the material"""
    struct: MatStructural | None = None
    """Structural properties of the material"""
    HT: MatHT | None = None
    """Heat Transfer properties of the material"""
    eco: MatEconomical | None = None
    """Economical properties of the material"""
    desc: str = "Material description"
    """material description"""
    path: str | None = None
    """Path to the material file"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Conductor,
                Frame,
                Hole,
                Lamination,
                Magnet,
                Notch,
                Shaft,
                Slot,
            ),
        ):
            raise TypeError(
                "Material parent must be an instance of Conductor or Frame or Hole or Lamination or Magnet or Notch or Shaft or Slot, or None; "
                + f"got {type(parent).__name__}"
            )
