import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotM11
        A SlotM11 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot coordinates
    """

    Rbo = self.get_Rbo(lam=lam)

    Z1 = Rbo * np.exp(-1j * self.W0 / 2)

    if self.is_outwards(lam=lam):
        Z2 = (Rbo + self.H0) * np.exp(-1j * self.W0 / 2)
        ZM1 = (Rbo + self.H0) * np.exp(-1j * self.W1 / 2)
        ZM2 = (Rbo + self.H0 - self.H1) * np.exp(-1j * self.W1 / 2)
    else:  # inward slot
        Z2 = (Rbo - self.H0) * np.exp(-1j * self.W0 / 2)
        ZM1 = (Rbo - self.H0) * np.exp(-1j * self.W1 / 2)
        ZM2 = (Rbo - self.H0 + self.H1) * np.exp(-1j * self.W1 / 2)

    point_dict = dict()
    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["ZM1"] = ZM1
    point_dict["ZM2"] = ZM2
    # symetry

    point_dict["Z3"] = Z2.conjugate()
    point_dict["Z4"] = Z1.conjugate()
    point_dict["ZM3"] = ZM2.conjugate()
    point_dict["ZM4"] = ZM1.conjugate()

    return point_dict
