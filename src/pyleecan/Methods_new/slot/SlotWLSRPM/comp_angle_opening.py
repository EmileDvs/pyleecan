import numpy as np


def comp_angle_opening(self):
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotWLSRPM：
        A SlotWLSRPM： object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """
    Rbo = self.get_Rbo()
    return 2 * (np.pi / self.Zs - np.arcsin(self.W3 / 2 / Rbo))
