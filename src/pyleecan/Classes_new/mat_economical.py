# Experimental dataclass generated from Generator/ClassesRef/Material/MatEconomical.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .material import Material


@dataclass(eq=False)
class MatEconomical(PyleecanClass):
    """material ecomomical properties

    Attributes
    ----------
    cost_unit : float
        Cost of one kilo of material
        Unit: unit/kg; Default: 0.127; Minimum: 0
    unit_name : str
        Name of the unit
        Default: "$"
    """

    cost_unit: float = 0.127
    """Cost of one kilo of material"""
    unit_name: str = "$"
    """Name of the unit"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Material,)):
            raise TypeError(
                "MatEconomical parent must be an instance of Material, or None; "
                + f"got {type(parent).__name__}"
            )
