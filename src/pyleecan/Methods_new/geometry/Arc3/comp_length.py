# -*- coding: utf-8 -*-

import numpy as np


def comp_length(self) -> float:
    """Compute the length of the arc

    Parameters
    ----------
    self : Arc3
        An Arc3 object

    Returns
    -------
    length: float
        length of the arc
    """

    self.check()

    R = self.comp_radius()

    # Half circle
    return float(np.pi * R)
