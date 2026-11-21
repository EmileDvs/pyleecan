from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch
    from ....Classes_new.geometry.surface import Surface


def get_surface_active(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None) -> Surface:
    """Return the full winding surface

    Parameters
    ----------
    self : SlotM16
        A SlotM16 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    surf_wind: Surface
        Surface corresponding to the Winding Area
    """

    # get the name of the lamination
    st = self.get_name_lam()

    # Create curve list
    curve_list = self.build_geometry(lam=lam)[1:-1]
    curve_list.append(
        Segment(begin=curve_list[-1].get_end(), end=curve_list[0].get_begin())
    )

    # Create surface
    if self.is_outwards(lam=lam):
        Zmid = self.get_Rbo(lam=lam) + self.H0 + self.H1 / 2
    else:
        Zmid = self.get_Rbo(lam=lam) - self.H0 - self.H1 / 2
    surface = SurfLine(
        line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
    )

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
