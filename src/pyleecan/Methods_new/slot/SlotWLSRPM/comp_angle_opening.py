import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_angle_opening(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotWLSRPM：
        A SlotWLSRPM： object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """
    Rbo = self.get_Rbo(lam=lam)
    return 2 * (np.pi / self.Zs - np.arcsin(self.W3 / 2 / Rbo))
