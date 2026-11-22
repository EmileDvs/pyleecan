import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_H1(self, lam: Lamination | Notch | None = None) -> float:
    """Return H1 in [m]

    Parameters
    ----------
    self : SlotW10
        A SlotW10 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    H1: float
        H1 in [m]

    """

    if self.H1_is_rad:  # H1 in rad
        return ((self.W1 - self.W0) / 2.0) * np.tan(self.H1)  # convertion to m
    else:  # H1 in m
        return self.H1
