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
    self : SlotW14
        A SlotW14 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    H1: float
        H1 in [m]

    """

    # H1 in rad
    if self.H1_is_rad:
        Rbo = self.get_Rbo(lam=lam)
        hssp = np.pi / self.Zs

        # alpha is the angle to rotate P0 so ||P1,P9|| = W0
        alpha = np.arcsin(self.W0 / (2 * Rbo))
        Harc = float(Rbo * (1 - np.cos(alpha)))

        Z1 = Rbo * np.exp(-1j * alpha)
        if self.is_outwards(lam=lam):
            R1 = Rbo - Harc + self.H0
            Z2 = Z1 + self.H0
        else:
            R1 = Rbo - Harc - self.H0
            Z2 = Z1 - self.H0

        Z3 = R1 + 1j * (self.W3 / 2 - R1 * np.sin(hssp)) / np.cos(hssp)

        # Z3t is Z3 in tooth ref
        Z3t = Z3 * np.exp(1j * hssp)
        if self.is_outwards(lam=lam):
            Z4t = Z3t + self.H3
        else:
            Z4t = Z3t - self.H3

        Z4 = Z4t * np.exp(-1j * hssp)
        # ending calcul slot point

        Zop = 0.5 * np.tan(self.H1)

        if self.is_outwards(lam=lam):
            Zc2 = Z2 - 0.5 * 1j + Zop
        else:
            Zc2 = Z2 - 0.5 * 1j - Zop

        ZiH = inter_line_line(Z3, Z4, Z2, Zc2)
        ZiH = ZiH[0]

        if self.is_outwards(lam=lam):
            H1 = abs(ZiH - Z3)
        else:
            H1 = abs(Z3 - ZiH)
        return H1  # convertion to m

    else:  # H1 in m
        return self.H1
