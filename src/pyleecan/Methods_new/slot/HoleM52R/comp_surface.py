import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the surface of the Hole

    Parameters
    ----------
    self : HoleM52R
        A HoleM52R object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    S: float
        Surface of the Hole. [m**2]

    """

    Smag = self.comp_surface_magnets(lam=lam)
    # one side rectangular air area
    Srect = self.W1 * (self.H1 - self.H2) - (4 - np.pi) * self.R0**2 / 4

    return Smag + 2 * Srect
