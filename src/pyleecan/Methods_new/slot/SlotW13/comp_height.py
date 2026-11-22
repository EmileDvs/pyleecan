import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height(self, lam: Lamination | Notch | None = None):
    """Compute the height of the Slot.
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW13
        A SlotW13 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: Height of the slot [m]

    """

    Rbo = self.get_Rbo()

    H1 = self.get_H1()

    # Computation of the arc height
    alpha = self.comp_angle_opening() / 2
    Harc = float(Rbo * (1 - np.cos(alpha)))

    if self.is_outwards():
        return abs(Rbo - Harc + self.H0 + H1 + self.H2 + 1j * self.W3 / 2.0) - Rbo
    else:
        return self.H0 + H1 + self.H2 + Harc
