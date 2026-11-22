import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the Slot.
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW30
        A SlotW30 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """
    point_dict = self._comp_point_coordinate(lam=lam)
    if self.R2 != 0:
        Z7 = point_dict["Z7"]
        Z6 = point_dict["Z6"]
    else:
        Z7 = point_dict["Z60"]
        Z6 = point_dict["Z80"]

    Rbo = self.get_Rbo(lam=lam)

    # The bottom is an arc
    alpha = self.comp_angle_opening(lam=lam)
    Harc = float(Rbo * (1 - np.cos(alpha / 2)))

    if self.is_outwards(lam=lam):
        return abs(Z7) - Rbo

    else:
        return abs((Z7 + Z6) / 2 - Rbo)
