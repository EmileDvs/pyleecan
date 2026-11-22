import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_angle_bottom(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the slot bottom angle of the Slot

    Parameters
    ----------
    self : Slot19
        A Slot19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    alpha: float
        slot bottom angle [rad]

    """

    Rbo = self.get_Rbo(lam=lam)

    if self.Wx_is_rad:
        return self.W1
    else:
        if self.is_outwards(lam=lam):
            alpha = 2 * float(np.arcsin(self.W1 / (2 * Rbo + 2 * self.H0)))
        else:  # inward slot
            alpha = 2 * float(np.arcsin(self.W1 / (2 * Rbo - 2 * self.H0)))

    return alpha
