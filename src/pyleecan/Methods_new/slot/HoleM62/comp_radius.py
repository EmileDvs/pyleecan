import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : HoleM62
        A HoleM62 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]
    """

    Rbo = self.get_Rbo(lam=lam)

    Rmax = Rbo - self.H1

    if not self.W0_is_rad:
        point_dict = self._comp_point_coordinate(lam=lam)
        Rmin = np.abs(point_dict["Z1"])
    else:
        Rmin = Rbo - self.H1 - self.H0

    return (Rmin, Rmax)
