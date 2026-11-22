import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_alpha(self, lam: Lamination | None = None) -> float:
    """The opening angle incl. W1 width and a Rext - H0 radius

    Parameters
    ----------
    self : HoleM52
        A HoleM52 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    alpha: float
        Angle between P1 and P9 (cf schematics) [rad]

    """
    Rext = self.get_Rext(lam=lam)

    alpha = 2 * np.arcsin((2 * self.W1 + self.W0) / (2 * (Rext - self.H0)))

    return alpha
