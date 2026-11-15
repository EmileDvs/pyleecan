# Experimental pydantic model generated from Generator/ClassesRef/Material/MatStructural.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel


class MatStructural(LegacyModel):
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

    rho: float = Field(default=7650, ge=0, json_schema_extra={"unit": "kg/m^3"})
    """mass per unit volume [kg/m3]"""
    Ex: float = Field(default=215000000000.0, ge=0, json_schema_extra={"unit": "Pa"})
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    Ey: float = Field(default=215000000000.0, ge=0, json_schema_extra={"unit": "Pa"})
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    Ez: float = Field(default=80000000000, ge=0, json_schema_extra={"unit": "Pa"})
    """equivalent Young modulus (XY is lamination plane, Z is rotation axis)"""
    nu_xy: float = Field(default=0.3, ge=0)
    """equivalent Poisson ratio in the XY plane (XY is lamination plane, Z is rotation axis)"""
    nu_xz: float = Field(default=0.03, ge=0)
    """equivalent Poisson ratio in the XZ plane (XY is lamination plane, Z is rotation axis)"""
    nu_yz: float = Field(default=0.03, ge=0)
    """equivalent Poisson ratio in the YZ plane (XY is lamination plane, Z is rotation axis)"""
    Gxz: float = Field(default=2000000000, ge=0, json_schema_extra={"unit": "Pa"})
    """shear modulus in XY plane (XY is lamination plane, Z is rotation axis)"""
    Gxy: float = Field(default=0, ge=0, json_schema_extra={"unit": "Pa"})
    """shear modulus in XZ plane (XY is lamination plane, Z is rotation axis)"""
    Gyz: float = Field(default=2000000000, ge=0, json_schema_extra={"unit": "Pa"})
    """shear modulus in YZ plane (XY is lamination plane, Z is rotation axis)"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
