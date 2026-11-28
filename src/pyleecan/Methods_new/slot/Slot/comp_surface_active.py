from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, Ndisc: int = 200, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot active surface (by numerical computation).
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
        Slot active surface [m**2]

    """

    surf = self.get_surface_active(lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False))

    return surf.comp_surface(Ndisc=Ndisc)
