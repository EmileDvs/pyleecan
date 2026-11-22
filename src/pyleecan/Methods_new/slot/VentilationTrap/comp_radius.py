import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the two circle that contains all the ventilation
    ducts

    Parameters
    ----------
    self : VentilationTrap
        A VentilationTrap object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin, Rmax): tuple
        Tuple of circle radius [m]

    """

    self.check(lam=lam)

    Rmin = np.sqrt(self.W1**2 + self.H0**2)
    Rmax = np.sqrt(self.W2**2 + (self.H0 + self.D0) ** 2)

    return (Rmin, Rmax)
