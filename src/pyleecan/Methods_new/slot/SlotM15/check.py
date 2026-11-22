import numpy as np

from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotM13 object is correct

    Parameters
    ----------
    self : SlotM15
        A SlotM15 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None
    """
    Rbo = self.get_Rbo()

    # conversion W0 rad -> m
    W0_m = 2 * (Rbo - self.H0) * np.sin(self.W0 / 2)

    if W0_m < self.W1:
        raise SlotCheckError("You must have W1 <= W0")
    if 2 * self.Rtopm < self.W1:
        raise SlotCheckError("You must have W1 <= 2*Rtopm")
