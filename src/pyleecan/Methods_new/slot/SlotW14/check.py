from ..Slot import SlotCheckError
from . import S14_Rbo0CheckError, S14_Rbo1CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW14 object is correct

    Parameters
    ----------
    self : SlotW14
        A SlotW14 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S14_Rbo0CheckError
        You must have W0/2 < Rbo
    S14_Rbo1CheckError
        W3 is too high comparing to the lamination bore radius (Rbo)
    """

    Rbo = self.get_Rbo(lam=lam)
    H1 = self.get_H1(lam=lam)

    if self.W0 * 0.5 / Rbo >= 1:
        raise S14_Rbo0CheckError("You must have W0/2 < Rbo")

    if self.is_outwards(lam=lam):
        R1 = Rbo + self.H0 + H1
    else:
        R1 = Rbo - self.H0 - H1

    if self.W3 * 0.5 / R1 >= 1:
        raise S14_Rbo1CheckError(
            "W3 is too high comparing to the lamination bore radius (Rbo)"
        )
