import numpy as np


def comp_angle_opening(self):
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """

    alpha = float(np.arcsin(self.W3 / (2 * self.get_Rbo())))
    return 2 * np.pi / self.Zs - 2 * alpha
