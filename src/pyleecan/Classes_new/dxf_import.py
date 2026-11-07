# Experimental dataclass generated from Generator/ClassesRef/Simulation/DXFImport.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from ._pyleecan_class import PyleecanClass
from .magnetics import Magnetics
from .surf_line import SurfLine


@dataclass(eq=False)
class DXFImport(PyleecanClass):
    """Use a DXF to define a lamination

    Attributes
    ----------
    file_path : str or None
        Path to the DXF file to import
        Default: None
    surf_dict : dict or None
        dictionary to assign the surfaces: key=complex reference point coordinate, value=label of the surface
        Default: {}
    BC_list : list
        List of tuple to apply boundary conditions (complex reference point coordinate, is_arc, label of the BC to apply)
        Default: []
    """

    file_path: str | None = None
    """Path to the DXF file to import"""
    surf_dict: dict[str, Any] | None = field(default_factory=dict)
    """dictionary to assign the surfaces: key=complex reference point coordinate, value=label of the surface"""
    BC_list: list[Any] = field(default_factory=list)
    """List of tuple to apply boundary conditions (complex reference point coordinate, is_arc, label of the BC to apply)"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Magnetics,)):
            raise TypeError(
                "DXFImport parent must be an instance of Magnetics, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Simulation.DXFImport.get_surfaces
    def get_surfaces(self):
        """Convert surf_dict to a list of surfaces without lines"""

        surf_list = []

        for key, value in self.surf_dict.items():
            surf_list.append(SurfLine(line_list=[], point_ref=key, label=value))

        return surf_list
