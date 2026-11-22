import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotW22
        A SlotW22 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """
    Rbo = self.get_Rbo()

    if self.is_outwards():
        # Surface of the external disk
        Sext = ((self.H2 + self.H0 + Rbo) ** 2) * np.pi

        # Surface of the internal disk
        Sint = ((self.H0 + Rbo) ** 2) * np.pi
    else:
        # Surface of the external disk
        Sext = ((Rbo - self.H0) ** 2) * np.pi

        # Surface of the internal disk
        Sint = ((Rbo - self.H2 - self.H0) ** 2) * np.pi

    # Surface of the ring
    Sring = Sext - Sint

    # Only an W2 angle of the ring
    return Sring * self.W2 / (2 * np.pi)
