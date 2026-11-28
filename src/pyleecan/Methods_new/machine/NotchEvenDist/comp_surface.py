from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the surface of ALL THE NOTCHES

    Parameters
    ----------
    self : NotchEvenDist
        A NotchEvenDist object
    lam : Lamination, optional
        Lamination holding the notch (default: the parent)

    Returns
    -------
    Snotch : float
        surface of ALL THE NOTCHES
    """

    # The notch shape gets the lamination of the notch as its container: the
    # Notch methods it would call (get_Rbo, is_outwards, get_label...) only
    # forward to that lamination
    lam = container_or_parent(self, lam, "lam")
    return self.notch_shape.Zs * self.notch_shape.comp_surface(lam=lam)
