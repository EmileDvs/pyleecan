# Experimental dataclass generated from Generator/ClassesRef/Material/MatElectrical.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class MatElectrical(PyleecanClass):
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

    rho: float = 0
    """Resistivity at 20 deg C"""
    epsr: float = 1
    """Relative dielectric constant"""
    alpha: float = 0
    """Thermal resistivity coefficient"""

    # Inlined from Methods.Material.MatElectrical.get_conductivity
    def get_conductivity(self, T_op=None, T_ref=20):
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
    def get_resistivity(self, T_op=None, T_ref=20):
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
