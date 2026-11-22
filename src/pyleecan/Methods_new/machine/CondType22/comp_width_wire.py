from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_width_wire(self, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Return bar width

    Parameters
    ----------
    self : CondType22
        A CondType22 object
    winding : Winding, optional
        Winding holding the object (default: the parent)
    lam : Lamination, optional
        Lamination of the winding (default: the parent of the winding)

    Returns
    -------
    W: float
        Width of the bar [m]

    """
    winding = container_or_parent(self, winding, "winding")
    lam = container_or_parent(self, lam, "lam", depth=2)

    if winding is not None and lam is not None:
        Wbar = lam.slot.comp_width()

    else:
        Wbar = np.sqrt(self.Sbar)

    return Wbar
