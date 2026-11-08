# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM53.csv
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
)
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM53(HoleMag):
    """V shape slot for buried magnet

    Attributes
    ----------
    H0 : float
        Slot depth
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Distance from the lamination Bore
        Unit: m; Default: 0; Minimum: 0
    W1 : float
        Tooth width (at V bottom)
        Unit: m; Default: 0.013; Minimum: 0
    H2 : float
        Magnet Height
        Unit: m; Default: 0.02; Minimum: 0
    W2 : float
        Distance Magnet to bottom of the V
        Unit: m; Default: 0.01; Minimum: 0
    H3 : float
        Additional depth for the magnet
        Unit: m; Default: 0.01; Minimum: 0
    W3 : float
        Magnet Width
        Unit: m; Default: 0.01; Minimum: 0
    W4 : float
        Slot angle
        Unit: rad; Default: 0.01; Minimum: 0
    magnet_0 : Magnet or None
        First Magnet
        Default: None
    magnet_1 : Magnet or None
        Second Magnet
        Default: None
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Slot depth"""
    H1: float = 0
    """Distance from the lamination Bore"""
    W1: float = 0.013
    """Tooth width (at V bottom)"""
    H2: float = 0.02
    """Magnet Height"""
    W2: float = 0.01
    """Distance Magnet to bottom of the V"""
    H3: float = 0.01
    """Additional depth for the magnet"""
    W3: float = 0.01
    """Magnet Width"""
    W4: float = 0.01
    """Slot angle"""
    magnet_0: Magnet | None = None
    """First Magnet"""
    magnet_1: Magnet | None = None
    """Second Magnet"""

    # Inlined from Methods.Slot.HoleM53._comp_point_coordinate
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
        Z6 = Z7 - 1j * (self.H2 - self.H3) * np.cos(self.W4)
        Z8 = Z7 + (self.H2 - self.H3) * np.sin(self.W4)

        # Compute the coordinate in the ref of Z6 with rotation -W4
        Z5 = self.W2 * np.exp(-1j * self.W4) + Z6
        Z4 = (self.W2 - 1j * self.H3) * np.exp(-1j * self.W4) + Z6
        Z3 = (self.W2 + self.W3 - 1j * self.H3) * np.exp(-1j * self.W4) + Z6
        Z2 = (self.W2 + self.W3) * np.exp(-1j * self.W4) + Z6
        Z9 = (self.W2 + 1j * (self.H2 - self.H3)) * np.exp(-1j * self.W4) + Z6
        Z10 = (self.W2 + self.W3 + 1j * (self.H2 - self.H3)) * np.exp(
            -1j * self.W4
        ) + Z6

        # Z1 and Z11 are defined as intersection between line and circle
        Zlist = inter_line_circle(Z8, Z10, Rext - self.H1)
        if len(Zlist) == 2 and Zlist[0].imag < 0 and Zlist[0].real > 0:
            Z11 = Zlist[0]
        elif len(Zlist) == 2 and Zlist[1].imag < 0 and Zlist[1].real > 0:
            Z11 = Zlist[1]
        else:
            raise self.Slot53InterError("ERROR: Slot 53, Can't find Z11 coordinates")

        Zlist = inter_line_circle(Z2, Z6, Rext - self.H1)
        if len(Zlist) == 2 and Zlist[0].imag < 0 and Zlist[0].real > 0:
            Z1 = Zlist[0]
        elif len(Zlist) == 2 and Zlist[1].imag < 0 and Zlist[1].real > 0:
            Z1 = Zlist[1]
        else:
            raise self.Slot53InterError("ERROR: Slot 53, Can't find Z1 coordinates")

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

    # Inlined from Methods.Slot.HoleM53.build_geometry
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
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z10))
        curve_list.append(Segment(Z10, Z11))
        curve_list.append(
            Arc1(begin=Z11, end=Z1, radius=-Rext + self.H1, is_trigo_direction=False)
        )
        point_ref = (Z1 + Z2 + Z10 + Z11) / 4
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # magnet_0 surface
        curve_list = []
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
        curve_list = []
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
        curve_list = []
        curve_list.append(Segment(Z1s, Z2s))
        curve_list.append(Segment(Z2s, Z10s))
        curve_list.append(Segment(Z10s, Z11s))
        curve_list.append(Arc1(Z11s, Z1s, Rext - self.H1, is_trigo_direction=True))
        point_ref = (Z1s + Z2s + Z10s + Z11s) / 4
        S4 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # magnet_1 surface
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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
        curve_list = []
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

    # Inlined from Methods.Slot.HoleM53.check
    def check(self):
        """Check that the HoleM53 object is correct

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object

        Returns
        -------
        None

        Raises
        -------
        S53_Rext0CheckError
            You must have H0 < Rext
        S53_Rext1CheckError
            You must have H1 < Rext
        S53_W4CheckError
            You must have W4 < pi/2
        S53_W5CheckError
            You must have W5 >=0
        """

        # Check that everything is set
        if self.W1 is None:
            raise self.S53_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise self.S53_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise self.S53_NoneError("You must set W3 !")
        elif self.W4 is None:
            raise self.S53_NoneError("You must set W4 !")
        elif self.H0 is None:
            raise self.S53_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise self.S53_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise self.S53_NoneError("You must set H2 !")
        elif self.H3 is None:
            raise self.S53_NoneError("You must set H3 !")

        Rext = self.get_Rext()

        if Rext <= self.H0:
            raise self.S53_Rext0CheckError("You must have H0 < Rext")

        if Rext <= self.H1:
            raise self.S53_Rext1CheckError("You must have H1 < Rext")

        if np.pi / 2 <= self.W4:
            raise self.S53_W4CheckError("You must have W4 < pi/2")

        if self.comp_W5() < 0:
            raise self.S53_W5CheckError("You must have W5 >=0")

        if self.H2 < self.H3:
            raise self.S53_W5CheckError("You must have H3 < H2")

    # Inlined from Methods.Slot.HoleM53.comp_alpha
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
        return np.pi / 2 - self.W4

    # Inlined from Methods.Slot.HoleM53.comp_magnetization_dict
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

        mag_dict = {}
        S0 = Segment(point_dict["Z4"], point_dict["Z3"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(point_dict["Z3s"], point_dict["Z4s"])
        mag_dict["magnet_1"] = S1.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi
            mag_dict["magnet_1"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM53.comp_radius
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
        Z6 = Z7 - 1j * (self.H2 - self.H3) * np.cos(self.W4)
        Z4 = (self.W2 - 1j * self.H3) * np.exp(-1j * self.W4) + Z6

        Rmin = min(abs(Z7), abs(Z4))
        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM53.comp_surface_magnet_id
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

    # Inlined from Methods.Slot.HoleM53.comp_W5
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
        Z8 = Z7 + (self.H2 - self.H3) * np.sin(self.W4)
        Z10 = (self.W2 + self.W3) * np.exp(-1j * self.W4) + Z8

        # Z1 and Z11 are defined as intersection between line and circle
        Zlist = inter_line_circle(Z8, Z10, Rext - self.H1)
        if len(Zlist) == 2 and Zlist[0].imag < 0 and Zlist[0].real > 0:
            Z11 = Zlist[0]
        elif len(Zlist) == 2 and Zlist[1].imag < 0 and Zlist[1].real > 0:
            Z11 = Zlist[1]
        else:
            raise self.Slot53InterError("ERROR: Slot 53, Can't find Z11 coordinates")

        return abs(Z11 - Z8) - self.W2 - self.W3

    # Inlined from Methods.Slot.HoleM53.has_magnet
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

    # Inlined from Methods.Slot.HoleM53.plot_schematics
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
                W4=np.pi / 3,
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
                # W1
                line = Segment(
                    (point_dict["Z8"] + point_dict["Z7"]) / 2 * np.exp(1j * alpha),
                    (point_dict["Z8s"] + point_dict["Z7s"]) / 2 * np.exp(1j * alpha),
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
                    point_dict["Z8s"] * np.exp(1j * alpha),
                    point_dict["Z9s"] * np.exp(1j * alpha),
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
                    point_dict["Z10s"] * np.exp(1j * alpha),
                    point_dict["Z9s"] * np.exp(1j * alpha),
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
                    begin=point_dict["Z9"] * np.exp(1j * alpha),
                    end=(point_dict["Z8"] + self.W2) * np.exp(1j * alpha),
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
                    point_dict["Z7"].real * np.exp(1j * alpha),
                    Rbo * np.exp(1j * alpha),
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
                    point_dict["Z1s"] * np.exp(1j * alpha),
                    Rbo * np.exp(1j * np.angle(point_dict["Z1s"])) * np.exp(1j * alpha),
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
                    (point_dict["Z3s"] + point_dict["Z4s"]) / 2 * np.exp(1j * alpha),
                    (point_dict["Z10s"] + point_dict["Z9s"]) / 2 * np.exp(1j * alpha),
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
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z3"] * np.exp(1j * alpha),
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
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
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
                # W2 lines
                line = Segment(
                    point_dict["Z6"] * np.exp(1j * alpha),
                    point_dict["Z8"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z6s"] * np.exp(1j * alpha),
                    point_dict["Z8s"] * np.exp(1j * alpha),
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
                    Rbo
                    * 1.3
                    * np.exp(1j * np.angle(point_dict["Z1s"]))
                    * np.exp(1j * alpha),
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
                    point_dict["Z8"] * np.exp(1j * alpha),
                    (Rbo * 1.3 + 1j * point_dict["Z8"].imag) * np.exp(1j * alpha),
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

    # Inlined from Methods.Slot.HoleM53.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM53
            a HoleM53 object
        """

        self.magnet_0 = None
        self.magnet_1 = None

    class S53_NoneError(SlotCheckError):
        """Raised when a propery of HoleM53 is None"""

    class S53_Rext0CheckError(SlotCheckError):
        """ """

    class S53_Rext1CheckError(SlotCheckError):
        """ """

    class S53_W4CheckError(SlotCheckError):
        """ """

    class S53_W5CheckError(SlotCheckError):
        """ """

    class Slot53InterError(SlotCheckError):
        """ """
