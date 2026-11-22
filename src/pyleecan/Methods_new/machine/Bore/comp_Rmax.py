import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_Rmax(self, lam: Lamination | None = None) -> float:
    """Compute the maximum radius of the Bore shape

    Parameters
    ----------
    self : Bore
        A Bore object
    lam : Lamination, optional
        Lamination holding the bore (default: the parent)

    Returns
    -------
    Rmax : float
        Maximum radius of the Bore shape [m]
    """

    line_list = self.get_bore_line(lam=lam)
    point_list = list()

    for line in line_list:
        point_list.extend(line.discretize(100))

    return np.max(np.abs(np.array(point_list)))
