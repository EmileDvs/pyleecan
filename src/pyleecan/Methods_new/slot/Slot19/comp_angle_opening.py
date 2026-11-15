import numpy as np


def comp_angle_opening(self) -> float:
    """Compute the slot opening angle of the Slot

    Parameters
    ----------
    self : Slot19
        A Slot19 object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """

    Rbo = self.get_Rbo()

    if self.Wx_is_rad:
        return self.W0
    else:
        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))
