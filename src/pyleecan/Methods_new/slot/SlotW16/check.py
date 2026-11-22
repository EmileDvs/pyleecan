from . import S16OutterError, S16AlphaT
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotW16 object is correct

    Parameters
    ----------
    self : SlotW16
        A SlotW16 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S16OutterError
        Slot 16 must be on internal lamination only
    """
    if self.is_outwards(lam=lam):
        raise S16OutterError("Slot 16 must be on internal lamination only")

    # Check W3 at min radius
    Rbo = self.get_Rbo(lam=lam)
    sp = 2 * np.pi / self.Zs  # slot pitch
    alphaT = 2 * np.arcsin(self.W3 * 0.5 / (Rbo - self.H0 - self.H2))

    if alphaT >= sp:
        raise S16AlphaT(
            "Tooth is larger than the slot pitch angle: reduce W3, H2 or Zs"
        )
