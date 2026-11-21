from ....classes_common.parents import container_or_parent
from ....Functions_new.utils.labels import WIND_LAB, DRAW_PROP_LAB
from ....Classes_new.geometry.surf_line import SurfLine
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
    self : SlotW24
        A SlotW24 object
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
    line_dict = self._comp_line_dict()
    curve_list: list[Line] = [
        line_dict["1-2"],
        line_dict["2-3"],
        line_dict["3-4"],
        line_dict["4-1"],
    ]
    curve_list = [line for line in curve_list if line is not None]

    # Only the closing arc (4-1) needs to be drawn (in FEMM)
    for curve in curve_list[:-1]:
        if curve.prop_dict is None:
            curve.prop_dict = dict()
        curve.prop_dict.update({DRAW_PROP_LAB: False})

    # Create surface
    if self.is_outwards():
        Zmid = self.get_Rbo() + self.H2 / 2
    else:
        Zmid = self.get_Rbo() - self.H2 / 2
    label = lam.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
    surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
