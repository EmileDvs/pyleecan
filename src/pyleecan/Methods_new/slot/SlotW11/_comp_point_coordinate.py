import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotW11
        A SlotW11 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot coordinates
    """

    if self.is_cstt_tooth and (self.W1 is None or self.W2 is None):
        # Compute W1 and W2 to match W3 tooth constraint
        self._comp_W(lam=lam)

    Rbo = self.get_Rbo(lam=lam)

    H1 = self.get_H1(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
    alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

    # comp point coordinate (in complex)
    Z0 = Rbo * np.exp(1j * 0)
    Z1 = Z0 * np.exp(-1j * alpha)

    if self.is_outwards(lam=lam):
        Z2 = Z1 + self.H0
        Z3 = Z2.real + H1 + -1j * self.W1 / 2.0
        Z4 = Z3.real + (self.H2 - self.R1) - 1j * self.W2 / 2.0
        Z5 = Z4 + self.R1 + self.R1 * 1j
        # rot_sign = 1  # Rotation direction for Arc1
    else:  # inward slot
        Z2 = Z1 - self.H0
        Z3 = Z2.real - H1 + -1j * self.W1 / 2.0
        Z4 = Z3.real - (self.H2 - self.R1) - 1j * self.W2 / 2.0
        Z5 = Z4 - self.R1 + self.R1 * 1j
        # rot_sign = -1  # Rotation direction for Arc1

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
    point_dict["Zc1"] = Z4 + 1j * self.R1
    point_dict["Zc2"] = point_dict["Z7"] - 1j * self.R1

    return point_dict
