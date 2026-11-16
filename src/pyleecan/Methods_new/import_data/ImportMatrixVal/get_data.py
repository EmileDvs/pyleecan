from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_data(self) -> np.ndarray:
    """Return the object's matrix

    Parameters
    ----------
    self : ImportMatrixVal
        An ImportMatrixVal object

    Returns
    -------
    matrix: ndarray
        The object's matrix

    """

    return self.edit_matrix(self.value)
