import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotM13
        A SlotM13 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot coordinates
    """

    Rbo = self.get_Rbo(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z10|| = W0
    alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

    Z1 = Rbo * np.exp(-1j * alpha)

    alpha_lim = 2 * np.arcsin(self.W1 * 0.5 / self.Rtopm)  # Angle of the top arc
    H_top_arc = self.Rtopm * (1 - np.cos(alpha_lim / 2))  # Heiht of the top arc
    if self.is_outwards(lam=lam):
        Z2 = Z1 + self.H0
    else:  # inward slot
        Z2 = Z1 - self.H0
    ZM1 = Z2.real - 1j * self.W1 / 2
    if self.is_outwards(lam=lam):
        ZM0 = Z2.real - self.H1
        Zc = ZM0 + self.Rtopm
        ZM2 = ZM1 - self.H1 + H_top_arc
    else:  # inward slot
        ZM0 = Z2.real + self.H1
        Zc = ZM0 - self.Rtopm
        ZM2 = ZM1 + self.H1 - H_top_arc

    point_dict = dict()
    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["ZM1"] = ZM1
    point_dict["ZM2"] = ZM2
    point_dict["ZM0"] = ZM0
    point_dict["Zc"] = Zc
    # symetry
    point_dict["Z3"] = Z2.conjugate()
    point_dict["Z4"] = Z1.conjugate()
    point_dict["ZM3"] = ZM2.conjugate()
    point_dict["ZM4"] = ZM1.conjugate()

    return point_dict
