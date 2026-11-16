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
    self: Norm_affine
        a Norm_affine object
    values: ndarray
        axis values
    Returns
    -------
    Vector of axis values
    """
    return values * self.slope + self.offset
