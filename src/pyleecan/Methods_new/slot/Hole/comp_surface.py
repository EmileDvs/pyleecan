from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the Hole total surface (by numerical computation).

    Parameters
    ----------
    self : Hole
        A Hole object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    S : float
        Slot total surface [m**2]

    """

    surf_list = self.build_geometry(lam=lam)
    S = 0
    for surf in surf_list:
        S += surf.comp_surface()

    return S
