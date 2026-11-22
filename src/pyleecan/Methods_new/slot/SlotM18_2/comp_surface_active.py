import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner active surface (by analytical computation)

    Parameters
    ----------
    self : SlotM18_2
        A SlotM18_2 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner active surface [m**2]

    """

    point_dict = self._comp_point_coordinate()
    ZM1 = point_dict["ZM1"]
    ZM3 = point_dict["ZM3"]

    R1 = abs(ZM1)
    R2 = abs(ZM3)

    S1 = np.pi * R1**2 / self.Zs
    S2 = np.pi * R2**2 / self.Zs

    return abs(S1 - S2)
