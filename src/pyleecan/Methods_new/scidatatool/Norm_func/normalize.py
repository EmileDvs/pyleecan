from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def normalize(
    self,
    values: np.ndarray,
):
    """Normalizes axis values
    Parameters
    ----------
    self: Norm_func
        a Norm_func object
    values: ndarray
        axis values
    Returns
    -------
    Vector of axis values
    """
    return self.function(values)
