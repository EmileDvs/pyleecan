from ....Classes_new.geometry.segment import Segment
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def build_geometry(self, lam: Lamination | Notch | None = None) -> list:
    """Compute the curve (Segment) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotW14
        A SlotW14 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    curve_list: list
        A list of 8 Segment

    """

    line_dict = self._comp_line_dict(lam=lam)

    curve_list = [
        line_dict["1-2"],
        line_dict["2-3"],
        line_dict["3-4"],
        line_dict["4-5"],
        line_dict["5-6"],
        line_dict["6-7"],
        line_dict["7-8"],
        line_dict["8-9"],
    ]
    return [line for line in curve_list if line is not None]
