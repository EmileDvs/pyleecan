from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the Slot total surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotM17
        A SlotM17 object
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)

    Returns
    -------
    S: float
        Slot total surface [m**2]

    """
    lam = container_or_parent(self, lam, "lam")

    return np.pi / 2 * (lam.Rext**2 - lam.Rint**2)
