import numpy as np

from ..Slot import SlotCheckError
from . import S21_H1rCheckError, S21_W01CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW21 object is correct

    Parameters
    ----------
    self : SlotW21
        A SlotW21 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S21_W01CheckError
        You must have W0 <= W1
    S21_H1rCheckError
        With H1 in radian, you must have H1 < pi/2
    """
    if self.W1 < self.W0:
        raise S21_W01CheckError("You must have W0 <= W1")

    if self.H1_is_rad and self.H1 >= np.pi / 2:
        raise S21_H1rCheckError("With H1 in radian, you must have H1 < pi/2")
