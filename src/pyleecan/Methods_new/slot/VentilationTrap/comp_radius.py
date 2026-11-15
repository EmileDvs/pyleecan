# -*- coding: utf-8 -*-

import numpy as np


def comp_radius(self):
    """Compute the radius of the two circle that contains all the ventilation
    ducts

    Parameters
    ----------
    self : VentilationTrap
        A VentilationTrap object

    Returns
    -------
    (Rmin, Rmax): tuple
        Tuple of circle radius [m]

    """

    self.check()

    Rmin = np.sqrt(self.W1**2 + self.H0**2)
    Rmax = np.sqrt(self.W2**2 + (self.H0 + self.D0) ** 2)

    return (Rmin, Rmax)
