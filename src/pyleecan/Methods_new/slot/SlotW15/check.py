from . import S15InnerError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW15 object is correct

    Parameters
    ----------
    self : SlotW15
        A SlotW15 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S15InnerError
        Slot Type 15 can't be used on inner lamination
    """

    if not self.is_outwards():
        raise S15InnerError("Slot Type 15 can't be used on inner lamination")
