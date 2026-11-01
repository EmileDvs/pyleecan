# File generated according to Generator/ClassesRef/Slot/HoleM51.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM51"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.HoleMag import HoleMag
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var

from pyleecan.definitions import config_dict

from pyleecan.Functions.Geometry.inter_line_circle import inter_line_circle
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.Plot import (
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
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import HOLEM_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class HoleM51(HoleMag):
    """3 magnets V hole"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.HoleM51._comp_point_coordinate
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

        point_dict = dict()
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

    # cf Methods.Slot.HoleM51.build_geometry
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

        surf_list = list()
        # Create all the surfaces for all the cases
        # Air surface bore around magnet_0
        curve_list = list()
        curve_list.append(Arc1(Z21, Z22, Rext - self.H1))
        curve_list.append(Segment(Z22, Z23))
        curve_list.append(Segment(Z23, Z19))
        curve_list.append(Segment(Z19, Z21))
        point_ref = (Z21 + Z22 + Z23 + Z19) / 4
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_0
        curve_list = list()
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
        curve_list = list()
        curve_list.append(Segment(Z24, Z25))
        curve_list.append(Segment(Z25, Z26))
        curve_list.append(Segment(Z26, Z14))
        curve_list.append(Segment(Z14, Z16))
        curve_list.append(Segment(Z16, Z18))
        curve_list.append(Segment(Z18, Z24))
        point_ref = (Z25 + Z16) / 2
        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_1
        curve_list = list()
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
        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z9))
        curve_list.append(Segment(Z9, Z11))
        curve_list.append(Segment(Z11, Z13))
        curve_list.append(Segment(Z13, Z1))
        point_ref = (Z11 + Z2) / 2
        S5 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_2
        curve_list = list()
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
        curve_list = list()
        curve_list.append(Arc1(Z5, Z6, Rext - self.H1))
        curve_list.append(Segment(Z6, Z8))
        curve_list.append(Segment(Z8, Z4))
        curve_list.append(Segment(Z4, Z5))
        point_ref = (Z4 + Z5 + Z6 + Z8) / 4
        S7 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_2 (no magnet_2 and magnet_1)
        curve_list = list()
        curve_list.append(Arc1(Z5, Z6, Rext - self.H1))
        curve_list.append(Segment(Z6, Z11))
        curve_list.append(Segment(Z11, Z13))
        curve_list.append(Segment(Z13, Z1))
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z5))
        point_ref = (Z2 + Z11) / 2
        S8 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_0 (no magnet_0 and magnet_1)
        curve_list = list()
        curve_list.append(Arc1(Z21, Z22, Rext - self.H1))
        curve_list.append(Segment(Z22, Z25))
        curve_list.append(Segment(Z25, Z26))
        curve_list.append(Segment(Z26, Z14))
        curve_list.append(Segment(Z14, Z16))
        curve_list.append(Segment(Z16, Z21))
        point_ref = (Z25 + Z16) / 2
        S9 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface bore around magnet_1 (no magnet_1 and magnet_0 and magnet_2)
        curve_list = list()
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
        curve_list = list()
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
        curve_list = list()
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
        curve_list = list()
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

    # cf Methods.Slot.HoleM51.check
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

    # cf Methods.Slot.HoleM51.comp_alpha
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

    # cf Methods.Slot.HoleM51.comp_magnetization_dict
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

        mag_dict = dict()
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

    # cf Methods.Slot.HoleM51.comp_radius
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

    # cf Methods.Slot.HoleM51.comp_surface_magnet_id
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

    # cf Methods.Slot.HoleM51.comp_width
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

    # cf Methods.Slot.HoleM51.has_magnet
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

    # cf Methods.Slot.HoleM51.plot_schematics
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

    # cf Methods.Slot.HoleM51.remove_magnet
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        H0=0.003,
        H1=0,
        H2=0.02,
        W0=0.01,
        W1=0,
        W2=0.01,
        W3=0,
        W4=0.01,
        W5=0.01,
        W6=0,
        W7=0,
        magnet_0=-1,
        magnet_1=-1,
        magnet_2=-1,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "W4" in list(init_dict.keys()):
                W4 = init_dict["W4"]
            if "W5" in list(init_dict.keys()):
                W5 = init_dict["W5"]
            if "W6" in list(init_dict.keys()):
                W6 = init_dict["W6"]
            if "W7" in list(init_dict.keys()):
                W7 = init_dict["W7"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "magnet_1" in list(init_dict.keys()):
                magnet_1 = init_dict["magnet_1"]
            if "magnet_2" in list(init_dict.keys()):
                magnet_2 = init_dict["magnet_2"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.H0 = H0
        self.H1 = H1
        self.H2 = H2
        self.W0 = W0
        self.W1 = W1
        self.W2 = W2
        self.W3 = W3
        self.W4 = W4
        self.W5 = W5
        self.W6 = W6
        self.W7 = W7
        self.magnet_0 = magnet_0
        self.magnet_1 = magnet_1
        self.magnet_2 = magnet_2
        # Call HoleMag init
        super(HoleM51, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM51_str = ""
        # Get the properties inherited from HoleMag
        HoleM51_str += super(HoleM51, self).__str__()
        HoleM51_str += "H0 = " + str(self.H0) + linesep
        HoleM51_str += "H1 = " + str(self.H1) + linesep
        HoleM51_str += "H2 = " + str(self.H2) + linesep
        HoleM51_str += "W0 = " + str(self.W0) + linesep
        HoleM51_str += "W1 = " + str(self.W1) + linesep
        HoleM51_str += "W2 = " + str(self.W2) + linesep
        HoleM51_str += "W3 = " + str(self.W3) + linesep
        HoleM51_str += "W4 = " + str(self.W4) + linesep
        HoleM51_str += "W5 = " + str(self.W5) + linesep
        HoleM51_str += "W6 = " + str(self.W6) + linesep
        HoleM51_str += "W7 = " + str(self.W7) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM51_str += "magnet_0 = " + tmp
        else:
            HoleM51_str += "magnet_0 = None" + linesep + linesep
        if self.magnet_1 is not None:
            tmp = self.magnet_1.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM51_str += "magnet_1 = " + tmp
        else:
            HoleM51_str += "magnet_1 = None" + linesep + linesep
        if self.magnet_2 is not None:
            tmp = self.magnet_2.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM51_str += "magnet_2 = " + tmp
        else:
            HoleM51_str += "magnet_2 = None" + linesep + linesep
        return HoleM51_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM51, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.H2 != self.H2:
            return False
        if other.W0 != self.W0:
            return False
        if other.W1 != self.W1:
            return False
        if other.W2 != self.W2:
            return False
        if other.W3 != self.W3:
            return False
        if other.W4 != self.W4:
            return False
        if other.W5 != self.W5:
            return False
        if other.W6 != self.W6:
            return False
        if other.W7 != self.W7:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        if other.magnet_1 != self.magnet_1:
            return False
        if other.magnet_2 != self.magnet_2:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from HoleMag
        diff_list.extend(
            super(HoleM51, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._H0 is not None
            and self._H0 is not None
            and np.isnan(other._H0)
            and np.isnan(self._H0)
        ):
            pass
        elif other._H0 != self._H0:
            if is_add_value:
                val_str = " (self=" + str(self._H0) + ", other=" + str(other._H0) + ")"
                diff_list.append(name + ".H0" + val_str)
            else:
                diff_list.append(name + ".H0")
        if (
            other._H1 is not None
            and self._H1 is not None
            and np.isnan(other._H1)
            and np.isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        if (
            other._H2 is not None
            and self._H2 is not None
            and np.isnan(other._H2)
            and np.isnan(self._H2)
        ):
            pass
        elif other._H2 != self._H2:
            if is_add_value:
                val_str = " (self=" + str(self._H2) + ", other=" + str(other._H2) + ")"
                diff_list.append(name + ".H2" + val_str)
            else:
                diff_list.append(name + ".H2")
        if (
            other._W0 is not None
            and self._W0 is not None
            and np.isnan(other._W0)
            and np.isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        if (
            other._W1 is not None
            and self._W1 is not None
            and np.isnan(other._W1)
            and np.isnan(self._W1)
        ):
            pass
        elif other._W1 != self._W1:
            if is_add_value:
                val_str = " (self=" + str(self._W1) + ", other=" + str(other._W1) + ")"
                diff_list.append(name + ".W1" + val_str)
            else:
                diff_list.append(name + ".W1")
        if (
            other._W2 is not None
            and self._W2 is not None
            and np.isnan(other._W2)
            and np.isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
        if (
            other._W3 is not None
            and self._W3 is not None
            and np.isnan(other._W3)
            and np.isnan(self._W3)
        ):
            pass
        elif other._W3 != self._W3:
            if is_add_value:
                val_str = " (self=" + str(self._W3) + ", other=" + str(other._W3) + ")"
                diff_list.append(name + ".W3" + val_str)
            else:
                diff_list.append(name + ".W3")
        if (
            other._W4 is not None
            and self._W4 is not None
            and np.isnan(other._W4)
            and np.isnan(self._W4)
        ):
            pass
        elif other._W4 != self._W4:
            if is_add_value:
                val_str = " (self=" + str(self._W4) + ", other=" + str(other._W4) + ")"
                diff_list.append(name + ".W4" + val_str)
            else:
                diff_list.append(name + ".W4")
        if (
            other._W5 is not None
            and self._W5 is not None
            and np.isnan(other._W5)
            and np.isnan(self._W5)
        ):
            pass
        elif other._W5 != self._W5:
            if is_add_value:
                val_str = " (self=" + str(self._W5) + ", other=" + str(other._W5) + ")"
                diff_list.append(name + ".W5" + val_str)
            else:
                diff_list.append(name + ".W5")
        if (
            other._W6 is not None
            and self._W6 is not None
            and np.isnan(other._W6)
            and np.isnan(self._W6)
        ):
            pass
        elif other._W6 != self._W6:
            if is_add_value:
                val_str = " (self=" + str(self._W6) + ", other=" + str(other._W6) + ")"
                diff_list.append(name + ".W6" + val_str)
            else:
                diff_list.append(name + ".W6")
        if (
            other._W7 is not None
            and self._W7 is not None
            and np.isnan(other._W7)
            and np.isnan(self._W7)
        ):
            pass
        elif other._W7 != self._W7:
            if is_add_value:
                val_str = " (self=" + str(self._W7) + ", other=" + str(other._W7) + ")"
                diff_list.append(name + ".W7" + val_str)
            else:
                diff_list.append(name + ".W7")
        if (other.magnet_0 is None and self.magnet_0 is not None) or (
            other.magnet_0 is not None and self.magnet_0 is None
        ):
            diff_list.append(name + ".magnet_0 None mismatch")
        elif self.magnet_0 is not None:
            diff_list.extend(
                self.magnet_0.compare(
                    other.magnet_0,
                    name=name + ".magnet_0",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.magnet_1 is None and self.magnet_1 is not None) or (
            other.magnet_1 is not None and self.magnet_1 is None
        ):
            diff_list.append(name + ".magnet_1 None mismatch")
        elif self.magnet_1 is not None:
            diff_list.extend(
                self.magnet_1.compare(
                    other.magnet_1,
                    name=name + ".magnet_1",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.magnet_2 is None and self.magnet_2 is not None) or (
            other.magnet_2 is not None and self.magnet_2 is None
        ):
            diff_list.append(name + ".magnet_2 None mismatch")
        elif self.magnet_2 is not None:
            diff_list.extend(
                self.magnet_2.compare(
                    other.magnet_2,
                    name=name + ".magnet_2",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from HoleMag
        S += super(HoleM51, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W0)
        S += getsizeof(self.W1)
        S += getsizeof(self.W2)
        S += getsizeof(self.W3)
        S += getsizeof(self.W4)
        S += getsizeof(self.W5)
        S += getsizeof(self.W6)
        S += getsizeof(self.W7)
        S += getsizeof(self.magnet_0)
        S += getsizeof(self.magnet_1)
        S += getsizeof(self.magnet_2)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from HoleMag
        HoleM51_dict = super(HoleM51, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM51_dict["H0"] = self.H0
        HoleM51_dict["H1"] = self.H1
        HoleM51_dict["H2"] = self.H2
        HoleM51_dict["W0"] = self.W0
        HoleM51_dict["W1"] = self.W1
        HoleM51_dict["W2"] = self.W2
        HoleM51_dict["W3"] = self.W3
        HoleM51_dict["W4"] = self.W4
        HoleM51_dict["W5"] = self.W5
        HoleM51_dict["W6"] = self.W6
        HoleM51_dict["W7"] = self.W7
        if self.magnet_0 is None:
            HoleM51_dict["magnet_0"] = None
        else:
            HoleM51_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_1 is None:
            HoleM51_dict["magnet_1"] = None
        else:
            HoleM51_dict["magnet_1"] = self.magnet_1.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_2 is None:
            HoleM51_dict["magnet_2"] = None
        else:
            HoleM51_dict["magnet_2"] = self.magnet_2.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM51_dict["__class__"] = "HoleM51"
        return HoleM51_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        H1_val = self.H1
        H2_val = self.H2
        W0_val = self.W0
        W1_val = self.W1
        W2_val = self.W2
        W3_val = self.W3
        W4_val = self.W4
        W5_val = self.W5
        W6_val = self.W6
        W7_val = self.W7
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        if self.magnet_1 is None:
            magnet_1_val = None
        else:
            magnet_1_val = self.magnet_1.copy()
        if self.magnet_2 is None:
            magnet_2_val = None
        else:
            magnet_2_val = self.magnet_2.copy()
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            H0=H0_val,
            H1=H1_val,
            H2=H2_val,
            W0=W0_val,
            W1=W1_val,
            W2=W2_val,
            W3=W3_val,
            W4=W4_val,
            W5=W5_val,
            W6=W6_val,
            W7=W7_val,
            magnet_0=magnet_0_val,
            magnet_1=magnet_1_val,
            magnet_2=magnet_2_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H0 = None
        self.H1 = None
        self.H2 = None
        self.W0 = None
        self.W1 = None
        self.W2 = None
        self.W3 = None
        self.W4 = None
        self.W5 = None
        self.W6 = None
        self.W7 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        if self.magnet_1 is not None:
            self.magnet_1._set_None()
        if self.magnet_2 is not None:
            self.magnet_2._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM51, self)._set_None()

    def _get_H0(self):
        """getter of H0"""
        return self._H0

    def _set_H0(self, value):
        """setter of H0"""
        check_var("H0", value, "float", Vmin=0)
        self._H0 = value

    H0 = property(
        fget=_get_H0,
        fset=_set_H0,
        doc="""Hole depth

        :Type: float
        :min: 0
        """,
    )

    def _get_H1(self):
        """getter of H1"""
        return self._H1

    def _set_H1(self, value):
        """setter of H1"""
        check_var("H1", value, "float", Vmin=0)
        self._H1 = value

    H1 = property(
        fget=_get_H1,
        fset=_set_H1,
        doc="""Distance from the lamination Bore

        :Type: float
        :min: 0
        """,
    )

    def _get_H2(self):
        """getter of H2"""
        return self._H2

    def _set_H2(self, value):
        """setter of H2"""
        check_var("H2", value, "float", Vmin=0)
        self._H2 = value

    H2 = property(
        fget=_get_H2,
        fset=_set_H2,
        doc="""Hole width

        :Type: float
        :min: 0
        """,
    )

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""Hole bottom width

        :Type: float
        :min: 0
        """,
    )

    def _get_W1(self):
        """getter of W1"""
        return self._W1

    def _set_W1(self, value):
        """setter of W1"""
        check_var("W1", value, "float", Vmin=0)
        self._W1 = value

    W1 = property(
        fget=_get_W1,
        fset=_set_W1,
        doc="""Hole angular width

        :Type: float
        :min: 0
        """,
    )

    def _get_W2(self):
        """getter of W2"""
        return self._W2

    def _set_W2(self, value):
        """setter of W2"""
        check_var("W2", value, "float", Vmin=0)
        self._W2 = value

    W2 = property(
        fget=_get_W2,
        fset=_set_W2,
        doc="""magnet_1 position

        :Type: float
        :min: 0
        """,
    )

    def _get_W3(self):
        """getter of W3"""
        return self._W3

    def _set_W3(self, value):
        """setter of W3"""
        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

    W3 = property(
        fget=_get_W3,
        fset=_set_W3,
        doc="""magnet_1 width

        :Type: float
        :min: 0
        """,
    )

    def _get_W4(self):
        """getter of W4"""
        return self._W4

    def _set_W4(self, value):
        """setter of W4"""
        check_var("W4", value, "float", Vmin=0)
        self._W4 = value

    W4 = property(
        fget=_get_W4,
        fset=_set_W4,
        doc="""magnet_2 position

        :Type: float
        :min: 0
        """,
    )

    def _get_W5(self):
        """getter of W5"""
        return self._W5

    def _set_W5(self, value):
        """setter of W5"""
        check_var("W5", value, "float", Vmin=0)
        self._W5 = value

    W5 = property(
        fget=_get_W5,
        fset=_set_W5,
        doc="""magnet_2 width

        :Type: float
        :min: 0
        """,
    )

    def _get_W6(self):
        """getter of W6"""
        return self._W6

    def _set_W6(self, value):
        """setter of W6"""
        check_var("W6", value, "float", Vmin=0)
        self._W6 = value

    W6 = property(
        fget=_get_W6,
        fset=_set_W6,
        doc="""magnet_0 position

        :Type: float
        :min: 0
        """,
    )

    def _get_W7(self):
        """getter of W7"""
        return self._W7

    def _set_W7(self, value):
        """setter of W7"""
        check_var("W7", value, "float", Vmin=0)
        self._W7 = value

    W7 = property(
        fget=_get_W7,
        fset=_set_W7,
        doc="""magnet_0 width

        :Type: float
        :min: 0
        """,
    )

    def _get_magnet_0(self):
        """getter of magnet_0"""
        return self._magnet_0

    def _set_magnet_0(self, value):
        """setter of magnet_0"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_0"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_0")
            value = Magnet()
        check_var("magnet_0", value, "Magnet")
        self._magnet_0 = value

        if self._magnet_0 is not None:
            self._magnet_0.parent = self

    magnet_0 = property(
        fget=_get_magnet_0,
        fset=_set_magnet_0,
        doc="""First Magnet

        :Type: Magnet
        """,
    )

    def _get_magnet_1(self):
        """getter of magnet_1"""
        return self._magnet_1

    def _set_magnet_1(self, value):
        """setter of magnet_1"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_1"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_1")
            value = Magnet()
        check_var("magnet_1", value, "Magnet")
        self._magnet_1 = value

        if self._magnet_1 is not None:
            self._magnet_1.parent = self

    magnet_1 = property(
        fget=_get_magnet_1,
        fset=_set_magnet_1,
        doc="""Second Magnet

        :Type: Magnet
        """,
    )

    def _get_magnet_2(self):
        """getter of magnet_2"""
        return self._magnet_2

    def _set_magnet_2(self, value):
        """setter of magnet_2"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_2"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_2")
            value = Magnet()
        check_var("magnet_2", value, "Magnet")
        self._magnet_2 = value

        if self._magnet_2 is not None:
            self._magnet_2.parent = self

    magnet_2 = property(
        fget=_get_magnet_2,
        fset=_set_magnet_2,
        doc="""Third Magnet

        :Type: Magnet
        """,
    )

    class MachineCheckError(Exception):
        """ """

        pass

    class LaminationCheckError(MachineCheckError):
        """ """

        pass

    class SlotCheckError(LaminationCheckError):
        """ """

        pass

    class S51_NoneError(SlotCheckError):
        """Raised when a propery of HoleM51 is None"""

        pass

    class S51_AlphaCheckError(SlotCheckError):
        """ """

        pass

    class S51_WCheckError(SlotCheckError):
        """ """

        pass

    class S51_RHCheckError(SlotCheckError):
        """ """

        pass


MachineCheckError = HoleM51.MachineCheckError

LaminationCheckError = HoleM51.LaminationCheckError

SlotCheckError = HoleM51.SlotCheckError

S51_NoneError = HoleM51.S51_NoneError

S51_AlphaCheckError = HoleM51.S51_AlphaCheckError

S51_WCheckError = HoleM51.S51_WCheckError

S51_RHCheckError = HoleM51.S51_RHCheckError
