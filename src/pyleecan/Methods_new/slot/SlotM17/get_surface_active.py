import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine


def get_surface_active(self, alpha=0, delta=0):
    """Return the full active surface

    Parameters
    ----------
    self : SlotM17
        A SlotM17 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)

    Returns
    -------
    surf_act: Surface
        Surface corresponding to the Active Area
    """

    self.check()
    # get the name of the lamination
    st = self.get_name_lam()
    Rext = self.parent.Rext
    Rint = self.parent.Rint

    Z1 = -Rext * 1j
    Z2 = Rext
    Z3 = Rext * 1j
    curve_list = list()
    curve_list.append(Arc1(begin=Z1, end=Z2, radius=Rext, is_trigo_direction=True))
    curve_list.append(Arc1(begin=Z2, end=Z3, radius=Rext, is_trigo_direction=True))
    if Rint == 0:
        curve_list.append(Segment(begin=Z3, end=Z1))
    else:
        Z4 = Rint * 1j
        Z5 = Rint
        Z6 = -Rint * 1j
        curve_list.append(Segment(begin=Z3, end=Z4))
        curve_list.append(Arc1(begin=Z4, end=Z5, radius=-Rint, is_trigo_direction=False))
        curve_list.append(Arc1(begin=Z5, end=Z6, radius=-Rint, is_trigo_direction=False))
        curve_list.append(Segment(begin=Z6, end=Z1))

    surface = SurfLine(
        line_list=curve_list,
        label="Wind_" + st + "_R0_T0_S0",
        point_ref=Rint + (Rext - Rint) / 2,
    )

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
