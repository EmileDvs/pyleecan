import numpy as np
from scipy.optimize import fsolve

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.labels import WIND_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.line import Line


def build_geometry_active(self, Nrad: int, Ntan: int, is_simplified: bool = False, alpha: float = 0, delta: complex = 0):
    """Split the slot active area in several zone

    Parameters
    ----------
    self : SlotWLSRPM
        A SlotWLSRPM object
    Nrad : int
        Number of radial layer
    Ntan : int
        Number of tangentiel layer
    is_simplified : bool
        boolean to specify if coincident lines are considered as one or different lines (Default value = False)
    alpha : float
        Angle for rotation (Default value = 0) [rad]
    delta : Complex
        complex for translation (Default value = 0)

    Returns
    -------
    surf_list:
        List of surface delimiting the active zone

    """

    lam_label = self.parent.get_label()
    Rbo = self.get_Rbo()

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

    Zcl = point_dict["Zcl"]
    Zcm = point_dict["Zcm"]
    Zch = point_dict["Zch"]
    Zmid = point_dict["Zmid"]

    # Creation of curve
    surf_list = list()
    if Nrad == 1 and Ntan == 2:
        # Part 1 (0,0)
        line1 = Segment(begin=Z3, end=Z4)
        line2 = Segment(begin=Z4, end=Zch)
        line3 = Segment(begin=Zch, end=Zcl)
        line4 = Arc1(begin=Zcl, end=Z1, radius=-Rbo, is_trigo_direction=False)
        line5 = Segment(begin=Z1, end=Z2)
        line6 = Arc1(begin=Z2, end=Z3, radius=self.R1, is_trigo_direction=True)
        point_ref = (Z3 + Z4 + Zch + Zcl + Z1 + Z2) / 6

        surface = SurfLine(
            line_list=[line1, line2, line3, line4, line5, line6],
            label=(lam_label + "_" + WIND_LAB + "_R0-T0-S0"),
            point_ref=point_ref,
        )
        surf_list.append(surface)

        # Part2 (0,1)
        line1 = Segment(begin=Zch, end=Z5)
        line2 = Segment(begin=Z5, end=Z6)
        line3 = Arc1(begin=Z6, end=Z7, radius=self.R1, is_trigo_direction=True)
        line4 = Segment(begin=Z7, end=Z8)
        line5 = Arc1(begin=Z8, end=Zcl, radius=-Rbo, is_trigo_direction=False)
        line6 = Segment(begin=Zcl, end=Zch)
        point_ref = (Zch + Z5 + Z6 + Z7 + Z8 + Zcl) / 6
        surface = SurfLine(
            line_list=[line1, line2, line3, line4, line5, line6],
            label=(lam_label + "_" + WIND_LAB + "_R0-T1-S0"),
            point_ref=point_ref,
        )
        surf_list.append(surface)

    if Nrad == 2 and Ntan == 2:
        # Part 1 (0,0)
        line1 = Segment(begin=Z3, end=Z4)
        line2 = Segment(begin=Z4, end=Zch)
        line3 = Segment(begin=Zch, end=Zcm)
        line4 = Arc1(begin=Zcm, end=Z9, radius=-(Rbo + self.H3), is_trigo_direction=False)
        line5 = Segment(begin=Z9, end=Z2)
        line6 = Arc1(begin=Z2, end=Z3, radius=self.R1, is_trigo_direction=True)
        point_ref = (Z3 + Z4 + Zch + Zcm + Z9 + Z2) / 6

        surface = SurfLine(
            line_list=[line1, line2, line3, line4, line5, line6],
            label=(lam_label + "_" + WIND_LAB + "_R0-T0-S0"),
            point_ref=point_ref,
        )
        surf_list.append(surface)

        # Part2 (0,1)
        line1 = Segment(begin=Zch, end=Z5)
        line2 = Segment(begin=Z5, end=Z6)
        line3 = Arc1(begin=Z6, end=Z7, radius=self.R1, is_trigo_direction=True)
        line4 = Segment(begin=Z7, end=Z10)
        line5 = Arc1(begin=Z10, end=Zcm, radius=-(Rbo + self.H3), is_trigo_direction=False)
        line6 = Segment(begin=Zcm, end=Zch)
        point_ref = (Zch + Z5 + Z6 + Z7 + Z10 + Zcm) / 6
        surface = SurfLine(
            line_list=[line1, line2, line3, line4, line5, line6],
            label=(lam_label + "_" + WIND_LAB + "_R0-T1-S0"),
            point_ref=point_ref,
        )
        surf_list.append(surface)

        # Part3 (1,1)
        line1 = Arc1(begin=Zcm, end=Z10, radius=Rbo + self.H3, is_trigo_direction=True)
        line2 = Segment(begin=Z10, end=Z8)
        line3 = Arc1(begin=Z8, end=Zcl, radius=-Rbo, is_trigo_direction=False)
        line4 = Segment(begin=Zcl, end=Zcm)
        point_ref = (Zcm + Z10 + Z8 + Zcl) / 4
        surface = SurfLine(
            line_list=[line1, line2, line3, line4],
            label=(lam_label + "_" + WIND_LAB + "_R1-T1-S0"),
            point_ref=point_ref,
        )
        surf_list.append(surface)

        # Part4 (1,0)
        line1 = Arc1(begin=Z9, end=Zcm, radius=Rbo + self.H3, is_trigo_direction=True)
        line2 = Segment(begin=Zcm, end=Zcl)
        line3 = Arc1(begin=Zcl, end=Z1, radius=-Rbo, is_trigo_direction=False)
        line4 = Segment(begin=Z1, end=Z9)
        point_ref = (Z9 + Zcm + Zcl + Z1) / 4
        surface = SurfLine(
            line_list=[line1, line2, line3, line4],
            label=(lam_label + "_" + WIND_LAB + "_R1-T0-S0"),
            point_ref=point_ref,
        )
        surf_list.append(surface)

    else:  # Default : only one zone
        curve_list = self.build_geometry()

        # Add a line to close the winding area
        lines: list[Line] = [
            Arc1(
                begin=curve_list[-1].end,
                end=curve_list[0].begin,
                radius=-Rbo,
                is_trigo_direction=False,
            )
        ]
        lines.extend(curve_list)
        surface = SurfLine(
            line_list=lines,
            label=lam_label + "_" + WIND_LAB + "_R0-T0-S0",
            point_ref=Zmid,
        )
        surf_list.append(surface)

    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)
    return surf_list
