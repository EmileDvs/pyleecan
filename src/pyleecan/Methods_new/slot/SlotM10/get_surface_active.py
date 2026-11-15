import numpy as np

from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.surface import Surface


def get_surface_active(self, alpha: float = 0, delta: complex = 0) -> Surface:
    """Return the full active surface

    Parameters
    ----------
    self : SlotM10
        A SlotM10 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)

    Returns
    -------
    surf_act: Surface
        Surface corresponding to the Active Area
    """

    # get the name of the lamination
    st = self.get_name_lam()

    point_dict = self._comp_point_coordinate()
    ZM1 = point_dict["ZM1"]
    ZM2 = point_dict["ZM2"]
    ZM3 = point_dict["ZM3"]
    ZM4 = point_dict["ZM4"]
    Z1 = point_dict["Z1"]
    Z4 = point_dict["Z4"]

    curve_list = list()
    curve_list.append(Segment(begin=ZM1, end=ZM2))
    # Case Z2-Z1 overlapping with ZM1-ZM2
    if self.H0 != 0 and self.H0 < self.H1 and self.W0 == self.W1:
        curve_list.append(Segment(begin=ZM1, end=Z1))
        curve_list.append(Segment(begin=Z1, end=ZM2))
    else:
        curve_list.append(Segment(begin=ZM1, end=ZM2))
    curve_list.append(Segment(begin=ZM2, end=ZM3))

    # Case Z3-Z4 overlapping with ZM3-ZM4
    if self.H0 != 0 and self.H0 < self.H1 and self.W0 == self.W1:
        curve_list.append(Segment(begin=ZM3, end=Z4))
        curve_list.append(Segment(begin=Z4, end=ZM4))
    else:
        curve_list.append(Segment(begin=ZM3, end=ZM4))
    curve_list.append(Segment(begin=ZM4, end=ZM1))

    Zmid = (ZM1 + ZM3) / 2

    surface = SurfLine(
        line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
    )

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
