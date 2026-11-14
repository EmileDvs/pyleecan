# Experimental dataclass generated from Generator/ClassesRef/Material/MatStructural.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class MatStructural(PyleecanClass):
    """Material Structural properties

    Attributes
    ----------
    rho : float
        mass per unit volume [kg/m3]
        Unit: kg/m^3; Default: 7650; Minimum: 0
    Ex : float
        equivalent Young modulus (XY is lamination plane, Z is rotation axis)
        Unit: Pa; Default: 215000000000.0; Minimum: 0
    Ey : float
        equivalent Young modulus (XY is lamination plane, Z is rotation axis)
        Unit: Pa; Default: 215000000000.0; Minimum: 0
    Ez : float
        equivalent Young modulus (XY is lamination plane, Z is rotation axis)
        Unit: Pa; Default: 80000000000; Minimum: 0
    nu_xy : float
        equivalent Poisson ratio in the XY plane (XY is lamination plane, Z is rotation axis)
        Default: 0.3; Minimum: 0
    nu_xz : float
        equivalent Poisson ratio in the XZ plane (XY is lamination plane, Z is rotation axis)
        Default: 0.03; Minimum: 0
    nu_yz : float
        equivalent Poisson ratio in the YZ plane (XY is lamination plane, Z is rotation axis)
        Default: 0.03; Minimum: 0
    Gxz : float
        shear modulus in XY plane (XY is lamination plane, Z is rotation axis)
        Unit: Pa; Default: 2000000000; Minimum: 0
    Gxy : float
        shear modulus in XZ plane (XY is lamination plane, Z is rotation axis)
        Unit: Pa; Default: 0; Minimum: 0
    Gyz : float
        shear modulus in YZ plane (XY is lamination plane, Z is rotation axis)
        Unit: Pa; Default: 2000000000; Minimum: 0
    """

    rho: float = field(default=7650, metadata={"unit": "kg/m^3", "min": 0})
    """mass per unit volume [kg/m3]"""
    Ex: float = field(default=215000000000.0, metadata={"unit": "Pa", "min": 0})
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    Ey: float = field(default=215000000000.0, metadata={"unit": "Pa", "min": 0})
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    Ez: float = field(default=80000000000, metadata={"unit": "Pa", "min": 0})
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    nu_xy: float = field(default=0.3, metadata={"min": 0})
    """equivalent Poisson ratio in the XY plane (XY is lamination plane, Z is rotation axis)"""
    nu_xz: float = field(default=0.03, metadata={"min": 0})
    """equivalent Poisson ratio in the XZ plane (XY is lamination plane, Z is rotation axis)"""
    nu_yz: float = field(default=0.03, metadata={"min": 0})
    """equivalent Poisson ratio in the YZ plane (XY is lamination plane, Z is rotation axis)"""
    Gxz: float = field(default=2000000000, metadata={"unit": "Pa", "min": 0})
    """shear modulus in XY plane (XY is lamination plane, Z is rotation axis)"""
    Gxy: float = field(default=0, metadata={"unit": "Pa", "min": 0})
    """shear modulus in XZ plane (XY is lamination plane, Z is rotation axis)"""
    Gyz: float = field(default=2000000000, metadata={"unit": "Pa", "min": 0})
    """shear modulus in YZ plane (XY is lamination plane, Z is rotation axis)"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
