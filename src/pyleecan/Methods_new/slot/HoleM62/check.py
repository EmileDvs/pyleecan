from ..Slot import SlotCheckError
from . import S62_NoneError
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleM62 object is correct

    Parameters
    ----------
    self : HoleM62
        A HoleM62 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    _______
    S62_WCheckError
    """

    # Check that everything is set
    if self.W0 is None:
        raise S62_NoneError("You must set W0 !")
    elif self.H0 is None:
        raise S62_NoneError("You must set H0 !")
    elif self.H1 is None:
        raise S62_NoneError("You must set H1 !")
