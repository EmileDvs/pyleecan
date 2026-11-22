import numpy as np

from ....Classes_new.geometry.arc_3 import Arc3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : HoleM60
        A HoleM60 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]
    """
    point_dict = self._comp_point_coordinate(lam=lam)

    point_list = list()
    # Discretize arcs to get the higher point and the lower point
    curve = Arc3(begin=point_dict["Z2"], end=point_dict["Z4"], is_trigo_direction=True)
    point_list.extend(curve.discretize())
    curve = Arc3(begin=point_dict["Z5"], end=point_dict["Z1"], is_trigo_direction=True)
    point_list.extend(curve.discretize())

    abs_list = [np.abs(point) for point in point_list]
    Rmax = max(abs_list)
    Rmin = min(abs_list)

    return (Rmin, Rmax)
