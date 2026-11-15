# -*- coding: utf-8 -*-

import numpy as np


def comp_angle_opening(self):
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotW25
        A SlotW25 object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """
    Rbo = self.get_Rbo()

    slot_pitch = 2 * np.pi / self.Zs

    alpha_4 = float(2 * np.arcsin(self.W4 / (2 * Rbo)))
    return slot_pitch - alpha_4
