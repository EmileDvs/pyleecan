from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.arc_3 import Arc3
from ....Classes_new.geometry.segment import Segment
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def build_geometry(self, lam: Lamination | Notch | None = None) -> list:
    """Compute the curve (Line) needed to plot the object.
    The ending point of a curve is the starting point of the next curve
    in the list

    Parameters
    ----------
    self : SlotUD2
        A SlotUD2 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    curve_list: list
        A list of Segments

    """

    return [line.copy() for line in self.line_list]
