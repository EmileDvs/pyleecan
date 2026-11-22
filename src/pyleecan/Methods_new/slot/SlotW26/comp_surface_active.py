import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotW26
        A SlotW26 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """

    # 2 half circle
    S1 = 0.5 * np.pi * self.R1**2
    S2 = 0.5 * np.pi * self.R2**2
    # Trapeze
    S3 = self.H1 * (2 * self.R1 + 2 * self.R2) / 2

    # Angle of the arc (P2,C1,P7)
    alpha2 = 2 * np.arcsin(self.W0 / (2.0 * self.R1))

    # Surface of arc (P2,C1,P7) in the isthmus
    Sarc = (self.R1**2.0) / 2.0 * (alpha2 - np.sin(alpha2))

    return S1 + S2 + S3 - Sarc
