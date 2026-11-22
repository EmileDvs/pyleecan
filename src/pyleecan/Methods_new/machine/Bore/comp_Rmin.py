import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_Rmin(self, lam: Lamination | None = None) -> float:
    """Compute the minimum radius of the Bore shape

    Parameters
    ----------
    self : Bore
        A Bore object
    lam : Lamination, optional
        Lamination holding the bore (default: the parent)

    Returns
    -------
    Rmin : float
        Minimum radius of the Bore shape
    """

    line_list = self.get_bore_line(lam=lam)
    point_list = list()

    for line in line_list:
        point_list.extend(line.discretize(100))

    return np.min(np.abs(np.array(point_list)))
