import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_width(self, lam: Lamination | None = None) -> float:
    """Compute the width of the Hole (cf schematics)

    Parameters
    ----------
    self : HoleM51
        A HoleM51 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    Whole: float
        Width of the Hole (cf schematics) [m]

    """

    Rext = self.get_Rext(lam=lam)
    return 2 * np.sin(self.W1 / 2) * (Rext - self.H1)
