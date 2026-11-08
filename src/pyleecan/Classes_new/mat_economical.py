# Experimental dataclass generated from Generator/ClassesRef/Material/MatEconomical.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass


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
