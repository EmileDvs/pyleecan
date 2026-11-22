from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_radius_mid_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the radius at the middle of the active part of the slot

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Rmw: float
        Mid active radius [m]

    """

    Rbo = self.get_Rbo(lam=lam)
    Hslot = self.comp_height(lam=lam)
    Hwind = self.comp_height_active(lam=lam)
    if self.is_outwards(lam=lam):
        return Rbo + Hslot - Hwind / 2
    else:
        return Rbo - Hslot + Hwind / 2
