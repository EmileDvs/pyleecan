from ..Slot import SlotCheckError
from . import S58_NoneError, S58_WCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleM58 object is correct

    Parameters
    ----------
    self : HoleM58
        A HoleM58 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    _______
    S58_WCheckError
        You must have W1+W2 <= W0
    """
    # Check that everything is set
    if self.W0 is None:
        raise S58_NoneError("You must set W0 !")
    elif self.W1 is None:
        raise S58_NoneError("You must set W1 !")
    elif self.W2 is None:
        raise S58_NoneError("You must set W2 !")
    elif self.W3 is None:
        raise S58_NoneError("You must set W3 !")
    elif self.R0 is None:
        raise S58_NoneError("You must set R0 !")
    elif self.H0 is None:
        raise S58_NoneError("You must set H0 !")
    elif self.H1 is None:
        raise S58_NoneError("You must set H1 !")
    elif self.H2 is None:
        raise S58_NoneError("You must set H2 !")

    Rext = self.get_Rext(lam=lam)

    if self.W0 < self.W1 + self.W2:
        raise S58_WCheckError("You must have W1+W2 <= W0")
