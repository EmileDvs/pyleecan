import numpy as np


def normalize(
    self,
    values,
):
    """Normalizes axis values
    Parameters
    ----------
    self: Norm_indices
        a Norm_indices object
    values: ndarray
        axis values
    Returns
    -------
    Vector of axis values
    """
    return np.array([i for i in range(len(values))])
