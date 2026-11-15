# Experimental pydantic model generated from Generator/ClassesRef/Material/MatEconomical.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._pyleecan_model import PyleecanModel


class MatEconomical(PyleecanModel):
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

    cost_unit: float = Field(default=0.127, ge=0, json_schema_extra={"unit": "unit/kg"})
    """Cost of one kilo of material"""
    unit_name: str = "$"
    """Name of the unit"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
