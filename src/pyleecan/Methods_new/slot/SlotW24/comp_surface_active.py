import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """

    Rbo = self.get_Rbo(lam=lam)
    point_dict = self._comp_point_coordinate()

    if self.is_outwards(lam=lam):
        Rint = Rbo
        Rext = abs(point_dict["Z2"])
    else:
        Rint = abs(point_dict["Z2"])
        Rext = Rbo

    # Surface of a slot pitch
    Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

    # Tooth surface
    St = self.H2 * self.W3

    alpha_bore = 2 * np.arcsin(self.W3 / (2 * Rint))
    Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

    alpha_yoke = 2 * np.arcsin(self.W3 / (2 * Rext))
    Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

    if self.is_outwards(lam=lam):
        return Sring - (St + Sarc_yoke - Sarc_bore)
    else:
        return Sring - (St + Sarc_yoke - Sarc_bore)
