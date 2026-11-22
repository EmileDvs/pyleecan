import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_angle_opening(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotM14
        A SlotM14 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """

    return self.W0
