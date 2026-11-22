from ..Slot import SlotCheckError
from . import S16_W01CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotM16 object is correct

    Parameters
    ----------
    self : SlotM16
        A SlotM16 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S29_W01CheckError
        You must have W0 < W1

    """
    if self.W1 <= self.W0:
        raise S16_W01CheckError("You must have W0 < W1")
