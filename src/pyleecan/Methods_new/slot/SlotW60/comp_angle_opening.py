# -*- coding: utf-8 -*-

import numpy as np


def comp_angle_opening(self):
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotW60
        A SlotW60 object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """

    return 2 * np.pi / self.Zs
