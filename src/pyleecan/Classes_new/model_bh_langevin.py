# Experimental dataclass generated from Generator/ClassesRef/Material/ModelBH_Langevin.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from math import isnan

import numpy as np

from .model_bh import ModelBH


@dataclass(eq=False)
class ModelBH_Langevin(ModelBH):
    """Abstract class for BH curve model

    Attributes
    ----------
    Bs : float or None
        To enforc Saturation flux density
        Unit: T; Default: None
    a : float or None
        To enforce Saturation parameter a
        Default: None
    param1 : float
        Init value for Bs for fitting algorithm
        Default: 1.89
    param2 : float
        Init value for a for fitting algorithm
        Default: 240
    """

    Bs: float | None = None
    """To enforc Saturation flux density"""
    a: float | None = None
    """To enforce Saturation parameter a"""
    param1: float = 1.89
    """Init value for Bs for fitting algorithm"""
    param2: float = 240
    """Init value for a for fitting algorithm"""

    # Inlined from Methods.Material.ModelBH_Langevin.BH_func
    def BH_func(self, H, Bs, a):
        """
        Return the B from H according to Langevin model.

        Parameters
        ----------
        self : ModelBH_Langevin
            a ModelBH_Langevin object

        Returns
        -------
        B: numpy.ndarray
            B(H) values

        """
        B = Bs * (np.cosh(H / a) / np.sinh(H / a) - a / H)

        if isinstance(B, np.ndarray):
            B[np.argwhere(np.isnan(B))] = Bs
            B[np.argwhere(H == 0)] = 0
        elif isnan(B):
            if H == 0:
                B = 0
            else:
                B = Bs

        return B

    # Inlined from Methods.Material.ModelBH_Langevin.get_BH
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
        if self.Bs is not None and self.a is not None:
            if Bmax is not None:
                delta = self.delta
                Hmax = H0
                iteration = 0
                new_B = 0
                while new_B < Bmax and iteration < 1000:
                    Hmax += delta
                    iteration += 1
                    new_B = self.BH_func(Hmax, self.Bs, self.a)

            else:
                Hmax = self.Hmax

            if Hmax is not None:
                H = np.linspace(H0, Hmax, 200)
                B = self.BH_func(H, self.Bs, self.a)

                BH = np.zeros((len(H), 2))
                BH[:, 0] = H
                BH[:, 1] = B

                return BH
