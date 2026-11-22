import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height_opening(self, Ndisc: int = 200, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the opening area (Hslot - Hactive)

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
        Height of the opening area [m]

    """

    return self.comp_height(Ndisc=Ndisc, lam=lam) - self.comp_height_active(Ndisc=Ndisc, lam=lam)
