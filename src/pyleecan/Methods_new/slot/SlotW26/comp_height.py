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
    self : SlotW26
        A SlotW26 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """
    Rbo = self.get_Rbo(lam=lam)

    # Computation of the arc height (P1,0,P8)
    alpha = self.comp_angle_opening(lam=lam) / 2
    Harc = float(Rbo * (1 - np.cos(alpha)))

    # Height of the arc (P2,C1,P7)
    Hwind = self.comp_height_active(lam=lam)

    if self.is_outwards(lam=lam):
        return self.H0 + Hwind - Harc
    else:
        return self.H0 + Hwind + Harc
