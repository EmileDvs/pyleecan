import numpy as np

from . import S15InnerError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_opening(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot opening surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW15
        A SlotW15 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot opening surface [m**2]

    """

    Rbo = self.get_Rbo(lam=lam)

    # The bottom is an arc
    alpha = self.comp_angle_opening(lam=lam)
    Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))
    Harc = float(Rbo * (1 - np.cos(alpha / 2)))
    S1 = (self.H0 + Harc) * self.W0

    # Because Slamination = S - Zs * Sslot
    if not self.is_outwards(lam=lam):
        raise S15InnerError("Slot Type 15 can't be used on inner lamination")
    return S1 - Sarc
