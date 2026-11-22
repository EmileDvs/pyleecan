from ..Slot import SlotCheckError
from . import S60_InnerCheckError, S60_RCheckError, S60_W21CheckError, S60_WindHError, S60_WindWError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW60 object is correct

    Parameters
    ----------
    self : SlotW60
        A SlotW60 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S60_InnerCheckError
       Slot 60 is for inner lamination only
    S60_W21CheckError
        You must have W2 < W1
    S60_RCheckError
        You must have R1 <= Rbo
    S60_WindHError
        You must have W3+W4 < H2
    S60_WindWError
        You must have W3 < (W1-W2)/2

    """

    if self.is_outwards(lam=lam):
        raise S60_InnerCheckError("Slot 60 is for inner lamination only")

    if self.W1 <= self.W2:
        raise S60_W21CheckError("You must have W2 < W1")

    if self.R1 > self.get_Rbo(lam=lam):
        raise S60_RCheckError("You must have R1 <= Rbo")

    if self.H3 + self.H4 >= self.H2:
        raise S60_WindHError("You must have W3+W4 < H2")

    if self.W3 >= (self.W1 - self.W2) / 2:
        raise S60_WindWError("You must have W3 < (W1-W2)/2")
