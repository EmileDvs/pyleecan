from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot total surface (by analytical computation for comp_surface_opening and numerical computation for comp_surface_active).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW11_2
        A SlotW11_2 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot total surface [m**2]

    """
    return self.comp_surface_active(lam=lam) + self.comp_surface_opening(lam=lam)
