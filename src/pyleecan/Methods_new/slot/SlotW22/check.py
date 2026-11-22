import numpy as np

from ..Slot import SlotCheckError
from . import S22_A02CheckError, S22_SpCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW22 object is correct

    Parameters
    ----------
    self : SlotW22
        A SlotW22 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S22_A02CheckError
        You must have W0 <= W2
    S22_SpCheckError
        You must have W2 < 2*pi/Zs
    """
    if self.W2 < self.W0:
        raise S22_A02CheckError("You must have W0 <= W2")

    if 2 * np.pi / self.Zs <= self.W2:
        raise S22_SpCheckError("You must have W2 < 2*pi/Zs")
