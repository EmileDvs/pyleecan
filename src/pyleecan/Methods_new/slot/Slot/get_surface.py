from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import DRAW_PROP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_surface(self, lam: Lamination | Notch | None = None) -> SurfLine:
    """Returns the surface delimiting the slot

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    surface: SurfLine
        A SurfLine object representing the slot

    """
    Rbo = self.get_Rbo(lam=lam)
    curve_list = self.build_geometry(lam=lam)

    # Remove line overlapping with bore/yoke lines (for FEMM)
    for line in curve_list:
        if line.prop_dict is None:
            line.prop_dict = dict()
        line.prop_dict[DRAW_PROP_LAB] = False

    # Add closing Arc
    Zbegin = curve_list[-1].get_end()
    Zend = curve_list[0].get_begin()
    curve_list.append(Arc1(begin=Zbegin, end=Zend, radius=-Rbo, is_trigo_direction=False))

    surf = SurfLine(line_list=curve_list, label="Slot")
    surf.comp_point_ref(is_set=True)
    return surf
