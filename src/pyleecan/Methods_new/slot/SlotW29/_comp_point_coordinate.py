import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotW29
        A SlotW29 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot point coordinates
    """
    Rbo = self.get_Rbo(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z12|| = W0
    alpha = np.arcsin(self.W0 / (2 * Rbo))

    Z0 = Rbo * np.exp(1j * 0)
    Z1 = Z0 * np.exp(-1j * alpha)

    if self.is_outwards(lam=lam):
        Z2 = Z1 + self.H0
        Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
        Z4 = Z3 + self.H1
        Z5 = Z4 - (self.W2 - self.W1) * 1j / 2.0
        Z6 = Z5 + self.H2
    else:
        Z2 = Z1 - self.H0
        Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
        Z4 = Z3 - self.H1
        Z5 = Z4 - (self.W2 - self.W1) * 1j / 2.0
        Z6 = Z5 - self.H2

    point_dict = dict()

    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["Z3"] = Z3
    point_dict["Z4"] = Z4
    point_dict["Z5"] = Z5
    point_dict["Z6"] = Z6
    # symetry
    point_dict["Z7"] = Z6.conjugate()
    point_dict["Z8"] = Z5.conjugate()
    point_dict["Z9"] = Z4.conjugate()
    point_dict["Z10"] = Z3.conjugate()
    point_dict["Z11"] = Z2.conjugate()
    point_dict["Z12"] = Z1.conjugate()
    return point_dict
