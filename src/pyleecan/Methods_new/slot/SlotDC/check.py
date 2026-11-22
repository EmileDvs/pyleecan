from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotDC object is correct

    Parameters
    ----------
    self : SlotDC
        A SlotDC object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None
    """
    if self.W1 >= self.D1:
        raise SlotCheckError("Slot 17 must have W1 < D1")
    if self.W2 >= self.D1:
        raise SlotCheckError("Slot 17 must have W2 < D1")
    if self.W2 >= self.D2:
        raise SlotCheckError("Slot 17 must have W2 < D2")
    if self.H2 <= (self.D1 / 2 + self.D2 / 2):
        raise SlotCheckError("Slot 17 must have D1/2 + D2/2 < H2")
