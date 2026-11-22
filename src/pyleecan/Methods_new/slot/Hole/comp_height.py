from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_height(self, lam: Lamination | None = None) -> float:
    """Compute the height of the Hole (Rmax-Rmin)

    Parameters
    ----------
    self : Hole
        A Hole object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    H : float
        Height of the hole

    """

    (Rmin, Rmax) = self.comp_radius(lam=lam)
    return Rmax - Rmin
