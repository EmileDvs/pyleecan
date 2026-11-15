# -*- coding: utf-8 -*-
import numpy as np


def comp_surface(self):
    """Compute the circle surface

    Parameters
    ----------
    self : Circle
        A Circle object

    Returns
    -------
    surf: float
        The circle surface [m**2]

    """

    return np.pi * self.radius**2
