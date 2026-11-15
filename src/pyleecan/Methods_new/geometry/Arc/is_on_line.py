# -*- coding: utf-8 -*-

import numpy as np


def is_on_line(self, Z: complex) -> bool:
    """Check is a point defined by its complex coordinate is on the arc

    Parameters
    ----------
    self : Arc
        An Arc object
    Z : complex
        Complex coordinate of the point

    Returns
    -------
    is_on_line : bool
        True if the point is on the arc
    """

    Zc = self.get_center()
    R = self.comp_radius()

    # Check if on the circle
    if abs(np.abs(Z - Zc) - R) > 1e-6:
        return False

    # Check if point is begin or end
    begin = self.get_begin()
    end = self.get_end()
    if np.abs(Z - begin) < 1e-6:
        return True
    if np.abs(Z - end) < 1e-6:
        return True

    # Go to the coordinate system Zc as center, begin on X > 0 axis
    Ze = (end - Zc) * np.exp(-1j * np.angle(begin - Zc))
    Z = (Z - Zc) * np.exp(-1j * np.angle(begin - Zc))

    alpha = self.get_angle()
    Ae = np.angle(Ze) % (2 * np.pi)
    Az = np.angle(Z) % (2 * np.pi)
    if alpha > 0:  # Trigo direction
        if Ae > Az:
            return True
        return False
    # Clockwise direction
    if Az > Ae:
        return True
    return False
