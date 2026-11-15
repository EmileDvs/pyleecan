# -*- coding: utf-8 -*-
import numpy as np


def comp_distance(self, Z: complex) -> float:
    """Compute the distance of a point to the Arc

    Parameters
    ----------
    self : Arc
        An Arc object
    Z : complex
        Complex coordinate of the point

    Returns
    -------
    D : float
        distance of a point to the Segment
    """

    Zc = self.get_center()
    Z2 = Z - Zc

    A1 = self.get_angle()
    A2 = np.angle(Z2 * np.exp(-1j * np.angle(self.get_begin() - Zc)))

    if np.sign(A1) == np.sign(A2) and abs(A2) < abs(A1):
        # The point is on the correct side of the arc
        D1 = abs(np.sqrt(Z2.real**2 + Z2.imag**2) - self.comp_radius())
        return D1
    else:
        D2 = abs(Z - self.get_begin())
        D3 = abs(Z - self.get_end())
        D4 = abs(Z - self.get_middle())
        return min([D2, D3, D4])
