from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_width(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the average width of the Slot by dividing its surface by its height

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    W2: float
        Average width of the slot [m]
    """

    S = self.comp_surface(lam=lam)

    H = self.comp_height(lam=lam)

    return S / H
