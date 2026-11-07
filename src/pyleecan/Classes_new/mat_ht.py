# Experimental dataclass generated from Generator/ClassesRef/Material/MatHT.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .material import Material


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

    lambda_x: float = 1
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    lambda_y: float = 1
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    lambda_z: float = 1
    """thermal conductivity (XY is lamination plane, Z is rotation axis)"""
    Cp: float = 1
    """specific heat capacity"""
    alpha: float = 0
    """thermal expansion coefficient"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Material,)):
            raise TypeError(
                "MatHT parent must be an instance of Material, or None; "
                + f"got {type(parent).__name__}"
            )
