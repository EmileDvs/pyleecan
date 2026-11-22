import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def _comp_point_coordinate(self, lam: Lamination | None = None) -> dict:
    """Compute the point coordinates needed to plot the Hole.

    Parameters
    ----------
    self : VentilationCirc
        A VentilationCirc object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot point coordinates
    """
    Rbo = self.get_Rbo(lam=lam)

    Z1 = (self.H0 - self.D0 / 2) * np.exp(1j * self.Alpha0)
    Z2 = (self.H0 + self.D0 / 2) * np.exp(1j * self.Alpha0)
    Zc = (self.H0) * np.exp(1j * self.Alpha0)

    point_dict = dict()
    # symetry
    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["Zc"] = Zc
    return point_dict
