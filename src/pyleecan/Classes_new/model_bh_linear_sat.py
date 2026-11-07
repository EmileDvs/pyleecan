# Experimental dataclass generated from Generator/ClassesRef/Material/ModelBH_linear_sat.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .model_bh import ModelBH


@dataclass(eq=False)
class ModelBH_linear_sat(ModelBH):
    """Abstract class for BH curve model

    Attributes
    ----------
    Bs : float or None
        Saturation flux density
        Unit: T; Default: None
    mu_a : float or None
        Linear permeability
        Default: None
    param1 : float
        Init value for Bs for fitting algorithm
        Default: 1.89
    param2 : float
        Init value for mu_a for fitting algorithm
        Default: 240
    """

    Bs: float | None = None
    """Saturation flux density"""
    mu_a: float | None = None
    """Linear permeability"""
    param1: float = 1.89
    """Init value for Bs for fitting algorithm"""
    param2: float = 240
    """Init value for mu_a for fitting algorithm"""

    # Inlined from Methods.Material.ModelBH_linear_sat.BH_func
    def BH_func(self, H, Bs, mu_a):
        """
        Return the B from H according to piecewise linear saturated model.

        Parameters
        ----------
        self : ModelBH_linear_sat
            a ModelBH_linear_sat object

        Returns
        -------
        B: numpy.ndarray
            B(H) values

        """
        B = mu_a * H

        if isinstance(B, np.ndarray):
            B[np.argwhere(B >= Bs)] = Bs
        elif B >= Bs:
            B = Bs

        return B

    # Inlined from Methods.Material.ModelBH_linear_sat.get_BH
    def get_BH(self):
        """
        Return the B(H) curve of the material according to Langevin model.

        Parameters
        ----------
        self : ModelBH
            a ModelBH object

        Returns
        -------
        BH: numpy.ndarray
            B(H) values (two colums matrix: H and B(H))

        """

        H0 = 1
        Bmax = self.Bmax
        if self.Bs is not None and self.mu_a is not None:
            if Bmax is not None:
                delta = self.delta
                Hmax = H0
                iteration = 0
                new_B = 0
                while new_B < Bmax and iteration < 1000:
                    Hmax += delta
                    iteration += 1
                    new_B = self.BH_func(Hmax, self.Bs, self.mu_a)
            else:
                Hmax = self.Hmax

            if Hmax is not None:
                H = np.linspace(H0, Hmax, 200)
                B = self.BH_func(H, self.Bs, self.mu_a)

                BH = np.zeros((len(H), 2))
                BH[:, 0] = H
                BH[:, 1] = B

                return BH
