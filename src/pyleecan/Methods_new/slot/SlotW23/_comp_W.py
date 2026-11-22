import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_W(self, lam: Lamination | Notch | None = None) -> None:
    """Compute W1 and W2 method (cste tooth compatibility)

    Parameters
    ----------
    self : SlotW23
        A SlotW23 object
    Zs : int
        Number of Slot
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    None

    """
    Rbo = self.get_Rbo(lam=lam)

    # To compute the slot width we use the fact that
    # alpha_tooth + alpha_slot = slot_pitch
    slot_pitch = 2 * np.pi / self.Zs

    # H0 and H1 are radial
    if self.is_outwards(lam=lam):
        R1 = Rbo + self.get_H1(lam=lam) + self.H0
    else:
        R1 = Rbo - self.get_H1(lam=lam) - self.H0

    alpha_T1 = float(np.arcsin(self.W3 / (2 * R1)))
    alpha_S1 = slot_pitch - 2 * alpha_T1
    self.W1 = 2 * np.sin(alpha_S1 / 2) * R1

    # H2 is parallel to the tooth axis
    if self.is_outwards(lam=lam):
        R2 = np.abs(R1 * np.exp(1j * alpha_T1) + self.H2)
    else:
        R2 = np.abs(R1 * np.exp(1j * alpha_T1) - self.H2)

    alpha_T2 = float(np.arcsin(self.W3 / (2 * R2)))
    alpha_S2 = slot_pitch - 2 * alpha_T2
    self.W2 = 2 * np.sin(alpha_S2 / 2) * R2
