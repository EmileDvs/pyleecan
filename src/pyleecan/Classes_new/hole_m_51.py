# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM51.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions.Geometry.inter_line_circle import inter_line_circle
from ..Functions.labels import HOLEM_LAB
from ..Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
    plot_quote,
)
from . import ParentMissingError
from .arc_1 import Arc1
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM51(HoleMag):
    """3 magnets V hole

    Attributes
    ----------
    H0 : float
        Hole depth
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Distance from the lamination Bore
        Unit: m; Default: 0; Minimum: 0
    H2 : float
        Hole width
        Unit: m; Default: 0.02; Minimum: 0
    W0 : float
        Hole bottom width
        Unit: m; Default: 0.01; Minimum: 0
    W1 : float
        Hole angular width
        Unit: rad; Default: 0; Minimum: 0
    W2 : float
        magnet_1 position
        Unit: m; Default: 0.01; Minimum: 0
    W3 : float
        magnet_1 width
        Unit: m; Default: 0; Minimum: 0
    W4 : float
        magnet_2 position
        Unit: m; Default: 0.01; Minimum: 0
    W5 : float
        magnet_2 width
        Unit: m; Default: 0.01; Minimum: 0
    W6 : float
        magnet_0 position
        Unit: m; Default: 0; Minimum: 0
    W7 : float
        magnet_0 width
        Unit: m; Default: 0; Minimum: 0
    magnet_0 : Magnet or None
        First Magnet
        Default: None
    magnet_1 : Magnet or None
        Second Magnet
        Default: None
    magnet_2 : Magnet or None
        Third Magnet
        Default: None
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Hole depth"""
    H1: float = 0
    """Distance from the lamination Bore"""
    H2: float = 0.02
    """Hole width"""
    W0: float = 0.01
    """Hole bottom width"""
    W1: float = 0
    """Hole angular width"""
    W2: float = 0.01
    """magnet_1 position"""
    W3: float = 0
    """magnet_1 width"""
    W4: float = 0.01
    """magnet_2 position"""
    W5: float = 0.01
    """magnet_2 width"""
    W6: float = 0
    """magnet_0 position"""
    W7: float = 0
    """magnet_0 width"""
    magnet_0: Magnet | None = None
    """First Magnet"""
    magnet_1: Magnet | None = None
    """Second Magnet"""
    magnet_2: Magnet | None = None
    """Third Magnet"""

    # Inlined from Methods.Slot.HoleM51._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rext = self.get_Rext()

        # comp point coordinate (in complex)
        alpha = self.comp_alpha()

        Wslot = 2 * np.sin(self.W1 / 2) * (Rext - self.H1)
        L = 0.5 * (Wslot - self.W0) / np.cos(alpha)  # ||P2,P5||

        # Center of the hole
        Z0 = Rext - self.H0
        Z2 = Z0 + 1j * self.W0 / 2
        Z25 = Z0 - 1j * self.W0 / 2
        Z15 = Z25 - self.H2
        Z1 = Z2 - 1j * self.W2
        Z26 = Z1 - 1j * self.W3
        Z12 = Z2 - self.H2
        Z13 = Z12 - 1j * self.W2
        Z14 = Z13 - 1j * self.W3
        Z11 = Z12 + 1j * np.tan(alpha / 2) * self.H2
        Z16 = Z15 - 1j * np.tan(alpha / 2) * self.H2

        # Draw the left side with center P2, and X axis =(P2,P5), Y axis=(P2,P10)
        Z3 = self.W4 * np.exp(1j * (np.pi / 2 - alpha)) + Z2
        Z4 = (self.W4 + self.W5) * np.exp(1j * (np.pi / 2 - alpha)) + Z2
        Z5 = (Rext - self.H1) * np.exp(1j * self.W1 / 2)
        Z10 = (1j * self.H2) * np.exp(1j * (np.pi / 2 - alpha)) + Z2
        Z9 = (1j * self.H2 + self.W4) * np.exp(1j * (np.pi / 2 - alpha)) + Z2
        Z8 = (1j * self.H2 + self.W4 + self.W5) * np.exp(1j * (np.pi / 2 - alpha)) + Z2
        Z7 = (1j * self.H2 + L) * np.exp(1j * (np.pi / 2 - alpha)) + Z2

        # Draw the right side with center P25, X axis (P25,P23), Y axis(P25,P17)
        Z24 = self.W6 * np.exp(-1j * (np.pi / 2 - alpha)) + Z25
        Z23 = (self.W6 + self.W7) * np.exp(-1j * (np.pi / 2 - alpha)) + Z25
        Z22 = (Rext - self.H1) * np.exp(-1j * self.W1 / 2)
        Z17 = (-1j * self.H2) * np.exp(-1j * (np.pi / 2 - alpha)) + Z25
        Z18 = (-1j * self.H2 + self.W6) * np.exp(-1j * (np.pi / 2 - alpha)) + Z25
        Z19 = (-1j * self.H2 + self.W6 + self.W7) * np.exp(
            -1j * (np.pi / 2 - alpha)
        ) + Z25
        Z20 = (-1j * self.H2 + L) * np.exp(-1j * (np.pi / 2 - alpha)) + Z25

        # Z6 is the intersection of the line [Z7,Z10] and Circle centre
        # (0,0) radius Rext - H1
        Zint = inter_line_circle(Z7, Z10, Rext - self.H1)

        # Select the point with Re(Z) > 0
        if Zint[0].real > 0:
            Z6 = Zint[0]
        else:
            Z6 = Zint[1]
        Z21 = Z6.conjugate()

        point_dict = {}
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        point_dict["Z7"] = Z7
        point_dict["Z8"] = Z8
        point_dict["Z9"] = Z9
        point_dict["Z10"] = Z10
        point_dict["Z11"] = Z11
        point_dict["Z12"] = Z12
        point_dict["Z13"] = Z13
        point_dict["Z14"] = Z14
        point_dict["Z15"] = Z15
        point_dict["Z16"] = Z16
        point_dict["Z17"] = Z17
        point_dict["Z18"] = Z18
        point_dict["Z19"] = Z19
        point_dict["Z20"] = Z20
        point_dict["Z21"] = Z21
        point_dict["Z22"] = Z22
        point_dict["Z23"] = Z23
        point_dict["Z24"] = Z24
        point_dict["Z25"] = Z25
        point_dict["Z26"] = Z26

        return point_dict

    # Inlined from Methods.Slot.HoleM51.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Line) needed to plot the Hole.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object
        alpha : float
            Angle to rotate the hole (Default value = 0) [rad]
        delta : complex
            Complex to translate the hole (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM51

        """
        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

        Rext = self.get_Rext()

        # Get all the points
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z8 = point_dict["Z8"]
        Z9 = point_dict["Z9"]
        Z11 = point_dict["Z11"]
        Z13 = point_dict["Z13"]
        Z14 = point_dict["Z14"]
        Z16 = point_dict["Z16"]
        Z18 = point_dict["Z18"]
        Z19 = point_dict["Z19"]
        Z21 = point_dict["Z21"]
        Z22 = point_dict["Z22"]
        Z23 = point_dict["Z23"]
        Z24 = point_dict["Z24"]
        Z25 = point_dict["Z25"]
        Z26 = point_dict["Z26"]

        surf_list = []
        # Create all the surfaces for all the cases
        # Air surface bore around magnet_0
        curve_list = []
        curve_list.append(Arc1(Z21, Z22, Rext - self.H1))
        curve_list.append(Segment(Z22, Z23))
        curve_list.append(Segment(Z23, Z19))
        curve_list.append(Segment(Z19, Z21))
        point_ref = (Z21 + Z22 + Z23 + Z19) / 4
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_0
        curve_list = []
        if is_simplified:
            curve_list.append(Segment(Z24, Z18))
            curve_list.append(Segment(Z19, Z23))
        else:
            curve_list.append(Segment(Z24, Z18))
            curve_list.append(Segment(Z18, Z19))
            curve_list.append(Segment(Z19, Z23))
            curve_list.append(Segment(Z23, Z24))
        point_ref = (Z24 + Z18 + Z19 + Z23) / 4

        S2 = SurfLine(
            line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref
        )

        # Air surface between magnet_0 and magnet_1
        curve_list = []
        curve_list.append(Segment(Z24, Z25))
        curve_list.append(Segment(Z25, Z26))
        curve_list.append(Segment(Z26, Z14))
        curve_list.append(Segment(Z14, Z16))
        curve_list.append(Segment(Z16, Z18))
        curve_list.append(Segment(Z18, Z24))
        point_ref = (Z25 + Z16) / 2
        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_1
        curve_list = []
        if is_simplified:
            curve_list.append(Segment(Z1, Z13))
            curve_list.append(Segment(Z14, Z26))
        else:
            curve_list.append(Segment(Z26, Z1))
            curve_list.append(Segment(Z1, Z13))
            curve_list.append(Segment(Z13, Z14))
            curve_list.append(Segment(Z14, Z26))
        point_ref = (Z26 + Z1 + Z13 + Z14) / 4
        S4 = SurfLine(
            line_list=curve_list, label=mag_label + "T1-S0", point_ref=point_ref
        )

        # Air surface between magnet_1 and magnet_2
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z9))
        curve_list.append(Segment(Z9, Z11))
        curve_list.append(Segment(Z11, Z13))
        curve_list.append(Segment(Z13, Z1))
        point_ref = (Z11 + Z2) / 2
        S5 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_2
        curve_list = []
        if is_simplified:
            curve_list.append(Segment(Z4, Z8))
            curve_list.append(Segment(Z9, Z3))
        else:
            curve_list.append(Segment(Z4, Z8))
            curve_list.append(Segment(Z8, Z9))
            curve_list.append(Segment(Z9, Z3))
            curve_list.append(Segment(Z3, Z4))
        point_ref = (Z4 + Z8 + Z9 + Z3) / 4

        S6 = SurfLine(
            line_list=curve_list, label=mag_label + "T2-S0", point_ref=point_ref
        )

        # Air surface bore around magnet_2
        curve_list = []
        curve_list.append(Arc1(Z5, Z6, Rext - self.H1))
        curve_list.append(Segment(Z6, Z8))
        curve_list.append(Segment(Z8, Z4))
        curve_list.append(Segment(Z4, Z5))
        point_ref = (Z4 + Z5 + Z6 + Z8) / 4
        S7 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_2 (no magnet_2 and magnet_1)
        curve_list = []
        curve_list.append(Arc1(Z5, Z6, Rext - self.H1))
        curve_list.append(Segment(Z6, Z11))
        curve_list.append(Segment(Z11, Z13))
        curve_list.append(Segment(Z13, Z1))
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z5))
        point_ref = (Z2 + Z11) / 2
        S8 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_0 (no magnet_0 and magnet_1)
        curve_list = []
        curve_list.append(Arc1(Z21, Z22, Rext - self.H1))
        curve_list.append(Segment(Z22, Z25))
        curve_list.append(Segment(Z25, Z26))
        curve_list.append(Segment(Z26, Z14))
        curve_list.append(Segment(Z14, Z16))
        curve_list.append(Segment(Z16, Z21))
        point_ref = (Z25 + Z16) / 2
        S9 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_1 (no magnet_1 and magnet_0 and magnet_2)
        curve_list = []
        curve_list.append(Segment(Z24, Z25))
        curve_list.append(Segment(Z25, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z9))
        curve_list.append(Segment(Z9, Z11))
        curve_list.append(Segment(Z11, Z16))
        curve_list.append(Segment(Z16, Z18))
        curve_list.append(Segment(Z18, Z24))
        point_ref = (Z1 + Z13) / 2
        S10 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_1 (no magnet_1 and no magnet_0 and magnet_2)
        curve_list = []
        curve_list.append(Arc1(Z21, Z22, Rext - self.H1))
        curve_list.append(Segment(Z22, Z25))
        curve_list.append(Segment(Z25, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z9))
        curve_list.append(Segment(Z9, Z11))
        curve_list.append(Segment(Z11, Z16))
        curve_list.append(Segment(Z16, Z21))
        point_ref = (Z1 + Z13) / 2
        S11 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_1 (no magnet_1 and magnet_0 and no magnet_2)
        curve_list = []
        curve_list.append(Arc1(Z5, Z6, Rext - self.H1))
        curve_list.append(Segment(Z6, Z11))
        curve_list.append(Segment(Z11, Z16))
        curve_list.append(Segment(Z16, Z18))
        curve_list.append(Segment(Z18, Z24))
        curve_list.append(Segment(Z24, Z25))
        curve_list.append(Segment(Z25, Z2))
        curve_list.append(Segment(Z2, Z5))
        point_ref = (Z1 + Z13) / 2
        S12 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface No magnet
        curve_list = []
        curve_list.append(Arc1(Z5, Z6, Rext - self.H1))
        curve_list.append(Segment(Z6, Z11))
        curve_list.append(Segment(Z11, Z16))
        curve_list.append(Segment(Z16, Z21))
        curve_list.append(Arc1(Z21, Z22, Rext - self.H1))
        curve_list.append(Segment(Z22, Z25))
        curve_list.append(Segment(Z25, Z2))
        curve_list.append(Segment(Z2, Z5))
        point_ref = (Z1 + Z13) / 2
        S13 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Create the surface list by selecting the correct ones
        if self.magnet_0 and self.magnet_1 and self.magnet_2:
            S1.label = vent_label + "T0-S0"  # Hole
            S3.label = vent_label + "T1-S0"  # Hole
            S5.label = vent_label + "T2-S0"  # Hole
            S7.label = vent_label + "T3-S0"  # Hole
            surf_list = [S1, S2, S3, S4, S5, S6, S7]
        elif not self.magnet_0 and self.magnet_1 and self.magnet_2:
            S9.label = vent_label + "T0-S0"  # Hole
            S5.label = vent_label + "T1-S0"  # Hole
            S7.label = vent_label + "T2-S0"  # Hole
            surf_list = [S9, S4, S5, S6, S7]
        elif self.magnet_0 and not self.magnet_1 and self.magnet_2:
            S1.label = vent_label + "T0-S0"  # Hole
            S10.label = vent_label + "T1-S0"  # Hole
            S7.label = vent_label + "T2-S0"  # Hole
            surf_list = [S1, S2, S10, S6, S7]
        elif not self.magnet_0 and not self.magnet_1 and self.magnet_2:
            S11.label = vent_label + "T0-S0"  # Hole
            S7.label = vent_label + "T1-S0"  # Hole
            surf_list = [S11, S6, S7]
        elif self.magnet_0 and self.magnet_1 and not self.magnet_2:
            S1.label = vent_label + "T0-S0"  # Hole
            S3.label = vent_label + "T1-S0"  # Hole
            S8.label = vent_label + "T2-S0"  # Hole
            surf_list = [S1, S2, S3, S4, S8]
        elif not self.magnet_0 and self.magnet_1 and not self.magnet_2:
            S9.label = vent_label + "T0-S0"  # Hole
            S8.label = vent_label + "T1-S0"  # Hole
            surf_list = [S9, S4, S8]
        elif self.magnet_0 and not self.magnet_1 and not self.magnet_2:
            S1.label = vent_label + "T0-S0"  # Hole
            S12.label = vent_label + "T1-S0"  # Hole
            surf_list = [S1, S2, S12]
        elif not self.magnet_0 and not self.magnet_1 and not self.magnet_2:
            S13.label = vent_label + "T0-S0"  # Hole
            surf_list = [S13]

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleM51.check
    def check(self):
        """Check that the HoleM51 object is correct

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object

        Returns
        -------
        None
        """

        # Check that everything is set
        if self.W0 is None:
            raise S51_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise S51_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise S51_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise S51_NoneError("You must set W3 !")
        elif self.W4 is None:
            raise S51_NoneError("You must set W4 !")
        elif self.W5 is None:
            raise S51_NoneError("You must set W5 !")
        elif self.W6 is None:
            raise S51_NoneError("You must set W6 !")
        elif self.W7 is None:
            raise S51_NoneError("You must set W7 !")
        elif self.H0 is None:
            raise S51_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S51_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise S51_NoneError("You must set H2 !")

        Rext = self.get_Rext()
        alpha = self.comp_alpha()

        if self.W0 < (self.W2 + self.W3):
            raise S51_WCheckError("You must have W2+W3 < W0")

        if Rext < self.H0 + self.H2:
            raise S51_RHCheckError("You must have H0+H2 < Rext")

        if alpha > np.pi / 2:
            raise S51_AlphaCheckError("You must have alpha < pi/2")

    # Inlined from Methods.Slot.HoleM51.comp_alpha
    def comp_alpha(self):
        """Compute the angle of the Hole (cf schematics)

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object

        Returns
        -------
        alpha: float
            Angle of the Hole (cf schematics) [rad]

        """
        Rext = self.get_Rext()

        alpha = -np.arctan(
            2
            * (
                self.H0
                - self.H1 * np.cos(0.5 * self.W1)
                + Rext * np.cos(0.5 * self.W1)
                - Rext
            )
            / (
                2.0 * self.H1 * np.sin(0.5 * self.W1)
                - 2 * Rext * np.sin(0.5 * self.W1)
                + self.W0
            )
        )

        return alpha

    # Inlined from Methods.Slot.HoleM51.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM51
            a HoleM51 object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        # Comp magnet
        point_dict = self._comp_point_coordinate()

        mag_dict = {}
        S0 = Segment(point_dict["Z18"], point_dict["Z19"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(point_dict["Z13"], point_dict["Z14"])
        mag_dict["magnet_1"] = S1.comp_normal()
        S2 = Segment(point_dict["Z8"], point_dict["Z9"])
        mag_dict["magnet_2"] = S2.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi
            mag_dict["magnet_1"] += np.pi
            mag_dict["magnet_2"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM51.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object

        Returns
        -------
        (Rmin, Rmax): tuple
            Radius of the circle that contains the hole [m]

        """

        Rext = self.get_Rext()

        Rmax = Rext - self.H1
        Rmin = Rext - self.H0 - self.H2

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM51.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        if index == 0 and self.magnet_0:
            return self.W7 * self.H2
        if index == 1 and self.magnet_1:
            return self.W3 * self.H2
        if index == 2 and self.magnet_2:
            return self.W5 * self.H2
        return 0

    # Inlined from Methods.Slot.HoleM51.comp_width
    def comp_width(self):
        """Compute the width of the Hole (cf schematics)

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object

        Returns
        -------
        Whole: float
            Width of the Hole (cf schematics) [m]

        """

        Rext = self.get_Rext()
        return 2 * np.sin(self.W1 / 2) * (Rext - self.H1)

    # Inlined from Methods.Slot.HoleM51.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return (
            self.magnet_0 is not None
            or self.magnet_1 is not None
            or self.magnet_2 is not None
        )

    # Inlined from Methods.Slot.HoleM51.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : HoleM51
            A HoleM51 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot)
        is_add_point_label : bool
            True to display the name of the points (Z1, Z2....)
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        type_add_active : int
            0: No active surface, 1: active surface as winding, 2: active surface as magnet
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamHole / LamSlot
            Default lamination used for the schematics

        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                Zh=8,
                W0=0.016,
                W1=np.pi / 6,
                W2=0.004,
                W3=0.01,
                W4=0.004,
                W5=0.008,
                W6=0.004,
                W7=0.008,
                H0=0.01196,
                H1=0.0025,
                H2=0.0055,
            )
            lam = LamHole(
                Rint=45e-3 / 2,
                Rext=81.5e-3,
                is_internal=True,
                is_stator=False,
                hole=[hole],
            )
            if is_return_default:
                return lam
            else:
                return hole.plot_schematics(
                    is_default=False,
                    is_return_default=False,
                    is_add_point_label=is_add_point_label,
                    is_add_schematics=is_add_schematics,
                    is_add_main_line=is_add_main_line,
                    type_add_active=type_add_active,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    fig=fig,
                    ax=ax,
                )

        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The hole is not inside a Lamination")
            lam = self.parent

            # Remove the magnets
            if type_add_active == 0:
                lam.hole[0].remove_magnet()

            alpha = np.pi / 2  # To rotate the schematics
            fig, ax = lam.plot(
                alpha=np.pi / self.Zh + alpha,
                is_show_fig=False,
                is_lam_only=type_add_active == 0,
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            sp = 2 * np.pi / self.Zh
            Rbo = self.get_Rbo()
            point_dict = self._comp_point_coordinate()

            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    Z = Z * np.exp(1j * alpha)
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Adding schematics
            if is_add_schematics:
                # W0
                Zlim1 = point_dict["Z2"] + self.H0 * 0.2
                Zlim2 = point_dict["Z25"] + self.H0 * 0.2
                plot_quote(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    Zlim1 * np.exp(1j * alpha),
                    Zlim2 * np.exp(1j * alpha),
                    point_dict["Z25"] * np.exp(1j * alpha),
                    offset_label=(1 + 1j) * self.H2 * 0.3,
                    fig=fig,
                    ax=ax,
                    label="W0",
                )
                # W1
                R = Rbo + self.H0 * 0.1
                line = Arc1(
                    begin=R * np.exp(-1j * self.W1 / 2) * np.exp(1j * alpha),
                    end=R * np.exp(1j * self.W1 / 2) * np.exp(1j * alpha),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=1j * self.H2 * 0.3,
                    fontsize=SC_FONT_SIZE,
                )
                if type_add_active != 0:
                    # W2
                    line = Segment(
                        (point_dict["Z2"] + point_dict["Z12"]) / 2 * np.exp(1j * alpha),
                        (point_dict["Z1"] + point_dict["Z13"]) / 2 * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W2",
                        offset_label=-self.H2 * 0.2 - 1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # W3
                    line = Segment(
                        point_dict["Z13"] * np.exp(1j * alpha),
                        point_dict["Z14"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W3",
                        offset_label=-1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # W4
                    line = Segment(
                        (point_dict["Z3"] + point_dict["Z9"]) / 2 * np.exp(1j * alpha),
                        (point_dict["Z10"] + point_dict["Z2"]) / 2 * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W4",
                        offset_label=-self.H2 * 0.2 - 1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # W5
                    line = Segment(
                        point_dict["Z9"] * np.exp(1j * alpha),
                        point_dict["Z8"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W5",
                        offset_label=-self.H2 * 0.2 - 1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # W6
                    line = Segment(
                        (point_dict["Z25"] + point_dict["Z17"])
                        / 2
                        * np.exp(1j * alpha),
                        (point_dict["Z24"] + point_dict["Z18"])
                        / 2
                        * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W6",
                        offset_label=-1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # W7
                    line = Segment(
                        point_dict["Z18"] * np.exp(1j * alpha),
                        point_dict["Z19"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W7",
                        offset_label=-1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                # H0
                line = Segment(
                    point_dict["Z1"].real * np.exp(1j * alpha), Rbo * np.exp(1j * alpha)
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.H2 * 0.2 + 1j * self.H0 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                A = np.angle(point_dict["Z22"])
                line = Segment(
                    Rbo * np.exp(1j * A) * np.exp(1j * alpha),
                    (Rbo - self.H1) * np.exp(1j * A) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=self.H2 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(
                    point_dict["Z5"] * np.exp(1j * alpha),
                    point_dict["Z7"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=-self.H2 * 0.6,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # W1 lines
                line = Segment(
                    0,
                    abs(point_dict["Z5"])
                    * 1.5
                    * np.exp(1j * np.angle(point_dict["Z5"]))
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    0,
                    abs(point_dict["Z22"])
                    * 1.5
                    * np.exp(1j * np.angle(point_dict["Z22"]))
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 radius
                line = Arc1(
                    begin=(Rbo - self.H1)
                    * np.exp(-1j * np.pi / 2 * 0.9)
                    * np.exp(1j * alpha),
                    end=(Rbo - self.H1)
                    * np.exp(1j * np.pi / 2 * 0.9)
                    * np.exp(1j * alpha),
                    radius=Rbo - self.H1,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Triangle lines
                line = Segment(
                    point_dict["Z7"] * np.exp(1j * alpha),
                    point_dict["Z5"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z10"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z12"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z25"] * np.exp(1j * alpha),
                    point_dict["Z15"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z25"] * np.exp(1j * alpha),
                    point_dict["Z17"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z22"] * np.exp(1j * alpha),
                    point_dict["Z20"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = (point_dict["Z22"] * np.exp(1j * alpha)).real * 1.2
            Rint = (point_dict["Z13"] * np.exp(1j * alpha)).imag * 0.9
            Rext = self.parent.Rext * 1.1

            ax.axis("equal")
            ax.set_ylim(Rint, Rext)
            ax.set_xlim(-W, W)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()
            fig.tight_layout()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    # Inlined from Methods.Slot.HoleM51.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM51
            a HoleM51 object
        """

        self.magnet_0 = None
        self.magnet_1 = None
        self.magnet_2 = None

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S51_RHCheckError(SlotCheckError):
        """ """

    class S51_AlphaCheckError(SlotCheckError):
        """ """

    class S51_WCheckError(SlotCheckError):
        """ """

    class S51_NoneError(SlotCheckError):
        """Raised when a propery of HoleM51 is None"""


MachineCheckError = HoleM51.MachineCheckError
LaminationCheckError = HoleM51.LaminationCheckError
SlotCheckError = HoleM51.SlotCheckError
S51_RHCheckError = HoleM51.S51_RHCheckError
S51_AlphaCheckError = HoleM51.S51_AlphaCheckError
S51_WCheckError = HoleM51.S51_WCheckError
S51_NoneError = HoleM51.S51_NoneError
