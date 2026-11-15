# -*- coding: utf-8 -*-

import numpy as np


def comp_surface_opening(self):
    """Compute the Slot opening surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW12
        A SlotW12 object

    Returns
    -------
    Sop: float
        Slot opening surface [m**2]

    """

    Rbo = self.get_Rbo()

    S1 = self.H0 * 2 * self.R2
    S2 = 4 * self.R1 * self.R2
    S3 = np.pi * self.R1**2

    # The bottom is an arc
    alpha = self.comp_angle_opening()
    Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

    # Because Slamination = S - Zs * Sslot
    if self.is_outwards():
        return S1 + S2 + S3 - Sarc
    else:
        return S1 + S2 + S3 + Sarc
