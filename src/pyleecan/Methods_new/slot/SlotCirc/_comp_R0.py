import numpy as np
from ....Functions_new.utils.geometry import circle_from_3_points
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_R0(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the radius of the circle

    Parameters
    ----------
    self : SlotCirc
        A SlotCirc object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    R0 : float
        Radius of the circle [m]
    """

    if self.is_H0_bore is None:
        self.is_H0_bore = True  # Set default value

    if self.is_H0_bore:
        return self._comp_point_coordinate(lam=lam)["R0"]
    else:
        # R0 is the radius of the circle
        # Pythagore in Triangle: Center, Z2, middle(Z1,Z2)
        # R0**2 = (W0/2)**2 + (H0-R0)**2

        return ((self.W0 / 2) ** 2 + self.H0**2) / (2 * self.H0)
