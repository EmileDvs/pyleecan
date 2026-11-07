# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Normalization.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .data import Data


@dataclass(eq=False)
class Normalization(PyleecanClass):
    """Abstract class for normalizations

    Attributes
    ----------
    unit : str
        Normalization must be applied on axis values in this unit
        Default: "SI"
    """

    unit: str = "SI"
    """Normalization must be applied on axis values in this unit"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Data,)):
            raise TypeError(
                "Normalization parent must be an instance of Data, or None; "
                + f"got {type(parent).__name__}"
            )
