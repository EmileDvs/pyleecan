import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the active area

    Parameters
    ----------
    self : SlotM12
        A SlotM12 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Hwind: float
        Height of the active area [m]

    """

    point_dict = self._comp_point_coordinate(lam=lam)
    ZM0 = point_dict["ZM0"]
    ZM1 = point_dict["ZM1"]
    ZM2 = point_dict["ZM2"]
    ZM3 = point_dict["ZM3"]
    ZM4 = point_dict["ZM4"]

    if self.is_outwards(lam=lam):
        R1 = np.abs(ZM0)
        R2 = np.abs(ZM1)
    else:
        R1 = np.abs((ZM1 + ZM4) / 2)
        R2 = np.abs(ZM0)
    return R2 - R1
