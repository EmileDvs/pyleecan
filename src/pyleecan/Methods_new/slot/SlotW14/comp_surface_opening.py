import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_opening(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot opening surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW14
        A SlotW14 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    S: float
        Slot opening surface [m**2]

    """
    H1 = self.get_H1(lam=lam)
    Rbo = self.get_Rbo(lam=lam)
    point_dict = self._comp_point_coordinate(lam=lam)
    Z7 = point_dict["Z7"]
    W1 = abs(Z7.imag) * 2

    S1 = (W1 + self.W0) * H1 / 2
    S0 = self.W0 * self.H0

    # The bottom is an arc
    alpha = self.comp_angle_opening(lam=lam)
    Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

    # Selection type Wedge
    if self.wedge_type == 0:
        if self.is_outwards(lam=lam):
            return S1 + S0 - Sarc
        else:
            return S1 + S0 + Sarc

    if self.wedge_type == 1:
        if self.is_outwards(lam=lam):
            return S0 - Sarc
        else:
            return S0 + Sarc

    raise NotImplementedError(f"SlotW14.wedge_type must be 0 or 1, got {self.wedge_type!r}")
