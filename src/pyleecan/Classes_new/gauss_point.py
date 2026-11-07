# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/GaussPoint.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .element_mat import ElementMat


@dataclass(eq=False)
class GaussPoint(PyleecanClass):
    """Store set of gauss points

    Attributes
    ----------
    """

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (ElementMat,)):
            raise TypeError(
                "GaussPoint parent must be an instance of ElementMat, or None; "
                + f"got {type(parent).__name__}"
            )
