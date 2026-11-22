from ....classes_common.parents import container_or_parent
from ....Functions_new.utils.geometry import comp_flower_arc
from ....Classes_new.geometry.arc_1 import Arc1
from ....classes_common.errors import ParentMissingError
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_bore_line(self, prop_dict: dict | None = None, lam: Lamination | None = None) -> list:
    """Return the bore line description

    Parameters
    ----------
    self : BoreFlower
        A BoreFlower object
    prop_dict : dict
        Property dictionary to apply on the lines
    lam : Lamination, optional
        Lamination holding the bore (default: the parent)

    Returns
    -------
    bore_list : list
        List of bore lines
    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        if self.is_yoke(lam=lam):
            R = lam.get_Ryoke()
        else:
            R = lam.get_Rbo()
    else:
        raise ParentMissingError("Error: The Bore object is not inside a Lamination")

    # Compute the shape
    (alpha_lim, zL, zR) = comp_flower_arc(2 * np.pi / self.N, self.Rarc, R)

    # Create the lines
    bore_list = list()
    for ii in range(self.N):
        rot = np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha))
        arc = Arc1(begin=zR * rot, end=zL * rot, radius=self.Rarc, prop_dict=prop_dict)
        bore_list.append(arc)
    return bore_list
