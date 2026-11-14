# Experimental dataclass generated from Generator/ClassesRef/Material/MatHT.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class MatHT(PyleecanClass):
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

    lambda_x: float = field(default=1, metadata={"unit": "W/K", "min": 0})
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    lambda_y: float = field(default=1, metadata={"unit": "W/K", "min": 0})
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    lambda_z: float = field(default=1, metadata={"unit": "W/K", "min": 0})
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    Cp: float = field(default=1, metadata={"unit": "W/kg/K", "min": 0})
    """specific heat capacity"""
    alpha: float = field(default=0, metadata={"min": 0})
    """thermal expansion coefficient"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
