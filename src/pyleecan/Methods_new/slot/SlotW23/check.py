import numpy as np

from ..Slot import SlotCheckError
from . import S23_H1rCheckError, S23_W01CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW23 object is correct

    Parameters
    ----------
    self : SlotW23
        A SlotW23 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S23_W01CheckError
        You must have W0 <= W1
    S23_H1rCheckError
        With H1 in radian, you must have H1 < pi/2

    """

    if self.H1_is_rad and self.H1 >= np.pi / 2:
        raise S23_H1rCheckError("With H1 in radian, you must have H1 < pi/2")

    if self.W1 is not None and self.W1 < self.W0:
        raise S23_W01CheckError("You must have W0 <= W1")
