import numpy as np



from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.surf_line import SurfLine
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
    self : SlotM19
        A SlotM19 object
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
    Rbo = self.get_Rbo(lam=lam)
    # get the name of the lamination
    st = self.get_name_lam()

    point_dict = self._comp_point_coordinate()
    Zmid = point_dict["Zmid"]
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]

    curve_list: list[Line] = list()
    curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z3))
    curve_list.append(Segment(begin=Z3, end=Z4))

    if self.is_outwards(lam=lam):
        curve_list.append(Arc1(begin=Z4, end=Z1, radius=-Rbo, is_trigo_direction=False))
    else:
        curve_list.append(Arc1(begin=Z4, end=Z1, radius=-Rbo, is_trigo_direction=False))

    surface = SurfLine(
        line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=(Z1 + Z3) / 2
    )

    # Apply transformation
    if alpha != 0:
        surface.rotate(alpha)
    if delta != 0:
        surface.translate(delta)

    return surface
