import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the surface of the Hole

    Parameters
    ----------
    self : HoleM63
        A HoleM63 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    S: float
        Surface of the Hole. [m**2]

    """
    if self.top_flat:
        return self.H0 * self.W0

    else:
        Rbo = self.get_Rbo(lam=lam)
        alpha = 2 * np.arcsin((self.W0 / 2) / (Rbo - self.H1))

        return self.H0 * self.W0 + (((Rbo - self.H1) ** 2) * (alpha - np.sin(alpha)) / 2)
