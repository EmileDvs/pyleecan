from ..Slot import SlotCheckError
from . import S29_H2CheckError, S29_W01CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW29 object is correct

    Parameters
    ----------
    self : SlotW29
        A SlotW29 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S29_W01CheckError
        You must have W0 <= W1

    S29_W12CheckError
        You must have W1 <= W2

    S29_H2CheckError
        You must have H2 > 0

    """
    if self.W1 < self.W0:
        raise S29_W01CheckError("You must have W0 <= W1")

    elif self.H2 == 0:
        raise S29_H2CheckError("You must have H2 > 0")
