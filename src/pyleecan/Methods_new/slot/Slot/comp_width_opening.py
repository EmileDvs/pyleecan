from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_width_opening(self, is_curved: bool = False, lam: Lamination | None = None) -> float:
    """Compute the average opening width of the Slot

    Parameters
    ----------
    self : Slot
        A Slot object
    is_curved : bool
        width opening curved or straight
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)

    Returns
    -------
    W0: float
        Average opening width of the slot [m] or [rad]
    """
    lam = container_or_parent(self, lam, "lam")

    if is_curved:
        R = self.get_Rbo(lam=lam)
        alpha = self.comp_angle_opening()
        Zs = lam.get_Zs()
        return 2 * np.pi * R / Zs - alpha * R
    else:
        line_list = self.build_geometry(lam=lam)
        Z1 = line_list[0].get_begin()
        Z2 = line_list[-1].get_end()
        return abs(Z2 - Z1)
