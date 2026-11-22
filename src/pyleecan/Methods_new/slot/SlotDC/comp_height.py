import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the Slot.
    Caution, the top of the Slot is an Arc

    Parameters
    ----------
    self : SlotDC
        A SlotDC object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """

    H = self.R3 + self.H3 + self.H2 + self.H1

    # Computation of the arc height
    Rbo = self.get_Rbo(lam=lam)
    alpha = self.comp_angle_opening(lam=lam) / 2
    Harc = float(Rbo * (1 - np.cos(alpha)))

    if self.is_outwards(lam=lam):
        return H - Harc
    else:
        return H + Harc
