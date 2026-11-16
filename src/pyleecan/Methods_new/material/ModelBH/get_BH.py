import numpy as np

from scipy.optimize import curve_fit, root_scalar


def get_BH(self) -> np.ndarray | None:
    """
    Return the B(H) curve of the material (by default do nothing).

    Parameters
    ----------
    self : ModelBH
        a ModelBH object

    Returns
    -------
    BH: numpy.ndarray
        B(H) values (two colums matrix: H and B(H))

    """

    return None
