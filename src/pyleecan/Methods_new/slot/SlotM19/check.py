import numpy as np

from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None):
    """
    Check that the SlotM19 object is correct

    Parameters
    ----------
    self : SlotM19
        A SlotM19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------

    """
    pass
