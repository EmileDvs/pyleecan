import numpy as np


def comp_angle_opening(self):
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotW63
        A SlotW63 object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """
    slot_pitch = 2 * np.pi / self.Zs
    tooth_angle = 2 * np.arcsin(self.W1 / (2 * self.get_Rbo()))

    return slot_pitch - tooth_angle
