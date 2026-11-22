from ..Slot import SlotCheckError
from . import S12_R20CheckError, S12_RboCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW12 object is correct

    Parameters
    ----------
    self : SlotW12
        A SlotW12 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S12_R20CheckError
        You must have R2 > 0
    S12_RboCheckError
        You must have R2 < Rbo
    """

    Rbo = self.get_Rbo()

    if self.R2 <= 0:
        raise S12_R20CheckError("You must have R2 > 0")

    if self.R2 / Rbo >= 1:
        raise S12_RboCheckError("You must have R2 < Rbo")
