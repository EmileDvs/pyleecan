# File generated according to Generator/ClassesRef/Slot/HoleM50.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM50"""

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
)
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import HOLEM_LAB, MAGNET_PROP_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save
from scipy.optimize import fsolve


class HoleM50(HoleMag):
    """V shape slot for buried magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.HoleM50._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM50
            A HoleM50 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rext = self.get_Rext()

        # magnet pole pitch angle, must be <2*pi/2*p
        alpham = 2 * np.arcsin(self.W0 / (2 * (Rext - self.H1)))  # angle (Z9,0,Z9')

        Harc = (Rext - self.H1) * (1 - np.cos(alpham / 2))
        # alpha on schematics
        gammam = np.arctan((self.H0 - self.H1 - Harc) / (self.W0 / 2.0 - self.W1 / 2.0))
        #  betam = pi/2-alpham/2-gammam;#40.5
        hssp = np.pi / self.Zh

        x78 = (self.H3 - self.H2) / np.cos(gammam)  # distance from 7 to 8
        Z9 = Rext - Harc - self.H1 - 1j * self.W0 / 2
        Z8 = Rext - self.H0 - 1j * self.W1 / 2
        Z7 = Rext - self.H0 - x78 - 1j * self.W1 / 2
        Z1 = (Rext - self.H1) * np.exp(
            1j * (-hssp + np.arcsin(self.W3 / (2 * (Rext - self.H1))))
        )
        Z11 = (Z1 * np.exp(1j * hssp) + self.H4) * np.exp(-1j * hssp)
        Z10 = (Z9 * np.exp(1j * hssp) + self.H4) * np.exp(-1j * hssp)

        # Magnet coordinate with Z8 as center and x as the top edge of the magnet
        Z8a = -1j * (self.H3 - self.H2)
        Z8b = self.W2
        Z8c = Z8b + self.W4
        Z5 = Z8b - 1j * self.H3
        Z4 = Z8c - 1j * self.H3
        Z6 = Z5 + 1j * self.H2
        Z3 = Z4 + 1j * self.H2

        Zmag = np.array([Z8a, Z8b, Z6, Z5, Z4, Z3, Z8c])
        Zmag = Zmag * np.exp(1j * np.angle(Z9 - Z8))
        Zmag = Zmag + Z8

        # final complex numbers Zmag=[Z8b Z6 Z5 Z4 Z3 Z8c]
        (Z8a, Z8b, Z6, Z5, Z4, Z3, Z8c) = Zmag

        # Rotation so [Z1,Z2] is parallel to the x axis
        Z3r, Z1r, Z6r = (
            Z3 * np.exp(1j * hssp),
            Z1 * np.exp(1j * hssp),
            Z6 * np.exp(1j * hssp),
        )
        # numerical resolution to find the last point Z2
        x = fsolve(
            lambda x: np.imag((Z3r - (Z1r - x)) / (Z6r - Z3r)), self.H3 - self.H2
        )
        Z2 = (Z1r - x[0]) * np.exp(-1j * hssp)

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
        point_dict["Z8a"] = Z8a
        point_dict["Z8b"] = Z8b
        point_dict["Z8c"] = Z8c

        # Symmetry
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
        point_dict["Z8as"] = Z8a.conjugate()
        point_dict["Z8bs"] = Z8b.conjugate()
        point_dict["Z8cs"] = Z8c.conjugate()
        return point_dict

    # cf Methods.Slot.HoleM50.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM50
            A HoleM50 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM50

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
        Z8c = point_dict["Z8c"]
        Z8b = point_dict["Z8b"]
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
        Z8cs = point_dict["Z8cs"]
        Z8bs = point_dict["Z8bs"]
        Rext = self.get_Rext()

        # Create all the lines
        L_1_2 = Segment(Z1, Z2, prop_dict=None)
        L_1s_2s = Segment(Z1s, Z2s, prop_dict=None)
        L_1s_11s = Segment(Z1s, Z11s, prop_dict=None)
        L_2_3 = Segment(Z2, Z3, prop_dict=None)
        L_2s_1s = Segment(Z2s, Z1s, prop_dict=None)
        L_2s_3s = Segment(Z2s, Z3s, prop_dict=None)
        L_3_4 = Segment(Z3, Z4, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_0_Right"})
        L_3s_2s = Segment(Z3s, Z2s, prop_dict=None)
        L_3s_4s = Segment(Z3s, Z4s, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_1_Left"})
        L_3_8c = Segment(Z3, Z8c, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_0_Right"})
        L_3s_8cs = Segment(Z3s, Z8cs, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_1_Left"})
        L_4_5 = Segment(Z4, Z5, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_0_Bottom"})
        L_4s_3s = Segment(Z4s, Z3s, prop_dict=None)
        L_4s_5s = Segment(
            Z4s, Z5s, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_1_Bottom"}
        )
        L_5_6 = Segment(Z5, Z6, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_0_Left"})
        L_5s_4s = Segment(Z5s, Z4s, prop_dict=None)
        L_5s_6s = Segment(Z5s, Z6s, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_1_Right"})
        L_6_7 = Segment(Z6, Z7, prop_dict=None)
        L_6s_5s = Segment(Z6s, Z5s, prop_dict=None)
        L_6s_7s = Segment(Z6s, Z7s, prop_dict=None)
        L_6_8b = Segment(Z6, Z8b, prop_dict=None)
        L_6s_8bs = Segment(Z6s, Z8bs, prop_dict=None)
        L_7_6s = Segment(Z7, Z6s, prop_dict=None)
        L_7_8 = Segment(Z7, Z8, prop_dict={MAGNET_PROP_LAB: "Rotor_Radial_Bridge"})
        L_7s_6 = Segment(Z7s, Z6, prop_dict=None)
        L_7s_8s = Segment(Z7s, Z8s, prop_dict={MAGNET_PROP_LAB: "Rotor_Radial_Bridge"})

        L_8_8b = Segment(Z8, Z8b, prop_dict=None)
        L_8_9 = Segment(Z8, Z9, prop_dict=None)
        L_8s_8bs = Segment(Z8s, Z8bs, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_1_Top"})
        L_8s_8b = Segment(Z8s, Z8b, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_0_Top"})
        L_8s_9 = Segment(Z8s, Z9, prop_dict=None)
        L_8s_9s = Segment(Z8s, Z9s, prop_dict=None)

        L_8b_6 = Segment(Z8b, Z6, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_0_Left"})
        L_8bs_6s = Segment(Z8bs, Z6s, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_1_Right"})
        L_8b_8c = Segment(Z8b, Z8c, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_0_Top"})
        L_8b_8s = Segment(Z8b, Z8s, prop_dict=None)
        L_8bs_8 = Segment(Z8bs, Z8, prop_dict=None)
        L_8bs_8s = Segment(Z8bs, Z8s, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_1_Top"})
        L_8bs_8cs = Segment(
            Z8bs, Z8cs, prop_dict={MAGNET_PROP_LAB: "Rotor_Magnet_1_Top"}
        )

        L_8c_3 = Segment(Z8c, Z3, prop_dict=None)
        L_8cs_3s = Segment(Z8cs, Z3s, prop_dict=None)
        L_8c_9 = Segment(Z8c, Z9, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_0_Top"})
        L_8cs_9s = Segment(Z8cs, Z9s, prop_dict={MAGNET_PROP_LAB: "Rotor_Hole_1_Top"})

        L_9_10 = Segment(Z9, Z10, prop_dict=None)
        L_9s_8s = Segment(Z9s, Z8s, prop_dict=None)
        L_9s_10s = Segment(Z9s, Z10s, prop_dict=None)
        L_10_11 = Arc1(
            Z10,
            Z11,
            -Rext + self.H1,
            is_trigo_direction=False,
            prop_dict={MAGNET_PROP_LAB: "Rotor_Tangential_Bridge"},
        )
        L_10s_9s = Segment(Z10s, Z9s, prop_dict=None)
        L_10s_11s = Arc1(
            Z10s,
            Z11s,
            Rext - self.H1,
            is_trigo_direction=True,
            prop_dict={MAGNET_PROP_LAB: "Rotor_Tangential_Bridge"},
        )
        L_11_1 = Segment(Z11, Z1, prop_dict=None)
        L_11s_1s = Segment(Z11s, Z1s, prop_dict=None)
        L_11s_10s = Arc1(Z11s, Z10s, -Rext + self.H1, is_trigo_direction=False)

        # Create all the surfaces for all the cases
        surf_list = list()
        # Air surface (W3) with magnet_0
        curve_list = [L_1_2, L_2_3, L_3_8c, L_8c_9]
        if self.H4 > 0:
            curve_list.append(L_9_10)
        curve_list.append(L_10_11)
        if self.H4 > 0:
            curve_list.append(L_11_1)
        point_ref = (Z1 + Z2 + Z3 + Z8c + Z9 + Z10 + Z11) / 7
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Magnet_0 surface
        curve_list = list()
        if is_simplified:
            curve_list.append(L_8c_3)
            curve_list.append(L_6_8b)
        else:
            if Z3 != Z4:  # Z3 == Z4 if H2 = 0
                curve_list.append(L_3_4)
            curve_list.append(L_4_5)
            if Z5 != Z6:  # Z5 == Z6 if H2 = 0
                curve_list.append(L_5_6)
            curve_list.append(L_6_8b)
            curve_list.append(L_8b_8c)
            curve_list.append(L_8c_3)
        point_ref = (Z3 + Z4 + Z5 + Z6 + Z8b + Z8c) / 6

        S2 = SurfLine(
            line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref
        )

        # Air surface with magnet_0 and W1 > 0
        curve_list = list()
        curve_list.append(L_6_7)
        curve_list.append(L_7_8)
        if self.W2 > 0:  # if W2=0 Z8 = Z8b
            curve_list.append(L_8_8b)
        curve_list.append(L_8b_6)
        point_ref = (Z6 + Z7 + Z8 + Z8b) / 4

        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Symmetry Air surface (W3) with magnet_1
        curve_list = list()
        curve_list.append(L_1s_2s)
        curve_list.append(L_2s_3s)
        curve_list.append(L_3s_8cs)
        curve_list.append(L_8cs_9s)
        if self.H4 > 0:
            curve_list.append(L_9s_10s)
        curve_list.append(L_10s_11s)
        if self.H4 > 0:
            curve_list.append(L_11s_1s)
        point_ref = (Z1s + Z2s + Z3s + Z8cs + Z9s + Z10s + Z11s) / 7

        S4 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # magnet_1 surface
        curve_list = list()
        if is_simplified:
            curve_list.append(L_8cs_3s.copy())
            curve_list.append(L_6s_8bs.copy())
        else:
            if Z3s != Z4s:  # Z3 == Z3 if H2 = 0
                curve_list.append(L_3s_4s.copy())
            curve_list.append(L_4s_5s.copy())
            if Z5s != Z6s:  # Z5 == Z6 if H2 = 0
                curve_list.append(L_5s_6s.copy())
            curve_list.append(L_6s_8bs.copy())
            curve_list.append(L_8bs_8cs.copy())
            curve_list.append(L_8cs_3s.copy())
        point_ref = (Z3s + Z4s + Z5s + Z6s + Z8bs + Z8cs) / 6
        S5 = SurfLine(
            line_list=curve_list, label=mag_label + "T1-S0", point_ref=point_ref
        )

        # Air surface with magnet_1 and W1 > 0
        curve_list = list()
        curve_list.append(L_6s_7s)
        curve_list.append(L_7s_8s)  # rad. bridge
        if self.W2 > 0:  # if W2=0: Z8s = Z8bs
            curve_list.append(L_8s_8bs)
        curve_list.append(L_8bs_6s)
        point_ref = (Z6s + Z7s + Z8s + Z8bs) / 4

        S6 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface both magnets and W1 = 0 (S6 + S3)
        curve_list = list()
        curve_list.append(L_6_7.copy())
        curve_list.append(L_7_6s.copy())
        curve_list.append(L_6s_8bs.copy())
        if self.W2 > 0:  # If W2 = 0: Z8b = Z8 = Z8bs
            curve_list.append(L_8bs_8s.copy())
            curve_list.append(L_8s_8b.copy())
        curve_list.append(L_8b_6.copy())  # == Magnet_0_Left
        point_ref = (Z6 + Z7 + Z6s + Z8s + Z8bs + Z8b) / 6
        S7 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface without magnet_0 and W1 > 0 (S1 + S2 + S3)
        curve_list = list()
        curve_list.append(L_1_2)
        curve_list.append(L_2_3)
        if self.H2 > 0:
            curve_list.append(L_3_4)
        curve_list.append(L_4_5)
        if self.H2 > 0:
            curve_list.append(L_5_6)
        curve_list.append(L_6_7)
        curve_list.append(L_7_8)
        curve_list.append(L_8_9)
        if self.H4 > 0:
            curve_list.append(L_9_10)
        curve_list.append(L_10_11)
        if self.H4 > 0:
            curve_list.append(L_11_1)
        point_ref = (Z1 + Z2 + Z3 + Z8c + Z9 + Z10 + Z11) / 7
        S8 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface without magnet_1 and W1 > 0
        curve_list = list()
        curve_list.append(L_1s_2s)
        curve_list.append(L_2s_3s)
        if self.H2 > 0:
            curve_list.append(L_3s_4s)
        curve_list.append(L_4s_5s)
        if self.H2 > 0:
            curve_list.append(L_5s_6s)
        curve_list.append(L_6s_7s)
        curve_list.append(L_7s_8s)
        curve_list.append(L_8s_9s)
        if self.H4 > 0:
            curve_list.append(L_9s_10s)
        curve_list.append(
            Arc1(Z10s, Z11s, Rext - self.H1, is_trigo_direction=True, prop_dict=None)
        )
        if self.H4 > 0:
            curve_list.append(L_11s_1s)
        point_ref = (Z1s + Z2s + Z3s + Z8cs + Z9s + Z10s + Z11s) / 7
        S9 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface with magnet_0 without magnet_1 and W1 = 0
        # (S4 + S5 + S7)
        curve_list = list()
        curve_list.append(L_1s_2s.copy())
        curve_list.append(L_2s_3s.copy())
        if self.H2 > 0:
            curve_list.append(L_3s_4s.copy())
        curve_list.append(L_4s_5s.copy())
        if self.H2 > 0:
            curve_list.append(L_5s_6s.copy())
        curve_list.append(L_6s_7s.copy())
        curve_list.append(L_7s_6.copy())
        curve_list.append(L_6_8b.copy())
        if Z8b != Z8s:
            curve_list.append(L_8b_8s.copy())
        curve_list.append(L_8s_9s.copy())
        if self.H4 > 0:
            curve_list.append(L_9s_10s.copy())
        curve_list.append(L_10s_11s.copy())
        if self.H4 > 0:
            curve_list.append(L_11s_1s.copy())
        point_ref = (Z1s + Z2s + Z3s + Z8cs + Z9s + Z10s + Z11s) / 7
        S10 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface with magnet_1 without magnet_0 and W1 = 0
        # (S1 + S2 + S7)
        curve_list = list()
        curve_list.append(L_1_2)
        curve_list.append(L_2_3)
        if self.H2 > 0:
            curve_list.append(L_3_4)
        curve_list.append(L_4_5)
        if self.H2 > 0:
            curve_list.append(L_5_6)
        curve_list.append(L_6_7)
        curve_list.append(L_7_6s)
        curve_list.append(L_6s_8bs)
        if Z8bs != Z8:
            curve_list.append(L_8bs_8)
        curve_list.append(L_8_9)
        if self.H4 > 0:
            curve_list.append(L_9_10)
        curve_list.append(L_10_11)
        if self.H4 > 0:
            curve_list.append(L_11_1)
        point_ref = (Z1 + Z2 + Z3 + Z8c + Z9 + Z10 + Z11) / 7
        S11 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface without magnets and W1 = 0
        # (S4 + S5 + S7 + S2 + S1)
        curve_list = list()
        curve_list.append(L_1_2)
        curve_list.append(L_2_3)
        if Z3 != Z4:  # if H2 = 0
            curve_list.append(L_3_4)
        curve_list.append(L_4_5)
        if Z5 != Z6:  # if H2 = 0
            curve_list.append(L_5_6)
        curve_list.append(L_6_7)
        curve_list.append(L_7_6s)
        if Z5s != Z6s:
            curve_list.append(L_6s_5s)
        curve_list.append(L_5s_4s)
        if Z3s != Z4s:
            curve_list.append(L_4s_3s)
        curve_list.append(L_3s_2s)
        curve_list.append(L_2s_1s)
        if self.H4 > 0:
            curve_list.append(L_1s_11s)
        curve_list.append(L_11s_10s)
        if self.H4 > 0:
            curve_list.append(L_10s_9s)
        curve_list.append(L_9s_8s)
        curve_list.append(L_8s_9)
        if self.H4 > 0:
            curve_list.append(L_9_10)
        curve_list.append(L_10_11)
        if self.H4 > 0:
            curve_list.append(L_11_1)

        point_ref = (Z6 + Z8b + Z7 + Z8 + Z6s + Z8bs) / 6
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
            S4.label = vent_label + "T1-S0"  # Hole
            surf_list = [S11, S5, S4]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 > 0:
            S8.label = vent_label + "T0-S0"  # Hole
            S9.label = vent_label + "T1-S0"  # Hole
            surf_list = [S8, S9]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 == 0:
            S12.label = vent_label + "T0-S0"  # Hole
            surf_list = [S12]

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.HoleM50.check
    def check(self):
        """Check that the HoleM50 object is correct

        Parameters
        ----------
        self : HoleM50
            A HoleM50 object

        Returns
        -------
        None

        Raises
        _______
        S50_W01CheckError
            You must have W1 < W0
        S50_H23CheckError
            You must have H2 < H3
        S50_H01CheckError
            You must have H1 < H0
        S50_W5CheckError
            You must have W5 >=0
        S50_SpCheckError
            Slot pitch too small for the slot, reduce Zh, W3 or W0
        """
        Rext = self.get_Rext()

        # Check that everything is set
        if self.W0 is None:
            raise S50_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise S50_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise S50_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise S50_NoneError("You must set W3 !")
        elif self.W4 is None:
            raise S50_NoneError("You must set W4 !")
        elif self.H0 is None:
            raise S50_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S50_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise S50_NoneError("You must set H2 !")
        elif self.H3 is None:
            raise S50_NoneError("You must set H3 !")
        elif self.H4 is None:
            raise S50_NoneError("You must set H4 !")

        if self.W0 <= self.W1:
            raise S50_W01CheckError("You must have W1 < W0")

        if self.H3 <= self.H2:
            raise S50_H23CheckError("You must have H2 < H3")

        if self.H0 <= self.H1:
            raise S50_H01CheckError("You must have H1 < H0")

        if self.comp_W5() < 0:
            raise S50_W5CheckError("You must have W5 >=0")

        alpha_0 = 2 * np.arcsin(self.W0 / (2 * (Rext - self.H1)))  # W0 in rad
        alpha_3 = 2 * np.arcsin(self.W3 / (2 * (Rext - self.H1)))  # W3 in rad
        if alpha_0 + alpha_3 > 2 * np.pi / self.Zh:
            raise S50_SpCheckError(
                "Slot pitch too small for the slot, reduce Zh, W3 or W0"
            )

        point_dict = self._comp_point_coordinate()
        if abs(point_dict["Z1"]) > abs(point_dict["Z11"]):
            raise S50_W3CheckError(
                "Points are colliding: unable to fulfill W3 constraints, for instance try increasing W3"
            )
        if abs(point_dict["Z2"]) > abs(point_dict["Z1"]):
            raise S50_W3CheckError(
                "Points are colliding: unable to fulfill W3 constraints, for instance try increasing W3"
            )

    # cf Methods.Slot.HoleM50.comp_alpha
    def comp_alpha(self):
        """Compute the alpha angle of the slot (cf schematics)

        Parameters
        ----------
        self : HoleM50
            a HoleM50 object

        Returns
        -------
        alpha: float
            Cf schematics [rad]
        """
        Rext = self.get_Rext()

        alpham = 2 * np.arcsin(self.W0 / (2 * (Rext - self.H1)))

        Harc = (Rext - self.H1) * (1 - np.cos(alpham / 2))
        return np.arctan((self.H0 - self.H1 - Harc) / (self.W0 / 2 - self.W1 / 2))

    # cf Methods.Slot.HoleM50.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM50
            a HoleM50 object
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
        S0 = Segment(point_dict["Z5"], point_dict["Z4"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(point_dict["Z4s"], point_dict["Z5s"])
        mag_dict["magnet_1"] = S1.comp_normal()

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        if not is_north:
            mag_dict["magnet_0"] += np.pi
            mag_dict["magnet_1"] += np.pi

        return mag_dict

    # cf Methods.Slot.HoleM50.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the slot

        Parameters
        ----------
        self : HoleM50
            A HoleM50 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the slot [m]
        """

        Rmax = self.get_Rext() - self.H1

        point_dict = self._comp_point_coordinate()
        Rmin = min(abs(point_dict["Z5"]), abs(point_dict["Z7"]))

        return (Rmin, Rmax)

    # cf Methods.Slot.HoleM50.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM50
            A HoleM50 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        # all magnet has the same surface
        label = "magnet_" + str(index)
        if index in [0, 1, 2] and getattr(self, label) is not None:
            return self.H3 * self.W4
        return 0

    # cf Methods.Slot.HoleM50.comp_W5
    def comp_W5(self):
        """Compute the W5 width of the slot (cf schematics)

        Parameters
        ----------
        self : HoleM50
            a HoleM50 object

        Returns
        -------
        W5: float
            Cf schematics [m]

        """

        alpha = self.comp_alpha()

        # Distance fromZ8 to Z9
        L89 = (self.W0 / 2 - self.W1 / 2) / np.cos(alpha)

        return L89 - self.W4 - self.W2

    # cf Methods.Slot.HoleM50.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM50
            A HoleM50 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None or self.magnet_1 is not None

    # cf Methods.Slot.HoleM50.plot_schematics
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
        self : HoleM50
            A HoleM50 object
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
        lam : LamHole
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                H0=0.01496,
                H1=0.0065,
                H2=0.003,
                H3=0.0085,
                H4=0.004,
                W0=0.042,
                W1=0.005,
                W2=0.004,
                W3=0.007,
                W4=0.0129,
                Zh=8,
            )
            lam = LamHole(
                Rint=0.05532,
                Rext=0.0812,
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
            alpha = np.pi / 2  # To rotate the schematics
            rot = np.exp(1j * alpha)
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
                    Z = Z * rot
                    ax.text(Z.real, Z.imag, name, fontsize=P_FONT_SIZE, bbox=TEXT_BOX)

            # Adding schematics
            if is_add_schematics:
                kwargs = dict(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W0
                line = Segment(point_dict["Z9"] * rot, point_dict["Z9s"] * rot)
                line.plot(
                    label="W0",
                    offset_label=self.W0 * 0.3 + 1j * self.H3 * 0.2,
                    **kwargs
                )
                # W1
                line = Segment(
                    (point_dict["Z8"] + point_dict["Z7"]) / 2 * rot,
                    (point_dict["Z8s"] + point_dict["Z7s"]) / 2 * rot,
                )
                line.plot(label="W1", offset_label=-1j * self.H3 * 0.4, **kwargs)
                # W2
                line = Segment(point_dict["Z8"] * rot, point_dict["Z8b"] * rot)
                line.plot(label="W2", offset_label=1j * self.H3 * 0.2, **kwargs)
                # W3
                line = Segment(
                    (point_dict["Z1s"] + point_dict["Z11s"]) * 0.5 * rot,
                    (point_dict["Z1"] + point_dict["Z11"])
                    * 0.5
                    * rot
                    * np.exp(1j * sp),
                )
                line.plot(label="W3", offset_label=-1j * self.H3 * 0.3, **kwargs)
                # W4
                line = Segment(point_dict["Z5"] * rot, point_dict["Z4"] * rot)
                line.plot(label="W4", offset_label=-1j * self.H3 * 0.3, **kwargs)
                # H0
                line = Segment(Rbo * rot, point_dict["Z8"].real * rot)
                line.plot(
                    label="H0",
                    offset_label=self.W0 * 0.05 + 1j * self.H3 * 0.2,
                    **kwargs
                )
                # H1
                line = Segment(
                    Rbo * np.exp(-1j * sp / 2) * rot,
                    (Rbo - self.H1) * np.exp(-1j * sp / 2) * rot,
                )
                line.plot(label="H1", offset_label=self.H3 * 0.2, **kwargs)
                # H2
                line = Segment(
                    (point_dict["Z3s"] + point_dict["Z6s"]) * 0.5 * rot,
                    (point_dict["Z4s"] + point_dict["Z5s"]) * 0.5 * rot,
                )
                line.plot(label="H2", offset_label=self.H3 * 0.2, **kwargs)
                # H3
                line = Segment(point_dict["Z4s"] * rot, point_dict["Z8cs"] * rot)
                line.plot(label="H3", offset_label=self.H3 * 0.2, **kwargs)
                # H4
                line = Segment(point_dict["Z9s"] * rot, point_dict["Z10s"] * rot)
                line.plot(label="H4", offset_label=self.H3 * 0.2, **kwargs)

            if is_add_main_line:
                lines = []
                # Ox axis
                lines.append(Segment(0, lam.Rext * 1.5 * rot))

                # Tooth axis
                lines.append(Segment(0, lam.Rext * 1.5 * np.exp(1j * sp / 2) * rot))

                lines.append(Segment(0, lam.Rext * 1.5 * np.exp(-1j * sp / 2) * rot))
                # H1 radius
                R = Rbo - self.H1
                rot_N = np.exp(-1j * np.pi / 2 * 0.9) * rot
                rot_P = np.exp(1j * np.pi / 2 * 0.9) * rot
                lines.append(
                    Arc1(
                        begin=R * rot_N,
                        end=R * rot_P,
                        radius=R,
                        is_trigo_direction=True,
                    )
                )
                # H4 radius
                R = Rbo - self.H1 + self.H4
                lines.append(
                    Arc1(
                        begin=R * rot_N,
                        end=R * rot_P,
                        radius=R,
                        is_trigo_direction=True,
                    )
                )
                # W1 lines
                lines.append(Segment(point_dict["Z7"] * rot, point_dict["Z7s"] * rot))
                lines.append(Segment(point_dict["Z8"] * rot, point_dict["Z8s"] * rot))
                # W2 lines
                lines.append(Segment(point_dict["Z8"] * rot, point_dict["Z8a"] * rot))
                lines.append(Segment(point_dict["Z8s"] * rot, point_dict["Z8as"] * rot))
                # H2 lines
                lines.append(Segment(point_dict["Z3s"] * rot, point_dict["Z6s"] * rot))

                for line in lines:
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

            # Zooming and cleaning
            W = abs(point_dict["Z11s"].imag) * 1.3
            Rint = self.parent.Rint
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

    # cf Methods.Slot.HoleM50.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM50
            a HoleM50 object
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
        W0=0.003,
        H1=0,
        W1=0.013,
        H2=0.02,
        W2=0.01,
        H3=0.01,
        W3=0.01,
        H4=0,
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
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
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
            if "H4" in list(init_dict.keys()):
                H4 = init_dict["H4"]
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
        self.W0 = W0
        self.H1 = H1
        self.W1 = W1
        self.H2 = H2
        self.W2 = W2
        self.H3 = H3
        self.W3 = W3
        self.H4 = H4
        self.W4 = W4
        self.magnet_0 = magnet_0
        self.magnet_1 = magnet_1
        # Call HoleMag init
        super(HoleM50, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM50_str = ""
        # Get the properties inherited from HoleMag
        HoleM50_str += super(HoleM50, self).__str__()
        HoleM50_str += "H0 = " + str(self.H0) + linesep
        HoleM50_str += "W0 = " + str(self.W0) + linesep
        HoleM50_str += "H1 = " + str(self.H1) + linesep
        HoleM50_str += "W1 = " + str(self.W1) + linesep
        HoleM50_str += "H2 = " + str(self.H2) + linesep
        HoleM50_str += "W2 = " + str(self.W2) + linesep
        HoleM50_str += "H3 = " + str(self.H3) + linesep
        HoleM50_str += "W3 = " + str(self.W3) + linesep
        HoleM50_str += "H4 = " + str(self.H4) + linesep
        HoleM50_str += "W4 = " + str(self.W4) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM50_str += "magnet_0 = " + tmp
        else:
            HoleM50_str += "magnet_0 = None" + linesep + linesep
        if self.magnet_1 is not None:
            tmp = self.magnet_1.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM50_str += "magnet_1 = " + tmp
        else:
            HoleM50_str += "magnet_1 = None" + linesep + linesep
        return HoleM50_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM50, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.W0 != self.W0:
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
        if other.H4 != self.H4:
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
            super(HoleM50, self).compare(
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
            other._H3 is not None
            and self._H3 is not None
            and np.isnan(other._H3)
            and np.isnan(self._H3)
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
            other._H4 is not None
            and self._H4 is not None
            and np.isnan(other._H4)
            and np.isnan(self._H4)
        ):
            pass
        elif other._H4 != self._H4:
            if is_add_value:
                val_str = " (self=" + str(self._H4) + ", other=" + str(other._H4) + ")"
                diff_list.append(name + ".H4" + val_str)
            else:
                diff_list.append(name + ".H4")
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
        S += super(HoleM50, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.W0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
        S += getsizeof(self.H3)
        S += getsizeof(self.W3)
        S += getsizeof(self.H4)
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
        HoleM50_dict = super(HoleM50, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM50_dict["H0"] = self.H0
        HoleM50_dict["W0"] = self.W0
        HoleM50_dict["H1"] = self.H1
        HoleM50_dict["W1"] = self.W1
        HoleM50_dict["H2"] = self.H2
        HoleM50_dict["W2"] = self.W2
        HoleM50_dict["H3"] = self.H3
        HoleM50_dict["W3"] = self.W3
        HoleM50_dict["H4"] = self.H4
        HoleM50_dict["W4"] = self.W4
        if self.magnet_0 is None:
            HoleM50_dict["magnet_0"] = None
        else:
            HoleM50_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_1 is None:
            HoleM50_dict["magnet_1"] = None
        else:
            HoleM50_dict["magnet_1"] = self.magnet_1.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM50_dict["__class__"] = "HoleM50"
        return HoleM50_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        W0_val = self.W0
        H1_val = self.H1
        W1_val = self.W1
        H2_val = self.H2
        W2_val = self.W2
        H3_val = self.H3
        W3_val = self.W3
        H4_val = self.H4
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
            W0=W0_val,
            H1=H1_val,
            W1=W1_val,
            H2=H2_val,
            W2=W2_val,
            H3=H3_val,
            W3=W3_val,
            H4=H4_val,
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
        self.W0 = None
        self.H1 = None
        self.W1 = None
        self.H2 = None
        self.W2 = None
        self.H3 = None
        self.W3 = None
        self.H4 = None
        self.W4 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        if self.magnet_1 is not None:
            self.magnet_1._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM50, self)._set_None()

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
        doc="""Slot opening

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
        doc="""Additional depth for the magnet

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
        doc="""Magnet Height

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
        doc="""Tooth width (at V top)

        :Type: float
        :min: 0
        """,
    )

    def _get_H4(self):
        """getter of H4"""
        return self._H4

    def _set_H4(self, value):
        """setter of H4"""
        check_var("H4", value, "float", Vmin=0)
        self._H4 = value

    H4 = property(
        fget=_get_H4,
        fset=_set_H4,
        doc="""Slot top height

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
        doc="""Magnet Width

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

    class MachineCheckError(Exception):
        """ """

        pass

    class LaminationCheckError(MachineCheckError):
        """ """

        pass

    class SlotCheckError(LaminationCheckError):
        """ """

        pass

    class S50_SpCheckError(SlotCheckError):
        """ """

        pass

    class S50_H01CheckError(SlotCheckError):
        """ """

        pass

    class S50_H23CheckError(SlotCheckError):
        """ """

        pass

    class S50_W5CheckError(SlotCheckError):
        """ """

        pass

    class S50_W01CheckError(SlotCheckError):
        """ """

        pass

    class S50_NoneError(SlotCheckError):
        """Raised when a propery of HoleM50 is None"""

        pass

    class S50_W3CheckError(SlotCheckError):
        """ """

        pass


MachineCheckError = HoleM50.MachineCheckError

LaminationCheckError = HoleM50.LaminationCheckError

SlotCheckError = HoleM50.SlotCheckError

S50_SpCheckError = HoleM50.S50_SpCheckError

S50_H01CheckError = HoleM50.S50_H01CheckError

S50_H23CheckError = HoleM50.S50_H23CheckError

S50_W5CheckError = HoleM50.S50_W5CheckError

S50_W01CheckError = HoleM50.S50_W01CheckError

S50_NoneError = HoleM50.S50_NoneError

S50_W3CheckError = HoleM50.S50_W3CheckError
