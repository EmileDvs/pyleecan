import numpy as np






@staticmethod
def change_layer(wind_mat: np.ndarray) -> np.ndarray:
    """Change the Winding Matrix along the layer

    Parameters
    ----------
    wind_mat : numpy.ndarray
        A Winding Matrix (Nlay_r, Nlay_theta, Zs, qs)
        (created by comp_connection_mat)

    Returns
    -------
    wind_mat: numpy.ndarray
        The winding matrix with changed layers

    """
    wind_shape = wind_mat.shape
    assert len(wind_shape) == 4, "wind_mat has a wrong shape (dim 4)"

    if wind_shape[0] == 1 and wind_shape[1] != 1:
        wind_mat2 = np.zeros((wind_shape[1], wind_shape[0], wind_shape[2], wind_shape[3]))
        wind_mat2[:, 0, :, :] = wind_mat[0, :, :, :]
        return wind_mat2
    elif wind_shape[0] != 1 and wind_shape[1] == 1:
        wind_mat2 = np.zeros((wind_shape[1], wind_shape[0], wind_shape[2], wind_shape[3]))
        wind_mat2[0, :, :, :] = wind_mat[:, 0, :, :]
        return wind_mat2
    else:
        return wind_mat


