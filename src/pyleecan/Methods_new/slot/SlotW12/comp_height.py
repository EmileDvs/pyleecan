import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the Slot.
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW12
        A SlotW12 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """

    Rbo = self.get_Rbo(lam=lam)

    # Computation of the arc height
    alpha = self.comp_angle_opening(lam=lam) / 2
    Harc = float(Rbo * (1 - np.cos(alpha)))

    if self.is_outwards(lam=lam):
        return self.H0 - Harc + self.R1 * 2 + self.H1 + self.R2
    else:
        return self.H0 + Harc + self.R1 * 2 + self.H1 + self.R2
