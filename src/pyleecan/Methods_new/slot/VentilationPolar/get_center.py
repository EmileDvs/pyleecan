# -*- coding: utf-8 -*-

import numpy as np


def get_center(self):
    """Return a list of the center of the ventilations

    Parameters
    ----------
    self : VentilationPolar
        A VentilationPolar object

    Returns
    -------
    Zc_list: list
        List of list of center complex coordinates

    """

    Zc_list = list()

    for ii in range(self.Zh):
        Zc = self.H0 + (self.D0 / 2.0) * np.exp(1j * self.Alpha0) * np.exp(
            1j * 2 * np.pi / self.Zh
        )
        Zc_list.append(Zc)

    return Zc_list
