import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height(self, Ndisc: int = 200, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the Slot.
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : Slot
        A Slot object
    Ndisc : int
        Number of point to discretize the lines
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """

    Rbo = self.get_Rbo()

    surf = self.get_surface()

    point_list = surf.discretize(Ndisc)
    point_list = np.array(point_list)
    if self.is_outwards():
        return max(abs(point_list)) - Rbo
    else:
        return Rbo - min(abs(point_list))
