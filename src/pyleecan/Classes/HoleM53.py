# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/HoleM53.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM53
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.HoleMag import HoleMag

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Slot.HoleM53.check import check
from numpy import cos, exp, sin, pi, angle
from pyleecan.Functions.Geometry.inter_line_circle import inter_line_circle
from pyleecan.Methods.Slot.HoleM53 import Slot53InterError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Functions.labels import HOLEM_LAB
import matplotlib.pyplot as plt
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from pyleecan.Methods import ParentMissingError

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class HoleM53(HoleMag):
    """V shape slot for buried magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.HoleM53._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """
        Rext = self.get_Rext()

        Z7 = Rext - self.H0 - 1j * self.W1 / 2
        Z6 = Z7 - 1j * (self.H2 - self.H3) * cos(self.W4)
        Z8 = Z7 + (self.H2 - self.H3) * sin(self.W4)

        # Compute the coordinate in the ref of Z6 with rotation -W4
        Z5 = self.W2 * exp(-1j * self.W4) + Z6
        Z4 = (self.W2 - 1j * self.H3) * exp(-1j * self.W4) + Z6
        Z3 = (self.W2 + self.W3 - 1j * self.H3) * exp(-1j * self.W4) + Z6
        Z2 = (self.W2 + self.W3) * exp(-1j * self.W4) + Z6
        Z9 = (self.W2 + 1j * (self.H2 - self.H3)) * exp(-1j * self.W4) + Z6
        Z10 = (self.W2 + self.W3 + 1j * (self.H2 - self.H3)) * exp(-1j * self.W4) + Z6

        # Z1 and Z11 are defined as intersection between line and circle
        Zlist = inter_line_circle(Z8, Z10, Rext - self.H1)
        if len(Zlist) == 2 and Zlist[0].imag < 0 and Zlist[0].real > 0:
            Z11 = Zlist[0]
        elif len(Zlist) == 2 and Zlist[1].imag < 0 and Zlist[1].real > 0:
            Z11 = Zlist[1]
        else:
            raise Slot53InterError("ERROR: Slot 53, Can't find Z11 coordinates")

        Zlist = inter_line_circle(Z2, Z6, Rext - self.H1)
        if len(Zlist) == 2 and Zlist[0].imag < 0 and Zlist[0].real > 0:
            Z1 = Zlist[0]
        elif len(Zlist) == 2 and Zlist[1].imag < 0 and Zlist[1].real > 0:
            Z1 = Zlist[1]
        else:
            raise Slot53InterError("ERROR: Slot 53, Can't find Z1 coordinates")

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
        point_dict["Z1s"] = Z1.conjugate()
        point_dict["Z2s"] = Z2.conjugate()
        point_dict["Z3s"] = Z3.conjugate()
        point_dict["Z4s"] = Z4.conjugate()
        point_dict["Z5s"] = Z5.conjugate()
        point_dict["Z6s"] = Z6.conjugate()
        point_dict["Z7s"] = Z7.conjugate()
        point_dict["Z8s"] = Z8.conjugate()
        point_dict["Z9s"] = Z9.conjugate()
        point_dict["Z10s"] = Z10.conjugate()
        point_dict["Z11s"] = Z11.conjugate()
        return point_dict

    # cf Methods.Slot.HoleM53.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Hole.
        The ending point of a curve is the starting point of the next curve in the
        list

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of Magnet Surface and Air Surface on the slot

        """
        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

        # Get all the points
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]
        Z9 = point_dict["Z9"]
        Z10 = point_dict["Z10"]
        Z11 = point_dict["Z11"]

        Z1s = point_dict["Z1s"]
        Z2s = point_dict["Z2s"]
        Z3s = point_dict["Z3s"]
        Z4s = point_dict["Z4s"]
        Z5s = point_dict["Z5s"]
        Z6s = point_dict["Z6s"]
        Z7s = point_dict["Z7s"]
        Z8s = point_dict["Z8s"]
        Z9s = point_dict["Z9s"]
        Z10s = point_dict["Z10s"]
        Z11s = point_dict["Z11s"]
        Rext = self.get_Rext()

        # Air surface with magnet_0
        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z10))
        curve_list.append(Segment(Z10, Z11))
        curve_list.append(
            Arc1(begin=Z11, end=Z1, radius=-Rext + self.H1, is_trigo_direction=False)
        )
        point_ref = (Z1 + Z2 + Z10 + Z11) / 4
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # magnet_0 surface
        curve_list = list()
        if is_simplified:
            curve_list.append(Segment(Z5, Z9))
            curve_list.append(Segment(Z2, Z10))
        else:
            curve_list.append(Segment(Z3, Z4))
            curve_list.append(Segment(Z4, Z9))
            curve_list.append(Segment(Z9, Z10))
            curve_list.append(Segment(Z10, Z3))
        point_ref = (Z3 + Z4 + Z9 + Z10) / 4

        S2 = SurfLine(
            line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref
        )

        # Air suface with magnet_0 and W1 > 0
        curve_list = list()
        if self.W2 > 0:
            curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z7))
        curve_list.append(Segment(Z7, Z8))
        if self.W2 > 0:
            curve_list.append(Segment(Z8, Z9))
            curve_list.append(Segment(Z9, Z5))
            point_ref = (Z5 + Z6 + Z7 + Z8 + Z9) / 5
        else:
            curve_list.append(Segment(Z8, Z6))
            point_ref = (Z6 + Z7 + Z8) / 3
        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface with magnet_1
        curve_list = list()
        curve_list.append(Segment(Z1s, Z2s))
        curve_list.append(Segment(Z2s, Z10s))
        curve_list.append(Segment(Z10s, Z11s))
        curve_list.append(Arc1(Z11s, Z1s, Rext - self.H1, is_trigo_direction=True))
        point_ref = (Z1s + Z2s + Z10s + Z11s) / 4
        S4 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # magnet_1 surface
        curve_list = list()
        if is_simplified:
            curve_list.append(Segment(Z5s, Z9s))
            curve_list.append(Segment(Z2s, Z10s))
        else:
            curve_list.append(Segment(Z3s, Z4s))
            curve_list.append(Segment(Z4s, Z9s))
            curve_list.append(Segment(Z9s, Z10s))
            curve_list.append(Segment(Z10s, Z3s))
        point_ref = (Z3s + Z4s + Z9s + Z10s) / 4
        S5 = SurfLine(
            line_list=curve_list, label=mag_label + "T1-S0", point_ref=point_ref
        )

        # Air suface with magnet_1 and W1 > 0
        curve_list = list()
        if self.W2 > 0:
            curve_list.append(Segment(Z5s, Z6s))
        curve_list.append(Segment(Z6s, Z7s))
        curve_list.append(Segment(Z7s, Z8s))
        if self.W2 > 0:
            curve_list.append(Segment(Z8s, Z9s))
            curve_list.append(Segment(Z9s, Z5s))
            point_ref = (Z5s + Z6s + Z7s + Z8s + Z9s) / 5
        else:
            curve_list.append(Segment(Z8s, Z6s))
            point_ref = (Z6s + Z7s + Z8s) / 3
        S6 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air with both magnet and W1 = 0
        curve_list = list()
        if self.W2 > 0:
            curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z6s))
        if self.W2 > 0:
            curve_list.append(Segment(Z6s, Z5s))
        curve_list.append(Segment(Z5s, Z9s))
        if self.W2 > 0:
            curve_list.append(Segment(Z9s, Z8s))
            curve_list.append(Segment(Z8s, Z9))
        curve_list.append(Segment(Z9, Z5))
        point_ref = (Z6 + Z6s + Z8) / 3
        S7 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # first hole without magnet_0 and W1 > 0
        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        if self.H3 > 0:
            curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z4))
        if self.H3 > 0:
            curve_list.append(Segment(Z4, Z5))
        if self.W2 > 0:
            curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z7))
        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z11))
        curve_list.append(Arc1(Z11, Z1, -Rext + self.H1, is_trigo_direction=False))
        point_ref = (Z3 + Z4 + Z9 + Z10) / 4
        S8 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # second hole without magnet_1 and W1 > 0
        curve_list = list()
        curve_list.append(Segment(Z1s, Z2s))
        if self.H3 > 0:
            curve_list.append(Segment(Z2s, Z3s))
        curve_list.append(Segment(Z3s, Z4s))
        if self.H3 > 0:
            curve_list.append(Segment(Z4s, Z5s))
        if self.W2 > 0:
            curve_list.append(Segment(Z5s, Z6s))
        curve_list.append(Segment(Z6s, Z7s))
        curve_list.append(Segment(Z7s, Z8s))
        curve_list.append(Segment(Z8s, Z11s))
        curve_list.append(Arc1(Z11s, Z1s, -Rext + self.H1, is_trigo_direction=False))
        point_ref = (Z3s + Z4s + Z9s + Z10s) / 4
        S9 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # No magnet_1 and W1 = 0
        curve_list = list()
        curve_list.append(Segment(Z1s, Z2s))
        if self.H3 > 0:
            curve_list.append(Segment(Z2s, Z3s))
        curve_list.append(Segment(Z3s, Z4s))
        if self.H3 > 0:
            curve_list.append(Segment(Z4s, Z5s))
        if self.W2 > 0:
            curve_list.append(Segment(Z5s, Z6s))
        curve_list.append(Segment(Z6s, Z6))
        if self.W2 > 0:
            curve_list.append(Segment(Z6, Z5))
        curve_list.append(Segment(Z5, Z9))
        if self.W2 > 0:
            curve_list.append(Segment(Z9, Z8))
        curve_list.append(Segment(Z8s, Z11s))
        curve_list.append(Arc1(Z11s, Z1s, -Rext + self.H1, is_trigo_direction=False))
        point_ref = (Z3s + Z4s + Z9s + Z10s) / 4
        S10 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # No magnet_0 and W1 = 0
        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        if self.H3 > 0:
            curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z4))
        if self.H3 > 0:
            curve_list.append(Segment(Z4, Z5))
        if self.W2 > 0:
            curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z6s))
        if self.W2 > 0:
            curve_list.append(Segment(Z6s, Z5s))
        curve_list.append(Segment(Z5s, Z9s))
        if self.W2 > 0:
            curve_list.append(Segment(Z9s, Z8s))
        curve_list.append(Segment(Z8, Z11))
        curve_list.append(Arc1(Z11, Z1, -Rext + self.H1, is_trigo_direction=False))
        point_ref = (Z3 + Z4 + Z9 + Z10) / 4
        S11 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # No magnet and W1 = 0
        curve_list = list()
        curve_list.append(Arc1(Z1, Z11, Rext - self.H1, is_trigo_direction=True))
        curve_list.append(Segment(Z11, Z8))
        curve_list.append(Segment(Z8, Z11s))
        curve_list.append(Arc1(Z11s, Z1s, Rext - self.H1, is_trigo_direction=True))
        curve_list.append(Segment(Z1s, Z2s))
        if self.H3 > 0:
            curve_list.append(Segment(Z2s, Z3s))
        curve_list.append(Segment(Z3s, Z4s))
        if self.H3 > 0:
            curve_list.append(Segment(Z4s, Z5s))
        if self.W2 > 0:
            curve_list.append(Segment(Z5s, Z6s))
        curve_list.append(Segment(Z6s, Z6))
        if self.W2 > 0:
            curve_list.append(Segment(Z6, Z5))
        if self.H3 > 0:
            curve_list.append(Segment(Z5, Z4))
        curve_list.append(Segment(Z4, Z3))
        if self.H3 > 0:
            curve_list.append(Segment(Z3, Z2))
        curve_list.append(Segment(Z2, Z1))

        point_ref = (Z6 + Z8 + Z6s) / 3
        S12 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Create the surface list by selecting the correct ones
        if self.magnet_0 and self.magnet_1 and self.W1 > 0:
            S1.label = vent_label + "T0-S0"  # Hole
            S3.label = vent_label + "T1-S0"  # Hole
            S6.label = vent_label + "T2-S0"  # Hole
            S4.label = vent_label + "T3-S0"  # Hole
            surf_list = [S1, S2, S3, S6, S5, S4]
        elif self.magnet_0 and self.magnet_1 and self.W1 == 0:
            S1.label = vent_label + "T0-S0"  # Hole
            S7.label = vent_label + "T1-S0"  # Hole
            S4.label = vent_label + "T2-S0"  # Hole
            surf_list = [S1, S2, S7, S5, S4]
        elif self.magnet_0 and not self.magnet_1 and self.W1 > 0:
            S1.label = vent_label + "T0-S0"  # Hole
            S3.label = vent_label + "T1-S0"  # Hole
            S9.label = vent_label + "T2-S0"  # Hole
            surf_list = [S1, S2, S3, S9]
        elif self.magnet_0 and not self.magnet_1 and self.W1 == 0:
            S1.label = vent_label + "T0-S0"  # Hole
            S10.label = vent_label + "T1-S0"  # Hole
            surf_list = [S1, S2, S10]
        elif not self.magnet_0 and self.magnet_1 and self.W1 > 0:
            S8.label = vent_label + "T0-S0"  # Hole
            S6.label = vent_label + "T1-S0"  # Hole
            S4.label = vent_label + "T2-S0"  # Hole
            surf_list = [S8, S6, S5, S4]
        elif not self.magnet_0 and self.magnet_1 and self.W1 == 0:
            S11.label = vent_label + "T0-S0"  # Hole
            S4.label = vent_label + "T2-S0"  # Hole
            surf_list = [S11, S5, S4]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 > 0:
            S8.label = vent_label + "T0-S0"  # Hole
            S9.label = vent_label + "T1-S0"  # Hole
            surf_list = [S8, S9]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 == 0:
            S12.label = vent_label + "T0-S0"  # Hole
            surf_list = [S12]

        # Apply the transformation
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.HoleM53.check
    check = check

    # cf Methods.Slot.HoleM53.comp_alpha
    def comp_alpha(self):
        """Compute the magnets angle of the slot type 53

        Parameters
        ----------
        self : HoleM53
            a HoleM53 object

        Returns
        -------
        alpha: float
            magnet angle [rad]
        """
        return pi / 2 - self.W4

    # cf Methods.Slot.HoleM53.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM53
            a HoleM53 object
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
        S0 = Segment(point_dict["Z4"], point_dict["Z3"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(point_dict["Z3s"], point_dict["Z4s"])
        mag_dict["magnet_1"] = S1.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += pi
            mag_dict["magnet_1"] += pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # cf Methods.Slot.HoleM53.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole [m]

        """

        Rext = self.get_Rext()

        Rmax = Rext - self.H1
        Z7 = Rext - self.H0 - 1j * self.W1 / 2
        Z6 = Z7 - 1j * (self.H2 - self.H3) * cos(self.W4)
        Z4 = (self.W2 - 1j * self.H3) * exp(-1j * self.W4) + Z6

        Rmin = min(abs(Z7), abs(Z4))
        return (Rmin, Rmax)

    # cf Methods.Slot.HoleM53.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        # all magnet has the same surface
        label = "magnet_" + str(index)
        if index in [0, 1] and getattr(self, label) is not None:
            return self.H2 * self.W3
        return 0

    # cf Methods.Slot.HoleM53.comp_W5
    def comp_W5(self):
        """Compute the W5 width of the hole (cf schematics)

        Parameters
        ----------
        self : HoleM53
            a HoleM53 object

        Returns
        -------
        W5: float
            Cf schematics [m]
        Raises
        --------
        Slot53InterError
            ERROR: Slot 53, Can't find Z11 coordinates

        """

        Rext = self.get_Rext()

        Z7 = Rext - self.H0 - 1j * self.W1 / 2
        Z8 = Z7 + (self.H2 - self.H3) * sin(self.W4)
        Z10 = (self.W2 + self.W3) * exp(-1j * self.W4) + Z8

        # Z1 and Z11 are defined as intersection between line and circle
        Zlist = inter_line_circle(Z8, Z10, Rext - self.H1)
        if len(Zlist) == 2 and Zlist[0].imag < 0 and Zlist[0].real > 0:
            Z11 = Zlist[0]
        elif len(Zlist) == 2 and Zlist[1].imag < 0 and Zlist[1].real > 0:
            Z11 = Zlist[1]
        else:
            raise Slot53InterError("ERROR: Slot 53, Can't find Z11 coordinates")

        return abs(Z11 - Z8) - self.W2 - self.W3

    # cf Methods.Slot.HoleM53.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None or self.magnet_1 is not None

    # cf Methods.Slot.HoleM53.plot_schematics
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
        self : HoleM53
            A HoleM53 object
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
                Zh=4,
                W1=15e-3,
                W2=20e-3,
                W3=50e-3,
                W4=pi / 3,
                H0=75e-3,
                H1=7.5e-3,
                H2=22.5e-3,
                H3=7.5e-3,
            )
            lam = LamHole(
                Rint=0.1, Rext=0.2, is_internal=True, is_stator=False, hole=[hole]
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
        elif type_add_active == 0:
            # Remove magnets
            lam = self.parent.copy()
            lam.hole[0].remove_magnet()
            return lam.hole[0].plot_schematics(
                is_default=False,
                is_add_point_label=is_add_point_label,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                type_add_active=2,
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
            alpha = pi / 2  # To rotate the schematics
            fig, ax = lam.plot(
                alpha=pi / self.Zh + alpha,
                is_show_fig=False,
                is_lam_only=type_add_active == 0,
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            sp = 2 * pi / self.Zh
            Rbo = self.get_Rbo()
            point_dict = self._comp_point_coordinate()

            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    Z = Z * exp(1j * alpha)
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Adding schematics
            if is_add_schematics:
                # W1
                line = Segment(
                    (point_dict["Z8"] + point_dict["Z7"]) / 2 * exp(1j * alpha),
                    (point_dict["Z8s"] + point_dict["Z7s"]) / 2 * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=self.W1 * 0.3 - 1j * self.W1 * 0.6,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W2
                line = Segment(
                    point_dict["Z8s"] * exp(1j * alpha),
                    point_dict["Z9s"] * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=(1 + 1j) * self.W1 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(
                    point_dict["Z10s"] * exp(1j * alpha),
                    point_dict["Z9s"] * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=(1 + 1j) * self.W1 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W4
                line = Arc1(
                    begin=point_dict["Z9"] * exp(1j * alpha),
                    end=(point_dict["Z8"] + self.W2) * exp(1j * alpha),
                    radius=self.W2,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W4",
                    offset_label=(1 + 1j) * self.W1 * 0.2,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(
                    point_dict["Z7"].real * exp(1j * alpha),
                    Rbo * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=(1 + 1j) * self.W1 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(
                    point_dict["Z1s"] * exp(1j * alpha),
                    Rbo * exp(1j * angle(point_dict["Z1s"])) * exp(1j * alpha),
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
                    (point_dict["Z3s"] + point_dict["Z4s"]) / 2 * exp(1j * alpha),
                    (point_dict["Z10s"] + point_dict["Z9s"]) / 2 * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=self.W1 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H3
                line = Segment(
                    point_dict["Z2"] * exp(1j * alpha),
                    point_dict["Z3"] * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H3",
                    offset_label=self.W1 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5 * exp(1j * alpha))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 radius
                line = Arc1(
                    begin=(Rbo - self.H1) * exp(-1j * pi / 2 * 0.9) * exp(1j * alpha),
                    end=(Rbo - self.H1) * exp(1j * pi / 2 * 0.9) * exp(1j * alpha),
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
                # W2 lines
                line = Segment(
                    point_dict["Z6"] * exp(1j * alpha),
                    point_dict["Z8"] * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z6s"] * exp(1j * alpha),
                    point_dict["Z8s"] * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 lines
                line = Segment(
                    0,
                    Rbo * 1.3 * exp(1j * angle(point_dict["Z1s"])) * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # W4 lines
                line = Segment(
                    point_dict["Z8"] * exp(1j * alpha),
                    (Rbo * 1.3 + 1j * point_dict["Z8"].imag) * exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = point_dict["Z1s"].imag * 1.05
            Rint = point_dict["Z7"].real * 0.9
            Rext = self.parent.Rext

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

    # cf Methods.Slot.HoleM53.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM53
            a HoleM53 object
        """

        self.magnet_0 = None
        self.magnet_1 = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        H0=0.003,
        H1=0,
        W1=0.013,
        H2=0.02,
        W2=0.01,
        H3=0.01,
        W3=0.01,
        W4=0.01,
        magnet_0=-1,
        magnet_1=-1,
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
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "H3" in list(init_dict.keys()):
                H3 = init_dict["H3"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "W4" in list(init_dict.keys()):
                W4 = init_dict["W4"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "magnet_1" in list(init_dict.keys()):
                magnet_1 = init_dict["magnet_1"]
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
        self.W1 = W1
        self.H2 = H2
        self.W2 = W2
        self.H3 = H3
        self.W3 = W3
        self.W4 = W4
        self.magnet_0 = magnet_0
        self.magnet_1 = magnet_1
        # Call HoleMag init
        super(HoleM53, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM53_str = ""
        # Get the properties inherited from HoleMag
        HoleM53_str += super(HoleM53, self).__str__()
        HoleM53_str += "H0 = " + str(self.H0) + linesep
        HoleM53_str += "H1 = " + str(self.H1) + linesep
        HoleM53_str += "W1 = " + str(self.W1) + linesep
        HoleM53_str += "H2 = " + str(self.H2) + linesep
        HoleM53_str += "W2 = " + str(self.W2) + linesep
        HoleM53_str += "H3 = " + str(self.H3) + linesep
        HoleM53_str += "W3 = " + str(self.W3) + linesep
        HoleM53_str += "W4 = " + str(self.W4) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM53_str += "magnet_0 = " + tmp
        else:
            HoleM53_str += "magnet_0 = None" + linesep + linesep
        if self.magnet_1 is not None:
            tmp = self.magnet_1.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM53_str += "magnet_1 = " + tmp
        else:
            HoleM53_str += "magnet_1 = None" + linesep + linesep
        return HoleM53_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM53, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W1 != self.W1:
            return False
        if other.H2 != self.H2:
            return False
        if other.W2 != self.W2:
            return False
        if other.H3 != self.H3:
            return False
        if other.W3 != self.W3:
            return False
        if other.W4 != self.W4:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        if other.magnet_1 != self.magnet_1:
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
            super(HoleM53, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._H0 is not None
            and self._H0 is not None
            and isnan(other._H0)
            and isnan(self._H0)
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
            and isnan(other._H1)
            and isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        if (
            other._W1 is not None
            and self._W1 is not None
            and isnan(other._W1)
            and isnan(self._W1)
        ):
            pass
        elif other._W1 != self._W1:
            if is_add_value:
                val_str = " (self=" + str(self._W1) + ", other=" + str(other._W1) + ")"
                diff_list.append(name + ".W1" + val_str)
            else:
                diff_list.append(name + ".W1")
        if (
            other._H2 is not None
            and self._H2 is not None
            and isnan(other._H2)
            and isnan(self._H2)
        ):
            pass
        elif other._H2 != self._H2:
            if is_add_value:
                val_str = " (self=" + str(self._H2) + ", other=" + str(other._H2) + ")"
                diff_list.append(name + ".H2" + val_str)
            else:
                diff_list.append(name + ".H2")
        if (
            other._W2 is not None
            and self._W2 is not None
            and isnan(other._W2)
            and isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
        if (
            other._H3 is not None
            and self._H3 is not None
            and isnan(other._H3)
            and isnan(self._H3)
        ):
            pass
        elif other._H3 != self._H3:
            if is_add_value:
                val_str = " (self=" + str(self._H3) + ", other=" + str(other._H3) + ")"
                diff_list.append(name + ".H3" + val_str)
            else:
                diff_list.append(name + ".H3")
        if (
            other._W3 is not None
            and self._W3 is not None
            and isnan(other._W3)
            and isnan(self._W3)
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
            and isnan(other._W4)
            and isnan(self._W4)
        ):
            pass
        elif other._W4 != self._W4:
            if is_add_value:
                val_str = " (self=" + str(self._W4) + ", other=" + str(other._W4) + ")"
                diff_list.append(name + ".W4" + val_str)
            else:
                diff_list.append(name + ".W4")
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from HoleMag
        S += super(HoleM53, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
        S += getsizeof(self.H3)
        S += getsizeof(self.W3)
        S += getsizeof(self.W4)
        S += getsizeof(self.magnet_0)
        S += getsizeof(self.magnet_1)
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
        HoleM53_dict = super(HoleM53, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM53_dict["H0"] = self.H0
        HoleM53_dict["H1"] = self.H1
        HoleM53_dict["W1"] = self.W1
        HoleM53_dict["H2"] = self.H2
        HoleM53_dict["W2"] = self.W2
        HoleM53_dict["H3"] = self.H3
        HoleM53_dict["W3"] = self.W3
        HoleM53_dict["W4"] = self.W4
        if self.magnet_0 is None:
            HoleM53_dict["magnet_0"] = None
        else:
            HoleM53_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_1 is None:
            HoleM53_dict["magnet_1"] = None
        else:
            HoleM53_dict["magnet_1"] = self.magnet_1.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM53_dict["__class__"] = "HoleM53"
        return HoleM53_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        H1_val = self.H1
        W1_val = self.W1
        H2_val = self.H2
        W2_val = self.W2
        H3_val = self.H3
        W3_val = self.W3
        W4_val = self.W4
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        if self.magnet_1 is None:
            magnet_1_val = None
        else:
            magnet_1_val = self.magnet_1.copy()
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
            W1=W1_val,
            H2=H2_val,
            W2=W2_val,
            H3=H3_val,
            W3=W3_val,
            W4=W4_val,
            magnet_0=magnet_0_val,
            magnet_1=magnet_1_val,
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
        self.W1 = None
        self.H2 = None
        self.W2 = None
        self.H3 = None
        self.W3 = None
        self.W4 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        if self.magnet_1 is not None:
            self.magnet_1._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM53, self)._set_None()

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
        doc="""Slot depth

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
        doc="""Tooth width (at V bottom)

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
        doc="""Magnet Height

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
        doc="""Distance Magnet to bottom of the V

        :Type: float
        :min: 0
        """,
    )

    def _get_H3(self):
        """getter of H3"""
        return self._H3

    def _set_H3(self, value):
        """setter of H3"""
        check_var("H3", value, "float", Vmin=0)
        self._H3 = value

    H3 = property(
        fget=_get_H3,
        fset=_set_H3,
        doc="""Additional depth for the magnet

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
        doc="""Magnet Width

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
        doc="""Slot angle

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
