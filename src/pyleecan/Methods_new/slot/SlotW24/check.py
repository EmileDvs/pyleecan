import numpy as np

from ..Slot import SlotCheckError
from . import S24_HWCheckError, S24_W3CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW24 object is correct

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

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
