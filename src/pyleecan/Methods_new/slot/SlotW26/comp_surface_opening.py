import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_opening(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot opening surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW26
        A SlotW26 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot opening surface [m**2]

    """
    Rbo = self.get_Rbo(lam=lam)

    S1 = self.H0 * self.W0

    # The bottom is an arc
    alpha = self.comp_angle_opening(lam=lam)
    Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

    # Because Slamination = S - Zs * Sslot
    if self.is_outwards(lam=lam):
        return S1 - Sarc
    else:
        return S1 + Sarc
