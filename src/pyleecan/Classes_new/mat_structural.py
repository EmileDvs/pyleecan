# Experimental dataclass generated from Generator/ClassesRef/Material/MatStructural.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

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

    rho: float = 7650
    """mass per unit volume [kg/m3]"""
    Ex: float = 215000000000.0
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    Ey: float = 215000000000.0
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    Ez: float = 80000000000
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    nu_xy: float = 0.3
    """equivalent Poisson ratio in the XY plane (XY is lamination plane, Z is rotation axis)"""
    nu_xz: float = 0.03
    """equivalent Poisson ratio in the XZ plane (XY is lamination plane, Z is rotation axis)"""
    nu_yz: float = 0.03
    """equivalent Poisson ratio in the YZ plane (XY is lamination plane, Z is rotation axis)"""
    Gxz: float = 2000000000
    """shear modulus in XY plane (XY is lamination plane, Z is rotation axis)"""
    Gxy: float = 0
    """shear modulus in XZ plane (XY is lamination plane, Z is rotation axis)"""
    Gyz: float = 2000000000
    """shear modulus in YZ plane (XY is lamination plane, Z is rotation axis)"""
