import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot active inner surface (by analytical computation)

    Parameters
    ----------
    self : SlotM19
        A SlotM19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot active inner surface [m**2]

    """
    return self.comp_surface(lam=lam)  # Magnet perfectly match the slot
