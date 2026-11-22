import numpy as np

from ..Slot import SlotCheckError
from . import H54_R1CheckError, H54_W0CheckError, S54_NoneError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleM54 object is correct

    Parameters
    ----------
    self : HoleM54
        A HoleM54 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    H54_W0CheckError
        You must have W0 < 2*pi/Zh
    H54_R1CheckError
        You must have H0 < R1
    """

    # Check that everything is set
    if self.W0 is None:
        raise S54_NoneError("You must set W0 !")
    elif self.R1 is None:
        raise S54_NoneError("You must set R1 !")
    elif self.H0 is None:
        raise S54_NoneError("You must set H0 !")
    elif self.H1 is None:
        raise S54_NoneError("You must set H1 !")

    if 2 * np.pi / self.Zh <= self.W0:
        raise H54_W0CheckError("You must have W0 < 2*pi/Zh")

    if self.R1 <= self.H0:
        raise H54_R1CheckError("You must have H0 < R1")
