from ..Slot import SlotCheckError
from . import S60_NoneError, S60_WCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleM60 object is correct

    Parameters
    ----------
    self : HoleM60
        A HoleM60 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    _______
    S60_WCheckError
        You must have W1+H0 <= W2
    """
    # Check that everything is set
    if self.W0 is None:
        raise S60_NoneError("You must set W0 !")
    elif self.W1 is None:
        raise S60_NoneError("You must set W1 !")
    elif self.W2 is None:
        raise S60_NoneError("You must set W2 !")
    elif self.W3 is None:
        raise S60_NoneError("You must set W3 !")
    elif self.H0 is None:
        raise S60_NoneError("You must set H0 !")
    elif self.H1 is None:
        raise S60_NoneError("You must set H1 !")

    if (self.W1 + self.H0) > self.W2:
        raise S60_WCheckError("You must have (W1 + H0) <= W2")
