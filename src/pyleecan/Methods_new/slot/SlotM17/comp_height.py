from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_height(self, lam: Lamination | None = None) -> float:
    """Compute the height of the Slot.
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotM17
        A SlotM17 object
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """
    lam = container_or_parent(self, lam, "lam")

    return lam.Rext - lam.Rint
