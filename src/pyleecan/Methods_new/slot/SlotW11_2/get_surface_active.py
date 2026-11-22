from ....classes_common.parents import container_or_parent
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import WIND_LAB, DRAW_PROP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.notch import Notch
    from ....Classes_new.geometry.surface import Surface


def get_surface_active(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None) -> Surface:
    """Return the full winding surface

    Parameters
    ----------
    self : SlotW11_2
        A SlotW11_2 object
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
    lam = container_or_parent(self, lam, "lam")

    # Create curve list
    line_dict = self._comp_line_dict(lam=lam)
    if self.H1 != 0:
        curve_list: list[Line] = [
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-3"],
        ]
    else:
        # Add 2-3 and 9-3 to make sure that FEMM handles all the lines
        # cf (Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
        curve_list: list[Line] = [
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-9"],
            line_dict["9-2"],
        ]
    curve_list = [line for line in curve_list if line is not None]

    # Only the closing arc (8-3) needs to be drawn (in FEMM)
    for curve in curve_list[:-1]:
        if curve.prop_dict is None:
            curve.prop_dict = dict()
        curve.prop_dict.update({DRAW_PROP_LAB: False})

    # Create surface
    H1 = self.get_H1(lam=lam)
    if self.is_outwards(lam=lam):
        Zmid = self.get_Rbo(lam=lam) + self.H0 + H1 + self.H2 / 2
    else:
        Zmid = self.get_Rbo(lam=lam) - self.H0 - H1 - self.H2 / 2
    label = lam.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
    surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
