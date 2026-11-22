import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotW26
        A SlotW26 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot point coordinates
    """
    Rbo = self.get_Rbo(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
    alpha = float(np.arcsin(self.W0 / (2 * Rbo)))
    # comp point coordinate (in complex)
    Z0 = Rbo * np.exp(1j * 0)
    Z1 = Z0 * np.exp(-1j * alpha)

    if self.is_outwards(lam=lam):
        Z2 = Z1 + self.H0
        Zc1 = Z2.real + np.sqrt(self.R1**2 - (self.W0 / 2.0) ** 2)
        Z3 = Zc1 - self.R1 * 1j
        Zc2 = Zc1 + self.H1
        Z4 = Zc2 - 1j * self.R2
        Zbot = Zc2 + self.R2
    else:  # inward slot
        Z2 = Z1 - self.H0
        Zc1 = Z2.real - np.sqrt(self.R1**2 - (self.W0 / 2.0) ** 2)
        Z3 = Zc1 - self.R1 * 1j
        Zc2 = Zc1 - self.H1
        Z4 = Zc2 - 1j * self.R2
        Zbot = Zc2 - self.R2

    point_dict = dict()
    # symetry
    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["Z3"] = Z3
    point_dict["Z4"] = Z4
    point_dict["Z5"] = Z4.conjugate()
    point_dict["Z6"] = Z3.conjugate()
    point_dict["Z7"] = Z2.conjugate()
    point_dict["Z8"] = Z1.conjugate()
    point_dict["Zc1"] = Zc1
    point_dict["Zc2"] = Zc2
    point_dict["Zbot"] = Zbot
    return point_dict
