# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotDC.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from .arc_1 import Arc1
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotDC(Slot):
    """Slot with two rods (for double squirrel cage)

    Attributes
    ----------
    W1 : float
        Slot isthmus width.
        Unit: m; Default: 0.0122; Minimum: 0
    H1 : float
        Distance upper rod center to bore
        Unit: m; Default: 0.0122; Minimum: 0
    D1 : float
        Diameter upper rod
        Unit: m; Default: 0.001; Minimum: 0
    W2 : float
        Middle connection width
        Unit: m; Default: 0.0122; Minimum: 0
    H2 : float
        Height between the first and second center
        Unit: m; Default: 0.001; Minimum: 0
    D2 : float
        Diameter upper section lower rod
        Unit: m; Default: 0.001; Minimum: 0
    H3 : float
        Length of lower rod
        Unit: m; Default: 0.001; Minimum: 0
    R3 : float
        Radius lower section lower rod
        Unit: m; Default: 0.001; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    W1: float = 0.0122
    """Slot isthmus width."""
    H1: float = 0.0122
    """Distance upper rod center to bore"""
    D1: float = 0.001
    """Diameter upper rod"""
    W2: float = 0.0122
    """Middle connection width"""
    H2: float = 0.001
    """Height between the first and second center"""
    D2: float = 0.001
    """Diameter upper section lower rod"""
    H3: float = 0.001
    """Length of lower rod"""
    R3: float = 0.001
    """Radius lower section lower rod"""

    # Inlined from Methods.Slot.SlotDC._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        point_list: list
            A list of 15 Point

        """

        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z12|| = W1
        # alpha = self.comp_angle_opening()
        alpha = 2 * float(np.arcsin(self.W1 / (2 * Rbo)))

        # Compute all points coordinates
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Rbo * np.exp(-1j * alpha / 2)
        if self.is_outwards():
            sign = +1
        else:
            sign = -1

        Zc1 = Z1.real + sign * self.H1
        Zc2 = Zc1 + sign * self.H2
        Zc3 = Zc2 + sign * self.H3

        Z2 = (
            Zc1
            - sign * np.sqrt((self.D1 / 2) ** 2 - (self.W1 / 2) ** 2)
            - 1j * (self.W1 / 2)
        )
        Z3 = (
            Zc1
            + sign * np.sqrt((self.D1 / 2) ** 2 - (self.W2 / 2) ** 2)
            - 1j * (self.W2 / 2)
        )
        Z4 = (
            Zc2
            - sign * np.sqrt((self.D2 / 2) ** 2 - (self.W2 / 2) ** 2)
            - 1j * (self.W2 / 2)
        )

        Z5 = Zc2.real - 1j * self.D2 / 2
        Z6 = Zc3.real - 1j * self.R3

        # Symmetries
        Z7 = Z6.conjugate()
        Z8 = Z5.conjugate()
        Z9 = Z4.conjugate()
        Z10 = Z3.conjugate()
        Z11 = Z2.conjugate()
        Z12 = Z1.conjugate()

        return [Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8, Z9, Z10, Z11, Z12, Zc1, Zc2, Zc3]

    # Inlined from Methods.Slot.SlotDC.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        curve_list: list
            A list of 6 Segment and 5 Arc

        """

        [
            Z1,
            Z2,
            Z3,
            Z4,
            Z5,
            Z6,
            Z7,
            Z8,
            Z9,
            Z10,
            Z11,
            Z12,
            _,
            _,
            _,
        ] = self._comp_point_coordinate()

        # Adapt the lines according to the lamination
        if self.is_outwards():
            sign = 1
            direc = True
        else:
            sign = -1
            direc = False

        # Creation of curve
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Arc1(Z2, Z3, sign * self.D1 / 2, is_trigo_direction=direc))
        curve_list.append(Segment(Z3, Z4))
        curve_list.append(Arc1(Z4, Z5, sign * self.D2 / 2, is_trigo_direction=direc))
        curve_list.append(Segment(Z5, Z6))

        curve_list.append(Arc1(Z6, Z7, sign * self.R3, is_trigo_direction=direc))

        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Arc1(Z8, Z9, sign * self.D2 / 2, is_trigo_direction=direc))
        curve_list.append(Segment(Z9, Z10))
        curve_list.append(Arc1(Z10, Z11, sign * self.D1 / 2, is_trigo_direction=direc))
        curve_list.append(Segment(Z11, Z12))

        return curve_list

    # Inlined from Methods.Slot.SlotDC.check
    def check(self):
        """Check that the SlotDC object is correct

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        None
        """
        if self.W1 >= self.D1:
            raise SlotCheckError("Slot 17 must have W1 < D1")
        if self.W2 >= self.D1:
            raise SlotCheckError("Slot 17 must have W2 < D1")
        if self.W2 >= self.D2:
            raise SlotCheckError("Slot 17 must have W2 < D2")
        if self.H2 <= (self.D1 / 2 + self.D2 / 2):
            raise SlotCheckError("Slot 17 must have D1/2 + D2/2 < H2")

    # Inlined from Methods.Slot.SlotDC.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W1 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotDC.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the top of the Slot is an Arc

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        H = self.R3 + self.H3 + self.H2 + self.H1

        # Computation of the arc height
        Rbo = self.get_Rbo()
        alpha = self.comp_angle_opening() / 2
        Harc = float(Rbo * (1 - np.cos(alpha)))

        if self.is_outwards():
            return H - Harc
        else:
            return H + Harc

    # Inlined from Methods.Slot.SlotDC.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return (
            self.R3
            + self.H3
            + self.H2
            + np.sqrt((self.D1 / 2) ** 2 - (self.W1 / 2) ** 2)
        )

    # Inlined from Methods.Slot.SlotDC.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the top of the Slot is an Arc

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        [
            Z1,
            Z2,
            Z3,
            Z4,
            Z5,
            Z6,
            Z7,
            Z8,
            Z9,
            Z10,
            Z11,
            Z12,
            _,
            _,
            _,
        ] = self._comp_point_coordinate()

        Rbo = self.get_Rbo()

        Swind = self.comp_surface_active()
        # Rectangle Z12,Z11,Z2,Z1
        S6 = self.W1 * abs(Z12.real - Z11.real)
        # Top arc of the slot (on bore radius)
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        if self.is_outwards():
            return Swind + S6 - Sarc
        else:
            return Swind + S6 + Sarc

    # Inlined from Methods.Slot.SlotDC.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotDC
            A SlotDC object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        [
            Z1,
            Z2,
            Z3,
            Z4,
            Z5,
            Z6,
            Z7,
            Z8,
            Z9,
            Z10,
            Z11,
            Z12,
            _,
            _,
            _,
        ] = self._comp_point_coordinate()

        # Half circle R3
        S1 = self.R3**2 * np.pi / 2
        # Tapeze H3
        S2 = self.H3 * (self.R3 * 2 + self.D2) / 2
        # Half circle D2
        S3 = (self.D2 / 2) ** 2 * np.pi / 2
        # Remove arc from Half Circle D2
        alpha1 = float(2 * np.arcsin(self.W2 / (2 * self.D2 / 2)))
        Sarc1 = ((self.D2 / 2) ** 2.0) / 2.0 * (alpha1 - np.sin(alpha1))
        # Rectangle Z10,Z9,Z4,Z3
        S4 = self.W2 * np.abs(Z10.real - Z9.real)
        # Circle D1
        S5 = (self.D1 / 2) ** 2 * np.pi
        # Remove arc from Circle D1 from rectangle Z10,Z9,Z4,Z3
        alpha2 = float(2 * np.arcsin(self.W2 / (2 * self.D1 / 2)))
        Sarc2 = ((self.D1 / 2) ** 2.0) / 2.0 * (alpha2 - np.sin(alpha2))
        # Remove arc from Circle D1 from W1 rectangle
        alpha3 = float(2 * np.arcsin(self.W1 / (2 * self.D1 / 2)))
        Sarc3 = ((self.D1 / 2) ** 2.0) / 2.0 * (alpha3 - np.sin(alpha3))

        return S1 + S2 + S3 - Sarc1 + S4 + S5 - Sarc2 - Sarc3

    # Inlined from Methods.Slot.SlotDC.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotDC
            A SlotDC object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        # get the name of the lamination
        st = self.get_name_lam()

        # Create curve list
        curve_list = self.build_geometry()[1:-1]
        curve_list.append(
            Segment(begin=curve_list[-1].get_end(), end=curve_list[0].get_begin())
        )

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H1 + self.H2
        else:
            Zmid = self.get_Rbo() - self.H1 - self.H2
        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """


MachineCheckError = SlotDC.MachineCheckError
LaminationCheckError = SlotDC.LaminationCheckError
SlotCheckError = SlotDC.SlotCheckError
