import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the Hole total surface (by analytical computation).

    Parameters
    ----------
    self : HoleM60
        A HoleM60 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    S: float
        Hole total surface [m**2]

    """
    # Two discus of radius H0 / 2
    S1 = 2 * (np.pi * (self.H0 / 2) ** 2)
    # Two rectangles of dimensions (W2 - H0) x H0
    S2 = 2 * ((self.W2 - self.H0) * self.H0)

    return S1 + S2
