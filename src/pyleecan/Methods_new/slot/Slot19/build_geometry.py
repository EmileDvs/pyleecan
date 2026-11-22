from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def build_geometry(self, lam: Lamination | Notch | None = None) -> list:
    """Compute the curve (Line) needed to plot the object.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : Slot19
        A Slot19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    curve_list: list
        A list of 2 Segment and 1 Arc

    """

    [Z1, Z2, Z3, Z4] = self._comp_point_coordinate(lam=lam)

    # Creation of curve
    curve_list = list()
    curve_list.append(Segment(begin=Z1, end=Z2))
    if self.W1 > 0:
        curve_list.append(Arc1(begin=Z2, end=Z3, radius=abs(Z3)))
    curve_list.append(Segment(begin=Z3, end=Z4))

    return curve_list
