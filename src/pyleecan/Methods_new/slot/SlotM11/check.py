import numpy as np

from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotM11 object is correct

    Parameters
    ----------
    self : SlotM11
        A SlotM11 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None
    """
    # percentage of the slot pitch that W0 and W1 should not exceed
    slot_pitch_tol = 0.99

    if self.W1 is not None and self.W0 < self.W1:
        raise SlotCheckError("You must have W1 <= W0")
    if self.W1 is not None and self.W1 >= slot_pitch_tol * 2 * np.pi / self.Zs:
        raise SlotCheckError("You must have W1 < pi/p (use ring magnet instead)")
    if self.W0 >= slot_pitch_tol * 2 * np.pi / self.Zs:
        raise SlotCheckError("You must have W0 < pi/p")
