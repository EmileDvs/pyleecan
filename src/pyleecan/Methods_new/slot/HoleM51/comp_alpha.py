import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_alpha(self, lam: Lamination | None = None) -> float:
    """Compute the angle of the Hole (cf schematics)

    Parameters
    ----------
    self : HoleM51
        A HoleM51 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    alpha: float
        Angle of the Hole (cf schematics) [rad]

    """
    Rext = self.get_Rext(lam=lam)

    alpha = -np.arctan(
        2
        * (self.H0 - self.H1 * np.cos(0.5 * self.W1) + Rext * np.cos(0.5 * self.W1) - Rext)
        / (2.0 * self.H1 * np.sin(0.5 * self.W1) - 2 * Rext * np.sin(0.5 * self.W1) + self.W0)
    )

    return alpha
