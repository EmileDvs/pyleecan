import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot total surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : Slot19
        A Slot19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot total surface [m**2]

    """

    Rbo = self.get_Rbo(lam=lam)

    # Wint is the with at the top of the opening
    alpha0 = self.comp_angle_opening(lam=lam)
    alpha1 = self.comp_angle_bottom(lam=lam)

    if self.is_outwards(lam=lam):
        R1 = Rbo + self.H0
    else:
        R1 = Rbo - self.H0

    W0 = 2 * Rbo * np.sin(alpha0 / 2)
    W1 = 2 * R1 * np.sin(alpha1 / 2)

    Str = 1 / 2 * (W0 + W1) * self.H0
    S0 = Rbo**2 / 2 * (alpha0 - np.sin(alpha0))
    S1 = R1**2 / 2 * (alpha1 - np.sin(alpha1))

    return Str + S1 - S0
