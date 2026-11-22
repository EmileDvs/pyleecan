import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_W5(self, lam: Lamination | None = None) -> float:
    """Compute the W5 width of the slot (cf schematics)

    Parameters
    ----------
    self : HoleM50
        a HoleM50 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    W5: float
        Cf schematics [m]

    """

    alpha = self.comp_alpha(lam=lam)

    # Distance fromZ8 to Z9
    L89 = (self.W0 / 2 - self.W1 / 2) / np.cos(alpha)

    return L89 - self.W4 - self.W2
