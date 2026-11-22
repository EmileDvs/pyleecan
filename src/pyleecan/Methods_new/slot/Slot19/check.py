from ..Slot import SlotCheckError
from . import S19_W1CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the Slot19 object is correct

    Parameters
    ----------
    self : Slot19
        A Slot19 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S19_H2CheckError
        H1 must be > 0

    S19_W1CheckError
        W1 must be > 0
    """
    if self.W1 < 0:
        raise S19_W1CheckError("W1 must be larger than zero")
