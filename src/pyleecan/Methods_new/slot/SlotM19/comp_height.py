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
    self : SlotM19
        A SlotM19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """

    point_dict = self._comp_point_coordinate()
    Zmid = point_dict["Zmid"]
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]

    Rbo = self.get_Rbo(lam=lam)

    if self.is_outwards(lam=lam):
        return np.abs(np.sqrt(Z2.real**2 + Z2.imag**2)) - np.abs(Rbo)

    else:
        return self.H0
