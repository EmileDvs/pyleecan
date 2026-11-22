import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_angle_active_eq(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the equivalent angle of the active part of the slot
    (Ideal polar shape with the same surface and height)

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    alpha: float
        Average angle of the slot [rad]

    """

    Swind = self.comp_surface_active(lam=lam)
    Hwind = self.comp_height_active(lam=lam)
    Rmw = self.comp_radius_mid_active(lam=lam)
    Rext = Rmw + Hwind / 2
    Rint = Rmw - Hwind / 2

    return Swind * 2 * np.pi / (np.pi * Rext**2 - np.pi * Rint**2)
