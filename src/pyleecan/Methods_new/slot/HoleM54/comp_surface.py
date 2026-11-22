import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the complete surface of the Hole

    Parameters
    ----------
    self : HoleM54
        A HoleM54 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    S: float
        Surface of the Hole [m**2]

    """

    Sint = np.pi * self.R1**2
    Sext = np.pi * (self.R1 + self.H1) ** 2
    Sarc = (Sext - Sint) * (self.W0 / (2 * np.pi))

    return Sarc + np.pi * (self.H1 / 2) ** 2
