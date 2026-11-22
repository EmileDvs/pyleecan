import numpy as np

from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotM12 object is correct

    Parameters
    ----------
    self : SlotM12
        A SlotM12 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None
    """
    if self.W0 < self.W1:
        raise SlotCheckError("You must have W1 <= W0")
