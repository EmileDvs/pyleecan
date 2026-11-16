# Experimental pydantic model generated from Generator/ClassesRef/Slot/Slot19.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

import numpy as np
from pydantic import Field

from ...classes_common.errors import S19_W1CheckError
from ..geometry.arc_1 import Arc1
from ..geometry.segment import Segment
from .slot import Slot


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

    W0: float = Field(default=0.013, ge=0, json_schema_extra={"unit": "m"})
    """Slot top width"""
    H0: float = Field(default=0.02, ge=0, json_schema_extra={"unit": "m"})
    """Slot height"""
    W1: float = Field(default=0.01, ge=0, json_schema_extra={"unit": "m"})
    """Slot bottom width."""
    Wx_is_rad: bool = False
    """Wx unit, False for m, True for rad"""

    _package: ClassVar[str] = "Slot"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Slot.Slot19._comp_point_coordinate
    def _comp_point_coordinate(self) -> list:
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
    def build_geometry(self) -> list:
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
        curve_list.append(Segment(begin=Z1, end=Z2))
        if self.W1 > 0:
            curve_list.append(Arc1(begin=Z2, end=Z3, radius=abs(Z3)))
        curve_list.append(Segment(begin=Z3, end=Z4))

        return curve_list

    # Inlined from Methods.Slot.Slot19.check
    def check(self) -> None:
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
    def comp_angle_bottom(self) -> float:
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
    def comp_angle_opening(self) -> float:
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
    def comp_height(self) -> float:
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
    def comp_surface(self) -> float:
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
