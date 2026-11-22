import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : HoleM57
        A HoleM57 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]
    """
    Rext = self.get_Rext(lam=lam)

    Rmax = Rext - self.H1
    Rmin = abs(self._comp_point_coordinate(lam=lam)["Z5"])

    return (Rmin, Rmax)
