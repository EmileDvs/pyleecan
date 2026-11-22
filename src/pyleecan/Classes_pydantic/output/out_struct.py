# Experimental pydantic model generated from Generator/ClassesRef/Output/OutStruct.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from ..mesh.mesh_solution import MeshSolution
from ..scidatatool.data import Data


class OutStruct(LegacyModel):
    """Gather the structural module outputs

    Attributes
    ----------
    axes_dict : {Data} or None
        Dict containing axes data used for Structural
        Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Structural"
    meshsolution : MeshSolution or None
        FEA software mesh and solution
        Default: MeshSolution()
    FEA_dict : dict or None
        dictionary containing the main FEA parameter
        Default: None
    """

    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data used for Structural"""
    logger_name: str = "Pyleecan.Structural"
    """Name of the logger to use"""
    meshsolution: MeshSolution = Field(default_factory=lambda: MeshSolution())
    """FEA software mesh and solution"""
    FEA_dict: dict[str, Any] | None = None
    """dictionary containing the main FEA parameter"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""
