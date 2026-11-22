from ..Slot import SlotCheckError
from . import S63_NoneError
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleM63 object is correct

    Parameters
    ----------
    self : HoleM63
        A HoleM63 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    _______
    S63_WCheckError
    """

    # Check that everything is set
    if self.W0 is None:
        raise S63_NoneError("You must set W0 !")
    elif self.H0 is None:
        raise S63_NoneError("You must set H0 !")
    elif self.H1 is None:
        raise S63_NoneError("You must set H1 !")
