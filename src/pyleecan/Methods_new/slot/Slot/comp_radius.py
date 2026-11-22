import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_radius(self, lam: Lamination | Notch | None = None):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]

    """

    Rbo = self.get_Rbo(lam=lam)

    H = self.comp_height(lam=lam)
    Hmag = self.comp_height_active(lam=lam)

    if H < Hmag:
        if self.is_outwards(lam=lam):
            return (Rbo - Hmag + H, Rbo + H)
        else:
            return (Rbo - H, Rbo + Hmag - H)
    else:
        if self.is_outwards(lam=lam):
            return (Rbo, Rbo + H)
        else:
            return (Rbo - H, Rbo)
