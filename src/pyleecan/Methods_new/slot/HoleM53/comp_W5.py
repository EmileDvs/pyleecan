import numpy as np

from ....Functions_new.utils.geometry import inter_line_circle
from . import Slot53InterError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_W5(self, lam: Lamination | None = None) -> float:
    """Compute the W5 width of the hole (cf schematics)

    Parameters
    ----------
    self : HoleM53
        a HoleM53 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    W5: float
        Cf schematics [m]
    Raises
    --------
    Slot53InterError
        ERROR: Slot 53, Can't find Z11 coordinates

    """

    Rext = self.get_Rext(lam=lam)

    Z7 = Rext - self.H0 - 1j * self.W1 / 2
    Z8 = Z7 + (self.H2 - self.H3) * np.sin(self.W4)
    Z10 = (self.W2 + self.W3) * np.exp(-1j * self.W4) + Z8

    # Z1 and Z11 are defined as intersection between line and circle
    Zlist = inter_line_circle(Z8, Z10, Rext - self.H1)
    if len(Zlist) == 2 and Zlist[0].imag < 0 and Zlist[0].real > 0:
        Z11 = Zlist[0]
    elif len(Zlist) == 2 and Zlist[1].imag < 0 and Zlist[1].real > 0:
        Z11 = Zlist[1]
    else:
        raise Slot53InterError("ERROR: Slot 53, Can't find Z11 coordinates")

    return abs(Z11 - Z8) - self.W2 - self.W3
