import numpy as np


from math import isnan


def BH_func(self, H, Bs, a):
    """
    Return the B from H according to Langevin model.

    Parameters
    ----------
    self : ModelBH_Langevin
        a ModelBH_Langevin object

    Returns
    -------
    B: numpy.ndarray
        B(H) values

    """
    B = Bs * (np.cosh(H / a) / np.sinh(H / a) - a / H)

    if isinstance(B, np.ndarray):
        B[np.argwhere(np.isnan(B))] = Bs
        B[np.argwhere(H == 0)] = 0
    elif isnan(B):
        if H == 0:
            B = 0
        else:
            B = Bs

    return B
