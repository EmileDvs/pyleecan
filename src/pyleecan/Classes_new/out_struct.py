# Experimental dataclass generated from Generator/ClassesRef/Output/OutStruct.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from ._pyleecan_class import PyleecanClass
from .data import Data
from .mesh_solution import MeshSolution
from .output import Output


@dataclass(eq=False)
class OutStruct(PyleecanClass):
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
        Default: None
    FEA_dict : dict or None
        dictionary containing the main FEA parameter
        Default: {}
    """

    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data used for Structural"""
    logger_name: str = "Pyleecan.Structural"
    """Name of the logger to use"""
    meshsolution: MeshSolution | None = None
    """FEA software mesh and solution"""
    FEA_dict: dict[str, Any] | None = field(default_factory=dict)
    """dictionary containing the main FEA parameter"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Output,)):
            raise TypeError(
                "OutStruct parent must be an instance of Output, or None; "
                + f"got {type(parent).__name__}"
            )
