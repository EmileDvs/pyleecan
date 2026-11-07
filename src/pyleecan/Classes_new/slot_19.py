# Experimental dataclass generated from Generator/ClassesRef/Slot/Slot19.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from .arc_1 import Arc1
from .segment import Segment
from .slot import Slot


@dataclass(eq=False)
class Slot19(Slot):
    """trapezoidal slot with rounded bottom

    Attributes
    ----------
    W0 : float
        Slot top width
        Unit: m; Default: 0.013; Minimum: 0
    H0 : float
        Slot height
        Unit: m; Default: 0.02; Minimum: 0
    W1 : float
        Slot bottom width.
        Unit: m; Default: 0.01; Minimum: 0
    Wx_is_rad : bool
        Wx unit, False for m, True for rad
        Default: False
    """

    IS_SYMMETRICAL: ClassVar = 1
    W0: float = 0.013
    """Slot top width"""
    H0: float = 0.02
    """Slot height"""
    W1: float = 0.01
    """Slot bottom width."""
    Wx_is_rad: bool = False
    """Wx unit, False for m, True for rad"""

    # Inlined from Methods.Slot.Slot19._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : Slot19
            A Slot19 object

        Returns
        -------
        point_list: list
            A list of Points

        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
        alpha0 = self.comp_angle_opening() / 2
        alpha1 = self.comp_angle_bottom() / 2

        # comp point coordinate (in complex)
        Z_ = Rbo * np.exp(1j * 0)
        Z0 = Z_ * np.exp(1j * alpha0)

        if self.is_outwards():
            Z1 = (Rbo + self.H0) * np.exp(1j * alpha1)
        else:  # inward slot
            Z1 = (Rbo - self.H0) * np.exp(1j * alpha1)

        # symetry
        Z2 = Z1.conjugate()
        Z3 = Z0.conjugate()

        return [Z3, Z2, Z1, Z0]

    # Inlined from Methods.Slot.Slot19.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : Slot19
            A Slot19 object

        Returns
        -------
        curve_list: list
            A list of 2 Segment and 1 Arc

        """

        [Z1, Z2, Z3, Z4] = self._comp_point_coordinate()

        # Creation of curve
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        if self.W1 > 0:
            curve_list.append(Arc1(Z2, Z3, abs(Z3)))
        curve_list.append(Segment(Z3, Z4))

        return curve_list

    # Inlined from Methods.Slot.Slot19.check
    def check(self):
        """Check that the Slot19 object is correct

        Parameters
        ----------
        self : Slot19
            A Slot19 object

        Returns
        -------
        None

        Raises
        -------
        S19_H2CheckError
            H1 must be > 0

        S19_W1CheckError
            W1 must be > 0
        """
        if self.W1 < 0:
            raise S19_W1CheckError("W1 must be larger than zero")

    # Inlined from Methods.Slot.Slot19.comp_angle_bottom
    def comp_angle_bottom(self):
        """Compute the slot bottom angle of the Slot

        Parameters
        ----------
        self : Slot19
            A Slot19 object

        Returns
        -------
        alpha: float
            slot bottom angle [rad]

        """

        Rbo = self.get_Rbo()

        if self.Wx_is_rad:
            return self.W1
        else:
            if self.is_outwards():
                alpha = 2 * float(np.arcsin(self.W1 / (2 * Rbo + 2 * self.H0)))
            else:  # inward slot
                alpha = 2 * float(np.arcsin(self.W1 / (2 * Rbo - 2 * self.H0)))

        return alpha

    # Inlined from Methods.Slot.Slot19.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the slot opening angle of the Slot

        Parameters
        ----------
        self : Slot19
            A Slot19 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        if self.Wx_is_rad:
            return self.W0
        else:
            return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.Slot19.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : Slot19
            A Slot19 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0

    # Inlined from Methods.Slot.Slot19.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : Slot19
            A Slot19 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        Rbo = self.get_Rbo()

        # Wint is the with at the top of the opening
        alpha0 = self.comp_angle_opening()
        alpha1 = self.comp_angle_bottom()

        if self.is_outwards():
            R1 = Rbo + self.H0
        else:
            R1 = Rbo - self.H0

        W0 = 2 * Rbo * np.sin(alpha0 / 2)
        W1 = 2 * R1 * np.sin(alpha1 / 2)

        Str = 1 / 2 * (W0 + W1) * self.H0
        S0 = Rbo**2 / 2 * (alpha0 - np.sin(alpha0))
        S1 = R1**2 / 2 * (alpha1 - np.sin(alpha1))

        return Str + S1 - S0

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S19_W1CheckError(SlotCheckError):
        """ """


MachineCheckError = Slot19.MachineCheckError
LaminationCheckError = Slot19.LaminationCheckError
SlotCheckError = Slot19.SlotCheckError
S19_W1CheckError = Slot19.S19_W1CheckError
