import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import WIND_LAB, COND_BOUNDARY_PROP_LAB, YSMR_LAB, YSML_LAB, YOKE_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.notch import Notch
    from ....Classes_new.geometry.surface import Surface


def get_surface_active(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None) -> Surface:
    """Return the full active surface

    Parameters
    ----------
    self : SlotM18
        A SlotM18 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    surf_act: Surface
        Surface corresponding to the Active Area
    """

    # get the name of the lamination
    st = self.get_name_lam()
    Rbo = self.get_Rbo(lam=lam)

    point_dict = self._comp_point_coordinate()
    ZM1 = point_dict["ZM1"]
    ZM2 = point_dict["ZM2"]
    ZM3 = point_dict["ZM3"]
    ZM4 = point_dict["ZM4"]

    curve_list: list[Line] = list()
    curve_list.append(Segment(begin=ZM1, end=ZM2, prop_dict={COND_BOUNDARY_PROP_LAB: YSMR_LAB}))

    if self.is_outwards(lam=lam):
        curve_list.append(Arc1(begin=ZM2, end=ZM3, radius=(Rbo - self.H0), is_trigo_direction=True))
    else:
        curve_list.append(Arc1(begin=ZM2, end=ZM3, radius=(Rbo + self.H0), is_trigo_direction=True))

    curve_list.append(Segment(begin=ZM3, end=ZM4, prop_dict={COND_BOUNDARY_PROP_LAB: YSML_LAB}))

    if self.is_outwards(lam=lam):
        curve_list.append(Arc1(begin=ZM4, end=ZM1, radius=-Rbo, is_trigo_direction=False))
    else:
        curve_list.append(Arc1(begin=ZM4, end=ZM1, radius=-Rbo, is_trigo_direction=False))
    # If no lamination, BC is required on bore
    curve_list[-1].prop_dict = {COND_BOUNDARY_PROP_LAB: YOKE_LAB}

    Zmid = (abs(ZM1) + abs(ZM3)) / 2

    surface = SurfLine(
        line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
    )

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
