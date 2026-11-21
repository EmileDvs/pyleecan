from ....classes_common.parents import container_or_parent
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import SOP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_surface_opening(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None) -> list:
    """Return the list of surfaces defining the opening area of the Slot

    Parameters
    ----------
    self : SlotUD
        A SlotUD object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    surf_list : list
        list of surfaces objects
    """
    lam = container_or_parent(self, lam, "lam")

    # get curve_list
    line_list = self.build_geometry(lam=lam)
    curve_list_start = line_list[: self.wind_begin_index]
    curve_list_end = line_list[self.wind_end_index :]
    # Active Line
    Zb = curve_list_start[-1].get_end()
    Ze = curve_list_end[0].get_begin()
    if self.type_line_wind == 0:
        act_line = Segment(begin=Zb, end=Ze)
    else:
        act_line = Arc1(
            begin=Zb,
            end=Ze,
            radius=abs(Zb),
            is_trigo_direction=True,
        )
    bot_line = Arc1(
        begin=curve_list_end[-1].get_end(),
        end=curve_list_start[0].get_begin(),
        radius=-self.get_Rbo(lam=lam),
        is_trigo_direction=False,
    )

    curve_list = curve_list_start + [act_line] + curve_list_end + [bot_line]
    label = lam.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
    surface = SurfLine(line_list=curve_list, label=label)
    surface.comp_point_ref(is_set=True)

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return [surface]
