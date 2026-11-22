from . import SLSRPMOutterError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW16 object is correct

    Parameters
    ----------
    self : SlotWLSRPM
        A SlotWLSRPM object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------

    """

    if self.is_outwards():
        raise SLSRPMOutterError("Slot Type LSRPM can’t be used on outer lamination")
