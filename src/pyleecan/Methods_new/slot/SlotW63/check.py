from . import S63_H0CheckError, S63_InnerCheckError, S63_W0CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW63 object is correct

    Parameters
    ----------
    self : SlotW63
        A SlotW63 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None
    Raises
    -------
    S63_InnerCheckError
        Slot 63 is for inner lamination only

    """
    if self.is_outwards():
        raise S63_InnerCheckError("Slot 63 is for inner lamination only")

    if self.W0 >= self.W1:
        raise S63_W0CheckError("You must have W1 > W0")

    if self.H0 == 0:
        raise S63_H0CheckError("You must have H0 > 0")

    if self.W0 == 0:
        raise S63_W0CheckError("You must have W0 > 0")
