import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_wedge(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot wedge surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW29
        A SlotW29 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot wedge surface [m**2]

    """
    # Selection type Wedge
    if self.wedge_type == 0:
        return self.comp_surface_opening(lam=lam)

    if self.wedge_type == 1:
        return (self.W1) * self.H1

    raise NotImplementedError(f"SlotW29.wedge_type must be 0 or 1, got {self.wedge_type!r}")
