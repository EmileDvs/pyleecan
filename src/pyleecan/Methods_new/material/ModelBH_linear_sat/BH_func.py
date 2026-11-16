import numpy as np


from math import isnan


def BH_func(self, H: float | np.ndarray, Bs: float, mu_a: float) -> float | np.ndarray:
    """
    Return the B from H according to piecewise linear saturated model.

    Parameters
    ----------
    self : ModelBH_linear_sat
        a ModelBH_linear_sat object

    Returns
    -------
    B: numpy.ndarray
        B(H) values

    """
    B = mu_a * H

    if isinstance(B, np.ndarray):
        B[np.argwhere(B >= Bs)] = Bs
    elif B >= Bs:
        B = Bs

    return B
