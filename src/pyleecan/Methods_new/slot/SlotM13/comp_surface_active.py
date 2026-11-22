import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot active inner surface (by analytical computation)

    Parameters
    ----------
    self : SlotM13
        A SlotM13 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot active inner surface [m**2]

    """

    point_dict = self._comp_point_coordinate()
    ZM1 = point_dict["ZM1"]
    ZM2 = point_dict["ZM2"]
    alpha = 2 * float(np.arcsin(self.W1 / (2 * self.Rtopm)))
    Sarc = (self.Rtopm**2.0) / 2.0 * (alpha - np.sin(alpha))

    S1 = abs(ZM1 - ZM2) * self.W1
    return S1 + Sarc
