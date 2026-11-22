import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : HoleM50
        A HoleM50 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]
    """

    Rmax = self.get_Rext(lam=lam) - self.H1

    point_dict = self._comp_point_coordinate(lam=lam)
    Rmin = min(abs(point_dict["Z5"]), abs(point_dict["Z7"]))

    return (Rmin, Rmax)
