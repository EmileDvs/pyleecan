import numpy as np


def comp_surface_opening(self) -> float:
    """Compute the Slot opening surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW16
        A SlotW16 object

    Returns
    -------
    S: float
        Slot total surface [m**2]

    """
    Rbo = self.get_Rbo()

    S0 = (np.pi * Rbo**2 - np.pi * (Rbo - self.H0) ** 2) * self.W0 / (2 * np.pi)

    return S0
