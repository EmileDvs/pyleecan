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
    self : SlotW25
        A SlotW25 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot opening surface [m**2]

    """

    point_dict = self._comp_point_coordinate(lam=lam)
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]

    if self.is_outwards(lam=lam):
        Rint = abs(Z1)
        Rext = abs(Z2)
    else:
        Rint = abs(Z2)
        Rext = abs(Z1)

    # Surface of a slot pitch
    Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

    # Tooth surface
    St = self.H1 * self.W4

    alpha_bore = 2 * np.arcsin(self.W4 / (2 * Rint))
    Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

    alpha_yoke = 2 * np.arcsin(self.W4 / (2 * Rext))
    Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

    return Sring - (St + Sarc_yoke - Sarc_bore)
