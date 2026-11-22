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
    self : SlotW25
        A SlotW25 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """
    point_dict = self._comp_point_coordinate(lam=lam)
    Z4 = point_dict["Z4"]
    Rbo = self.get_Rbo(lam=lam)

    if self.is_outwards(lam=lam):
        return abs(Z4) - Rbo
    else:  # inward slot
        return Rbo - abs(Z4)
