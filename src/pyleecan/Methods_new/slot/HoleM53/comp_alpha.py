import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_alpha(self, lam: Lamination | None = None) -> float:
    """Compute the magnets angle of the slot type 53

    Parameters
    ----------
    self : HoleM53
        a HoleM53 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    alpha: float
        magnet angle [rad]
    """
    return np.pi / 2 - self.W4
