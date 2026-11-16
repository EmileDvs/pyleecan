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
    self: Norm_ref
        a Norm_ref object
    values: ndarray
        axis values
    Returns
    -------
    Vector of axis values
    """
    return values / self.ref
