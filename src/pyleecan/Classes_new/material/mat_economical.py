# Experimental dataclass generated from Generator/ClassesRef/Material/MatEconomical.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from .._legacy_class import LegacyClass


@dataclass(eq=False)
class MatEconomical(LegacyClass):
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

    cost_unit: float = field(default=0.127, metadata={"unit": "unit/kg", "min": 0})
    """Cost of one kilo of material"""
    unit_name: str = "$"
    """Name of the unit"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
