import numpy as np

from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.surf_line import SurfLine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.geometry.surface import Surface


def get_surface_active(self, alpha: float = 0, delta: complex = 0) -> Surface:
    """Return the full active surface

    Parameters
    ----------
    self : SlotM15
        A SlotM15 object
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
    ZM0 = point_dict["ZM0"]
    ZM1 = point_dict["ZM1"]
    ZM2 = point_dict["ZM2"]
    ZM3 = point_dict["ZM3"]
    ZM4 = point_dict["ZM4"]

    curve_list: list[Line] = list()
    curve_list.append(Segment(begin=ZM1, end=ZM2))
    if self.is_outwards():
        curve_list.append(Arc1(begin=ZM2, end=ZM3, radius=-self.Rtopm, is_trigo_direction=False))
    else:
        curve_list.append(Arc1(begin=ZM2, end=ZM3, radius=self.Rtopm))
    curve_list.append(Segment(begin=ZM3, end=ZM4))
    curve_list.append(Arc1(begin=ZM4, end=ZM1, radius=-abs(ZM4), is_trigo_direction=False))

    Zmid = (abs(ZM1) + abs(ZM3)) / 2  # ref. point on x-axis with respective radius

    surface = SurfLine(
        line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
    )

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
