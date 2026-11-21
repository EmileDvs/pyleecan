import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the winding area

    Parameters
    ----------
    self : SlotW26
        A SlotW26 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Hwind: float
        Height of the winding area [m]

    """

    # Height of the arc (P2,C1,P7)
    alpha2 = np.arcsin(self.W0 / (2.0 * self.R1))
    Harc2 = float(self.R1 * (1 - np.cos(alpha2)))

    return self.H1 + self.R2 + self.R1 - Harc2
