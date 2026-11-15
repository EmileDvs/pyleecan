# -*- coding: utf-8 -*-

import numpy as np


def get_center(self) -> complex:
    """Return the center of the arc

    Parameters
    ----------
    self : Arc3
        An Arc3 object

    Returns
    -------
    Zc: complex
        Complex coordinates of the center of the Arc3
    """

    self.check()

    # the center is on the bisection of [begin, end]
    z1 = self.begin
    z2 = self.end

    Zc = (z1 + z2) / 2.0

    # Return (0,0) if the point is too close from 0
    if np.abs(Zc) < 1e-6:
        Zc = 0

    return Zc
