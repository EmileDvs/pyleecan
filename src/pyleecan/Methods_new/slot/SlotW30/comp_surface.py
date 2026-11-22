from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot total surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW30
        A SlotW30 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot total surface [m**2]

    """
    # comp_surface_active is an numerical computation (defined in Slot class)
    # comp_surface_opening is an analytical computation
    return self.comp_surface_active(lam=lam) + self.comp_surface_opening(lam=lam)
