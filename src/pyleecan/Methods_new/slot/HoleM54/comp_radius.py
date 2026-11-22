import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the hole

    Parameters
    ----------
    self : HoleM54
        A HoleM54 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the hole [m]

    """

    Rext = self.get_Rext(lam=lam)

    surf_list = self.build_geometry(lam=lam)
    point_list = list()
    for curve in surf_list[0].line_list:
        point_list.extend(curve.discretize())

    Rmax = max([np.abs(point) for point in point_list])
    Rmin = Rext - self.H0 - self.H1
    return (Rmin, Rmax)
