import numpy as np


def comp_angle_opening(self) -> float:
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotM12
        A SlotM12 object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """

    Rbo = self.get_Rbo()

    return float(2 * np.arcsin(self.W0 / (2 * Rbo)))
