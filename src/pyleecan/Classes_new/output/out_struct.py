# Experimental dataclass generated from Generator/ClassesRef/Output/OutStruct.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any, ClassVar

from .._legacy_class import LegacyClass
from ..mesh.mesh_solution import MeshSolution
from ..scidatatool.data import Data


@dataclass(eq=False)
class OutStruct(LegacyClass):
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
    meshsolution: MeshSolution | None = field(
        default_factory=lambda: MeshSolution(),
        metadata={"default_class": "MeshSolution"},
    )
    """FEA software mesh and solution"""
    FEA_dict: dict[str, Any] | None = None
    """dictionary containing the main FEA parameter"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""
