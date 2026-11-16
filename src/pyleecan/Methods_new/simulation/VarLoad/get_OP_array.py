from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_OP_array(self, *arg_list) -> np.ndarray:
    """Return the OP matrix

    Parameters
    ----------
    self : VarLoadCurrent
        A VarLoadCurrent object

    Returns
    -------
    OP_matrix : ndarray
        Operating Points matrix
    """

    return self.OP_matrix.get_OP_array(*arg_list)
