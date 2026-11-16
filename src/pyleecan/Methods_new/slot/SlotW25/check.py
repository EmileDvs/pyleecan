import numpy as np

from ..Slot import SlotCheckError
from . import *


def check(self) -> None:
    """Check that the SlotW25 object is correct

    Parameters
    ----------
    self : SlotW25
        A SlotW25 object

    Returns
    -------
    None

    Raises
    -------
    S25_W4CheckError
        The teeth are too wide, reduce Zs or W4
    S25_HWCheckError
        The teeth are too wide, reduce Zs, H2 or W3

    """
    Rbo = self.get_Rbo()

    if self.H1 == 0:
        raise S25_W4CheckError("You must have H1>0 (use Slot 24 for H1=0)")
    if self.H2 == 0:
        raise S25_W4CheckError("You must have H2>0 (use Slot 24 for H2=0)")
    if self.W4 == self.W3:
        raise S25_W4CheckError("You must have W4 != W3 (use Slot 24 for W4=W3)")

    if 2 * np.arcsin(self.W4 / (2 * Rbo)) > 2 * np.pi / self.Zs:
        raise S25_W4CheckError("The teeth are too wide, reduce Zs or W4")

    if (
        not self.is_outwards()
        and 2 * np.arcsin(self.W3 / (2 * Rbo - self.H2 - self.H1)) > 2 * np.pi / self.Zs
    ):
        raise S25_HWCheckError("The teeth are too wide, reduce Zs, H2 or W3")
