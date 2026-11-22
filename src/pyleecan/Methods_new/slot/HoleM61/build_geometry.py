from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import HOLEV_LAB, HOLEM_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.lamination import Lamination


def build_geometry(self, alpha: float = 0, delta: complex = 0, is_simplified: bool = False, lam: Lamination | None = None) -> list:
    """Compute the curve (Segment) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : HoleM61
        A HoleM61 object
    alpha : float
        Angle to rotate the slot (Default value = 0) [rad]
    delta : complex
        Complex to translate the slot (Default value = 0)
    is_simplified : bool
        True to avoid line superposition
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    surf_list: list
        List of SurfLine needed to draw the HoleM58

    """
    lam = container_or_parent(self, lam, "lam")
    Rbo = self.get_Rbo(lam=lam)

    # Get correct label for surfaces
    lam_label = lam.get_label()
    R_id, surf_type = self.get_R_id(lam=lam)
    vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
    mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

    # Get all the points
    point_dict = self._comp_point_coordinate(lam=lam)
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
    Z12 = point_dict["Z12"]

    # add possibility to create hole without magnet
    if self.W1 != None and self.W2 != None:
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]
        ZM5 = point_dict["ZM5"]
        ZM6 = point_dict["ZM6"]
        ZM7 = point_dict["ZM7"]
        ZM8 = point_dict["ZM8"]
        ZM9 = point_dict["ZM9"]
        ZM10 = point_dict["ZM10"]
        ZM11 = point_dict["ZM11"]
        ZM12 = point_dict["ZM12"]
        ZM13 = point_dict["ZM13"]
        ZM14 = point_dict["ZM14"]
        ZM15 = point_dict["ZM15"]
        ZM16 = point_dict["ZM16"]

    surf_list = list()
    # Create all the surfaces for all the cases

    # surface Hole without magnet
    curve_list: list[Line] = list()
    curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z3))
    curve_list.append(Segment(begin=Z3, end=Z4))
    curve_list.append(
        Arc1(
            begin=Z4,
            end=Z5,
            radius=Rbo - self.H2,
            is_trigo_direction=True,
        )
    )
    curve_list.append(Segment(begin=Z5, end=Z6))
    curve_list.append(Segment(begin=Z6, end=Z1))
    point_ref = (Z3 + Z6) / 2
    S2 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # surface Hole without magnet
    curve_list = list()
    curve_list.append(Segment(begin=Z7, end=Z8))
    curve_list.append(Segment(begin=Z8, end=Z9))
    curve_list.append(Segment(begin=Z9, end=Z10))
    curve_list.append(
        Arc1(
            begin=Z10,
            end=Z11,
            radius=Rbo - self.H2,
            is_trigo_direction=True,
        )
    )
    curve_list.append(Segment(begin=Z11, end=Z12))
    curve_list.append(Segment(begin=Z12, end=Z7))

    point_ref = (Z9 + Z12) / 2
    S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # add possibility to create hole without magnet
    if self.W1 != None and self.W2 != None:
        # Magnet_2 surface
        curve_list = list()
        curve_list.append(Segment(begin=ZM1, end=ZM2))
        curve_list.append(Segment(begin=ZM2, end=ZM3))
        curve_list.append(Segment(begin=ZM3, end=ZM4))
        curve_list.append(Segment(begin=ZM4, end=ZM1))
        point_ref = (ZM1 + ZM3) / 2
        SM2 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface between magnet_2 and magnet_3
        curve_list = list()
        curve_list.append(Segment(begin=ZM4, end=ZM3))
        curve_list.append(Segment(begin=ZM3, end=Z3))
        curve_list.append(Segment(begin=Z3, end=ZM5))
        curve_list.append(Segment(begin=ZM5, end=ZM8))
        curve_list.append(Segment(begin=ZM8, end=Z6))
        curve_list.append(Segment(begin=Z6, end=ZM4))
        point_ref = (Z3 + ZM4) / 2
        S23 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_3
        curve_list = list()
        curve_list.append(Segment(begin=ZM5, end=ZM6))
        curve_list.append(Segment(begin=ZM6, end=ZM7))
        curve_list.append(Segment(begin=ZM7, end=ZM8))
        curve_list.append(Segment(begin=ZM8, end=ZM5))

        point_ref = (ZM5 + ZM7) / 2
        SM3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface between magnet_3 and top of slot
        curve_list = list()
        curve_list.append(Segment(begin=ZM6, end=Z4))
        curve_list.append(
            Arc1(begin=Z4, end=Z5, radius=Rbo - self.H2, is_trigo_direction=True)
        )
        curve_list.append(Segment(begin=Z5, end=ZM7))
        curve_list.append(Segment(begin=ZM7, end=ZM6))

        point_ref = (Z5 + ZM6) / 2
        S3T = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface without magnet_2 but with magnet_3
        curve_list = list()
        curve_list.append(Segment(begin=Z1, end=Z2))
        curve_list.append(Segment(begin=Z2, end=Z3))
        curve_list.append(Segment(begin=Z3, end=ZM5))
        curve_list.append(Segment(begin=ZM5, end=ZM8))
        curve_list.append(Segment(begin=ZM8, end=Z6))
        curve_list.append(Segment(begin=Z6, end=Z1))
        point_ref = (Z1 + Z3) / 2
        SW02 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface without magnet_3 but with magnet_2
        curve_list = list()
        curve_list.append(Segment(begin=ZM3, end=Z3))
        curve_list.append(Segment(begin=Z3, end=Z4))
        curve_list.append(
            Arc1(begin=Z4, end=Z5, radius=Rbo - self.H2, is_trigo_direction=True)
        )
        curve_list.append(Segment(begin=Z5, end=Z6))
        curve_list.append(Segment(begin=Z6, end=ZM4))
        curve_list.append(Segment(begin=ZM4, end=ZM3))

        point_ref = (Z5 + Z3) / 2
        SW03 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Magnet_1 surface
        curve_list = list()
        curve_list.append(Segment(begin=ZM9, end=ZM10))
        curve_list.append(Segment(begin=ZM10, end=ZM11))
        curve_list.append(Segment(begin=ZM11, end=ZM12))
        curve_list.append(Segment(begin=ZM12, end=ZM9))
        point_ref = (ZM10 + ZM12) / 2
        SM1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface between magnet_1 and magnet_0
        curve_list = list()
        curve_list.append(Segment(begin=ZM11, end=ZM12))
        curve_list.append(Segment(begin=ZM12, end=Z12))
        curve_list.append(Segment(begin=Z12, end=ZM16))
        curve_list.append(Segment(begin=ZM16, end=ZM13))
        curve_list.append(Segment(begin=ZM13, end=Z9))
        curve_list.append(Segment(begin=Z9, end=ZM11))
        point_ref = (Z9 + ZM12) / 2
        S10 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Surface for magnet_0
        curve_list = list()
        curve_list.append(Segment(begin=ZM13, end=ZM14))
        curve_list.append(Segment(begin=ZM14, end=ZM15))
        curve_list.append(Segment(begin=ZM15, end=ZM16))
        curve_list.append(Segment(begin=ZM16, end=ZM13))

        point_ref = (ZM13 + ZM15) / 2
        SM0 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface between magnet_0 and top of slot
        curve_list = list()
        curve_list.append(Segment(begin=ZM15, end=Z11))
        curve_list.append(
            Arc1(begin=Z11, end=Z10, radius=Rbo - self.H2, is_trigo_direction=True)
        )
        curve_list.append(Segment(begin=Z10, end=ZM14))
        curve_list.append(Segment(begin=ZM14, end=ZM15))

        point_ref = (Z10 + ZM15) / 2
        S0T = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface without magnet_1 but with magnet_0
        curve_list = list()
        curve_list.append(Segment(begin=Z7, end=Z8))
        curve_list.append(Segment(begin=Z8, end=Z9))
        curve_list.append(Segment(begin=Z9, end=ZM13))
        curve_list.append(Segment(begin=ZM13, end=ZM16))
        curve_list.append(Segment(begin=ZM16, end=Z12))
        curve_list.append(Segment(begin=Z12, end=Z7))
        point_ref = (Z12 + Z8) / 2
        SW01 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface without magnet_0 but with magnet_1
        curve_list = list()
        curve_list.append(Segment(begin=ZM11, end=Z9))
        curve_list.append(Segment(begin=Z9, end=Z10))
        curve_list.append(
            Arc1(begin=Z10, end=Z11, radius=Rbo - self.H2, is_trigo_direction=True)
        )
        curve_list.append(Segment(begin=Z11, end=Z12))
        curve_list.append(Segment(begin=Z12, end=ZM12))
        curve_list.append(Segment(begin=ZM12, end=ZM11))

        point_ref = (Z10 + Z12) / 2
        SW00 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Create the surface list by selecting the correct ones

    # add possibility to create hole without magnet
    surf_list = list()
    if self.W1 != None and self.W2 != None:
        if self.magnet_0:
            SM0.label = mag_label + "T0-S0"
            S0T.label = vent_label + "T0-S0"
            surf_list += [SM0, S0T]
            if self.magnet_1:
                SM1.label = mag_label + "T1-S0"
                S10.label = vent_label + "T1-S0"
                surf_list += [
                    S10,
                    SM1,
                ]
                if self.magnet_2:
                    SM2.label = mag_label + "T2-S0"
                    surf_list += [SM2]
                    if self.magnet_3:
                        SM3.label = mag_label + "T3-S0"
                        S23.label = vent_label + "T2-S0"
                        S3T.label = vent_label + "T3-S0"
                        surf_list += [S23, SM3, S3T]
                    else:
                        SW03.label = vent_label + "T2-S0"
                        surf_list += [SW03]
                else:
                    if self.magnet_3:
                        SW02.label = vent_label + "T2-S0"
                        SM3.label = mag_label + "T2-S0"
                        S3T.label = vent_label + "T3-S0"
                        surf_list += [SW02, SM3, S3T]
                    else:
                        S2.label = vent_label + "T2-S0"
                        surf_list += [S2]

            else:
                SW01.label = vent_label + "T1-S0"
                surf_list += [SW01]
                if self.magnet_2:
                    SM2.label = mag_label + "T1-S0"
                    surf_list += [SM2]
                    if self.magnet_3:
                        SM3.label = mag_label + "T2-S0"
                        S23.label = vent_label + "T1-S0"
                        S3T.label = vent_label + "T3-S0"
                        surf_list += [S23, SM3, S3T]
                    else:
                        SW03.label = vent_label + "T2-S0"
                        surf_list += [SW03]
                else:
                    if self.magnet_3:
                        SW02.label = vent_label + "T2-S0"
                        SM3.label = mag_label + "T1-S0"
                        S3T.label = vent_label + "T3-S0"
                        surf_list += [SW02, SM3, S3T]
                    else:
                        S2.label = vent_label + "T1-S0"
                        surf_list += [S2]
        else:
            if self.magnet_1:
                SW00.label = vent_label + "T0-S0"
                SM1.label = mag_label + "T0-S0"
                surf_list += [SW00, SM1]
                if self.magnet_2:
                    SM2.label = mag_label + "T1-S0"
                    surf_list += [SM2]
                    if self.magnet_3:
                        SM3.label = mag_label + "T2-S0"
                        S23.label = vent_label + "T1-S0"
                        S3T.label = vent_label + "T2-S0"
                        surf_list += [S23, SM3, S3T]
                    else:
                        SW03.label = vent_label + "T1-S0"
                        surf_list += [SW03]
                else:
                    if self.magnet_3:
                        SW02.label = vent_label + "T1-S0"
                        SM3.label = mag_label + "T1-S0"
                        S3T.label = vent_label + "T2-S0"
                        surf_list += [SW02, SM3, S3T]
                    else:
                        S2.label = vent_label + "T1-S0"
                        surf_list += [S2]
            else:
                S1.label = vent_label + "T0-S0"
                surf_list += [S1]
                if self.magnet_2:
                    SM2.label = mag_label + "T0-S0"
                    surf_list += [SM2]
                    if self.magnet_3:
                        SM3.label = mag_label + "T1-S0"
                        S23.label = vent_label + "T1-S0"
                        S3T.label = vent_label + "T2-S0"
                        surf_list += [S23, SM3, S3T]
                    else:
                        SW03.label = vent_label + "T1-S0"
                        surf_list += [SW03]
                else:
                    if self.magnet_3:
                        SW02.label = vent_label + "T1-S0"
                        SM3.label = mag_label + "T1-S0"
                        S3T.label = vent_label + "T2-S0"
                        surf_list += [SW02, SM3, S3T]
                    else:
                        S2.label = vent_label + "T1-S0"
                        surf_list += [S2]

    else:
        S1.label = vent_label + "T0-S0"
        surf_list += [S1]
        S2.label = vent_label + "T1-S0"
        surf_list += [S2]

    # Apply the transformations
    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)

    return surf_list
