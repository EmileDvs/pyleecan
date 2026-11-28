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


def build_geometry(self, alpha: float = 0, delta: complex = 0, is_simplified: bool = False, lam: Lamination | None = None, lam_label: str | None = None) -> list:
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
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    surf_list: list
        List of SurfLine needed to draw the HoleM51

    """
    lam = container_or_parent(self, lam, "lam")
    # Get correct label for surfaces
    if lam_label is None:
        lam_label = lam.get_label()
    R_id, surf_type = self.get_R_id(lam=lam)
    vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
    mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

    Rext = self.get_Rext(lam=lam)

    # Get all the points
    point_dict = self._comp_point_coordinate(lam=lam)
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
    curve_list: list[Line] = list()
    curve_list.append(Arc1(begin=Z21, end=Z22, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z22, end=Z23))
    curve_list.append(Segment(begin=Z23, end=Z19))
    curve_list.append(Segment(begin=Z19, end=Z21))
    point_ref = (Z21 + Z22 + Z23 + Z19) / 4
    S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Surface for magnet_0
    curve_list = list()
    if is_simplified:
        curve_list.append(Segment(begin=Z24, end=Z18))
        curve_list.append(Segment(begin=Z19, end=Z23))
    else:
        curve_list.append(Segment(begin=Z24, end=Z18))
        curve_list.append(Segment(begin=Z18, end=Z19))
        curve_list.append(Segment(begin=Z19, end=Z23))
        curve_list.append(Segment(begin=Z23, end=Z24))
    point_ref = (Z24 + Z18 + Z19 + Z23) / 4

    S2 = SurfLine(line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref)

    # Air surface between magnet_0 and magnet_1
    curve_list = list()
    curve_list.append(Segment(begin=Z24, end=Z25))
    curve_list.append(Segment(begin=Z25, end=Z26))
    curve_list.append(Segment(begin=Z26, end=Z14))
    curve_list.append(Segment(begin=Z14, end=Z16))
    curve_list.append(Segment(begin=Z16, end=Z18))
    curve_list.append(Segment(begin=Z18, end=Z24))
    point_ref = (Z25 + Z16) / 2
    S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Surface for magnet_1
    curve_list = list()
    if is_simplified:
        curve_list.append(Segment(begin=Z1, end=Z13))
        curve_list.append(Segment(begin=Z14, end=Z26))
    else:
        curve_list.append(Segment(begin=Z26, end=Z1))
        curve_list.append(Segment(begin=Z1, end=Z13))
        curve_list.append(Segment(begin=Z13, end=Z14))
        curve_list.append(Segment(begin=Z14, end=Z26))
    point_ref = (Z26 + Z1 + Z13 + Z14) / 4
    S4 = SurfLine(line_list=curve_list, label=mag_label + "T1-S0", point_ref=point_ref)

    # Air surface between magnet_1 and magnet_2
    curve_list = list()
    curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z3))
    curve_list.append(Segment(begin=Z3, end=Z9))
    curve_list.append(Segment(begin=Z9, end=Z11))
    curve_list.append(Segment(begin=Z11, end=Z13))
    curve_list.append(Segment(begin=Z13, end=Z1))
    point_ref = (Z11 + Z2) / 2
    S5 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Surface for magnet_2
    curve_list = list()
    if is_simplified:
        curve_list.append(Segment(begin=Z4, end=Z8))
        curve_list.append(Segment(begin=Z9, end=Z3))
    else:
        curve_list.append(Segment(begin=Z4, end=Z8))
        curve_list.append(Segment(begin=Z8, end=Z9))
        curve_list.append(Segment(begin=Z9, end=Z3))
        curve_list.append(Segment(begin=Z3, end=Z4))
    point_ref = (Z4 + Z8 + Z9 + Z3) / 4

    S6 = SurfLine(line_list=curve_list, label=mag_label + "T2-S0", point_ref=point_ref)

    # Air surface bore around magnet_2
    curve_list = list()
    curve_list.append(Arc1(begin=Z5, end=Z6, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z6, end=Z8))
    curve_list.append(Segment(begin=Z8, end=Z4))
    curve_list.append(Segment(begin=Z4, end=Z5))
    point_ref = (Z4 + Z5 + Z6 + Z8) / 4
    S7 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Air surface bore around magnet_2 (no magnet_2 and magnet_1)
    curve_list = list()
    curve_list.append(Arc1(begin=Z5, end=Z6, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z6, end=Z11))
    curve_list.append(Segment(begin=Z11, end=Z13))
    curve_list.append(Segment(begin=Z13, end=Z1))
    curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z5))
    point_ref = (Z2 + Z11) / 2
    S8 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Air surface bore around magnet_0 (no magnet_0 and magnet_1)
    curve_list = list()
    curve_list.append(Arc1(begin=Z21, end=Z22, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z22, end=Z25))
    curve_list.append(Segment(begin=Z25, end=Z26))
    curve_list.append(Segment(begin=Z26, end=Z14))
    curve_list.append(Segment(begin=Z14, end=Z16))
    curve_list.append(Segment(begin=Z16, end=Z21))
    point_ref = (Z25 + Z16) / 2
    S9 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Air surface bore around magnet_1 (no magnet_1 and magnet_0 and magnet_2)
    curve_list = list()
    curve_list.append(Segment(begin=Z24, end=Z25))
    curve_list.append(Segment(begin=Z25, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z3))
    curve_list.append(Segment(begin=Z3, end=Z9))
    curve_list.append(Segment(begin=Z9, end=Z11))
    curve_list.append(Segment(begin=Z11, end=Z16))
    curve_list.append(Segment(begin=Z16, end=Z18))
    curve_list.append(Segment(begin=Z18, end=Z24))
    point_ref = (Z1 + Z13) / 2
    S10 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Air surface bore around magnet_1 (no magnet_1 and no magnet_0 and magnet_2)
    curve_list = list()
    curve_list.append(Arc1(begin=Z21, end=Z22, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z22, end=Z25))
    curve_list.append(Segment(begin=Z25, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z3))
    curve_list.append(Segment(begin=Z3, end=Z9))
    curve_list.append(Segment(begin=Z9, end=Z11))
    curve_list.append(Segment(begin=Z11, end=Z16))
    curve_list.append(Segment(begin=Z16, end=Z21))
    point_ref = (Z1 + Z13) / 2
    S11 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Air surface bore around magnet_1 (no magnet_1 and magnet_0 and no magnet_2)
    curve_list = list()
    curve_list.append(Arc1(begin=Z5, end=Z6, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z6, end=Z11))
    curve_list.append(Segment(begin=Z11, end=Z16))
    curve_list.append(Segment(begin=Z16, end=Z18))
    curve_list.append(Segment(begin=Z18, end=Z24))
    curve_list.append(Segment(begin=Z24, end=Z25))
    curve_list.append(Segment(begin=Z25, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z5))
    point_ref = (Z1 + Z13) / 2
    S12 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Air surface No magnet
    curve_list = list()
    curve_list.append(Arc1(begin=Z5, end=Z6, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z6, end=Z11))
    curve_list.append(Segment(begin=Z11, end=Z16))
    curve_list.append(Segment(begin=Z16, end=Z21))
    curve_list.append(Arc1(begin=Z21, end=Z22, radius=Rext - self.H1))
    curve_list.append(Segment(begin=Z22, end=Z25))
    curve_list.append(Segment(begin=Z25, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z5))
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
