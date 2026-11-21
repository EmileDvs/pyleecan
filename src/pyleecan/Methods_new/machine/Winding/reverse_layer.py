import numpy as np




@staticmethod
def reverse_layer(wind_mat: np.ndarray) -> np.ndarray:
    """reverse the Winding Matrix along the layer

    Parameters
    ----------
    wind_mat : numpy.ndarray
        A Winding Matrix (Nlay_r, Nlay_theta, Zs, qs)
        (created by comp_connection_mat)

    Returns
    -------
    wind_mat: numpy.ndarray
        The reverse matrix along the layer

    """
    assert len(wind_mat.shape) == 4, "wind_mat has a wrong shape (dim 4)"

    wind_mat = wind_mat[:, ::-1, :, :]
    wind_mat = wind_mat[::-1, :, :, :]

    return wind_mat




