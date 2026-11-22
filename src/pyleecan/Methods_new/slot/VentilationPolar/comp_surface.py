import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the surface of all the axial ventilation ducts

    Parameters
    ----------
    self : VentilationPolar
        A VentilationPolar object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    surface: float
        Axial ventilation ducts total surface [m**2]

    """

    self.check(lam=lam)

    return np.pi * ((self.H0 + self.D0) ** 2 - self.H0**2) / (2 * np.pi / self.W1)
