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
    self : SlotW29
        A SlotW29 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot opening surface [m**2]

    """

    Rbo = self.get_Rbo(lam=lam)

    S0 = self.H0 * self.W0
    S1 = self.H1 * self.W1

    # The bottom is an arc
    alpha = self.comp_angle_opening(lam=lam)
    Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

    # Because Slamination = S - Zs * Sslot
    # Selection type Wedge
    if self.wedge_type == 0:
        if self.is_outwards(lam=lam):
            return S1 + S0 - Sarc
        else:
            return S1 + S0 + Sarc

    if self.wedge_type == 1:
        if self.is_outwards(lam=lam):
            return S0 - Sarc
        else:
            return S0 + Sarc

    raise NotImplementedError(f"SlotW29.wedge_type must be 0 or 1, got {self.wedge_type!r}")
