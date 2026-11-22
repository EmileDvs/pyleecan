from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_wedges(self, Ndisc: int = 200, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot wedges surface (by numerical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : Slot
        A Slot object
    Ndisc : int
        Number of point to discretize the lines
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot wedges surface [m**2]

    """

    surf_list = self.get_surface_wedges(lam=lam)

    S = 0
    for surf in surf_list:
        S += surf.comp_surface(Ndisc=Ndisc)
    return S
