# -*- coding: utf-8 -*-

import numpy as np


def comp_mass(self):
    """Computation of the Shaft mass

    Parameters
    ----------
    self: Shaft
        A Shaft object
    Returns
    -------
    M_shaft: float
        Mass of the Shaft [kg]

    """
    if self.Lshaft is None:
        return 0
    else:
        return self.Lshaft * np.pi * ((self.Drsh / 2) ** 2) * self.mat_type.struct.rho
