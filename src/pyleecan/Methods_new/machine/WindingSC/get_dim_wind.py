from ....classes_common.errors import NotImplementedYetError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_dim_wind(self, lam: Lamination | None = None):
    """Get the two first dimension of the winding matrix

    Parameters
    ----------
    self : Winding
        A Winding object
    lam : Lamination, optional
        Lamination holding the winding (default: the parent)

    Returns
    -------
    (Nrad, Ntan): tuple
        Number of layer in radial and tangential direction

    """

    return (1, 1)
