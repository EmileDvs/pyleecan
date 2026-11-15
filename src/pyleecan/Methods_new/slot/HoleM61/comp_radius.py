# -*- coding: utf-8 -*-

import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1


def comp_radius(self):
    """Compute the radius of the min and max circle that contains the slot

    Parameters
    ----------
    self : HoleM61
        A HoleM61 object

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the slot [m]
    """

    Rbo = self.get_Rbo()

    Rmax = Rbo - self.H2
    Rmin = np.abs((Rbo - self.H0) + 1j * self.W0 / 2)

    return (Rmin, Rmax)
