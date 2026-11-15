# Experimental pydantic model generated from Generator/ClassesRef/Output/OutForce.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._pyleecan_model import PyleecanModel
from ..mesh.mesh_solution import MeshSolution
from ..scidatatool.data import Data
from ..scidatatool.data_time import DataTime
from ..scidatatool.vector_field import VectorField


class OutForce(PyleecanModel):
    """Gather the structural module outputs

    Attributes
    ----------
    axes_dict : {Data} or None
        Dict containing axes data used for Force
        Default: None
    AGSF : VectorField or None
        Air Gap Surface Force (mainly computed with Maxwell stress tensor)
        Unit: N.m^2; Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Force"
    Rag : float or None
        Radius value for air-gap computation
        Default: None
    meshsolution : MeshSolution or None
        Force computed on a mesh
        Default: None
    """

    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data used for Force"""
    AGSF: VectorField | None = Field(default=None, json_schema_extra={"unit": "N.m^2"})
    """Air Gap Surface Force (mainly computed with Maxwell stress tensor)"""
    logger_name: str = "Pyleecan.Force"
    """Name of the logger to use"""
    Rag: float | None = None
    """Radius value for air-gap computation"""
    meshsolution: MeshSolution | None = None
    """Force computed on a mesh"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Output.OutForce.store
    def store(self, out_dict, axes_dict):
        """Store the standard outputs of Force that are temporarily in out_dict as arrays into OutForce as Data object

        Parameters
        ----------
        self: OutForce
            the OutForce object to update
        out_dict : dict
            Dict containing all force quantities
        axes_dict: {Data}
            Dict of axes used for magnetic calculation

        """

        # Store axes_dict
        self.axes_dict = axes_dict

        # Store air-gap surface force as VectorField object

        # Axes for each component
        axis_list = [axes_dict["time"], axes_dict["angle"]]

        # Create VectorField with empty components
        self.AGSF = VectorField(
            name="Air gap Surface Force",
            symbol="AGSF",
        )
        # Radial air-gap surface force component
        if "AGSF_r" in out_dict:
            self.AGSF.components["radial"] = DataTime(
                name="Radial air gap surface force",
                unit="N/m^2",
                symbol="AGSF_r",
                axes=axis_list,
                values=out_dict.pop("AGSF_r"),
            )
        # Tangential air-gap surface force component
        if "AGSF_t" in out_dict:
            self.AGSF.components["tangential"] = DataTime(
                name="Tangential air gap surface force",
                unit="N/m^2",
                symbol="AGSF_t",
                axes=axis_list,
                values=out_dict.pop("AGSF_t"),
            )
        # Axial air-gap surface force component
        if "AGSF_z" in out_dict:
            self.AGSF.components["axial"] = DataTime(
                name="Axial air gap surface force",
                unit="N/m^2",
                symbol="AGSF_z",
                axes=axis_list,
                values=out_dict.pop("AGSF_z"),
            )

        if "Rag" in out_dict:
            self.Rag = out_dict.pop("Rag")

        if "meshsolution" in out_dict:
            self.meshsolution = out_dict.pop("meshsolution")
