# File generated according to Generator/ClassesRef/Slot/SlotW30.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW30"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Slot import Slot
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var
from pyleecan.definitions import config_dict
from pyleecan.Functions.Geometry.inter_line_circle import inter_line_circle
from pyleecan.Functions.Geometry.inter_line_line import inter_line_line
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
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import DRAW_PROP_LAB, SOP_LAB, WIND_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class SlotW30(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.SlotW30._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        if self.R1 != 0:
            Z3 = point_dict["Z3"]
            Z4 = point_dict["Z4"]
            Z9 = point_dict["Z9"]
            Z10 = point_dict["Z10"]

        else:
            Z40 = point_dict["Z40"]
            Z100 = point_dict["Z100"]

        if self.R2 != 0:
            Z5 = point_dict["Z5"]
            Z6 = point_dict["Z6"]
            Z7 = point_dict["Z7"]
            Z8 = point_dict["Z8"]

        else:
            Z60 = point_dict["Z60"]
            Z80 = point_dict["Z80"]

        Z11 = point_dict["Z11"]
        Z12 = point_dict["Z12"]

        # Creation of curve
        line_dict = dict()

        # Closing Arc (Rbo)
        line_dict["12-1"] = Arc1(Z12, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-11"] = Segment(Z2, Z11)
        line_dict["11-2"] = Segment(Z11, Z2)

        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
            line_dict["11-12"] = Segment(Z11, Z12)
        else:
            line_dict["1-2"] = None
            line_dict["11-12"] = None

        if self.is_outwards():
            if self.R1 != 0 and self.R2 != 0:
                line_dict["2-3"] = Segment(Z2, Z3)
                line_dict["3-4"] = Arc1(Z3, Z4, self.R1)
                line_dict["4-5"] = Segment(Z4, Z5)
                line_dict["5-6"] = Arc1(Z5, Z6, self.R2)
                line_dict["6-7"] = Segment(Z6, Z7)
                line_dict["7-8"] = Arc1(Z7, Z8, self.R2)
                line_dict["8-9"] = Segment(Z8, Z9)
                line_dict["9-10"] = Arc1(Z9, Z10, self.R1)
                line_dict["10-11"] = Segment(Z10, Z11)

            elif self.R1 == 0 and self.R2 != 0:
                line_dict["2-40"] = Segment(Z2, Z40)
                line_dict["40-5"] = Segment(Z40, Z5)
                line_dict["5-6"] = Arc1(Z5, Z6, self.R2)
                line_dict["6-7"] = Segment(Z6, Z7)
                line_dict["7-8"] = Arc1(Z7, Z8, self.R2)
                line_dict["8-100"] = Segment(Z8, Z100)
                line_dict["100-11"] = Segment(Z100, Z11)

            elif self.R1 != 0 and self.R2 == 0:
                line_dict["2-3"] = Segment(Z2, Z3)
                line_dict["3-4"] = Arc1(Z3, Z4, self.R1)
                line_dict["4-60"] = Segment(Z4, Z60)
                line_dict["60-80"] = Segment(Z60, Z80)
                line_dict["80-9"] = Segment(Z80, Z9)
                line_dict["9-10"] = Arc1(Z9, Z10, self.R1)
                line_dict["10-11"] = Segment(Z10, Z11)

            elif self.R1 == 0 and self.R2 == 0:
                line_dict["2-40"] = Segment(Z2, Z40)
                line_dict["40-60"] = Segment(Z40, Z60)
                line_dict["60-80"] = Segment(Z60, Z80)
                line_dict["80-100"] = Segment(Z80, Z100)
                line_dict["100-11"] = Segment(Z100, Z11)

        else:
            if self.R1 != 0 and self.R2 != 0:
                line_dict["2-3"] = Segment(Z2, Z3)
                line_dict["3-4"] = Arc1(Z3, Z4, -self.R1, False)
                line_dict["4-5"] = Segment(Z4, Z5)
                line_dict["5-6"] = Arc1(Z5, Z6, -self.R2, False)
                line_dict["6-7"] = Segment(Z6, Z7)
                line_dict["7-8"] = Arc1(Z7, Z8, -self.R2, False)
                line_dict["8-9"] = Segment(Z8, Z9)
                line_dict["9-10"] = Arc1(Z9, Z10, -self.R1, False)
                line_dict["10-11"] = Segment(Z10, Z11)

            elif self.R1 == 0 and self.R2 != 0:
                line_dict["2-40"] = Segment(Z2, Z40)
                line_dict["40-5"] = Segment(Z40, Z5)
                line_dict["5-6"] = Arc1(Z5, Z6, -self.R2, False)
                line_dict["6-7"] = Segment(Z6, Z7)
                line_dict["7-8"] = Arc1(Z7, Z8, -self.R2, False)
                line_dict["8-100"] = Segment(Z8, Z100)
                line_dict["100-11"] = Segment(Z100, Z11)

            elif self.R1 != 0 and self.R2 == 0:
                line_dict["2-3"] = Segment(Z2, Z3)
                line_dict["3-4"] = Arc1(Z3, Z4, -self.R1, False)
                line_dict["4-60"] = Segment(Z4, Z60)
                line_dict["60-80"] = Segment(Z60, Z80)
                line_dict["80-9"] = Segment(Z80, Z9)
                line_dict["9-10"] = Arc1(Z9, Z10, -self.R1, False)
                line_dict["10-11"] = Segment(Z10, Z11)

            elif self.R1 == 0 and self.R2 == 0:
                line_dict["2-40"] = Segment(Z2, Z40)
                line_dict["40-60"] = Segment(Z40, Z60)
                line_dict["60-80"] = Segment(Z60, Z80)
                line_dict["80-100"] = Segment(Z80, Z100)
                line_dict["100-11"] = Segment(Z100, Z11)

        return line_dict

    # cf Methods.Slot.SlotW30._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z12|| = W0
        alpha = np.arcsin(self.W0 / (2 * Rbo))
        hsp = np.pi / self.Zs  # Half slot pitch

        Z0 = Rbo * np.exp(1j * 0)
        Z12 = Z0 * np.exp(1j * alpha)

        if self.is_outwards():
            Z11 = Z12 + self.H0

            Zp1 = Rbo * np.exp(1j * hsp)
            Zp2 = 2 * Rbo * np.exp(1j * hsp)
            Zp1 = Zp1 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j
            Zp2 = Zp2 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j

            Zp1 = Zp1 * np.exp(1j * hsp)
            Zp2 = Zp2 * np.exp(1j * hsp)

            Zp3 = Z12.real + self.H0 + self.H1
            Zp4 = Z12.real + self.H0 + self.H1 + 1j

            if self.R2 == 0:
                Zc1 = inter_line_line(Zp1, Zp2, Zp3, Zp4)
                Z80 = Zc1[0]

            else:
                ZR1 = Rbo * np.exp(1j * hsp)
                ZR2 = 2 * Rbo * np.exp(1j * hsp)
                ZR1 = ZR1 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R2 * 1j
                ZR2 = ZR2 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R2 * 1j

                ZR1 = ZR1 * np.exp(1j * hsp)
                ZR2 = ZR2 * np.exp(1j * hsp)

                ZR3 = Z12.real + self.H0 + self.H1 - self.R2
                ZR4 = Z12.real + self.H0 + self.H1 - self.R2 + 1j

                ZcenterR2 = inter_line_line(ZR2, ZR1, ZR3, ZR4)

                Z8 = inter_line_circle(Zp1, Zp2, self.R2, ZcenterR2[0])
                Z7 = inter_line_circle(Zp3, Zp4 + 1j, self.R2, ZcenterR2[0])

                # we can have approximation, but we want a line tangent. So we can approximate coordinate center of cercle at 10e-6
                if len(Z8) == 0:
                    Z8 = inter_line_circle(Zp1, Zp2, self.R2, ZcenterR2[0] + 1e-6 * 1j)

                if len(Z7) == 0:
                    Z7 = inter_line_circle(Zp3, Zp4 + 1j, self.R2, ZcenterR2[0] + 1e-6)

                Z8 = Z8[0]
                Z7 = Z7[0]
                Zc3 = ZcenterR2[0]

            Zp5 = Z11
            Zp6 = Z11 + 1j

            if self.R1 == 0:
                Zc2 = inter_line_line(Zp5, Zp6, Zp1, Zp2)
                Z100 = Zc2[0]

            else:
                Zt1 = Rbo * np.exp(1j * hsp)
                Zt2 = 2 * Rbo * np.exp(1j * hsp)
                Zt1 = Zt1 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R1 * 1j
                Zt2 = Zt2 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R1 * 1j

                Zt1 = Zt1 * np.exp(1j * hsp)
                Zt2 = Zt2 * np.exp(1j * hsp)

                Zt3 = Z12.real + self.H0 + self.R1
                Zt4 = Z12.real + self.H0 + self.R1 + 1j

                ZcenterR1 = inter_line_line(Zt2, Zt1, Zt3, Zt4)

                Z9 = inter_line_circle(Zp1, Zp2, self.R1, ZcenterR1[0])
                Z10 = inter_line_circle(Zp5, Zp6, self.R1, ZcenterR1[0])

                # we can have approximation, but we want a line tangent. So we can approximate coordinate center of cercle at 10e-6
                if len(Z9) == 0:
                    Z9 = inter_line_circle(Zp1, Zp2, self.R1, ZcenterR1[0] + 1e-6 * 1j)

                if len(Z10) == 0:
                    Z10 = inter_line_circle(Zp5, Zp6, self.R1, ZcenterR1[0] - 1e-6)

                Z9 = Z9[0]
                Z10 = Z10[0]
                Zc4 = ZcenterR1[0]

        # is internal
        else:
            Z11 = Z12 - self.H0

            Zp1 = Rbo * np.exp(1j * hsp)
            Zp2 = 2 * Rbo * np.exp(1j * hsp)
            Zp1 = Zp1 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j
            Zp2 = Zp2 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j

            Zp1 = Zp1 * np.exp(1j * hsp)
            Zp2 = Zp2 * np.exp(1j * hsp)

            Zp3 = Z12.real - self.H0 - self.H1
            Zp4 = Z12.real - self.H0 - self.H1 + 1j

            if self.R2 == 0:
                Zc1 = inter_line_line(Zp1, Zp2, Zp3, Zp4)
                Z80 = Zc1[0]

            else:
                ZR1 = Rbo * np.exp(1j * hsp)
                ZR2 = 2 * Rbo * np.exp(1j * hsp)
                ZR1 = ZR1 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R2 * 1j
                ZR2 = ZR2 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R2 * 1j

                ZR1 = ZR1 * np.exp(1j * hsp)
                ZR2 = ZR2 * np.exp(1j * hsp)

                ZR3 = Z12.real - self.H0 - self.H1 + self.R2
                ZR4 = Z12.real - self.H0 - self.H1 + self.R2 + 1j

                ZcenterR2 = inter_line_line(ZR2, ZR1, ZR3, ZR4)

                Z8 = inter_line_circle(Zp1, Zp2, self.R2, ZcenterR2[0])
                Z7 = inter_line_circle(Zp3, Zp4 + 1j, self.R2, ZcenterR2[0])

                # we can have approximation, but we want a line tangent. So we can approximate coordinate center of cercle at 10e-6
                if len(Z8) == 0:
                    Z8 = inter_line_circle(Zp1, Zp2, self.R2, ZcenterR2[0] + 1e-6 * 1j)

                if len(Z7) == 0:
                    Z7 = inter_line_circle(Zp3, Zp4 + 1j, self.R2, ZcenterR2[0] - 1e-6)

                Z8 = Z8[0]
                Z7 = Z7[0]
                Zc3 = ZcenterR2[0]

            Zp5 = Z11
            Zp6 = Z11 + 1j

            if self.R1 == 0:
                Zc2 = inter_line_line(Zp5, Zp6, Zp1, Zp2)
                Z100 = Zc2[0]

            else:
                Zt1 = Rbo * np.exp(1j * hsp)
                Zt2 = 2 * Rbo * np.exp(1j * hsp)
                Zt1 = Zt1 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R1 * 1j
                Zt2 = Zt2 * np.exp(-1j * hsp) - (self.W3 / 2) * 1j - self.R1 * 1j

                Zt1 = Zt1 * np.exp(1j * hsp)
                Zt2 = Zt2 * np.exp(1j * hsp)

                Zt3 = Z12.real - self.H0 - self.R1
                Zt4 = Z12.real - self.H0 - self.R1 + 1j

                ZcenterR1 = inter_line_line(Zt2, Zt1, Zt3, Zt4)

                Z9 = inter_line_circle(Zp1, Zp2, self.R1, ZcenterR1[0])
                Z10 = inter_line_circle(Zp5, Zp6, self.R1, ZcenterR1[0])

                # we can have approximation, but we want a line tangent. So we can approximate coordinate center of cercle at 10e-6
                if len(Z9) == 0:
                    Z9 = inter_line_circle(Zp1, Zp2, self.R1, ZcenterR1[0] + 1e-6 * 1j)

                if len(Z10) == 0:
                    Z10 = inter_line_circle(Zp5, Zp6, self.R1, ZcenterR1[0] + 1e-6)

                Z9 = Z9[0]
                Z10 = Z10[0]
                Zc4 = ZcenterR1[0]

        point_dict = dict()
        # symetry
        point_dict["Z12"] = Z12
        point_dict["Z11"] = Z11
        point_dict["Z2"] = Z11.conjugate()
        point_dict["Z1"] = Z12.conjugate()

        if self.R1 != 0:
            point_dict["Z10"] = Z10
            point_dict["Z9"] = Z9
            point_dict["Z4"] = Z9.conjugate()
            point_dict["Z3"] = Z10.conjugate()
            point_dict["Zc4"] = Zc4
            point_dict["Zc1"] = Zc4.conjugate()

        else:
            point_dict["Z100"] = Z100
            point_dict["Z40"] = Z100.conjugate()

        if self.R2 != 0:
            point_dict["Z8"] = Z8
            point_dict["Z7"] = Z7
            point_dict["Z6"] = Z7.conjugate()
            point_dict["Z5"] = Z8.conjugate()
            point_dict["Zc3"] = Zc3
            point_dict["Zc2"] = Zc3.conjugate()

        else:
            point_dict["Z80"] = Z80
            point_dict["Z60"] = Z80.conjugate()

        return point_dict

    # cf Methods.Slot.SlotW30.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW30
            A SlotW15 object

        Returns
        -------
        curve_list: list
            A list of Segment and Arc

        """

        line_dict = self._comp_line_dict()

        if self.R1 != 0 and self.R2 != 0:
            curve_list = [
                line_dict["1-2"],
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-8"],
                line_dict["8-9"],
                line_dict["9-10"],
                line_dict["10-11"],
                line_dict["11-12"],
            ]

        elif self.R1 == 0 and self.R2 != 0:
            curve_list = [
                line_dict["1-2"],
                line_dict["2-40"],
                line_dict["40-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-8"],
                line_dict["8-100"],
                line_dict["100-11"],
                line_dict["11-12"],
            ]

        elif self.R1 != 0 and self.R2 == 0:
            curve_list = [
                line_dict["1-2"],
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-60"],
                line_dict["60-80"],
                line_dict["80-9"],
                line_dict["9-10"],
                line_dict["10-11"],
                line_dict["11-12"],
            ]

        elif self.R1 == 0 and self.R2 == 0:
            curve_list = [
                line_dict["1-2"],
                line_dict["2-40"],
                line_dict["40-60"],
                line_dict["60-80"],
                line_dict["80-100"],
                line_dict["100-11"],
                line_dict["11-12"],
            ]

        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW30.check
    def check(self):
        """Check that the SlotW30 object is correct

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        None

        Raises
        -------
        S30_W0Error
            wrong definition of W0
        S30_W3Error
            wrong definition of W3
        S30_R1Error
            wrong definition of R1
        S30_R2Error
            wrong definition of R2
        """
        Rbo = self.get_Rbo()

        if self.W0 == 0:
            raise S30_W0Error("You must have W0 > 0")

        if self.W0 * 0.5 / Rbo >= 1:
            raise S30_W0Error("You must have W0/2 < Rbo")

        if self.is_outwards():
            R1 = Rbo + self.H0 + self.R1
        else:
            R1 = Rbo - self.H0 - self.R1

        if self.W3 * 0.5 / R1 >= 1:
            raise S30_W3Error(
                "W3 is too high comparing to the lamination bore radius (Rbo)"
            )

        if self.H1 < self.R1 + self.R2:
            raise S30_R1Error("You must have R1 + R2 < H1")

        R1 = self.R1
        R2 = self.R2

        self.R1 = 0
        self.R2 = 0
        point_dict = self._comp_point_coordinate()
        self.R1 = R1
        self.R2 = R2

        Z60 = point_dict["Z60"]
        Z80 = point_dict["Z80"]
        Z40 = point_dict["Z40"]
        Z100 = point_dict["Z100"]

        lr2 = abs(Z80 - Z60)
        lr1 = abs(Z100 - Z40) - self.W0

        if R2 >= lr2 / 2:
            raise S30_R2Error("R2 is too high")

        if R1 >= lr1 / 2:
            if self.R1 != 0:
                raise S30_R1Error("R1 is too high")
            else:
                raise S30_W3Error("W3 is too high")

    # cf Methods.Slot.SlotW30.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotW30.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        point_dict = self._comp_point_coordinate()
        if self.R2 != 0:
            Z7 = point_dict["Z7"]
            Z6 = point_dict["Z6"]
        else:
            Z7 = point_dict["Z60"]
            Z6 = point_dict["Z80"]

        Rbo = self.get_Rbo()

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Harc = float(Rbo * (1 - np.cos(alpha / 2)))

        if self.is_outwards():
            return abs(Z7) - Rbo

        else:
            return abs((Z7 + Z6) / 2 - Rbo)

    # cf Methods.Slot.SlotW30.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """
        return self.H1

    # cf Methods.Slot.SlotW30.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        # comp_surface_active is an numerical computation (defined in Slot class)
        # comp_surface_opening is an analytical computation
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW30.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        Rbo = self.get_Rbo()

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        S1 = (self.H0) * self.W0

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 - Sarc
        else:
            return S1 + Sarc

    # cf Methods.Slot.SlotW30.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        # Create curve list
        line_dict = self._comp_line_dict()
        if self.R1 != 0 and self.R2 != 0:
            curve_list = [
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-8"],
                line_dict["8-9"],
                line_dict["9-10"],
                line_dict["10-11"],
                line_dict["11-2"],
            ]

        elif self.R1 == 0 and self.R2 != 0:
            curve_list = [
                line_dict["2-40"],
                line_dict["40-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-8"],
                line_dict["8-100"],
                line_dict["100-11"],
                line_dict["11-2"],
            ]

        elif self.R1 != 0 and self.R2 == 0:
            curve_list = [
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-60"],
                line_dict["60-80"],
                line_dict["80-9"],
                line_dict["9-10"],
                line_dict["10-11"],
                line_dict["11-2"],
            ]

        elif self.R1 == 0 and self.R2 == 0:
            curve_list = [
                line_dict["2-40"],
                line_dict["40-60"],
                line_dict["60-80"],
                line_dict["80-100"],
                line_dict["100-11"],
                line_dict["11-2"],
            ]

        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (12-2) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Creating surface
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H1 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.H1 / 2
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW30.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=0 no opening
        if self.H0 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-11"],
            line_dict["11-12"],
            line_dict["12-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (13-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 / 2
        label = f"{self.parent.get_label()}_{SOP_LAB}_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW30.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=1,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotW30
            A SlotW30 object
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
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges
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
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            slot = type(self)(
                Zs=12,
                W0=30e-3,
                W3=30e-3,
                H0=25e-3,
                H1=80e-3,
                R1=10e-3,
                R2=15e-3,
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.3, is_internal=False, is_stator=True, slot=slot
            )
            if is_return_default:
                return lam
            else:
                return slot.plot_schematics(
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
                raise ParentMissingError("Error: The slot is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(
                alpha=np.pi / self.Zs, is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = self._comp_point_coordinate()
            if self.is_outwards():
                sign = 1
            else:
                sign = -1
            Rbo = self.get_Rbo()
            sp = 2 * np.pi / self.Zs
            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Adding schematics
            if is_add_schematics:
                # H0
                line = Segment(
                    point_dict["Z1"] * np.exp(1j * sp),
                    point_dict["Z2"] * np.exp(1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.W0 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # H1
                line = Segment(
                    (point_dict["Z11"] + point_dict["Z2"]) / 2,
                    (point_dict["Z6"] + point_dict["Z7"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=self.W0 * 0.5 + 1j * self.W0 * 0.4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # R1
                line = Segment(point_dict["Zc1"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R1",
                    offset_label=self.W0 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R2
                line = Segment(point_dict["Zc2"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R2",
                    offset_label=self.W0 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # W3
                line = Segment(point_dict["Z8"], point_dict["Z5"] * np.exp(1j * sp))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=self.W0 * 0.4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W0
                line = Segment(
                    point_dict["Z12"] * np.exp(-1j * sp),
                    point_dict["Z1"] * np.exp(-1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=self.W0 * 0.4 - self.W0 * 0.3 * 1j,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Tooth axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * np.pi / self.Zs))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Top arc
                line = Arc1(
                    begin=Rbo * np.exp(-1j * np.pi / 2 * 0.9),
                    end=Rbo * np.exp(1j * np.pi / 2 * 0.9),
                    radius=Rbo,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R1 lines
                line = Segment(point_dict["Zc1"], point_dict["Z3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc1"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

                # R2 lines
                line = Segment(point_dict["Z5"], point_dict["Zc2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z6"], point_dict["Zc2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

                # W3 line
                line = Segment(point_dict["Z8"], point_dict["Z5"] * np.exp(1j * sp))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z9"], point_dict["Z4"] * np.exp(1j * sp))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active in [1, 3]:  # Wind and Wedge
                is_add_wedge = type_add_active == 3
                self.plot_active(
                    fig=fig, ax=ax, is_show_fig=False, is_add_wedge=is_add_wedge
                )
            elif type_add_active == 2:  # Magnet
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = (point_dict["Z7"] * np.exp(1j * sp)).imag * 1
            Rint = min(point_dict["Z5"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z5"].real, point_dict["Z1"].real)

            ax.axis("equal")
            ax.set_xlim(Rint, Rext)
            ax.set_ylim(-W, W)
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.0122,
        W3=0.0122,
        H0=0.001,
        H1=0.006,
        R1=0.001,
        R2=0.001,
        Zs=36,
        wedge_mat=None,
        is_bore=True,
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
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "R2" in list(init_dict.keys()):
                R2 = init_dict["R2"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.W3 = W3
        self.H0 = H0
        self.H1 = H1
        self.R1 = R1
        self.R2 = R2
        # Call Slot init
        super(SlotW30, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW30_str = ""
        # Get the properties inherited from Slot
        SlotW30_str += super(SlotW30, self).__str__()
        SlotW30_str += "W0 = " + str(self.W0) + linesep
        SlotW30_str += "W3 = " + str(self.W3) + linesep
        SlotW30_str += "H0 = " + str(self.H0) + linesep
        SlotW30_str += "H1 = " + str(self.H1) + linesep
        SlotW30_str += "R1 = " + str(self.R1) + linesep
        SlotW30_str += "R2 = " + str(self.R2) + linesep
        return SlotW30_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW30, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.W3 != self.W3:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.R1 != self.R1:
            return False
        if other.R2 != self.R2:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Slot
        diff_list.extend(
            super(SlotW30, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._R1 is not None
            and self._R1 is not None
            and np.isnan(other._R1)
            and np.isnan(self._R1)
        ):
            pass
        elif other._R1 != self._R1:
            if is_add_value:
                val_str = " (self=" + str(self._R1) + ", other=" + str(other._R1) + ")"
                diff_list.append(name + ".R1" + val_str)
            else:
                diff_list.append(name + ".R1")
        if (
            other._R2 is not None
            and self._R2 is not None
            and np.isnan(other._R2)
            and np.isnan(self._R2)
        ):
            pass
        elif other._R2 != self._R2:
            if is_add_value:
                val_str = " (self=" + str(self._R2) + ", other=" + str(other._R2) + ")"
                diff_list.append(name + ".R2" + val_str)
            else:
                diff_list.append(name + ".R2")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW30, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.W3)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.R1)
        S += getsizeof(self.R2)
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

        # Get the properties inherited from Slot
        SlotW30_dict = super(SlotW30, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        SlotW30_dict["W0"] = self.W0
        SlotW30_dict["W3"] = self.W3
        SlotW30_dict["H0"] = self.H0
        SlotW30_dict["H1"] = self.H1
        SlotW30_dict["R1"] = self.R1
        SlotW30_dict["R2"] = self.R2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW30_dict["__class__"] = "SlotW30"
        return SlotW30_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        W3_val = self.W3
        H0_val = self.H0
        H1_val = self.H1
        R1_val = self.R1
        R2_val = self.R2
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            W3=W3_val,
            H0=H0_val,
            H1=H1_val,
            R1=R1_val,
            R2=R2_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.W3 = None
        self.H0 = None
        self.H1 = None
        self.R1 = None
        self.R2 = None
        # Set to None the properties inherited from Slot
        super(SlotW30, self)._set_None()

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
        doc="""Slot isthmus width.

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
        doc="""Tooth width

        :Type: float
        :min: 0
        """,
    )

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
        doc="""Slot isthmus height.

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
        doc="""Slot active height.

        :Type: float
        :min: 0
        """,
    )

    def _get_R1(self):
        """getter of R1"""
        return self._R1

    def _set_R1(self, value):
        """setter of R1"""
        check_var("R1", value, "float", Vmin=0)
        self._R1 = value

    R1 = property(
        fget=_get_R1,
        fset=_set_R1,
        doc="""Top radius

        :Type: float
        :min: 0
        """,
    )

    def _get_R2(self):
        """getter of R2"""
        return self._R2

    def _set_R2(self, value):
        """setter of R2"""
        check_var("R2", value, "float", Vmin=0)
        self._R2 = value

    R2 = property(
        fget=_get_R2,
        fset=_set_R2,
        doc="""Bottom radius

        :Type: float
        :min: 0
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

    class S30_W0Error(SlotCheckError):
        """ """

        pass

    class S30_W3Error(SlotCheckError):
        """ """

        pass

    class S30_R1Error(SlotCheckError):
        """ """

        pass

    class S30_R2Error(SlotCheckError):
        """ """

        pass


MachineCheckError = SlotW30.MachineCheckError

LaminationCheckError = SlotW30.LaminationCheckError

SlotCheckError = SlotW30.SlotCheckError

S30_W0Error = SlotW30.S30_W0Error

S30_W3Error = SlotW30.S30_W3Error

S30_R1Error = SlotW30.S30_R1Error

S30_R2Error = SlotW30.S30_R2Error
