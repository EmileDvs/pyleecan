# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM50.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

from ..definitions import config_dict
from ..Functions_new.labels import HOLEM_LAB, MAGNET_PROP_LAB
from ..Functions_new.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM50(HoleMag):
    """V shape slot for buried magnet

    Attributes
    ----------
    H0 : float
        Slot depth
        Unit: m; Default: 0.003; Minimum: 0
    W0 : float
        Slot opening
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Distance from the lamination Bore
        Unit: m; Default: 0; Minimum: 0
    W1 : float
        Tooth width (at V bottom)
        Unit: m; Default: 0.013; Minimum: 0
    H2 : float
        Additional depth for the magnet
        Unit: m; Default: 0.02; Minimum: 0
    W2 : float
        Distance Magnet to bottom of the V
        Unit: m; Default: 0.01; Minimum: 0
    H3 : float
        Magnet Height
        Unit: m; Default: 0.01; Minimum: 0
    W3 : float
        Tooth width (at V top)
        Unit: m; Default: 0.01; Minimum: 0
    H4 : float
        Slot top height
        Unit: m; Default: 0; Minimum: 0
    W4 : float
        Magnet Width
        Unit: m; Default: 0.01; Minimum: 0
    magnet_0 : Magnet or None
        First Magnet
        Default: Magnet()
    magnet_1 : Magnet or None
        Second Magnet
        Default: Magnet()
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Slot depth"""
    W0: float = 0.003
    """Slot opening"""
    H1: float = 0
    """Distance from the lamination Bore"""
    W1: float = 0.013
    """Tooth width (at V bottom)"""
    H2: float = 0.02
    """Additional depth for the magnet"""
    W2: float = 0.01
    """Distance Magnet to bottom of the V"""
    H3: float = 0.01
    """Magnet Height"""
    W3: float = 0.01
    """Tooth width (at V top)"""
    H4: float = 0
    """Slot top height"""
    W4: float = 0.01
    """Magnet Width"""
    magnet_0: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """First Magnet"""
    magnet_1: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """Second Magnet"""

    # Inlined from Methods.Slot.HoleM50._comp_point_coordinate
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

    # Inlined from Methods.Slot.HoleM50.build_geometry
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
        surf_list = []
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
        curve_list = []
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
        curve_list = []
        curve_list.append(L_6_7)
        curve_list.append(L_7_8)
        if self.W2 > 0:  # if W2=0 Z8 = Z8b
            curve_list.append(L_8_8b)
        curve_list.append(L_8b_6)
        point_ref = (Z6 + Z7 + Z8 + Z8b) / 4

        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Symmetry Air surface (W3) with magnet_1
        curve_list = []
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
        curve_list = []
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
        curve_list = []
        curve_list.append(L_6s_7s)
        curve_list.append(L_7s_8s)  # rad. bridge
        if self.W2 > 0:  # if W2=0: Z8s = Z8bs
            curve_list.append(L_8s_8bs)
        curve_list.append(L_8bs_6s)
        point_ref = (Z6s + Z7s + Z8s + Z8bs) / 4

        S6 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface both magnets and W1 = 0 (S6 + S3)
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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

    # Inlined from Methods.Slot.HoleM50.check
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
            raise self.S50_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise self.S50_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise self.S50_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise self.S50_NoneError("You must set W3 !")
        elif self.W4 is None:
            raise self.S50_NoneError("You must set W4 !")
        elif self.H0 is None:
            raise self.S50_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise self.S50_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise self.S50_NoneError("You must set H2 !")
        elif self.H3 is None:
            raise self.S50_NoneError("You must set H3 !")
        elif self.H4 is None:
            raise self.S50_NoneError("You must set H4 !")

        if self.W0 <= self.W1:
            raise self.S50_W01CheckError("You must have W1 < W0")

        if self.H3 <= self.H2:
            raise self.S50_H23CheckError("You must have H2 < H3")

        if self.H0 <= self.H1:
            raise self.S50_H01CheckError("You must have H1 < H0")

        if self.comp_W5() < 0:
            raise self.S50_W5CheckError("You must have W5 >=0")

        alpha_0 = 2 * np.arcsin(self.W0 / (2 * (Rext - self.H1)))  # W0 in rad
        alpha_3 = 2 * np.arcsin(self.W3 / (2 * (Rext - self.H1)))  # W3 in rad
        if alpha_0 + alpha_3 > 2 * np.pi / self.Zh:
            raise self.S50_SpCheckError(
                "Slot pitch too small for the slot, reduce Zh, W3 or W0"
            )

        point_dict = self._comp_point_coordinate()
        if abs(point_dict["Z1"]) > abs(point_dict["Z11"]):
            raise self.S50_W3CheckError(
                "Points are colliding: unable to fulfill W3 constraints, for instance try increasing W3"
            )
        if abs(point_dict["Z2"]) > abs(point_dict["Z1"]):
            raise self.S50_W3CheckError(
                "Points are colliding: unable to fulfill W3 constraints, for instance try increasing W3"
            )

    # Inlined from Methods.Slot.HoleM50.comp_alpha
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

    # Inlined from Methods.Slot.HoleM50.comp_magnetization_dict
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

        mag_dict = {}
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

    # Inlined from Methods.Slot.HoleM50.comp_radius
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

    # Inlined from Methods.Slot.HoleM50.comp_surface_magnet_id
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

    # Inlined from Methods.Slot.HoleM50.comp_W5
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

    # Inlined from Methods.Slot.HoleM50.has_magnet
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

    # Inlined from Methods.Slot.HoleM50.plot_schematics
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
                    **kwargs,
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
                    **kwargs,
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

    # Inlined from Methods.Slot.HoleM50.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM50
            a HoleM50 object
        """

        self.magnet_0 = None
        self.magnet_1 = None

    class S50_H01CheckError(SlotCheckError):
        """ """

    class S50_H23CheckError(SlotCheckError):
        """ """

    class S50_NoneError(SlotCheckError):
        """Raised when a propery of HoleM50 is None"""

    class S50_SpCheckError(SlotCheckError):
        """ """

    class S50_W01CheckError(SlotCheckError):
        """ """

    class S50_W3CheckError(SlotCheckError):
        """ """

    class S50_W5CheckError(SlotCheckError):
        """ """
