import numpy as np


def comp_surface(self) -> float:
    """Compute the Slot total surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotM14
        A SlotM14 object

    Returns
    -------
    S: float
        Slot total surface [m**2]

    """

    point_dict = self._comp_point_coordinate()
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]

    R1 = abs(Z1)
    R2 = abs(Z2)

    S1 = np.pi * R1**2 * (self.W0 / (2 * np.pi))
    S2 = np.pi * R2**2 * (self.W0 / (2 * np.pi))

    return abs(S1 - S2)
