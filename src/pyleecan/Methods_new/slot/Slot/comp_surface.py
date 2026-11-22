from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface(self, Ndisc: int = 200, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot total surface (by numerical computation).
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
        Slot total surface [m**2]
    """

    surf = self.get_surface(lam=lam)
    return surf.comp_surface(Ndisc=Ndisc)
