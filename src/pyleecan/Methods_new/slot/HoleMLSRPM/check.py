from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleMLSRPM object is correct

    Parameters
    ----------
    self : HoleMLSRPM
        A HoleMLSRPM object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    -------

    """

    # Check that everything is set
    if self.W0 is None:
        raise SLSRPM_NoneError("You must set W0 !")
    elif self.W1 is None:
        raise SLSRPM_NoneError("You must set W1 !")
    elif self.W2 is None:
        raise SLSRPM_NoneError("You must set W2 !")
    elif self.H1 is None:
        raise SLSRPM_NoneError("You must set H1 !")
    elif self.R1 is None:
        raise SLSRPM_NoneError("You must set R1 !")
    elif self.R2 is None:
        raise SLSRPM_NoneError("You must set R2 !")
    elif self.R3 is None:
        raise SLSRPM_NoneError("You must set R3 !")
    elif self.magnet_0 is None:
        raise SLSRPM_NoneError("You must set magnet_0 !")


class SLSRPM_NoneError(SlotCheckError):
    """Raised when a propery of HoleM52 is None"""

    pass


class SLSRPM_H12CheckError(SlotCheckError):
    """ """

    pass


class SLSRPM_alphaCheckError(SlotCheckError):
    """ """

    pass


class SLSRPM_W1CheckError(SlotCheckError):
    """ """

    pass
