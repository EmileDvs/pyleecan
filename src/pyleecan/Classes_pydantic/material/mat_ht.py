# Experimental pydantic model generated from Generator/ClassesRef/Material/MatHT.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel


class MatHT(LegacyModel):
    """Material Heat Transfer properties

    Attributes
    ----------
    lambda_x : float
        thermal conductivity (XY is lamination plane, Z is rotation axis)
        Unit: W/K; Default: 1; Minimum: 0
    lambda_y : float
        thermal conductivity (XY is lamination plane, Z is rotation axis)
        Unit: W/K; Default: 1; Minimum: 0
    lambda_z : float
        thermal conductivity (XY is lamination plane, Z is rotation axis)
        Unit: W/K; Default: 1; Minimum: 0
    Cp : float
        specific heat capacity
        Unit: W/kg/K; Default: 1; Minimum: 0
    alpha : float
        thermal expansion coefficient
        Default: 0; Minimum: 0
    """

    lambda_x: float = Field(default=1, ge=0, json_schema_extra={"unit": "W/K"})
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    lambda_y: float = Field(default=1, ge=0, json_schema_extra={"unit": "W/K"})
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    lambda_z: float = Field(default=1, ge=0, json_schema_extra={"unit": "W/K"})
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    Cp: float = Field(default=1, ge=0, json_schema_extra={"unit": "W/kg/K"})
    """specific heat capacity"""
    alpha: float = Field(default=0, ge=0)
    """thermal expansion coefficient"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
