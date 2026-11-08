# Experimental dataclass generated from Generator/ClassesRef/Machine/BoreLSRPM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._error import ParentMissingError
from .arc_1 import Arc1
from .bore import Bore
from .segment import Segment


@dataclass(eq=False)
class BoreLSRPM(Bore):
    """Class for Bore LSRPM

    Attributes
    ----------
    N : int
        Number of flower arc
        Default: 8; Minimum: 0
    Rarc : float
        Radius of the flower arc
        Unit: m; Default: 0.0375; Minimum: 0
    W1 : float
        Width of segement
        Unit: m; Default: 0.0035
    """

    N: int = 8
    """Number of flower arc"""
    Rarc: float = 0.0375
    """Radius of the flower arc"""
    W1: float = 0.0035
    """Width of segement"""

    # Inlined from Methods.Machine.BoreLSRPM.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the Bore

        Parameters
        ----------
        self : BoreLSRPM
            A BoreLSRPM object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the bore
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.N, False

    # Inlined from Methods.Machine.BoreLSRPM.get_bore_line
    def get_bore_line(self, prop_dict=None):
        """Return the bore line description

        Parameters
        ----------
        self : BoreLSRPM
            A BoreLSRPM object
        prop_dict : dict
            Property dictionary to apply on the lines

        Returns
        -------
        bore_list : list
            List of bore lines
        """

        if self.parent is not None:
            if self.is_yoke():
                R = self.parent.get_Ryoke()
            else:
                R = self.parent.get_Rbo()
        else:
            raise ParentMissingError(
                "Error: The Bore object is not inside a Lamination"
            )

        # Compute the shape

        alpha1 = np.pi / self.N

        # Z1
        Z1 = R * np.exp(-1j * alpha1)

        # ZC1
        ZC1 = (R - self.Rarc) * np.exp(-1j * alpha1)
        XC1 = ZC1.real
        YC1 = ZC1.imag

        # Z2
        X2 = np.sqrt(self.Rarc**2 - (self.W1 + YC1) ** 2) + XC1
        Y2 = -self.W1
        Z2 = X2 + 1j * Y2

        Z3 = Z2.conjugate()
        Z4 = Z1.conjugate()

        # Create the lines
        bore_list = []
        for ii in range(self.N):
            bore_list.append(
                Arc1(
                    begin=Z1
                    * np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha)),
                    end=Z2 * np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha)),
                    radius=self.Rarc,
                    is_trigo_direction=True,
                    prop_dict=prop_dict,
                )
            )

            bore_list.append(
                Segment(
                    Z2 * np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha)),
                    Z3 * np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha)),
                    prop_dict=prop_dict,
                )
            )

            bore_list.append(
                Arc1(
                    begin=Z3
                    * np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha)),
                    end=Z4 * np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha)),
                    radius=self.Rarc,
                    is_trigo_direction=True,
                    prop_dict=prop_dict,
                )
            )

        return bore_list
