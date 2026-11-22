import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the hole

    Parameters
    ----------
    self : HoleM52
        A HoleM52 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the hole [m]

    """

    Rext = self.get_Rext(lam=lam)

    Rmax = Rext - self.H0

    alpha = self.comp_alpha(lam=lam)
    Z1 = (Rext - self.H0) * np.exp(1j * alpha / 2)
    Z5 = Z1.real - self.H1
    Rmin = abs(Z5)

    return (Rmin, Rmax)
