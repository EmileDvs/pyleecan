import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height_active(self, Ndisc: int = 200, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the active area

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
    Hwind: float
        Height of the active area [m]

    """

    surf = self.get_surface_active(lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False))

    point_list = surf.discretize(Ndisc)
    point_list = abs(np.array(point_list))

    return max(point_list) - min(point_list)
