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
    self : SlotW22
        A SlotW22 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot opening surface [m**2]

    """
    Rbo = self.get_Rbo(lam=lam)

    # Computation of isthmus surface
    if self.is_outwards(lam=lam):
        # Surface of the external disk
        Sext = ((self.H0 + Rbo) ** 2) * np.pi

        # Surface of the internal disk
        Sint = (Rbo**2) * np.pi
    else:
        # Surface of the external disk
        Sext = (Rbo**2) * np.pi

        # Surface of the internal disk
        Sint = ((Rbo - self.H0) ** 2) * np.pi
    # Surface of the ring
    Sring = Sext - Sint

    # Only an W0 angle of the ring
    return Sring * self.W0 / (2 * np.pi)
