import numpy as np








@staticmethod
def permute_B_C(wind_mat: np.ndarray) -> np.ndarray:
    """Permute B & C phases

    Parameters
    ----------
    wind_mat : numpy.ndarray
        A Winding Matrix (Nlay_r, Nlay_theta, Zs, qs)
        (created by comp_connection_mat)

    Returns
    -------
    wind_mat: numpy.ndarray
        The winding matrix with permuted phases

    """
    wind_shape = wind_mat.shape
    assert len(wind_shape) == 4, "wind_mat has a wrong shape (dim 4)"
    assert wind_shape[3] > 2

    wind_mat2 = wind_mat.copy()
    wind_mat2[:, :, :, 1] = wind_mat[:, :, :, 2]
    wind_mat2[:, :, :, 2] = wind_mat[:, :, :, 1]
    return wind_mat2
