# Experimental pydantic model generated from Generator/ClassesRef/Simulation/DXFImport.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from ..geometry.surf_line import SurfLine


class DXFImport(LegacyModel):
    """Use a DXF to define a lamination

    Attributes
    ----------
    file_path : str
        Path to the DXF file to import
        Default: ""
    surf_dict : dict or None
        dictionary to assign the surfaces: key=complex reference point coordinate, value=label of the surface
        Default: {}
    BC_list : list
        List of tuple to apply boundary conditions (complex reference point coordinate, is_arc, label of the BC to apply)
        Default: []
    """

    file_path: str = ""
    """Path to the DXF file to import"""
    surf_dict: dict[str, Any] = Field(default_factory=dict)
    """dictionary to assign the surfaces: key=complex reference point coordinate, value=label of the surface"""
    BC_list: list[Any] = Field(default_factory=list)
    """List of tuple to apply boundary conditions (complex reference point coordinate, is_arc, label of the BC to apply)"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.DXFImport.get_surfaces
    def get_surfaces(self):
        """Convert surf_dict to a list of surfaces without lines"""

        surf_list = []

        for key, value in self.surf_dict.items():
            surf_list.append(SurfLine(line_list=[], point_ref=key, label=value))

        return surf_list
