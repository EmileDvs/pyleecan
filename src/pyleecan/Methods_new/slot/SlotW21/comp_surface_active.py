from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotW21
        A SlotW21 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """

    S3 = 0.5 * (self.W1 + self.W2) * self.H2

    return S3
