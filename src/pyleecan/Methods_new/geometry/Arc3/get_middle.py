# -*- coding: utf-8 -*-

import numpy as np


def get_middle(self):
    """Return the point at the middle of the arc

    Parameters
    ----------
    self : Arc3
        An Arc3 object

    Returns
    -------
    Zmid: complex
        Complex coordinates of the middle of the Arc3
    """

    # We use the complex representation of the point
    z1 = self.begin
    zc = self.get_center()
    R = self.comp_radius()

    # Generation of the point by rotation
    if self.is_trigo_direction:  # Top
        Zmid = R * np.exp(1j * np.pi / 2.0)
    else:  # Bottom
        Zmid = R * np.exp(-1j * np.pi / 2.0)

    # Geometric transformation : return to the main axis
    Zmid = Zmid * np.exp(1j * np.angle(z1 - zc)) + zc

    # Return (0,0) if the point is too close from 0
    if np.abs(Zmid) < 1e-6:
        Zmid = 0

    return Zmid
