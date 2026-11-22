import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : HoleM63
        A HoleM63 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]
    """
    point_dict = self._comp_point_coordinate(lam=lam)
    Rbo = self.get_Rbo(lam=lam)

    if self.top_flat:
        Rmax = np.abs(point_dict["Z2"])
        Rmin = np.abs((point_dict["Z1"] + point_dict["Z4"]) / 2)

    else:
        Rmax = Rbo - self.H1
        Rmin = np.abs((point_dict["Z1"] + point_dict["Z4"]) / 2)
    return (Rmin, Rmax)
