from ..Slot import SlotCheckError
from . import S26_WCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW26 object is correct

    Parameters
    ----------
    self : SlotW26
        A SlotW26 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S26_WCheckError
        You must have W0 < 2*R1
    """
    if self.R1 * 2 <= self.W0:
        raise S26_WCheckError("You must have W0 < 2*R1")
