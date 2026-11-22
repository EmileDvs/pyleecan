import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotW13
        A SlotW13 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot coordinates
    """
    Rbo = self.get_Rbo(lam=lam)

    H1 = self.get_H1(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z10|| = W0
    alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

    # comp point coordinate (in complex)
    Z0 = Rbo * np.exp(1j * 0)
    Z1 = Z0 * np.exp(-1j * alpha)

    if self.is_outwards(lam=lam):
        Z2 = Z1 + self.H0
        Z3 = Z2 + H1 - (self.W1 - self.W0) * 1j / 2.0
        Z4 = Z3 + (self.W1 - self.W2) / 2.0 * 1j
        Z5 = Z4 + self.H2 - (self.W3 - self.W2) / 2.0 * 1j
    else:  # inward slot
        Z2 = Z1 - self.H0
        Z3 = Z2 - H1 - (self.W1 - self.W0) * 1j / 2.0
        Z4 = Z3 + (self.W1 - self.W2) / 2.0 * 1j
        Z5 = Z4 - self.H2 - (self.W3 - self.W2) / 2.0 * 1j

    point_dict = dict()
    # symetry
    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["Z3"] = Z3
    point_dict["Z4"] = Z4
    point_dict["Z5"] = Z5
    point_dict["Z6"] = Z5.conjugate()
    point_dict["Z7"] = Z4.conjugate()
    point_dict["Z8"] = Z3.conjugate()
    point_dict["Z9"] = Z2.conjugate()
    point_dict["Z10"] = Z1.conjugate()
    return point_dict
