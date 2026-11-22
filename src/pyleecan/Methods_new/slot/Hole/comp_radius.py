import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the hole

    Parameters
    ----------
    self : Hole
        A Hole object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the hole

    """

    surf_list = self.build_geometry(lam=lam)
    point_list = list()
    for surf in surf_list:
        for curve in surf.get_lines():
            point_list.extend(curve.discretize())

    abs_list = [np.abs(point) for point in point_list]
    Rmax = max(abs_list)
    Rmin = min(abs_list)
    return (Rmin, Rmax)
