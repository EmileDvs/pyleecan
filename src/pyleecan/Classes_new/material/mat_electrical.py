# Experimental dataclass generated from Generator/ClassesRef/Material/MatElectrical.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np

from .._legacy_class import LegacyClass


@dataclass(eq=False)
class MatElectrical(LegacyClass):
    """material electrical properties

    Attributes
    ----------
    rho : float
        Resistivity at 20 deg C
        Unit: ohm.m; Default: 0; Minimum: 0
    epsr : float
        Relative dielectric constant
        Default: 1; Minimum: 0
    alpha : float
        Thermal resistivity coefficient
        Unit: 1/K; Default: 0; Minimum: 0
    """

    rho: float = field(default=0, metadata={"unit": "ohm.m", "min": 0})
    """Resistivity at 20 deg C"""
    epsr: float = field(default=1, metadata={"min": 0})
    """Relative dielectric constant"""
    alpha: float = field(default=0, metadata={"unit": "1/K", "min": 0})
    """Thermal resistivity coefficient"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Material.MatElectrical.get_conductivity
    def get_conductivity(self, T_op: float | None = None, T_ref: float = 20) -> float:
        """Get conductivity for given temperature T_op

        Parameters
        ----------
        self : MatElectrical
            a MatElectrical object
        T_op: float
            Material operational temperature [degC]
        T_ref: float
            Material reference temperature [degC]

        Returns
        -------
        sigma: float
            Electric conductivity [S]
        """

        if T_op is None:
            T_op = T_ref

        if self.rho is None:
            raise Exception("Cannot calculate conductivity if rh0 is None")

        if self.rho == 0:
            sigma = np.inf

        else:
            rho = self.get_resistivity(T_op, T_ref)
            sigma = 1 / rho

        return sigma

    # Inlined from Methods.Material.MatElectrical.get_resistivity
    def get_resistivity(self, T_op: float | None = None, T_ref: float = 20) -> float:
        """Get resistivity for given temperature T_op

        Parameters
        ----------
        self : MatElectrical
            a MatElectrical object
        T_op: float
            Material operational temperature [degC]
        T_ref: float
            Material reference temperature [degC]

        Returns
        -------
        rho: float
            Electric resistivity [ohm.m]
        """

        if T_op is None:
            T_op = T_ref

        if self.rho is None:
            raise Exception("Cannot calculate resistivity if rho is None")

        # Update resistivity
        rho = self.rho * (1 + self.alpha * (T_op - T_ref))

        return rho
