import numpy as np

from ....Functions_new.utils.geometry import inter_line_line
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_H1(self, lam: Lamination | Notch | None = None) -> float:
    """Return H1 in [m]

    Parameters
    ----------
    self : SlotW23
        A SlotW23 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    H1: float
        H1 in [m]

    """

    if not (self.H1_is_rad):
        return self.H1

    Rbo = self.get_Rbo(lam=lam)

    # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
    alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

    if self.is_outwards(lam=lam):
        Z2 = (Rbo + self.H0) * np.exp(-1j * alpha)

    else:  # inward slot
        Z2 = (Rbo - self.H0) * np.exp(-1j * alpha)

    # H1 in rad
    if self.is_cstt_tooth:
        Z2t = Z2 * np.exp(1j * np.pi / self.Zs)
        Zangle = np.exp(-1j * ((np.pi / 2) - self.H1)) + Z2t

        Zt1 = 1j * (self.W3 / 2)
        Zt2 = 1 + (1j * self.W3) / 2
        L = inter_line_line(Zt1, Zt2, Z2t, Zangle)
        Z3 = L[0]
        return abs(Z3.real - Z2.real)

    else:
        return (self.W1 - self.W0) * np.tan(self.H1) / 2.0  # convertion to m
