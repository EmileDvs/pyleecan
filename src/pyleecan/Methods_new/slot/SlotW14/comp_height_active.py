import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the winding area

    Parameters
    ----------
    self : SlotW14
        A SlotW14 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Hwind: float
        Height of the winding area [m]

    """
    H1 = self.get_H1()
    Rbo = self.get_Rbo(lam=lam)

    # alpha is the angle to rotate P0 so ||P1,P10|| = W0
    alpha = np.arcsin(self.W0 / (2 * Rbo))

    # Compute W1 to have tooth width at W3
    Harc = Rbo * (1 - np.cos(alpha / 2))

    if self.is_outwards(lam=lam):
        R1 = Rbo - Harc + self.H0 + H1
    else:
        R1 = Rbo + Harc - self.H0 - H1

    theta1 = np.arcsin(self.W3 * 0.5 / R1) * 2
    hsp = np.pi / self.Zs
    W1 = np.sin((hsp * 2 - theta1) * 0.5) * R1 * 2

    Z9 = Rbo * np.exp(-1j * alpha)

    if self.is_outwards(lam=lam):
        Z8 = Z9 + self.H0
        Z7 = Z8 + H1 - (W1 - self.W0) * 1j / 2
    else:
        Z8 = Z9 - self.H0
        Z7 = Z8 - H1 - (W1 - self.W0) * 1j / 2

    # Rotate Z7 to get the tooth parallel to Ox
    Z7r = Z7 * np.exp(1j * hsp)
    if self.is_outwards(lam=lam):
        Z6r = Z7r + self.H3
    else:
        Z6r = Z7r - self.H3

    W2 = np.tan(hsp) * Z6r.real
    Z5r = Z6r.real + 1j * W2
    Z5 = Z5r * np.exp(-1j * hsp)
    Z3 = Z7.conjugate()

    Ztan1 = (Z3 + Z7) / 2.0
    Ztan2 = Z5

    return abs(Ztan1 - Ztan2)
