import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : HoleM61
        A HoleM61 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]
    """

    Rbo = self.get_Rbo(lam=lam)

    Rmax = Rbo - self.H2
    Rmin = np.abs((Rbo - self.H0) + 1j * self.W0 / 2)

    return (Rmin, Rmax)
