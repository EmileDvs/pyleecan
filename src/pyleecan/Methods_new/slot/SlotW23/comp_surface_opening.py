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
    self : SlotW23
        A SlotW23 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot opening surface [m**2]

    """
    if self.is_cstt_tooth and (self.W1 is None or self.W2 is None):
        # Compute W1 and W2 to match W3 tooth constraint
        self._comp_W(lam=lam)

    Rbo = self.get_Rbo(lam=lam)

    # Wint is the with at the top of the opening
    alpha = self.comp_angle_opening(lam=lam)
    if self.is_outwards(lam=lam):
        Wint = 2 * np.sin(alpha / 2) * (Rbo + self.H0)
        # Arc between opening H0 and wedge H1
        Sarc = ((Rbo + self.H0) ** 2.0) / 2.0 * (alpha - np.sin(alpha))
        # The opening part is radial
        S1 = (np.pi * ((Rbo + self.H0) ** 2) - np.pi * (Rbo**2)) * alpha / (2 * np.pi) - Sarc
    else:
        Wint = 2 * np.sin(alpha / 2) * (Rbo - self.H0)
        # Arc between opening H0 and wedge H1
        Sarc = ((Rbo - self.H0) ** 2.0) / 2.0 * (alpha - np.sin(alpha))
        # The opening part is radial
        S1 = (np.pi * (Rbo**2) - np.pi * ((Rbo - self.H0) ** 2)) * alpha / (2 * np.pi) + Sarc

    S2 = 0.5 * self.get_H1(lam=lam) * (Wint + self.W1)

    return S1 + S2
