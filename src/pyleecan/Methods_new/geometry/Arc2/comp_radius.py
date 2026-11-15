# -*- coding: utf-8 -*-

import numpy as np


def comp_radius(self) -> float:
    """Compute the radius of the arc

    Parameters
    ----------
    self : Arc2
        An Arc2 object

    Returns
    -------
    radius: float
        radius of the arc
    """

    self.check()

    z1 = self.begin
    zc = self.center
    return float(np.abs(z1 - zc))  # Radius of the arc
