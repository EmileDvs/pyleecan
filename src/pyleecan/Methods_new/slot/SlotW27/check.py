from ..Slot import SlotCheckError
from . import S27_W01CheckError, S27_W03CheckError, S27_W12CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW27 object is correct

    Parameters
    ----------
    self : SlotW27
        A SlotW27 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S27_W01CheckError
        You must have W0 <= W1
    S27_W12CheckError
        You must have W1 <= W2
    S27_W03CheckError
        You must have W0 <= W3

    """
    if self.W1 < self.W0:
        raise S27_W01CheckError("You must have W0 <= W1")

    if self.W2 < self.W1:
        raise S27_W12CheckError("You must have W1 <= W2")

    if self.W3 < self.W0:
        raise S27_W03CheckError("You must have W0 <= W3")
