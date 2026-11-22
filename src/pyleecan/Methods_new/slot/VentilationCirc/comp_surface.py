import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None):
    """Compute the surface of all the axial ventilation ducts

    Parameters
    ----------
    self : VentilationCirc
        A VentilationCirc object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    Svent:
        Axial ventilation ducts total surface [m**2]

    """

    self.check(lam=lam)

    return np.pi * ((self.D0 / 2.0) ** 2)
