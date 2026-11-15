# -*- coding: utf-8 -*-

import numpy as np


def get_angle(self, is_deg: bool = False) -> float:
    """Return the angle of the arc

    Parameters
    ----------
    self : Arc3
        An Arc3 object
    is_deg: bool
        True to convert to degree

    Returns
    -------
    angle: float
        Angle of the arc
    """

    if self.is_trigo_direction:
        sign = 1
    else:
        sign = -1

    if is_deg:
        return sign * 180
    else:
        return sign * np.pi
