import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotCirc
        A SlotCirc object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]
    """

    R0 = self._comp_R0()
    alpha = float(2 * np.arcsin(self.W0 / (2 * R0)))
    # Area of the full circle
    S1 = np.pi * (R0**2)
    # Area of the top Arc
    S2 = (R0**2.0) / 2.0 * (alpha - np.sin(alpha))
    # Arc of the bore
    alpha_op = self.comp_angle_opening()
    S3 = (self.get_Rbo() ** 2.0) / 2.0 * (alpha_op - np.sin(alpha_op))

    if self.H0 < self.W0 / 2:
        # Center is in airgap
        if self.is_outwards():
            return S2 - S3
        else:
            return S2 + S3
    else:  # Center is in the Lamination
        if self.is_outwards():
            return S1 - S2 - S3
        else:
            return S1 - S2 + S3
