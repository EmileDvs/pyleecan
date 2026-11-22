import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_opening(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot opening surface (by analytical computation)

    Parameters
    ----------
    self : SlotW10
        A SlotW10 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Sop: float
        Slot opening surface [m**2]

    """

    Rbo = self.get_Rbo(lam=lam)

    S1 = self.H0 * self.W0
    H1 = self.get_H1(lam=lam)
    S2 = 0.5 * (self.W0 + self.W1) * H1

    # The bottom is an arc
    alpha = self.comp_angle_opening(lam=lam)
    Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

    # Because Slamination = S - Zs * Sslot
    if self.is_outwards(lam=lam):
        return S1 + S2 - Sarc
    else:
        return S1 + S2 + Sarc
