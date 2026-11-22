import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotM19
        A SlotM19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot coordinates
    """

    Rbo = self.get_Rbo(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z4|| = W1
    alpha = float(np.arcsin(self.W1 / (2 * Rbo)))

    Z1 = Rbo * np.exp(-1j * alpha)

    if self.is_outwards(lam=lam):
        Zmid = Rbo + self.H0

    else:  # inward slot
        Zmid = Rbo - self.H0

    Z2 = Zmid - 1j * (self.W0 / 2)

    point_dict = dict()
    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["Zmid"] = Zmid
    # symetry
    point_dict["Z3"] = Z2.conjugate()
    point_dict["Z4"] = Z1.conjugate()

    return point_dict
