import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the winding area

    Parameters
    ----------
    self : SlotCirc
        A SlotCirc object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Hwind: float
        Height of the winding area [m]
    """

    if self.is_H0_bore is None:
        self.is_H0_bore = True  # Set default value

    if self.is_H0_bore:
        return self.H0
    else:
        point_dict = self._comp_point_coordinate()
        ZM = point_dict["ZM"]
        Rbo = self.get_Rbo()
        return abs(Rbo - abs(ZM))
