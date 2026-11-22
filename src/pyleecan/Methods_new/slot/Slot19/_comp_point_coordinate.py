import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> list:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : Slot19
        A Slot19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_list: list
        A list of Points

    """
    Rbo = self.get_Rbo(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
    alpha0 = self.comp_angle_opening(lam=lam) / 2
    alpha1 = self.comp_angle_bottom(lam=lam) / 2

    # comp point coordinate (in complex)
    Z_ = Rbo * np.exp(1j * 0)
    Z0 = Z_ * np.exp(1j * alpha0)

    if self.is_outwards(lam=lam):
        Z1 = (Rbo + self.H0) * np.exp(1j * alpha1)
    else:  # inward slot
        Z1 = (Rbo - self.H0) * np.exp(1j * alpha1)

    # symetry
    Z2 = Z1.conjugate()
    Z3 = Z0.conjugate()

    return [Z3, Z2, Z1, Z0]
