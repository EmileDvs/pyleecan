from ..Slot import SlotCheckError
from . import *


def check(self) -> None:
    """Check that the SlotM16 object is correct

    Parameters
    ----------
    self : SlotM16
        A SlotM16 object

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
