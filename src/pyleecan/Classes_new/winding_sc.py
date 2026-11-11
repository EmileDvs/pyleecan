# Experimental dataclass generated from Generator/ClassesRef/Machine/WindingSC.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from ..Functions_new.Winding.reverse_wind_mat import reverse_wind_mat
from ..Functions_new.Winding.shift_wind_mat import shift_wind_mat
from ._error import WindingError
from .lamination import Lamination
from .winding import Winding


@dataclass(eq=False)
class WindingSC(Winding):
    """short-circuit winding (e.g. squirrel cage type)

    Attributes
    ----------
    """

    NAME: ClassVar = "short-circuit"

    # Inlined from Methods.Machine.WindingSC.comp_connection_mat
    # TODO: update docstring -> there should not be elementary circuits since
    #       every bar could have its own unique current
    def comp_connection_mat(self, Zs=None, p=None):
        """Compute the Winding Matrix (for winding type 10)
        type 10 : Squirrel cage Winding (elementary circuit loop involving bar n°1
        and bar n°Zr for alphar0_rad=0) (Nlay_rad=Nlay_tan=1)

        Parameters
        ----------
        self : Winding
            A: Winding object
        Zs : int
            Number of Slot (Integer >0)
        p : int
            Number of pole pairs (Integer >0)

        Returns
        -------
        numpy.ndarray
            Winding Matrix (Nlay_rad, Nlay_tan, Zs, qs)

        Raises
        ------
        WindingT10DefQsError
            qs must be equal to Zs

        """
        if Zs is None:
            if self.parent is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object."
                )

            if self.parent.slot is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object with Slot."
                )

            Zs = self.parent.slot.Zs

        if p is None:
            if self.parent is None:
                raise WindingError(
                    "ERROR: The Winding object must be in a Lamination object."
                )

            p = self.parent.get_pole_pair_number()

        assert Zs > 0, "Zs must be >0"
        assert Zs % 1 == 0, "Zs must be an integer"

        if self.qs != Zs:
            raise self.WindingT10DefQsError(
                "wrong winding definition, you must have qs = Zs !"
            )

        wind_mat = np.zeros((1, 1, Zs, self.qs))

        for ii in range(Zs):
            # phase n°ii
            # wind_mat[0, 0, ii, ii] = -1 # there are only positive 'windings' for now
            # wind_mat[0, 0, (ii - 1) % Zs, ii] = 1
            wind_mat[0, 0, ii, ii] = 1

        # Set default values
        if self.is_reverse_wind is None:
            self.is_reverse_wind = False
        if self.Nslot_shift_wind is None:
            self.Nslot_shift_wind = 0
        # Apply the transformations
        if self.is_reverse_wind:
            wind_mat = reverse_wind_mat(wind_mat)
        if self.Nslot_shift_wind != 0:
            wind_mat = shift_wind_mat(wind_mat, self.Nslot_shift_wind)

        return wind_mat

    # Inlined from Methods.Machine.WindingSC.comp_periodicity
    def comp_periodicity(self):
        """Computes the winding matrix (anti-)periodicity

        Parameters
        ----------
        self : WindingSC
            A WindingSC object

        Returns
        -------
        per_a: int
            Number of spatial periods of the winding
        is_aper_a: bool
            True if the winding is anti-periodic over space

        """

        lamination = self.parent

        if lamination is not None:
            # Call comp_periodicity of Lamination class since squirrel cage periodicity
            # depends on lamination properties: number of pole pairs and number of slots
            per_a, is_aper_a = Lamination.comp_periodicity_spatial(lamination)

            if is_aper_a:
                # Multiply periodicity by 2 to be compliant with Winding.comp_periodicity()
                per_a = int(2 * per_a)

            return per_a, is_aper_a

        else:
            return None, False

    # Inlined from Methods.Machine.WindingSC.get_dim_wind
    def get_dim_wind(self):
        """Get the two first dimension of the winding matrix

        Parameters
        ----------
        self : Winding
            A Winding object

        Returns
        -------
        (Nrad, Ntan): tuple
            Number of layer in radial and tangential direction

        """

        return (1, 1)

    class WindingT10DefQsError(WindingError):
        """ """
