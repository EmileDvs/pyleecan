from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def build_geometry(self, lam: Lamination | Notch | None = None) -> list:
    """Compute the curve (Line) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotM18
        A SlotM18 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    curve_list: list
        A list of 3 Segments

    """
    Rbo = self.get_Rbo(lam=lam)
    point_dict = self._comp_point_coordinate(lam=lam)
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]

    # Creation of curve
    curve_list = list()
    curve_list.append(Arc1(begin=Z1, end=Z2, radius=Rbo, is_trigo_direction=True))

    return curve_list
