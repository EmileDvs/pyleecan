import numpy as np

from ..Slot import SlotCheckError
from . import *


def check(self) -> None:
    """Check that the SlotW22 object is correct

    Parameters
    ----------
    self : SlotW22
        A SlotW22 object

    Returns
    -------
    None

    Raises
    -------
    S22_A02CheckError
        You must have W0 <= W2
    S22_SpCheckError
        You must have W2 < 2*pi/Zs
    """
    if self.W2 < self.W0:
        raise S22_A02CheckError("You must have W0 <= W2")

    if 2 * np.pi / self.Zs <= self.W2:
        raise S22_SpCheckError("You must have W2 < 2*pi/Zs")
