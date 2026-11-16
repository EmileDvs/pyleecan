import numpy as np

from ..Slot import SlotCheckError
from . import *


def check(self) -> None:
    """Check that the SlotW24 object is correct

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object

    Returns
    -------
    None

    Raises
    -------
    S24_W3CheckError
        The teeth are too wide, reduce Zs or W3
    S24_HWCheckError
        The teeth are too wide, reduce Zs, H2 or W3
    """
    Rbo = self.get_Rbo()

    if 2 * np.arcsin(self.W3 / (2 * Rbo)) > 2 * np.pi / self.Zs:
        raise S24_W3CheckError("The teeth are too wide, reduce Zs or W3")

    if (
        not self.is_outwards()
        and 2 * np.arcsin(self.W3 / (2 * Rbo - self.H2)) > 2 * np.pi / self.Zs
    ):
        raise S24_HWCheckError("The teeth are too wide, reduce Zs, H2 or W3")
